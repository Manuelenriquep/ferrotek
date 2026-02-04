import streamlit as st
import pandas as pd
import math
import os
from fpdf import FPDF
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURACIÓN GENERAL
# ==========================================
st.set_page_config(page_title="Ferrotek | ERP Técnico 2024", page_icon="🏗️", layout="wide")

# ==========================================
# 🧪 MÓDULO FÁBRICA (NORMA 2024)
# ==========================================
# Densidades aproximadas para conversión Vol -> Peso
DENSIDAD = {
    'cemento': 1.50, # kg/L
    'arena': 1.60,   # kg/L
    'cal': 0.55,     # kg/L (Liviana)
    'carbonato': 0.80 # kg/L (Polvo fino)
}

def calcular_produccion_lote(tipo_mezcla, cantidad_baldes_resultado):
    """
    Calcula la receta basada en el Cap. 3 del Manual Ferrotek.
    Entrada: Cuántos baldes de mezcla final quieres preparar.
    """
    insumos = {}
    
    # 3.1 MEZCLA A: RELLENO ESTRUCTURAL (Base)
    # Proporción: 1 Cemento : 3 Arena (1.5 Gruesa + 1.5 Fina)
    # Aditivo: 15% Carbonato respecto al peso del Cemento
    if "A (Base)" in tipo_mezcla:
        # Por cada unidad de volumen de Cemento, van 3 de Arena.
        # Volumen Total Partes = 1 + 3 = 4 partes
        factor = cantidad_baldes_resultado / 4 
        
        insumos['cemento_L'] = factor * 1
        insumos['arena_L']   = factor * 3
        insumos['cal_L']     = 0
        
        # Carbonato: 15% del PESO del cemento
        peso_cemento = insumos['cemento_L'] * DENSIDAD['cemento']
        peso_carbonato = peso_cemento * 0.15
        insumos['carbonato_kg'] = peso_carbonato

    # 3.2 MEZCLA B: ACABADO HIDROFÓBICO (Piel)
    # Proporción: 1 Cemento : 3 Arena : 3 Cal
    elif "B (Piel)" in tipo_mezcla:
        # Volumen Total Partes = 1 + 3 + 3 = 7 partes
        factor = cantidad_baldes_resultado / 7
        
        insumos['cemento_L'] = factor * 1
        insumos['arena_L']   = factor * 3
        insumos['cal_L']     = factor * 3
        insumos['carbonato_kg'] = 0

    # Conversión a Kilos para Bodega
    insumos['arena_kg']   = insumos.get('arena_L', 0) * DENSIDAD['arena']
    insumos['cemento_kg'] = insumos.get('cemento_L', 0) * DENSIDAD['cemento']
    insumos['cal_kg']     = insumos.get('cal_L', 0) * DENSIDAD['cal']
    
    return insumos

