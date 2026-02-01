import streamlit as st
import core_planos
import os # Necesario para buscar imágenes
import math

st.set_page_config(page_title="Ferrotek | Catálogo Digital", page_icon="🏡", layout="centered")

# ==========================================
# 🧠 CEREBRO DE CÁLCULO (Integrado)
# ==========================================
PRECIOS = {
    'cemento': 28000,     'arena': 90000,       'triturado': 110000,
    'varilla': 25000,     'malla': 180000,      'tubo_est': 150000,
    'alambron': 8000,     'cal': 15000,
    'mo_m2_casa': 450000, 'kit_techo_m2': 120000,
    'kit_vidrios_global_peq': 3500000, 'kit_vidrios_global_med': 5000000, 'kit_vidrios_global_gra': 8000000,
    'mo_m2_ferro': 350000, 'kit_impermeabilizante': 450000,
    'kit_fachada_boveda': 2500000, 'kit_hidraulico_estanque': 300000
}

def calcular_interno(tipo, dimension):
    lista = {}
    costo_extra = 0
    margen = 0.35 # Por defecto

    # --- A. CASAS ---
    if tipo == "vivienda":
        margen = 0.35
        if dimension == 1:
            lista = {'info_nombre': "Modelo 1: Loft (35m²)", 'info_desc': "Ideal para parejas. Espacio abierto optimizado.", 'info_area': 35, 'info_altura': 3.0, 'cemento': 75, 'arena': 5, 'triturado': 3, 'varillas': 18, 'malla': 12, 'tubos': 6, 'alambron': 10}
            costo_extra = PRECIOS['kit_vidrios_global_peq']
        elif dimension == 2:
            lista = {'info_nombre': "Modelo 2: Familiar (65m²)", 'info_desc': "2 habitaciones y zona social amplia.", 'info_area': 65, 'info_altura': 3.2, 'cemento': 130, 'arena': 9, 'triturado': 5, 'varillas': 30, 'malla': 22, 'tubos': 10, 'alambron': 20}
            costo_extra = PRECIOS['kit_vidrios_global_med']
        elif dimension == 3:
            lista = {'info_nombre': "Modelo 3: Hacienda (110m²)", 'info_desc': "Casa principal. 3 habitaciones, techos altos.", 'info_area': 110, 'info_altura': 4.5, 'cemento': 210, 'arena': 15, 'triturado': 9, 'varillas': 45, 'malla': 38, 'tubos': 16, 'alambron': 35}
            costo_extra = PRECIOS['kit_vidrios_global_gra']
        
        costo_extra += (lista['info_area'] * PRECIOS['mo_m2_casa']) + (lista['info_area'] * PRECIOS['kit_techo_m2'])

    # --- B. ESTANQUES ---
    elif tipo == "estanque":
        margen = 0.30
        diametro = dimension
        altura = 1.2
        area_piso = math.pi * ((diametro/2)**2)
        volumen_m3 = area_piso * altura
        cemento_est = int(volumen_m3 * 1.5)
        if cemento_est < 5: cemento_est = 5 # Mínimo
        
        lista = {
            'info_nombre': f"Estanque Circular (Ø {diametro}m)", 'info_desc': "Ferrocemento de alta resistencia para piscicultura.",
            'info_area': round(area_piso, 1), 'info_altura': altura, 'info_volumen': int(volumen_m3 * 1000),
            'cemento': cemento_est, 'cal': int(cemento_est * 0.2), 'arena': round(cemento_est * 0.06, 1),
            'malla': int(area_piso * 2), 'varillas': int(diametro * 2), 'alambron': int(cemento_est * 0.5)
        }
        # Costo MO aproximado + Kit Hidráulico
        costo_extra = (area_piso * 1.5 * PRECIOS['mo_m2_ferro']) + PRECIOS['kit_hidraulico_estanque']

    # --- C. BÓVEDAS ---
    elif tipo == "boveda":
        margen = 0.45
        largo = dimension
        ancho = 3.5
        area = largo * ancho
        desc = "Cápsula compacta para parejas." if largo == 3 else "Suite profunda con espacio para sala."
        
        lista = {
            'info_nombre': f"Bóveda Glamping ({largo}m)", 'info_desc': desc,
            'info_area': area, 'info_altura': 2.8,
            'cemento': int(area * 3.5), 'arena': round(area * 0.2, 1),
            'malla': int(area * 2.5), 'varillas': int(largo * 4), 'alambron': 5, 'tubos': 2
        }
        costo_extra = (area * PRECIOS['mo_m2_ferro']) + PRECIOS['kit_impermeabilizante'] + PRECIOS['kit_fachada_boveda']

    # CÁLCULO FINAL PRECIO
    costo_materiales = (lista.get('cemento',0)*PRECIOS['cemento']) + (lista.get('arena',0)*PRECIOS['arena']) + \
                       (lista.get('triturado',0)*PRECIOS['triturado']) + (lista.get('varillas',0)*PRECIOS['varilla']) + \
                       (lista.get('malla',0)*PRECIOS['malla']) + (lista.get('tubos',0)*PRECIOS['tubo_est']) + \
                       (lista.get('cal',0)*PRECIOS['cal'])
    
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
# 🎨 INTERFAZ GRÁFICA (FRONTEND)
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
categoria = st.sidebar.radio("¿Qué deseas construir?", ["🏠 Casas Modulares", "🐟 Estanques Piscícolas", "⛺ Bóvedas Glamping"])

