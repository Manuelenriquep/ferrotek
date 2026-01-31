import streamlit as st
import core_calculo as core

st.set_page_config(page_title="Ferrotek | Lista de Compras", page_icon="🛒", layout="centered")

# CSS Estilos
st.markdown("""
    <style>
    .big-font { font-size:26px !important; color: #154360; font-weight: bold; }
    .price-tag { font-size:32px; color: #27AE60; font-weight: bold; }
    .check-list { background-color: #fff; padding: 15px; border-radius: 8px; border: 1px solid #ddd; margin-bottom: 10px; }
    .check-header { font-weight: bold; color: #E67E22; font-size: 18px; margin-bottom: 10px; border-bottom: 2px solid #E67E22;}
    </style>
    """, unsafe_allow_html=True)

st.image("https://via.placeholder.com/800x150.png?text=FERROTEK+Listado+de+Materiales", use_container_width=True)

# --- CONFIGURACIÓN ---
st.sidebar.header("🛠️ Configura tu Pedido")
categoria = st.sidebar.radio("Categoría:", ["🏠 Casas Modulares", "🐟 Estanques", "⛺ Bóvedas"])

datos = None

if categoria == "🏠 Casas Modulares":
    st.sidebar.info("Incluye Carpintería y Redes")
    modelo = st.sidebar.selectbox("Modelo:", [1, 2, 3], format_func=lambda x: f"Modelo {x}")
    datos = core.generar_presupuesto("vivienda", modelo)
elif categoria == "🐟 Estanques":
    dim = st.sidebar.select_slider("Diámetro:", [2, 4, 8, 10, 12], value=4)
    datos = core.generar_presupuesto("estanque", dim)
elif categoria == "⛺ Bóvedas":
    largo = st.sidebar.radio("Fondo:", [3, 6], format_func=lambda x: f"{x} Metros")
    datos = core.generar_presupuesto("boveda", largo)

if datos:
    st.markdown(f"### {datos['nombre']}")
    st.caption(datos['descripcion'])
    
    # TABS (PESTAÑAS)
    tab1, tab2 = st.tabs(["🛒 Lista de Compras", "💰 Resumen Financiero"])
    
    with tab1:
        lc = datos['lista_compras']
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown('<div class="check-list">', unsafe_allow_html=True)
            st.markdown('<p class="check-header">🧱 Obra Negra (Ferretería)</p>', unsafe_allow_html=True)
            # AQUÍ ESTÁ LA CORRECCIÓN VISUAL:
            st.checkbox(f"{lc['cemento']} Bultos Cemento (50kg)", value=True)
            st.checkbox(f"{lc['cal']} Bultos Cal Hidratada (10kg)", value=True) 
            st.checkbox(f"{lc['arena']} m³ Arena de Río", value=True)
            if lc['triturado'] > 0:
                st.checkbox(f"{lc['triturado']} m³ Triturado (Piso)", value=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="check-list">', unsafe_allow_html=True)
            st.markdown('<p class="check-header">🦴 Acero y Estructura</p>', unsafe_allow_html=True)
            if lc['tubos'] > 0:
                st.checkbox(f"{lc['tubos']} Tubos Estructurales 50x50 (6m)", value=True)
            if lc['varillas'] > 0:
                st.checkbox(f"{lc['varillas']} Varillas Corrugadas (6m)", value=True)
            st.checkbox(f"{lc['malla']} Paneles Malla Electrosoldada", value=True)
            st.checkbox(f"{lc['zaranda']} Rollos Malla Gallinero (30m)", value=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_b:
            if lc['techo']:
                st.markdown('<div class="check-list">', unsafe_allow_html=True)
                st.markdown('<p class="check-header">☂️ Cubierta Nelta</p>', unsafe_allow_html=True)
                st.checkbox(f"{lc['techo']['tejas']} Tejas Termoacústicas (5.70m)", value=True)
                st.checkbox(f"{lc['techo']['caballetes']} Caballetes", value=True)
                st.checkbox(f"{lc['techo']['perfiles']} Perfiles C (Correas)", value=True)
                st.markdown('</div>', unsafe_allow_html=True)

            if lc.get('carpinteria') or lc.get('hidro'):
                st.markdown('<div class="check-list">', unsafe_allow_html=True)
                st.markdown('<p class="check-header">🚪 Acabados y Dotación</p>', unsafe_allow_html=True)
                
                # Carpintería
                carp = lc.get('carpinteria', {})
                if carp.get('p_ext'): st.checkbox(f"{carp['p_ext']} Puertas ppal. Seguridad", value=True)
                if carp.get('p_int'): st.checkbox(f"{carp['p_int']} Puertas Interior Entamboradas", value=True)
                if carp.get('vent'): st.checkbox(f"{carp['vent']} Ventanas Aluminio 1x1", value=True)
                
                # Hidro
                hidro = lc.get('hidro', {})
                if hidro.get('baños'): st.checkbox(f"{hidro['baños']} Kits Baño (Sanitario+Grifería)", value=True)
                if hidro.get('cocina'): st.checkbox("1 Kit Lavaplatos + Grifería", value=True)
                
                # Varios
                if lc['elec']: st.checkbox(f"{lc['elec']} Puntos Eléctricos (Material)", value=True)
                if lc['area_piso']: st.checkbox(f"{lc['area_piso']} m² Microcemento (Acabado)", value=True)
                st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.metric("Precio Sugerido Venta", f"${datos['precio_venta']:,.0f}")
        st.metric("Costo Directo", f"${datos['costo_directo']:,.0f}")
        st.progress(0.7, text="Margen de Utilidad: 30%")

st.markdown("---")
st.caption("© 2026 Ferrotek | Sistema de Gestión de Materiales")