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
# 🧠 MOTOR DE COSTOS (V78 - OPTIMIZADO + GOTERO)
# ==========================================
def calcular_proyecto(area_m2, ml_muro=0, tipo="general", tiene_gotero=False):
    P = st.session_state['precios_reales']
    margen = st.session_state['margen'] / 100
    
    espesor = 0.04 if tipo != "estanque" else 0.06
    vol_total = area_m2 * espesor * 1.05
    
    vol_relleno = vol_total * 0.70
    vol_acabado = vol_total * 0.30
    
    cemento_tot = (vol_relleno * 8.5) + (vol_acabado * 4.5)
    cal_tot = vol_acabado * 10.0 
    arena_tot = vol_total * 1.1
    
    factor_perfil = 0.9 
    
    mat = (
        (math.ceil(cemento_tot) * P['cemento_gris_50kg']) +
        (math.ceil(cal_tot) * P['cal_hidratada_25kg']) +
        (arena_tot * P['arena_rio_m3']) +
        (area_m2 * 2.1 * P['malla_5mm_m2']) +
        (area_m2 * factor_perfil * P['perfil_c18_ml']) + 
        (area_m2 * 5000)
    )
    
    rendimiento = P.get('rendimiento_dia', 4.5)
    dias = math.ceil(area_m2 / rendimiento)
    mo_base = dias * P['dia_cuadrilla']
    
    costo_gotero = 0
    if tiene_gotero and ml_muro > 0:
        costo_gotero = ml_muro * 25000 
    
    total = mat + mo_base + costo_gotero
    venta = total / (1 - margen)
    
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
        self.cell(0, 10, 'Ingeniería Unibody & Construcción Monolítica', 0, 1, 'C')
        self.line(10, 30, 200, 30); self.ln(10)

def generar_pdf(cliente, obra, datos, incluye_gotero=False):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", 0, 1)
    pdf.cell(0, 10, f"Cliente: {cliente}", 0, 1)
    pdf.cell(0, 10, f"Proyecto: {obra}", 0, 1); pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "ALCANCE TÉCNICO", 0, 1)
    pdf.set_font('Arial', '', 11)
    
    texto_base = "Suministro e instalación de sistema Ferrotek Unibody (Piel de Roca). Estructura sismo-resistente de acero con recubrimiento monolítico impermeable."
    if incluye_gotero:
        texto_base += " Incluye remate superior tipo 'Gotero/Viga Cinta' para protección de fachada y mayor rigidez."
        
    pdf.multi_cell(0, 7, texto_base)
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "INVERSIÓN", 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 10, f"Valor Total: ${datos['precio']:,.0f}", 0, 1)
    
    pdf.ln(10)
    pdf.set_font('Arial', 'I', 9)
    pdf.cell(0, 10, "Validez de la oferta: 15 días. No incluye viáticos fuera del área metropolitana.", 0, 1)
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 🎛️ SIDEBAR
# ==========================================
with st.sidebar:
    st.title("🎛️ Panel Gerente")
    pwd = st.text_input("Contraseña:", type="password")
    
    defaults = {
        'cemento_gris_50kg': 29500, 'cal_hidratada_25kg': 25000, 
        'arena_rio_m3': 98000, 'malla_5mm_m2': 28000, 
        'perfil_c18_ml': 11500, 'dia_cuadrilla': 250000, 'rendimiento_dia': 4.5
    }
    if 'precios_reales' not in st.session_state: st.session_state['precios_reales'] = defaults
    if 'margen' not in st.session_state: st.session_state['margen'] = 30
    
    es_admin = (pwd == "ferrotek2026")
    if es_admin:
        st.success("🔓 Admin Activo")
        margen = st.slider("Utilidad Deseada %", 0, 60, st.session_state['margen'])
        st.session_state['margen'] = margen
        with st.expander("Editar Costos Insumos"):
            edited = st.data_editor(st.session_state['precios_reales'], key="p_edit", num_rows="fixed")
            st.session_state['precios_reales'] = edited

if 'view' not in st.session_state: st.session_state.view = 'home'
def set_view(name): st.session_state.view = name

