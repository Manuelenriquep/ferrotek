import streamlit as st
import os
import math
import json
import urllib.parse

st.set_page_config(page_title="Ferrotek Master Portfolio", page_icon="🏗️", layout="wide")

# ==========================================
# 💾 BASE DE DATOS UNIFICADA
# ==========================================
ARCHIVO_DB = 'ferrotek_db.json'
def cargar_db():
    if not os.path.exists(ARCHIVO_DB):
        return {"config": {"margen_utilidad": 0.30, "admin_pass": "ferrotek2026"},
                "precios": {
                    'perfil_2_pulg_mt': 12500, 'perfil_C_9cm_mt': 18500,
                    'malla_5mm_m2': 28000, 'malla_zaranda_m2': 8500,
                    'cemento': 29500, 'arena': 98000, 'cal_hidratada': 18000,
                    'aditivo_F1_kg': 48000, 'sellado_FX_galon': 195000,
                    'valor_jornal_dia': 125000
                }}
    with open(ARCHIVO_DB, 'r') as f: return json.load(f)

if 'db' not in st.session_state: st.session_state['db'] = cargar_db()

# ==========================================
# 🧠 LÓGICA DE PRODUCTOS (VIVIENDAS, MUROS, ESTANQUES)
# ==========================================
def calcular_solucion(tipo, cantidad, db):
    p = db['precios']
    if tipo == "Muro de Cerramiento (Sistema Raíz)":
        # ml = cantidad (metros lineales)
        cant_postes = math.ceil(cantidad / 1.5) + 1
        c_acero = (cant_postes * 2.8) * p['perfil_2_pulg_mt'] # 2.2m vista + 0.6m enterrado
        area_malla = cantidad * 2.35 # Alto real de la malla
        c_mallas = (area_malla * p['malla_5mm_m2']) + (area_malla * 2 * p['malla_zaranda_m2'])
        c_mezcla = (cantidad * 2.2 * 0.04 * 1.1) * (5*p['cemento'] + 5*p['cal_hidratada'] + p['arena'])
        c_mo = (cantidad * 0.8) * p['valor_jornal_dia']
        res = c_acero + c_mallas + c_mezcla + c_mo
        return round(res / (1 - db['config']['margen_utilidad']), -3)

    elif tipo == "Estanque Piscícola (Piel de Roca)":
        # m3 = cantidad (asumimos estanque circular de 6m diametro)
        area_pared = 18.8 * 1.2 # Perímetro x Altura
        c_mallas = (area_pared * p['malla_5mm_m2']) + (area_pared * 2 * p['malla_zaranda_m2'])
        c_mezcla = (area_pared * 0.05 * 1.1) * (10*p['cemento'] + p['arena']) # Mezcla rica sin cal
        c_mo = 15 * p['valor_jornal_dia'] # 15 jornales para estanque
        res = c_mallas + c_mezcla + c_mo
        return round(res / (1 - db['config']['margen_utilidad']), -3)

    # Lógica simplificada para viviendas por m2
    elif "Vivienda" in tipo:
        m2 = float(tipo.split('(')[1].split('m2')[0])
        res = m2 * 950000 # Costo base estimado por m2
        return round(res / (1 - db['config']['margen_utilidad']), -3)
    return 0

# ==========================================
# 🎨 INTERFAZ MULTI-PRODUCTO
# ==========================================
st.title("🏗️ FERROTEK.GUANES.BIZ")
st.subheader("Soluciones de Ingeniería Unibody")

menu = st.sidebar.selectbox("Línea de Producto:", [
    "Muro de Cerramiento (Sistema Raíz)",
    "Vivienda 1 Alcoba (30m2)",
    "Vivienda 2 Alcobas (54m2)",
    "Vivienda 3 Alcobas (84m2)",
    "Bóveda / Domo Geodésico (25m2)",
    "Estanque Piscícola (Circular)",
    "Módulo de Baño Tech (Poliuretano)"
])

if "Muro" in menu:
    ml = st.sidebar.number_input("Metros Lineales:", value=50)
    precio = calcular_solucion(menu, ml, st.session_state['db'])
    st.header(f"🛡️ {menu}")
    st.metric("INVERSIÓN TOTAL", f"${precio:,.0f}")
    st.write(f"**Precio por Metro Lineal:** ${precio/ml:,.0f}")
    
    st.info("### El 'Hit' de Ferrotek frente a la mampostería:")
    st.write("- **Sin vigas de amarre costosas:** Usamos el sistema de Anclaje Raíz.")
    st.write("- **Sin pañete ni pintura:** Matriz 1:3:3 autoprotegida contra el hongo.")
    st.write("- **Velocidad:** Instalamos 50 metros en menos de 10 días.")
    

elif "Vivienda" in menu:
    precio = calcular_solucion(menu, 0, st.session_state['db'])
    st.header(f"🏠 {menu}")
    st.metric("INVERSIÓN LLAVE EN MANO", f"${precio:,.0f}")
    st.write("- **Estructura Monocasco:** Sismo-resistente y térmica.")
    st.write("- **Acabados Industriales:** Pisos poliméricos y muros de alta densidad.")
    

# ==========================================
# 📈 COMPARADOR DE "EL PALO" (Muro Tradicional vs Ferrotek)
# ==========================================
st.divider()
st.subheader("📊 Comparativa de Costos: Muro de 50 metros")
col1, col2 = st.columns(2)
with col1:
    st.error("### Mampostería Tradicional")
    st.write("- Ladrillo, Viga, Columnas, Revoque, Pintura.")
    st.write("- Tiempo: 30-40 días.")
    st.write("- **Costo Est: $45,000,000+**")
with col2:
    st.success("### Sistema Ferrotek Unibody")
    st.write("- Postes 2\", Sándwich 5mm, Matriz 1:3:3.")
    st.write("- Tiempo: 10 días.")
    st.write(f"- **Costo Est: ${precio:,.0f}**") # Basado en el cálculo dinámico