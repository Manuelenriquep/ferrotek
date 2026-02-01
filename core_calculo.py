import streamlit as st
import core_planos
import os 
import math

st.set_page_config(page_title="Ferrotek | Catálogo Digital", page_icon="🏡", layout="centered")

# ==========================================
# 🧠 CEREBRO DE CÁLCULO (MÉTODO GUANES: SÁNDWICH)
# ==========================================
PRECIOS = {
    'cemento': 28000,     'arena': 90000,       'triturado': 110000,
    'varilla': 24000,     # Varilla 3/8 o 1/2
    'malla_electro': 180000, # Panel Electrosoldada (4mm o similar)
    'malla_zaranda': 140000, # Rollo de Malla Gallinero/Zaranda (30m lineales aprox)
    'tubo_est': 150000,   
    'alambron': 8000,     'cal': 15000,
    
    # Mano de obra 
    'mo_m2_casa': 450000,    
    'mo_m2_tanque': 70000,   # Precio ajustado
    'mo_m2_boveda': 80000,
    
    'kit_techo_m2': 120000,
    'kit_vidrios_global_peq': 3500000, 'kit_vidrios_global_med': 5000000, 'kit_vidrios_global_gra': 8000000,
    'kit_impermeabilizante': 450000,
    'kit_fachada_boveda': 2500000, 
    'kit_hidraulico_estanque': 300000
}

# Constantes Técnicas
AREA_PANEL_ELECTRO = 13.0  # m2 útiles por panel
AREA_ROLLO_ZARANDA = 40.0  # m2 útiles por rollo (aprox un rollo de 1.50x30m)
BULTOS_POR_M3 = 9        

