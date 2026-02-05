import streamlit as st
import pandas as pd
import math
import os
from fpdf import FPDF
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURACIÓN GENERAL
# ==========================================
st.set_page_config(page_title="Ferrotek | Construcción Inteligente", page_icon="🏗️", layout="wide")

# ==========================================
# 🧪 MÓDULO FÁBRICA (PRIVADO)
# ==========================================
DENSIDAD = {'cemento': 1.50, 'arena': 1.60, 'cal': 0.55}

def calcular_produccion_lote(tipo_mezcla, cantidad_bultos_30kg):
    peso_meta = cantidad_bultos_30kg * 30
    insumos = {}
    if "Relleno" in tipo_mezcla: 
        peso_vol = (3 * DENSIDAD['arena']) + (1 * DENSIDAD['cemento'])
        if peso_vol > 0:
            units = peso_meta / peso_vol
            insumos = {'arena_L': units*3, 'cemento_L': units*1, 'cal_L': 0}
    elif "Acabado" in tipo_mezcla: 
        peso_vol = (3 * DENSIDAD['arena']) + (3 * DENSIDAD['cal']) + (1 * DENSIDAD['cemento'])
        if peso_vol > 0:
            units = peso_meta / peso_vol
            insumos = {'arena_L': units*3, 'cal_L': units*3, 'cemento_L': units*1}
    if not insumos: return {}
    insumos['arena_kg'] = insumos['arena_L'] * DENSIDAD['arena']
    insumos['cemento_kg'] = insumos['cemento_L'] * DENSIDAD['cemento']
    insumos['cal_kg'] = insumos.get('cal_L', 0) * DENSIDAD['cal']
    return insumos

# ==========================================
# 🧠 MOTOR DE COSTOS
# ==========================================
def calcular_proyecto(input_data, tipo="general", tiene_gotero=False):
    P = st.session_state['precios_reales']
    margen = st.session_state['margen'] / 100
    
    # --- CASO VIS BÓVEDA ---
    if tipo == "boveda_vis":
        ancho = input_data['ancho']; fondo = input_data['fondo']
        radio = ancho / 2.0 
        long_arco = math.pi * radio 
        area_total_envolvente = (long_arco * fondo) + ((math.pi * (radio**2)))
        
        # Estructura
        total_pgc = ((math.ceil(fondo/0.6)+1) * long_arco) + (((math.pi*(radio**2))) * 3.5)
        
        # Envolvente
        costo_mat = (
            (total_pgc * P['perfil_c18_ml']) +
            ((area_total_envolvente * 0.05 * 1.05 * 350 / 50) * P['cemento_gris_50kg']) + 
            (area_total_envolvente * 0.05 * 1.05 * 1.1 * P['arena_rio_m3']) + 
            (area_total_envolvente * 2.1 * P['malla_5mm_m2']) + 
            ((long_arco * fondo) * P.get('aislante_m2', 12000)) + 
            (area_total_envolvente * 5000) 
        )
        costo_mo = math.ceil((ancho*fondo)/2.5) * P['dia_cuadrilla']
        costo_acabados = (ancho*fondo) * P.get('valor_acabados_vis_m2', 350000)
        
        costo_total = costo_mat + costo_mo + costo_acabados
        return {"precio": costo_total/(1-margen), "utilidad": (costo_total/(1-margen))-costo_total}

    # --- CASO GENERAL ---
    else:
        area_m2 = input_data['area']; ml_muro_val = input_data.get('ml', 0)
        espesor = 0.06 if tipo=="estanque" else 0.055 if tipo=="vivienda" else 0.04
        fac_malla = 1.6 if tipo=="vivienda" else 2.1
        varilla = area_m2*1.5 if tipo=="estanque" else 0
        
        vol = area_m2 * espesor * 1.05
        costo_mat = (
            (math.ceil(vol*0.7*8.5) * P['cemento_gris_50kg']) +
            (math.ceil(vol*0.3*10) * P['cal_hidratada_25kg']) +
            (vol*1.1 * P['arena_rio_m3']) +
            (area_m2 * fac_malla * P['malla_5mm_m2']) +
            (area_m2 * 0.9 * P['perfil_c18_ml']) +
            (math.ceil(varilla) * P.get('varilla_refuerzo_6m', 24000)) +
            (area_m2 * 5000)
        )
        mo = math.ceil(area_m2/P.get('rendimiento_dia', 4.5)) * P['dia_cuadrilla']
        extra = ml_muro_val * 25000 if tiene_gotero else 0
        acabados = (area_m2/3.5 * P.get('valor_acabados_m2', 450000)) if tipo=="vivienda" else 0
        
        total = costo_mat + mo + extra + acabados
        return {"precio": total/(1-margen), "utilidad": (total/(1-margen))-total}

