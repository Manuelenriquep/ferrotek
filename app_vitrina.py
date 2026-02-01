import streamlit as st
import core_calculo as core
import core_planos
import os # Necesario para verificar si las imágenes existen

st.set_page_config(page_title="Ferrotek | Catálogo Digital", page_icon="🏡", layout="centered")

# --- FUNCIONES AUXILIARES ---
def mostrar_render_inteligente(nombre_base):
    """Busca y muestra un render probando extensiones .png, .jpg, .jpeg"""
    possible_files = [f"{nombre_base}.png", f"{nombre_base}.jpg", f"{nombre_base}.jpeg"]
    image_found = False
    for file_path in possible_files:
        if os.path.exists(file_path):
            st.image(file_path, use_container_width=True)
            image_found = True
            break 
    if not image_found:
        st.info(f"ℹ️ Render no disponible. Se buscó: {', '.join(possible_files)}")

# --- ESTILOS CSS (Optimizados) ---
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
dimension_seleccionada = 0

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
    dim = st.sidebar.select_slider("Diámetro del Tanque:", [1, 2, 4, 8, 10, 12], value=8) # Valor por defecto 8m
    datos = core.generar_presupuesto("estanque", dim)
    dimension_seleccionada = dim

elif categoria == "⛺ Bóvedas":
    st.sidebar.markdown("---")
    st.sidebar.warning("🚀 Rápido: Estructura de Ferrocemento Ultra-resistente.")
    # Usamos radio para seleccionar el modelo de bóveda (3m o 6m)
    largo = st.sidebar.radio("Selecciona el Modelo:", [3, 6], format_func=lambda x: f"Modelo {x} Metros (Profundidad)")
    datos = core.generar_presupuesto("boveda", largo)
    dimension_seleccionada = largo

