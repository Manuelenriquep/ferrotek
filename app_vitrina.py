import streamlit as st
import pandas as pd
import math
import os
from fpdf import FPDF
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURACIÓN GENERAL
# ==========================================
st.set_page_config(page_title="Ferrotek | ERP Integral", page_icon="🏗️", layout="wide")

# ==========================================
# 🧪 MÓDULO FÁBRICA
# ==========================================
DENSIDAD = {'cemento': 1.50, 'arena': 1.60, 'cal': 0.55}

def calcular_produccion_lote(tipo_mezcla, cantidad_bultos_30kg):
    peso_meta = cantidad_bultos_30kg * 30
    insumos = {}
    
    if "Relleno" in tipo_mezcla: 
        peso_vol = (3 * DENSIDAD['arena']) + (1 * DENSIDAD['cemento'])
        if peso_vol > 0:
            units = peso_meta / peso_vol
            insumos = {'arena_L': units*3, 'cemento_L': units*1, 'cal_L': 0}
    elif "Acabado" in tipo_mezcla: 
        peso_vol = (3 * DENSIDAD['arena']) + (3 * DENSIDAD['cal']) + (1 * DENSIDAD['cemento'])
        if peso_vol > 0:
            units = peso_meta / peso_vol
            insumos = {'arena_L': units*3, 'cal_L': units*3, 'cemento_L': units*1}
    
    if not insumos: return {}

    insumos['arena_kg'] = insumos['arena_L'] * DENSIDAD['arena']
    insumos['cemento_kg'] = insumos['cemento_L'] * DENSIDAD['cemento']
    insumos['cal_kg'] = insumos.get('cal_L', 0) * DENSIDAD['cal']
    return insumos

# ==========================================
# 🧠 MOTOR DE COSTOS (V83 - ESTRUCTURA + PACK ACABADOS)
# ==========================================
def calcular_proyecto(area_m2, ml_muro=0, tipo="general", tiene_gotero=False):
    P = st.session_state['precios_reales']
    margen = st.session_state['margen'] / 100
    
    # --- 1. CÁLCULO DE ESTRUCTURA (FERROTEK) ---
    espesor = 0.04 
    factor_malla = 2.1
    factor_perfil = 0.9 
    varillas_refuerzo = 0
    
    if tipo == "estanque":
        espesor = 0.06; varillas_refuerzo = area_m2 * 1.5; factor_perfil = 0
    elif tipo == "boveda":
        espesor = 0.05; varillas_refuerzo = area_m2 * 0.8; factor_perfil = 0
    elif tipo == "vivienda":
        espesor = 0.055; factor_malla = 1.6 # Mixto
    
    vol_total = area_m2 * espesor * 1.05
    vol_relleno = vol_total * 0.70
    vol_acabado = vol_total * 0.30
    
    cemento_tot = (vol_relleno * 8.5) + (vol_acabado * 4.5)
    cal_tot = vol_acabado * 10.0 
    arena_tot = vol_total * 1.1
    
    costo_estructura_mat = (
        (math.ceil(cemento_tot) * P['cemento_gris_50kg']) +
        (math.ceil(cal_tot) * P['cal_hidratada_25kg']) +
        (arena_tot * P['arena_rio_m3']) +
        (area_m2 * factor_malla * P['malla_5mm_m2']) +
        (area_m2 * factor_perfil * P['perfil_c18_ml']) +
        (math.ceil(varillas_refuerzo) * P.get('varilla_refuerzo_6m', 24000)) +
        (area_m2 * 5000)
    )
    
    rendimiento = P.get('rendimiento_dia', 4.5)
    if tipo in ["estanque", "boveda"]: rendimiento = 3.0
    dias = math.ceil(area_m2 / rendimiento)
    costo_mo_estructura = dias * P['dia_cuadrilla']
    
    costo_gotero = 0
    if tiene_gotero and ml_muro > 0: costo_gotero = ml_muro * 25000 
    
    costo_directo_estructura = costo_estructura_mat + costo_mo_estructura + costo_gotero
    
    # --- 2. CÁLCULO DE ACABADOS (PAQUETE LLAVE EN MANO) ---
    costo_acabados = 0
    if tipo == "vivienda":
        valor_m2_acabado = P.get('valor_acabados_m2', 450000)
        area_piso = area_m2 / 3.5 
        costo_acabados = area_piso * valor_m2_acabado

    # --- 3. TOTALES ---
    costo_total_proyecto = costo_directo_estructura + costo_acabados
    precio_venta = costo_total_proyecto / (1 - margen)
    
    # Logística
    b_r = math.ceil((vol_relleno * 1000) / 16)
    b_a = math.ceil((vol_acabado * 1000) / 16)
    
    return {
        "precio": precio_venta, 
        "utilidad": precio_venta - costo_total_proyecto, 
        "costo_total": costo_total_proyecto,
        "desglose": {"estructura": costo_directo_estructura, "acabados": costo_acabados},
        "logistica": {"R": b_r, "A": b_a, "total": b_r + b_a},
        "insumos": {"cemento": cemento_tot, "cal": cal_tot, "varilla": varillas_refuerzo}
    }

