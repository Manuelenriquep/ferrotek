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
    peso_total = cantidad_bultos_30kg_meta * 30
    insumos = {}
    if "Mezcla A" in tipo_mezcla: 
        f = peso_total / 100.0
        insumos = {'cemento_kg': 29.5*f, 'arena_kg': 66.5*f, 'carbonato_kg': 4.5*f, 'fibras_kg': 0.1*f, 'cal_kg':0, 'zeolita_kg':0}
    elif "Mezcla B" in tipo_mezcla: 
        den_mix = (1*1.5) + (3*1.6) + (3*0.55)
        u = peso_total / den_mix
        insumos = {'cemento_kg': u*1.5, 'arena_kg': u*4.8, 'cal_kg': u*1.65, 'carbonato_kg':0, 'zeolita_kg':0}
    elif "Mezcla T" in tipo_mezcla: 
        den_mix = (1*1.5) + (2*0.55) + (3*0.9)
        u = peso_total / den_mix
        insumos = {'cemento_kg': u*1.5, 'cal_kg': u*1.1, 'zeolita_kg': u*2.7, 'arena_kg':0, 'carbonato_kg':0}
    return insumos

# ==========================================
# 3. MOTOR DE COSTOS AUDITADO (V119)
# ==========================================
def calcular_proyecto(input_data, linea_negocio="general", incluye_acabados=True):
    P = st.session_state['precios_reales']
    margen = st.session_state['margen'] / 100
    
    lista_mat = [] # Lista de materiales detallada
    
    # --- DOMOS ---
    if linea_negocio == "domo":
        ancho = input_data['ancho']; fondo = input_data['fondo']
        alt_m = 0.80; radio = ancho/2.0; alt_c = alt_m + radio 
        
        # Geometría
        perim_arco = (math.pi * radio) + (alt_m * 2)
        area_timp = (math.pi * radio**2) + (2 * ancho * alt_m)
        area_tot = (perim_arco * fondo) + area_timp
        
        # Cantidades Físicas (Cálculo Real)
        num_arcos = math.ceil(fondo/0.6) + 1
        ml_pgc_tot = (num_arcos * perim_arco) + (area_timp * 3.5)
        cant_tubos = math.ceil(ml_pgc_tot / 6.0)
        cant_malla = math.ceil(area_tot * 2.1) 
        cant_cemento = math.ceil(area_tot * 0.35) 
        cant_arena = math.ceil(area_tot * 0.05)
        
        # Lista Valorizada
        lista_mat = [
            {"Insumo": "Perfil PGC 90 (6m)", "Cant": cant_tubos, "Unid": "Tubos", "Costo": cant_tubos * 6 * P['perfil_pgc90_ml']},
            {"Insumo": "Malla 5mm", "Cant": cant_malla, "Unid": "m2", "Costo": cant_malla * P['malla_5mm_m2']},
            {"Insumo": "Cemento Gris (50kg)", "Cant": cant_cemento, "Unid": "Bultos", "Costo": cant_cemento * P['cemento_gris_50kg']},
            {"Insumo": "Arena Río", "Cant": cant_arena, "Unid": "m3", "Costo": cant_arena * P['arena_rio_m3']},
            {"Insumo": "Tornillería/Anclajes", "Cant": 1, "Unid": "Global", "Costo": area_tot * 4000}
        ]
        
        c_mat = sum([item['Costo'] for item in lista_mat]) # Suma exacta
        c_mo = math.ceil(ancho*fondo/2.0) * P['dia_cuadrilla']
        c_acab = (ancho*fondo * P.get('valor_acabados_vis_m2', 350000)) if incluye_acabados else 0
        
        total = c_mat + c_mo + c_acab
        return {"precio": total/(1-margen), "utilidad": (total/(1-margen))-total, 
                "geo": {"h": alt_c, "area": area_tot}, 
                "desglose": {"mat":c_mat, "mo":c_mo, "acab":c_acab}, "materiales": lista_mat}

    # --- MUROS ---
    elif linea_negocio == "muro":
        ml = input_data['ml']; alt = input_data['altura']; area = ml*alt
        tipo = input_data['tipo']; es_doble = "Doble" in tipo
        
        f_perf = 1.8 if es_doble else 1.0; f_malla = 2.1 if es_doble else 1.1
        f_cem = 0.4 if es_doble else 0.25 
        
        ml_perf = area * 1.5 * f_perf
        cant_tubos = math.ceil(ml_perf / 6.0)
        cant_malla = math.ceil(area * f_malla)
        cant_cemento = math.ceil(area * f_cem)
        
        # Cimentación
        vol_cinta = ml * 0.20 * 0.25
        cant_cem_cim = math.ceil(vol_cinta * 7)
        cant_arena_cim = vol_cinta * 1.1
        
        lista_mat = [
            {"Insumo": "Perfil PGC Estructura", "Cant": cant_tubos, "Unid": "Tubos", "Costo": cant_tubos*6*P['perfil_pgc90_ml']},
            {"Insumo": "Malla Refuerzo", "Cant": cant_malla, "Unid": "m2", "Costo": cant_malla*P['malla_5mm_m2']},
            {"Insumo": "Cemento (Muro+Cim)", "Cant": cant_cemento+cant_cem_cim, "Unid": "Bultos", "Costo": (cant_cemento+cant_cem_cim)*P['cemento_gris_50kg']},
            {"Insumo": "Arena Lavada", "Cant": math.ceil(cant_arena_cim), "Unid": "m3", "Costo": (cant_arena_cim)*P['arena_rio_m3']}
        ]
        
        c_mat = sum([item['Costo'] for item in lista_mat])
        c_mo = (area/5.0 * P['dia_cuadrilla']) * (1.5 if es_doble else 1.0)
        
        total = c_mat + c_mo
        return {"precio": total/(1-margen), "utilidad": (total/(1-margen))-total, 
                "desglose": {"mat":c_mat, "mo":c_mo, "acab":0}, "materiales": lista_mat}

    # --- CASAS ---
    elif linea_negocio == "casa":
        area = input_data['area']
        estilo = input_data.get('estilo', 'Tradicional')
        
        if estilo == 'Tradicional':
            fac_muros = 2.8; fac_techo = 1.4; nom_teja = "Teja PVC Colonial"; p_teja = 60000
        else: # Serie M
            fac_muros = 2.6; fac_techo = 1.2; nom_teja = "Teja PVC Termo"; p_teja = 45000

        area_muros = area * fac_muros
        area_techo = area * fac_techo
        
        cant_tubos_muro = math.ceil((area_muros * 1.5) / 6.0)
        cant_tubos_techo = math.ceil((area_techo * 1.2) / 6.0)
        cant_malla = math.ceil(area_muros * 2.2)
        cant_cemento = math.ceil(area_muros * 0.35 + (area*0.1*7))
        cant_tejas = math.ceil(area_techo / 1.8)
        
        lista_mat = [
            {"Insumo": "Perfil PGC (Total)", "Cant": cant_tubos_muro+cant_tubos_techo, "Unid": "Tubos", "Costo": (cant_tubos_muro+cant_tubos_techo)*6*P['perfil_pgc90_ml']},
            {"Insumo": f"Cubierta {nom_teja}", "Cant": cant_tejas, "Unid": "Piezas", "Costo": cant_tejas*1.8*p_teja},
            {"Insumo": "Malla Electrosoldada", "Cant": cant_malla, "Unid": "m2", "Costo": cant_malla*P['malla_5mm_m2']},
            {"Insumo": "Cemento (Gris)", "Cant": cant_cemento, "Unid": "Bultos", "Costo": cant_cemento*P['cemento_gris_50kg']},
            {"Insumo": "Arena/Triturado", "Cant": math.ceil(area*0.2), "Unid": "m3", "Costo": math.ceil(area*0.2)*P['arena_rio_m3']}
        ]
        
        c_mat = sum([item['Costo'] for item in lista_mat]) # Auditoría OK
        c_mo = area * P['dia_cuadrilla'] * 1.1
        c_acab = (area * P['valor_acabados_m2']) if incluye_acabados else 0
        
        total = c_mat + c_mo + c_acab
        return {"precio": total/(1-margen), "utilidad": (total/(1-margen))-total, 
                "desglose": {"mat": c_mat, "mo": c_mo, "acab": c_acab}, "materiales": lista_mat}

    # --- AGUA ---
    elif linea_negocio == "agua":
        vol = input_data['vol']; h = 1.5; r = math.sqrt(vol/(math.pi*h)); area_m = 2*math.pi*r*h
        cant_malla = math.ceil(area_m * 4)
        cant_cemento = math.ceil(area_m * 0.6)
        
        lista_mat = [
            {"Insumo": "Malla Hexagonal/Electro", "Cant": cant_malla, "Unid": "m2", "Costo": cant_malla*P['malla_5mm_m2']},
            {"Insumo": "Cemento Impermeable", "Cant": cant_cemento, "Unid": "Bultos", "Costo": cant_cemento*P['cemento_gris_50kg']},
            {"Insumo": "Aditivos/Sika", "Cant": 1, "Unid": "Global", "Costo": 200000}
        ]
        c_mat = sum([item['Costo'] for item in lista_mat])
        c_mo = area_m/2.0 * P['dia_cuadrilla']
        total = c_mat + c_mo
        return {"precio": total/(1-margen), "utilidad": (total/(1-margen))-total, 
                "desglose": {"mat":c_mat, "mo":c_mo, "acab":0}, "materiales": lista_mat}

    return {"precio": 0}

