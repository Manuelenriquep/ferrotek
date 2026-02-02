import streamlit as st
import os
import math
import json
import urllib.parse

# Configuración de página
st.set_page_config(page_title="Ferrotek Master | Admin Panel", page_icon="🏗️", layout="wide")

# ==========================================
# 💾 GESTIÓN DE DATOS (ADMIN CENTRAL)
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
        for k, v in DB_INICIAL["precios"].items():
            if k not in data["precios"]: data["precios"][k] = v
        if "config" not in data: data["config"] = DB_INICIAL["config"]
        return data

def guardar_db(nueva_db):
    with open(ARCHIVO_DB, 'w') as f: json.dump(nueva_db, f)

if 'db' not in st.session_state: st.session_state['db'] = cargar_db()

# ==========================================
# 🧠 CÁLCULOS TÉCNICOS Y DE COSTOS
# ==========================================
def realizar_calculos(cat, sub, db, ext):
    p = db['precios']
    margen = db['config']['margen_utilidad']
    
    # Valores por defecto
    res = {"mat_detalle": {}, "costo_total_mat": 0, "costo_mo": 0, "dias": 0}
    
    if cat == "Vivienda":
        models = {
            "6x12 Smart (72m²)": {"a": 72, "p": 36, "d": 45},
            "Loft 35m²": {"a": 35, "p": 24, "d": 22},
            "Eco-Hogar 40m²": {"a": 40, "p": 26, "d": 28},
            "Familiar 65m²": {"a": 65, "p": 34, "d": 35},
            "Domo/Bóveda 25m²": {"a": 25, "p": 18, "d": 15}
        }
        m = models[sub]
        es_2p = ext.get('piso2', False)
        
        peso = 13 if es_2p else 9
        precio_kg = p['acero_estructural_kg'] if es_2p else p['acero_comercial_kg']
        
        cant_c = math.ceil((m['p']/0.50)/2) + 6
        if es_2p: cant_c = int(cant_c * 1.8)
        
        vol_mort = (m['a']*0.08) + (m['p']*2.4*0.05)
        cem = int(vol_mort * 8.5)
        
        # Detalle para el Administrador (Precios de costo)
        res["mat_detalle"] = {
            "Perfiles PHR C": [cant_c, f"${cant_c * peso * precio_kg:,.0f}"],
            "Bultos Cemento": [cem, f"${cem * p['cemento']:,.0f}"],
            "Arena (m³)": [round(vol_mort*1.1,1), f"${vol_mort*1.1*p['arena']:,.0f}"],
            "Mallas": [math.ceil(m['a']/12)+2, f"${(math.ceil(m['a']/12)+2)*p['malla_electro']:,.0f}"]
        }
        
        res["costo_total_mat"] = (cant_c * peso * precio_kg) + (cem * p['cemento']) + (vol_mort * 1.1 * p['arena'])
        if ext.get('wifi'): res["costo_total_mat"] += p['kit_starlink']
        if es_2p: res["costo_total_mat"] += (p['anclaje_epoxico_und'] * 12)
        
        res["costo_mo"] = m['a'] * p['mo_m2_casa'] * (1.3 if es_2p else 1.0)
        res["dias"] = m['d}

    # (Lógica simplificada para otros modelos para ahorrar espacio en el prompt)
    res["precio_venta"] = (res["costo_total_mat"] + res["costo_mo"]) / (1 - margen)
    return res

# ==========================================
# 🎨 INTERFAZ (ORGANIZACIÓN POR TABS)
# ==========================================
st.sidebar.title("🏗️ FERROTEK V33.0")
cat_sel = st.sidebar.selectbox("Categoría:", ["Vivienda", "Estanques"])

with st.sidebar:
    if cat_sel == "Vivienda":
        sub_sel = st.selectbox("Modelo:", ["6x12 Smart (72m²)", "Loft 35m²", "Eco-Hogar 40m²", "Familiar 65m²", "Domo/Bóveda 25m²"])
        p2 = st.checkbox("Incluir 2do Piso")
        stk = st.checkbox("Kit Starlink")
        par = {'piso2': p2, 'wifi': stk}
    else:
        sub_sel = "Estanque"
        v = st.slider("Volumen m³", 5, 100, 20)
        par = {'volumen': v}

calc = realizar_calculos(cat_sel, sub_sel, st.session_state['db'], par)

# TABS PRINCIPALES
tab_comercial, tab_ficha, tab_admin = st.tabs(["📊 Cotización Cliente", "📑 Ficha Técnica", "⚙️ ZONA ADMINISTRATIVA"])

with tab_comercial:
    st.subheader(f"Presupuesto para: {sub_sel}")
    st.metric("PRECIO LLAVE EN MANO", f"${calc['precio_venta']:,.0f}")
    st.write("---")
    st.write("### 🏠 ¿Qué incluye este valor?")
    st.write("- Estructura en Steel Framing Galvanizado.")
    st.write("- Piel de Ferrocemento de alta densidad.")
    st.write("- Mano de obra calificada y cimentación básica.")
    
    wa_msg = f"Hola Manuel! 👋 Quiero el {sub_sel} (${calc['precio_venta']:,.0f})"
    st.markdown(f'<a href="https://wa.me/573012428215?text={urllib.parse.quote(wa_msg)}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold; cursor:pointer;">RESERVAR CITA TÉCNICA</button></a>', unsafe_allow_html=True)

with tab_ficha:
    st.markdown("### 🧬 ADN Tecnológico Ferrotek")
    st.write("Explicación del porqué el Ferrocemento con Steel Framing es superior al ladrillo...")
    

with tab_admin:
    st.header("🔑 Panel de Control de Costos")
    psw = st.text_input("Clave Maestra:", type="password")
    
    if psw == st.session_state['db']['config']['admin_pass']:
        st.success("Acceso Autorizado")
        
        st.subheader("📋 Cotización Detallada de Materiales (Costo Interno)")
        st.write("Estos valores son a PRECIO DE COSTO y no los ve el cliente:")
        st.table(calc["mat_detalle"])
        
        st.write(f"**Costo Total Materiales:** ${calc['costo_total_mat']:,.0f}")
        st.write(f"**Costo Mano de Obra:** ${calc['costo_mo']:,.0f}")
        
        st.divider()
        st.subheader("⚙️ Configuración Global de Precios")
        nuevos_p = st.data_editor(st.session_state['db']['precios'])
        if st.button("💾 Guardar Nuevos Precios"):
            st.session_state['db']['precios'] = nuevos_p
            guardar_db(st.session_state['db'])
            st.rerun()
    elif psw != "":
        st.error("Contraseña Incorrecta")