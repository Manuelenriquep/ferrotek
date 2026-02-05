import streamlit as st
import pandas as pd
import math
import os
from fpdf import FPDF
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURACIÓN GENERAL
# ==========================================
st.set_page_config(page_title="Ferrotek | Sistema Constructivo V7", page_icon="🏗️", layout="wide")

# ==========================================
# 🧪 MÓDULO FÁBRICA (NORMA V7.0)
# ==========================================
DENSIDAD = {'cemento': 1.50, 'arena': 1.60, 'cal': 0.55, 'zeolita': 0.90}

def calcular_produccion_lote(tipo_mezcla, cantidad_bultos_30kg_meta):
    insumos = {}
    if "Industrial (Batch 100)" in tipo_mezcla:
        peso_total_meta = cantidad_bultos_30kg_meta * 30
        factor = peso_total_meta / 100.0
        insumos = {
            'cemento_kg': 29.5 * factor,
            'arena_kg': 66.5 * factor,
            'carbonato_kg': 4.5 * factor,
            'fibras_kg': 0.1 * factor,
            'cal_kg': 0, 'zeolita_kg': 0
        }
    elif "Manual (1:2.5)" in tipo_mezcla:
        peso_meta = cantidad_bultos_30kg_meta * 30
        peso_vol = (2.5 * DENSIDAD['arena']) + (1 * DENSIDAD['cemento'])
        units = peso_meta / peso_vol
        insumos = {
            'cemento_kg': units * 1 * DENSIDAD['cemento'],
            'arena_kg': units * 2.5 * DENSIDAD['arena'],
            'cal_kg': 0, 'carbonato_kg': 0, 'zeolita_kg': 0
        }
    elif "Piel de Roca" in tipo_mezcla: 
        peso_meta = cantidad_bultos_30kg_meta * 30
        peso_vol = (3 * DENSIDAD['arena']) + (3 * DENSIDAD['cal']) + (1 * DENSIDAD['cemento'])
        units = peso_meta / peso_vol
        insumos = {
            'cemento_kg': units * 1 * DENSIDAD['cemento'],
            'arena_kg': units * 3 * DENSIDAD['arena'],
            'cal_kg': units * 3 * DENSIDAD['cal'],
            'carbonato_kg': 0, 'zeolita_kg': 0
        }
    elif "Thermo (Zeolita)" in tipo_mezcla:
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
# 🧠 MOTOR DE COSTOS
# ==========================================
def calcular_proyecto(input_data, tipo="general", tiene_gotero=False, incluye_acabados=True):
    P = st.session_state['precios_reales']
    margen = st.session_state['margen'] / 100
    
    # --- CASO DOMOS V7 ---
    if tipo == "domo_boveda":
        ancho = input_data['ancho']; fondo = input_data['fondo']
        radio = ancho / 2.0 
        long_arco = math.pi * radio 
        area_cubierta_curva = long_arco * fondo 
        area_timpanos = (math.pi * (radio**2))
        area_total_envolvente = area_cubierta_curva + area_timpanos
        num_arcos = math.ceil(fondo/0.6) + 1
        total_pgc_90 = (num_arcos * long_arco) + (area_timpanos * 3.5)
        
        costo_mat = (
            (total_pgc_90 * P['perfil_pgc90_ml']) +
            (area_total_envolvente * 0.015 * 1.03 * 2200 / 50 * P['cemento_gris_50kg'] * 0.295) +
            (area_total_envolvente * 0.015 * 1.03 * 2200 * 0.045 * P.get('carbonato_kg', 1500)) +
            (area_total_envolvente * 0.015 * 1.03 * 1.1 * P['arena_rio_m3']) +
            (area_total_envolvente * 2.1 * P['malla_5mm_m2']) +
            ((long_arco * fondo) * P.get('aislante_m2', 12000)) +
            (area_total_envolvente * 4000)
        )
        costo_mo = math.ceil((ancho*fondo)/2.2) * P['dia_cuadrilla'] 
        costo_acabados = (ancho*fondo) * P.get('valor_acabados_vis_m2', 350000) if incluye_acabados else 0
        costo_total = costo_mat + costo_mo + costo_acabados
        return {"precio": costo_total/(1-margen), "utilidad": (costo_total/(1-margen))-costo_total, "desglose": {"materiales": costo_mat, "mano_obra": costo_mo, "acabados": costo_acabados}}

    # --- CASO GENERAL ---
    else:
        area_m2 = input_data['area']; ml_muro_val = input_data.get('ml', 0)
        espesor = 0.06 if tipo=="estanque" else 0.055 if tipo=="vivienda" else 0.04
        fac_malla = 1.6 if tipo=="vivienda" else 2.1
        varilla = area_m2*1.5 if tipo=="estanque" else 0
        vol = area_m2 * espesor * 1.05
        costo_mat = (
            (math.ceil(vol*0.7*8.5) * P['cemento_gris_50kg']) +
            (math.ceil(vol*0.3*10) * P['cal_hidratada_25kg']) +
            (vol*1.1 * P['arena_rio_m3']) +
            (area_m2 * fac_malla * P['malla_5mm_m2']) +
            (area_m2 * 0.9 * P['perfil_c18_ml']) +
            (math.ceil(varilla) * P.get('varilla_refuerzo_6m', 24000)) +
            (area_m2 * 5000)
        )
        mo = math.ceil(area_m2/P.get('rendimiento_dia', 4.5)) * P['dia_cuadrilla']
        extra = ml_muro_val * 25000 if tiene_gotero else 0
        if tipo == "vivienda": costo_acabados = (area_m2/3.5 * P.get('valor_acabados_m2', 450000)) if incluye_acabados else 0
        else: costo_acabados = 0 
        total = costo_mat + mo + extra + acabados
        return {"precio": total/(1-margen), "utilidad": (total/(1-margen))-total, "desglose": {"materiales": costo_mat, "mano_obra": mo, "acabados": acabados}}