# ==========================================
# 📄 PDF GENERATOR (CORREGIDO)
# ==========================================
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'FERROTEK S.A.S', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, 'Ingeniería Unibody & Construcción Monolítica', 0, 1, 'C')
        self.line(10, 30, 200, 30); self.ln(10)

def generar_pdf(cliente, obra, datos, tipo="general", incluye_gotero=False):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", 0, 1)
    pdf.cell(0, 10, f"Cliente: {cliente}", 0, 1)
    pdf.cell(0, 10, f"Proyecto: {obra}", 0, 1); pdf.ln(5)
    
    # SECCIÓN 1: ESTRUCTURA
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "1. ESPECIFICACIONES ESTRUCTURALES", 0, 1)
    pdf.set_font('Arial', '', 11)
    texto_est = (
        "Sistema Ferrotek Unibody Sismo-Resistente.\n"
        "- Muros con alma de acero y mortero estructural de alta resistencia.\n"
        "- Acabado Piel de Roca impermeable (No requiere pintura)."
    )
    if incluye_gotero: texto_est += "\n- Remate superior tipo Gotero."
    pdf.multi_cell(0, 7, texto_est)
    pdf.ln(3)

    # SECCIÓN 2: PAQUETE DE ACABADOS (SOLO VIVIENDA)
    if tipo == "vivienda":
        pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "2. PAQUETE DE ACABADOS E INSTALACIONES", 0, 1)
        pdf.set_font('Arial', '', 10)
        texto_acabados = (
            "El valor 'Llave en Mano' incluye:\n"
            "A. INSTALACIONES: Red eléctrica interna (Puntos tomacorriente, interruptores y rosetas básicos norma RETIE). "
            "Red hidrosanitaria estándar (PVC y CPVC) para baños y cocina.\n"
            "B. PISOS: Cerámica tráfico medio o Piso Polimérico estándar (Según disponibilidad).\n"
            "C. BAÑOS: Combo sanitario estándar (Sanitario + Lavamanos de pedestal) y grifería básica.\n"
            "D. CARPINTERÍA: Puertas internas entamboradas y ventanería en aluminio crudo/natural.\n"
            "NOTA: No incluye cocina integral (solo mesón básico), ni calentador, ni acabados de lujo."
        )
        pdf.multi_cell(0, 6, texto_acabados)
        pdf.ln(5)
    
    # SECCIÓN 3: PRECIO
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "INVERSIÓN TOTAL", 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 10, f"Valor: ${datos['precio']:,.0f}", 0, 1)
    
    pdf.ln(10)
    pdf.set_font('Arial', 'I', 9)
    pdf.cell(0, 10, "Validez: 15 días. Excluye movimiento de tierras y viáticos.", 0, 1)
    
    # --- CORRECCIÓN DEL BUG ---
    # Convertimos el buffer a bytes directamente, sin encode
    return bytes(pdf.output(dest='S'))