# ==========================================
# 🧠 MOTOR DE COSTOS (NORMA TÉCNICA)
# ==========================================
def calcular_proyecto(area_m2, ml_muro=0, tipo="general", altura_muro=2.44):
    P = st.session_state['precios_reales']
    margen = st.session_state['margen'] / 100
    
    # --- 1. ESTRUCTURA METÁLICA (SEGÚN ANEXO) ---
    # Perfil PGC (Montantes): Separación máx 40cm 
    # Cantidad: (Metros lineales muro / 0.40) + Arranque
    # Pero el manual da un consumo estimado de 3.5 ml/m2 
    # Usaremos el valor del manual para ser precisos.
    consumo_pgc = area_m2 * 3.5
    
    # Perfil PGU (Soleras): 1.2 ml/m2 
    consumo_pgu = area_m2 * 1.2
    
    # Tornillos T2 Wafer: 25 un/m2 
    consumo_tornillos = math.ceil(area_m2 * 25)

    # --- 2. PIEL Y REFUERZO ---
    # Malla Electrosoldada: 1.10 m2/m2 (10% traslape) 
    consumo_malla_elec = area_m2 * 1.10
    
    # Malla Zaranda: 1.25 m2/m2 (Traslape óptimo 15cm) 
    consumo_malla_zar = area_m2 * 1.25

    # --- 3. MORTEROS (VOLÚMENES EXACTOS CAP. 2) ---
    # Espesor Capa 1: 1.5 cm [cite: 43] -> 0.015 m3/m2
    vol_capa_A = area_m2 * 0.015 
    
    # Espesor Capa 2: 1.5 cm [cite: 46] -> 0.015 m3/m2
    vol_capa_B = area_m2 * 0.015
    
    # --- 4. DESGLOSE DE MATERIALES (RECETAS) ---
    
    # Mezcla A (1:3 + Carbonato)
    # Rendimiento aprox: 1 m3 mortero 1:3 consume ~450kg cemento y 1.1m3 arena
    cemento_A_kg = vol_capa_A * 450
    arena_A_m3   = vol_capa_A * 1.1
    carbonato_kg = cemento_A_kg * 0.15 # 
    
    # Mezcla B (1:3:3)
    # Rendimiento aprox: 1 m3 mortero 1:3:3 consume ~300kg cemento, 300kg cal, 1m3 arena
    cemento_B_kg = vol_capa_B * 300
    cal_B_kg     = vol_capa_B * 300 # La cal pesa menos, pero ocupa mucho volumen
    arena_B_m3   = vol_capa_B * 1.0

    # TOTALES DE COMPRA
    total_cemento_kg = cemento_A_kg + cemento_B_kg
    total_arena_m3   = arena_A_m3 + arena_B_m3
    total_cal_kg     = cal_B_kg
    total_carb_kg    = carbonato_kg
    
    # --- 5. COSTOS DIRECTOS ---
    costo_mat = (
        (consumo_pgc * P['perfil_pgc_ml']) +
        (consumo_pgu * P['perfil_pgu_ml']) +
        (consumo_tornillos * P['tornillo_t2_un']) +
        (consumo_malla_elec * P['malla_electro_m2']) +
        (consumo_malla_zar * P['malla_zaranda_m2']) +
        ((total_cemento_kg / 50) * P['cemento_50kg']) +
        ((total_cal_kg / 25) * P['cal_25kg']) +
        (total_arena_m3 * P['arena_m3']) +
        (total_carb_kg * P['carbonato_kg']) +
        (area_m2 * 2000) # Agua y varios menores
    )
    
    rendimiento = P.get('rendimiento_dia', 4.5)
    dias = math.ceil(area_m2 / rendimiento)
    costo_mo = dias * P['dia_cuadrilla']
    
    costo_total = costo_mat + costo_mo
    precio_venta = costo_total / (1 - margen)
    
    return {
        "precio": precio_venta, 
        "costo": costo_total,
        "utilidad": precio_venta - costo_total,
        "cantidades": {
            "PGC (ml)": consumo_pgc,
            "PGU (ml)": consumo_pgu,
            "Tornillos (un)": consumo_tornillos,
            "Cemento (kg)": total_cemento_kg,
            "Carbonato (kg)": total_carb_kg
        }
    }

# ==========================================
# 🎛️ SIDEBAR (PRECIOS ACTUALIZADOS)
# ==========================================
with st.sidebar:
    st.title("🎛️ Panel Gerente")
    pwd = st.text_input("Contraseña:", type="password")
    
    # Precios Base (¡AGREGAMOS LOS NUEVOS!)
    defaults = {
        'cemento_50kg': 29500, 
        'cal_25kg': 25000, 
        'arena_m3': 98000, 
        'carbonato_kg': 1500, # Precio estimado del carbonato/filler
        'malla_electro_m2': 18000, 
        'malla_zaranda_m2': 5000,
        'perfil_pgc_ml': 18000, # Perfil estructural 90/60
        'perfil_pgu_ml': 14000, 
        'tornillo_t2_un': 80,   # Precio unitario tornillo
        'dia_cuadrilla': 250000, 
        'rendimiento_dia': 4.5
    }
    if 'precios_reales' not in st.session_state: st.session_state['precios_reales'] = defaults
    if 'margen' not in st.session_state: st.session_state['margen'] = 30
    
    es_admin = (pwd == "ferrotek2026")
    if es_admin:
        st.success("🔓 Admin Activo")
        margen = st.slider("Utilidad %", 0, 60, st.session_state['margen'])
        st.session_state['margen'] = margen
        with st.expander("Costos Insumos"):
            edited = st.data_editor(st.session_state['precios_reales'], key="p_edit", num_rows="fixed")
            st.session_state['precios_reales'] = edited