# ==========================================
# 4. GENERADOR PDF
# ==========================================
class PDFDossier(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16); self.cell(0, 10, 'FERROTEK S.A.S', 0, 1, 'C')
        self.set_font('Arial', 'I', 10); self.cell(0, 10, 'Innovación Constructiva', 0, 1, 'C'); self.ln(5)

def generar_pdf_cotizacion(cliente, proyecto, datos, desc):
    pdf = PDFDossier(); pdf.add_page(); pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Cliente: {cliente} | Fecha: {datetime.now().strftime('%d/%m/%Y')}", 0, 1)
    pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, f"COTIZACION: {proyecto}", 0, 1)
    pdf.set_font('Arial', '', 11); pdf.multi_cell(0, 6, desc); pdf.ln(10)
    pdf.set_font('Arial', 'B', 16); pdf.cell(0, 15, f"INVERSION TOTAL: ${datos['precio']:,.0f}", 0, 1)
    pdf.set_font('Arial', 'I', 9); pdf.multi_cell(0, 5, "Validez: 15 días. Incluye: Materiales, Mano de Obra, Dirección Técnica.")
    return bytes(pdf.output(dest='S'))

def generar_portafolio(tipo="master"):
    pdf = PDFDossier(); pdf.add_page()
    pdf.set_font('Arial', 'B', 24); pdf.set_text_color(0, 51, 102); pdf.cell(0, 20, "PORTAFOLIO FERROTEK", 0, 1, 'C')
    pdf.set_font('Arial', '', 11); pdf.set_text_color(0)
    if tipo in ["master", "casas"]:
        pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, "1. LINEA VIVIENDA", 0, 1)
        pdf.multi_cell(0, 6, "A. SERIE TRADICIONAL: Techo PVC 2 aguas.\nB. SERIE M: Minimalista cúbica.")
        pdf.ln(5)
    if tipo in ["master", "muros"]:
        pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, "2. LINEA MUROS", 0, 1); pdf.multi_cell(0, 6, "Cerramientos alta resistencia."); pdf.ln(5)
    if tipo in ["master", "domos"]:
        pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, "3. LINEA DOMOS", 0, 1); pdf.multi_cell(0, 6, "Bóvedas evolutivas."); pdf.ln(5)
    return bytes(pdf.output(dest='S'))

