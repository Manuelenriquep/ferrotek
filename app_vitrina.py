import streamlit as st
import pandas as pd
import math
from fpdf import FPDF
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURACIÓN GENERAL
# ==========================================
st.set_page_config(page_title="Ferrotek | ERP Integral", page_icon="🏗️", layout="wide")

# ==========================================
# 🧪 INGENIERÍA DE MEZCLAS (DENSIDADES)
# ==========================================
# Esto es vital para que "Volumen" coincida con "Peso"
DENSIDAD = {
    'cemento': 1.50, # kg/litro (aprox)
    'arena': 1.60,   # kg/litro (seca)
    'cal': 0.55      # kg/litro (¡La cal es muy liviana!)
}

def calcular_produccion_lote(tipo_mezcla, cantidad_bultos_30kg):
    """
    Calcula insumos para producir X bultos de 30kg
    basado en las recetas volumétricas 3:1 y 3:3:1
    """
    peso_meta_lote = cantidad_bultos_30kg * 30 # kg totales a producir
    
    insumos = {}
    
    if tipo_mezcla == "R (Relleno 3:1)":
        # RECETA 3 PARTES ARENA : 1 PARTE CEMENTO
        # Calculamos el peso de "1 unidad de volumen" teórica
        # 3 L Arena (4.8kg) + 1 L Cemento (1.5kg) = 6.3 kg por unidad volumétrica
        peso_unidad_vol = (3 * DENSIDAD['arena']) + (1 * DENSIDAD['cemento'])
        
        # Cuántas unidades volumétricas necesitamos para llegar al peso meta
        unidades_necesarias = peso_meta_lote / peso_unidad_vol
        
        # Desglose en Litros y Kilos
        insumos['arena_L'] = unidades_necesarias * 3
        insumos['cemento_L'] = unidades_necesarias * 1
        insumos['cal_L'] = 0
        
        insumos['arena_kg'] = insumos['arena_L'] * DENSIDAD['arena']
        insumos['cemento_kg'] = insumos['cemento_L'] * DENSIDAD['cemento']
        insumos['cal_kg'] = 0
        
    elif tipo_mezcla == "A (Acabado 3:3:1)":
        # RECETA 3 ARENA : 3 CAL : 1 CEMENTO
        # 3 L Arena (4.8kg) + 3 L Cal (1.65kg) + 1 L Cemento (1.5kg) = 7.95 kg
        peso_unidad_vol = (3 * DENSIDAD['arena']) + (3 * DENSIDAD['cal']) + (1 * DENSIDAD['cemento'])
        
        unidades_necesarias = peso_meta_lote / peso_unidad_vol
        
        insumos['arena_L'] = unidades_necesarias * 3
        insumos['cal_L'] = unidades_necesarias * 3
        insumos['cemento_L'] = unidades_necesarias * 1
        
        insumos['arena_kg'] = insumos['arena_L'] * DENSIDAD['arena']
        insumos['cal_kg'] = insumos['cal_L'] * DENSIDAD['cal']
        insumos['cemento_kg'] = insumos['cemento_L'] * DENSIDAD['cemento']
        
    return insumos

