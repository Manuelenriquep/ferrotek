import streamlit as st
import pandas as pd
import math
import os
from fpdf import FPDF
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURACIÓN GENERAL
# ==========================================
st.set_page_config(page_title="Ferrotek | Suite Empresarial V8", page_icon="🏗️", layout="wide")

# ==========================================
# 🧪 MÓDULO FÁBRICA (NORMA V8.0)
# ==========================================
DENSIDAD = {'cemento': 1.50, 'arena': 1.60, 'cal': 0.55, 'zeolita': 0.90}

def calcular_produccion_lote(tipo_mezcla, cantidad_bultos_30kg_meta):
    insumos = {}
    if "Mezcla A (Estructural)" in tipo_mezcla: 
        peso_total_meta = cantidad_bultos_30kg_meta * 30
        factor = peso_total_meta / 100.0
        insumos = {
            'cemento_kg': 29.5 * factor,
            'arena_kg': 66.5 * factor,
            'carbonato_kg': 4.5 * factor,
            'fibras_kg': 0.1 * factor,
            'cal_kg': 0, 'zeolita_kg': 0
        }
    elif "Mezcla B (Piel de Roca)" in tipo_mezcla: 
        peso_meta = cantidad_bultos_30kg_meta * 30
        peso_vol = (3 * DENSIDAD['arena']) + (3 * DENSIDAD['cal']) + (1 * DENSIDAD['cemento'])
        units = peso_meta / peso_vol
        insumos = {
            'cemento_kg': units * 1 * DENSIDAD['cemento'],
            'arena_kg': units * 3 * DENSIDAD['arena'],
            'cal_kg': units * 3 * DENSIDAD['cal'],
            'carbonato_kg': 0, 'zeolita_kg': 0
        }
    elif "Mezcla T (Térmica)" in tipo_mezcla:
        peso_meta = cantidad_bultos_30kg_meta * 30
        peso_vol = (1 * DENSIDAD['cemento']) + (2 * DENSIDAD['cal']) + (3 * DENSIDAD['zeolita'])
        units = peso_meta / peso_vol
        insumos = {
            'cemento_kg': units * 1 * DENSIDAD['cemento'],
            'cal_kg': units * 2 * DENSIDAD['cal'],
            'zeolita_kg': units * 3 * DENSIDAD['zeolita'],
            'arena_kg': 0, 'carbonato_kg': 0
        }
    return insumos

