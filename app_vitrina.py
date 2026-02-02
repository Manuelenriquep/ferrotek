import streamlit as st
import os
import math
import json
import urllib.parse

st.set_page_config(page_title="Ferrotek Smart | Consolidado 2026", page_icon="🏗️", layout="wide")

# ==========================================
# 💾 GESTIÓN DE DATOS (Conservando todo)
# ==========================================
ARCHIVO_DB = 'ferrotek_db.json'

DB_INICIAL = {
    "config": {"margen_utilidad": 0.30},
    "precios": {
        'acero_estructural_kg': 7200, 'acero_comercial_kg': 5500,
        'cemento': 28000, 'arena': 95000, 'triturado': 115000,
        'malla_electro': 210000, 'malla_zaranda': 285000,
        'pintura_asfaltica': 48000, 'esmalte_negro': 72000,
        'vinilo_madera_m2': 58000, 'mo_m2_casa': 240000,
        'kit_starlink': 2500000, 'anclaje_epoxico_und': 85000
    }
}

def cargar_db():
    if not os.path.exists(ARCHIVO_DB):
        with open(ARCHIVO_DB, 'w') as f: json.dump(DB_INICIAL, f)
        return DB_INICIAL
    with open(ARCHIVO_DB, 'r') as f: return json.load(f)

if 'db' not in st.session_state: st.session_state['db'] = cargar_db()

# ==========================================
# 🧠 LÓGICA DE CÁLCULO INTEGRAL
# ==========================================
def calcular_materiales(tipo, id_modelo, db, extra_param=None):
    p = db['precios']
    margen = db.get('config', {}).get('margen_utilidad', 0.30)
    
    # Base de datos de Modelos (Sin quitar ninguno)
    modelos = {
        "loft_35": {"nombre": "Loft 35m²", "area": 35, "perim": 24, "dias": 25},
        "familiar_65": {"nombre": "Familiar 65m²", "area": 65, "perim": 36, "dias": 35},
        "smart_612": {"nombre": "Modelo 6x12 Smart (72m²)", "area": 72, "perim": 36, "dias": 45},
        "eco_40": {"nombre": "Eco-Hogar 40m²", "area": 40, "perim": 26, "dias": 28}
    }
    
    mod = modelos.get(id_modelo)
    es_2piso = extra_param.get('2piso', False) if extra_param else False
    es_starlink = extra_param.get('starlink', False) if extra_param else False
    
    peso_perfil = 13 if es_2piso else 9 
    precio_kg = p['acero_estructural_kg'] if es_2piso else p['acero_comercial_kg']
    
    num_parales = math.ceil(mod['perim'] / 0.50)
    total_C = math.ceil(num_parales / 2) + math.ceil(mod['perim']/6)
    if es_2piso: total_C = int(total_C * 1.9)

    vol_mortero = (mod['area'] * 0.08) + (mod['perim'] * 2.4 * 0.05)
    
    costo_mat = (total_C * peso_perfil * precio_kg) + (int(vol_mortero * 8.5) * p['cemento']) + (vol_mortero * p['arena'])
    if es_starlink: costo_mat += p['kit_starlink']
    if es_2piso: costo_mat += (p['anclaje_epoxico_und'] * 12)

    costo_mo = mod['area'] * p['mo_m2_casa']
    if es_2piso: costo_mo *= 1.4

    precio_v = (costo_mat + costo_mo) / (1 - margen)
    
    return {
        "nombre": mod['nombre'], "area": mod['area'], "dias": mod['dias'],
        "precio": round(precio_v, -3), "materiales": {"Perfiles C": total_C, "Cemento": int(vol_mortero * 8.5)}
    }

# ==========================================
# 🎨 INTERFAZ ACTUALIZADA
# ==========================================
st.sidebar.title("🛠️ FERROTEK V29.0")
with st.sidebar:
    sel = st.selectbox("Elige tu modelo:", ["Loft 35m²", "Eco-Hogar 40m²", "Familiar 65m²", "Modelo 6x12 Smart (72m²)"])
    id_map = {"Loft 35m²": "loft_35", "Eco-Hogar 40m²": "eco_40", "Familiar 65m²": "familiar_65", "Modelo 6x12 Smart (72m²)": "smart_612"}
    
    piso2 = st.checkbox("Proyectar 2do Piso (Estructural)")
    wifi = st.checkbox("Incluir Starlink")
    res = calcular_materiales("vivienda", id_map[sel], st.session_state['db'], {'2piso': piso2, 'starlink': wifi})

tabs = st.tabs(["🏡 Modelos y Cotización", "📄 Ficha Técnica Superior", "📐 Esquema 6x12", "👷 Manual Maestro"])

with tabs[0]:
    c1, c2 = st.columns(2)
    with c1:
        st.header(res['nombre'])
        st.metric("Inversión Estimada", f"${res['precio']:,.0f}")
        st.write(f"⏱️ Tiempo estimado: {res['dias']} días.")
    with c2:
        st.write("📈 **Capacidades del Modelo:**")
        st.json(res['materiales'])
        link_wa = f"https://wa.me/573012428215?text=Cotice%20{res['nombre']}"
        st.markdown(f'<a href="{link_wa}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold; cursor:pointer;">RESERVAR CITA TÉCNICA</button></a>', unsafe_allow_html=True)

with tabs[1]:
    st.markdown("## 📑 FICHA TÉCNICA: Sistema Híbrido Ferrotek")
    st.write("**Superior al ladrillo y al drywall por:**")
    st.write("1. **Espesor:** Gana hasta 2m² libres por habitación.")
    st.write("2. **Solidez:** Paredes de ferrocemento que se sienten como piedra, no como plástico.")
    st.write("3. **Sismo-Resistencia:** Esqueleto de acero estructural galvanizado.")

with tabs[2]:
    st.header("📐 Esquema de Solución Lote 6x12")
    st.info("Diseño optimizado para normativa de Interés Social en Colombia.")
    st.code("""
    FRENTE: 6.00m | FONDO: 12.00m
    --------------------------------------
    | [ Patio ] (2.0m) | [ Alcoba 2 ]    |
    |------------------|-----------------|
    | [ Baño ]         | [ Alcoba 1 ]    |
    |------------------|-----------------|
    | [ Cocina/Ropas ] | [ Salón/Smart ] |
    --------------------------------------
    | [ Acceso/Jardín ] (1.5m)          |
    --------------------------------------
    * Muros de 5cm: El pasillo gana 14cm de ancho real vs ladrillo.
    """)

with tabs[3]:
    st.video("https://www.youtube.com/watch?v=FjS68XzVp-0")