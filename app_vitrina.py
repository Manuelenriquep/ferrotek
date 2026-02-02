import streamlit as st
import os
import math
import json
import urllib.parse

# Configuración de página
st.set_page_config(page_title="Ferrotek Master | Catálogo 2026", page_icon="🏗️", layout="wide")

# ==========================================
# 💾 BASE DE DATOS INTEGRAL
# ==========================================
ARCHIVO_DB = 'ferrotek_db.json'

DB_INICIAL = {
    "config": {"margen_utilidad": 0.30},
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
        # Asegurar que nuevos precios de Starlink y Acero estén presentes
        for k, v in DB_INICIAL["precios"].items():
            if k not in data["precios"]: data["precios"][k] = v
        return data

if 'db' not in st.session_state: st.session_state['db'] = cargar_db()

# ==========================================
# 🧠 MOTOR DE CÁLCULO V31 (Multi-Producto)
# ==========================================
def calcular_presupuesto(categoria, subcat, db, extras):
    p = db['precios']
    margen = db.get('config', {}).get('margen_utilidad', 0.30)
    
    # Inicialización de variables
    lista_materiales = {}
    costo_materiales = 0
    costo_mo = 0
    dias = 0
    
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
        
        # Lógica Steel Framing
        peso_kg = 13 if es_2p else 9
        pr_kg = p['acero_estructural_kg'] if es_2p else p['acero_comercial_kg']
        
        cant_c = math.ceil((m['perim']/0.50)/2) + 6
        if es_2p: cant_c = int(cant_c * 1.8)
        
        vol_mortero = (m['area']*0.08) + (m['perim']*2.4*0.05)
        cem = int(vol_mortero * 8.5)
        
        lista_materiales = {
            "Bultos de Cemento": cem,
            "Arena de Río (m³)": round(vol_mortero * 1.1, 1),
            "Perfiles PHR C (Estructural)": cant_c,
            "Mallas Electrosoldadas": math.ceil(m['area']/12) + 2,
            "Malla Zaranda (Rollos)": math.ceil((m['perim']*2.4)/30)
        }
        
        costo_materiales = (cant_c * peso_kg * pr_kg) + (cem * p['cemento']) + (vol_mortero * p['arena'])
        if extras.get('wifi'): costo_materiales += p['kit_starlink']
        if es_2p: costo_materiales += (p['anclaje_epoxico_und'] * 12)
        
        costo_mo = m['area'] * p['mo_m2_casa'] * (1.3 if es_2p else 1.0)
        dias = m['dias']

    elif categoria == "Estanques / Piscícola":
        vol = extras.get('volumen', 10)
        # Estimación rápida de área de ferrocemento para cilindro
        area_f = vol * 1.6 
        cem = int(area_f * 0.5)
        lista_materiales = {
            "Cemento": cem,
            "Arena (m³)": round(area_f * 0.05, 1),
            "Malla Zaranda (m)": int(area_f * 2.5),
            "Aditivo Impermeabilizante": 2
        }
        costo_materiales = (cem * p['cemento']) + (area_f * 0.05 * p['arena'])
        costo_mo = area_f * p['mo_m2_tanque']
        dias = 7 if vol < 50 else 15

    # Cálculo Final con Margen
    precio_venta = (costo_materiales + costo_mo) / (1 - margen)
    return {"precio": round(precio_venta, -3), "lista": lista_materiales, "dias": dias}

# ==========================================
# 🎨 INTERFAZ DE USUARIO (REFORMADA)
# ==========================================
st.sidebar.title("🏗️ FERROTEK CATALOG")
cat_principal = st.sidebar.selectbox("¿Qué desea construir?", ["Vivienda", "Estanques / Piscícola"])

with st.sidebar:
    if cat_principal == "Vivienda":
        modelo_sel = st.selectbox("Elija el modelo:", ["6x12 Smart (72m²)", "Loft 35m²", "Eco-Hogar 40m²", "Familiar 65m²", "Domo/Bóveda 25m²"])
        p2 = st.checkbox("Proyectar 2do Piso (Estructural)")
        wifi = st.checkbox("Incluir Kit Starlink (Internet)")
        params = {'piso2': p2, 'wifi': wifi}
    else:
        modelo_sel = "Estanque Ferrocemento"
        vol_estanque = st.slider("Volumen del estanque (m³):", 5, 200, 20)
        params = {'volumen': vol_estanque}

datos = calcular_presupuesto(cat_principal, modelo_sel, st.session_state['db'], params)

# TABS PRINCIPALES
t1, t2, t3, t4 = st.tabs(["📊 Cotización Real", "📄 Ficha Técnica Superior", "📐 Plano 6x12", "👷 Guía Técnica"])

with t1:
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.subheader(f"Propuesta Técnica: {modelo_sel}")
        st.write("---")
        st.write("### 📋 Desglose de Materiales Sugeridos")
        # FORZAMOS TABLA PARA EVITAR EL FORMATO JSON { }
        st.table(datos['lista'])
        
    with col_b:
        st.metric("PRECIO TOTAL ESTIMADO", f"${datos['precio']:,.0f}")
        st.success(f"⏱️ Ejecución en {datos['dias']} días")
        
        if params.get('wifi'):
            st.info("🛰️ **Internet Satelital:** Kit residencial incluido. Costo mensual $150k (Ideal para compartir con 5 vecinos).")
            
        # Botón de WhatsApp
        mensaje = f"Hola Manuel Prada! Me interesa el {modelo_sel} por un valor de ${datos['precio']:,.0f}. Solicito visita técnica."
        wa_url = f"https://wa.me/573012428215?text={urllib.parse.quote(mensaje)}"
        st.markdown(f'''<a href="{wa_url}" target="_blank">
            <button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold; font-size:16px; cursor:pointer;">
                🟢 RESERVAR CITA TÉCNICA
            </button></a>''', unsafe_allow_html=True)

with t2:
    st.markdown("## 📑 ¿Por qué elegir el Sistema Híbrido Ferrotek?")
    st.write("El ladrillo tradicional y las placas de yeso son cosa del pasado. Ferrotek ofrece:")
    st.write("- **Espesor de 6cm:** Ganas espacio real en tu lote.")
    st.write("- **Estructura Steel Framing:** Acero galvanizado que no se pudre ni se quiebra.")
    st.write("- **Acabado de Roca:** Paredes sólidas de ferrocemento de alta densidad.")
    

with t3:
    if "6x12" in modelo_sel:
        st.markdown("### 📐 Distribución Lote 6x12 (Ideal para Colombia)")
        st.code("""
        FRENTE: 6.00m | FONDO: 12.00m
        ________________________________________________
        | PATIO (2m) | ALCOBA 2 (3.5m) | ALCOBA 1 (3.5m)|
        |------------|-----------------|----------------|
        | BAÑO (1.5) | COCINA/ROPAS    | SALA-COMEDOR   |
        ------------------------------------------------
        JARDÍN FRONTAL | ACCESO SMART
        """)
        

with t4:
    st.header("👷 Manual para el Constructor")
    st.video("https://www.youtube.com/watch?v=FjS68XzVp-0")