import streamlit as st
import streamlit.components.v1 as components # Importante para dibujar el plano
import core_calculo as core
import core_planos # Tu archivo de dibujo

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Ferrotek | Catálogo Digital", page_icon="🏡", layout="centered")

# --- ESTILOS CSS ---
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

# --- ENCABEZADO ---
st.image("https://via.placeholder.com/800x200.png?text=FERROTEK+Ingenieria+Rural", use_container_width=True)

# --- MENÚ LATERAL ---
st.sidebar.header("🛠️ Configurador de Proyectos")
categoria = st.sidebar.radio("¿Qué deseas construir?", 
    ["🏠 Casas Modulares", "🐟 Estanques Piscícolas", "⛺ Bóvedas Glamping"])

datos = None
modelo_seleccionado = 0 

# --- LÓGICA DE SELECCIÓN ---
if categoria == "🏠 Casas Modulares":
    st.sidebar.markdown("---")
    st.sidebar.info("✨ **Llave en Mano:**\nIncluye Redes, Baños, Cocina, Vidrios y Pisos en Microcemento.")
    modelo = st.sidebar.selectbox("Selecciona tu Modelo:", [1, 2, 3], 
        format_func=lambda x: f"Modelo {x} ({['Suite 35m²', 'Cotidiana 65m²', 'Patriarca 110m²'][x-1]})")
    datos = core.generar_presupuesto("vivienda", modelo)
    modelo_seleccionado = modelo

elif categoria == "🐟 Estanques":
    st.sidebar.markdown("---")
    st.sidebar.success("💧 **Garantía Total:**\nMezcla Impermeable con Cal Hidrófuga + Malla Doble.")
    dim = st.sidebar.select_slider("Diámetro del Tanque:", [1, 2, 4, 8, 10, 12], value=4)
    datos = core.generar_presupuesto("estanque", dim)

elif categoria == "⛺ Bóvedas":
    st.sidebar.markdown("---")
    st.sidebar.warning("🚀 **Sistema Rápido:**\nEstructura Telescópica (Murete + Arco).")
    largo = st.sidebar.radio("Profundidad:", [3, 6], format_func=lambda x: f"{x} Metros (Frente 3.80m)")
    datos = core.generar_presupuesto("boveda", largo)

