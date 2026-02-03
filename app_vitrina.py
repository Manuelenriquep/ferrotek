import streamlit as st
import pandas as pd
import math
from fpdf import FPDF
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURACIÓN GENERAL
# ==========================================
st.set_page_config(page_title="Ferrotek | Construcción Monolítica", page_icon="🏗️", layout="wide")

# ==========================================
# 🧪 MÓDULO FÁBRICA (DENSIDADES)
# ==========================================
DENSIDAD = {'cemento': 1.50, 'arena': 1.60, 'cal': 0.55}

def calcular_produccion_lote(tipo_mezcla, cantidad_bultos_30kg):
    peso_meta = cantidad_bultos_30kg * 30
    insumos = {}
    
    if "Relleno" in tipo_mezcla: 
        peso_vol = (3 * DENSIDAD['arena']) + (1 * DENSIDAD['cemento'])
        units = peso_meta / peso_vol
        insumos = {'arena_L': units*3, 'cemento_L': units*1, 'cal_L': 0}
    elif "Acabado" in tipo_mezcla: 
        peso_vol = (3 * DENSIDAD['arena']) + (3 * DENSIDAD['cal']) + (1 * DENSIDAD['cemento'])
        units = peso_meta / peso_vol
        insumos = {'arena_L': units*3, 'cal_L': units*3, 'cemento_L': units*1}
    
    insumos['arena_kg'] = insumos['arena_L'] * DENSIDAD['arena']
    insumos['cemento_kg'] = insumos['cemento_L'] * DENSIDAD['cemento']
    insumos['cal_kg'] = insumos.get('cal_L', 0) * DENSIDAD['cal']
    return insumos

# ==========================================
# 🧠 MOTOR DE COSTOS
# ==========================================
def calcular_proyecto(area_m2, tipo="general"):
    P = st.session_state['precios_reales']
    margen = st.session_state['margen'] / 100
    
    espesor = 0.04 if tipo != "estanque" else 0.06
    vol_total = area_m2 * espesor * 1.05
    vol_relleno = vol_total * 0.70
    vol_acabado = vol_total * 0.30
    
    cemento_tot = (vol_relleno * 8.5) + (vol_acabado * 4.5)
    cal_tot = vol_acabado * 10.0 
    arena_tot = vol_total * 1.1
    
    mat = (
        (math.ceil(cemento_tot) * P['cemento_gris_50kg']) +
        (math.ceil(cal_tot) * P['cal_hidratada_25kg']) +
        (arena_tot * P['arena_rio_m3']) +
        (area_m2 * 2.1 * P['malla_5mm_m2']) +
        (area_m2 * 1.2 * P['perfil_c18_ml']) +
        (area_m2 * 6000) 
    )
    
    dias = math.ceil(area_m2 / P.get('rendimiento_dia', 4.0))
    mo = dias * P['dia_cuadrilla']
    total = mat + mo
    venta = total / (1 - margen)
    
    b_r = math.ceil((vol_relleno * 1000) / 16)
    b_a = math.ceil((vol_acabado * 1000) / 16)
    
    return {
        "precio": venta, "utilidad": venta - total, "costo": total,
        "logistica": {"R": b_r, "A": b_a, "total": b_r + b_a},
        "insumos": {"cemento": cemento_tot, "cal": cal_tot}
    }

# ==========================================
# 📄 PDF CLIENTE
# ==========================================
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'FERROTEK S.A.S', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, 'Ingeniería Unibody & Construcción Monolítica', 0, 1, 'C')
        self.line(10, 30, 200, 30); self.ln(10)

def generar_pdf(cliente, obra, datos):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", 0, 1)
    pdf.cell(0, 10, f"Cliente: {cliente}", 0, 1)
    pdf.cell(0, 10, f"Obra: {obra}", 0, 1); pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "PROPUESTA TÉCNICA", 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 7, "Suministro de sistema Ferrotek Unibody (Piel de Roca). Estructura sismo-resistente de acero, con acabado monolítico impermeable.")
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "INVERSION ESTIMADA", 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 10, f"Valor Total: ${datos['precio']:,.0f}", 0, 1)
    
    pdf.ln(10)
    pdf.set_font('Arial', 'I', 9)
    pdf.cell(0, 10, "Nota: Precio sujeto a visita técnica. Validez 15 días.", 0, 1)
    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 🎛️ SIDEBAR
# ==========================================
with st.sidebar:
    st.title("🎛️ Panel Admin")
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
        st.success("🔓 Modo Edición")
        margen = st.slider("Utilidad %", 0, 60, st.session_state['margen'])
        st.session_state['margen'] = margen
        with st.expander("Costos Insumos"):
            edited = st.data_editor(st.session_state['precios_reales'], key="p_edit", num_rows="fixed")
            st.session_state['precios_reales'] = edited

if 'view' not in st.session_state: st.session_state.view = 'home'
def set_view(name): st.session_state.view = name

