import streamlit as st
import os
import math
import json
import urllib.parse

st.set_page_config(page_title="Ferrotek Master Catalog", page_icon="🏗️", layout="wide")

# ==========================================
# 💾 PERSISTENCIA DE DATOS
# ==========================================
ARCHIVO_DB = 'ferrotek_db.json'
DB_INICIAL = {
    "config": {"margen_utilidad": 0.30, "admin_pass": "ferrotek2026"},
    "precios": {
        'acero_estructural_kg': 7200, 'acero_comercial_kg': 5500,
        'cemento': 28500, 'arena': 95000, 'triturado': 115000,
        'malla_electro': 215000, 'malla_zaranda': 285000,
        'valor_jornal_dia': 110000,
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
# 🧠 DICCIONARIO DE INGENIERÍA Y ESQUEMAS
# ==========================================
CATALOGO = {
    "Máster Unibody (100m²)": {
        "area": 100, "perim": 40, "jornales": 160, "dias": 60,
        "esquema": """
        LOTE 10x10m
        __________________________________________
        | ALCOBA 3 |  PATIO  | ALCOBA PRINCIPAL  |
        | (3x3.5)  | (2x3.5) | (4x3.5 + Baño)    |
        |__________|_________|___________________|
        | ALCOBA 2 |   BAÑO  |   ZONA SOCIAL     |
        | (3x3.5)  | SOCIAL  |   TIPO LOFT       |
        |__________|_________|   (SALA-COMEDOR)  |
        |   COCINA EN ISLA   |      (6x6.5)      |
        |____________________|___________________|
        """
    },
    "6x12 Smart (72m²)": {
        "area": 72, "perim": 36, "jornales": 120, "dias": 45,
        "esquema": """
        LOTE 6x12m
        __________________________
        | PATIO (2m) | ALCOBA 2  |
        |------------|-----------|
        | BAÑO       | ALCOBA 1  |
        |------------|-----------|
        | COCINA     | SALÓN     |
        | ROPAS      | COMEDOR   |
        |------------|-----------|
        | ACCESO / JARDÍN (1.5m) |
        --------------------------
        """
    },
    "Familiar 65m²": {
        "area": 65, "perim": 34, "jornales": 110, "dias": 35,
        "esquema": "Distribución optimizada para 2 alcobas y zona social abierta."
    }
}

def calcular_sistema(cat, sub, db, ext):
    p = db['precios']
    m = CATALOGO.get(sub, {"area": 35, "perim": 24, "jornales": 60, "dias": 22})
    
    # Materiales
    peso = 13 if ext.get('piso2') else 9
    pr_kg = p['acero_estructural_kg'] if ext.get('piso2') else p['acero_comercial_kg']
    cant_c = math.ceil((m['perim']/0.50)/2) + 6
    vol_mort = (m['area']*0.08) + (m['perim']*2.4*0.05)
    cem = int(vol_mort * 8.5)
    
    # Costos
    c_mat = (cant_c * peso * pr_kg) + (cem * p['cemento']) + (vol_mort * 1.1 * p['arena'])
    if ext.get('wifi'): c_mat += p['kit_starlink']
    c_mo = m['jornales'] * p['valor_jornal_dia'] * (1.4 if ext.get('piso2') else 1.0)
    
    precio_v = (c_mat + c_mo) / (1 - db['config']['margen_utilidad'])
    return {"precio": round(precio_v, -3), "esquema": m.get('esquema', ""), "dias": m['dias'], "c_base": c_mat+c_mo}

# ==========================================
# 🎨 INTERFAZ
# ==========================================
st.sidebar.title("🏗️ FERROTEK UNIFIED")
sel = st.sidebar.selectbox("Modelo Unibody:", list(CATALOGO.keys()))
p2 = st.sidebar.checkbox("Proyección Multinivel")
sat = st.sidebar.checkbox("Nodo Starlink")

res = calcular_sistema("Vivienda", sel, st.session_state['db'], {'piso2': p2, 'wifi': sat})

tab_v, tab_e, tab_a = st.tabs(["🚀 Propuesta", "📐 Esquema Técnico", "🔑 Admin"])

with tab_v:
    st.header(sel)
    st.metric("INVERSIÓN ESTIMADA", f"${res['precio']:,.0f}")
    st.write("---")
    st.write("✅ **Incluye:** Piel de Roca de 5cm, Estructura Stress-Skin, Instalaciones básicas.")
    wa = f"https://wa.me/573012428215?text=Interes%20en%20{sel}"
    st.markdown(f'<a href="{wa}" target="_blank"><button style="width:100%; background-color:#1E3A8A; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold; cursor:pointer;">VALIDACIÓN TÉCNICA</button></a>', unsafe_allow_html=True)

with tab_e:
    st.subheader("Planta de Distribución Sugerida")
    st.code(res['esquema'])
    st.info("💡 Recuerda: Al usar Piel de Roca de 5cm, ganas espacio real frente al ladrillo tradicional.")

with tab_a:
    psw = st.text_input("Password:", type="password")
    if psw == st.session_state['db']['config']['admin_pass']:
        st.write(f"Costo Base: ${res['c_base']:,.0f}")
        nuevos_p = st.data_editor(st.session_state['db']['precios'])
        if st.button("Guardar Precios"):
            st.session_state['db']['precios'] = nuevos_p
            with open(ARCHIVO_DB, 'w') as f: json.dump(st.session_state['db'], f)
            st.rerun()