import streamlit as st
import core_calculo as core
import core_planos
import os # Necesario para verificar si las imágenes existen

st.set_page_config(page_title="Ferrotek | Catálogo Digital", page_icon="🏡", layout="centered")

# --- ESTILOS CSS (Optimizados) ---
st.markdown("""
    <style>
    .big-font { font-size:28px !important; color: #154360; font-weight: 800;}
    .sub-font { font-size:18px !important; color: #555; font-style: italic;}
    .price-tag { font-size:42px; color: #27AE60; font-weight: bold; background-color: #eafaf1; padding: 10px; border-radius: 8px; text-align: center;}
    .card { background-color: #ffffff; padding: 25px; border-radius: 15px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 6px solid #2980B9;}
    .check-list { background-color: #f8f9f9; padding: 15px; border-radius: 8px; border: 1px solid #ddd; margin-bottom: 10px; }
    .highlight { color: #E67E22; font-weight: bold; }
    .area-badge { background-color: #E67E22; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; vertical-align: middle;}
    </style>
    """, unsafe_allow_html=True)

# Banner Principal
st.image("https://via.placeholder.com/800x200.png?text=FERROTEK+Ingenieria+Rural", use_container_width=True)

# --- MENÚ LATERAL ---
st.sidebar.header("🛠️ Configurador de Proyectos")
categoria = st.sidebar.radio("¿Qué deseas construir?", ["🏠 Casas Modulares", "🐟 Estanques Piscícolas", "⛺ Bóvedas Glamping"])

datos = None
modelo_seleccionado = 0 

# LÓGICA DE SELECCIÓN Y CÁLCULO
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

