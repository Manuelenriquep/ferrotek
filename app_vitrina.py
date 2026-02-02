import streamlit as st
import os
import math
import json
import urllib.parse

st.set_page_config(page_title="Ferrotek Smart | Concreción 2026", page_icon="🏗️", layout="wide")

# ==========================================
# 💾 GESTIÓN DE DATOS Y CONFIGURACIÓN
# ==========================================
ARCHIVO_DB = 'ferrotek_db.json'

DB_INICIAL = {
    "config": {"margen_utilidad": 0.30},
    "precios": {
        'acero_estructural_kg': 7200,  # Acero pesado Cal 14-16 para carga
        'acero_comercial_kg': 5500,    # Perfiles delgados para cerramiento
        'cemento': 28000, 'arena': 95000, 'triturado': 115000,
        'malla_electro': 210000, 'malla_zaranda': 285000,
        'pintura_asfaltica': 48000, 'esmalte_negro': 72000,
        'vinilo_madera_m2': 58000, 'pegante_boxer': 62000,
        'mo_m2_casa': 240000, 'mo_m2_muro': 48000,
        'kit_starlink': 2500000,
        'kit_techo_m2': 115000, 'kit_vidrios_med': 4800000,
        'anclaje_epoxico_und': 85000
    },
    "receta_mezcla": {"muro_cemento_arena": 3.0, "muro_cal_factor": 0.5}
}

def cargar_db():
    if not os.path.exists(ARCHIVO_DB):
        with open(ARCHIVO_DB, 'w') as f: json.dump(DB_INICIAL, f)
        return DB_INICIAL
    with open(ARCHIVO_DB, 'r') as f:
        data = json.load(f)
        # Asegurar que los nuevos campos existan si la DB es vieja
        for k, v in DB_INICIAL["precios"].items():
            if k not in data["precios"]: data["precios"][k] = v
        return data

def guardar_db(nueva_db):
    with open(ARCHIVO_DB, 'w') as f: json.dump(nueva_db, f)

if 'db' not in st.session_state: st.session_state['db'] = cargar_db()

# ==========================================
# 🧠 CEREBRO DE CÁLCULO ESTRUCTURAL V28.0
# ==========================================
def calcular_materiales(tipo, dimension, db, extra_param=None):
    p = db['precios']
    margen = db.get('config', {}).get('margen_utilidad', 0.30)
    
    lista_cantidades = {}; costo_mo_total = 0; costo_otros = 0; info = {}
    
    # Extraer parámetros de configuración
    es_cabaña = extra_param.get('estilo') == "Cabaña (Madera)" if extra_param else False
    es_2piso = extra_param.get('2piso', False) if extra_param else False
    es_starlink = extra_param.get('starlink', False) if extra_param else False

    if tipo == "vivienda":
        if dimension == "6x12":
            nombre = "Modelo 6x12 Smart"; area_piso = 72; perimetro_muros = 36; dias_obra = 45
        elif dimension == 1:
            nombre = "Loft 35m2"; area_piso = 35; perimetro_muros = 24; dias_obra = 25
        else:
            nombre = "Familiar 65m2"; area_piso = 65; perimetro_muros = 36; dias_obra = 35

        # Lógica de Acero: Diferenciación de Calibres
        # Un perfil PHR C de 6m pesa aprox 8kg en cal comercial y 12kg+ en estructural
        peso_perfil = 13 if es_2piso else 9 
        precio_kg = p['acero_estructural_kg'] if es_2piso else p['acero_comercial_kg']
        costo_unidad_perfil = peso_perfil * precio_kg

        num_parales = math.ceil(perimetro_muros / 0.50)
        total_C = math.ceil(num_parales / 2) + math.ceil(perimetro_muros/6)
        
        if es_2piso:
            total_C = int(total_C * 1.9) # Refuerzo Inline Framing
            costo_otros += p['anclaje_epoxico_und'] * 12 # Pernos de anclaje
            nombre += " (Estructura Reforzada 2P)"
        
        if es_starlink:
            costo_otros += p['kit_starlink']
            nombre += " + Starlink Ready"

        vol_mortero = (area_piso * 0.08) + (perimetro_muros * 2.4 * 0.05)
        cem = int(vol_mortero * 8.5)

        lista_cantidades = {
            'Cemento Gris (Bultos)': cem,
            'Arena de Río (m³)': round(vol_mortero * 1.1, 1),
            'Acero PHR C (Unidades)': total_C,
            'Malla Electrosoldada': math.ceil((area_piso + (perimetro_muros * 2.4))/13),
            'Vinilo Madera (m²)': math.ceil(total_C * 0.7) if es_cabaña else 0
        }
        
        costo_materiales = (total_C * costo_unidad_perfil) + (cem * p['cemento']) + \
                          (vol_mortero * p['arena']) + (costo_otros)
        
        costo_mo_total = area_piso * p['mo_m2_casa']
        if es_2piso: costo_mo_total *= 1.4 # Mayor complejidad técnica

        info = {
            'info_nombre': nombre,
            'info_desc': "Sistema Steel Framing + Piel de Ferrocemento.",
            'costo_total': costo_materiales + costo_mo_total,
            'precio_venta': (costo_materiales + costo_mo_total) / (1 - margen),
            'lista_visible': lista_cantidades,
            'dias': dias_obra
        }
    
    return info