# ==========================================
# 🧠 MOTOR DE COSTOS INTEGRAL (V8 + SERIE M)
# ==========================================
def calcular_proyecto(input_data, linea_negocio="general", incluye_acabados=True):
    P = st.session_state['precios_reales']
    margen = st.session_state['margen'] / 100
    
    # --- DOMOS EVOLUTIVOS ---
    if linea_negocio == "domo":
        ancho = input_data['ancho']; fondo = input_data['fondo']
        altura_murete = 0.80  
        radio = ancho / 2.0 
        altura_cumbrera = altura_murete + radio 
        long_arco_curvo = math.pi * radio 
        long_muretes_vert = altura_murete * 2 
        perimetro_seccion = long_arco_curvo + long_muretes_vert
        area_envolvente = perimetro_seccion * fondo
        area_timpanos = (math.pi * (radio**2)) + (2 * ancho * altura_murete)
        area_total_m2 = area_envolvente + area_timpanos
        num_arcos = math.ceil(fondo/0.6) + 1
        ml_pgc = (num_arcos * perimetro_seccion) + (area_timpanos * 3.5)
        
        costo_mat = (
            (ml_pgc * P['perfil_pgc90_ml']) +
            (area_total_m2 * 0.015 * 1.05 * 2200 / 50 * P['cemento_gris_50kg'] * 0.3) +
            (area_total_m2 * 0.015 * 1.05 * 1.1 * P['arena_rio_m3']) +
            (area_total_m2 * 2.1 * P['malla_5mm_m2']) +
            ((perimetro_seccion * fondo) * P.get('aislante_m2', 12000)) +
            (area_total_m2 * 4000)
        )
        costo_mo = math.ceil((ancho*fondo)/2.0) * P['dia_cuadrilla'] 
        costo_acab = (ancho*fondo) * P.get('valor_acabados_vis_m2', 350000) if incluye_acabados else 0
        total = costo_mat + costo_mo + costo_acab
        return {"precio": total/(1-margen), "utilidad": (total/(1-margen))-total, 
                "desglose": {"mat": costo_mat, "mo": costo_mo, "acab": costo_acab},
                "geo": {"h_total": altura_cumbrera, "area": area_total_m2}}

    # --- MUROS FERROTEK ---
    elif linea_negocio == "muro":
        ml = input_data['ml']; altura = input_data['altura']
        tipo_muro = input_data['tipo_muro']
        area = ml * altura
        factor_mat = 1.8 if "Doble" in tipo_muro else 1.0
        factor_mo = 1.5 if "Doble" in tipo_muro else 1.0
        costo_mat_base = (
            (area * 1.5 * P['perfil_pgc90_ml']) + 
            (area * 2.1 * P['malla_5mm_m2']) +    
            (area * 0.04 * 2200 / 50 * P['cemento_gris_50kg']) +
            (area * 0.04 * 1.1 * P['arena_rio_m3']) 
        ) * factor_mat
        vol_cinta = ml * 0.20 * 0.25
        costo_cimentacion = (vol_cinta * 350000)
        costo_mo = (area / 5.0 * P['dia_cuadrilla']) * factor_mo
        total = costo_mat_base + costo_cimentacion + costo_mo
        return {"precio": total/(1-margen), "utilidad": (total/(1-margen))-total,
                "desglose": {"mat": costo_mat_base + costo_cimentacion, "mo": costo_mo, "acab": 0}}

    # --- CASA SERIE M ---
    elif linea_negocio == "casa":
        area_piso = input_data['area']
        area_muros = area_piso * 2.6 
        area_techo = area_piso * 1.2 
        costo_muros = area_muros * 65000 
        costo_cubierta = area_techo * (P['perfil_pgc90_ml'] * 1.2 + 45000) 
        costo_losa = area_piso * 0.10 * 450000 
        costo_mat = costo_muros + costo_cubierta + costo_losa
        costo_mo = (area_piso / 1.0 * P['dia_cuadrilla']) 
        costo_acab = (area_piso * P['valor_acabados_m2']) if incluye_acabados else 0
        total = costo_mat + costo_mo + costo_acab
        return {"precio": total/(1-margen), "utilidad": (total/(1-margen))-total,
                "desglose": {"mat": costo_mat, "mo": costo_mo, "acab": costo_acab}}

    # --- ESTANQUES ---
    elif linea_negocio == "agua":
        volumen_m3 = input_data['volumen']
        altura_tanque = 1.5
        radio = math.sqrt(volumen_m3 / (math.pi * altura_tanque))
        perimetro = 2 * math.pi * radio
        area_muro_tanque = perimetro * altura_tanque
        area_piso_tanque = math.pi * (radio**2)
        costo_mallas = area_muro_tanque * 4 * P['malla_5mm_m2']
        costo_mortero = (area_muro_tanque * 0.06 + area_piso_tanque * 0.10) * 450000
        costo_varios = 200000
        costo_mat = costo_mallas + costo_mortero + costo_varios
        costo_mo = (area_muro_tanque / 2.0 * P['dia_cuadrilla'])
        total = costo_mat + costo_mo
        return {"precio": total/(1-margen), "utilidad": (total/(1-margen))-total,
                "desglose": {"mat": costo_mat, "mo": costo_mo, "acab": 0}}

    return {"precio": 0, "utilidad": 0, "desglose": {"mat":0, "mo":0, "acab":0}}

# ==========================================
# 📄 PDF GENERATOR
# ==========================================
class PDFBase(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16); self.cell(0, 10, 'FERROTEK S.A.S - SUITE EMPRESARIAL', 0, 1, 'C')
        self.set_font('Arial', 'I', 10); self.cell(0, 10, 'Ingeniería Unibody & Construcción Monolítica', 0, 1, 'C'); self.ln(5)

def generar_pdf(cliente, proyecto, datos, desc, tipo_doc="Cotización"):
    pdf = PDFBase(); pdf.add_page(); pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Documento: {tipo_doc} | Fecha: {datetime.now().strftime('%d/%m/%Y')}", 0, 1)
    pdf.cell(0, 10, f"Cliente: {cliente}", 0, 1); pdf.ln(5)
    pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, f"PROYECTO: {proyecto}", 0, 1)
    pdf.set_font('Arial', '', 11); pdf.multi_cell(0, 6, desc); pdf.ln(10)
    if "Cotización" in tipo_doc:
        pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "RESUMEN DE INVERSIÓN", 0, 1)
        pdf.set_font('Arial', '', 11)
        pdf.set_font('Arial', 'B', 16); pdf.cell(0, 15, f"TOTAL: ${datos['precio']:,.0f}", 0, 1)
        pdf.set_font('Arial', 'I', 9); pdf.multi_cell(0, 5, "Validez: 15 días. Incluye materiales, mano de obra y dirección técnica (Manual V8.0).")
    return bytes(pdf.output(dest='S'))