def calcular_interno(tipo, dimension):
    lista = {}
    costo_extra = 0
    margen = 0.35 

    # --- A. CASAS ---
    if tipo == "vivienda":
        margen = 0.35
        if dimension == 1:
            lista = {'info_nombre': "Modelo 1: Loft (35m²)", 'info_desc': "Ideal para parejas.", 'info_area': 35, 'info_altura': 3.0, 'cemento': 75, 'arena': 5, 'triturado': 3, 'varillas': 18, 'malla_electro': 12, 'malla_zaranda': 0, 'tubos': 6, 'alambron': 10}
            costo_extra = PRECIOS['kit_vidrios_global_peq']
        elif dimension == 2:
            lista = {'info_nombre': "Modelo 2: Familiar (65m²)", 'info_desc': "2 habitaciones.", 'info_area': 65, 'info_altura': 3.2, 'cemento': 130, 'arena': 9, 'triturado': 5, 'varillas': 30, 'malla_electro': 22, 'malla_zaranda': 0, 'tubos': 10, 'alambron': 20}
            costo_extra = PRECIOS['kit_vidrios_global_med']
        elif dimension == 3:
            lista = {'info_nombre': "Modelo 3: Hacienda (110m²)", 'info_desc': "Casa principal.", 'info_area': 110, 'info_altura': 4.5, 'cemento': 210, 'arena': 15, 'triturado': 9, 'varillas': 45, 'malla_electro': 38, 'malla_zaranda': 0, 'tubos': 16, 'alambron': 35}
            costo_extra = PRECIOS['kit_vidrios_global_gra']
        
        costo_extra += (lista['info_area'] * PRECIOS['mo_m2_casa']) + (lista['info_area'] * PRECIOS['kit_techo_m2'])

    # --- B. ESTANQUES (MÉTODO GUANES) ---
    elif tipo == "estanque":
        margen = 0.30
        diametro = dimension
        altura = 1.2
        radio = diametro / 2
        
        # 1. Geometría
        area_piso = math.pi * (radio**2)
        area_muros = (math.pi * diametro) * altura
        area_total = area_piso + area_muros 

        # 2. Concreto (Mortero)
        volumen_mortero = area_total * 0.05 # 5cm espesor
        cemento_est = int(volumen_mortero * BULTOS_POR_M3)
        if cemento_est < 4: cemento_est = 4

        # 3. Mallas (El Sándwich)
        # Una capa central de electrosoldada
        paneles_electro = math.ceil(area_total / AREA_PANEL_ELECTRO)
        # Dos capas de zaranda (interna y externa)
        rollos_zaranda = math.ceil((area_total * 2) / AREA_ROLLO_ZARANDA)

        # 4. Varillas (Los Aros)
        perimetro = math.pi * diametro
        # Distribución: 0cm, 15cm, 40cm, 65cm, 90cm, 115cm (aprox 6 aros en 1.2m)
        num_aros = 6 
        metros_lineales_varilla = perimetro * num_aros
        # Agregamos varillas verticales de soporte (cada 1m)
        num_verticales = int(perimetro) 
        metros_lineales_varilla += (num_verticales * altura)
        
        total_varillas_6m = math.ceil(metros_lineales_varilla / 6)

        lista = {
            'info_nombre': f"Estanque Circular (Ø {diametro}m)", 'info_desc': "Técnica Sándwich: Electrosoldada + Doble Zaranda.",
            'info_area': round(area_piso, 1), 'info_altura': altura, 'info_volumen': int(area_piso * altura * 1000),
            'cemento': cemento_est, 
            'cal': int(cemento_est * 0.2), 
            'arena': round(volumen_mortero * 1.1, 1),
            'malla_electro': paneles_electro,  # 1 Capa
            'malla_zaranda': rollos_zaranda,   # 2 Capas
            'varillas': total_varillas_6m, 
            'alambron': int(cemento_est * 0.5) # Bastante amarre
        }
        costo_extra = (area_total * PRECIOS['mo_m2_tanque']) + PRECIOS['kit_hidraulico_estanque']

    # --- C. BÓVEDAS (Mismo Principio) ---
    elif tipo == "boveda":
        margen = 0.40 
        largo = dimension
        ancho = 3.5
        
        perimetro_transversal = 7.1 
        area_cascara = perimetro_transversal * largo
        area_piso = ancho * largo
        area_culatas = 15 
        area_total_trabajo = area_cascara + area_culatas

        volumen_mortero = area_total_trabajo * 0.035
        cemento_bov = int(volumen_mortero * BULTOS_POR_M3)
        
        # Bóvedas: 1 Electro + 2 Zaranda
        paneles_electro = math.ceil(area_total_trabajo / AREA_PANEL_ELECTRO)
        rollos_zaranda = math.ceil((area_total_trabajo * 2) / AREA_ROLLO_ZARANDA)

        desc = "Cápsula compacta (3.5cm). Sismorresistente." if largo == 3 else "Suite profunda. Estructura liviana."
        
        lista = {
            'info_nombre': f"Bóveda Glamping ({largo}m)", 'info_desc': desc,
            'info_area': round(area_piso, 1), 'info_altura': 2.8,
            'cemento': cemento_bov, 
            'arena': round(volumen_mortero * 1.1, 1),
            'malla_electro': paneles_electro,
            'malla_zaranda': rollos_zaranda,
            'varillas': int(largo * 3), 
            'alambron': int(cemento_bov * 0.3), 
            'tubos': 3
        }
        costo_extra = (area_total_trabajo * PRECIOS['mo_m2_boveda']) + PRECIOS['kit_impermeabilizante'] + PRECIOS['kit_fachada_boveda']

    # CÁLCULO FINAL PRECIO
    costo_materiales = (lista.get('cemento',0)*PRECIOS['cemento']) + (lista.get('arena',0)*PRECIOS['arena']) + \
                       (lista.get('triturado',0)*PRECIOS['triturado']) + (lista.get('varillas',0)*PRECIOS['varilla']) + \
                       (lista.get('malla_electro',0)*PRECIOS['malla_electro']) + \
                       (lista.get('malla_zaranda',0)*PRECIOS['malla_zaranda']) + \
                       (lista.get('tubos',0)*PRECIOS['tubo_est']) + \
                       (lista.get('cal',0)*PRECIOS['cal']) + (lista.get('alambron',0)*PRECIOS['alambron'])
    
    costo_total = costo_materiales + costo_extra
    precio_venta = costo_total / (1 - margen)

    return {
        'nombre': lista['info_nombre'], 'descripcion': lista['info_desc'],
        'area': lista['info_area'], 'altura': lista['info_altura'],
        'volumen_litros': lista.get('info_volumen', 0),
        'lista_compras': lista,
        'costo_directo': round(costo_total, -3),
        'precio_venta': round(precio_venta, -3)
    }

