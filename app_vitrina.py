import streamlit as st
import math

# ==========================================
# ⚙️ CONFIGURACIÓN Y ESTILOS
# ==========================================
st.set_page_config(page_title="Ferrotek | Ingeniería Unibody", page_icon="🏗️", layout="wide")

# Inicialización de la DB de Precios y Configuración
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
# 🧠 MOTOR DE LOGÍSTICA (BULTOS DE 30KG)
# ==========================================
def calcular_bultos(area_m2, espesor_cm=4):
    # Un bulto de 30kg produce aprox 16 litros de mezcla húmeda
    volumen_litros = area_m2 * espesor_cm * 10
    total_bultos = math.ceil(volumen_litros / 16)
    # 70% Relleno (Gris), 30% Acabado (Crema con Cal)
    return math.ceil(total_bultos * 0.7), math.ceil(total_bultos * 0.3)

# ==========================================
# 🎨 VISTA 1: HOME
# ==========================================
if st.session_state.view == 'home':
    st.title("🏗️ FERROTEK: Soluciones en Piel de Roca")
    st.subheader("Ingeniería Unibody | Manuel Enrique Prada Forero (TP: 176.633)")
    st.write("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("### 🛡️ Cerramientos")
        st.write("Muros perimetrales con Sistema Raíz. El hit contra la mampostería.")
        if st.button("Cotizar Muros", key="nav_muros"): set_view('muros')
    with col2:
        st.success("### 🏠 Viviendas")
        st.write("Modelos de 30, 54 y 84 m². Ingeniería de doble membrana y pisos poliméricos.")
        if st.button("Explorar Modelos", key="nav_casas"): set_view('viviendas')
    with col3:
        st.warning("### 🏺 Especiales")
        st.write("Bóvedas de 3.80m de frente y Estanques Piscícolas de alta densidad.")
        if st.button("Ver Especiales", key="nav_especiales"): set_view('especiales')

# ==========================================
# 🎨 VISTA 2: MUROS
# ==========================================
elif st.session_state.view == 'muros':
    st.button("⬅️ Menú Principal", on_click=lambda: set_view('home'))
    st.header("🛡️ Configurador de Muro Perimetral")
    
    ml = st.number_input("Metros Lineales del lote:", value=50.0, step=10.0)
    h = 2.2 # Altura estándar
    br, ba = calcular_bultos(ml * h)
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Inversión Total Estimada", f"${(ml * 325000):,.0f}")
        st.write("### 📦 Despacho de Materiales:")
        st.write(f"- **{br} Bultos Tipo R** (Relleno Rugoso)")
        st.write(f"- **{ba} Bultos Tipo A** (Acabado Piel de Roca)")
    with c2:
        # Usando la imagen de la textura del muro
        st.image("image_4.png", caption="Textura real Piel de Roca al natural")

# ==========================================
# 🎨 VISTA 3: VIVIENDAS
# ==========================================
elif st.session_state.view == 'viviendas':
    st.button("⬅️ Menú Principal", on_click=lambda: set_view('home'))
    st.header("🏠 Viviendas Unibody (Llave en Mano)")
    
    opcion = st.radio("Modelo:", ["Suite (30m²)", "Familiar (54m²)", "Máster (84m²)"], horizontal=True)
    m2 = 30 if "30" in opcion else (54 if "54" in opcion else 84)
    
    c_a, c_b = st.columns(2)
    with c_a:
        st.metric(f"Inversión {opcion}", f"${(m2 * 1000000):,.0f}")
        st.write("### ✅ Incluye:")
        st.write("- Fachadas de doble membrana.")
        st.write("- Muros internos de membrana simple.")
        st.write("- Pisos poliméricos de alta resistencia.")
    with c_b:
        # Usando la imagen de la casa terminada
        st.image("image_6.png", caption="Ejecución real sistema Ferrotek")

# ==========================================
# 🎨 VISTA 4: ESPECIALES
# ==========================================
elif st.session_state.view == 'especiales':
    st.button("⬅️ Menú Principal", on_click=lambda: set_view('home'))
    st.header("🏺 Bóvedas y Estanques")
    
    t1, t2 = st.tabs(["Bóveda Ferrotek", "Estanques"])
    with t1:
        st.subheader("Bóveda (3.80m frente x 2.40m centro)")
        largo = st.slider("Largo (m):", 3.0, 15.0, 6.0)
        st.metric("Inversión Est.", f"${(largo * 3800000):,.0f}")
        st.write("Estructura naciendo de perfiles C18 (90cm) con arcos de varilla.")
        # Usando el render del domo moderno para vender el potencial
        st.image("image_15.png", caption="Potencial de acabado Bóveda Ferrotek")
    with t2:
        st.subheader("Piscicultura de Alta Densidad")
        d = st.number_input("Diámetro del estanque (m):", value=6.0)
        st.metric("Inversión Estanque", f"${(d * 1200000):,.0f}")
        st.write("Tanques monolíticos sin juntas.")

# ==========================================
# ⚖️ FOOTER CORPORATIVO
# ==========================================
st.divider()
# Mucho más limpio, enfocado en la marca y la ubicación.
st.caption("© 2026 FERROTEK Ingeniería Unibody | Floridablanca, Santander, Colombia")