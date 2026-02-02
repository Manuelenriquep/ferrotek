import streamlit as st
import math

# ==========================================
# ⚙️ CONFIGURACIÓN Y ESTILOS
# ==========================================
st.set_page_config(page_title="Ferrotek | Ingeniería Unibody", page_icon="🏗️", layout="wide")

# --- BARRA LATERAL ADMINISTRATIVA ---
with st.sidebar:
    st.header("🔐 Panel Director")
    pwd = st.text_input("Contraseña:", type="password")
    if pwd == st.session_state.get('db', {}).get('config', {}).get('admin_pass', 'ferrotek2026'):
        st.success("Acceso Concedido - Modo Edición")
        st.markdown("### 💲 Ajuste de Precios Base")
        if 'db' in st.session_state:
             new_prices = st.data_editor(st.session_state['db']['precios'], num_rows="fixed")
             st.session_state['db']['precios'] = new_prices
             st.toast("¡Precios actualizados en caliente!", icon="✅")
    else:
        st.caption("Área restringida para dirección Ferrotek.")
    
    st.divider()
    # Contacto legal se mantiene aquí, discreto
    st.markdown("### ⚖️ Contacto Jurídico")
    st.markdown("**Manuel E. Prada Forero**\nTP: 176.633 CSJ")


# Inicialización de la DB
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
    volumen_litros = area_m2 * espesor_cm * 10
    total_bultos = math.ceil(volumen_litros / 16)
    return math.ceil(total_bultos * 0.7), math.ceil(total_bultos * 0.3)

