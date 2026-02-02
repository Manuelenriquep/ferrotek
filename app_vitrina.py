import streamlit as st
import math
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURACIÓN Y ESTILOS
# ==========================================
st.set_page_config(page_title="Ferrotek | Ingeniería Unibody", page_icon="🏗️", layout="wide")

# Inicialización de la DB en sesión si no existe
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

# ==========================================
# 🧠 LÓGICA DE NAVEGACIÓN
# ==========================================
if 'view' not in st.session_state:
    st.session_state.view = 'home'

def set_view(name):
    st.session_state.view = name

# ==========================================
# 🎨 VISTA 1: HOME (MENÚ PRINCIPAL)
# ==========================================
if st.session_state.view == 'home':
    st.title("🏗️ FERROTEK: Soluciones en Piel de Roca")
    st.subheader("Ingeniería Unibody | Manuel Enrique Prada Forero (TP: 176.633)")
    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("### 🛡️ Cerramientos")
        st.write("Muros perimetrales con Sistema Raíz. El 'Hit' de ventas contra la mampostería tradicional.")
        if st.button("Cotizar Muros", key="btn_muros"): set_view('muros')

    with col2:
        st.success("### 🏠 Viviendas")
        st.write("Modelos de 30, 54 y 84 m². Ingeniería de doble membrana y pisos poliméricos.")
        if st.button("Explorar Modelos", key="btn_casas"): set_view('viviendas')

    with col3:
        st.warning("### 🏺 Especiales")
        st.write("Bóvedas (3.80x2.40m) y Estanques Piscícolas de alta densidad.")
        if st.button("Ver Especiales", key="btn_especiales"): set_view('especiales')

# ==========================================
# 🎨 VISTA 2: MUROS (YA FUNCIONAL)
# ==========================================
elif st.session_state.view == 'muros':
    st.button("⬅️ Volver al Menú", on_click=lambda: set_view('home'))
    st.header("🛡️ Configurador de Muro Perimetral")
    ml = st.number_input("Metros Lineales del lote:", value=50.0)
    # Lógica simplificada para visualización
    precio = ml * 325000 
    st.metric("Inversión Total", f"${precio:,.0f}")
    st.write("**Sistema:** Postes 2\" @ 1.5m + Malla 5mm + Matriz 1:3:3.")

# ==========================================
# 🎨 VISTA 3: VIVIENDAS (CORREGIDA)
# ==========================================
elif st.session_state.view == 'viviendas':
    st.button("⬅️ Volver al Menú", on_click=lambda: set_view('home'))
    st.header("🏠 Modelos Vivienda Unibody")
    
    opcion = st.radio("Seleccione Tamaño:", ["Suite (30m²)", "Familiar (54m²)", "Máster (84m²)"], horizontal=True)
    m2 = 30 if "30" in opcion else (54 if "54" in opcion else 84)
    
    # Cálculo base
    costo_m2 = 980000 
    total = m2 * costo_m2
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric(f"Inversión {opcion}", f"${total:,.0f}")
        st.write("### ✅ Especificaciones:")
        st.write("- Fachadas en **Doble Membrana**.")
        st.write("- Muros internos en **Membrana Simple**.")
        st.write("- Pisos en **Matriz 2:1 + Polímeros**.")
    
    with col_b:
        st.write("### 📐 Detalle Constructivo")
        # Aquí es donde estaba el error de indentación, ahora tiene contenido:
        st.write("El sistema Unibody garantiza que la estructura sea una sola pieza ligada por el sándwich de malla 5mm.")
        

# ==========================================
# 🎨 VISTA 4: ESPECIALES (SIGUIENTE BLOQUE)
# ==========================================
elif st.session_state.view == 'especiales':
    # ... resto del código
        

# ==========================================
# 🎨 VISTA 4: ESPECIALES (NUEVA!)
# ==========================================
elif st.session_state.view == 'especiales':
    st.button("⬅️ Volver al Menú", on_click=lambda: set_view('home'))
    st.header("🏺 Estructuras Especiales")
    
    tab1, tab2 = st.tabs(["Bóvedas Ferrotek", "Estanques Piscícolas"])
    
    with tab1:
        st.subheader("Bóveda de Ingeniería (3.80m frente x 2.40m centro)")
        largo = st.slider("Largo de la Bóveda (m):", 3.0, 15.0, 6.0)
        # Base Perfil C18 (90cm) + Arcos de Varilla
        costo_boveda = largo * 3800000 # Estimado según core_planos
        st.metric("Inversión Est. Bóveda", f"${costo_boveda:,.0f}")
        st.info("Refuerzo base en Perfil C18 (primeros 90cm) para anclaje de arcos.")
        

    with tab2:
        st.subheader("Estanques de Alta Densidad")
        diametro = st.number_input("Diámetro del Estanque (m):", value=6.0)
        st.write("Piel de roca rica en cemento para cero filtraciones.")
        st.metric("Inversión Estanque", f"${(diametro * 1200000):,.0f}")

# ==========================================
# ⚖️ FOOTER JURÍDICO
# ==========================================
st.divider()
st.caption(f"© 2026 Ferrotek - Manuel Enrique Prada Forero | TP: 176.633 CSJ | Floridablanca, Santander")