class PDFDossier(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 20); self.set_text_color(50, 50, 50)
        self.cell(0, 15, 'FERROTEK (R)', 0, 1, 'L'); self.line(10, 25, 200, 25); self.ln(10)
    def footer(self):
        self.set_y(-15); self.set_font('Arial', 'I', 8); self.set_text_color(128)
        self.cell(0, 10, 'Propiedad Intelectual de Manuel Enrique Prada F. - Innovación Colombiana', 0, 0, 'C')

def generar_dossier_comercial():
    pdf = PDFDossier(); pdf.add_page()
    pdf.set_font('Arial', 'B', 24); pdf.set_text_color(0, 51, 102); pdf.cell(0, 15, 'CATALOGO SERIE M (MODULAR)', 0, 1, 'C')
    pdf.set_font('Arial', 'I', 14); pdf.set_text_color(100); pdf.cell(0, 10, 'Eficiencia Pura - Cero Desperdicio', 0, 1, 'C'); pdf.ln(5)
    pdf.set_font('Arial', '', 11); pdf.set_text_color(0)
    pdf.multi_cell(0, 6, "Diseñados bajo la modulación estricta del Steel Framing (40/60 cm) para eliminar cortes y maximizar el beneficio.")
    pdf.ln(5)
    pdf.set_fill_color(240, 240, 240); pdf.rect(10, pdf.get_y(), 190, 8, 'F'); pdf.set_xy(10, pdf.get_y())
    pdf.set_font('Arial', 'B', 14); pdf.cell(0, 8, '1. MODELO M-2: "MINIMALISTA ESENCIAL" (45 m2)', 0, 1, 'L'); pdf.ln(2)
    pdf.set_font('Arial', '', 11); pdf.multi_cell(0, 6, "- PERFIL: Parejas jóvenes, adultos mayores.\n- DISTRIBUCION: 2 Hab, 1 Baño, Sala-Comedor (Open Plan).\n- VENTAJAS: Acústica superior y Acabado Piel de Roca.\n- VELOCIDAD: Tiempo récord de ejecución.")
    pdf.ln(5)
    pdf.set_fill_color(240, 240, 240); pdf.rect(10, pdf.get_y(), 190, 8, 'F'); pdf.set_xy(10, pdf.get_y())
    pdf.set_font('Arial', 'B', 14); pdf.cell(0, 8, '2. MODELO M-3: "FAMILIAR PRO" (60-70 m2)', 0, 1, 'L'); pdf.ln(2)
    pdf.set_font('Arial', '', 11); pdf.multi_cell(0, 6, "- PERFIL: Familias consolidadas.\n- DISTRIBUCION: 3 Hab, 1-2 Baños, Cocina Barra.\n- VENTAJAS: Climatización pasiva y resistencia impacto.\n- ZONA HUMEDA: Wet Wall optimizado.")
    return bytes(pdf.output(dest='S'))

def generar_dossier_tecnico():
    pdf = PDFDossier(); pdf.add_page(); pdf.set_font('Arial', 'B', 20); pdf.cell(0, 10, 'MANUAL TECNICO - SERIE M', 0, 1, 'C')
    pdf.set_font('Arial', '', 10); pdf.multi_cell(0, 5, "Resumen Técnico: Estructura PGC 90, Modulación 40/60cm.")
    return bytes(pdf.output(dest='S'))

def generar_manual_mantenimiento():
    pdf = PDFDossier(); pdf.add_page(); pdf.set_font('Arial', 'B', 20); pdf.cell(0, 10, 'MANTENIMIENTO SERIE M', 0, 1, 'C')
    pdf.set_font('Arial', '', 10); pdf.multi_cell(0, 5, "Limpieza con jabón neutro.")
    return bytes(pdf.output(dest='S'))