# ==========================================
# 🎛️ SIDEBAR
# ==========================================
with st.sidebar:
    st.title("🎛️ Panel Gerente")
    pwd = st.text_input("Contraseña:", type="password")
    
    defaults = {
        'cemento_gris_50kg': 29500, 'cal_hidratada_25kg': 25000, 
        'arena_rio_m3': 98000, 'malla_5mm_m2': 28000, 
        'perfil_c18_ml': 11500, 'varilla_refuerzo_6m': 24000,
        'dia_cuadrilla': 250000, 'rendimiento_dia': 4.5,
        'valor_acabados_m2': 450000 
    }
    if 'precios_reales' not in st.session_state: st.session_state['precios_reales'] = defaults
    if 'margen' not in st.session_state: st.session_state['margen'] = 30
    
    es_admin = (pwd == "ferrotek2026")
    if es_admin:
        st.success("🔓 Admin Activo")
        margen = st.slider("Utilidad %", 0, 60, st.session_state['margen'])
        st.session_state['margen'] = margen
        with st.expander("Costos & Acabados"):
            edited = st.data_editor(st.session_state['precios_reales'], key="p_edit", num_rows="fixed")
            st.session_state['precios_reales'] = edited

if 'view' not in st.session_state: st.session_state.view = 'home'
def set_view(name): st.session_state.view = name

