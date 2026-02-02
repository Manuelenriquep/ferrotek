import streamlit as st
import os
import math
import json
import urllib.parse

st.set_page_config(page_title="Ferrotek Unified | Financial Control", page_icon="🏗️", layout="wide")

# ==========================================
# 💾 GESTIÓN DE DATOS (CON JORNALES)
# ==========================================
ARCHIVO_DB = 'ferrotek_db.json'

# Definimos los valores iniciales. El jornal incluye prestaciones y seguridad social.
DB_INICIAL = {
    "config": {"margen_utilidad": 0.30, "admin_pass": "ferrotek2026"},
    "precios": {
        'acero_estructural_kg': 7200, 'acero_comercial_kg': 5500,
        'cemento': 28500, 'arena': 95000, 'triturado': 115000,
        'malla_electro': 215000, 'malla_zaranda': 285000,
        'valor_jornal_dia': 110000, # Valor a actualizar cada año
        'kit_starlink': 2200000, 'anclaje_epoxico_und': 85000
    }
}

def cargar_db():
    if not os.path.exists(ARCHIVO_DB):
        with open(ARCHIVO_DB, 'w') as f: json.dump(DB_INICIAL, f)
        return DB_INICIAL
    with open(ARCHIVO_DB, 'r') as f: 
        data = json.load(f)
        # Aseguramos que existan las llaves nuevas
        if 'valor_jornal_dia' not in data['precios']: data['precios']['valor_jornal_dia'] = 110000
        return data

def guardar_db(nueva_db):
    with open(ARCHIVO_DB, 'w') as f: json.dump(nueva_db, f)

if 'db' not in st.session_state: st.session_state['db'] = cargar_db()

# ==========================================
# 🧠 MOTOR DE INGENIERÍA Y COSTEO POR JORNAL
# ==========================================
def calcular_sistema_unificado(cat, sub, db, ext):
    p = db['precios']
    margen = db['config']['margen_utilidad']
    
    # Cantidad de JORNALES (Días de trabajo de cuadrilla) por modelo
    # Esto es lo que NO cambia aunque suba el salario
    esfuerzo_obra = {
        "6x12 Smart (72m²)": {"a": 72, "p": 36, "dias_obra": 45, "jornales_total": 120},
        "Loft 35m²": {"a": 35, "p": 24, "dias_obra": 22, "jornales_total": 60},
        "Eco-Hogar 40m²": {"a": 40, "p": 26, "dias_obra": 28, "jornales_total": 75},
        "Familiar 65m²": {"a": 65, "p": 34, "dias_obra": 35, "jornales_total": 110},
        "Domo/Bóveda 25m²": {"a": 25, "p": 18, "dias_obra": 15, "jornales_total": 45}
    }

    if cat == "Vivienda Unibody":
        m = esfuerzo_obra[sub]
        es_2p = ext.get('piso2', False)
        
        # Cálculo de Materiales
        peso = 13 if es_2p else 9
        pr_kg = p['acero_estructural_kg'] if es_2p else p['acero_comercial_kg']
        cant_c = math.ceil((m['p']/0.50)/2) + 6
        if es_2p: cant_c = int(cant_c * 1.8)
        
        vol_mort = (m['a']*0.08) + (m['p']*2.4*0.05)
        cem = int(vol_mort * 8.5)
        
        costo_mat = (cant_c * peso * pr_kg) + (cem * p['cemento']) + (vol_mort * 1.1 * p['arena'])
        if ext.get('wifi'): costo_mat += p['kit_starlink']
        
        # CÁLCULO DE MANO DE OBRA BASADO EN JORNALES
        num_jornales = m['jornales_total']
        if es_2p: num_jornales *= 1.4 # Un 40% más de esfuerzo humano por altura
        
        costo_mo_total = num_jornales * p['valor_jornal_dia']
        
        # Detalle para Admin
        mat_detalle = {
            "Componente": ["Acero Estructural", "Piel de Roca (Cemento)", "Insumos Varios", "Mano de Obra (Jornales)"],
            "Cantidad": [f"{cant_c} PHR", f"{cem} Bultos", "N/A", f"{round(num_jornales)} Días/Hombre"],
            "Costo": [f"${cant_c*peso*pr_kg:,.0f}", f"${cem*p['cemento']:,.0f}", f"${(vol_mort*1.1*p['arena']):,.0f}", f"${costo_mo_total:,.0f}"]
        }
        dias_entrega = m['dias_obra']
    else:
        # Lógica simplificada para tanques
        vol = ext.get('volumen', 20)
        costo_mat = vol * 165000
        costo_mo_total = (vol * 0.8) * p['valor_jornal_dia'] # 0.8 jornales por m3
        mat_detalle = {"Componente": ["Sistema Tanque"], "Cantidad": [vol], "Costo": [f"${costo_mat:,.0f}"]}
        dias_entrega = 12

    precio_final = (costo_mat + costo_mo_total) / (1 - margen)
    return {"precio": round(precio_final, -3), "mat_detalle": mat_detalle, "dias": dias_entrega, "costo_base": costo_mat + costo_mo_total}

# ==========================================
# 🎨 INTERFAZ ACTUALIZADA
# ==========================================
st.sidebar.title("🏗️ FERROTEK UNIFIED")
opcion = st.sidebar.selectbox("Línea de Ingeniería:", ["Vivienda Unibody", "Unidades de Almacenamiento"])

with st.sidebar:
    if opcion == "Vivienda Unibody":
        sel = st.selectbox("Configuración:", ["6x12 Smart (72m²)", "Loft 35m²", "Eco-Hogar 40m²", "Familiar 65m²", "Domo/Bóveda 25m²"])
        p2 = st.checkbox("Refuerzo Estructural Multinivel")
        wifi = st.checkbox("Nodo Starlink")
        par = {'piso2': p2, 'wifi': wifi}
    else:
        sel = "Almacenamiento"
        vol = st.slider("Capacidad m³:", 5, 200, 20)
        par = {'volumen': vol}

calc = calcular_sistema_unificado(opcion, sel, st.session_state['db'], par)

t1, t2, t3 = st.tabs(["🚀 Inversión", "📐 Ingeniería", "🔑 Admin Privado"])

with t1:
    c1, c2 = st.columns([2, 1])
    with c1:
        st.header(sel)
        st.write("### 💎 Características del Sistema:")
        st.write("- Piel de Roca de Alta Densidad.")
        st.write("- Estructura Unibody Sismo-Resistente.")
    with c2:
        st.metric("VALOR TOTAL", f"${calc['precio']:,.0f}")
        wa_url = f"https://wa.me/573012428215?text=Info%20{sel}"
        st.markdown(f'<a href="{wa_url}" target="_blank"><button style="width:100%; background-color:#1E3A8A; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold; cursor:pointer;">VALIDACIÓN TÉCNICA</button></a>', unsafe_allow_html=True)

with t3:
    st.subheader("⚙️ Control Maestro de Costos")
    psw = st.text_input("Password:", type="password")
    if psw == st.session_state['db']['config']['admin_pass']:
        st.write("### Desglose de Costos de Ejecución")
        st.table(calc["mat_detalle"])
        
        st.divider()
        st.subheader("📊 Inventario de Precios y Jornal")
        st.info("Actualice aquí el 'valor_jornal_dia' cuando cambie el salario mínimo o el costo de vida.")
        nuevos_p = st.data_editor(st.session_state['db']['precios'])
        if st.button("💾 Guardar y Sincronizar"):
            st.session_state['db']['precios'] = nuevos_p
            guardar_db(st.session_state['db'])
            st.rerun()