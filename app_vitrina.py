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
def calcular_proyecto(input_data, tipo="general", tiene_gotero=False):
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
        costo_acabados = (ancho*fondo) * P.get('valor_acabados_vis_m2', 350000)
        
        costo_total = costo_mat + costo_mo + costo_acabados
        return {
            "precio": costo_total/(1-margen), 
            "utilidad": (costo_total/(1-margen))-costo_total,
            "costo_total": costo_total,
            "desglose": {"materiales": costo_mat, "mano_obra": costo_mo, "acabados": costo_acabados}
        }

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
        acabados = (area_m2/3.5 * P.get('valor_acabados_m2', 450000)) if tipo=="vivienda" else 0
        
        total = costo_mat + mo + extra + acabados
        return {
            "precio": total/(1-margen), 
            "utilidad": (total/(1-margen))-total,
            "costo_total": total,
            "desglose": {"materiales": costo_mat, "mano_obra": mo, "acabados": acabados}
        }

# ==========================================
# 📄 PDF GENERATOR
# ==========================================
class PDFBase(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16); self.cell(0, 10, 'FERROTEK S.A.S', 0, 1, 'C')
        self.set_font('Arial', 'I', 10); self.cell(0, 10, 'Ingeniería Unibody & Construcción Monolítica', 0, 1, 'C'); self.ln(10)

def generar_pdf_cotizacion(cliente, obra, datos, desc):
    pdf = PDFBase(); pdf.add_page(); pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Cliente: {cliente} | Fecha: {datetime.now().strftime('%d/%m/%Y')}", 0, 1)
    pdf.cell(0, 10, f"Proyecto: {obra}", 0, 1); pdf.ln(5)
    
    # SECCIÓN DE ALCANCE (CARACTERES SEGUROS)
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "ALCANCE DE LA ENTREGA (LLAVE EN MANO)", 0, 1)
    pdf.set_font('Arial', '', 10)
    alcance = (
        "- Estructura: Sistema Sismo-Resistente en Acero Galvanizado Certificado.\n"
        "- Muros: Ferrocemento de alta resistencia (Batch 100) con aislamiento térmico.\n"
        "- Fachada: Acabado 'Piel de Roca' impermeable y monolítico (Sin mantenimiento).\n"
        "- Instalaciones: Red hidrosanitaria y eléctrica interna completa (puntos).\n"
        "- Acabados: Pisos, enchapes de baño, ventanería y puertas entamboradas.\n"
        "- NOTA: No incluye lote, acometidas externas ni licencias."
    )
    pdf.multi_cell(0, 6, alcance); pdf.ln(10)

    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "ESPECIFICACIONES DEL MODELO", 0, 1)
    pdf.set_font('Arial', '', 11); pdf.multi_cell(0, 7, desc); pdf.ln(5)
    pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, f"INVERSIÓN TOTAL: ${datos['precio']:,.0f}", 0, 1)
    pdf.ln(5); pdf.set_font('Arial', 'I', 8); pdf.cell(0, 10, "Cálculo optimizado Manual Técnico Ferrotek V7.0", 0, 1)
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
    pdf.set_font('Arial', 'B', 26); pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 15, 'FERROTEK (R) BOVEDA EVOLUTIVA', 0, 1, 'C')
    pdf.set_font('Arial', 'I', 14); pdf.set_text_color(100, 100, 100); pdf.cell(0, 10, 'La Revolucion del Espacio en 60 m2', 0, 1, 'C'); pdf.ln(5)
    if os.path.exists("Loft_rural.png"): pdf.image("Loft_rural.png", x=20, y=50, w=170); pdf.ln(100)
    else: pdf.ln(10); pdf.cell(0, 10, "[FOTO EXTERIOR AQUI]", 1, 1, 'C')
    pdf.set_y(160); pdf.set_font('Arial', 'B', 16); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, '¿Cansado de la "Caja de Fosforos"?', 0, 1, 'C')
    pdf.set_font('Arial', '', 12); pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 6, "En Colombia, el lote tradicional de 6x10m se ha convertido en sinónimo de oscuridad y calor.\nFERROTEK ROMPE EL MOLDE.\nUtilizamos la ingeniería de arcos para darle lo que nadie más ofrece: LUZ, ALTURA y FRESCURA NATURAL.", align='C')
    pdf.add_page(); pdf.set_font('Arial', 'B', 18); pdf.set_text_color(0, 51, 102); pdf.cell(0, 10, 'UN DISEÑO, DOS POSIBILIDADES', 0, 1, 'L'); pdf.ln(5)
    if os.path.exists("vis_loft.png"): pdf.image("vis_loft.png", x=15, y=30, w=80)
    if os.path.exists("vis_familiar.png"): pdf.image("vis_familiar.png", x=105, y=30, w=80)
    pdf.ln(70); pdf.set_font('Arial', 'B', 12); pdf.set_text_color(0, 0, 0)
    y_start = pdf.get_y(); pdf.set_xy(10, y_start); pdf.multi_cell(90, 6, "OPCION A: OPEN LOFT (Turismo)\n\nEspacio continuo sin divisiones. Ideal para Glamping.")
    pdf.set_xy(105, y_start); pdf.multi_cell(90, 6, "OPCION B: FAMILIAR (2 Hab)\n\nAprovechamiento vertical inteligente. Incluye Mezzanine.")
    pdf.ln(10); pdf.set_fill_color(240, 240, 240); pdf.rect(10, pdf.get_y(), 190, 40, 'F'); pdf.set_xy(15, pdf.get_y()+5)
    pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, 'EL AS BAJO LA MANGA: EL MEZZANINE', 0, 1)
    pdf.set_font('Arial', '', 11); pdf.multi_cell(180, 6, "Gracias a la geometría curva, su casa gana altura en el centro. Permite instalar un entrepiso liviano, convirtiendo sus 60 m2 en casi 85 m2 útiles.")
    pdf.add_page(); pdf.set_font('Arial', 'B', 18); pdf.set_text_color(0, 51, 102); pdf.cell(0, 10, 'TECNOLOGIA QUE PROTEGE SU INVERSION', 0, 1, 'L'); pdf.ln(10)
    pdf.set_font('Arial', 'B', 13); pdf.set_text_color(0,0,0); pdf.cell(0, 8, "1. THERMO-SHIELD (Adios al Calor)", 0, 1); pdf.set_font('Arial', '', 11); pdf.multi_cell(0, 6, "Paredes que respiran con Zeolita. Hasta 4 grados más fresco."); pdf.ln(5)
    pdf.set_font('Arial', 'B', 13); pdf.cell(0, 8, "2. ACABADO PIEL DE ROCA", 0, 1); pdf.set_font('Arial', '', 11); pdf.multi_cell(0, 6, "Olvídese de estucar y pintar. Superficie pétrea, impermeable y lavable."); pdf.ln(5)
    pdf.set_font('Arial', 'B', 13); pdf.cell(0, 8, "3. SISMO-RESISTENCIA", 0, 1); pdf.set_font('Arial', '', 11); pdf.multi_cell(0, 6, "Estructura de Acero Galvanizado continua (Unibody)."); pdf.ln(15)
    pdf.set_draw_color(0, 51, 102); pdf.rect(30, 160, 150, 40); pdf.set_y(165); pdf.set_font('Arial', 'B', 16); pdf.cell(0, 10, '¡VISITE NUESTRA CASA MODELO!', 0, 1, 'C')
    return bytes(pdf.output(dest='S'))

