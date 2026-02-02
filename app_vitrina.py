import streamlit as st
import os
import math
import json
import urllib.parse

st.set_page_config(page_title="Ferrotek Master | Catálogo Integral", page_icon="🏗️", layout="wide")

# ==========================================
# 💾 BASE DE DATOS INTEGRAL (No se borra nada)
# ==========================================
ARCHIVO_DB = 'ferrotek_db.json'

DB_INICIAL = {
    "config": {"margen_utilidad": 0.30},
    "precios": {
        'acero_estructural_kg': 7200, 'acero_comercial_kg': 5500,
        'cemento': 28500, 'arena': 95000, 'triturado': 115000,
        'malla_electro': 215000, 'malla_zaranda': 285000,
        'pintura_asfaltica': 48000, 'esmalte_negro': 75000,
        'vinilo_madera_m2': 58000, 'mo_m2_casa': 245000,
        'mo_m2_tanque': 85000, 'mo_m2_muro': 48000,
        'kit_starlink': 2200000, 'anclaje_epoxico_und': 85000
    }
}

def cargar_db():
    if not os.path.exists(ARCHIVO_DB):
        with open(ARCHIVO_DB, 'w') as f: json.dump(DB_INICIAL, f)
        return DB_INICIAL
    with open(ARCHIVO_DB, 'r') as f: return json.load(f)

if 'db' not in st.session_state: st.session_state['db'] = cargar_db()

# ==========================================
# 🧠 MOTOR DE CÁLCULO MULTI-SERVICIO
# ==========================================
def calcular_todo(categoria, subcat, db, extras):
    p = db['precios']
    margen = db.get('config', {}).get('margen_utilidad', 0.30)
    lista = {}; costo_mo = 0; info = ""; costo_adicional = 0

    if categoria == "Vivienda":
        # MODELOS DE CASA (TODOS)
        models = {
            "6x12 Smart (72m²)": {"area": 72, "perim": 36, "dias": 45},
            "Loft 35m²": {"area": 35, "perim": 24, "dias": 22},
            "Eco-Hogar 40m²": {"area": 40, "perim": 26, "dias": 28},
            "Familiar 65m²": {"area": 65, "perim": 34, "dias": 35},
            "Domo/Bóveda 25m²": {"area": 25, "perim": 18, "dias": 15}
        }
        m = models[subcat]
        es_2p = extras.get('piso2', False)
        
        peso = 13 if es_2p else 9
        pr_kg = p['acero_estructural_kg'] if es_2p else p['acero_comercial_kg']
        
        cant_c = math.ceil((m['perim']/0.50)/2) + 6
        if es_2p: cant_c = int(cant_c * 1.8); costo_adicional += p['anclaje_epoxico_und']*8
        
        vol = (m['area']*0.08) + (m['perim']*2.4*0.05)
        cem = int(vol * 8.5)
        
        lista = {"Cemento (Bultos)": cem, "Arena (m³)": round(vol*1.1,1), "Perfiles PHR C": cant_c, "Mallas": math.ceil(m['area']/12)}
        costo_mo = m['area'] * p['mo_m2_casa'] * (1.3 if es_2p else 1.0)
        costo_mat = (cant_c * peso * pr_kg) + (cem * p['cemento']) + costo_adicional
        
        if extras.get('wifi'): costo_mat += p['kit_starlink']

    elif categoria == "Estanques / Piscícola":
        # Recuperamos la lógica de estanques
        vol_m3 = extras.get('volumen', 10)
        area_ferro = vol_m3 * 1.5 # Factor aproximado
        cem = int(area_ferro * 0.4)
        lista = {"Cemento": cem, "Malla Zaranda (m)": int(area_ferro*2), "Impermeabilizante": 2}
        costo_mo = area_ferro * p['mo_m2_tanque']
        costo_mat = cem * p['cemento']
        info = f"Estanque de {vol_m3}m³ optimizado para Tilapia/Cachama."

    total = (costo_mat + costo_mo) / (1 - margen)
    return {"precio": round(total, -3), "lista": lista, "info": info}

# ==========================================
# 🎨 INTERFAZ MAESTRA
# ==========================================
st.sidebar.title("🛠️ FERROTEK V30.0")
menu = st.sidebar.selectbox("Categoría de Servicio:", ["Vivienda", "Estanques / Piscícola", "Bóvedas y Domes", "Muros de Cerramiento"])

with st.sidebar:
    if menu == "Vivienda":
        sub = st.selectbox("Modelo:", ["6x12 Smart (72m²)", "Loft 35m²", "Eco-Hogar 40m²", "Familiar 65m²", "Domo/Bóveda 25m²"])
        p2 = st.checkbox("Estructura 2do Piso (Steel Framing)")
        sat = st.checkbox("Internet Starlink (Opcional)")
        ext = {'piso2': p2, 'wifi': sat}
    else:
        sub = "General"
        vol = st.slider("Volumen/Área:", 5, 200, 20)
        ext = {'volumen': vol}

res = calcular_todo(menu, sub, st.session_state['db'], ext)

# VISUALIZACIÓN
t1, t2, t3, t4 = st.tabs(["📊 Cotización", "📄 Ficha Técnica", "📐 Plano 6x12", "👷 Manual"])

with t1:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.header(f"{menu}: {sub}")
        if menu == "Vivienda" and sub == "6x12 Smart (72m²)":
            st.info("🎯 **Especial Lotes VIS:** El modelo más vendido en Colombia. Aprovecha cada cm del lote.")
        
        st.subheader("📋 Materiales Principales")
        st.table(res['lista'])
    
    with col2:
        st.metric("PRECIO LLAVE EN MANO", f"${res['precio']:,.0f}")
        if ext.get('wifi'):
            st.warning("🛰️ **Tip de Inversión:** Suscripción Residencial $150.000/mes. Si compartes con 5 vecinos a $30k cada uno, ¡tu internet es GRATIS!")
        
        msg = f"Hola Manuel! 👋 Quiero cotizar {menu} {sub} por ${res['precio']:,.0f}"
        st.markdown(f'<a href="https://wa.me/573012428215?text={urllib.parse.quote(msg)}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold; cursor:pointer;">SOLICITAR VISITA TÉCNICA</button></a>', unsafe_allow_html=True)

with t2:
    st.markdown("### 📑 Ventaja Ferrotek Híbrido")
    st.write("- **Más Espacio:** Muros de 6cm vs 15cm de ladrillo. Ganas un baño extra en área libre.")
    st.write("- **Más Fuerza:** Acero estructural G50 sismo-resistente.")
    st.write("- **Mejor Acabado:** Paredes sólidas que no suenan a hueco.")

with t3:
    if "6x12" in sub:
        st.markdown("### 📐 Distribución Lote 6x12 (Sugerida)")
        st.code("""
        FONDO: 12.00m  <------------------------------>
        ________________________________________________
        | PATIO (2m) | ALCOBA 2 (3.5m) | ALCOBA 1 (3.5m)|
        |------------|-----------------|----------------|
        | BAÑO (1.5) | COCINA/ROPAS    | SALA-COMEDOR   |
        ------------------------------------------------
        FRENTE: 6.00m | [ ACCESO Y JARDÍN FRONTAL ]
        """)
        

with t4:
    st.video("https://www.youtube.com/watch?v=FjS68XzVp-0")