# ==========================================
# 📄 PDF GENERATOR
# ==========================================
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16); self.cell(0, 10, 'FERROTEK S.A.S', 0, 1, 'C')
        self.set_font('Arial', 'I', 10); self.cell(0, 10, 'Ingeniería Unibody', 0, 1, 'C'); self.ln(10)

def generar_pdf(cliente, obra, datos, desc):
    pdf = PDF(); pdf.add_page(); pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Cliente: {cliente} | Fecha: {datetime.now().strftime('%d/%m/%Y')}", 0, 1)
    pdf.cell(0, 10, f"Proyecto: {obra}", 0, 1); pdf.ln(5)
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "ESPECIFICACIONES", 0, 1)
    pdf.set_font('Arial', '', 11); pdf.multi_cell(0, 7, desc); pdf.ln(5)
    pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, f"INVERSIÓN: ${datos['precio']:,.0f}", 0, 1)
    return bytes(pdf.output(dest='S'))

# ==========================================
# 🎛️ SIDEBAR (LOGIN)
# ==========================================
with st.sidebar:
    st.title("🎛️ Administración")
    pwd = st.text_input("Contraseña:", type="password")
    
    defaults = {
        'cemento_gris_50kg': 29500, 'cal_hidratada_25kg': 25000, 'arena_rio_m3': 98000, 
        'malla_5mm_m2': 28000, 'perfil_c18_ml': 11500, 'varilla_refuerzo_6m': 24000,
        'aislante_m2': 12000, 'dia_cuadrilla': 250000, 'rendimiento_dia': 4.5,
        'valor_acabados_m2': 450000, 'valor_acabados_vis_m2': 350000 
    }
    if 'precios_reales' not in st.session_state: st.session_state['precios_reales'] = defaults
    if 'margen' not in st.session_state: st.session_state['margen'] = 30
    
    es_admin = (pwd == "ferrotek2026")
    if es_admin:
        st.success("🔓 Sesión Gerente")
        st.session_state['margen'] = st.slider("Utilidad %", 0, 60, st.session_state['margen'])
        with st.expander("Costos Insumos"):
            st.session_state['precios_reales'] = st.data_editor(st.session_state['precios_reales'], key="p_edit")
    else:
        st.info("Ingrese contraseña para ver costos reales y fábrica.")

if 'view' not in st.session_state: st.session_state.view = 'home'
def set_view(name): st.session_state.view = name

# ==========================================
# 🎨 VISTA 1: HOME (VITRINA VENDEDORA - RESTAURADA)
# ==========================================
if st.session_state.view == 'home':
    st.title("🏗️ FERROTEK: Ingeniería Monolítica")
    st.subheader("La evolución inteligente de la construcción tradicional.")
    st.markdown("---")

    # --- AQUÍ ESTÁ LA MAGIA QUE HABÍAMOS PERDIDO ---
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("### 🛡️ Sismo-Resistente")
        st.write("Estructura continua (Unibody) con alma de acero. Mayor seguridad estructural que la mampostería suelta.")
    with c2:
        st.success("### 🌡️ Confort Térmico")
        st.write("Doble membrana aislante. Ambientes más frescos de forma natural, reduciendo el calor radiante.")
    with c3:
        st.warning("### 💰 Mínimo Mantenimiento")
        st.write("Acabado Piel de Roca impermeable. Una superficie pétrea que elimina el gasto de pintura por años.")
    # ------------------------------------------------

    st.markdown("---")
    st.subheader("🚀 ¿Qué desea cotizar hoy?")
    
    b1, b2, b3, b4 = st.columns(4)
    with b1: st.button("🛡️ Muros de Cerramiento", on_click=lambda: set_view('muros'), use_container_width=True)
    with b2: st.button("🏠 Viviendas Unibody", on_click=lambda: set_view('viviendas'), use_container_width=True)
    with b3: st.button("🌾 Bóveda Campesina / VIS", on_click=lambda: set_view('vis_boveda'), use_container_width=True)
    with b4: 
        # Botón Fábrica (Protegido en la vista, accesible el botón)
        st.button("🏭 Planta de Producción", on_click=lambda: set_view('fabrica'), use_container_width=True)
    
    st.markdown("---")
    st.subheader("📸 Galería de Proyectos")
    imgs = [f for f in os.listdir('.') if f.endswith(('.png','.jpg'))]
    if imgs:
        c = st.columns(3)
        for i, f in enumerate(imgs): c[i%3].image(f, caption=f, use_container_width=True)

