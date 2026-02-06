import streamlit as st
import pandas as pd
import math
import os
from fpdf import FPDF
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN
# ==========================================
st.set_page_config(page_title="Ferrotek | Suite V8", page_icon="🏗️", layout="wide")

# ==========================================
# 2. MOTOR DE MEZCLAS (FÁBRICA)
# ==========================================
DENSIDAD = {'cemento': 1.50, 'arena': 1.60, 'cal': 0.55, 'zeolita': 0.90}

def calcular_produccion_lote(tipo_mezcla, cantidad_bultos_30kg_meta):
    """Calculadora de insumos según receta V8."""
    peso_total = cantidad_bultos_30kg_meta * 30
    insumos = {}
    
    if "Mezcla A" in tipo_mezcla: # Estructural
        f = peso_total / 100.0
        insumos = {'cemento_kg': 29.5*f, 'arena_kg': 66.5*f, 'carbonato_kg': 4.5*f, 'fibras_kg': 0.1*f, 'cal_kg':0, 'zeolita_kg':0}
    elif "Mezcla B" in tipo_mezcla: # Piel de Roca (1:3:3 vol)
        den_mix = (1*1.5) + (3*1.6) + (3*0.55)
        u = peso_total / den_mix
        insumos = {'cemento_kg': u*1.5, 'arena_kg': u*4.8, 'cal_kg': u*1.65, 'carbonato_kg':0, 'zeolita_kg':0}
    elif "Mezcla T" in tipo_mezcla: # Térmica
        den_mix = (1*1.5) + (2*0.55) + (3*0.9)
        u = peso_total / den_mix
        insumos = {'cemento_kg': u*1.5, 'cal_kg': u*1.1, 'zeolita_kg': u*2.7, 'arena_kg':0, 'carbonato_kg':0}
    
    return insumos

# ==========================================
# 3. MOTOR DE COSTOS (LOGICA DE NEGOCIO)
# ==========================================
def calcular_proyecto(input_data, linea_negocio="general", incluye_acabados=True):
    P = st.session_state['precios_reales']
    margen = st.session_state['margen'] / 100
    
    # --- DOMOS ---
    if linea_negocio == "domo":
        ancho = input_data['ancho']; fondo = input_data['fondo']
        alt_m = 0.80; radio = ancho/2.0; alt_c = alt_m + radio 
        perim = (math.pi * radio) + (alt_m * 2)
        area_tot = (perim * fondo) + (math.pi * radio**2) + (2 * ancho * alt_m)
        ml_pgc = (math.ceil(fondo/0.6)+1) * perim + ((math.pi * radio**2) * 3.5)
        
        c_mat = (ml_pgc * P['perfil_pgc90_ml']) + (area_tot * 2.1 * P['malla_5mm_m2']) + (area_tot * 65000) # Mix mat aprox
        c_mo = math.ceil(ancho*fondo/2.0) * P['dia_cuadrilla']
        c_acab = (ancho*fondo * P.get('valor_acabados_vis_m2', 350000)) if incluye_acabados else 0
        total = c_mat + c_mo + c_acab
        return {"precio": total/(1-margen), "utilidad": (total/(1-margen))-total, "geo": {"h": alt_c, "area": area_tot}, "desglose": {"mat":c_mat, "mo":c_mo}}

    # --- MUROS ---
    elif linea_negocio == "muro":
        ml = input_data['ml']; alt = input_data['altura']; area = ml*alt
        fac = 1.8 if "Doble" in input_data['tipo'] else 1.0
        c_mat = ((area * 1.5 * P['perfil_pgc90_ml']) + (area * 2.1 * P['malla_5mm_m2']) + (area * 35000)) * fac
        c_cim = (ml * 0.2 * 0.25) * 350000
        c_mo = (area/5.0 * P['dia_cuadrilla']) * fac
        total = c_mat + c_cim + c_mo
        return {"precio": total/(1-margen), "utilidad": (total/(1-margen))-total, "desglose": {"mat":c_mat+c_cim, "mo":c_mo}}

    # --- CASAS (MOTOR UNIFICADO) ---
    elif linea_negocio == "casa":
        area = input_data['area']
        estilo = input_data.get('estilo', 'Tradicional')
        
        if estilo == 'Tradicional':
            fac_muros = 2.8 # Más tabiquería
            fac_techo = 1.4 # Pendiente + Aleros + Cerchas
            costo_teja = 60000 # Teja PVC Colonial (Más cara) + Estructura compleja
        else: # Serie M
            fac_muros = 2.6
            fac_techo = 1.2 # Techo plano/oculto
            costo_teja = 45000 # Teja PVC Trapezoidal

        c_mur = area * fac_muros * 65000 # Costo directo M2 muro
        c_cub = area * fac_techo * (P['perfil_pgc90_ml'] + costo_teja)
        c_losa = area * 0.10 * 450000
        c_mo = area * P['dia_cuadrilla'] * 1.1 # 1.1 factor seguridad MO
        c_acab = (area * P['valor_acabados_m2']) if incluye_acabados else 0
        
        total = c_mur + c_cub + c_losa + c_mo + c_acab
        return {"precio": total/(1-margen), "utilidad": (total/(1-margen))-total, 
                "desglose": {"mat": c_mur+c_cub+c_losa, "mo": c_mo}}

    # --- AGUA ---
    elif linea_negocio == "agua":
        vol = input_data['vol']; h = 1.5; r = math.sqrt(vol/(math.pi*h)); area_m = 2*math.pi*r*h
        c_mat = (area_m * 4 * P['malla_5mm_m2']) + (area_m * 0.06 * 450000) + 200000
        c_mo = area_m/2.0 * P['dia_cuadrilla']
        total = c_mat + c_mo
        return {"precio": total/(1-margen), "utilidad": (total/(1-margen))-total, "desglose": {"mat":c_mat, "mo":c_mo}}

    return {"precio": 0}

