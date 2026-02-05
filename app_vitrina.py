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
            (area_total_envolvente * 0.015 * 1.05 * 2200 / 50 * P['cemento_gris_50kg'] * 0.3) +
            (area_total_envolvente * 0.015 * 1.05 * 2200 * 0.045 * P.get('carbonato_kg', 1500)) +
            (area_total_envolvente * 0.015 * 1.05 * 1.1 * P['arena_rio_m3']) +
            (area_total_envolvente * 2.1 * P['malla_5mm_m2']) +
            ((long_arco * fondo) * P.get('aislante_m2', 12000)) +
            (area_total_envolvente * 5000)
        )
        costo_mo = math.ceil((ancho*fondo)/2.0) * P['dia_cuadrilla'] 
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
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "ESPECIFICACIONES", 0, 1)
    pdf.set_font('Arial', '', 11); pdf.multi_cell(0, 7, desc); pdf.ln(5)
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, f"INVERSIÓN TOTAL: ${datos['precio']:,.0f}", 0, 1)
    pdf.ln(5); pdf.set_font('Arial', 'I', 8); pdf.cell(0, 10, "Cálculo basado en Manual Técnico Ferrotek V7.0", 0, 1)
    return bytes(pdf.output(dest='S'))

class PDFDossier(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 20); self.set_text_color(50, 50, 50)
        self.cell(0, 15, 'FERROTEK ®', 0, 1, 'L'); self.line(10, 25, 200, 25); self.ln(10)
    def footer(self):
        self.set_y(-15); self.set_font('Arial', 'I', 8); self.set_text_color(128)
        self.cell(0, 10, 'Propiedad Intelectual de Manuel Enrique Prada F. - Innovación Colombiana', 0, 0, 'C')

def generar_dossier_comercial():
    pdf = PDFDossier(); pdf.add_page()
    pdf.set_font('Arial', 'B', 24); pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, 'MODELO "BÓVEDA EVOLUTIVA"', 0, 1, 'C')
    pdf.set_font('Arial', 'I', 14); pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 10, 'La Revolución del Espacio en 60 m2', 0, 1, 'C'); pdf.ln(10)
    pdf.set_font('Arial', 'B', 14); pdf.set_text_color(0, 0, 0); pdf.cell(0, 10, '¿Cansado de la "Caja de Fósforos"?', 0, 1)
    pdf.set_font('Arial', '', 11); pdf.multi_cell(0, 6, "En Colombia, el lote tradicional de 6x10m... (Texto Resumido para Dossier)... FERROTEK ROMPE EL MOLDE.")
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, 'FICHA TÉCNICA: SU PRÓXIMO HOGAR', 0, 1)
    pdf.set_font('Arial', '', 11); pdf.multi_cell(0, 6, "- Área: 60 m2\n- Altura: Doble altura curva\n- Distribución: Loft o Familiar (Mezzanine)")
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, 'TECNOLOGÍA Y CONFORT', 0, 1)
    pdf.set_font('Arial', '', 11); pdf.multi_cell(0, 6, "1. Thermo-Shield (Zeolita)\n2. Acabado Piel de Roca\n3. Sismo-Resistencia Steel Frame")
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, '¡VISITE NUESTRA CASA MODELO!', 0, 1, 'C')
    return bytes(pdf.output(dest='S'))

