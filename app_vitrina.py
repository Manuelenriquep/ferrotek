import streamlit as st
import math
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURACIÓN Y ESTILOS
# ==========================================
st.set_page_config(page_title="Ferrotek | Ingeniería Unibody", page_icon="🏗️", layout="wide")

# Inicialización de la DB en sesión
if 'db' not in st.session_state:
    st.session_state['db'] = {
        "config": {"margen_utilidad": 0.30, "admin_pass": "ferrotek2026"},
        "precios": {
            'perfil_2_pulg_mt': 12500,
            'perfil_c18_mt': 11500,
            'malla_5mm_m2': 28000,
            'malla_zaranda_m2': 8500,
            'cemento_bulto': 29500,
            'cal_bulto': 18500,
            'arena_m3': 98000,
            'aditivo_F1_kg': 48000,
            'sellado_FX_galon': 195000,
            'valor_jornal': 125000
        }
    }

if 'view' not in st.session_state:
    st.session_state.view = 'home'

def set_view(name):
    st.session_state.view = name

# ==========================================
# 🎨 VISTA 1: HOME
# ==========================================
if st.session_state.view == 'home':
    st.title("🏗️ FERROTEK: Soluciones en Piel de Roca")
    st.subheader("Ingeniería Unibody | Manuel Enrique Prada Forero (TP: 176.633)")
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("### 🛡️ Cerramientos")
        st.write("Muros perimetrales con Sistema Raíz.")
        if st.button("Cotizar Muros", key="btn_muros"): set_view('muros')
    with col2:
        st.success("### 🏠 Viviendas")
        st.write("Modelos de 30, 54 y 84 m².")
        if st.button("Explorar Modelos", key="btn_casas"): set_view('viviendas')
    with col3:
        st.warning("### 🏺 Especiales")
        st.write("Bóvedas (3.80x2.40m) y Estanques.")
        if st.button("Ver Especiales", key="btn_especiales"): set_view('especiales')

# ==========================================
# 🎨 VISTA 2: MUROS
# ==========================================
elif st.session_state.view == 'muros':
    st.button("⬅️ Volver al Menú", on_click=lambda: set_view('home'))
    st.header("🛡️ Configurador de Muro Perimetral")
    ml = st.number_input("Metros Lineales del lote:", value=50.0)
    precio = ml * 325000 
    st.metric("Inversión Total Estimada", f"${precio:,.0f}")
    st.write("**Sistema:** Postes 2\" @ 1.5m + Malla 5mm + Matriz 1:3:3 + Anclaje Raíz de 15cm.")
    

# ==========================================
# 🎨 VISTA 3: VIVIENDAS
# ==========================================
elif st.session_state.view == 'viviendas':
    st.button("⬅️ Volver al Menú", on_click=lambda: set_view('home'))
    st.header("🏠 Modelos Vivienda Unibody")
    
    opcion = st.radio("Seleccione Tamaño:", ["Suite (30m²)", "Familiar (54m²)", "Máster (84m²)"], horizontal=True)
    m2 = 30 if "30" in opcion else (54 if "54" in opcion else 84)
    total = m2 * 980000 
    
    c_a, c_b = st.columns(2)
    with c_a:
        st.metric(f"Inversión {opcion}", f"${total:,.0f}")
        st.write("### ✅ Especificaciones:")
        st.write("- Fachadas: **Doble Membrana**.")
        st.write("- Internos: **Membrana Simple**.")
    with c_b:
        st.write("### 📐 Detalle Técnico")
        st.write("Mortero 1:3:3 autoprotegido y pisos poliméricos.")
        

# ==========================================
# 🎨 VISTA 4: ESPECIALES
# ==========================================
elif st.session_state.view == 'especiales':
    st.button("⬅️ Volver al Menú", on_click=lambda: set_view('home'))
    st.header("🏺 Estructuras Especiales")
    
    t1, t2 = st.tabs(["Bóvedas Ferrotek", "Estanques"])
    with t1:
        st.subheader("Bóveda (3.80m frente x 2.40m centro)")
        largo = st.slider("Largo (m):", 3.0, 15.0, 6.0)
        st.metric("Inversión Est. Bóveda", f"${(largo * 3800000):,.0f}")
        st.info("Base en Perfil C18 (primeros 90cm) + Arcos de varilla.")
        
    with t2:
        st.subheader("Estanques de Alta Densidad")
        d = st.number_input("Diámetro (m):", value=6.0)
        st.metric("Inversión Estanque", f"${(d * 1200000):,.0f}")

# ==========================================
# ⚖️ FOOTER
# ==========================================
st.divider()
st.caption(f"© 2026 Ferrotek - Manuel Enrique Prada Forero | TP: 176.633 CSJ")