def generar_dossier_tecnico():
    pdf = PDFDossier(); pdf.add_page()
    pdf.set_font('Arial', 'B', 20); pdf.set_text_color(0, 51, 102); pdf.cell(0, 10, 'SISTEMA CONSTRUCTIVO FERROTEK (R)', 0, 1, 'C')
    pdf.set_font('Arial', 'I', 12); pdf.set_text_color(80, 80, 80); pdf.cell(0, 8, 'Híbrido de Alta Eficiencia: Steel Frame + Ferrocemento', 0, 1, 'C'); pdf.ln(5)
    pdf.set_font('Arial', 'B', 12); pdf.set_text_color(0, 0, 0); pdf.cell(0, 8, '1. FUNDAMENTO DE INGENIERIA', 0, 1)
    pdf.set_font('Arial', '', 10); pdf.multi_cell(0, 5, "Ferrotek fusiona la precisión del Steel Framing con la resistencia monolítica del Ferrocemento. Resistencia por FORMA. Estructuras 50% más livianas."); pdf.ln(8)
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 8, '2. VENTAJAS COMPETITIVAS', 0, 1); pdf.ln(2)
    col_var, col_trad, col_ferro = 35, 75, 75
    pdf.set_font('Arial', 'B', 10); pdf.set_fill_color(230, 230, 230)
    pdf.cell(col_var, 8, "VARIABLE", 1, 0, 'C', 1); pdf.cell(col_trad, 8, "TRADICIONAL", 1, 0, 'C', 1); pdf.cell(col_ferro, 8, "FERROTEK", 1, 1, 'C', 1)
    pdf.set_font('Arial', '', 9); y_b = pdf.get_y()
    pdf.cell(col_var, 12, "VELOCIDAD", 1, 0, 'C'); pdf.set_xy(10+col_var, y_b); pdf.multi_cell(col_trad, 6, "LENTA\n(Fraguados, mucha MO)", 1, 'C'); pdf.set_xy(10+col_var+col_trad, y_b); pdf.multi_cell(col_ferro, 6, "RAPIDA\n(Montaje seco + Proyeccion)", 1, 'C')
    y_b = pdf.get_y(); pdf.cell(col_var, 12, "PESO", 1, 0, 'C'); pdf.set_xy(10+col_var, y_b); pdf.multi_cell(col_trad, 6, "PESADO\n(Cimentacion profunda)", 1, 'C'); pdf.set_xy(10+col_var+col_trad, y_b); pdf.multi_cell(col_ferro, 6, "LIVIANO\n(Ideal laderas)", 1, 'C')
    y_b = pdf.get_y(); pdf.cell(col_var, 12, "ACABADO", 1, 0, 'C'); pdf.set_xy(10+col_var, y_b); pdf.multi_cell(col_trad, 6, "COSTOSO\n(Requiere panete y pintura)", 1, 'C'); pdf.set_xy(10+col_var+col_trad, y_b); pdf.multi_cell(col_ferro, 6, "PIEL DE ROCA\n(Directo e impermeable)", 1, 'C')
    pdf.ln(10); pdf.add_page(); pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, '3. APLICACIONES Y VERSATILIDAD', 0, 1)
    pdf.set_font('Arial', '', 10); pdf.multi_cell(0, 5, "A. VIVIENDA (VIS): Elimina costos de cubierta.\nB. TANQUES: Impermeabilidad superior.\nC. TURISMO: Arquitectura organica sin encofrados.")
    pdf.ln(5); pdf.set_fill_color(240, 240, 240); pdf.rect(10, pdf.get_y(), 190, 45, 'F'); pdf.set_xy(15, pdf.get_y()+5)
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 8, '4. ESPECIFICACIONES TECNICAS', 0, 1)
    # --- AQUÍ ESTABA EL ERROR DE CARÁCTER ---
    pdf.set_font('Arial', '', 10); pdf.multi_cell(180, 6, "- ESQUELETO: Perfilería PGC 90mm Certificada (Z275).\n- ARMADURA: Malla Electrosoldada + Malla Zaranda.\n- MATRIZ: Mortero Alta Resistencia (Batch 100).\n- ACABADO: Piel de Roca.")
    pdf.ln(20); pdf.set_draw_color(150); pdf.line(10, pdf.get_y(), 200, pdf.get_y()); pdf.ln(5)
    pdf.set_font('Arial', 'B', 11); pdf.cell(0, 6, "Contacto Comercial y Asesoria Tecnica", 0, 1, 'C'); pdf.cell(0, 6, "Bucaramanga - Colombia", 0, 1, 'C')
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
    st.subheader("📂 Centro de Documentación")
    col_d1, col_d2 = st.columns(2)
    with col_d1: st.download_button("Descargar Dossier Comercial (Bóveda VIS)", generar_dossier_comercial(), "Ferrotek_Comercial.pdf", "application/pdf")
    with col_d2: st.download_button("Descargar Ficha Técnica (Sistema)", generar_dossier_tecnico(), "Ferrotek_Tecnico.pdf", "application/pdf")
    st.markdown("---")
    imgs = [f for f in os.listdir('.') if f.endswith(('.png','.jpg'))]
    if imgs:
        st.subheader("📸 Galería")
        c = st.columns(3)
        for i, f in enumerate(imgs): c[i%3].image(f, caption=f, use_container_width=True)