# ==========================================
# 🎛️ SIDEBAR (LOGIN SEGURO V112.1)
# ==========================================
with st.sidebar:
    st.markdown("### Acceso Corporativo")
    pwd = st.text_input("Clave de Acceso:", type="password", help="Solo personal autorizado")
    
    defaults = {
        'cemento_gris_50kg': 29500, 'cal_hidratada_25kg': 25000, 'arena_rio_m3': 98000, 
        'malla_5mm_m2': 28000, 'perfil_pgc90_ml': 18500, 'dia_cuadrilla': 250000, 
        'valor_acabados_m2': 450000, 'valor_acabados_vis_m2': 350000, 'aislante_m2': 12000 
    }
    if 'precios_reales' not in st.session_state: st.session_state['precios_reales'] = defaults
    if 'margen' not in st.session_state: st.session_state['margen'] = 30
    
    es_admin = (pwd == "ferrotek2026")
    if es_admin:
        st.success("🔓 Modo Gerente Activo")
        st.session_state['margen'] = st.slider("Margen Utilidad %", 10, 60, 30)
        with st.expander("Costos Base Insumos"):
            st.session_state['precios_reales'] = st.data_editor(st.session_state['precios_reales'], key="p_edit")
    else:
        st.caption("Ferrotek S.A.S © 2026 | Sistema de Gestión V8.0")

if 'view' not in st.session_state: st.session_state.view = 'home'
def set_view(name): st.session_state.view = name

# --- VISTA HOME ---
if st.session_state.view == 'home':
    st.title("🏗️ FERROTEK: Soluciones Industrializadas")
    st.markdown("### Portafolio 'Serie M' (Manual V8.0)")
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    with c1: 
        st.image("https://img.icons8.com/color/96/wall.png", width=64)
        st.subheader("Línea Muros"); st.caption("Cerramientos y Fachadas")
        st.button("Cotizar Muros", on_click=lambda: set_view('muros'), use_container_width=True)
    with c2: 
        st.image("https://img.icons8.com/color/96/home.png", width=64)
        st.subheader("Línea Casa"); st.caption("Serie M (M-2 / M-3)")
        st.button("Cotizar Serie M", on_click=lambda: set_view('casas'), use_container_width=True)
    with c3: 
        st.image("https://img.icons8.com/color/96/igloo.png", width=64)
        st.subheader("Línea Domos"); st.caption("Evolutivos (Bóveda)")
        st.button("Cotizar Domos", on_click=lambda: set_view('domos'), use_container_width=True)
    with c4: 
        st.image("https://img.icons8.com/color/96/water-tank.png", width=64)
        st.subheader("Línea Agua"); st.caption("Estanques Rurales")
        st.button("Cotizar Tanques", on_click=lambda: set_view('agua'), use_container_width=True)

    st.markdown("---")
    st.markdown("### 📂 Documentación Comercial")
    col_d1, col_d2 = st.columns(2)
    with col_d1: st.download_button("📄 Descargar Dossier Serie M", generar_dossier_comercial(), "Ferrotek_SerieM.pdf", "application/pdf")
    if es_admin:
        with col_d2: st.download_button("🔒 Manual Técnico V8 (Privado)", b"DUMMY", "Manual_Tecnico_V8.pdf")

# --- VISTA CASAS (SERIE M) ---
elif st.session_state.view == 'casas':
    st.button("⬅️ Inicio", on_click=lambda: set_view('home')); st.header("🏠 Línea Casa - Serie M (Modular)")
    c1, c2 = st.columns(2)
    with c1:
        mod_sel = st.selectbox("Seleccione Modelo:", ["Modelo M-2: Minimalista (45m2 - 2 Alcobas)", "Modelo M-3: Familiar Pro (70m2 - 3 Alcobas)"])
        area = 45 if "M-2" in mod_sel else 70
        full = st.checkbox("Incluir Acabados (Llave en Mano)", True)
        data = calcular_proyecto({'area':area}, linea_negocio="casa", incluye_acabados=full)
        titulo = "INVERSIÓN TOTAL" if full else "VALOR OBRA GRIS"
        st.metric(titulo, f"${data['precio']:,.0f}")
        if "M-2" in mod_sel: st.info("💡 M-2: Ideal Parejas. Eficiencia Pura. Sin pasillos.")
        else: st.success("💡 M-3: Familiar. Wet-Wall optimizado. Barra Americana.")
        if es_admin: st.write(f"Costo: ${data['desglose']['mat'] + data['desglose']['mo']:,.0f} | Util: ${data['utilidad']:,.0f}")
        if st.text_input("Cliente:"):
            desc = f"Cotización {mod_sel}. Sistema Ferrotek Serie M."
            st.download_button("PDF Cotización", generar_pdf(st.session_state.get('cliente_name','Cliente'), "Casa Serie M", data, desc), "cotizacion_casa.pdf")
    with c2:
        img = "vivienda_suite.png" if "M-2" in mod_sel else "vivienda_familiar.png"
        try: st.image(img, caption=f"Render {mod_sel}", use_container_width=True)
        except: st.info(f"Sube imagen '{img}'")