# ==========================================
# 📄 PDF GENERATOR
# ==========================================
class PDFBase(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16); self.cell(0, 10, 'FERROTEK S.A.S', 0, 1, 'C')
        self.set_font('Arial', 'I', 10); self.cell(0, 10, 'Ingeniería Unibody & Construcción Monolítica', 0, 1, 'C'); self.ln(10)

def generar_pdf_cotizacion(cliente, obra, datos, desc, incluye_acabados):
    pdf = PDFBase(); pdf.add_page(); pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Cliente: {cliente} | Fecha: {datetime.now().strftime('%d/%m/%Y')}", 0, 1)
    pdf.cell(0, 10, f"Proyecto: {obra}", 0, 1); pdf.ln(5)
    titulo_alcance = "ALCANCE: LLAVE EN MANO (FULL)" if incluye_acabados else "ALCANCE: OBRA GRIS AVANZADA"
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, titulo_alcance, 0, 1)
    pdf.set_font('Arial', '', 10)
    if incluye_acabados:
        alcance = "- Estructura Sismo-Resistente.\n- Muros Ferrocemento con aislamiento.\n- Instalaciones internas.\n- ACABADOS: Pisos, enchapes, ventaneria.\n- NO INCLUYE: Lote ni licencias."
    else:
        alcance = "- Estructura Sismo-Resistente.\n- Muros Ferrocemento con aislamiento.\n- Instalaciones (Puntos).\n- EXCLUYE: Pisos, enchapes, carpinteria.\n- ESTADO: Obra Gris Habitable."
    pdf.multi_cell(0, 6, alcance); pdf.ln(10)
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "ESPECIFICACIONES", 0, 1)
    pdf.set_font('Arial', '', 11); pdf.multi_cell(0, 7, desc); pdf.ln(5)
    pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, f"INVERSIÓN TOTAL: ${datos['precio']:,.0f}", 0, 1)
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
    pdf.set_font('Arial', 'B', 26); pdf.set_text_color(0, 51, 102); pdf.cell(0, 15, 'FERROTEK (R) BOVEDA EVOLUTIVA', 0, 1, 'C')
    pdf.set_font('Arial', 'I', 14); pdf.set_text_color(100); pdf.cell(0, 10, 'La Revolucion del Espacio en 60 m2', 0, 1, 'C'); pdf.ln(5)
    if os.path.exists("Loft_rural.png"): pdf.image("Loft_rural.png", x=20, y=50, w=170); pdf.ln(100)
    pdf.set_y(160); pdf.set_font('Arial', 'B', 16); pdf.set_text_color(0); pdf.cell(0, 10, '¿Cansado de la "Caja de Fosforos"?', 0, 1, 'C')
    pdf.set_font('Arial', '', 12); pdf.set_text_color(50); pdf.multi_cell(0, 6, "En Colombia, el lote tradicional de 6x10m se ha convertido en sinonimo de oscuridad.\nFERROTEK ROMPE EL MOLDE.\nUtilizamos arcos para darle: LUZ, ALTURA y FRESCURA.", align='C')
    pdf.add_page(); pdf.set_font('Arial', 'B', 18); pdf.set_text_color(0, 51, 102); pdf.cell(0, 10, 'UN DISENO, DOS POSIBILIDADES', 0, 1, 'L'); pdf.ln(5)
    if os.path.exists("vis_loft.png"): pdf.image("vis_loft.png", x=15, y=30, w=80)
    if os.path.exists("vis_familiar.png"): pdf.image("vis_familiar.png", x=105, y=30, w=80)
    pdf.ln(70); pdf.set_font('Arial', 'B', 12); pdf.set_text_color(0)
    y_start = pdf.get_y(); pdf.set_xy(10, y_start); pdf.multi_cell(90, 6, "OPCION A: OPEN LOFT\n\nEspacio continuo. Ideal Turismo.")
    pdf.set_xy(105, y_start); pdf.multi_cell(90, 6, "OPCION B: FAMILIAR\n\nIncluye Mezzanine y divisiones.")
    return bytes(pdf.output(dest='S'))