# ==========================================
# 🎨 VISTA: DOMOS (LLAVE EN MANO)
# ==========================================
elif st.session_state.view == 'domos':
    st.button("⬅️ Volver", on_click=lambda: set_view('home'))
    st.header("🌾 Domos & Bóvedas Evolutivas")
    c1, c2 = st.columns([1, 1.5]) 
    with c1:
        distribucion = st.radio("Modelo:", ["Open Loft (Turista)", "Familiar (2 Hab)"])
        ancho = st.number_input("Frente (m):", 6.0, disabled=True)
        fondo = st.number_input("Fondo (m):", 10.0)
        data = calcular_proyecto({'ancho': ancho, 'fondo': fondo}, tipo="domo_boveda")
        st.markdown("---")
        st.metric("VALOR LLAVE EN MANO", f"${data['precio']:,.0f}")
        st.markdown("##### 📦 ¿Qué incluye este precio?")
        st.success("✅ Cimentación y Estructura Sismo-Resistente")
        st.success("✅ Fachada Piel de Roca (Impermeable)")
        st.success("✅ Aislamiento Thermo-Shield (Zeolita)")
        st.success("✅ Puntos Hidráulicos y Eléctricos")
        st.success("✅ Pisos, Baños y Ventanería")
        st.caption("⛔ No incluye: Lote ni Licencias.")
        if es_admin:
            st.warning("🕵️ RADIOGRAFÍA DE COSTOS")
            c1b, c2b = st.columns(2)
            c1b.write(f"Mat: ${data['desglose']['materiales']:,.0f}"); c1b.write(f"MO: ${data['desglose']['mano_obra']:,.0f}")
            c2b.write(f"Acab: ${data['desglose']['acabados']:,.0f}"); c2b.success(f"Util: ${data['utilidad']:,.0f}")
        if st.text_input("Cliente:"):
            desc = f"Modelo Domo V7. Dim: {ancho}x{fondo}m. Distribución: {distribucion}."
            st.download_button("Descargar Cotización", generar_pdf_cotizacion("Cliente", "Domo V7", data, desc), "cotizacion_domo.pdf")
    with c2:
        if distribucion == "Open Loft (Turista)":
            try: st.image("Loft_rural.png", caption="Modelo Rural Ecoturismo", use_container_width=True)
            except: st.info("Sube 'Loft_rural.png'")
        else:
            try: st.image("vis_familiar.png", caption="Modelo Familiar", use_container_width=True)
            except: st.info("Sube 'vis_familiar.png'")