# ... (todo el código anterior sigue igual) ...

# ==========================================
# 🎨 VISTAS DE COTIZACIÓN
# ==========================================
elif st.session_state.view == 'vis_boveda':
    st.button("⬅️ Volver a Vitrina", on_click=lambda: set_view('home'))
    st.header("🌾 Bóveda Evolutiva (Manual V.2)")
    c1, c2 = st.columns([1, 1.5]) 
    with c1:
        distribucion = st.radio("Distribución Interna:", ["Open Loft (Turista)", "Familiar (2 Hab)"])
        ancho = st.number_input("Frente (m):", 6.0, disabled=True)
        fondo = st.number_input("Fondo (m):", 10.0)
        data = calcular_proyecto({'ancho': ancho, 'fondo': fondo}, tipo="boveda_vis")
        st.metric("Inversión Total", f"${data['precio']:,.0f}")
        st.info("✅ Piel de Roca Impermeable (Sin mantenimientos)")
        if st.text_input("Cliente:"):
            desc = f"Modelo VIS Bóveda. Distribución: {distribucion}. Estructura curva Ferrotek."
            st.download_button("Descargar Cotización", generar_pdf("Cliente", "Bóveda 60m2", data, desc), "cotizacion.pdf")
    with c2:
        if distribucion == "Open Loft (Turista)":
            # --- CAMBIO AQUÍ: USAMOS TU NUEVA FOTO ---
            try: st.image("Loft_rural.png", caption="Modelo Rural - Ideal Ecoturismo", use_container_width=True)
            except: st.warning("Sube la foto 'Loft_rural.png'")
        else:
            # Mantenemos la isométrica para el familiar para mostrar la distribución
            try: st.image("vis_familiar.png", caption="Mezzanine Dividido - Familiar", use_container_width=True)
            except: st.warning("Sube la foto 'vis_familiar.png'")

# ... (el resto de las vistas siguen igual) ...

elif st.session_state.view == 'muros':
    st.button("⬅️ Volver a Vitrina", on_click=lambda: set_view('home')); st.header("🛡️ Cotizador Muros")
    ml = st.number_input("Metros Lineales:", 50.0); got = st.checkbox("Gotero", True)
    data = calcular_proyecto({'area': ml*2.2, 'ml': ml}, tipo="muro", tiene_gotero=got)
    st.metric("Precio", f"${data['precio']:,.0f}")
    if st.text_input("Cliente:"): st.download_button("PDF", generar_pdf("Cliente", "Muro", data, "Muro Perimetral Ferrotek"), "muro.pdf")

elif st.session_state.view == 'viviendas':
    st.button("⬅️ Volver a Vitrina", on_click=lambda: set_view('home')); st.header("🏠 Cotizador Vivienda")
    mod = st.selectbox("Modelo", ["Suite 30m2", "Familiar 54m2"])
    area = int(mod.split()[1].replace("m2","")) * 3.5
    data = calcular_proyecto({'area': area}, tipo="vivienda")
    st.metric("Valor", f"${data['precio']:,.0f}")
    if st.text_input("Cliente:"): st.download_button("PDF", generar_pdf("Cliente", mod, data, "Vivienda Unibody"), "casa.pdf")

# ==========================================
# 🏭 VISTA FÁBRICA (PROTEGIDA)
# ==========================================
elif st.session_state.view == 'fabrica':
    st.button("⬅️ Volver a Vitrina", on_click=lambda: set_view('home')); st.header("🏭 Fábrica (Acceso Restringido)")
    
    # 🔒 CANDADO DIGITAL
    if not es_admin:
        st.error("⛔ ACCESO DENEGADO")
        st.warning("Esta sección contiene Secretos Industriales (Fórmulas de Mezcla y Manual Técnico).")
        st.info("Por favor inicie sesión como Administrador en la barra lateral.")
    else:
        st.success("🔓 Modo Ingeniero Activo")
        tipo = st.radio("Mezcla:", ["Relleno", "Acabado"]); qty = st.number_input("Bultos:", 10)
        res = calcular_produccion_lote(tipo, qty)
        if res: st.write(res)