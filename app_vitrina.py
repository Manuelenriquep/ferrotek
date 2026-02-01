import streamlit as st
import core_calculo as core
import core_planos
import os # Necesario para verificar si la imagen existe

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

# Banner Principal
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

# VISUALIZACIÓN DE RESULTADOS
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
    tab1, tab2, tab3 = st.tabs(["📐 Distribución", "💰 Inversión", "🛒 Materiales"])

    # 1. PESTAÑA DISEÑO
    with tab1:
        if categoria == "🏠 Casas Modulares":
            col_text, col_visual = st.columns([1, 1.5])
            
            with col_text:
                if modelo == 1: 
                    st.markdown("### 🌟 Concepto Loft")
                    st.write("Diseñado para maximizar la vista. La cama King Size 'flota' en el centro, mirando al paisaje, mientras que el baño y vestier quedan ocultos tras un muro cabecero funcional.")
                elif modelo == 2: 
                    st.markdown("### 🏡 Concepto Familiar")
                    st.write("Privacidad ante todo. Un pasillo central separa acústicamente la zona social (ruido) de las habitaciones (descanso).")
                elif modelo == 3: 
                    st.markdown("### 🏰 Concepto Hacienda")
                    st.write("Majestuosidad rural. Un gran salón central de techo alto conecta dos alas independientes: una para los dueños y otra para huéspedes.")
            
            with col_visual:
                # --- LÓGICA VISUAL: RENDER + PLANO ---
                
                # A. INTENTAR MOSTRAR RENDER SI EXISTE
                if modelo_seleccionado == 1:
                    st.caption("👁️ Render 3D - Experiencia Inmersiva")
                    if os.path.exists("render_modelo1.png"):
                        st.image("render_modelo1.png", use_container_width=True)
                    else:
                        st.info("ℹ️ Para ver el render, asegúrate que el archivo se llame 'render_modelo1.png'")
                    st.markdown("---")

                # B. SIEMPRE MOSTRAR PLANO TÉCNICO
                st.caption("📐 Plano de Distribución")
                svg_plano = core_planos.dibujar_planta(modelo_seleccionado)
                st.markdown(svg_plano, unsafe_allow_html=True)
        
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