# ==========================================
# 🧠 MOTOR DE VENTAS (CÓDIGO ANTERIOR)
# ==========================================
def calcular_proyecto_al_detalle(area_m2):
    P = st.session_state['precios_reales']
    margen_decimal = st.session_state['margen'] / 100
    vol_total_m3 = area_m2 * 0.04 * 1.05
    vol_relleno = vol_total_m3 * 0.70
    vol_acabado = vol_total_m3 * 0.30
    
    # Receta 1:3
    cemento_relleno = vol_relleno * 8.5 
    arena_relleno   = vol_relleno * 1.1 
    
    # Receta 1:3:3
    cemento_piel = vol_acabado * 4.5
    cal_piel     = vol_acabado * 10.0 
    arena_piel   = vol_acabado * 1.1

    total_cemento = math.ceil(cemento_relleno + cemento_piel)
    total_cal     = math.ceil(cal_piel)
    total_arena   = (arena_relleno + arena_piel)
    
    total_malla   = area_m2 * 2.1
    total_perfil  = area_m2 * 1.2
    
    costo_materiales = (
        (total_cemento * P.get('cemento_gris_50kg', 29500)) +
        (total_cal * P.get('cal_hidratada_25kg', 25000)) +    
        (total_arena * P.get('arena_rio_m3', 98000)) +
        (total_malla * P.get('malla_5mm_m2', 28000)) +
        (total_perfil * P.get('perfil_c18_ml', 11500)) +
        (area_m2 * 5000)
    )

    rendimiento = P.get('rendimiento_dia', 4.0)
    dias = math.ceil(area_m2 / rendimiento)
    costo_mo = dias * P.get('dia_cuadrilla', 250000)
    
    costo_total = costo_materiales + costo_mo
    precio_venta = costo_total / (1 - margen_decimal)
    utilidad = precio_venta - costo_total
    
    bultos_r = math.ceil((vol_relleno * 1000) / 16)
    bultos_a = math.ceil((vol_acabado * 1000) / 16)
    
    return {
        "raw_mat": costo_materiales, "raw_mo": costo_mo, "raw_total": costo_total,
        "precio_venta": precio_venta, "utilidad": utilidad,
        "logistica": {"total_30kg": bultos_r + bultos_a, "R": bultos_r, "A": bultos_a},
        "insumos": {"cemento": total_cemento, "cal": total_cal}
    }

# ==========================================
# 📄 PDF (Igual que antes)
# ==========================================
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'FERROTEK S.A.S - DOCUMENTO OFICIAL', 0, 1, 'C')
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
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "LOGÍSTICA DE MATERIALES", 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 7, f"- Bultos Tipo R (Estructural): {datos['logistica']['R']} Unidades", 0, 1)
    pdf.cell(0, 7, f"- Bultos Tipo A (Piel Roca): {datos['logistica']['A']} Unidades", 0, 1)
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "INVERSIÓN", 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(100, 8, "Valor Total", 1)
    pdf.cell(50, 8, f"${datos['precio_venta']:,.0f}", 1, 1)
    
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 🎛️ PANEL LATERAL
# ==========================================
with st.sidebar:
    st.title("🎛️ Ferrotek Manager")
    pwd = st.text_input("Contraseña:", type="password")
    
    defaults = {
        'cemento_gris_50kg': 29500, 'cal_hidratada_25kg': 25000,   
        'arena_rio_m3': 98000, 'malla_5mm_m2': 28000, 
        'perfil_c18_ml': 11500, 'dia_cuadrilla': 250000, 'rendimiento_dia': 4.0
    }
    
    if 'precios_reales' not in st.session_state: st.session_state['precios_reales'] = defaults
    if 'margen' not in st.session_state: st.session_state['margen'] = 30 
    
    es_admin = (pwd == "ferrotek2026")
    if es_admin:
        st.success("🔓 Admin Activo")
        margen = st.slider("% Utilidad", 0, 60, st.session_state['margen'])
        st.session_state['margen'] = margen
        with st.expander("Editar Costos Insumos"):
            edited = st.data_editor(st.session_state['precios_reales'], key="grid_precios", num_rows="fixed")
            st.session_state['precios_reales'] = edited

if 'view' not in st.session_state: st.session_state.view = 'home'
def set_view(name): st.session_state.view = name

# ==========================================
# 🎨 VISTAS
# ==========================================
if st.session_state.view == 'home':
    st.title("🏗️ FERROTEK: ERP Integral")
    st.subheader("Seleccione Módulo:")
    
    col1, col2, col3 = st.columns(3)
    with col1: 
        st.info("### 💰 Ventas")
        if st.button("Ir a Cotizador", key="go_ventas"): set_view('viviendas')
    with col2: 
        st.warning("### 🏭 Fábrica")
        st.write("Control de Mezclas y Producción.")
        if st.button("Ir a Planta", key="go_fabrica"): set_view('fabrica')
    with col3:
        st.success("### 🛡️ Muros")
        if st.button("Ir a Muros", key="go_muros"): set_view('muros')