# --- VISTA MUROS ---
elif st.session_state.view == 'muros':
    st.button("⬅️ Inicio", on_click=lambda: set_view('home')); st.header("🧱 Línea Muros Ferrotek")
    c1, c2 = st.columns(2)
    with c1:
        tipo = st.radio("Tipo de Muro:", ["Tipo 2: Sencillo (Cerramiento)", "Tipo 1: Doble (Fachada Térmica)"])
        ml = st.number_input("Longitud (m):", 10.0); alt = st.number_input("Altura (m):", 2.2)
        data = calcular_proyecto({'ml':ml, 'altura':alt, 'tipo_muro':tipo}, linea_negocio="muro")
        st.metric("Inversión Estimada", f"${data['precio']:,.0f}")
        if st.text_input("Cliente Muros:"):
            st.download_button("PDF Muros", generar_pdf("Cliente", "Muros", data, f"Muro {tipo} {ml}x{alt}m"), "cotizacion_muro.pdf")
    with c2:
        try: st.image("muro_perimetral.png", use_container_width=True)
        except: pass

# --- VISTA DOMOS ---
elif st.session_state.view == 'domos':
    st.button("⬅️ Inicio", on_click=lambda: set_view('home')); st.header("🌾 Línea Domos Evolutivos")
    c1, c2 = st.columns(2)
    with c1:
        uso = st.selectbox("Configuración:", ["Vivienda (6m Frente)", "Garage/Bodega (3.8m Frente)", "Personalizado"])
        w = 6.0 if "Vivienda" in uso else 3.8 if "Garage" in uso else 5.0
        ancho = st.number_input("Frente (m):", 2.0, 15.0, w)
        fondo = st.number_input("Fondo (m):", 3.0, 50.0, 10.0)
        full = st.checkbox("Acabados Full", True if "Vivienda" in uso else False)
        data = calcular_proyecto({'ancho':ancho, 'fondo':fondo}, linea_negocio="domo", incluye_acabados=full)
        st.metric("Inversión Total", f"${data['precio']:,.0f}")
        st.success(f"Altura Central: {data['geo']['h_total']:.2f}m")
        if st.text_input("Cliente Domo:"):
            st.download_button("PDF Domo", generar_pdf("Cliente", "Domo V8", data, f"Domo {ancho}x{fondo}m"), "cotizacion_domo.pdf")
    with c2:
        try: st.image("Loft_rural.png", use_container_width=True)
        except: pass

# --- VISTA AGUA ---
elif st.session_state.view == 'agua':
    st.button("⬅️ Inicio", on_click=lambda: set_view('home')); st.header("💧 Línea Agua")
    c1, c2 = st.columns(2)
    with c1:
        vol = st.slider("Capacidad (Litros):", 1000, 20000, 5000, 1000)
        data = calcular_proyecto({'volumen': vol/1000}, linea_negocio="agua")
        st.metric("Costo Tanque", f"${data['precio']:,.0f}")
        if st.text_input("Cliente Agua:"):
            st.download_button("PDF Tanque", generar_pdf("Cliente", "Tanque Ferrotek", data, f"Tanque {vol} Litros"), "cotizacion_tanque.pdf")

# --- VISTA FÁBRICA ---
elif st.session_state.view == 'fabrica':
    st.button("⬅️ Inicio", on_click=lambda: set_view('home')); st.header("🏭 Planta de Mezclas V8")
    if not es_admin: st.warning("Restringido"); st.stop()
    tipo = st.selectbox("Mezcla:", ["Mezcla A (Estructural)", "Mezcla B (Piel de Roca)", "Mezcla T (Térmica)"])
    qty = st.number_input("Bultos:", 1); res = calcular_produccion_lote(tipo, qty)
    st.table(pd.DataFrame(list(res.items()), columns=["Insumo", "Kg"]))