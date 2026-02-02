import streamlit as st
import math
import json
from datetime import datetime
import urllib.parse

# ==========================================
# ⚙️ CONFIGURACIÓN Y ESTILOS
# ==========================================
st.set_page_config(page_title="Ferrotek | Ingeniería Unibody", page_icon="🏗️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; }
    .card { padding: 20px; border-radius: 15px; background-color: white; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 💾 BASE DE DATOS ESTRUCTURAL
# ==========================================
# Se asume que estos valores son los base, pero se pueden editar en el Panel Director
if 'db' not in st.session_state:
    st.session_state['db'] = {
        "config": {"margen_utilidad": 0.30, "admin_pass": "ferrotek2026"},
        "precios": {
            'perfil_2_pulg_mt': 12500,
            'malla_5mm_m2': 28000,
            'malla_zaranda_m2': 8500,
            'cemento_bulto': 29500,
            'cal_bulto': 18500,
            'arena_m3': 98000,
            'aditivo_F1_kg': 48000,
            'sellado_FX_galon': 195000,
            'valor_jornal': 125000
        }
    }

# ==========================================
# 🧠 MOTORES DE CÁLCULO (TU INGENIERÍA)
# ==========================================

def calcular_muro_perimetral(ml, h):
    p = st.session_state['db']['precios']
    # Estructura Raíz: Postes cada 1.5m
    cant_postes = math.ceil(ml / 1.5) + 1
    c_acero = (cant_postes * (h + 0.6) + (ml * 2)) * p['perfil_2_pulg_mt']
    # Sándwich Simple para cerramiento (Ahorro)
    area_malla = ml * 2.35 # Altura comercial de la malla electrosoldada
    c_mallas = (area_malla * p['malla_5mm_m2']) + (area_malla * 2 * p['malla_zaranda_m2'])
    # Mezcla 1:3:3
    vol_mezcla = (ml * h * 0.04) * 1.1
    c_mezcla = vol_mezcla * (5*p['cemento_bulto'] + 5*p['cal_bulto'] + p['arena_m3'])
    # Mano de obra optimizada
    c_mo = (ml * 0.8) * p['valor_jornal']
    
    total_dir = c_acero + c_mallas + c_mezcla + c_mo
    return round(total_dir / (1 - st.session_state['db']['config']['margen_utilidad']), -3)

def calcular_vivienda(area_m2):
    p = st.session_state['db']['precios']
    # Estimación de perímetros según metraje
    perim = math.sqrt(area_m2) * 4
    div_int = perim * 0.6 # Estimación de muros internos
    
    # Fachadas (Doble Membrana) + Internos (Simple)
    area_ext = perim * 2.4
    area_int = div_int * 2.4
    
    c_mallas = (area_ext * (p['malla_5mm_m2'] + 2*p['malla_zaranda_m2'])) + \
               (area_int * (p['malla_5mm_m2'] + p['malla_zaranda_m2']))
    
    # Mezcla 1:3:3 muros + 2:1 polimérica en pisos
    c_mezcla = (area_ext + area_int) * 0.04 * (5*p['cemento_bulto'] + 5*p['cal_bulto'] + p['arena_m3'])
    c_pisos = area_m2 * (0.2 * p['aditivo_F1_kg'] + 0.1 * p['sellado_FX_galon'])
    
    # Estructura y MO
    c_est = (perim + div_int) * 1.5 * p['perfil_2_pulg_mt']
    c_mo = area_m2 * 2.5 * p['valor_jornal'] # 2.5 jornales por m2
    
    total_dir = c_mallas + c_mezcla + c_pisos + c_est + c_mo
    return round(total_dir / (1 - st.session_state['db']['config']['margen_utilidad']), -3)

# ==========================================
# 🎨 NAVEGACIÓN Y VISTAS
# ==========================================
if 'view' not in st.session_state: st.session_state.view = 'home'

def set_view(name): st.session_state.view = name

# --- HEADER JURÍDICO ---
st.sidebar.markdown(f"""
    ### ⚖️ Dirección Jurídica
    **Manuel Enrique Prada Forero**
    TP: 176.633 CSJ
    [abogado@guanes.biz](mailto:abogado@guanes.biz)
    """)

if st.session_state.view == 'home':
    st.title("🏗️ Portafolio de Ingeniería Ferrotek")
    st.subheader("Soluciones Monocasco en Piel de Roca")
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("### 🛡️ Cerramientos")
        st.write("Muros perimetrales con Sistema Raíz. El 'Hit' de ventas contra la mampostería.")
        if st.button("Cotizar Muro"): set_view('muros')
    with col2:
        st.write("### 🏠 Viviendas")
        st.write("Modelos Unibody de 30, 54 y 84 m². Térmicas, sismo-resistentes y rápidas.")
        if st.button("Ver Viviendas"): set_view('viviendas')
    with col3:
        st.write("### 🏺 Especiales")
        st.write("Estanques piscícolas, bóvedas y módulos de baño industriales.")
        if st.button("Ver Especiales"): set_view('especiales')

elif st.session_state.view == 'muros':
    st.button("⬅️ Volver al Menú", on_click=lambda: set_view('home'))
    st.header("🛡️ Cotizador de Muros Perimetrales")
    
    ml = st.number_input("Metros Lineales del lote:", value=50.0, step=10.0)
    h = st.slider("Altura del muro (m):", 1.0, 3.0, 2.2)
    
    precio_total = calcular_muro_perimetral(ml, h)
    
    c1, c2 = st.columns(2)
    c1.metric("INVERSIÓN TOTAL", f"${precio_total:,.0f}")
    c2.metric("PRECIO POR METRO", f"${precio_total/ml:,.0f}")
    
    st.divider()
    st.subheader("📊 Comparativa de Mercado (50m)")
    col_a, col_b = st.columns(2)
    col_a.error(f"**Tradicional:** ~$45,000,000\n(30 días, escombros, grietas)")
    col_b.success(f"**Ferrotek:** ${precio_total:,.0f}\n(10 días, monolítico, autoprotegido)")

    # DOCUMENTO TÉCNICO
    if st.button("📄 Generar Propuesta de Inversión"):
        txt = f"PROPUESTA FERROTEK\nMetros: {ml}m\nAltura: {h}m\nTotal: ${precio_total:,.0f}\nFórmula: 1:3:3 con Sistema Raíz."
        st.download_button("Descargar Documento", txt, file_name="Propuesta_Muro.txt")

elif st.session_state.view == 'viviendas':
    st.button("⬅️ Volver al Menú", on_click=lambda: set_view('home'))
    st.header("🏠 Modelos de Vivienda Unibody")
    
    sel_casa = st.selectbox("Seleccione Modelo:", ["Suite (30m²)", "Familiar (54m²)", "Máster (84m²)"])
    area = 30 if "30" in sel_casa else (54 if "54" in sel_casa else 84)
    
    precio_casa = calcular_vivienda(area)
    
    st.metric(f"INVERSIÓN LLAVE EN MANO ({area}m²)", f"${precio_casa:,.0f}")
    
    st.write("### 📐 Criterios de Ingeniería Aplicados:")
    st.write("- **Fachadas:** Doble membrana para confort térmico.")
    
    st.write("- **Internos:** Membrana simple para ganancia de área real.")
    
    st.write("- **Acabados:** Matriz 1:3:3 en muros y 2:1 polimérica en pisos (Cero pintura).")

# --- PANEL DIRECTOR (OCULTO) ---
st.sidebar.divider()
if st.sidebar.checkbox("🔑 Acceso Director"):
    pwd = st.sidebar.text_input("Contraseña:", type="password")
    if pwd == st.session_state['db']['config']['admin_pass']:
        st.sidebar.success("Acceso Concedido")
        new_prices = st.data_editor(st.session_state['db']['precios'])
        if st.sidebar.button("💾 Guardar Precios"):
            st.session_state['db']['precios'] = new_prices
            st.sidebar.toast("Precios actualizados!")