# ==========================================
# 4. GENERADOR PDF (MARKETING)
# ==========================================
class PDFDossier(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16); self.cell(0, 10, 'FERROTEK S.A.S', 0, 1, 'C')
        self.set_font('Arial', 'I', 10); self.cell(0, 10, 'Innovación Constructiva', 0, 1, 'C'); self.ln(5)

def generar_pdf_cotizacion(cliente, proyecto, datos, desc):
    pdf = PDFDossier(); pdf.add_page(); pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Cliente: {cliente} | Fecha: {datetime.now().strftime('%d/%m/%Y')}", 0, 1)
    pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, f"PROYECTO: {proyecto}", 0, 1)
    pdf.set_font('Arial', '', 11); pdf.multi_cell(0, 6, desc); pdf.ln(10)
    pdf.set_font('Arial', 'B', 16); pdf.cell(0, 15, f"INVERSION TOTAL: ${datos['precio']:,.0f}", 0, 1)
    pdf.set_font('Arial', 'I', 9); pdf.multi_cell(0, 5, "Validez: 15 días. Incluye: Materiales, Mano de Obra, Dirección Técnica.")
    return bytes(pdf.output(dest='S'))

def generar_portafolio(tipo="master"):
    pdf = PDFDossier(); pdf.add_page()
    pdf.set_font('Arial', 'B', 24); pdf.set_text_color(0, 51, 102); pdf.cell(0, 20, "PORTAFOLIO FERROTEK", 0, 1, 'C')
    pdf.set_font('Arial', '', 11); pdf.set_text_color(0)
    
    if tipo in ["master", "casas"]:
        pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, "1. LINEA VIVIENDA (2 ESTILOS)", 0, 1)
        pdf.set_font('Arial', '', 11)
        pdf.multi_cell(0, 6, "A. SERIE TRADICIONAL: El calor de hogar con tecnología moderna. Techo a dos aguas (PVC Colonial), aleros amplios y distribución clásica.\nB. SERIE M (MODERNA): Eficiencia minimalista. Techos ocultos y espacios abiertos.")
        pdf.ln(5)
    
    if tipo in ["master", "muros"]:
        pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, "2. LINEA MUROS", 0, 1)
        pdf.set_font('Arial', '', 11); pdf.multi_cell(0, 6, "Cerramientos perimetrales de alta resistencia. Antibalas y sin mantenimiento.")
        pdf.ln(5)

    if tipo in ["master", "domos"]:
        pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, "3. LINEA DOMOS", 0, 1)
        pdf.set_font('Arial', '', 11); pdf.multi_cell(0, 6, "Bóvedas evolutivas con muretes de 80cm. Ideales para Glamping y Bodegas.")
        pdf.ln(5)

    return bytes(pdf.output(dest='S'))

