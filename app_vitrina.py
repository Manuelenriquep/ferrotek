import streamlit as st
import pandas as pd
import math
from fpdf import FPDF
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURACIÓN E IMÁGENES
# ==========================================
st.set_page_config(page_title="Ferrotek | ERP Integral", page_icon="🏗️", layout="wide")

# ==========================================
# 🧪 MÓDULO FÁBRICA (DENSIDADES)
# ==========================================
DENSIDAD = {'cemento': 1.50, 'arena': 1.60, 'cal': 0.55}

def calcular_produccion_lote(tipo_mezcla, cantidad_bultos_30kg):
    peso_meta = cantidad_bultos_30kg * 30
    insumos = {}
    
    if "Relleno" in tipo_mezcla: # 3:1 (Arena:Cemento)
        peso_vol = (3 * DENSIDAD['arena']) + (1 * DENSIDAD['cemento'])
        unidades = peso_meta / peso_vol
        insumos = {'arena_L': units*3, 'cemento_L': units*1, 'cal_L': 0} if (units := unidades) else {}
        
    elif "Acabado" in tipo_mezcla: # 3:3:1 (Arena:Cal:Cemento)
        peso_vol = (3 * DENSIDAD['arena']) + (3 * DENSIDAD['cal']) + (1 * DENSIDAD['cemento'])
        unidades = peso_meta / peso_vol
        insumos = {'arena_L': units*3, 'cal_L': units*3, 'cemento_L': units*1} if (units := unidades) else {}
    
    # Calcular Kilos para Bodega
    insumos['arena_kg'] = insumos['arena_L'] * DENSIDAD['arena']
    insumos['cemento_kg'] = insumos['cemento_L'] * DENSIDAD['cemento']
    insumos['cal_kg'] = insumos.get('cal_L', 0) * DENSIDAD['cal']
    
    return insumos

# ==========================================
# 🧠 MOTOR DE COSTOS (DOBLE RECETA + BULTOS 30KG)
# ==========================================
def calcular_proyecto(area_m2, tipo="general"):
    P = st.session_state['precios_reales']
    margen = st.session_state['margen'] / 100
    
    # Espesores y Volúmenes
    espesor = 0.04 if tipo != "estanque" else 0.06 # Estanques más gruesos
    vol_total = area_m2 * espesor * 1.05
    
    vol_relleno = vol_total * 0.70
    vol_acabado = vol_total * 0.30
    
    # Recetas
    cemento_tot = (vol_relleno * 8.5) + (vol_acabado * 4.5)
    cal_tot = vol_acabado * 10.0 # Solo en acabado
    arena_tot = vol_total * 1.1
    
    # Costos Directos
    mat = (
        (math.ceil(cemento_tot) * P['cemento_gris_50kg']) +
        (math.ceil(cal_tot) * P['cal_hidratada_25kg']) +
        (arena_tot * P['arena_rio_m3']) +
        (area_m2 * 2.1 * P['malla_5mm_m2']) +
        (area_m2 * 1.2 * P['perfil_c18_ml']) +
        (area_m2 * 6000) # Varios
    )
    
    rendimiento = P.get('rendimiento_dia', 4.0)
    dias = math.ceil(area_m2 / rendimiento)
    mo = dias * P['dia_cuadrilla']
    
    total = mat + mo
    venta = total / (1 - margen)
    
    # Logística 30kg
    b_r = math.ceil((vol_relleno * 1000) / 16)
    b_a = math.ceil((vol_acabado * 1000) / 16)
    
    return {
        "precio": venta, "utilidad": venta - total, "costo": total,
        "logistica": {"R": b_r, "A": b_a, "total": b_r + b_a},
        "insumos": {"cemento": cemento_tot, "cal": cal_tot}
    }

# ==========================================
# 📄 PDF GENERATOR
# ==========================================
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'FERROTEK S.A.S', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, 'Tecnologia Unibody - Cotizacion Oficial', 0, 1, 'C')
        self.line(10, 30, 200, 30); self.ln(10)

def generar_pdf(cliente, obra, datos):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", 0, 1)
    pdf.cell(0, 10, f"Cliente: {cliente}", 0, 1)
    pdf.cell(0, 10, f"Obra: {obra}", 0, 1); pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "LOGISTICA DE MATERIALES (30KG)", 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 7, f"- Bultos Tipo R (Estructural): {datos['logistica']['R']}", 0, 1)
    pdf.cell(0, 7, f"- Bultos Tipo A (Piel Roca): {datos['logistica']['A']}", 0, 1)
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "INVERSION", 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 10, f"Valor Total: ${datos['precio']:,.0f}", 0, 1)
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 🎛️ SIDEBAR (ADMIN)
# ==========================================
with st.sidebar:
    st.title("🎛️ Panel Gerente")
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
        st.success("🔓 Admin")
        margen = st.slider("Utilidad %", 0, 60, st.session_state['margen'])
        st.session_state['margen'] = margen
        with st.expander("Costos Insumos"):
            edited = st.data_editor(st.session_state['precios_reales'], key="p_edit", num_rows="fixed")
            st.session_state['precios_reales'] = edited

if 'view' not in st.session_state: st.session_state.view = 'home'
def set_view(name): st.session_state.view = name

# ==========================================
# 🎨 VISTA 1: HOME (MENÚ)
# ==========================================
if st.session_state.view == 'home':
    st.title("🏗️ FERROTEK: Sistema Integral")
    st.markdown("### Seleccione Módulo:")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: 
        if st.button("🛡️ Muros", key="nav_m", use_container_width=True): set_view('muros')
    with c2: 
        if st.button("🏠 Viviendas", key="nav_v", use_container_width=True): set_view('viviendas')
    with c3:
        if st.button("🏺 Especiales", key="nav_e", use_container_width=True): set_view('especiales')
    with c4:
        if st.button("🏭 Fábrica", key="nav_f", use_container_width=True): set_view('fabrica')

