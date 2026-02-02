import streamlit as st
import os
import math
import json
import urllib.parse

st.set_page_config(page_title="Ferrotek Master Portfolio", page_icon="🏗️", layout="wide")

# ==========================================
# 💾 PERSISTENCIA Y PRECIOS
# ==========================================
ARCHIVO_DB = 'ferrotek_db.json'
DB_INICIAL = {
    "config": {"margen_utilidad": 0.30, "admin_pass": "ferrotek2026"},
    "precios": {
        'acero_estructural_kg': 7200, 'acero_comercial_kg': 5500,
        'cemento': 28500, 'arena': 95000, 'triturado': 115000,
        'malla_electro': 215000, 'malla_zaranda': 285000,
        'valor_jornal_dia': 110000, 'kit_starlink': 2200000
    }
}

def cargar_db():
    if not os.path.exists(ARCHIVO_DB):
        with open(ARCHIVO_DB, 'w') as f: json.dump(DB_INICIAL, f)
        return DB_INICIAL
    with open(ARCHIVO_DB, 'r') as f: return json.load(f)

if 'db' not in st.session_state: st.session_state['db'] = cargar_db()

# ==========================================
# 🧠 DICCIONARIO MAESTRO DE PORTAFOLIO
# ==========================================
PORTAFOLIO = {
    "Vivienda 1 Alcoba (30m²)": {"area": 30, "perim": 22, "jornales": 50, "tipo": "Vivienda"},
    "Vivienda 2 Alcobas (54m²)": {"area": 54, "perim": 30, "jornales": 90, "tipo": "Vivienda"},
    "Vivienda 3 Alcobas (84m²)": {"area": 84, "perim": 38, "jornales": 140, "tipo": "Vivienda"},
    "Vivienda Interés Social (72m²)": {"area": 72, "perim": 36, "jornales": 120, "tipo": "Vivienda"},
    "Máster Unibody (100m²)": {"area": 100, "perim": 40, "jornales": 160, "tipo": "Vivienda"},
    "Bóveda / Domo Geodésico": {"area": 25, "perim": 18, "jornales": 40, "tipo": "Especial"},
    "Estanque Piscícola (20m³)": {"area": 32, "perim": 16, "jornales": 25, "tipo": "Estanque"},
    "Muro Perimetral (metro lineal)": {"area": 2.5, "perim": 1, "jornales": 2, "tipo": "Muro"}
}

def calcular_portafolio(item, db, ext):
    p = db['precios']
    m = PORTAFOLIO[item]
    
    # Lógica de materiales optimizada
    p_acero = p['acero_estructural_kg'] if ext.get('piso2') else p['acero_comercial_kg']
    cant_c = math.ceil((m['perim']/0.50)/2) + 4
    vol_mort = (m['area']*0.08) + (m['perim']*2.4*0.05)
    cem = int(vol_mort * 8.5)
    
    # Costos
    c_mat = (cant_c * 9 * p_acero) + (cem * p['cemento']) + (vol_mort * p['arena'])
    if ext.get('wifi'): c_mat += p['kit_starlink']
    c_mo = m['jornales'] * p['valor_jornal_dia']
    
    precio_venta = (c_mat + c_mo) / (1 - db['config']['margen_utilidad'])
    return {"precio": round(precio_venta, -3), "mat_detalle": [cant_c, cem, round(vol_mort,1)], "c_base": c_mat+c_mo}

# ==========================================
# 🎨 INTERFAZ UNIFICADA
# ==========================================
st.sidebar.title("🛠️ FERROTEK.GUANES.BIZ")
categoria = st.sidebar.radio("Filtrar Portafolio:", ["Todo", "Vivienda", "Especial", "Estanque", "Muro"])

lista_items = [k for k, v in PORTAFOLIO.items() if categoria == "Todo" or v['tipo'] == categoria]
item_sel = st.sidebar.selectbox("Seleccione Solución:", lista_items)

with st.sidebar:
    st.write("---")
    p2 = st.checkbox("Incluir Refuerzo 2do Piso") if "Vivienda" in item_sel else False
    sat = st.checkbox("Conectividad Starlink") if "Vivienda" in item_sel else False

calc = calcular_portafolio(item_sel, st.session_state['db'], {'piso2': p2, 'wifi': sat})

t1, t2, t3 = st.tabs(["📊 Cotización", "📐 Ficha Unibody", "🔑 Admin Privado"])

with t1:
    st.header(item_sel)
    st.metric("INVERSIÓN FINAL", f"${calc['precio']:,.0f}")
    st.write("### ✅ Especificaciones Técnicas:")
    if "Vivienda" in item_sel:
        st.write("- Piel de Roca de 5cm (Gana hasta 6% de área útil).")
        st.write("- Estructura Monocasco Sismo-Resistente.")
    elif "Estanque" in item_sel:
        st.write("- Diseño Hidráulico de alta presión.")
        st.write("- Recubrimiento de grado alimenticio.")
    
    msg = f"Hola Manuel! Me interesa {item_sel} por ${calc['precio']:,.0f}"
    st.markdown(f'<a href="https://wa.me/573012428215?text={urllib.parse.quote(msg)}" target="_blank"><button style="width:100%; background-color:#1E3A8A; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold; cursor:pointer;">SOLICITAR FICHA TÉCNICA</button></a>', unsafe_allow_html=True)

with t2:
    st.subheader("Concepto de Ingeniería Monocasco")
    
    st.write("Nuestro sistema elimina la necesidad de columnas pesadas, permitiendo que la pared misma soporte la carga de forma distribuida.")

with t3:
    psw = st.text_input("Password Master:", type="password")
    if psw == st.session_state['db']['config']['admin_pass']:
        st.write(f"Costo de Operación: ${calc['c_base']:,.0f}")
        st.write(f"Desglose: Perfiles: {calc['mat_detalle'][0]} | Bultos: {calc['mat_detalle'][1]}")
        nuevos_p = st.data_editor(st.session_state['db']['precios'])
        if st.button("Guardar Cambios"):
            st.session_state['db']['precios'] = nuevos_p
            with open(ARCHIVO_DB, 'w') as f: json.dump(st.session_state['db'], f)
            st.rerun()