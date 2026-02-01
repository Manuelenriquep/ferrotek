# GUARDA ESTO COMO: app_vitrina.py

import streamlit as st
import core_calculo as core
import core_planos  # Conexión con los planos SVG

st.set_page_config(page_title="Ferrotek | Catálogo Digital", page_icon="🏡", layout="centered")

# Estilos CSS
st.markdown("""
    <style>
    .big-font { font-size:28px !important; color: #154360; font-weight: 800;}
    .sub-font { font-size:18px !important; color: #555; font-style: italic;}
    .price-tag { font-size:42px; color: #27AE60; font-weight: bold; background-color: #eafaf1; padding: 10px; border-radius: 8px; text-align: center;}
    .card { background-color: #ffffff; padding: 25px; border-radius: 15px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 6px solid #2980B9;}
    .check-list { background-color: #f8f9f9; padding: 15px; border-radius: 8px; border: 1px solid #ddd; margin-bottom: 10px; }
    .highlight { color: #E67E22; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.image("https://via.placeholder.com/800x200.png?text=FERROTEK+Ingenieria+Rural", use_container_width=True)

# --- MENÚ LATERAL ---
st.sidebar.header("🛠️ Configurador de Proyectos")
categoria = st.sidebar.radio("¿Qué deseas construir?", ["🏠 Casas Modulares", "🐟 Estanques Piscícolas", "⛺ Bóvedas Glamping"])

datos = None
modelo_seleccionado = 0 

# LÓGICA DE SELECCIÓN
if categoria == "🏠 Casas Modulares":
    st.sidebar.markdown("---")
    st.sidebar.info("✨ Llave en Mano: Baños, Cocina, Redes y Vidrios.")
    modelo = st.sidebar.selectbox("Selecciona tu Modelo:", [1, 2, 3], format_func=lambda x: f"Modelo {x}")
    datos = core.generar_presupuesto("vivienda", modelo)
    modelo_seleccionado = modelo
elif categoria == "🐟 Estanques":
    st.sidebar.markdown("---")
    st.sidebar.success("💧 Garantía: Cal Hidrófuga + Malla Doble.")
    dim = st.sidebar.select_slider("Diámetro del Tanque:", [1, 2, 4, 8, 10, 12], value=4)
    datos = core.generar_presupuesto("estanque", dim)
elif categoria == "⛺ Bóvedas":
    st.sidebar.markdown("---")
    st.sidebar.warning("🚀 Rápido: Estructura Telescópica.")
    largo = st.sidebar.radio("Profundidad:", [3, 6], format_func=lambda x: f"{x} Metros")
    datos = core.generar_presupuesto("boveda", largo)

# VISUALIZACIÓN
if datos:
    st.markdown(f'<p class="big-font">{datos["nombre"]}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-font">{datos["descripcion"]}</p>', unsafe_allow_html=True)

    # Métricas
    c1, c2, c3 = st.columns(3)
    if categoria == "🐟 Estanques":
        c1.metric("💧 Capacidad", f"{datos['volumen_litros']:,} L")
        c2.metric("📏 Altura Muro", "1.20 m")
    else:
        c1.metric("📏 Área Total", f"{datos['area']} m²")
        c2.metric("🏠 Altura", f"{datos['altura']} m")
    c3.metric("🔨 Tiempo Est.", "Entrega Rápida")
    
    st.markdown("---")

    # PESTAÑAS
    tab1, tab2, tab3 = st.tabs(["📐 Distribución y Diseño", "💰 Inversión", "🛒 Materiales"])

    # 1. PESTAÑA DISEÑO (LÓGICA RENDER vs PLANO)
    with tab1:
        if categoria == "🏠 Casas Modulares":
            col_text, col_plan = st.columns([1, 1.5])
            with col_text:
                if modelo == 1: 
                    st.markdown("""
                    ### 🌟 "El Refugio Inteligente"
                    **Ideal para Glamping o Solteros.**
                    * **Fachada:** Techo a un agua y gran ventanal.
                    * **Loft:** Cama King orientada a la vista.
                    * **Baño Oculto:** Detrás del cabecero para máxima estética.
                    """)
                elif modelo == 2: 
                    st.markdown("""
                    ### 🏡 "La Casa Funcional"
                    **Ideal Familia Pequeña.**
                    * **Privacidad:** Habitaciones separadas de la zona social.
                    * **Acabados:** Piso microcemento industrial.
                    """)
                elif modelo == 3: 
                    st.markdown("""
                    ### 🏰 "La Hacienda Moderna"
                    **Vivienda Definitiva.**
                    * **Volumen:** Techo catedral a dos aguas.
                    * **Social:** Sala-Comedor gigante.
                    * **Master:** Suite privada.
                    """)
            
            with col_plan:
                # --- AQUÍ ESTÁ EL CAMBIO ---
                if modelo_seleccionado == 1:
                    # SI ES MODELO 1, MUESTRA TU RENDER
                    try:
                        st.image("render_modelo1.png", caption="Render 3D: Concepto Glamping", use_column_width=True)
                    except:
                        st.error("⚠️ Falta el archivo 'render_modelo1.png' en la carpeta.")
                else:
                    # SI ES MODELO 2 o 3, MUESTRA EL PLANO SVG
                    svg_plano = core_planos.dibujar_planta(modelo_seleccionado)
                    st.markdown(svg_plano, unsafe_allow_html=True) 
                    st.caption("Distribución Arquitectónica Optimizada")
        
        elif categoria == "🐟 Estanques":
            st.info("Diseño circular para máxima resistencia hidrostática.")
        elif categoria == "⛺ Bóvedas":
            st.info("Diseño de arco sobre muretes para altura y confort.")

    # 2. PESTAÑA FINANCIERA
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
             st.markdown(f'<div class="card"><div class="price-tag">${datos["precio_venta"]:,.0f}</div></div>', unsafe_allow_html=True)
        with col2:
             st.write(f"**Costo Directo:** ${datos['costo_directo']:,.0f}")
             st.progress(0.7, text="Margen Saludable")

    # 3. PESTAÑA COMPRAS
    with tab3:
        lc = datos['lista_compras']
        st.write("### 📋 Resumen de Materiales")
        c_a, c_b = st.columns(2)
        with c_a:
            st.checkbox(f"{lc['cemento']} Bultos Cemento", value=True)
            if lc['cal'] > 0: st.checkbox(f"{lc['cal']} Bultos Cal", value=True)
            st.checkbox(f"{lc['arena']} Arena", value=True)
            st.checkbox(f"{lc['triturado']} Triturado", value=True)
        with c_b:
            if lc['tubos'] > 0: st.checkbox(f"{lc['tubos']} Tubos Est.", value=True)
            if lc['varillas'] > 0: st.checkbox(f"{lc['varillas']} Varillas", value=True)
            if lc['alambron'] > 0: st.checkbox(f"{lc['alambron']} Kg Alambrón", value=True)
            st.checkbox(f"{lc['malla']} Malla", value=True)