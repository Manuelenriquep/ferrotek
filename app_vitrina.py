import streamlit as st
import core_calculo as core

st.set_page_config(page_title="Ferrotek | Catálogo Digital", page_icon="🏡", layout="centered")

# CSS Estilos Premium
st.markdown("""
    <style>
    .big-font { font-size:28px !important; color: #154360; font-weight: 800; font-family: 'Helvetica', sans-serif;}
    .sub-font { font-size:18px !important; color: #555; font-style: italic;}
    .price-tag { font-size:42px; color: #27AE60; font-weight: bold; background-color: #eafaf1; padding: 10px; border-radius: 8px; text-align: center;}
    .card { background-color: #ffffff; padding: 25px; border-radius: 15px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 6px solid #2980B9;}
    .check-list { background-color: #f8f9f9; padding: 15px; border-radius: 8px; border: 1px solid #ddd; margin-bottom: 10px; }
    .highlight { color: #E67E22; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# Encabezado
st.image("https://via.placeholder.com/800x200.png?text=FERROTEK+Ingenieria+Rural", use_container_width=True)

# --- MENÚ LATERAL ---
st.sidebar.header("🛠️ Configurador de Proyectos")
categoria = st.sidebar.radio("¿Qué deseas construir?", 
    ["🏠 Casas Modulares", "🐟 Estanques Piscícolas", "⛺ Bóvedas Glamping"])

datos = None

# --- LÓGICA DE CASAS ---
if categoria == "🏠 Casas Modulares":
    st.sidebar.markdown("---")
    st.sidebar.info("✨ **Llave en Mano:**\nIncluye Redes, Baños, Cocina, Vidrios y Pisos en Microcemento.")
    modelo = st.sidebar.selectbox("Selecciona tu Modelo:", [1, 2, 3], 
        format_func=lambda x: f"Modelo {x} ({['Suite 35m²', 'Cotidiana 65m²', 'Patriarca 110m²'][x-1]})")
    datos = core.generar_presupuesto("vivienda", modelo)

# --- LÓGICA DE ESTANQUES ---
elif categoria == "🐟 Estanques":
    st.sidebar.markdown("---")
    st.sidebar.success("💧 **Garantía Total:**\nMezcla Impermeable con Cal Hidrófuga + Malla Doble.")
    dim = st.sidebar.select_slider("Diámetro del Tanque:", [1, 2, 4, 8, 10, 12], value=4)
    datos = core.generar_presupuesto("estanque", dim)

# --- LÓGICA DE BÓVEDAS ---
elif categoria == "⛺ Bóvedas":
    st.sidebar.markdown("---")
    st.sidebar.warning("🚀 **Sistema Rápido:**\nEstructura Telescópica (Murete + Arco).")
    largo = st.sidebar.radio("Profundidad:", [3, 6], format_func=lambda x: f"{x} Metros (Frente 3.80m)")
    datos = core.generar_presupuesto("boveda", largo)

# --- VISUALIZACIÓN DE RESULTADOS ---
if datos:
    # Título del Producto
    st.markdown(f'<p class="big-font">{datos["nombre"]}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-font">{datos["descripcion"]}</p>', unsafe_allow_html=True)

    # Métricas Clave (Top Bar)
    c1, c2, c3 = st.columns(3)
    if categoria == "🐟 Estanques":
        c1.metric("💧 Capacidad", f"{datos['volumen_litros']:,} L")
        c2.metric("📏 Altura Muro", "1.20 m")
        c3.metric("🛡️ Vida Útil", "40+ Años")
    else:
        c1.metric("📏 Área Total", f"{datos['area']} m²")
        c2.metric("🏠 Altura", f"{datos['altura']} m")
        c3.metric("🔨 Tiempo Est.", "4-6 Semanas")

    st.markdown("---")

    # --- PESTAÑAS DE CONTENIDO ---
    tab_diseno, tab_financiero, tab_compras = st.tabs(["📐 Distribución y Diseño", "💰 Inversión", "🛒 Lista de Materiales"])

    # 1. PESTAÑA DE DISEÑO (TEXTOS DE VENTA)
    with tab_diseno:
        if categoria == "🏠 Casas Modulares":
            if modelo == 1: # SUITE 35m2
                st.markdown("""
                ### 🌟 Concepto: "El Refugio Inteligente"
                Diseñado para el **Glamping de Lujo** o la **Vivienda de Soltero**. Este modelo maximiza cada centímetro cúbico.
                
                * **Fachada Moderna:** Techo a un agua con pendiente optimizada para la teja Nelta de 5.70m (Cero desperdicio, Cero goteras).
                * **Planta Libre (Loft):** Sin muros internos innecesarios. La luz cruza de lado a lado.
                * **Baño Spa:** Un baño sorprendentemente amplio (1.50m x 3.00m) que permite acabados de lujo.
                
                **📍 Distribución Sugerida:**
                > Entrada lateral -> Cocina compacta (Kitchenette) -> Zona de Cama King con vista al ventanal de fondo -> Baño privado detrás de la cabecera.
                """)
                st.image("https://via.placeholder.com/600x300.png?text=Planta+Tipo+Loft+35m2", use_container_width=True)

            elif modelo == 2: # COTIDIANA 65m2
                st.markdown("""
                ### 🏡 Concepto: "La Casa Funcional"
                El equilibrio perfecto entre costo y habitabilidad. Ideal para **Familias Pequeñas** o **Renta Rural**.
                
                * **Eficiencia Térmica:** Al tener 5 metros de ancho, logramos ventilación cruzada perfecta. La casa es fresca todo el día.
                * **Privacidad:** El diseño separa las habitaciones de la zona social mediante un pasillo o núcleo húmedo.
                * **Acabados:** El piso en microcemento le da un toque industrial y limpio, fácil de barrer y trapear en el campo.
                
                **📍 Distribución Sugerida:**
                > Sala-Comedor al frente (Amplitud) -> Cocina abierta con barra -> Pasillo central -> Baño social completo -> Dos habitaciones gemelas al fondo (Silencio y descanso).
                """)
                st.image("https://via.placeholder.com/600x300.png?text=Planta+2+Habitaciones+65m2", use_container_width=True)

            elif modelo == 3: # PATRIARCA 110m2
                st.markdown("""
                ### 🏰 Concepto: "La Hacienda Moderna"
                Una vivienda definitiva. Espacios anchos, techos altos y la solidez de una fortaleza.
                
                * **Techo Catedral:** Estructura a dos aguas (10m de ancho) que genera un volumen interior imponente y fresco.
                * **Zona Social Gigante:** Sala y comedor integrados de casi 40m² para reunir a toda la familia.
                * **Master Suite:** Habitación principal con baño privado y espacio para clóset de pared a pared.
                
                **📍 Distribución Sugerida:**
                > Acceso Central -> Gran Salón Social -> Cocina en "L" con Isla -> Ala Derecha: 2 Habitaciones + Baño Auxiliar -> Ala Izquierda: Master Suite Privada.
                """)
                st.image("https://via.placeholder.com/600x300.png?text=Planta+3+Habitaciones+110m2", use_container_width=True)
        
        elif categoria == "🐟 Estanques":
             st.markdown(f"""
             ### 🌊 Tecnología: Ferrocemento vs. Plástico
             Usted no está comprando un tanque, está comprando **Tranquilidad para sus peces**.
             
             1. **Temperatura Estable:** A diferencia de los tanques plásticos azules que se calientan con el sol, el cemento mantiene el agua fresca. **Agua fresca = Más oxígeno = Peces más gordos.**
             2. **Eterno:** El plástico se cristaliza y se rompe a los 5 años. Este tanque es de piedra y acero. Dura para siempre.
             3. **Sanidad:** Nuestro mortero incluye **Cal Hidrófuga**, que evita hongos y facilita el lavado.
             
             **Ideal para:** Tilapia, Trucha, Reserva de Agua de Riego.
             """)

        elif categoria == "⛺ Bóvedas":
             st.markdown("""
             ### ⛺ Concepto: "Glamping Indestructible"
             La forma más eficiente de la naturaleza (el arco) llevada a la construcción.
             
             * **Altura Confort:** Gracias a nuestro sistema de muretes de 90cm, la altura central es de **2.80m**. Nada de agacharse.
             * **Rápido:** Se arma la estructura en 2 días.
             * **Seguro:** A diferencia de una carpa de lona, esto no se rasga, no se lo comen los ratones y aísla el ruido de la lluvia.
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
            st.markdown("#### 📊 Desglose de Costos (Transparencia)")
            st.write(f"**Materiales y Equipos:** ${datos['costo_directo']*0.75:,.0f}")
            st.write(f"**Mano de Obra Exp.:** ${datos['costo_directo']*0.25:,.0f}")
            st.info("💡 Este precio incluye imprevistos y gestión. No incluye viáticos si la obra es fuera del área metropolitana.")

    # 3. PESTAÑA DE COMPRAS (CHECKLIST)
    with tab_compras:
        lc = datos['lista_compras']
        st.markdown("#### 📋 Listado Maestro de Insumos")
        
        c_a, c_b = st.columns(2)
        
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
                if hidro.get('cocina'): st.checkbox("1 Kit Cocina (Poceta+Grifería)", value=True)
                if lc['elec']: st.checkbox(f"{lc['elec']} Puntos Eléctricos", value=True)
                if lc['area_piso']: st.checkbox(f"{lc['area_piso']} m² Microcemento", value=True)
                st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption("© 2026 Ferrotek | Ingeniería Rural & Ferrocemento Avanzado")