# --- VISTA FÁBRICA (NUEVA) ---
elif st.session_state.view == 'fabrica':
    st.button("⬅️ Menú Principal", on_click=lambda: set_view('home'))
    st.header("🏭 Módulo de Producción (Planta)")
    st.markdown("---")
    
    tipo_prod = st.radio("¿Qué vamos a producir hoy?", ["R (Relleno 3:1)", "A (Acabado 3:3:1)"], horizontal=True)
    
    col_input, col_result = st.columns(2)
    with col_input:
        qty = st.number_input("Cantidad de Bultos (30kg) a fabricar:", value=10, step=5)
        tamano_balde = st.selectbox("Tamaño del Balde de Medida:", [10, 20], format_func=lambda x: f"{x} Litros")
        
    insumos = calcular_produccion_lote(tipo_prod, qty)
    
    with col_result:
        st.subheader("📋 Orden de Mezcla")
        st.write(f"Para producir **{qty} Bultos** de 30kg:")
        
        # Mostrar en BALDES (Lo que entiende el operario)
        b_arena = round(insumos['arena_L'] / tamano_balde, 1)
        b_cemento = round(insumos['cemento_L'] / tamano_balde, 1)
        b_cal = round(insumos.get('cal_L', 0) / tamano_balde, 1)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Arena", f"{b_arena}", delta="Baldes")
        c2.metric("Cemento", f"{b_cemento}", delta="Baldes")
        if b_cal > 0:
            c3.metric("Cal", f"{b_cal}", delta="Baldes")
        else:
            c3.metric("Cal", "0", delta="No lleva")
            
        st.info(f"ℹ️ Medido en baldes de {tamano_balde} Litros al ras.")

    st.markdown("---")
    st.subheader("🛒 Requisición a Bodega (Materia Prima)")
    st.caption("Esto es lo que se debe sacar del inventario para esta orden:")
    
    df_bodega = pd.DataFrame({
        "Insumo": ["Cemento", "Cal Hidratada", "Arena Seca"],
        "Cantidad Exacta (kg)": [
            f"{insumos['cemento_kg']:.1f} kg",
            f"{insumos.get('cal_kg', 0):.1f} kg",
            f"{insumos['arena_kg']:.1f} kg"
        ],
        "Equivalente Bultos Compra": [
            f"{insumos['cemento_kg']/50:.1f} btos (50kg)",
            f"{insumos.get('cal_kg', 0)/25:.1f} btos (25kg)",
            f"{insumos['arena_kg']/40:.1f} btos (40kg aprox)"
        ]
    })
    st.table(df_bodega)

# --- VISTAS VENTAS (MANTENIDAS) ---
elif st.session_state.view == 'viviendas':
    st.button("⬅️ Volver", on_click=lambda: set_view('home'))
    st.header("🏠 Cotizador de Vivienda")
    modelo = st.selectbox("Modelo", ["Suite 30m2", "Familiar 54m2", "Máster 84m2"])
    area_real = int(modelo.split()[1].replace("m2","")) * 3.5 
    finanzas = calcular_proyecto_al_detalle(area_real)
    precio_final = finanzas['precio_venta'] * 1.25
    
    st.metric("Precio Venta", f"${precio_final:,.0f}")
    
    if es_admin:
        st.write("---")
        st.warning(f"Utilidad: ${finanzas['utilidad']*1.25:,.0f}")
    
    nom = st.text_input("Cliente PDF:")
    if nom:
        d = finanzas.copy()
        d['precio_venta'] = precio_final
        pdf = generar_pdf(nom, modelo, int(area_real/3.5), d)
        st.download_button("Descargar PDF", pdf, "cotizacion.pdf", "application/pdf")

elif st.session_state.view == 'muros':
    st.button("⬅️ Volver", on_click=lambda: set_view('home'))
    st.header("🛡️ Cotizador de Muros")
    ml = st.number_input("Metros Lineales:", value=50.0)
    area = ml * 2.2
    finanzas = calcular_proyecto_al_detalle(area)
    
    st.metric("Precio Cliente", f"${finanzas['precio_venta']:,.0f}")
    st.write(f"Logística: {finanzas['logistica']['total_30kg']} bultos (R: {finanzas['logistica']['R']} | A: {finanzas['logistica']['A']})")
    
    nom = st.text_input("Cliente:")
    if nom:
        pdf = generar_pdf(nom, f"Muro {ml}ml", area, finanzas)
        st.download_button("Descargar PDF", pdf, "cotizacion.pdf", "application/pdf")