# ==========================================
# 🎨 VISTA 1: HOME (TEXTOS CORREGIDOS)
# ==========================================
if st.session_state.view == 'home':
    st.title("🏗️ FERROTEK: Ingeniería Monolítica")
    st.subheader("La evolución inteligente de la construcción tradicional.")
    st.markdown("---")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("### 🛡️ Sismo-Resistente") # Cambio Indestructible
        st.write("Estructura continua (Unibody) con alma de acero. Mayor seguridad estructural que la mampostería suelta.")
    with c2:
        st.success("### 🌡️ Confort Térmico")
        st.write("Doble membrana aislante. Ambientes más frescos de forma natural, reduciendo el calor radiante.")
    with c3:
        st.warning("### 💰 Mínimo Mantenimiento") # Cambio Cero Mantenimiento
        st.write("Acabado Piel de Roca. Una superficie pétrea impermeable que elimina el gasto de pintura por años.")

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

    # --- GALERÍA AUTOMÁTICA ---
    st.markdown("---")
    st.subheader("📸 Galería de Obras")
    
    archivos = os.listdir('.')
    imagenes = [f for f in archivos if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    
    if imagenes:
        cols = st.columns(3)
        for i, img_file in enumerate(imagenes):
            with cols[i % 3]:
                st.image(img_file, caption=img_file, use_container_width=True)
    else:
        st.info("ℹ️ Galería lista. Suba sus fotos al repositorio para verlas aquí.")

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
        gotero = st.checkbox("Incluir Remate Superior (Gotero/Viga Cinta)", value=True, help="Agrega costo extra por filos y detalles.")
        
    area = ml * 2.2
    data = calcular_proyecto(area, ml_muro=ml, tipo="general", tiene_gotero=gotero)
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("💰 Inversión")
        st.metric("Precio Cliente", f"${data['precio']:,.0f}")
        
        if gotero:
            st.success("✅ Incluye Viga Cinta / Gotero.")
        else:
            st.warning("⚠️ Remate simple.")
            
        if es_admin:
            st.error("🕵️ DATA PRIVADA")
            st.write(f"Costo Real: ${data['costo']:,.0f} | Utilidad: ${data['utilidad']:,.0f}")
            st.write(f"Logística: {data['logistica']['total']} Bultos 30kg")
            st.caption(f"Cemento: {data['insumos']['cemento']:.1f} btos | Cal: {data['insumos']['cal']:.1f} btos")
            
    with c2:
        try: st.image("image_4.png", caption="Textura Real", use_container_width=True)
        except: pass

    if st.text_input("Nombre Cliente:"):
        pdf = generar_pdf("Cliente", f"Muro {ml}ml", data, incluye_gotero=gotero)
        st.download_button("Descargar Cotización PDF", pdf, "muro.pdf")

# ==========================================
# 🎨 VISTA 3: VIVIENDAS
# ==========================================
elif st.session_state.view == 'viviendas':
    st.button("⬅️ Volver al Inicio", on_click=lambda: set_view('home'))
    st.header("🏠 Cotizador de Vivienda")
    
    mod = st.selectbox("Seleccione Modelo", ["Suite 30m2", "Familiar 54m2", "Máster 84m2"])
    area = int(mod.split()[1].replace("m2","")) * 3.5
    
    data = calcular_proyecto(area)
    final_price = data['precio'] * 1.25 # Factor acabados
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Valor Llave en Mano", f"${final_price:,.0f}")
        st.info("Incluye estructura, muros Piel de Roca y pisos poliméricos.")
        
        if es_admin:
            st.error("🕵️ DATA PRIVADA")
            st.write(f"Utilidad Est: ${(data['utilidad']*1.25):,.0f}")
            st.write(f"Estructura Base: {data['logistica']['total']} Bultos 30kg")
            
    with c2:
        img_map = {"Suite 30m2": "render_modelo1.png", "Familiar 54m2": "render_modelo2.png", "Máster 84m2": "render_modelo3.png"}
        try: st.image(img_map[mod], use_container_width=True)
        except: st.error("Imagen no cargada")

    if st.text_input("Nombre Cliente:"):
        d_pdf = data.copy(); d_pdf['precio'] = final_price
        pdf = generar_pdf("Cliente", mod, d_pdf)
        st.download_button("Descargar Cotización PDF", pdf, "casa.pdf")

# ==========================================
# 🎨 VISTA 4: ESPECIALES
# ==========================================
elif st.session_state.view == 'especiales':
    st.button("⬅️ Volver al Inicio", on_click=lambda: set_view('home'))
    st.header("🏺 Proyectos Especiales")
    
    tab1, tab2 = st.tabs(["Bóvedas", "Estanques"])
    
    with tab1:
        st.subheader("Bóveda Auto-Portante (3.80m)")
        largo = st.slider("Largo (m)", 3.0, 15.0, 6.0)
        data_b = calcular_proyecto(largo * 7.5) 
        
        c_a, c_b = st.columns(2)
        with c_a:
            st.metric("Inversión Bóveda", f"${data_b['precio']:,.0f}")
        with c_b:
            try: st.image("image_15.png", caption="Bóveda", use_container_width=True)
            except: pass
            
    with tab2:
        st.subheader("Estanque Piscícola")
        diam = st.number_input("Diámetro (m)", 4.0, 20.0, 6.0)
        area_est = (math.pi * diam * 1.2) + (math.pi * (diam/2)**2)
        data_e = calcular_proyecto(area_est, tipo="estanque") 
        st.metric("Inversión Estanque", f"${data_e['precio']:,.0f}")

# ==========================================
# 🎨 VISTA 5: FÁBRICA
# ==========================================
elif st.session_state.view == 'fabrica':
    st.button("⬅️ Volver al Inicio", on_click=lambda: set_view('home'))
    st.header("🏭 Planta de Producción")
    
    tipo = st.radio("Tipo de Mezcla:", ["Relleno (3:1)", "Acabado (3:3:1)"], horizontal=True)
    qty = st.number_input("Cantidad de Bultos (30kg) a fabricar:", 10, 500, 20)
    balde = st.selectbox("Tamaño Balde:", [10, 20], format_func=lambda x: f"{x} Litros")
    
    res = calcular_produccion_lote(tipo, qty)
    
    if res:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📋 Receta Operativa")
            st.metric("Arena", f"{round(res['arena_L']/balde, 1)}", "Baldes")
            st.metric("Cemento", f"{round(res['cemento_L']/balde, 1)}", "Baldes")
            if res.get('cal_L', 0) > 0:
                st.metric("Cal", f"{round(res['cal_L']/balde, 1)}", "Baldes")
                
        with c2:
            st.subheader("🛒 Consumo Bodega")
            st.table(pd.DataFrame({
                "Insumo": ["Arena", "Cemento", "Cal"],
                "Kg Reales": [f"{res['arena_kg']:.1f}", f"{res['cemento_kg']:.1f}", f"{res.get('cal_kg',0):.1f}"]
            }))