# ==========================================
# 🎨 VISTA 1: HOME (LA VENDEDORA 🌟)
# ==========================================
if st.session_state.view == 'home':
    # 1. HERO SECTION (Encabezado Potente)
    st.title("🏗️ FERROTEK: Construcción del Futuro")
    st.subheader("Más fuerte que el bloque, más fresco que el ladrillo.")
    st.markdown("---")

    # 2. LOS 3 PILARES (VENTAJAS COMPETITIVAS)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/2362/2362365.png", width=60) # Icono Sismo (Generico)
        st.markdown("### 🛡️ Indestructible")
        st.markdown("""
        **Tecnología Unibody:** A diferencia de la mampostería que se agrieta, nuestras casas son **una sola pieza monolítica** con alma de acero.
        *Sismo-Resistencia Superior.*
        """)
        
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/3062/3062634.png", width=60) # Icono Clima
        st.markdown("### 🌡️ Climatizada")
        st.markdown("""
        **Doble Membrana:**
        El sistema crea una cámara térmica natural. Su casa se mantiene fresca en días calurosos sin necesidad de aire acondicionado.
        *Confort Real.*
        """)

    with col3:
        st.image("https://cdn-icons-png.flaticon.com/512/2854/2854203.png", width=60) # Icono Dinero
        st.markdown("### 💰 Piel de Roca")
        st.markdown("""
        **Cero Mantenimiento:**
        Nuestros muros tienen un acabado pétreo impermeable que **nunca necesita pintura**. La lluvia los limpia y los endurece.
        *Ahorro de por vida.*
        """)

    st.markdown("---")

    # 3. MENÚ DE ACCIÓN (COTIZADORES)
    st.subheader("🚀 ¿Qué desea construir hoy?")
    
    c_muros, c_casas, c_esp, c_fab = st.columns(4)
    with c_muros: 
        st.info("🛡️ **Cerramientos**")
        st.caption("Seguridad Perimetral")
        if st.button("Cotizar Muros", key="nav_m", use_container_width=True): set_view('muros')
    with c_casas: 
        st.success("🏠 **Viviendas**")
        st.caption("Llave en Mano")
        if st.button("Cotizar Casa", key="nav_v", use_container_width=True): set_view('viviendas')
    with c_esp:
        st.warning("🏺 **Especiales**")
        st.caption("Bóvedas y Estanques")
        if st.button("Ver Diseños", key="nav_e", use_container_width=True): set_view('especiales')
    with c_fab:
        st.error("🏭 **Fábrica**")
        st.caption("Solo Personal")
        if st.button("Producción", key="nav_f", use_container_width=True): set_view('fabrica')
        
    # 4. GALERÍA RÁPIDA (GANCHO VISUAL)
    st.markdown("---")
    st.subheader("📸 Galería Ferrotek")
    g1, g2, g3 = st.columns(3)
    with g1: 
        try: st.image("render_modelo1.png", caption="Diseño Moderno", use_container_width=True)
        except: pass
    with g2: 
        try: st.image("image_4.png", caption="Acabado Piel de Roca", use_container_width=True)
        except: pass
    with g3: 
        try: st.image("image_15.png", caption="Arquitectura Bóveda", use_container_width=True)
        except: pass

# ==========================================
# 🎨 VISTA 2: MUROS
# ==========================================
elif st.session_state.view == 'muros':
    st.button("⬅️ Volver al Inicio", on_click=lambda: set_view('home'))
    st.header("🛡️ Cotizador de Muros")
    
    ml = st.number_input("Metros Lineales:", value=50.0)
    area = ml * 2.2
    data = calcular_proyecto(area)
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("💰 Inversión")
        st.metric("Precio Cliente", f"${data['precio']:,.0f}")
        st.write("✅ Incluye materiales, estructura y mano de obra.")
        st.write("✅ Acabado impermeable natural.")
        
        if es_admin:
            st.error("🕵️ DATA PRIVADA")
            st.write(f"Despacho: {data['logistica']['total']} bultos 30kg")
            st.caption(f"Cemento: {data['insumos']['cemento']:.1f} btos | Cal: {data['insumos']['cal']:.1f} btos")
    with c2:
        try: st.image("image_4.png", caption="Textura Real", use_container_width=True)
        except: pass

    if st.text_input("Nombre Cliente:"):
        pdf = generar_pdf("Cliente", f"Muro {ml}ml", data)
        st.download_button("Descargar Cotización PDF", pdf, "muro.pdf")

# ==========================================
# 🎨 VISTA 3: VIVIENDAS
# ==========================================
elif st.session_state.view == 'viviendas':
    st.button("⬅️ Volver al Inicio", on_click=lambda: set_view('home'))
    st.header("🏠 Cotizador de Vivienda Unibody")
    
    mod = st.selectbox("Seleccione Modelo", ["Suite 30m2", "Familiar 54m2", "Máster 84m2"])
    area = int(mod.split()[1].replace("m2","")) * 3.5
    
    data = calcular_proyecto(area)
    final_price = data['precio'] * 1.25 
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Valor Llave en Mano", f"${final_price:,.0f}")
        st.success("**¡La mejor relación costo-beneficio del mercado!**")
        st.markdown("""
        * **Cimientos:** Losa flotante.
        * **Estructura:** Acero + Mortero Alta Resistencia.
        * **Acabados:** Pisos poliméricos y muros pulidos.
        """)
        
        if es_admin:
            st.error(f"Utilidad Neta: ${(data['utilidad']*1.25):,.0f}")
            
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
            st.write("Ideal para Glamping, Bodegas o Vivienda Campestre.")
        with c_b:
            try: st.image("image_15.png", caption="Render Bóveda", use_container_width=True)
            except: pass
            
    with tab2:
        st.subheader("Estanque Piscícola")
        diam = st.number_input("Diámetro (m)", 4.0, 20.0, 6.0)
        data_e = calcular_proyecto(((math.pi * diam * 1.2) + (math.pi * (diam/2)**2)), tipo="estanque") 
        st.metric("Inversión Estanque", f"${data_e['precio']:,.0f}")

# ==========================================
# 🎨 VISTA 5: FÁBRICA
# ==========================================
elif st.session_state.view == 'fabrica':
    st.button("⬅️ Volver al Inicio", on_click=lambda: set_view('home'))
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
        st.subheader("🛒 Requisición Bodega")
        st.table(pd.DataFrame({
            "Material": ["Arena", "Cemento", "Cal"],
            "Kg": [f"{res['arena_kg']:.1f}", f"{res['cemento_kg']:.1f}", f"{res.get('cal_kg',0):.1f}"]
        }))