# ==========================================
# 5. SIDEBAR (ACCESO SEGURO)
# ==========================================
with st.sidebar:
    st.markdown("### Acceso Corporativo"); pwd = st.text_input("Clave:", type="password")
    defaults = {'cemento_gris_50kg': 29500, 'cal_hidratada_25kg': 25000, 'arena_rio_m3': 98000, 
        'malla_5mm_m2': 28000, 'perfil_pgc90_ml': 18500, 'dia_cuadrilla': 250000, 'valor_acabados_m2': 450000, 'valor_acabados_vis_m2': 350000}
    if 'precios_reales' not in st.session_state: st.session_state['precios_reales'] = defaults
    if 'margen' not in st.session_state: st.session_state['margen'] = 30
    es_admin = (pwd == "ferrotek2026")
    if es_admin:
        st.success("Gerencia Activa"); st.session_state['margen'] = st.slider("Margen %", 10, 60, 30)
        with st.expander("Costos"): st.session_state['precios_reales'] = st.data_editor(st.session_state['precios_reales'], key="p_edit")

if 'view' not in st.session_state: st.session_state.view = 'home'
def set_view(name): st.session_state.view = name

# ==========================================
# 6. VISTAS (UI)
# ==========================================

# --- HOME ---
if st.session_state.view == 'home':
    st.title("🏗️ FERROTEK: Soluciones Industrializadas")
    st.markdown("### 📂 Documentación")
    c1, c2 = st.columns(2)
    with c1: st.download_button("📘 Portafolio General", generar_portafolio("master"), "Ferrotek_Master.pdf", "application/pdf", use_container_width=True)
    with c2: st.download_button("🏠 Brochure Casas (Trad + M)", generar_portafolio("casas"), "Ferrotek_Casas.pdf", "application/pdf", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 🚀 Cotizadores")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.subheader("🧱 Muros"); st.button("Ir a Muros", on_click=lambda: set_view('muros'), use_container_width=True)
    with c2: st.subheader("🏠 Casas"); st.button("Ir a Casas", on_click=lambda: set_view('casas'), use_container_width=True)
    with c3: st.subheader("🌾 Domos"); st.button("Ir a Domos", on_click=lambda: set_view('domos'), use_container_width=True)
    with c4: st.subheader("💧 Agua"); st.button("Ir a Tanques", on_click=lambda: set_view('agua'), use_container_width=True)

# --- CASAS (A LA PAR: TABS) ---
elif st.session_state.view == 'casas':
    st.button("⬅️ Volver", on_click=lambda: set_view('home')); st.header("🏠 Línea Vivienda")
    
    # AQUÍ ESTÁ LA SOLUCIÓN: TABS PARA IGUALDAD DE CONDICIONES
    tab_trad, tab_mod = st.tabs(["🏡 SERIE TRADICIONAL", "🏗️ SERIE M (MODERNA)"])
    
    # 1. PESTAÑA TRADICIONAL
    with tab_trad:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("#### Estilo Clásico / Campestre")
            st.caption("Techo a dos aguas (PVC Colonial), Aleros, Distribución familiar.")
            
            mod_t = st.selectbox("Modelo Tradicional:", 
                ["T-1: Refugio (30m2)", "T-2: Familiar (48m2)", "T-3: Hacienda (70m2)"])
            
            area_t = int(mod_t.split()[2].replace("m2)","").replace("(",""))
            full_t = st.checkbox("Llave en Mano (Tradicional)", True, key="chk_t")
            
            data_t = calcular_proyecto({'area': area_t, 'estilo': 'Tradicional'}, "casa", full_t)
            st.metric("Inversión Tradicional", f"${data_t['precio']:,.0f}")
            
            if st.text_input("Cliente Tradicional:", key="cli_t"):
                desc = f"Casa Estilo Tradicional. {mod_t}. Cubierta PVC Colonial + Cerchas."
                st.download_button("PDF Tradicional", generar_pdf_cotizacion(st.session_state.get('cli_t'), "Casa Tradicional", data_t, desc), "cot_trad.pdf")
        
        with c2:
            try: st.image("vis_familiar.png", caption="Fachada Tradicional", use_container_width=True)
            except: st.info("Imagen Tradicional")

    # 2. PESTAÑA MODERNA
    with tab_mod:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("#### Estilo Minimalista / Inversión")
            st.caption("Techo Oculto, Cubos, Wet-Wall compartido, Máxima eficiencia.")
            
            mod_m = st.selectbox("Modelo Serie M:", 
                ["M-2: Minimalista (45m2)", "M-3: Familiar Pro (70m2)"])
            
            area_m = 45 if "M-2" in mod_m else 70
            full_m = st.checkbox("Llave en Mano (Serie M)", True, key="chk_m")
            
            data_m = calcular_proyecto({'area': area_m, 'estilo': 'Serie M'}, "casa", full_m)
            st.metric("Inversión Serie M", f"${data_m['precio']:,.0f}")
            
            if st.text_input("Cliente Serie M:", key="cli_m"):
                desc = f"Casa Serie M. {mod_m}. Cubierta Termoacústica Oculta."
                st.download_button("PDF Serie M", generar_pdf_cotizacion(st.session_state.get('cli_m'), "Casa Serie M", data_m, desc), "cot_mod.pdf")
        
        with c2:
            img = "vivienda_suite.png" if "M-2" in mod_m else "vivienda_master.png"
            try: st.image(img, caption="Fachada Serie M", use_container_width=True)
            except: st.info("Imagen Serie M")

# --- MUROS ---
elif st.session_state.view == 'muros':
    st.button("⬅️ Volver", on_click=lambda: set_view('home')); st.header("🧱 Línea Muros")
    c1, c2 = st.columns(2)
    with c1:
        tipo = st.radio("Tipo:", ["Tipo 2 (Sencillo)", "Tipo 1 (Doble)"])
        ml = st.number_input("Largo (m):", 10.0); alt = st.number_input("Alto (m):", 2.2)
        data = calcular_proyecto({'ml':ml, 'altura':alt, 'tipo':tipo}, "muro")
        st.metric("Inversión", f"${data['precio']:,.0f}")
        if st.text_input("Cliente:"): st.download_button("PDF", generar_pdf_cotizacion("Cli", "Muro", data, f"Muro {tipo}"), "cot.pdf")
    with c2: try: st.image("muro_perimetral.png", use_container_width=True); except: pass

# --- DOMOS ---
elif st.session_state.view == 'domos':
    st.button("⬅️ Volver", on_click=lambda: set_view('home')); st.header("🌾 Línea Domos")
    c1, c2 = st.columns(2)
    with c1:
        uso = st.selectbox("Uso:", ["Vivienda (6m)", "Garage (3.8m)", "Personalizado"])
        w = 6.0 if "Vivienda" in uso else 3.8 if "Garage" in uso else 5.0
        ancho = st.number_input("Frente:", 2.0, 15.0, w); fondo = st.number_input("Fondo:", 3.0, 50.0, 10.0)
        full = st.checkbox("Acabados", True if "Vivienda" in uso else False)
        data = calcular_proyecto({'ancho':ancho, 'fondo':fondo}, "domo", full)
        st.metric("Inversión", f"${data['precio']:,.0f}")
        st.success(f"Altura: {data['geo']['h']:.2f}m")
        if st.text_input("Cliente:"): st.download_button("PDF", generar_pdf_cotizacion("Cli", "Domo", data, f"Domo {ancho}x{fondo}m"), "cot.pdf")
    with c2: try: st.image("Loft_rural.png", use_container_width=True); except: pass

# --- AGUA ---
elif st.session_state.view == 'agua':
    st.button("⬅️ Volver", on_click=lambda: set_view('home')); st.header("💧 Línea Agua")
    c1, c2 = st.columns(2)
    with c1:
        vol = st.slider("Litros:", 1000, 20000, 5000, 1000)
        data = calcular_proyecto({'vol': vol/1000}, "agua")
        st.metric("Precio", f"${data['precio']:,.0f}")
        if st.text_input("Cliente:"): st.download_button("PDF", generar_pdf_cotizacion("Cli", "Tanque", data, f"Tanque {vol}L"), "cot.pdf")

# --- FÁBRICA ---
elif st.session_state.view == 'fabrica':
    st.button("⬅️ Volver"); st.header("🏭 Fábrica")
    if not es_admin: st.warning("Restringido"); st.stop()
    tipo = st.selectbox("Mezcla:", ["Mezcla A", "Mezcla B", "Mezcla T"])
    qty = st.number_input("Bultos:", 1); res = calcular_produccion_lote(tipo, qty)
    st.table(pd.DataFrame(list(res.items()), columns=["Insumo", "Kg"]))