# ==========================================
# 🎨 VISTA 2: MUROS
# ==========================================
elif st.session_state.view == 'muros':
    st.button("⬅️ Volver", on_click=lambda: set_view('home'))
    st.header("🛡️ Cotizador de Muros")
    
    ml = st.number_input("Metros Lineales:", value=50.0)
    area = ml * 2.2
    data = calcular_proyecto(area)
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📦 Logística (Bultos 30kg)")
        st.info(f"Relleno (Tipo R): {data['logistica']['R']}")
        st.success(f"Acabado (Tipo A): {data['logistica']['A']}")
        st.write(f"**Total Despacho: {data['logistica']['total']} bultos**")
    with c2:
        st.subheader("💰 Inversión")
        st.metric("Precio Cliente", f"${data['precio']:,.0f}")
        try: st.image("image_4.png", caption="Acabado Piel de Roca")
        except: st.warning("Imagen image_4.png no encontrada")

    if st.text_input("Cliente PDF:"):
        pdf = generar_pdf("Cliente", f"Muro {ml}ml", data)
        st.download_button("Descargar PDF", pdf, "muro.pdf")

# ==========================================
# 🎨 VISTA 3: VIVIENDAS
# ==========================================
elif st.session_state.view == 'viviendas':
    st.button("⬅️ Volver", on_click=lambda: set_view('home'))
    st.header("🏠 Cotizador de Vivienda")
    
    mod = st.selectbox("Modelo", ["Suite 30m2", "Familiar 54m2", "Máster 84m2"])
    area = int(mod.split()[1].replace("m2","")) * 3.5
    
    data = calcular_proyecto(area)
    # Factor acabados internos
    final_price = data['precio'] * 1.25
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Valor Llave en Mano", f"${final_price:,.0f}")
        st.write("---")
        st.write(f"**Logística Estructura:** {data['logistica']['total']} Bultos 30kg")
        if es_admin:
            st.warning(f"Utilidad Real: ${(data['utilidad']*1.25):,.0f}")
    with c2:
        img_map = {"Suite 30m2": "render_modelo1.png", "Familiar 54m2": "render_modelo2.png", "Máster 84m2": "render_modelo3.png"}
        try: st.image(img_map[mod], use_column_width=True)
        except: st.error("Imagen del render no encontrada")

    if st.text_input("Cliente PDF:"):
        d_pdf = data.copy(); d_pdf['precio'] = final_price
        pdf = generar_pdf("Cliente", mod, d_pdf)
        st.download_button("Descargar PDF", pdf, "casa.pdf")

# ==========================================
# 🎨 VISTA 4: ESPECIALES (DOMOS Y ESTANQUES) - ¡RECUPERADO!
# ==========================================
elif st.session_state.view == 'especiales':
    st.button("⬅️ Volver", on_click=lambda: set_view('home'))
    st.header("🏺 Ingeniería Especial")
    
    tab1, tab2 = st.tabs(["Bóvedas / Domos", "Estanques"])
    
    with tab1:
        st.subheader("Bóveda Auto-Portante (Luz 3.80m)")
        largo = st.slider("Largo (m)", 3.0, 15.0, 6.0)
        area_bov = largo * 7.5 # Perimetro arco aprox
        data_b = calcular_proyecto(area_bov)
        
        c_a, c_b = st.columns(2)
        with c_a:
            st.metric("Inversión Bóveda", f"${data_b['precio']:,.0f}")
            st.write(f"Materiales: {data_b['logistica']['total']} Bultos")
        with c_b:
            try: st.image("image_15.png", caption="Bóveda Ferrotek")
            except: st.warning("Imagen image_15.png no encontrada")
            
    with tab2:
        st.subheader("Estanque Piscícola Monolítico")
        diam = st.number_input("Diámetro (m)", 4.0, 20.0, 6.0)
        altura = 1.2
        area_est = (math.pi * diam * altura) + (math.pi * (diam/2)**2)
        data_e = calcular_proyecto(area_est, tipo="estanque") # Usa espesor mayor
        
        st.metric("Inversión Estanque", f"${data_e['precio']:,.0f}")
        st.info(f"Incluye {data_e['logistica']['total']} bultos de alta resistencia.")

# ==========================================
# 🎨 VISTA 5: FÁBRICA (PRODUCCIÓN)
# ==========================================
elif st.session_state.view == 'fabrica':
    st.button("⬅️ Volver", on_click=lambda: set_view('home'))
    st.header("🏭 Planta de Producción")
    
    tipo = st.radio("Mezcla:", ["Relleno (3:1)", "Acabado (3:3:1)"], horizontal=True)
    qty = st.number_input("Bultos a Fabricar (30kg):", 10, 500, 20)
    balde = st.selectbox("Balde Medida:", [10, 20], format_func=lambda x: f"{x} Litros")
    
    res = calcular_produccion_lote(tipo, qty)
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📋 Receta (Baldes)")
        st.metric("Arena", f"{round(res['arena_L']/balde, 1)}", "Baldes")
        st.metric("Cemento", f"{round(res['cemento_L']/balde, 1)}", "Baldes")
        if res.get('cal_L', 0) > 0:
            st.metric("Cal", f"{round(res['cal_L']/balde, 1)}", "Baldes")
            
    with c2:
        st.subheader("🛒 Sacar de Bodega")
        st.table(pd.DataFrame({
            "Material": ["Arena", "Cemento", "Cal"],
            "Kg Reales": [f"{res['arena_kg']:.1f}", f"{res['cemento_kg']:.1f}", f"{res.get('cal_kg',0):.1f}"]
        }))