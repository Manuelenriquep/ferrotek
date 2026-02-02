import streamlit as st
import os
import math
import json
import urllib.parse

st.set_page_config(page_title="Ferrotek | Anclaje Integral", page_icon="🏗️", layout="wide")

# ==========================================
# 💾 DB - INSUMOS V51
# ==========================================
ARCHIVO_DB = 'ferrotek_db.json'
def cargar_db():
    if not os.path.exists(ARCHIVO_DB):
        return {"config": {"margen_utilidad": 0.30, "admin_pass": "ferrotek2026"},
                "precios": {
                    'perfil_2_pulg_mt': 12500,
                    'malla_electrosoldada_5mm_m2': 28000, # Viene de 2.35m alto
                    'malla_zaranda_m2': 8500,
                    'cemento': 29500, 'arena': 98000, 'cal_hidratada': 18000,
                    'valor_jornal_dia': 125000,
                    'concreto_ciclopeo_m3': 380000 # Para los dados y zapata corrida
                }}
    with open(ARCHIVO_DB, 'r') as f: return json.load(f)

if 'db' not in st.session_state: st.session_state['db'] = cargar_db()

# ==========================================
# 🧠 CÁLCULO DE CIMENTACIÓN INTEGRAL
# ==========================================
def calcular_muro_raiz(ml, h_vista, db):
    p = db['precios']
    h_total_malla = 2.35
    h_enterrada = h_total_malla - h_vista # Tus 15 cm de "zapata"
    
    # 1. Estructura Postes (Cada 1.50m)
    cant_postes = math.ceil(ml / 1.5) + 1
    mts_perfil = cant_postes * (h_vista + 0.6) # 60cm de empotramiento para el poste
    c_acero = mts_perfil * p['perfil_2_pulg_mt']
    
    # 2. Malla Sándwich (Usando el alto total de 2.35m)
    area_malla = ml * h_total_malla
    c_mallas = (area_malla * p['malla_electrosoldada_5mm_m2']) + \
               (area_malla * 2 * p['malla_zaranda_m2'])
    
    # 3. Cimentación (Dados para postes + relleno de zapata de 15cm)
    vol_dados = cant_postes * (0.3 * 0.3 * 0.6) # Dados de 30x30x60
    vol_zapata_corrida = ml * 0.2 * 0.2 # Zanja de 20x20 para enterrar los 15cm de malla
    c_cimentacion = (vol_dados + vol_zapata_corrida) * p['concreto_ciclopeo_m3']
    
    # 4. Mortero 1:3:3 (Solo área vista)
    vol_mortero = (ml * h_vista * 0.04) * 1.15
    c_mezcla = (int(vol_mortero * 5) * p['cemento']) + \
               (int(vol_mortero * 5) * p['cal_hidratada']) + \
               (vol_mortero * p['arena'])
    
    # 5. Mano de Obra
    c_mo = (ml * 0.9) * p['valor_jornal_dia'] # Incluye excavación de zanja
    
    costo_dir = c_acero + c_mallas + c_cimentacion + c_mezcla + c_mo
    precio_v = costo_dir / (1 - db['config']['margen_utilidad'])
    
    return {"total": round(precio_v, -3), "metro": round(precio_v/ml, -3), "postes": cant_postes}

# ==========================================
# 🎨 INTERFAZ
# ==========================================
st.title("🛡️ Cerramiento Ferrotek: Sistema Raíz")
st.subheader("Anclaje Monolítico mediante Malla de 5mm")

col_a, col_b = st.columns(2)
with col_a:
    ml_input = st.number_input("Metros de cerramiento:", value=50.0)
with col_b:
    st.write(f"**Altura de Muro:** 2.20 m")
    st.write(f"**Anclaje a Tierra:** 0.15 m (Zapata continua de malla)")

res = calcular_muro_raiz(ml_input, 2.2, st.session_state['db'])

st.divider()
c1, c2, c3 = st.columns(3)
c1.metric("INVERSIÓN TOTAL", f"${res['total']:,.0f}")
c2.metric("VALOR METRO LINEAL", f"${res['metro']:,.0f}")
c3.metric("POSTES DE 2\"", res['postes'])

with st.expander("📐 Detalle de Cimentación"):
    st.write("Nuestro sistema no solo 'se apoya' en el suelo:")
    st.write("1. **Postes Anclados:** Dados de concreto para estabilidad estructural.")
    st.write("2. **Malla Raíz:** Los 15cm excedentes de la malla de 5mm se integran a una zapata continua, evitando filtraciones y socavaciones.")