# ==========================================
# 5. SIDEBAR
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
        with st.expander("Costos Base"): st.session_state['precios_reales'] = st.data_editor(st.session_state['precios_reales'], key="p_edit")

if 'view' not in st.session_state: st.session_state.view = 'home'
def set_view(name): st.session_state.view = name

# ==========================================
# 6. VISTAS
# ==========================================
def mostrar_desglose(data):
    if es_admin:
        st.markdown("---")
        st.markdown("##### 🕵️ Auditoría Financiera")
        c1, c2, c3 = st.columns(3)
        c1.metric("🧱 Materiales", f"${data['desglose']['mat']:,.0f}")
        c2.metric("👷 Mano de Obra", f"${data['desglose']['mo']:,.0f}")
        c3.success(f"📈 UTILIDAD: ${data['utilidad']:,.0f}")
        with st.expander("📦 LISTA DE MATERIALES (LOGÍSTICA)"):
            if 'materiales' in data:
                st.dataframe(pd.DataFrame(data['materiales']), hide_index=True, use_container_width=True)

# --- HOME ---
if st.session_state.view == 'home':
    st.title("🏗️ FERROTEK: Soluciones Industrializadas")
    c1, c2 = st.columns(2)
    with c1: st.download_button("📘 Portafolio Master", generar_portafolio("master"), "Master.pdf", "application/pdf", use_container_width=True)
    with c2: st.download_button("🏠 Brochure Casas", generar_portafolio("casas"), "Casas.pdf", "application/pdf", use_container_width=True)
    
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.button("🧱 Muros", on_click=lambda: set_view('muros'), use_container_width=True)
    with c2: st.button("🏠 Casas", on_click=lambda: set_view('casas'), use_container_width=True)
    with c3: st.button("🌾 Domos", on_click=lambda: set_view('domos'), use_container_width=True)
    with c4: st.button("💧 Agua", on_click=lambda: set_view('agua'), use_container_width=True)
    
    # 📸 GALERÍA DE PROYECTOS (RESTAURADA)
    st.markdown("---")
    st.subheader("📸 Galería de Proyectos")
    imgs = [f for f in os.listdir('.') if f.endswith(('.png','.jpg','.jpeg'))]
    if imgs:
        cols = st.columns(3)
        for i, img in enumerate(imgs):
            with cols[i % 3]:
                st.image(img, caption=img.split('.')[0].replace('_', ' ').title(), use_container_width=True)
    else:
        st.info("No hay imágenes en la carpeta. Sube tus renders para verlos aquí.")