# ==========================================
# 🎨 VISTA 1: HOME
# ==========================================
if st.session_state.view == 'home':
    st.title("🏗️ FERROTEK: Soluciones en Piel de Roca")
    st.subheader("Ingeniería Unibody de Alta Resistencia")
    
    with st.expander("💡 ¿Qué es la Tecnología Unibody Ferrotek? (Leer más)"):
        st.markdown("""
        A diferencia de la construcción tradicional, **Ferrotek crea una sola pieza monolítica** sismo-resistente.
        * **Alma de Acero:** Malla electrosoldada de 5mm.
        * **Piel de Roca:** Morteros de alta densidad que no necesitan pintura.
        * **Eficiencia:** Más rápido y resistente que el bloque.
        """)
    st.write("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("### 🛡️ Cerramientos")
        st.write("Muros perimetrales con Sistema Raíz.")
        if st.button("Cotizar Muros", key="nav_muros"): set_view('muros')
    with col2:
        st.success("### 🏠 Viviendas")
        st.write("Modelos desde 30m² hasta 84m². La ganga del $1M/m².")
        if st.button("Explorar Modelos", key="nav_casas"): set_view('viviendas')
    with col3:
        st.warning("### 🏺 Especiales")
        st.write("Bóvedas arquitectónicas y estanques.")
        if st.button("Ver Especiales", key="nav_especiales"): set_view('especiales')

# ==========================================
# 🎨 VISTA 2: MUROS
# ==========================================
elif st.session_state.view == 'muros':
    st.button("⬅️ Menú Principal", on_click=lambda: set_view('home'))
    st.header("🛡️ Configurador de Muro Perimetral")
    
    ml = st.number_input("Metros Lineales del lote:", value=50.0, step=10.0)
    h = 2.2
    br, ba = calcular_bultos(ml * h)
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Inversión Total Estimada", f"${(ml * 325000):,.0f}")
        st.markdown("---")
        st.write("### 📦 Logística de Materiales (Bultos 30kg)")
        st.write(f"- **{br} Bultos Tipo R** (Relleno Estructural Gris)")
        st.write(f"- **{ba} Bultos Tipo A** (Acabado Piel de Roca Crema)")
        st.info("ℹ️ Cada bulto se mezcla con 6L de agua en obra.")
        
        with st.expander("Ver Ventajas Técnicas"):
            st.write("- **Anclaje Raíz:** Zapata continua de 15cm.")
            st.write("- **Autoprotegido:** Matriz de cal hidrófuga.")
            st.write("- **Seguridad:** Alma de acero de 5mm.")

    with c2:
        st.write("#### Textura Real 'Piel de Roca'")
        # ATENCIÓN: Verifica que este nombre sea exacto en tu repo
        try:
            st.image("image_4.png", caption="Acabado natural tras 12h de lluvia.")
        except:
            st.error("⚠️ Error: No se encuentra 'image_4.png' en el repositorio.")

# ==========================================
# 🎨 VISTA 3: VIVIENDAS (CORREGIDA CON TUS NOMBRES)
# ==========================================
elif st.session_state.view == 'viviendas':
    st.button("⬅️ Menú Principal", on_click=lambda: set_view('home'))
    st.header("🏠 Viviendas Unibody (Llave en Mano)")
    
    # --- CORRECCIÓN DE NOMBRES AQUÍ ---
    fotos_casas = {
        "Suite (30m²)": "render_modelo1.png",
        "Familiar (54m²)": "render_modelo2.png", 
        "Máster (84m²)": "render_modelo3.png"
    }
    
    opcion = st.radio("Seleccione Modelo:", list(fotos_casas.keys()), horizontal=True)
    m2 = 30 if "30" in opcion else (54 if "54" in opcion else 84)
    foto_actual = fotos_casas[opcion]
    
    c_a, c_b = st.columns([1, 2])
    with c_a:
        st.metric(f"Inversión {opcion}", f"${(m2 * 1000000):,.0f}")
        st.write(f"**Precio por m²: $1,000,000 COP**")
        st.markdown("---")
        
        st.write("### ✅ Especificaciones Premium:")
        with st.expander("🌡️ Doble Membrana Térmica"):
            st.write("Aislamiento superior en fachadas.")
        with st.expander("📐 Optimización de Espacio"):
            st.write("Muros internos delgados de alta resistencia.")
        with st.expander("✨ Acabados de Autor"):
            st.write("Pisos poliméricos y muros Piel de Roca (sin pintura).")

    with c_b:
        st.write(f"#### Render: Modelo {opcion}")
        try:
            st.image(foto_actual, use_column_width=True)
        except:
            st.error(f"⚠️ Error: No se encuentra '{foto_actual}' en el repositorio. Verifique el nombre exacto.")

# ==========================================
# 🎨 VISTA 4: ESPECIALES
# ==========================================
elif st.session_state.view == 'especiales':
    st.button("⬅️ Menú Principal", on_click=lambda: set_view('home'))
    st.header("🏺 Estructuras Especiales Ferrotek")
    
    t1, t2 = st.tabs(["Bóveda Arquitectónica", "Estanques Productivos"])
    with t1:
        st.subheader("Bóveda de 3.80m (Luz) x 2.40m (Altura)")
        largo = st.slider("Largo (m):", 3.0, 15.0, 6.0)
        st.metric("Inversión Estimada", f"${(largo * 3800000):,.0f}")
        
        c_esp1, c_esp2 = st.columns(2)
        with c_esp1:
             st.write("### ⚙️ Ingeniería de Arco:")
             st.write("Nace de **Perfil C Calibre 18** (primeros 90cm) con proyección de arcos de varilla y malla.")
        with c_esp2:
             # ATENCIÓN: Verifica este nombre también
             try:
                st.image("image_15.png", caption="Potencial de acabado Bóveda", use_column_width=True)
             except:
                 st.error("⚠️ Error: No se encuentra 'image_15.png' en el repositorio.")
                 
    with t2:
        st.subheader("Piscicultura de Alta Densidad")
        d = st.number_input("Diámetro del estanque (m):", value=6.0)
        st.metric("Inversión Estanque Monolítico", f"${(d * 1200000):,.0f}")
        st.write("Tanques de una sola pieza, sin filtraciones.")

# ==========================================
# ⚖️ FOOTER CORPORATIVO (LIMPIO)
# ==========================================
st.divider()
st.caption("© 2026 FERROTEK Ingeniería Unibody | Floridablanca, Santander, Colombia")