# --- VISUALIZACIÓN PRINCIPAL ---
if datos:
    # Título y Descripción General
    st.markdown(f'<p class="big-font">{datos["nombre"]}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-font">{datos["descripcion"]}</p>', unsafe_allow_html=True)

    # --- MÉTRICAS CON TIEMPOS DE ENTREGA ---
    c1, c2, c3 = st.columns(3)
    
    # 1. Definir tiempos estimados (Ajusta estos valores a tu realidad)
    tiempo_entrega = "Consultar"
    if categoria == "🏠 Casas Modulares": tiempo_entrega = "30 - 45 Días"
    elif categoria == "🐟 Estanques": tiempo_entrega = "10 - 15 Días"
    elif categoria == "⛺ Bóvedas": tiempo_entrega = "15 - 20 Días" # Ajustado para bóvedas de ferrocemento

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
    tab1, tab2, tab3 = st.tabs(["👁️ Galería y Diseño", "💰 Inversión", "🛒 Materiales"])

    # 1. PESTAÑA DISEÑO (Renders + Planos + Textos)
    with tab1:
        col_text, col_visual = st.columns([1, 1.5])
        
        with col_text:
            # --- TEXTOS DESCRIPTIVOS SEGÚN CATEGORÍA Y MODELO ---
            if categoria == "🏠 Casas Modulares":
                if modelo == 1: 
                    st.markdown(f"### 🌟 Concepto Loft | <span class='highlight'>{datos['area']} m²</span>", unsafe_allow_html=True)
                    st.write("Diseñado para maximizar la vista. La cama King Size 'flota' en el centro, mirando al paisaje, mientras que el baño y vestier quedan ocultos tras un muro cabecero funcional.")
                elif modelo == 2: 
                    st.markdown(f"### 🏡 Concepto Familiar | <span class='highlight'>{datos['area']} m²</span>", unsafe_allow_html=True)
                    st.write("Privacidad ante todo. Un pasillo central separa acústicamente la zona social (ruido) de las habitaciones (descanso). Ideal para lotes estrechos y largos.")
                elif modelo == 3: 
                    st.markdown(f"### 🏰 Concepto Hacienda | <span class='highlight'>{datos['area']} m²</span>", unsafe_allow_html=True)
                    st.write("Majestuosidad rural. Un gran salón central de techo alto conecta dos alas independientes: una privada para los dueños y otra para huéspedes o hijos.")
            
            elif categoria == "⛺ Bóvedas":
                if dimension_seleccionada == 3:
                    st.markdown(f"### 🥥 Modelo Cápsula (3m) | <span class='highlight'>{datos['area']} m²</span>", unsafe_allow_html=True)
                    st.write("El refugio perfecto para parejas. Compacto, íntimo y diseñado para que la cama sea el balcón hacia la naturaleza. Ferrocemento liso para una estética orgánica y moderna.")
                elif dimension_seleccionada == 6:
                    st.markdown(f"### 🛌 Modelo Suite (6m) | <span class='highlight'>{datos['area']} m²</span>", unsafe_allow_html=True)
                    st.write("Experiencia Glamping de lujo. Su profundidad permite una pequeña sala de estar al ingreso y un baño privado al fondo, separados de la zona de descanso. Confort total.")

            elif categoria == "🐟 Estanques":
                st.markdown(f"### 🐟 Tanque Productivo | Diámetro: <span class='highlight'>{dimension_seleccionada} m</span>", unsafe_allow_html=True)
                st.write("Tecnología de Ferrocemento para máxima durabilidad e higiene. Superficies lisas que evitan hongos y facilitan la limpieza. Resistencia estructural superior con paredes delgadas de alta densidad.")

        # --- SECCIÓN VISUAL (DERECHA) ---
        with col_visual:
            st.caption("👁️ Visualización 3D")
            
            # A. LÓGICA DE RENDERS
            if categoria == "🏠 Casas Modulares":
                mostrar_render_inteligente(f"render_modelo{modelo_seleccionado}")
            elif categoria == "⛺ Bóvedas":
                mostrar_render_inteligente(f"render_boveda{dimension_seleccionada}")
            elif categoria == "🐟 Estanques":
                # Para estanques usamos una imagen genérica ilustrativa
                mostrar_render_inteligente("render_estanque")
            
            st.markdown("---")

            # B. PLANO TÉCNICO / ESQUEMA (Siempre visible)
            if categoria in ["🏠 Casas Modulares", "⛺ Bóvedas"]:
                st.caption(f"📐 Plano de Distribución ({datos['area']} m²)")
                # Nota: core_planos.dibujar_planta() debe manejar 'vivienda' y 'boveda' internamente si se desea
                # Por ahora, asumimos que dibuja algo genérico o que ya lo actualizaste.
                # Si no, mostrará el plano cuadrado por defecto, que es aceptable como esquema.
                svg_plano = core_planos.dibujar_planta(1) # Usamos un ID genérico por ahora para no romperlo
                st.markdown(svg_plano, unsafe_allow_html=True)
            elif categoria == "🐟 Estanques":
                 st.caption("📐 Esquema Estructural (Planta Circular)")
                 # Aquí podrías poner un SVG de un círculo simple si quisieras en el futuro
                 st.info("Planta circular optimizada para la presión hidrostática.")

    # 2. PESTAÑA FINANCIERA (Común para todos)
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
             st.markdown(f'<div class="card"><h3 style="text-align:center; color:#154360">Precio Llave en Mano</h3><div class="price-tag">${datos["precio_venta"]:,.0f}</div></div>', unsafe_allow_html=True)
        with col2:
             st.markdown("#### 📊 Estructura de Costos")
             st.write(f"**Costo Directo (Material + MO):** ${datos['costo_directo']:,.0f}")
             margen_pct = (datos['precio_venta'] - datos['costo_directo']) / datos['precio_venta'] if datos['precio_venta'] > 0 else 0
             st.progress(margen_pct, text=f"Margen Bruto Estimado: {int(margen_pct*100)}%")
             st.caption("Nota: El margen cubre imprevistos, gestión y utilidad.")

    # 3. PESTAÑA COMPRAS (Común para todos, se adapta según los datos)
    with tab3:
        lc = datos['lista_compras']
        st.write("### 📋 Listado Maestro de Insumos")
        c_a, c_b = st.columns(2)
        with c_a:
            st.markdown('<p class="highlight">🧱 Obra Gris & Estructura</p>', unsafe_allow_html=True)
            st.checkbox(f"{lc['cemento']} Bultos Cemento", value=True)
            if lc.get('cal', 0) > 0: st.checkbox(f"{lc['cal']} Bultos Cal Hidratada", value=True)
            st.checkbox(f"{lc['arena']} m³ Arena", value=True)
            if lc.get('triturado', 0) > 0: st.checkbox(f"{lc['triturado']} m³ Triturado", value=True)
            if lc.get('malla', 0) > 0: st.checkbox(f"{lc['malla']} Unidades Malla/Refuerzo", value=True)
        with c_b:
            st.markdown('<p class="highlight">🦴 Refuerzos & Acabados</p>', unsafe_allow_html=True)
            if lc.get('tubos', 0) > 0: st.checkbox(f"{lc['tubos']} Tubos Estructurales", value=True)
            if lc.get('varillas', 0) > 0: st.checkbox(f"{lc['varillas']} Varillas", value=True)
            if lc.get('alambron', 0) > 0: st.checkbox(f"{lc['alambron']} Kg Alambrón", value=True)
            
            # Kits específicos según categoría
            if categoria == "🏠 Casas Modulares":
                 st.checkbox(f"Kit Techo Nelta ({int(datos['area'])}m² cubiertos)", value=True)
                 st.checkbox("Paquete Carpintería y Vidrios", value=True)
            elif categoria == "⛺ Bóvedas":
                 st.checkbox("Kit Impermeabilizante Acrílico", value=True)
                 st.checkbox("Fachada Frontal (Vidrio/Madera)", value=True)
            elif categoria == "🐟 Estanques":
                 st.checkbox("Kit Hidráulico (Entrada/Salida PVC)", value=True)
                 st.checkbox("Aditivo Impermeabilizante Integral", value=True)