# --- CASAS ---
elif st.session_state.view == 'casas':
    st.button("⬅️ Volver", on_click=lambda: set_view('home')); st.header("🏠 Línea Vivienda")
    tab_trad, tab_mod = st.tabs(["🏡 TRADICIONAL", "🏗️ SERIE M"])
    
    with tab_trad:
        c1, c2 = st.columns(2)
        with c1:
            mod_t = st.selectbox("Modelo:", ["T-1 (30m2)", "T-2 (48m2)", "T-3 (70m2)"])
            area_t = int(mod_t.split()[1].replace("m2)","").replace("(",""))
            full_t = st.checkbox("Llave en Mano", True, key="chk_t")
            data_t = calcular_proyecto({'area': area_t, 'estilo': 'Tradicional'}, "casa", full_t)
            st.metric("Inversión", f"${data_t['precio']:,.0f}")
            mostrar_desglose(data_t)
            if st.text_input("Cliente Tradicional:", key="cli_t"):
                st.download_button("PDF", generar_pdf_cotizacion(st.session_state.get('cli_t'), "Casa Tradicional", data_t, mod_t), "cot_trad.pdf")
        with c2: st.info("Techo PVC Colonial, Aleros.")
        try: st.image("vis_familiar.png", width=400)
        except: pass

    with tab_mod:
        c1, c2 = st.columns(2)
        with c1:
            mod_m = st.selectbox("Modelo:", ["M-2 (45m2)", "M-3 (70m2)"])
            area_m = 45 if "M-2" in mod_m else 70
            full_m = st.checkbox("Llave en Mano", True, key="chk_m")
            data_m = calcular_proyecto({'area': area_m, 'estilo': 'Serie M'}, "casa", full_m)
            st.metric("Inversión", f"${data_m['precio']:,.0f}")
            mostrar_desglose(data_m)
            if st.text_input("Cliente Serie M:", key="cli_m"):
                st.download_button("PDF", generar_pdf_cotizacion(st.session_state.get('cli_m'), "Casa Serie M", data_m, mod_m), "cot_mod.pdf")
        with c2: st.success("Diseño Cúbico, Wet-Wall.")
        try: st.image("vivienda_suite.png" if "M-2" in mod_m else "vivienda_master.png", width=400)
        except: pass

# --- MUROS ---
elif st.session_state.view == 'muros':
    st.button("⬅️ Volver", on_click=lambda: set_view('home')); st.header("🧱 Línea Muros")
    c1, c2 = st.columns(2)
    with c1:
        tipo = st.radio("Tipo:", ["Tipo 2 (Sencillo)", "Tipo 1 (Doble)"])
        ml = st.number_input("Largo (m):", 10.0); alt = st.number_input("Alto (m):", 2.2)
        data = calcular_proyecto({'ml':ml, 'altura':alt, 'tipo':tipo}, "muro")
        st.metric("Inversión", f"${data['precio']:,.0f}")
        mostrar_desglose(data)
        if st.text_input("Cliente:"): st.download_button("PDF", generar_pdf_cotizacion("Cli", "Muro", data, f"{tipo}"), "cot.pdf")
    with c2: 
        st.info("Cerramientos de alta resistencia.")
        try: st.image("muro_perimetral.png", use_container_width=True); except: pass

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
        mostrar_desglose(data)
        if st.text_input("Cliente:"): st.download_button("PDF", generar_pdf_cotizacion("Cli", "Domo", data, f"{ancho}x{fondo}m"), "cot.pdf")
    with c2: 
        st.success(f"Altura: {data['geo']['h']:.2f}m")
        try: st.image("Loft_rural.png", use_container_width=True); except: pass

# --- AGUA ---
elif st.session_state.view == 'agua':
    st.button("⬅️ Volver", on_click=lambda: set_view('home')); st.header("💧 Línea Agua")
    c1, c2 = st.columns(2)
    with c1:
        vol = st.slider("Litros:", 1000, 20000, 5000, 1000)
        data = calcular_proyecto({'vol': vol/1000}, "agua")
        st.metric("Precio", f"${data['precio']:,.0f}")
        mostrar_desglose(data)
        if st.text_input("Cliente:"): st.download_button("PDF", generar_pdf_cotizacion("Cli", "Tanque", data, f"{vol}L"), "cot.pdf")

# --- FÁBRICA ---
elif st.session_state.view == 'fabrica':
    st.button("⬅️ Volver"); st.header("🏭 Fábrica")
    if not es_admin: st.warning("Restringido"); st.stop()
    tipo = st.selectbox("Mezcla:", ["Mezcla A", "Mezcla B", "Mezcla T"])
    qty = st.number_input("Bultos:", 1); res = calcular_produccion_lote(tipo, qty)
    st.table(pd.DataFrame(list(res.items()), columns=["Insumo", "Kg"]))