def generar_dossier_tecnico():
    pdf = PDFDossier(); pdf.add_page()
    pdf.set_font('Arial', 'B', 22); pdf.set_text_color(0, 51, 102); pdf.cell(0, 10, 'SISTEMA CONSTRUCTIVO FERROTEK', 0, 1, 'C')
    pdf.set_font('Arial', 'I', 12); pdf.set_text_color(80, 80, 80); pdf.cell(0, 10, 'Híbrido: Steel Frame + Ferrocemento', 0, 1, 'C'); pdf.ln(10)
    pdf.set_font('Arial', 'B', 12); pdf.set_text_color(0, 0, 0); pdf.cell(0, 10, 'FUNDAMENTO', 0, 1)
    pdf.set_font('Arial', '', 10); pdf.multi_cell(0, 5, "Resistencia por FORMA, no por PESO. Estructuras 50% más livianas.")
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 11); pdf.cell(40, 8, "VARIABLE", 1); pdf.cell(75, 8, "TRADICIONAL", 1); pdf.cell(75, 8, "FERROTEK", 1, 1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(40, 8, "Velocidad", 1); pdf.cell(75, 8, "Lenta", 1); pdf.cell(75, 8, "Rápida (Industrializada)", 1, 1)
    pdf.cell(40, 8, "Peso", 1); pdf.cell(75, 8, "Pesado", 1); pdf.cell(75, 8, "Liviano", 1, 1)
    pdf.cell(40, 8, "Acabado", 1); pdf.cell(75, 8, "Requiere Pañete", 1); pdf.cell(75, 8, "Piel de Roca (Directo)", 1, 1)
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
        data = calcular_proyecto({'ancho': ancho, 'fondo': fondo}, tipo="domo_boveda")
        st.markdown("---")
        st.metric("Inversión Total", f"${data['precio']:,.0f}")
        
        # --- DESGLOSE MOSTRADO CORRECTAMENTE ---
        if es_admin:
            st.warning("🕵️ RADIOGRAFÍA DE COSTOS (Privado)")
            col_d1, col_d2 = st.columns(2)
            col_d1.write(f"🔵 Materiales: ${data['desglose']['materiales']:,.0f}")
            col_d1.write(f"👷 Mano de Obra: ${data['desglose']['mano_obra']:,.0f}")
            col_d2.write(f"🏠 Acabados: ${data['desglose']['acabados']:,.0f}")
            col_d2.success(f"💰 Utilidad: ${data['utilidad']:,.0f}")

        if st.text_input("Cliente:"):
            desc = f"Modelo Domo/Bóveda Ferrotek V7. Dim: {ancho}x{fondo}m. Distribución: {distribucion}."
            st.download_button("Descargar Cotización", generar_pdf_cotizacion("Cliente", "Domo V7", data, desc), "cotizacion_domo.pdf")
    with c2:
        if distribucion == "Open Loft (Turista)":
            try: st.image("Loft_rural.png", caption="Modelo Rural Ecoturismo", use_container_width=True)
            except: st.info("Imagen 'Loft_rural.png' no cargada.")
        else:
            try: st.image("vis_familiar.png", caption="Modelo Familiar", use_container_width=True)
            except: st.info("Imagen 'vis_familiar.png' no cargada.")

# ==========================================
# 🎨 VISTA: MUROS (CORREGIDO MO)
# ==========================================
elif st.session_state.view == 'muros':
    st.button("⬅️ Volver", on_click=lambda: set_view('home')); st.header("🛡️ Cotizador Muros")
    ml = st.number_input("Metros Lineales:", 50.0); got = st.checkbox("Gotero", True)
    data = calcular_proyecto({'area': ml*2.2, 'ml': ml}, tipo="muro", tiene_gotero=got)
    st.metric("Precio", f"${data['precio']:,.0f}")
    
    if es_admin:
        st.warning("🕵️ RADIOGRAFÍA DE COSTOS")
        c1, c2 = st.columns(2)
        c1.write(f"🔵 Materiales: ${data['desglose']['materiales']:,.0f}")
        c1.write(f"👷 Mano de Obra: ${data['desglose']['mano_obra']:,.0f}")
        c2.success(f"💰 Utilidad: ${data['utilidad']:,.0f}")

    if st.text_input("Cliente:"): st.download_button("PDF", generar_pdf_cotizacion("Cliente", "Muro", data, "Muro Perimetral Ferrotek"), "muro.pdf")

# ==========================================
# 🎨 VISTA: VIVIENDAS (CORREGIDO MO)
# ==========================================
elif st.session_state.view == 'viviendas':
    st.button("⬅️ Volver", on_click=lambda: set_view('home')); st.header("🏠 Cotizador Vivienda Recta")
    mod = st.selectbox("Modelo", ["Suite 30m2", "Familiar 54m2"])
    area = int(mod.split()[1].replace("m2","")) * 3.5
    data = calcular_proyecto({'area': area}, tipo="vivienda")
    st.metric("Valor", f"${data['precio']:,.0f}")
    
    if es_admin:
        st.warning("🕵️ RADIOGRAFÍA DE COSTOS")
        c1, c2 = st.columns(2)
        c1.write(f"🔵 Estructura (Mat): ${data['desglose']['materiales']:,.0f}")
        c1.write(f"👷 Mano de Obra: ${data['desglose']['mano_obra']:,.0f}")
        c2.write(f"🏠 Acabados: ${data['desglose']['acabados']:,.0f}")
        c2.success(f"💰 Utilidad: ${data['utilidad']:,.0f}")

    if st.text_input("Cliente:"): st.download_button("PDF", generar_pdf_cotizacion("Cliente", mod, data, "Vivienda Unibody Recta"), "casa.pdf")

# ==========================================
# 🏭 VISTA FÁBRICA
# ==========================================
elif st.session_state.view == 'fabrica':
    st.button("⬅️ Volver", on_click=lambda: set_view('home')); st.header("🏭 Fábrica de Mezclas V7.0")
    if not es_admin:
        st.error("⛔ ACCESO RESTRINGIDO")
        st.warning("Área exclusiva para Gerencia e Ingeniería.")
        st.info("Ingrese su contraseña en la barra lateral para acceder.")
    else:
        st.success("🔓 Ingeniero en Línea")
        col_mix1, col_mix2 = st.columns(2)
        with col_mix1:
            st.subheader("🧪 Calculadora de Lotes")
            tipo = st.selectbox("Receta Maestra:", ["Industrial (Batch 100)", "Manual (1:2.5)", "Piel de Roca (1:3:3)", "Thermo (Zeolita)"])
            qty = st.number_input("Bultos de 30kg a Producir:", 10)
        res = calcular_produccion_lote(tipo, qty)
        with col_mix2:
            st.markdown("### 📋 Orden de Producción")
            st.table(pd.DataFrame(list(res.items()), columns=["Insumo", "Cantidad (Kg)"]))
            
        st.markdown("---")
        st.subheader("📂 Documentación Confidencial")
        archivo_manual = "MANUAL TÉCNICO CONSTRUCTIVO - SISTEMA FERROTEK ® Versión 7.0.pdf"
        if os.path.exists(archivo_manual):
            with open(archivo_manual, "rb") as pdf_file:
                st.download_button("⬇️ Descargar Manual V7 (Privado)", pdf_file, "Manual_V7.pdf", "application/pdf")
        else:
            st.warning("Manual PDF no encontrado en servidor.")