import streamlit as st
import os
import math
import json
import urllib.parse

st.set_page_config(page_title="Ferrotek | Industrialized Systems", page_icon="🏭", layout="wide")

# ==========================================
# 💾 PERSISTENCIA (Sincronizada)
# ==========================================
ARCHIVO_DB = 'ferrotek_db.json'
def cargar_db():
    if not os.path.exists(ARCHIVO_DB):
        return {"config": {"margen_utilidad": 0.35, "admin_pass": "ferrotek2026"},
                "precios": {'acero_estructural_kg': 7200, 'acero_comercial_kg': 5800, 'cemento': 29500, 
                           'arena': 98000, 'triturado': 118000, 'malla_electro': 225000, 
                           'valor_jornal_dia': 125000, 'kit_starlink': 2200000}}
    with open(ARCHIVO_DB, 'r') as f: return json.load(f)

if 'db' not in st.session_state: st.session_state['db'] = cargar_db()

# ==========================================
# 🧠 MOTOR DE PRODUCTIVIDAD INDUSTRIAL
# ==========================================
PORTAFOLIO = {
    "Vivienda 1 Alcoba (30m²)": {"area": 30, "perim": 24, "jornales": 65, "cat": "Vivienda"},
    "Vivienda 2 Alcobas (54m²)": {"area": 54, "perim": 32, "jornales": 105, "cat": "Vivienda"},
    "Vivienda 3 Alcobas (84m²)": {"area": 84, "perim": 40, "jornales": 155, "cat": "Vivienda"},
    "Vivienda Interés Social (72m²)": {"area": 72, "perim": 36, "jornales": 135, "cat": "Vivienda"},
    "Máster Unibody (100m²)": {"area": 100, "perim": 44, "jornales": 185, "cat": "Vivienda"},
    "Bóveda / Domo Geodésico": {"area": 25, "perim": 18, "jornales": 55, "cat": "Especial"},
    "Estanque Piscícola (20m³)": {"area": 32, "perim": 16, "jornales": 35, "cat": "Estanque"},
    "Muro Perimetral (metro lineal)": {"area": 2.5, "perim": 1, "jornales": 3, "cat": "Muro"}
}

def calcular_industrial(item, db, ext):
    p = db['precios']
    m = PORTAFOLIO[item]
    # Cálculo de Insumos Estándar
    c_mat = (math.ceil((m['perim']/0.40)/2)+6)*9.5*(p['acero_estructural_kg'] if ext.get('p2') else p['acero_comercial_kg'])
    c_mat += (int(((m['area']*0.10)+(m['perim']*2.4*0.05))*9.5)*p['cemento'])
    c_mo = m['jornales'] * p['valor_jornal_dia']
    precio = (c_mat + c_mo) / (1 - db['config']['margen_utilidad'])
    return {"precio": round(precio, -3), "costo_directo": c_mat + c_mo, "eficiencia": round(m['area']/m['jornales'], 2)}

# ==========================================
# 🎨 INTERFAZ
# ==========================================
st.sidebar.title("🏗️ FERROTEK INDUSTRIAL")
sel = st.sidebar.selectbox("Seleccione Prototipo:", list(PORTAFOLIO.keys()))
p2 = st.sidebar.checkbox("Refuerzo Multinivel")
res = calcular_industrial(sel, st.session_state['db'], {'p2': p2})

t1, t2, t3 = st.tabs(["📊 Propuesta Ejecutiva", "🔬 Ficha de Proceso", "🔑 Control de Planta"])

with t1:
    st.header(sel)
    st.metric("INVERSIÓN SISTEMA LLAVE EN MANO", f"${res['precio']:,.0f}")
    st.write("---")
    st.write("### 💎 Por qué es un Sistema Industrializado:")
    st.write("- **Precisión:** Estructuras pre-calculadas que eliminan el error humano.")
    st.write("- **Velocidad:** Reducción del 40% en tiempos de obra frente a mampostería.")
    st.write("- **Sostenibilidad:** Cero escombros y desperdicio de materiales optimizado.")
    
    wa = f"https://wa.me/573012428215?text=Interes%20Prototipo%20{sel}"
    st.markdown(f'<a href="{wa}" target="_blank"><button style="width:100%; background-color:#1E3A8A; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold; cursor:pointer;">INICIAR PROCESO DE VALIDACIÓN</button></a>', unsafe_allow_html=True)

with t2:
    st.subheader("Flujo de Manufactura en Sitio")
    st.write("1. **Anclaje:** Fijación de bases sobre cimentación técnica.")
    st.write("2. **Armado:** Montaje de esqueleto Steel Framing Unibody.")
    st.write("3. **Blindaje:** Aplicación de Piel de Roca de Alta Densidad.")
    

with t3:
    psw = st.text_input("Acceso Director:", type="password")
    if psw == st.session_state['db']['config']['admin_pass']:
        st.write(f"**Costo Directo:** ${res['costo_directo']:,.0f}")
        st.write(f"**Índice de Productividad:** {res['eficiencia']} m²/jornal")
        st.info("💡 Este índice mide cuántos m² construye un operario por día. ¡Optimízalo!")