def generar_dossier_tecnico():
    pdf = PDFDossier(); pdf.add_page()
    pdf.set_font('Arial', 'B', 20); pdf.set_text_color(0, 51, 102); pdf.cell(0, 10, 'SISTEMA CONSTRUCTIVO FERROTEK (R)', 0, 1, 'C')
    pdf.set_font('Arial', 'I', 12); pdf.set_text_color(80); pdf.cell(0, 8, 'Hibrido de Alta Eficiencia: Steel Frame + Ferrocemento', 0, 1, 'C'); pdf.ln(5)
    pdf.set_font('Arial', 'B', 12); pdf.set_text_color(0); pdf.cell(0, 8, '1. FUNDAMENTO', 0, 1)
    pdf.set_font('Arial', '', 10); pdf.multi_cell(0, 5, "Resistencia por FORMA. Estructuras 50% mas livianas."); pdf.ln(8)
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 8, '2. VENTAJAS', 0, 1); pdf.ln(2)
    col_var, col_trad, col_ferro = 35, 75, 75
    pdf.set_font('Arial', 'B', 10); pdf.set_fill_color(230)
    pdf.cell(col_var, 8, "VARIABLE", 1, 0, 'C', 1); pdf.cell(col_trad, 8, "TRADICIONAL", 1, 0, 'C', 1); pdf.cell(col_ferro, 8, "FERROTEK", 1, 1, 'C', 1)
    pdf.set_font('Arial', '', 9); y_b = pdf.get_y()
    pdf.cell(col_var, 12, "VELOCIDAD", 1, 0, 'C'); pdf.set_xy(10+col_var, y_b); pdf.multi_cell(col_trad, 6, "LENTA\n(Fraguados)", 1, 'C'); pdf.set_xy(10+col_var+col_trad, y_b); pdf.multi_cell(col_ferro, 6, "RAPIDA\n(Montaje seco)", 1, 'C')
    y_b = pdf.get_y(); pdf.cell(col_var, 12, "PESO", 1, 0, 'C'); pdf.set_xy(10+col_var, y_b); pdf.multi_cell(col_trad, 6, "PESADO", 1, 'C'); pdf.set_xy(10+col_var+col_trad, y_b); pdf.multi_cell(col_ferro, 6, "LIVIANO", 1, 'C')
    pdf.ln(10); pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, '3. APLICACIONES', 0, 1)
    pdf.set_font('Arial', '', 10); pdf.multi_cell(0, 5, "Vivienda VIS, Tanques, Turismo.")
    return bytes(pdf.output(dest='S'))