# ==========================================
# 🎨 VISTA 1: HOME
# ==========================================
if st.session_state.view == 'home':
    st.title("🏗️ FERROTEK: Ingeniería Monolítica")
    st.subheader("La evolución inteligente de la construcción tradicional.")
    st.markdown("---")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("### 🛡️ Sismo-Resistente")
        st.write("Estructura continua (Unibody) con alma de acero.")
    with c2:
        st.success("### 🌡️ Confort Térmico")
        st.write("Doble membrana aislante en muros exteriores.")
    with c3:
        st.warning("### 💰 Mínimo Mantenimiento")
        st.write("Acabado Piel de Roca impermeable.")

    st.markdown("---")
    st.subheader("🚀 Cotizadores")
    
    b1, b2, b3, b4 = st.columns(4)
    with b1: 
        if st.button("🛡️ Muros", key="nav_m", use_container_width=True): set_view('muros')
    with b2: 
        if st.button("🏠 Viviendas", key="nav_v", use_container_width=True): set_view('viviendas')
    with b3:
        if st.button("🏺 Especiales", key="nav_e", use_container_width=True): set_view('especiales')
    with b4:
        if st.button("🏭 Fábrica", key="nav_f", use_container_width=True): set_view('fabrica')

    st.markdown("---")
    st.subheader("📸 Galería de Obras")
    archivos = os.listdir('.')
    imagenes = [f for f in archivos if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    if imagenes:
        cols = st.columns(3)
        for i, img_file in enumerate(imagenes):
            with cols[i % 3]:
                st.image(img_file, caption=img_file, use_container_width=True)

# ==========================================
# 🎨 VISTA 2: MUROS
# ==========================================
elif st.session_state.view == 'muros':
    st.button("⬅️ Volver al Inicio", on_click=lambda: set_view('home'))
    st.header("🛡️ Cotizador de Muros")
    
    c_in1, c_in2 = st.columns(2)
    with c_in1:
        ml = st.number_input("Metros Lineales:", value=50.0)
    with c_in2:
        gotero = st.checkbox("Incluir Remate Superior (Gotero)", value=True)
        
    area = ml * 2.2
    data = calcular_proyecto(area, ml_muro=ml, tipo="general", tiene_gotero=gotero)
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Precio Cliente", f"${data['precio']:,.0f}")
        if es_admin:
            st.error("🕵️ DATA PRIVADA")
            st.write(f"Costo: ${data['costo_total']:,.0f} | Utilidad: ${data['utilidad']:,.0f}")
            st.caption(f"Cemento: {data['insumos']['cemento']:.1f} btos")
    with c2:
        try: st.image("image_4.png", use_container_width=True)
        except: pass

    if st.text_input("Nombre Cliente:"):
        pdf = generar_pdf("Cliente", f"Muro {ml}ml", data, tipo="general", incluye_gotero=gotero)
        st.download_button("Descargar PDF", pdf, "muro.pdf")

# ==========================================
# 🎨 VISTA 3: VIVIENDAS
# ==========================================
elif st.session_state.view == 'viviendas':
    st.button("⬅️ Volver al Inicio", on_click=lambda: set_view('home'))
    st.header("🏠 Cotizador de Vivienda")
    
    mod = st.selectbox("Seleccione Modelo", ["Suite 30m2", "Familiar 54m2", "Máster 84m2"])
    area = int(mod.split()[1].replace("m2","")) * 3.5
    
    data = calcular_proyecto(area, tipo="vivienda") 
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Valor Llave en Mano", f"${data['precio']:,.0f}")
        st.info("Incluye estructura, muros, pisos, baño estándar y red eléctrica básica.")
        
        if es_admin:
            st.error("🕵️ DATA PRIVADA")
            st.write(f"Utilidad: ${(data['utilidad']):,.0f}")
            st.write(f"Costo Estructura: ${data['desglose']['estructura']:,.0f}")
            st.write(f"Costo Acabados (Est): ${data['desglose']['acabados']:,.0f}")
            
    with c2:
        img_map = {"Suite 30m2": "render_modelo1.png", "Familiar 54m2": "render_modelo2.png", "Máster 84m2": "render_modelo3.png"}
        try: st.image(img_map[mod], use_container_width=True)
        except: st.error("Imagen no cargada")

    if st.text_input("Nombre Cliente:"):
        pdf = generar_pdf("Cliente", mod, data, tipo="vivienda")
        st.download_button("Descargar PDF", pdf, "casa.pdf")

# ==========================================
# 🎨 VISTA 4: ESPECIALES
# ==========================================
elif st.session_state.view == 'especiales':
    st.button("⬅️ Volver al Inicio", on_click=lambda: set_view('home'))
    st.header("🏺 Proyectos Especiales")
    
    tab1, tab2 = st.tabs(["Bóvedas", "Estanques"])
    with tab1:
        st.subheader("Bóveda (3.80m)")
        largo = st.slider("Largo (m)", 3.0, 15.0, 6.0)
        data_b = calcular_proyecto(largo * 7.5, tipo="boveda") 
        st.metric("Inversión Bóveda", f"${data_b['precio']:,.0f}")
        if es_admin: st.caption(f"Refuerzo: {data_b['insumos']['varilla']:.1f} un")
            
    with tab2:
        st.subheader("Estanque Piscícola")
        diam = st.number_input("Diámetro (m)", 4.0, 20.0, 6.0)
        area_est = (math.pi * diam * 1.2) + (math.pi * (diam/2)**2)
        data_e = calcular_proyecto(area_est, tipo="estanque") 
        st.metric("Inversión Estanque", f"${data_e['precio']:,.0f}")
        if es_admin: st.caption(f"Refuerzo: {data_e['insumos']['varilla']:.1f} un")

# ==========================================
# 🎨 VISTA 5: FÁBRICA
# ==========================================
elif st.session_state.view == 'fabrica':
    st.button("⬅️ Volver al Inicio", on_click=lambda: set_view('home'))
    st.header("🏭 Planta de Producción")
    
    tipo = st.radio("Mezcla:", ["Relleno (3:1)", "Acabado (3:3:1)"], horizontal=True)
    qty = st.number_input("Bultos a Fabricar (30kg):", 10, 500, 20)
    balde = st.selectbox("Balde:", [10, 20], format_func=lambda x: f"{x} Litros")
    res = calcular_produccion_lote(tipo, qty)
    
    if res:
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Arena", f"{round(res['arena_L']/balde, 1)}", "Baldes")
            st.metric("Cemento", f"{round(res['cemento_L']/balde, 1)}", "Baldes")
            if res.get('cal_L', 0) > 0: st.metric("Cal", f"{round(res['cal_L']/balde, 1)}", "Baldes")
        with c2:
            st.table(pd.DataFrame({
                "Insumo": ["Arena", "Cemento", "Cal"],
                "Kg": [f"{res['arena_kg']:.1f}", f"{res['cemento_kg']:.1f}", f"{res.get('cal_kg',0):.1f}"]
            }))