if 'view' not in st.session_state: st.session_state.view = 'home'
def set_view(name): st.session_state.view = name

# ==========================================
# 🎨 VISTA 1: HOME
# ==========================================
if st.session_state.view == 'home':
    st.title("🏗️ FERROTEK: Sistema Híbrido 2024")
    st.subheader("Acero Galvanizado + Ferrocemento de Alta Resistencia")
    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.info("### 📘 Manual Técnico")
        st.write("Cálculos basados en Norma 2024: PGC @ 40cm, Mezclas Densificadas con Carbonato.")
    with c2:
        st.success("### 🧪 Dosificación Exacta")
        st.write("Recetas separadas para Relleno Estructural y Piel Hidrofóbica.")

    st.markdown("---")
    
    b1, b2 = st.columns(2)
    with b1: 
        if st.button("🛡️ Cotizar Muros (Norma)", key="nav_m", use_container_width=True): set_view('muros')
    with b2:
        if st.button("🏭 Fábrica de Mezclas", key="nav_f", use_container_width=True): set_view('fabrica')

# ==========================================
# 🎨 VISTA 2: MUROS
# ==========================================
elif st.session_state.view == 'muros':
    st.button("⬅️ Inicio", on_click=lambda: set_view('home'))
    st.header("🛡️ Cotizador Muros (Estándar 2024)")
    
    ml = st.number_input("Metros Lineales:", value=10.0)
    altura = st.number_input("Altura (m):", value=2.44)
    area = ml * altura
    
    data = calcular_proyecto(area)
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Precio Venta", f"${data['precio']:,.0f}")
        st.caption(f"Área: {area:.1f} m2")
        
        if es_admin:
            st.warning("📊 INSUMOS REQUERIDOS (Manual Cap. 4)")
            st.write(f"- Perfil PGC: {data['cantidades']['PGC (ml)']:.1f} ml")
            st.write(f"- Perfil PGU: {data['cantidades']['PGU (ml)']:.1f} ml")
            st.write(f"- Tornillos T2: {data['cantidades']['Tornillos (un)']} un")
            st.write(f"- Carbonato Calcio: {data['cantidades']['Carbonato (kg)']:.1f} kg")

# ==========================================
# 🎨 VISTA 3: FÁBRICA
# ==========================================
elif st.session_state.view == 'fabrica':
    st.button("⬅️ Inicio", on_click=lambda: set_view('home'))
    st.header("🏭 Dosificación de Mezclas (Cap. 3)")
    
    tipo = st.selectbox("Tipo de Mezcla:", ["A (Base) - Relleno Estructural", "B (Piel) - Acabado Hidrofóbico"])
    baldes = st.number_input("¿Cuántos baldes de mezcla necesita?", value=10)
    
    res = calcular_produccion_lote(tipo, baldes)
    
    st.markdown("### 📋 Receta:")
    c1, c2, c3 = st.columns(3)
    c1.metric("Cemento", f"{res.get('cemento_L',0):.1f}", "Baldes")
    c2.metric("Arena", f"{res.get('arena_L',0):.1f}", "Baldes")
    
    if res.get('cal_L', 0) > 0:
        c3.metric("Cal", f"{res.get('cal_L',0):.1f}", "Baldes")
    elif res.get('carbonato_kg', 0) > 0:
        c3.metric("Carbonato", f"{res.get('carbonato_kg',0):.2f}", "KILOS (Pesados)")
        st.info("⚠️ OJO: El Carbonato se pesa, no se mide en baldes.")

    st.caption("Nota: 'Arena' incluye 50% Gruesa y 50% Fina según Cap 3.1.")