# ==========================================
# 🎨 INTERFAZ GRÁFICA
# ==========================================

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .big-font { font-size:28px !important; color: #154360; font-weight: 800;}
    .sub-font { font-size:18px !important; color: #555; font-style: italic;}
    .price-tag { font-size:42px; color: #27AE60; font-weight: bold; background-color: #eafaf1; padding: 10px; border-radius: 8px; text-align: center;}
    .card { background-color: #ffffff; padding: 25px; border-radius: 15px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 6px solid #2980B9;}
    .highlight { color: #E67E22; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# Banner
st.image("https://via.placeholder.com/800x200.png?text=FERROTEK+Ingenieria+Rural", use_container_width=True)

# --- MENÚ LATERAL ---
st.sidebar.header("🛠️ Configurador de Proyectos")

OPCION_CASAS = "🏠 Casas Modulares"
OPCION_ESTANQUES = "🐟 Estanques Piscícolas"
OPCION_BOVEDAS = "⛺ Bóvedas Glamping"

categoria = st.sidebar.radio("¿Qué deseas construir?", [OPCION_CASAS, OPCION_ESTANQUES, OPCION_BOVEDAS])

datos = None
modelo_seleccionado = 0 
dimension_seleccionada = 0

# --- LÓGICA DE SELECCIÓN ---
if categoria == OPCION_CASAS:
    st.sidebar.markdown("---")
    st.sidebar.info("✨ Llave en Mano: Baños, Cocina, Redes y Vidrios.")
    modelo = st.sidebar.selectbox("Selecciona tu Modelo:", [1, 2, 3], format_func=lambda x: f"Modelo {x}")
    datos = calcular_interno("vivienda", modelo)
    modelo_seleccionado = modelo

elif categoria == OPCION_ESTANQUES:
    st.sidebar.markdown("---")
    st.sidebar.success("💧 Garantía: Cal Hidrófuga + Malla Doble.")
    dim = st.sidebar.select_slider("Diámetro del Tanque:", [1, 2, 4, 8, 10, 12], value=8)
    datos = calcular_interno("estanque", dim)
    dimension_seleccionada = dim

elif categoria == OPCION_BOVEDAS:
    st.sidebar.markdown("---")
    st.sidebar.warning("🚀 Rápido: Estructura Telescópica.")
    largo = st.sidebar.radio("Profundidad:", [3, 6], format_func=lambda x: f"{x} Metros")
    datos = calcular_interno("boveda", largo)
    dimension_seleccionada = largo

# --- VISUALIZACIÓN ---
if datos:
    # Encabezado
    st.markdown(f'<p class="big-font">{datos["nombre"]}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-font">{datos["descripcion"]}</p>', unsafe_allow_html=True)

    # --- TIEMPOS ---
    tiempo_entrega = "Consultar"
    if categoria == OPCION_CASAS:
        if modelo_seleccionado == 1: tiempo_entrega = "30 - 45 Días"
        elif modelo_seleccionado == 2: tiempo_entrega = "45 - 60 Días"
        elif modelo_seleccionado == 3: tiempo_entrega = "75 - 90 Días"
    elif categoria == OPCION_ESTANQUES: tiempo_entrega = "10 - 15 Días"
    elif categoria == OPCION_BOVEDAS: tiempo_entrega = "15 - 20 Días"

    # Métricas
    c1, c2, c3 = st.columns(3)
    if categoria == OPCION_ESTANQUES:
        c1.metric("💧 Capacidad", f"{datos['volumen_litros']:,} L")
        c2.metric("📏 Altura Muro", "1.20 m")
    else:
        c1.metric("📏 Área Total", f"{datos['area']} m²")
        c2.metric("🏠 Altura", f"{datos['altura']} m")
    c3.metric("🗓️ Tiempo Aprox.", tiempo_entrega)
    
    st.markdown("---")

    # Pestañas
    tab1, tab2, tab3 = st.tabs(["👁️ Galería y Diseño", "💰 Inversión", "🛒 Materiales"])

    # 1. DISEÑO
    with tab1:
        col_text, col_visual = st.columns([1, 1.5])
        with col_text:
            if categoria == OPCION_CASAS:
                st.write(f"Diseño optimizado Modelo {modelo_seleccionado}.")
            elif categoria == OPCION_BOVEDAS:
                st.write(f"Bóveda de ferrocemento de {dimension_seleccionada}m. Diseño Sismorresistente.")
            elif categoria == OPCION_ESTANQUES:
                st.write("Tanque circular de alta producción en ferrocemento. Técnica Sándwich de alta durabilidad.")

        with col_visual:
            img_name = ""
            if categoria == OPCION_CASAS: img_name = f"render_modelo{modelo_seleccionado}"
            elif categoria == OPCION_BOVEDAS: img_name = f"render_boveda{dimension_seleccionada}"
            elif categoria == OPCION_ESTANQUES: img_name = "render_estanque"

            possible_files = [f"{img_name}.png", f"{img_name}.jpg", f"{img_name}.jpeg"]
            found = False
            for f in possible_files:
                if os.path.exists(f):
                    st.image(f, use_container_width=True)
                    found = True
                    break
            if not found:
                st.info(f"Falta imagen: {img_name}")

            if categoria != OPCION_ESTANQUES:
                st.caption("📐 Esquema de Distribución")
                try:
                    st.markdown(core_planos.dibujar_planta(1), unsafe_allow_html=True)
                except: pass

    # 2. FINANCIERA
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
             st.markdown(f'<div class="card"><h3 style="text-align:center; color:#154360">Precio Llave en Mano</h3><div class="price-tag">${datos["precio_venta"]:,.0f}</div></div>', unsafe_allow_html=True)
        with col2:
             st.write(f"**Costo Directo:** ${datos['costo_directo']:,.0f}")
             st.progress(0.7, text="Margen Saludable")

    # 3. MATERIALES
    with tab3:
        lc = datos['lista_compras']
        c_a, c_b = st.columns(2)
        with c_a:
            st.checkbox(f"{lc.get('cemento',0)} Bultos Cemento", value=True)
            st.checkbox(f"{lc.get('arena',0)} m³ Arena", value=True)
            if lc.get('triturado',0)>0: st.checkbox(f"{lc.get('triturado',0)} m³ Triturado", value=True)
            if lc.get('malla_electro',0)>0: st.checkbox(f"{lc.get('malla_electro',0)} Paneles Electro", value=True)
        with c_b:
            if lc.get('malla_zaranda',0)>0: st.checkbox(f"{lc.get('malla_zaranda',0)} Rollos Zaranda", value=True)
            if lc.get('tubos',0)>0: st.checkbox(f"{lc.get('tubos',0)} Tubos Est.", value=True)
            if lc.get('varillas',0)>0: st.checkbox(f"{lc.get('varillas',0)} Varillas", value=True)
            if lc.get('cal',0)>0: st.checkbox(f"{lc.get('cal',0)} Bultos Cal", value=True)