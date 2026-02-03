import streamlit as st
import pandas as pd
import math
from fpdf import FPDF
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURACIÓN GENERAL
# ==========================================
st.set_page_config(page_title="Ferrotek | Tablero de Control", page_icon="🏗️", layout="wide")

# ==========================================
# 🧠 MOTOR DE CÁLCULO (DOBLE RECETA: RELLENO vs PIEL)
# ==========================================
def calcular_proyecto_al_detalle(area_m2):
    P = st.session_state['precios_reales']
    margen_decimal = st.session_state['margen'] / 100
    
    # 1. VOLÚMENES (Espesor total 4cm + 5% desperdicio)
    vol_total_m3 = area_m2 * 0.04 * 1.05
    
    # Dividimos el muro en dos capas técnicas
    vol_relleno = vol_total_m3 * 0.70  # 70% Estructural
    vol_acabado = vol_total_m3 * 0.30  # 30% Piel de Roca
    
    # -------------------------------------------------------
    # 2. RECETA 1: RELLENO ESTRUCTURAL (Proporción 1:3 Cemento:Arena)
    # -------------------------------------------------------
    # Rendimiento aprox: 8.5 bultos cemento (50kg) por m3 de mortero 1:3
    cemento_relleno = vol_relleno * 8.5 
    arena_relleno   = vol_relleno * 1.1 # m3 arena
    cal_relleno     = 0 # El relleno es fuerte, sin cal (o muy poca)

    # -------------------------------------------------------
    # 3. RECETA 2: PIEL DE ROCA (Proporción 1:3:3 Cemento:Cal:Arena)
    # -------------------------------------------------------
    # Esta mezcla lleva menos cemento y mucha cal.
    # Rendimiento aprox: 4.5 bultos cemento (50kg) por m3 de mezcla 1:3:3
    # Cal (25kg): Por volumen, 3 partes cal vs 1 cemento. 
    # Si usamos 4.5 btos cemento, necesitamos ~10 btos de cal de 25kg (por densidad)
    cemento_piel = vol_acabado * 4.5
    cal_piel     = vol_acabado * 10.0 
    arena_piel   = vol_acabado * 1.1

    # -------------------------------------------------------
    # 4. TOTALES DE COMPRA
    # -------------------------------------------------------
    total_cemento = math.ceil(cemento_relleno + cemento_piel)
    total_cal     = math.ceil(cal_piel) # Solo la piel lleva carga fuerte de cal
    total_arena   = (arena_relleno + arena_piel)
    
    total_malla   = area_m2 * 2.1 # Malla no cambia
    total_perfil  = area_m2 * 1.2
    
    # Costo Directo Materiales
    costo_materiales = (
        (total_cemento * P.get('cemento_gris_50kg', 29500)) +
        (total_cal * P.get('cal_hidratada_25kg', 25000)) +    
        (total_arena * P.get('arena_rio_m3', 98000)) +
        (total_malla * P.get('malla_5mm_m2', 28000)) +
        (total_perfil * P.get('perfil_c18_ml', 11500)) +
        (area_m2 * 5000) # Insumos menores
    )

    # Costo Directo Mano de Obra
    rendimiento = P.get('rendimiento_dia', 4.0)
    dias = math.ceil(area_m2 / rendimiento)
    costo_mo = dias * P.get('dia_cuadrilla', 250000)
    
    # Totales Financieros
    costo_total = costo_materiales + costo_mo
    precio_venta = costo_total / (1 - margen_decimal)
    utilidad = precio_venta - costo_total
    
    # Logística de Bultos (Para transporte)
    # Relleno (Tipo R) vs Acabado (Tipo A)
    bultos_r = math.ceil((vol_relleno * 1000) / 16)
    bultos_a = math.ceil((vol_acabado * 1000) / 16)
    
    return {
        "raw_mat": costo_materiales,
        "raw_mo": costo_mo,
        "raw_total": costo_total,
        "precio_venta": precio_venta,
        "utilidad": utilidad,
        "logistica": {"total_30kg": bultos_r + bultos_a, "R": bultos_r, "A": bultos_a},
        "insumos": {"cemento": total_cemento, "cal": total_cal} # Datos clave para ti
    }

# ==========================================
# 📄 PDF FORMAL
# ==========================================
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'FERROTEK S.A.S - COTIZACION', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, 'Ingeniería Unibody & Construcción Monolítica', 0, 1, 'C')
        self.line(10, 30, 200, 30)
        self.ln(10)