# --- VISUALIZACIÓN PRINCIPAL ---
if datos:
    # Título y Descripción General
    st.markdown(f'<p class="big-font">{datos["nombre"]}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-font">{datos["descripcion"]}</p>', unsafe_allow_html=True)

    # --- MÉTRICAS CON TIEMPOS DE ENTREGA (NUEVO) ---
    c1, c2, c3 = st.columns(3)
    
    # 1. Definir tiempos estimados (Ajustables)
    tiempo_entrega = "Consultar"
    if categoria == "🏠 Casas Modulares":
         tiempo_entrega = "30 - 45 Días"
    elif categoria == "🐟 Estanques":
         tiempo_entrega = "10 - 15 Días"
    elif categoria == "⛺ Bóvedas":
         tiempo_entrega = "5 - 7 Días"

    # 2. Mostrar métricas
    if categoria == "🐟 Estanques":
        c1.metric("💧 Capacidad", f"{datos['volumen_litros']:,} L")
        c2.metric("📏 Altura Muro", "1.20 m")
    else:
        c1.metric("📏 Área Total", f"{datos['area']} m²")
        c2.metric("🏠 Altura", f"{datos['altura']} m")
    
    # 3. Métrica de Tiempo
    c3.metric("🗓️ Tiempo Aprox.", tiempo_entrega)
    
    st.markdown("---")

    # PESTAÑAS DE DETALLE
    tab1, tab2, tab3 = st.tabs(["📐 Distribución y Renders", "💰 Inversión", "🛒 Materiales"])

    # 1. PESTAÑA DISEÑO (Renders + Planos + Áreas Notorias)
    with tab1:
        if categoria == "🏠 Casas Modulares":
            col_text, col_visual = st.columns([1, 1.5])
            
            # Columna de Texto (Izquierda) - ÁREAS RESALTADAS
            with col_text:
                if modelo == 1: 
                    st.markdown(f"### 🌟 Concepto Loft | <span class='highlight'>{datos['area']} m²</span>", unsafe_allow_html=True)
                    st.write("Diseñado para maximizar la vista. La cama King Size 'flota' en el centro, mirando al paisaje, mientras que el baño y vestier quedan ocultos tras un muro cabecero funcional.")
                elif modelo == 2: 
                    st.markdown(f"### 🏡 Concepto Familiar | <span class='highlight'>{datos['area']} m²</span>", unsafe_allow_html=True)
                    st.write("Privacidad ante todo. Un pasillo central separa acústicamente la zona social (ruido) de las habitaciones (descanso). Ideal para lotes estrechos y largos.")
                elif modelo == 3: 
                    st.markdown(f"### 🏰 Concepto Hacienda | <span class='highlight'>{datos['area']} m²</span>", unsafe_allow_html=True)
                    st.write("Majestuosidad rural. Un gran salón central de techo alto conecta dos alas independientes: una privada para los dueños y otra para huéspedes o hijos.")
            
            # Columna Visual (Derecha) - RENDERS INTELIGENTES Y PLANOS
            with col_visual:
                st.caption("👁️ Así se siente vivir aquí (Render 3D)")
                
                # --- BÚSQUEDA INTELIGENTE DE IMAGEN (PNG o JPG) ---
                base_name = f"render_modelo{modelo_seleccionado}"
                possible_files = [f"{base_name}.png", f"{base_name}.jpg", f"{base_name}.jpeg"]
                
                image_found = False
                for file_path in possible_files:
                    if os.path.exists(file_path):
                        st.image(file_path, use_container_width=True)
                        image_found = True
                        break 

                if not image_found:
                    st.info(f"ℹ️ Render no disponible. Se buscó: {', '.join(possible_files)}")
                
                st.markdown("---")

                # B. PLANO TÉCNICO (Siempre visible)
                st.caption(f"📐 Plano de Distribución ({datos['area']} m²)")
                svg_plano = core_planos.dibujar_planta(modelo_seleccionado)
                st.markdown(svg_plano, unsafe_allow_html=True)
        
        elif categoria == "🐟 Estanques":
            st.info("Diseño circular para máxima resistencia hidrostática utilizando la forma natural del tanque.")
        elif categoria == "⛺ Bóvedas":
            st.info("Diseño de arco catenario sobre muretes rectos para ganar altura y confort habitable.")

    # 2. PESTAÑA FINANCIERA
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
             st.markdown(f'<div class="card"><h3 style="text-align:center; color:#154360">Precio Llave en Mano</h3><div class="price-tag">${datos["precio_venta"]:,.0f}</div></div>', unsafe_allow_html=True)
        with col2:
             st.markdown("#### 📊 Estructura de Costos")
             st.write(f"**Costo Directo (Material + MO):** ${datos['costo_directo']:,.0f}")
             # Barra de progreso visual para el margen
             margen_pct = (datos['precio_venta'] - datos['costo_directo']) / datos['precio_venta']
             st.progress(margen_pct, text=f"Margen Bruto Estimado: {int(margen_pct*100)}%")
             st.caption("Nota: El margen cubre imprevistos, gestión y utilidad.")

    # 3. PESTAÑA COMPRAS
    with tab3:
        lc = datos['lista_compras']
        st.write("### 📋 Listado Maestro de Insumos")
        c_a, c_b = st.columns(2)
        with c_a:
            st.markdown('<p class="highlight">🧱 Obra Gris & Estructura</p>', unsafe_allow_html=True)
            st.checkbox(f"{lc['cemento']} Bultos Cemento", value=True)
            if lc['cal'] > 0: st.checkbox(f"{lc['cal']} Bultos Cal Hidratada", value=True)
            st.checkbox(f"{lc['arena']} m³ Arena", value=True)
            if lc['triturado'] > 0: st.checkbox(f"{lc['triturado']} m³ Triturado", value=True)
            if lc['malla'] > 0: st.checkbox(f"{lc['malla']} Paneles Malla", value=True)
        with c_b:
            st.markdown('<p class="highlight">🦴 Refuerzos & Acabados</p>', unsafe_allow_html=True)
            if lc['tubos'] > 0: st.checkbox(f"{lc['tubos']} Tubos Estructurales", value=True)
            if lc['varillas'] > 0: st.checkbox(f"{lc['varillas']} Varillas", value=True)
            if lc['alambron'] > 0: st.checkbox(f"{lc['alambron']} Kg Alambrón", value=True)
            # Resumen de kits si es casa
            if categoria == "🏠 Casas Modulares":
                 st.checkbox(f"Kit Techo Nelta ({int(datos['area'])}m² cubiertos)", value=True)
                 st.checkbox("Paquete Carpintería y Vidrios", value=True)