datos = None
modelo_seleccionado = 0 
dimension_seleccionada = 0

# SELECCIÓN
if categoria == "🏠 Casas Modulares":
    st.sidebar.markdown("---")
    st.sidebar.info("✨ Llave en Mano: Baños, Cocina, Redes y Vidrios.")
    modelo = st.sidebar.selectbox("Selecciona tu Modelo:", [1, 2, 3], format_func=lambda x: f"Modelo {x}")
    datos = calcular_interno("vivienda", modelo)
    modelo_seleccionado = modelo

elif categoria == "🐟 Estanques":
    st.sidebar.markdown("---")
    st.sidebar.success("💧 Garantía: Cal Hidrófuga + Malla Doble.")
    dim = st.sidebar.select_slider("Diámetro del Tanque:", [1, 2, 4, 8, 10, 12], value=8)
    datos = calcular_interno("estanque", dim)
    dimension_seleccionada = dim

elif categoria == "⛺ Bóvedas":
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

    # Métricas
    c1, c2, c3 = st.columns(3)
    tiempo_entrega = "Consultar"
    if categoria == "🏠 Casas Modulares": tiempo_entrega = "30 - 45 Días"
    elif categoria == "🐟 Estanques": tiempo_entrega = "10 - 15 Días"
    elif categoria == "⛺ Bóvedas": tiempo_entrega = "15 - 20 Días"

    if categoria == "🐟 Estanques":
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
            if categoria == "🏠 Casas Modulares":
                if modelo == 1: st.write("Diseño Loft abierto para parejas.")
                elif modelo == 2: st.write("Diseño familiar con separación de ambientes.")
                elif modelo == 3: st.write("Gran casa tipo Hacienda con techos altos.")
            elif categoria == "⛺ Bóvedas":
                st.write(f"Bóveda de ferrocemento de {dimension_seleccionada}m de profundidad. Ideal para Glamping.")
            elif categoria == "🐟 Estanques":
                st.write("Tanque circular de alta producción en ferrocemento.")

        with col_visual:
            # Búsqueda de IMAGEN INTELIGENTE (PNG/JPG)
            img_name = ""
            if categoria == "🏠 Casas Modulares": img_name = f"render_modelo{modelo_seleccionado}"
            elif categoria == "⛺ Bóvedas": img_name = f"render_boveda{dimension_seleccionada}"
            elif categoria == "🐟 Estanques": img_name = "render_estanque"

            possible_files = [f"{img_name}.png", f"{img_name}.jpg", f"{img_name}.jpeg"]
            found = False
            for f in possible_files:
                if os.path.exists(f):
                    st.image(f, use_container_width=True)
                    found = True
                    break
            if not found:
                st.info(f"Falta imagen: {img_name} (.png/.jpg)")

            # PLANO (Solo casas y bóvedas)
            if categoria != "🐟 Estanques":
                st.caption("📐 Esquema de Distribución")
                svg_plano = core_planos.dibujar_planta(1) # Genérico para evitar errores
                st.markdown(svg_plano, unsafe_allow_html=True)

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
            if lc.get('malla',0)>0: st.checkbox(f"{lc.get('malla',0)} Unid. Malla", value=True)
        with c_b:
            if lc.get('tubos',0)>0: st.checkbox(f"{lc.get('tubos',0)} Tubos Est.", value=True)
            if lc.get('varillas',0)>0: st.checkbox(f"{lc.get('varillas',0)} Varillas", value=True)
            if lc.get('cal',0)>0: st.checkbox(f"{lc.get('cal',0)} Bultos Cal", value=True)