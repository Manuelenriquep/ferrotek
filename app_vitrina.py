import streamlit as st
import os
import math
import json
import urllib.parse

# Configuración de página
st.set_page_config(page_title="Ferrotek Master | Vitrina 2026", page_icon="🏗️", layout="wide")

# ==========================================
# 💾 GESTIÓN DE DATOS CENTRAL
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
        return data

def guardar_db(nueva_db):
    with open(ARCHIVO_DB, 'w') as f: json.dump(nueva_db, f)

if 'db' not in st.session_state: st.session_state['db'] = cargar_db()

# ==========================================
# 🧠 MOTOR TÉCNICO (CÁLCULO PRIVADO)
# ==========================================
def realizar_calculos(cat, sub, db, ext):
    p = db['precios']
    margen = db['config']['margen_utilidad']
    
    # Modelos de Vivienda
    models = {
        "6x12 Smart (72m²)": {"a": 72, "p": 36, "d": 45},
        "Loft 35m²": {"a": 35, "p": 24, "d": 22},
        "Eco-Hogar 40m²": {"a": 40, "p": 26, "d": 28},
        "Familiar 65m²": {"a": 65, "p": 34, "d": 35},
        "Domo/Bóveda 25m²": {"a": 25, "p": 18, "d": 15}
    }

    if cat == "Vivienda":
        m = models[sub]
        es_2p = ext.get('piso2', False)
        peso = 13 if es_2p else 9
        precio_kg = p['acero_estructural_kg'] if es_2p else p['acero_comercial_kg']
        
        cant_c = math.ceil((m['p']/0.50)/2) + 6
        if es_2p: cant_c = int(cant_c * 1.8)
        
        vol_mort = (m['a']*0.08) + (m['p']*2.4*0.05)
        cem = int(vol_mort * 8.5)
        
        # Detalle interno para Manuel
        mat_detalle = {
            "Item": ["Perfiles PHR C", "Bultos Cemento", "Arena (m³)", "Mallas"],
            "Cantidad": [cant_c, cem, round(vol_mort*1.1,1), math.ceil(m['a']/12)+2],
            "Costo Est.": [f"${cant_c*peso*precio_kg:,.0f}", f"${cem*p['cemento']:,.0f}", f"${vol_mort*1.1*p['arena']:,.0f}", f"${(math.ceil(m['a']/12)+2)*p['malla_electro']:,.0f}"]
        }
        
        costo_mat = (cant_c * peso * precio_kg) + (cem * p['cemento']) + (vol_mort * 1.1 * p['arena'])
        if ext.get('wifi'): costo_mat += p['kit_starlink']
        if es_2p: costo_mat += (p['anclaje_epoxico_und'] * 12)
        
        costo_mo = m['a'] * p['mo_m2_casa'] * (1.3 if es_2p else 1.0)
        dias = m['dias']
    else:
        # Lógica para estanques simplificada
        vol = ext.get('volumen', 20)
        costo_mat = vol * 150000; costo_mo = vol * 80000; dias = 15
        mat_detalle = {"Item": ["Materiales Estanque"], "Cantidad": [vol], "Costo Est.": [f"${costo_mat:,.0f}"]}

    precio_v = (costo_mat + costo_mo) / (1 - margen)
    return {"precio": round(precio_v, -3), "mat_detalle": mat_detalle, "dias": dias, "costo_base": costo_mat + costo_mo}

# ==========================================
# 🎨 INTERFAZ LIMPIA
# ==========================================
st.sidebar.title("🏗️ FERROTEK V34.0")
cat_sel = st.sidebar.selectbox("Línea de Servicio:", ["Vivienda", "Estanques / Tanques"])

with st.sidebar:
    if cat_sel == "Vivienda":
        sub_sel = st.selectbox("Modelo:", ["6x12 Smart (72m²)", "Loft 35m²", "Eco-Hogar 40m²", "Familiar 65m²", "Domo/Bóveda 25m²"])
        p2 = st.checkbox("Preparar para 2do Piso")
        stk = st.checkbox("Internet Satelital Ready")
        par = {'piso2': p2, 'wifi': stk}
    else:
        sub_sel = "Estanque de Ferrocemento"
        v = st.slider("Volumen (m³):", 5, 100, 20)
        par = {'volumen': v}

calc = realizar_calculos(cat_sel, sub_sel, st.session_state['db'], par)

# TABS
t_cliente, t_ficha, t_admin = st.tabs(["🏡 Cotización", "📑 Ficha Técnica", "🔑 Administración"])

with t_cliente:
    c1, c2 = st.columns([2, 1])
    with c1:
        st.header(sub_sel)
        st.write("### ✅ Su proyecto incluye:")
        st.write("- **Estructura:** Sistema Steel Framing sismo-resistente (NSR-10).")
        st.write("- **Cerramiento:** Paredes monolíticas de ferrocemento (Espesor 5-6cm).")
        st.write("- **Infraestructura:** Canalizaciones para servicios públicos y Smart Home.")
        if par.get('wifi'):
            st.info("🛰️ **Bono Conectividad:** Equipo Starlink incluido para internet satelital de alta velocidad.")
        
    with c2:
        st.metric("INVERSIÓN ESTIMADA", f"${calc['precio']:,.0f}")
        st.write(f"⏱️ Tiempo de entrega: **{calc['dias']} días**.")
        wa_msg = f"Hola Manuel! 👋 Solicito visita para {sub_sel}. Valor: ${calc['precio']:,.0f}"
        st.markdown(f'<a href="https://wa.me/573012428215?text={urllib.parse.quote(wa_msg)}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold; cursor:pointer;">SOLICITAR VISITA TÉCNICA</button></a>', unsafe_allow_html=True)

with t_ficha:
    st.markdown("### 📑 ¿Por qué elegir Ferrotek?")
    st.write("Nuestro sistema híbrido ofrece paredes más delgadas (más espacio), mayor resistencia sísmica y una solidez de piedra que el drywall o las placas no pueden igualar.")
    

with t_admin:
    st.subheader("🔐 Acceso Privado")
    psw = st.text_input("Clave Maestra:", type="password")
    if psw == st.session_state['db']['config']['admin_pass']:
        st.success("Bienvenido, Manuel.")
        st.write("---")
        st.subheader("📋 Explosión de Materiales (Costo Real)")
        st.table(calc["mat_detalle"])
        st.write(f"**Costo Operativo Base:** ${calc['costo_base']:,.0f}")
        
        st.divider()
        st.subheader("⚙️ Actualizar Precios Globales")
        nuevos_p = st.data_editor(st.session_state['db']['precios'])
        if st.button("💾 Guardar Cambios"):
            st.session_state['db']['precios'] = nuevos_p
            guardar_db(st.session_state['db'])
            st.rerun()