def generar_manual_mantenimiento():
    pdf = PDFDossier(); pdf.add_page()
    pdf.set_font('Arial', 'B', 22); pdf.set_text_color(0, 100, 0); pdf.cell(0, 10, 'GUIA DE MANTENIMIENTO', 0, 1, 'C')
    pdf.set_font('Arial', 'I', 12); pdf.set_text_color(80); pdf.cell(0, 8, 'Cuidados para su Hogar Ferrotek', 0, 1, 'C'); pdf.ln(10)
    
    pdf.set_font('Arial', 'B', 14); pdf.set_text_color(0); pdf.cell(0, 10, '1. MICROCEMENTO (Pisos y Banos)', 0, 1)
    pdf.set_font('Arial', '', 11); pdf.multi_cell(0, 6, "- LIMPIEZA: Use solamente agua y jabon neutro (pH neutro).\n- PROHIBIDO: No usar Cloro, hipoclorito, acidos o amoniaco.\n- PROTECCION: Use fieltros en las patas de los muebles para no rayar.")
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, '2. PIEL DE ROCA (Muros y Fachada)', 0, 1)
    pdf.set_font('Arial', '', 11); pdf.multi_cell(0, 6, "- LAVADO: Se puede lavar con agua a presion moderada.\n- PINTURA: Aunque no lo requiere, es compatible con pinturas tipo latex/acrilicas si desea cambiar el color.\n- HUMEDAD: El material respira, evite sellarlo con esmaltes sinteticos.")
    pdf.ln(10)
    
    pdf.set_fill_color(240, 240, 240); pdf.rect(10, pdf.get_y(), 190, 30, 'F'); pdf.set_xy(15, pdf.get_y()+5)
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, 'GARANTIA', 0, 1)
    pdf.set_font('Arial', '', 11); pdf.multi_cell(180, 6, "Recuerde que cualquier modificacion estructural (regatas, roturas) sin autorizacion anula la garantia de impermeabilidad.")
    return bytes(pdf.output(dest='S'))

# ==========================================
# 🎛️ SIDEBAR (LOGIN)
# ==========================================
with st.sidebar:
    st.title("🎛️ Admin Ferrotek")
    pwd = st.text_input("Contraseña:", type="password")
    
    defaults = {
        'cemento_gris_50kg': 29500, 'cal_hidratada_25kg': 25000, 'arena_rio_m3': 98000, 
        'malla_5mm_m2': 28000, 'perfil_c18_ml': 11500, 'perfil_pgc90_ml': 18500, 
        'varilla_refuerzo_6m': 24000, 'carbonato_kg': 1500, 'zeolita_kg': 2500, 
        'aislante_m2': 12000, 'dia_cuadrilla': 250000, 'rendimiento_dia': 4.5,
        'valor_acabados_m2': 450000, 'valor_acabados_vis_m2': 350000 
    }
    if 'precios_reales' not in st.session_state: st.session_state['precios_reales'] = defaults
    if 'margen' not in st.session_state: st.session_state['margen'] = 30
    
    es_admin = (pwd == "ferrotek2026")
    if es_admin:
        st.success("🔓 Sesión Gerente")
        st.session_state['margen'] = st.slider("Utilidad %", 0, 60, st.session_state['margen'])
        with st.expander("Costos Insumos V7"):
            st.session_state['precios_reales'] = st.data_editor(st.session_state['precios_reales'], key="p_edit")
    else:
        st.info("Ingrese contraseña para ver costos reales.")

if 'view' not in st.session_state: st.session_state.view = 'home'
def set_view(name): st.session_state.view = name