def generar_pdf(cliente, obra, area, datos):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", 0, 1)
    pdf.cell(0, 10, f"Cliente: {cliente}", 0, 1)
    pdf.cell(0, 10, f"Proyecto: {obra} ({area} m2)", 0, 1)
    pdf.ln(5)
    
    # LOGÍSTICA
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "LOGÍSTICA DE MATERIALES (SISTEMA 30KG)", 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 7, f"- Bultos Tipo R (Estructural 1:3): {datos['logistica']['R']} Unidades", 0, 1)
    pdf.cell(0, 7, f"- Bultos Tipo A (Piel Roca 1:3:3): {datos['logistica']['A']} Unidades", 0, 1)
    pdf.cell(0, 7, f"TOTAL: {datos['logistica']['total_30kg']} Bultos", 0, 1)
    pdf.ln(5)
    
    # COSTOS
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "INVERSIÓN", 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(100, 8, "Valor Total del Proyecto", 1)
    pdf.cell(50, 8, f"${datos['precio_venta']:,.0f}", 1, 1)
    
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 🎛️ PANEL GERENCIAL
# ==========================================
with st.sidebar:
    st.title("🎛️ Panel Gerencial")
    pwd = st.text_input("Contraseña:", type="password")
    
    defaults = {
        'cemento_gris_50kg': 29500, 
        'cal_hidratada_25kg': 25000,   
        'arena_rio_m3': 98000, 
        'malla_5mm_m2': 28000, 
        'perfil_c18_ml': 11500,
        'dia_cuadrilla': 250000, 
        'rendimiento_dia': 4.0
    }
    
    if 'precios_reales' not in st.session_state: st.session_state['precios_reales'] = defaults
    if 'margen' not in st.session_state: st.session_state['margen'] = 30 

    es_admin = (pwd == "ferrotek2026")

    if es_admin:
        st.success("🔓 Edición Activa")
        st.divider()
        st.header("📈 Margen Utilidad")
        margen = st.slider("% Ganancia", 0, 60, st.session_state['margen'])
        st.session_state['margen'] = margen
        
        st.divider()
        st.header("🧱 Costos Insumos")
        edited = st.data_editor(st.session_state['precios_reales'], key="grid_precios", num_rows="fixed")
        st.session_state['precios_reales'] = edited
    else:
        st.info("Ingrese contraseña para ver costos reales.")

if 'view' not in st.session_state: st.session_state.view = 'home'
def set_view(name): st.session_state.view = name

# ==========================================
# 🎨 VISTAS
# ==========================================
if st.session_state.view == 'home':
    st.title("🏗️ FERROTEK: Sistema de Gestión")
    c1, c2 = st.columns(2)
    with c1: 
        if st.button("🛡️ Cotizar Muros", key="nav_muros"): set_view('muros')
    with c2: 
        if st.button("🏠 Cotizar Casas", key="nav_casas"): set_view('viviendas')

elif st.session_state.view == 'muros':
    st.button("⬅️ Volver", on_click=lambda: set_view('home'))
    st.header("🛡️ Cotizador de Muros")
    
    ml = st.number_input("Metros Lineales:", value=50.0)
    area = ml * 2.2
    
    finanzas = calcular_proyecto_al_detalle(area)
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📦 Logística (Bultos 30kg)")
        st.write(f"**Total Despacho: {finanzas['logistica']['total_30kg']} bultos**")
        st.info(f"Tipo R (1:3): {finanzas['logistica']['R']} btos")
        st.success(f"Tipo A (1:3:3): {finanzas['logistica']['A']} btos")
        
        if es_admin:
            st.markdown("---")
            st.caption("Consumo interno estimado (Receta 1:3:3 + 1:3):")
            st.caption(f"- Cemento (50kg): {finanzas['insumos']['cemento']} bultos")
            st.caption(f"- Cal (25kg): {finanzas['insumos']['cal']} bultos")

    with c2:
        st.subheader("💰 Inversión")
        st.metric("Precio Cliente", f"${finanzas['precio_venta']:,.0f}")
        if es_admin:
            st.warning(f"Utilidad Neta: ${finanzas['utilidad']:,.0f}")
            
    nom = st.text_input("Cliente:")
    if nom:
        pdf = generar_pdf(nom, f"Muro {ml}ml", area, finanzas)
        st.download_button("Descargar PDF", pdf, "cotizacion.pdf", "application/pdf")

elif st.session_state.view == 'viviendas':
    st.button("⬅️ Volver", on_click=lambda: set_view('home'))
    st.header("🏠 Cotizador de Vivienda")
    
    col_sel, col_img = st.columns([1,1])
    with col_sel:
        modelo = st.selectbox("Modelo", ["Suite 30m2", "Familiar 54m2", "Máster 84m2"])
        area_real = int(modelo.split()[1].replace("m2","")) * 3.5 
    with col_img:
        img_map = {"Suite 30m2": "render_modelo1.png", "Familiar 54m2": "render_modelo2.png", "Máster 84m2": "render_modelo3.png"}
        try: st.image(img_map[modelo], width=200)
        except: pass

    # Cálculos
    finanzas = calcular_proyecto_al_detalle(area_real)
    factor = 1.25
    precio_final = finanzas['precio_venta'] * factor
    costo_final = finanzas['raw_total'] * factor
    utilidad_final = finanzas['utilidad'] * factor

    st.markdown("---")
    c_log, c_fin = st.columns(2)
    
    with c_log:
        st.subheader("📦 Logística Estimada")
        st.write(f"**Bultos 30kg (Estructura): {finanzas['logistica']['total_30kg']}**")
        st.caption(f"Tipo R: {finanzas['logistica']['R']} | Tipo A: {finanzas['logistica']['A']}")
        
    with c_fin:
        st.subheader("💰 Finanzas")
        st.metric("Precio Venta", f"${precio_final:,.0f}")
        
        if es_admin:
            st.error("🕵️ CONTROL INTERNO")
            col_a, col_b = st.columns(2)
            col_a.metric("Costo Real", f"${costo_final:,.0f}")
            col_b.metric("Utilidad", f"${utilidad_final:,.0f}", delta=f"{st.session_state['margen']}%")
            
    nom = st.text_input("Cliente PDF:")
    if nom:
        datos_pdf = finanzas.copy()
        datos_pdf['precio_venta'] = precio_final
        pdf_data = generar_pdf(nom, modelo, int(area_real/3.5), datos_pdf)
        st.download_button("Descargar PDF", pdf_data, "Cotizacion.pdf", "application/pdf")