# ==========================================
# 🎨 VISTA: MUROS (VISUAL)
# ==========================================
elif st.session_state.view == 'muros':
    st.button("⬅️ Volver", on_click=lambda: set_view('home')); st.header("🛡️ Cotizador Muros")
    c1, c2 = st.columns([1, 1.5])
    with c1:
        ml = st.number_input("Metros Lineales:", 50.0); got = st.checkbox("Gotero", True)
        data = calcular_proyecto({'area': ml*2.2, 'ml': ml}, tipo="muro", tiene_gotero=got)
        st.metric("VALOR TOTAL", f"${data['precio']:,.0f}")
        st.success("✅ Estructura + Cimentación Corrida")
        st.success("✅ Acabado Impermeable (Ambas Caras)")
        if es_admin:
            st.warning("🕵️ RADIOGRAFÍA")
            st.write(f"Mat: ${data['desglose']['materiales']:,.0f} | MO: ${data['desglose']['mano_obra']:,.0f}")
            st.success(f"Util: ${data['utilidad']:,.0f}")
        if st.text_input("Cliente:"): st.download_button("PDF", generar_pdf_cotizacion("Cliente", "Muro", data, "Muro Perimetral Ferrotek"), "muro.pdf")
    with c2:
        try: st.image("muro_perimetral.png", caption="Muro Blindado con Gotero", use_container_width=True)
        except: st.info("Sube imagen 'muro_perimetral.png'")

# ==========================================
# 🎨 VISTA: VIVIENDAS (3 OPCIONES)
# ==========================================
elif st.session_state.view == 'viviendas':
    st.button("⬅️ Volver", on_click=lambda: set_view('home')); st.header("🏠 Cotizador Vivienda Recta")
    c1, c2 = st.columns([1, 1.5])
    with c1:
        mod = st.selectbox("Modelo", ["Suite 30m2", "Familiar 54m2", "Máster 72m2 (3 Hab)"])
        area = int(mod.split()[1].replace("m2","")) * 3.5
        data = calcular_proyecto({'area': area}, tipo="vivienda")
        st.metric("VALOR LLAVE EN MANO", f"${data['precio']:,.0f}")
        st.markdown("##### 📦 Entrega Full:")
        st.success("✅ Obra Blanca Habitable")
        st.success("✅ Baños y Cocina Enchapados")
        st.success("✅ Estructura Unibody Sismo-Resistente")
        if es_admin:
            st.warning("🕵️ RADIOGRAFÍA")
            st.write(f"Mat: ${data['desglose']['materiales']:,.0f} | MO: ${data['desglose']['mano_obra']:,.0f}")
            st.success(f"Util: ${data['utilidad']:,.0f}")
        if st.text_input("Cliente:"): st.download_button("PDF", generar_pdf_cotizacion("Cliente", mod, data, "Vivienda Unibody Recta"), "casa.pdf")
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
                st.download_button("⬇️ Descargar Manual V7", pdf_file, "Manual_V7.pdf", "application/pdf")
        else: st.warning("Manual PDF no encontrado.")