# --- VISUALIZACIÓN DE RESULTADOS ---
if datos:
    # Título y Descripción
    st.markdown(f'<p class="big-font">{datos["nombre"]}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-font">{datos["descripcion"]}</p>', unsafe_allow_html=True)

    # Métricas Superiores
    c1, c2, c3 = st.columns(3)
    if categoria == "🐟 Estanques":
        c1.metric("💧 Capacidad", f"{datos['volumen_litros']:,} L")
        c2.metric("📏 Altura Muro", "1.20 m")
    else:
        c1.metric("📏 Área Total", f"{datos['area']} m²")
        c2.metric("🏠 Altura", f"{datos['altura']} m")
    c3.metric("🔨 Tiempo Est.", "Entrega Rápida")
    
    st.markdown("---")

    # --- PESTAÑAS PRINCIPALES ---
    tab_diseno, tab_financiero, tab_compras = st.tabs(["📐 Distribución", "💰 Inversión", "🛒 Materiales"])

    # 1. PESTAÑA DISEÑO
    with tab_diseno:
        if categoria == "🏠 Casas Modulares":
            col_text, col_plan = st.columns([1, 1.5])
            
            with col_text:
                if modelo == 1:
                    st.markdown("""
                    ### 🌟 "El Refugio Inteligente"
                    **Ideal para Glamping o Solteros.**
                    * **Fachada:** Techo a un agua (5.70m).
                    * **Loft:** Sin muros internos que corten la luz.
                    * **Baño Oculto:** Detrás del cabecero para máxima estética.
                    """)
                elif modelo == 2:
                    st.markdown("""
                    ### 🏡 "La Casa Funcional"
                    **Ideal Familia Pequeña.**
                    * **Clima:** 5m de ancho = Ventilación total.
                    * **Privacidad:** Habitaciones separadas de la sala.
                    * **Acabados:** Piso microcemento industrial.
                    """)
                elif modelo == 3:
                    st.markdown("""
                    ### 🏰 "La Hacienda Moderna"
                    **Vivienda Definitiva.**
                    * **Volumen:** Techo catedral a dos aguas.
                    * **Social:** Sala-Comedor de 40m².
                    * **Master:** Suite privada en ala independiente.
                    """)
            
            with col_plan:
                # --- DIBUJO DEL PLANO (SVG) ---
                # Usamos components.html para asegurar que se dibuje bien
                svg_plano = core_planos.dibujar_planta(modelo_seleccionado)
                components.html(svg_plano, height=550, scrolling=True)
                
        elif categoria == "🐟 Estanques":
             st.markdown("""
             ### 🌊 Tecnología: Ferrocemento vs. Plástico
             * **Temperatura:** El cemento aísla, el plástico calienta. Agua fresca = Peces sanos.
             * **Durabilidad:** Piedra eterna vs. Plástico que se cristaliza en 5 años.
             * **Sanidad:** Cal Hidrófuga evita hongos.
             """)
             st.info("💡 El diseño circular auto-soporta la presión del agua, reduciendo la necesidad de hierro costoso.")

        elif categoria == "⛺ Bóvedas":
             st.markdown("""
             ### ⛺ "Glamping Indestructible"
             * **Altura:** 2.80m en el centro (Muretes de 90cm).
             * **Resistencia:** No se rasga como la lona, no suena con la lluvia.
             * **Rápido:** Montaje de estructura en 48 horas.
             """)

    # 2. PESTAÑA FINANCIERA
    with tab_financiero:
        col_fin1, col_fin2 = st.columns(2)
        with col_fin1:
            st.markdown(f"""
            <div class="card">
                <h3 style="color:#2C3E50; text-align:center;">Precio de Venta</h3>
                <div class="price-tag">${datos['precio_venta']:,.0f}</div>
                <p style="text-align:center; color:#7F8C8D; margin-top:10px;">Todo incluido (Llave en Mano)</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_fin2:
            st.markdown("#### 📊 Desglose de Costos")
            st.write(f"**Materiales y Equipos:** ${datos['costo_directo']*0.75:,.0f}")
            st.write(f"**Mano de Obra Exp.:** ${datos['costo_directo']*0.25:,.0f}")
            st.info("💡 Precio asume terreno plano y acceso vehicular.")

    # 3. PESTAÑA COMPRAS
    with tab_compras:
        lc = datos['lista_compras']
        st.markdown("#### 📋 Listado Maestro de Insumos")
        c_a, c_b = st.columns(2)
        
        # Columna A: Obra Negra
        with c_a:
            st.markdown('<div class="check-list">', unsafe_allow_html=True)
            st.markdown('<p class="highlight">🧱 Obra Gris</p>', unsafe_allow_html=True)
            st.checkbox(f"{lc['cemento']} Bultos Cemento (50kg)", value=True)
            if lc['cal'] > 0: st.checkbox(f"{lc['cal']} Bultos Cal Hidratada (10kg)", value=True)
            st.checkbox(f"{lc['arena']} m³ Arena de Río", value=True)
            if lc['triturado'] > 0: st.checkbox(f"{lc['triturado']} m³ Triturado", value=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="check-list">', unsafe_allow_html=True)
            st.markdown('<p class="highlight">🦴 Estructura Metálica</p>', unsafe_allow_html=True)
            if lc['tubos'] > 0: st.checkbox(f"{lc['tubos']} Tubos Estructurales", value=True)
            if lc['varillas'] > 0: st.checkbox(f"{lc['varillas']} Varillas Corrugadas", value=True)
            if lc['alambron'] > 0: st.checkbox(f"{lc['alambron']} Kg Alambrón (4.2mm)", value=True)
            st.checkbox(f"{lc['malla']} Paneles Malla Electrosoldada", value=True)
            st.checkbox(f"{lc['zaranda']} Rollos Malla Gallinero", value=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Columna B: Acabados y Techo (COMPLETA)
        with c_b:
            if lc.get('techo'):
                st.markdown('<div class="check-list">', unsafe_allow_html=True)
                st.markdown('<p class="highlight">☂️ Cubierta Nelta</p>', unsafe_allow_html=True)
                st.checkbox(f"{lc['techo']['tejas']} Tejas (5.70m)", value=True)
                st.checkbox(f"{lc['techo']['caballetes']} Caballetes", value=True)
                st.checkbox(f"{lc['techo']['perfiles']} Perfiles C", value=True)
                st.markdown('</div>', unsafe_allow_html=True)

            if lc.get('carpinteria') or lc.get('hidro'):
                st.markdown('<div class="check-list">', unsafe_allow_html=True)
                st.markdown('<p class="highlight">🚪 Acabados & Dotación</p>', unsafe_allow_html=True)
                
                carp = lc.get('carpinteria', {})
                if carp.get('p_ext'): st.checkbox(f"{carp['p_ext']} Puertas Seguridad", value=True)
                if carp.get('p_int'): st.checkbox(f"{carp['p_int']} Puertas Interior", value=True)
                if carp.get('vent'): st.checkbox(f"{carp['vent']} Ventanas Aluminio", value=True)
                
                hidro = lc.get('hidro', {})
                if hidro.get('baños'): st.checkbox(f"{hidro['baños']} Kits Baño Completos", value=True)
                if hidro.get('cocina'): st.checkbox("1 Kit Cocina", value=True)
                
                if lc['elec']: st.checkbox(f"{lc['elec']} Puntos Eléctricos", value=True)
                if lc['area_piso']: st.checkbox(f"{lc['area_piso']} m² Microcemento", value=True)
                st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption("© 2026 Ferrotek | Ingeniería Rural & Ferrocemento Avanzado")