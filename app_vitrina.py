import streamlit as st
import pandas as pd
import math
from fpdf import FPDF
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURACIÓN Y ESTILOS
# ==========================================
st.set_page_config(page_title="Ferrotek | Ingeniería Unibody", page_icon="🏗️", layout="wide")

# ==========================================
# 📄 CLASE GENERADORA DE PDF (DOCUMENTO FORMAL)
# ==========================================
class PDF(FPDF):
    def header(self):
        # Logo o Título
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'FERROTEK S.A.S - COTIZACION FORMAL', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, 'Ingeniería Unibody & Construcción Monolítica', 0, 1, 'C')
        self.line(10, 30, 200, 30)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()} | Generado por Software Ferrotek | Floridablanca, Santander', 0, 0, 'C')

def generar_pdf_cotizacion(cliente, tipo_obra, area, precio_total, detalles_logistica, desglose_costos):
    pdf = PDF()
    pdf.add_page()
    
    # 1. Datos Generales
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Fecha de Emisión: {datetime.now().strftime('%d/%m/%Y')}", 0, 1)
    pdf.cell(0, 10, f"Cliente / Referencia: {cliente}", 0, 1)
    pdf.cell(0, 10, f"Tipo de Proyecto: {tipo_obra}", 0, 1)
    pdf.ln(5)
    
    # 2. El Objeto del Contrato (Alcance)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "1. ALCANCE TÉCNICO & ESPECIFICACIONES", 0, 1)
    pdf.set_font('Arial', '', 11)
    texto_alcance = (
        f"Suministro de tecnología y ejecución de obra para {area} m2 (aprox) de sistema Unibody Ferrotek. "
        "Incluye estructura de alma de acero (malla 5mm), morteros de alta densidad (Piel de Roca) "
        "y acabados pulidos naturales impermeables. No requiere pintura posterior."
    )
    pdf.multi_cell(0, 6, texto_alcance)
    pdf.ln(5)

    # 3. Logística de Materiales
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "2. LOGÍSTICA DE MATERIALES (SISTEMA DE BULTOS)", 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 7, f"- Bultos Tipo R (Núcleo Estructural): {detalles_logistica.get('bultos_r', 0)} Unidades", 0, 1)
    pdf.cell(0, 7, f"- Bultos Tipo A (Acabado Piel de Roca): {detalles_logistica.get('bultos_a', 0)} Unidades", 0, 1)
    pdf.multi_cell(0, 6, "Nota: El material se entrega en bultos de 30kg predosificados, listos para mezcla en sitio.")
    pdf.ln(5)

    # 4. Inversión Económica
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "3. VALOR DE LA INVERSIÓN (ESTIMADO)", 0, 1)
    pdf.set_font('Arial', '', 11)
    
    # Tabla simple de costos
    pdf.cell(100, 8, "Concepto", 1)
    pdf.cell(50, 8, "Valor", 1, 1)
    
    pdf.cell(100, 8, "Costo Directo Materiales", 1)
    pdf.cell(50, 8, f"${desglose_costos['mat']:,.0f}", 1, 1)
    
    pdf.cell(100, 8, "Mano de Obra Especializada", 1)
    pdf.cell(50, 8, f"${desglose_costos['mo']:,.0f}", 1, 1)
    
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(100, 8, "TOTAL PROYECTADO", 1)
    pdf.cell(50, 8, f"${precio_total:,.0f}", 1, 1)
    pdf.ln(10)

    # 5. Cláusulas de Cierre (Sin Cabos Sueltos)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 10, "CONDICIONES COMERCIALES Y EXCLUSIONES:", 0, 1)
    pdf.set_font('Arial', '', 9)
    condiciones = (
        "- VALIDEZ: Esta cotización tiene una vigencia de 15 días calendario.\n"
        "- EXCLUSIONES: El valor no incluye adecuación de terreno (loteo), transporte a zonas de difícil acceso, "
        "licencias de construcción, ni viáticos de cuadrilla fuera del área metropolitana.\n"
        "- REQUISITO: Se requiere visita técnica previa para confirmar condiciones del suelo.\n"
        "- FORMA DE PAGO: 50% Anticipo para materiales, 50% contra avance de obra."
    )
    pdf.multi_cell(0, 5, condiciones)
    
    pdf.ln(15)
    pdf.cell(0, 10, "__________________________", 0, 1, 'C')
    pdf.cell(0, 5, "Manuel E. Prada Forero", 0, 1, 'C')
    pdf.cell(0, 5, "Dirección General - FERROTEK", 0, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')

# ==========================================
# 🧠 CÓDIGO PRINCIPAL (INTEGRADO)
# ==========================================

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🔐 Acceso Corporativo")
    pwd = st.text_input("Contraseña:", type="password")
    
    default_prices = {
        'cemento_gris_50kg': 29500, 'cal_hidratada_10kg': 18500, 'arena_rio_m3': 98000,
        'malla_5mm_m2': 28000, 'malla_gallinero_m2': 8500, 'perfil_c18_ml': 11500,
        'dia_cuadrilla': 250000, 'rendimiento_dia': 4.0
    }

    if pwd == "ferrotek2026":
        st.success("Modo Editor Activo")
        if 'precios_reales' not in st.session_state: st.session_state['precios_reales'] = default_prices
        edited_prices = st.data_editor(st.session_state['precios_reales'], key="editor")
        st.session_state['precios_reales'] = edited_prices
        margen = st.slider("Margen Utilidad %:", 10, 50, 30)
        st.session_state['margen'] = margen / 100
    else:
        if 'precios_reales' not in st.session_state: st.session_state['precios_reales'] = default_prices
        if 'margen' not in st.session_state: st.session_state['margen'] = 0.30

if 'view' not in st.session_state: st.session_state.view = 'home'
def set_view(name): st.session_state.view = name

# --- MOTOR CÁLCULO ---
def calcular_proyecto(area_m2, tipo="muro"):
    P = st.session_state['precios_reales']
    
    # Consumos Base
    q_cemento = math.ceil(area_m2 * 0.04 * 1.05 * 8) 
    costo_mat = (q_cemento * P['cemento_gris_50kg']) + (area_m2 * 2.1 * P['malla_5mm_m2']) + (area_m2 * 10000) # + Arenas/Cal est
    
    dias = math.ceil(area_m2 / P.get('rendimiento_dia', 4.0))
    costo_mo = dias * P.get('dia_cuadrilla', 250000)
    
    precio_venta = (costo_mat + costo_mo) / (1 - st.session_state['margen'])
    
    # Bultos para Logística (Aprox)
    total_bultos_30kg = math.ceil((area_m2 * 0.04 * 10) / 16 * 30)
    bultos_r = math.ceil(total_bultos_30kg * 0.7)
    bultos_a = math.ceil(total_bultos_30kg * 0.3)

    return {
        "mat": costo_mat, "mo": costo_mo, "total": precio_venta,
        "logistica": {"bultos_r": bultos_r, "bultos_a": bultos_a}
    }

# --- VISTAS ---
if st.session_state.view == 'home':
    st.title("🏗️ FERROTEK: Soluciones Monolíticas")
    col1, col2 = st.columns(2)
    with col1: 
        if st.button("🛡️ Cotizar Muros", key="nav_muros"): set_view('muros')
    with col2: 
        if st.button("🏠 Cotizar Casas", key="nav_casas"): set_view('viviendas')

elif st.session_state.view == 'viviendas':
    st.button("⬅️ Volver", on_click=lambda: set_view('home'))
    st.header("🏠 Cotizador Formal de Vivienda")
    
    modelo = st.selectbox("Seleccione Modelo", ["Suite 30m2", "Familiar 54m2", "Máster 84m2"])
    area = int(modelo.split()[1].replace("m2","")) * 3.5 # Area desarrollada muros
    
    datos = calcular_proyecto(area, "vivienda")
    precio_final = datos['total'] * 1.25 # Factor Acabados Internos
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Precio Referencia", f"${precio_final:,.0f}")
        st.write("---")
        
        # INPUT PARA PDF
        cliente_nombre = st.text_input("Nombre del Cliente (Para Cotización):")
        
        if cliente_nombre:
            pdf_bytes = generar_pdf_cotizacion(
                cliente=cliente_nombre,
                tipo_obra=f"Vivienda Unibody - {modelo}",
                area=area,
                precio_total=precio_final,
                detalles_logistica=datos['logistica'],
                desglose_costos={"mat": datos['mat']*1.25, "mo": datos['mo']*1.25}
            )
            st.download_button(
                label="📄 Descargar Cotización Formal (PDF)",
                data=pdf_bytes,
                file_name=f"Cotizacion_Ferrotek_{cliente_nombre}.pdf",
                mime="application/pdf"
            )
        else:
            st.info("👆 Ingrese el nombre del cliente para habilitar la descarga del PDF.")

    with c2:
        img_map = {"Suite 30m2": "render_modelo1.png", "Familiar 54m2": "render_modelo2.png", "Máster 84m2": "render_modelo3.png"}
        try: st.image(img_map[modelo])
        except: st.warning("Imagen no disponible")

elif st.session_state.view == 'muros':
    st.button("⬅️ Volver", on_click=lambda: set_view('home'))
    st.header("🛡️ Cotizador Formal de Muros")
    ml = st.number_input("Metros Lineales", value=50.0)
    area = ml * 2.2
    
    datos = calcular_proyecto(area, "muro")
    
    st.metric("Inversión Estimada", f"${datos['total']:,.0f}")
    
    cliente_nombre = st.text_input("Nombre del Cliente:")
    if cliente_nombre:
        pdf_bytes = generar_pdf_cotizacion(
            cliente=cliente_nombre,
            tipo_obra=f"Muro Perimetral ({ml} ml)",
            area=area,
            precio_total=datos['total'],
            detalles_logistica=datos['logistica'],
            desglose_costos={"mat": datos['mat'], "mo": datos['mo']}
        )
        st.download_button(
            label="📄 Descargar Cotización Formal (PDF)",
            data=pdf_bytes,
            file_name=f"Cotizacion_Muros_{cliente_nombre}.pdf",
            mime="application/pdf"
        )