# ==========================================
# 🎨 INTERFAZ GRÁFICA STREAMLIT
# ==========================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/4336/4336825.png", width=100)
st.sidebar.title("Configurador Ferrotek")

with st.sidebar:
    modelo = st.selectbox("Modelo de Vivienda:", ["6x12 Smart (72m2)", "Loft 35m2", "Familiar 65m2"])
    estilo = st.radio("Acabado Estructural:", ["Industrial (Negro)", "Cabaña (Madera)"])
    st.markdown("---")
    piso2 = st.checkbox("Estructura para 2do Piso (Steel Framing Cal 14-16)")
    wifi = st.checkbox("Internet Starlink Satelital")
    
    dim_key = {"6x12 Smart (72m2)": "6x12", "Loft 35m2": 1, "Familiar 65m2": 2}
    datos = calcular_materiales("vivienda", dim_key[modelo], st.session_state['db'], 
                               extra_param={'2piso': piso2, 'starlink': wifi, 'estilo': estilo})

tabs = st.tabs(["👁️ Cotización Comercial", "👷‍♂️ Manual para el Maestro", "⚙️ Configuración Admin"])

# TAB 1: COMERCIAL
with tabs[0]:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.header(datos['info_nombre'])
        st.write(datos['info_desc'])
        if piso2: st.success("🛡️ **CALIDAD ESTRUCTURAL:** Perfiles de alta resistencia para multinivel.")
        if wifi: st.info("🛰️ **CONECTIVIDAD:** Incluye soporte y kit Starlink de alta velocidad.")
        st.write("---")
        st.write("📋 **Resumen de Materiales Principales:**")
        st.table(datos['lista_visible'])

    with col2:
        st.metric("PRECIO TOTAL ESTIMADO", f"${datos['precio_venta']:,.0f}")
        st.caption(f"Tiempo de ejecución: {datos['dias']} días aprox.")
        
        # WhatsApp Link
        msg = f"Hola Manuel! 👋 Coticé el {datos['info_nombre']}. Precio: ${datos['precio_venta']:,.0f}. Quiero iniciar el proyecto."
        link_wa = f"https://wa.me/573012428215?text={urllib.parse.quote(msg)}"
        st.markdown(f'<a href="{link_wa}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:20px; border-radius:10px; font-weight:bold; font-size:18px; cursor:pointer;">🚀 ENVIAR A MI WHATSAPP</button></a>', unsafe_allow_html=True)

# TAB 2: MANUAL TÉCNICO (Para el Maestro)
with tabs[1]:
    st.header("📚 Guía Técnica Steel Framing & Ferrocemento")
    
    st.subheader("1. La Zapata (Fundación)")
    st.write("Para 2 pisos: Zapatas aisladas de 60x60x60cm unidas por viga de amarre. El acero PHR debe ir anclado con pernos epóxicos de 1/2\".")
    

    st.subheader("2. Estructura (Steel Framing)")
    st.write("Uso obligatorio de tornillería punta broca #8x1/2 (para unión de perfiles) y #10x3/4 (para anclaje). Los parales deben estar alineados verticalmente entre pisos (Inline Framing).")
    

    st.subheader("3. Capacitación en Video")
    st.video("https://www.youtube.com/watch?v=FjS68XzVp-0")
    st.caption("Tutorial recomendado para el equipo de obra.")

# TAB 3: CONFIGURACIÓN
with tabs[2]:
    st.subheader("⚙️ Precios de Referencia (Solo Admin)")
    if st.text_input("Contraseña Admin", type="password") == "ferrotek2026":
        new_prices = st.data_editor(st.session_state['db']['precios'])
        if st.button("💾 Actualizar Precios Globales"):
            st.session_state['db']['precios'] = new_prices
            guardar_db(st.session_state['db'])
            st.success("Precios actualizados.")