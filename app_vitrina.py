import streamlit as st
import core_calculo as core

st.set_page_config(page_title="Ferrotek | Ingeniería Rural", page_icon="🏗️", layout="centered")

# CSS Estilos
st.markdown("""
    <style>
    .big-font { font-size:26px !important; color: #154360; font-weight: bold; }
    .price-tag { font-size:38px; color: #27AE60; font-weight: bold; }
    .card { background-color: #f4f6f7; padding: 20px; border-radius: 12px; margin-bottom: 20px; border-left: 5px solid #2980B9;}
    .unit-tag { color: #555; font-size: 14px; font-style: italic; }
    </style>
    """, unsafe_allow_html=True)

st.image("https://via.placeholder.com/800x200.png?text=FERROTEK+Bucaramanga", use_container_width=True)
st.markdown("### 🏗️ Vitrina Digital de Costos")

# --- MENÚ LATERAL ---
st.sidebar.header("🛠️ Configuración")
categoria = st.sidebar.radio("Categoría:", 
    ["🏠 Casas Modulares", "🐟 Estanques", "⛺ Bóvedas"])

datos = None

if categoria == "🏠 Casas Modulares":
    st.sidebar.markdown("---")
    st.sidebar.info("📍 **Estándar Santander:**\nTeja Termoacústica 5.70m\nAncho Casa: 5.00m")
    modelo = st.sidebar.selectbox("Selecciona Modelo:", [1, 2, 3], 
        format_func=lambda x: f"Modelo {x} ({['Suite', 'Cotidiana', 'Patriarca'][x-1]})")
    datos = core.generar_presupuesto("vivienda", modelo)

elif categoria == "🐟 Estanques":
    st.sidebar.markdown("---")
    dim = st.sidebar.select_slider("Diámetro (m):", [2, 4, 8, 10, 12], value=4)
    datos = core.generar_presupuesto("estanque", dim)

elif categoria == "⛺ Bóvedas":
    st.sidebar.markdown("---")
    largo = st.sidebar.radio("Fondo:", [3, 6], format_func=lambda x: f"{x} Metros")
    datos = core.generar_presupuesto("boveda", largo)

# --- RESULTADOS ---
if datos:
    st.markdown("---")
    st.markdown(f'<p class="big-font">{datos["nombre"]}</p>', unsafe_allow_html=True)
    st.caption(f"📌 {datos['descripcion']}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="card">
            <h4>💰 Precio Sugerido</h4>
            <p class="price-tag">${datos['precio_venta']:,.0f}</p>
            <small>Costo Directo: ${datos['costo_directo']:,.0f}</small>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="card">
            <h4>📋 Especificaciones</h4>
            <p><b>Área:</b> {datos['area']} m²</p>
            <p><b>Techo:</b> Termoacústica (Garantía 10 años)</p>
            <p><b>Mezcla:</b> 1:3:3 Impermeable</p>
        </div>
        """, unsafe_allow_html=True)

    # --- SECCIÓN MEJORADA CON UNIDADES ---
    with st.expander("🧱 Ver Lista de Materiales (Detallada)", expanded=True):
        m = datos['materiales']
        
        st.markdown("##### 🦴 Acero & Estructura")
        st.write(f"• **{m['estructura']}**")
        st.write(f"• **{m['malla']}** Paneles <span class='unit-tag'>(Malla Electrosoldada 6m x 2.35m)</span>", unsafe_allow_html=True)
        st.write(f"• **{m['zaranda']}** Rollos <span class='unit-tag'>(Malla Gallinero 30m x 0.90m)</span>", unsafe_allow_html=True)
        
        st.markdown("##### 🧪 Agregados (Mezcla 1:3:3)")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Cemento", f"{m['cemento']}", "Bultos 50kg")
        with c2:
            st.metric("Cal", f"{m['cal']}", "Bultos 25kg")
        with c3:
            st.metric("Arena", f"{m['arena']}", "m³ (Lavada)")

st.markdown("---")
st.caption("© 2026 Ferrotek | Precios actualizados Bucaramanga")