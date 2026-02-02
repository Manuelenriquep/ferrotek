import streamlit as st
import os
import math
import json
import urllib.parse

# Configuración de página
st.set_page_config(page_title="Ferrotek Master | Gestión Privada", page_icon="🏗️", layout="wide")

# ==========================================
# 💾 BASE DE DATOS INTEGRAL
# ==========================================
ARCHIVO_DB = 'ferrotek_db.json'

DB_INICIAL = {
    "config": {"margen_utilidad": 0.30, "admin_pass": "ferrotek2026"},
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
    with open(ARCHIVO_DB, 'r') as f:
        data = json.load(f)
        # Sincronizar precios nuevos si la DB es antigua
        for k, v in DB_INICIAL["precios"].items():
            if k not in data["precios"]: data["precios"][k] = v
        if "config" not in data: data["config"] = DB_INICIAL["config"]
        return data

def guardar_db(nueva_db):
    with open(ARCHIVO_DB, 'w') as f: json.dump(nueva_db, f)

if 'db' not in st.session_state: st.session_state['db'] = cargar_db()

# ==========================================
# 🧠 MOTOR DE CÁLCULO V32 (Protegido)
# ==========================================
def calcular_presupuesto(categoria, subcat, db, extras):
    p = db['precios']
    margen = db['config']['margen_utilidad']
    lista_mat = {}; costo_mat = 0; costo_mo = 0; dias = 0
    
    if categoria == "Vivienda":
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
        if es_2p: cant_c = int(cant_c * 1.8)
        
        vol = (m['area']*0.08) + (m['perim']*2.4*0.05)
        cem = int(vol * 8.5)
        
        lista_mat = {"Bultos Cemento": cem, "Arena (m³)": round(vol*1.1,1), "Perfiles C": cant_c, "Mallas": math.ceil(m['area']/12)+2}
        costo_mat = (cant_c * peso * pr_kg) + (cem * p['cemento']) + (vol * p['arena'])
        if extras.get('wifi'): costo_mat += p['kit_starlink']
        if es_2p: costo_mat += (p['anclaje_epoxico_und'] * 12)
        costo_mo = m['area'] * p['mo_m2_casa'] * (1.3 if es_2p else 1.0)
        dias = m['dias']

    elif categoria == "Estanques":
        vol = extras.get('volumen', 10)
        area_f = vol * 1.6
        cem = int(area_f * 0.5)
        lista_mat = {"Cemento": cem, "Arena (m³)": round(area_f*0.05,1), "Malla Zaranda (m)": int(area_f*2.5)}
        costo_mat = (cem * p['cemento']) + (area_f * 0.05 * p['arena'])
        costo_mo = area_f * p['mo_m2_tanque']
        dias = 10

    total = (costo_mat + costo_mo) / (1 - margen)
    return {"precio": round(total, -3), "lista": lista_mat, "dias": dias}

# ==========================================
# 🎨 INTERFAZ PROFESIONAL
# ==========================================
st.sidebar.title("🏗️ FERROTEK V32.0")
cat = st.sidebar.selectbox("Línea de Negocio:", ["Vivienda", "Estanques"])

with st.sidebar:
    if cat == "Vivienda":
        sub = st.selectbox("Modelo:", ["6x12 Smart (72m²)", "Loft 35m²", "Eco-Hogar 40m²", "Familiar 65m²", "Domo/Bóveda 25m²"])
        p2 = st.checkbox("2do Piso (Estructural)")
        stk = st.checkbox("Incluir Starlink")
        params = {'piso2': p2, 'wifi': stk}
    else:
        sub = "Estanque Ferrocemento"
        v_est = st.slider("Volumen (m³):", 5, 200, 20)
        params = {'volumen': v_est}

datos = calcular_presupuesto(cat, sub, st.session_state['db'], params)

# TABS
tabs = st.tabs(["📊 Cotización Pública", "📑 Ficha Técnica", "⚙️ Administración Privada"])

with tabs[0]:
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader(f"{cat}: {sub}")
        st.table(datos['lista'])
    with c2:
        st.metric("PRECIO ESTIMADO", f"${datos['precio']:,.0f}")
        if params.get('wifi'): st.info("🛰️ Starlink Residencial incluido ($150k/mes).")
        wa_msg = f"Hola Manuel! Me interesa el {sub} por ${datos['precio']:,.0f}"
        st.markdown(f'<a href="https://wa.me/573012428215?text={urllib.parse.quote(wa_msg)}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold; cursor:pointer;">RESERVAR CITA TÉCNICA</button></a>', unsafe_allow_html=True)

with tabs[1]:
    st.markdown("### 🧬 ADN Tecnológico Ferrotek")
    st.write("- **Steel Framing:** Estructura galvanizada sismo-resistente.")
    st.write("- **Ferrocemento:** Piel de piedra de alta densidad (6cm de espesor).")
    

with tabs[2]:
    st.subheader("🔑 Acceso Restringido")
    password = st.text_input("Ingrese la clave maestra:", type="password")
    if password == st.session_state['db']['config']['admin_pass']:
        st.success("Acceso Concedido")
        # Editor de precios
        st.write("### 🛠️ Editor de Precios Unitarios")
        nuevos_precios = st.data_editor(st.session_state['db']['precios'])
        # Editor de margen
        nuevo_margen = st.slider("Margen de Utilidad:", 0.1, 0.5, st.session_state['db']['config']['margen_utilidad'])
        
        if st.button("💾 Guardar Cambios en Servidor"):
            st.session_state['db']['precios'] = nuevos_precios
            st.session_state['db']['config']['margen_utilidad'] = nuevo_margen
            guardar_db(st.session_state['db'])
            st.rerun()
    elif password != "":
        st.error("Clave incorrecta")