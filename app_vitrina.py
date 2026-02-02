import streamlit as st
import os
import math
import json
import urllib.parse

st.set_page_config(page_title="Ferrotek | Exclusividad Unibody", page_icon="🏗️", layout="wide")

# ==========================================
# 💾 DB - Nombres de Insumos "Codificados" para el Cliente
# ==========================================
ARCHIVO_DB = 'ferrotek_db.json'
def cargar_db():
    if not os.path.exists(ARCHIVO_DB):
        return {"config": {"margen_utilidad": 0.35, "admin_pass": "ferrotek2026"},
                "precios": {'acero_estructural_kg': 7200, 'acero_comercial_kg': 5800, 'cemento': 29500, 
                           'arena': 98000, 'valor_jornal_dia': 125000, 'punto_electrico': 40000, 
                           'punto_hidraulico': 120000, 'aditivo_F1_kg': 48000, # Nombre codificado
                           'sellado_FX_galon': 195000, 'acometida_base': 1200000}}
    with open(ARCHIVO_DB, 'r') as f: return json.load(f)

if 'db' not in st.session_state: st.session_state['db'] = cargar_db()

# ==========================================
# 🧠 CÁLCULOS PRIVADOS
# ==========================================
PORTAFOLIO = {
    "Vivienda 1 Alcoba (30m²)": {"area": 30, "perim": 24, "esp": 3, "j": 70},
    "Vivienda 2 Alcobas (54m²)": {"area": 54, "perim": 32, "esp": 5, "j": 115},
    "Vivienda 3 Alcobas (84m²)": {"area": 84, "perim": 40, "esp": 7, "j": 165},
    "Máster Unibody (100m²)": {"area": 100, "perim": 44, "esp": 8, "j": 200}
}

def cotizar_blindado(item, db):
    p = db['precios']
    m = PORTAFOLIO[item]
    # Cálculos internos (basados en tu investigación de 20 años)
    c_base = (math.ceil((m['perim']/0.4)+6)*9.5*p['acero_comercial_kg']) + (int(((m['area']*0.12)+(m['perim']*2.4*0.05))*9.5)*p['cemento'])
    c_quimicos = (m['area'] * 0.2 * p['aditivo_F1_kg']) + (m['area'] / 12 * p['sellado_FX_galon'])
    c_inst = (m['esp'] * 3 * p['punto_electrico']) + p['acometida_base'] + (5 * p['punto_hidraulico'])
    costo = c_base + c_quimicos + c_inst + (m['j'] * p['valor_jornal_dia'])
    return {"precio": round(costo / (1 - db['config']['margen_utilidad']), -3), "area_g": round(m['perim']*0.1, 1)}

# ==========================================
# 🎨 INTERFAZ ESTRATÉGICA
# ==========================================
t_home, t_quote, t_admin = st.tabs(["💎 EL SISTEMA FERROTEK", "📊 ESTUDIO DE INVERSIÓN", "🔑 PANEL DIRECTOR"])

with t_home:
    st.title("🏗️ FERROTEK: Vivienda Monocasco de Alta Tecnología")
    st.write("### 🛡️ Respaldado por 20 años de investigación en Ciencia de Materiales")
    
    st.markdown("""
    Nuestro sistema no se 'construye', se **manufactura** bajo estándares de ingeniería avanzada que superan por 
    completo la mampostería tradicional.
    """)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("### 📐 Recuperación Espacial")
        st.write("La eficiencia de nuestra **Piel de Roca Unibody** le otorga hasta un 10% más de área libre que una casa de ladrillo. No pague por muros gruesos y obsoletos.")
        
        
    with c2:
        st.success("### 🧪 Matriz Polimérica F1")
        st.write("Utilizamos una aleación cementicia modificada con polímeros de alta densidad. El resultado: superficies elásticas, impermeables y de mantenimiento cero.")
        
        
    with c3:
        st.warning("### ⏱️ Ciclos de Manufactura")
        st.write("Reducimos el tiempo de entrega en un 40%. Un sistema industrializado en sitio que garantiza precisión milimétrica y sismo-resistencia superior.")

with t_quote:
    sel = st.selectbox("Seleccione Prototipo para Análisis de Inversión:", list(PORTAFOLIO.keys()))
    res = cotizar_blindado(sel, st.session_state['db'])
    
    col1, col2 = st.columns(2)
    col1.metric("VALOR TOTAL DEL PROYECTO", f"${res['precio']:,.0f}")
    col2.metric("ÁREA EXTRA GANADA", f"{res['area_g']} m²")
    
    st.divider()
    st.write("⚠️ *La composición exacta de la **Matriz Ferrotek F1** es propiedad intelectual de la compañía y solo se aplica bajo supervisión técnica autorizada.*")
    
    msg = f"Deseo una validación técnica para el modelo {sel} de Ferrotek."
    st.markdown(f'<a href="https://wa.me/573012428215?text={urllib.parse.quote(msg)}" target="_blank"><button style="width:100%; background-color:#1E3A8A; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold; cursor:pointer;">🟢 CONTACTAR DIRECTOR TÉCNICO</button></a>', unsafe_allow_html=True)

with t_admin:
    psw = st.text_input("Acceso de Seguridad:", type="password")
    if psw == st.session_state['db']['config']['admin_pass']:
        st.write("### Gestión de Insumos Críticos")
        st.data_editor(st.session_state['db']['precios'])
        if st.button("Guardar"):
            with open(ARCHIVO_DB, 'w') as f: json.dump(st.session_state['db'], f)
            st.success("Base de datos sincronizada.")