# ==========================================
# 🎨 VISTA 1: HOME
# ==========================================
if st.session_state.view == 'home':
    st.title("🏗️ FERROTEK: Innovación Constructiva")
    st.subheader("Solidez de Roca, Precisión de Acero.")
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1: st.info("### 🛡️ Sismo-Resistencia"); st.write("Estructura dúctil PGC 90mm que protege la vida.")
    with c2: st.success("### 🌡️ Termo-Acústico"); st.write("Núcleo aislante y Zeolita para confort superior.")
    with c3: st.warning("### 💧 Impermeabilidad"); st.write("Piel de Roca hidrofóbica sin mantenimiento.")
    st.markdown("---")
    st.subheader("🚀 Cotizadores")
    b1, b2, b3, b4 = st.columns(4)
    with b1: st.button("🛡️ Muros Perimetrales", on_click=lambda: set_view('muros'), use_container_width=True)
    with b2: st.button("🏠 Viviendas Unibody", on_click=lambda: set_view('viviendas'), use_container_width=True)
    with b3: st.button("🌾 Domos / Bóvedas", on_click=lambda: set_view('domos'), use_container_width=True)
    with b4: st.button("🏭 Planta de Mezclas", on_click=lambda: set_view('fabrica'), use_container_width=True)
    st.markdown("---")
    st.subheader("📂 Centro de Documentación Pública")
    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1: st.download_button("📄 Dossier Comercial", generar_dossier_comercial(), "Ferrotek_Comercial.pdf", "application/pdf")
    with col_d2: st.download_button("📐 Ficha Técnica", generar_dossier_tecnico(), "Ferrotek_Tecnico.pdf", "application/pdf")
    with col_d3: st.download_button("🧹 Manual Mantenimiento", generar_manual_mantenimiento(), "Ferrotek_Mantenimiento.pdf", "application/pdf")

    st.markdown("---")
    imgs = [f for f in os.listdir('.') if f.endswith(('.png','.jpg'))]
    if imgs:
        st.subheader("📸 Galería de Proyectos")
        c = st.columns(3)
        for i, f in enumerate(imgs): c[i%3].image(f, caption=f, use_container_width=True)

# ==========================================
# 🎨 VISTA: DOMOS
# ==========================================
elif st.session_state.view == 'domos':
    st.button("⬅️ Volver", on_click=lambda: set_view('home'))
    st.header("🌾 Domos & Bóvedas Evolutivas")
    c1, c2 = st.columns([1, 1.5]) 
    with c1:
        distribucion = st.radio("Modelo:", ["Open Loft (Turista)", "Familiar (2 Hab)"])
        ancho = st.number_input("Frente (m):", 6.0, disabled=True)
        fondo = st.number_input("Fondo (m):", 10.0)
        incluir_acabados = st.checkbox("Incluir Acabados (Llave en Mano)", value=True)
        data = calcular_proyecto({'ancho': ancho, 'fondo': fondo}, tipo="domo_boveda", incluye_acabados=incluir_acabados)
        st.markdown("---")
        titulo_precio = "VALOR LLAVE EN MANO" if incluir_acabados else "VALOR OBRA GRIS"
        st.metric(titulo_precio, f"${data['precio']:,.0f}")
        st.markdown("##### 📦 Alcance:")
        if incluir_acabados: st.success("✅ Cimentación, Estructura, Pisos, Baños Terminados")
        else: st.info("✅ Cimentación, Estructura, Fachada (Sin Pisos/Enchapes)")
        if es_admin:
            st.warning("🕵️ RADIOGRAFÍA")
            c1b, c2b = st.columns(2)
            c1b.write(f"Mat: ${data['desglose']['materiales']:,.0f}"); c1b.write(f"MO: ${data['desglose']['mano_obra']:,.0f}")
            c2b.write(f"Acab: ${data['desglose']['acabados']:,.0f}"); c2b.success(f"Util: ${data['utilidad']:,.0f}")
        if st.text_input("Cliente:"):
            desc = f"Modelo Domo V7. Dim: {ancho}x{fondo}m. Distribución: {distribucion}."
            st.download_button("Descargar Cotización", generar_pdf_cotizacion("Cliente", "Domo V7", data, desc, incluir_acabados), "cotizacion_domo.pdf")
    with c2:
        if distribucion == "Open Loft (Turista)":
            try: st.image("Loft_rural.png", caption="Modelo Rural Ecoturismo", use_container_width=True)
            except: st.info("Sube 'Loft_rural.png'")
        else:
            try: st.image("vis_familiar.png", caption="Modelo Familiar", use_container_width=True)
            except: st.info("Sube 'vis_familiar.png'")

# ==========================================
# 🎨 VISTA: MUROS
# ==========================================
elif st.session_state.view == 'muros':
    st.button("⬅️ Volver", on_click=lambda: set_view('home')); st.header("🛡️ Cotizador Muros")
    c1, c2 = st.columns([1, 1.5])
    with c1:
        ml = st.number_input("Metros Lineales:", 50.0); got = st.checkbox("Gotero", True)
        data = calcular_proyecto({'area': ml*2.2, 'ml': ml}, tipo="muro", tiene_gotero=got, incluye_acabados=False)
        st.metric("VALOR TOTAL", f"${data['precio']:,.0f}")
        st.success("✅ Estructura + Cimentación Corrida + Acabado Impermeable")
        if es_admin:
            st.warning("🕵️ RADIOGRAFÍA")
            st.write(f"Mat: ${data['desglose']['materiales']:,.0f} | MO: ${data['desglose']['mano_obra']:,.0f}")
            st.success(f"Util: ${data['utilidad']:,.0f}")
        if st.text_input("Cliente:"): st.download_button("PDF", generar_pdf_cotizacion("Cliente", "Muro", data, "Muro Perimetral Ferrotek", False), "muro.pdf")
    with c2:
        try: st.image("muro_perimetral.png", caption="Muro Blindado con Gotero", use_container_width=True)
        except: st.info("Sube imagen 'muro_perimetral.png'")

# ==========================================
# 🎨 VISTA: VIVIENDAS
# ==========================================
elif st.session_state.view == 'viviendas':
    st.button("⬅️ Volver", on_click=lambda: set_view('home')); st.header("🏠 Cotizador Vivienda Recta")
    c1, c2 = st.columns([1, 1.5])
    with c1:
        mod = st.selectbox("Modelo", ["Suite 30m2", "Familiar 54m2", "Máster 72m2 (3 Hab)"])
        area = int(mod.split()[1].replace("m2","")) * 3.5
        incluir_acabados = st.checkbox("Incluir Acabados (Llave en Mano)", value=True)
        data = calcular_proyecto({'area': area}, tipo="vivienda", incluye_acabados=incluir_acabados)
        titulo_precio = "VALOR LLAVE EN MANO" if incluir_acabados else "VALOR OBRA GRIS"
        st.metric(titulo_precio, f"${data['precio']:,.0f}")
        if incluir_acabados: st.success("✅ Obra Blanca Habitable")
        else: st.info("✅ Estructura Unibody (Sin Pisos/Enchapes)")
        if es_admin:
            st.warning("🕵️ RADIOGRAFÍA")
            st.write(f"Mat: ${data['desglose']['materiales']:,.0f} | MO: ${data['desglose']['mano_obra']:,.0f}")
            st.success(f"Util: ${data['utilidad']:,.0f}")
        if st.text_input("Cliente:"): st.download_button("PDF", generar_pdf_cotizacion("Cliente", mod, data, "Vivienda Unibody Recta", incluir_acabados), "casa.pdf")
    with c2:
        img_file = "vivienda_suite.png"
        if "Familiar" in mod: img_file = "vivienda_familiar.png"
        elif "Máster" in mod: img_file = "vivienda_master.png"
        try: st.image(img_file, caption=f"Render Modelo {mod}", use_container_width=True)
        except: st.info(f"Sube imagen '{img_file}'")

# ==========================================
# 🏭 VISTA FÁBRICA
# ==========================================
elif st.session_state.view == 'fabrica':
    st.button("⬅️ Volver", on_click=lambda: set_view('home')); st.header("🏭 Fábrica de Mezclas V7.0")
    if not es_admin:
        st.error("⛔ ACCESO RESTRINGIDO"); st.info("Ingrese contraseña.")
    else:
        st.success("🔓 Ingeniero en Línea")
        col_mix1, col_mix2 = st.columns(2)
        with col_mix1:
            st.subheader("🧪 Calculadora")
            tipo = st.selectbox("Receta:", ["Industrial (Batch 100)", "Manual (1:2.5)", "Piel de Roca (1:3:3)", "Thermo (Zeolita)"])
            qty = st.number_input("Bultos (30kg):", 10)
        res = calcular_produccion_lote(tipo, qty)
        with col_mix2:
            st.markdown("### 📋 Orden Producción")
            st.table(pd.DataFrame(list(res.items()), columns=["Insumo", "Kg"]))
        st.markdown("---")
        st.subheader("📂 Documentación Confidencial")
        archivo_manual = "MANUAL TÉCNICO CONSTRUCTIVO - SISTEMA FERROTEK ® Versión 7.0.pdf"
        if os.path.exists(archivo_manual):
            with open(archivo_manual, "rb") as pdf_file:
                st.download_button("⬇️ Descargar Manual V7 (Privado)", pdf_file, "Manual_V7.pdf", "application/pdf")
        else: st.warning("Manual PDF no encontrado.")