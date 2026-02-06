import streamlit as st
import pandas as pd
import math
import os
from fpdf import FPDF
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN GENERAL
# ==========================================
st.set_page_config(page_title="Ferrotek | Suite Empresarial V8", page_icon="🏗️", layout="wide")

# ==========================================
# 2. MÓDULO FÁBRICA (NORMA V8.0)
# ==========================================
DENSIDAD = {'cemento': 1.50, 'arena': 1.60, 'cal': 0.55, 'zeolita': 0.90}

def calcular_produccion_lote(tipo_mezcla, cantidad_bultos_30kg_meta):
    """Calcula los kilos exactos de cada insumo según la receta."""
    insumos = {}
    peso_total = cantidad_bultos_30kg_meta * 30
    
    if "Mezcla A (Estructural)" in tipo_mezcla: 
        # Batch 100: Fórmula Industrial por porcentaje de peso
        factor = peso_total / 100.0
        insumos = {
            'cemento_kg': 29.5 * factor,
            'arena_kg': 66.5 * factor,
            'carbonato_kg': 4.5 * factor,
            'fibras_kg': 0.1 * factor,
            'cal_kg': 0, 'zeolita_kg': 0
        }
    elif "Mezcla B (Piel de Roca)" in tipo_mezcla: 
        # Fórmula Volumétrica 1:3:3 (Cemento:Arena:Cal)
        # Calculamos volumen total y luego peso por densidad
        peso_unidad_volumen = (1 * 1.50) + (3 * 1.60) + (3 * 0.55) # Densidad combinada aprox
        unidades = peso_total / peso_unidad_volumen
        insumos = {
            'cemento_kg': units * 1 * 1.50,
            'arena_kg': units * 3 * 1.60,
            'cal_kg': units * 3 * 0.55,
            'carbonato_kg': 0, 'zeolita_kg': 0
        }
    elif "Mezcla T (Térmica)" in tipo_mezcla:
        # Fórmula con Zeolita
        peso_unidad_volumen = (1 * 1.50) + (2 * 0.55) + (3 * 0.90)
        unidades = peso_total / peso_unidad_volumen
        insumos = {
            'cemento_kg': units * 1 * 1.50,
            'cal_kg': units * 2 * 0.55,
            'zeolita_kg': units * 3 * 0.90,
            'arena_kg': 0, 'carbonato_kg': 0
        }
    return insumos

# ==========================================
# 3. MOTOR DE COSTOS (CEREBRO DEL SISTEMA)
# ==========================================
def calcular_proyecto(input_data, linea_negocio="general", incluye_acabados=True):
    P = st.session_state['precios_reales']
    margen = st.session_state['margen'] / 100
    
    # ---------------------------------------
    # LÍNEA DOMOS (Con Murete 0.80m)
    # ---------------------------------------
    if linea_negocio == "domo":
        ancho = input_data['ancho']
        fondo = input_data['fondo']
        
        # Geometría
        altura_murete = 0.80
        radio = ancho / 2.0
        altura_total = altura_murete + radio
        
        # Perímetro de la sección (La "U" invertida)
        perimetro_arco = math.pi * radio
        perimetro_muros = altura_murete * 2
        perimetro_total = perimetro_arco + perimetro_muros
        
        # Áreas
        area_envolvente = perimetro_total * fondo
        area_timpanos = (math.pi * (radio**2)) + (2 * ancho * altura_murete)
        area_total_m2 = area_envolvente + area_timpanos
        
        # Estructura Metálica (Arcos cada 60cm + Tímpanos)
        num_arcos = math.ceil(fondo / 0.60) + 1
        ml_perfileria = (num_arcos * perimetro_total) + (area_timpanos * 3.5)
        
        # Costos Materiales
        costo_mat = (
            (ml_perfileria * P['perfil_pgc90_ml']) +
            (area_total_m2 * 2.1 * P['malla_5mm_m2']) + # Doble malla
            (area_total_m2 * 0.04 * P['cemento_gris_50kg']) + # Aprox mortero
            (area_total_m2 * 4000) # Tornillería
        )
        
        costo_mo = math.ceil(ancho * fondo / 2.0) * P['dia_cuadrilla']
        costo_acab = (ancho * fondo * P.get('valor_acabados_vis_m2', 350000)) if incluye_acabados else 0
        
        total = costo_mat + costo_mo + costo_acab
        return {
            "precio": total / (1 - margen),
            "utilidad": (total / (1 - margen)) - total,
            "geo": {"h": altura_total, "area": area_total_m2},
            "desglose": {"mat": costo_mat, "mo": costo_mo}
        }

    # ---------------------------------------
    # LÍNEA MUROS (Sencillo vs Doble)
    # ---------------------------------------
    elif linea_negocio == "muro":
        ml = input_data['ml']
        altura = input_data['altura']
        tipo = input_data['tipo']
        area = ml * altura
        
        # Factores según tipo
        if "Doble" in tipo:
            factor_mat = 1.8  # Doble cara, doble malla, núcleo
            factor_mo = 1.5   # Más lento
        else:
            factor_mat = 1.0  # Sencillo
            factor_mo = 1.0
            
        costo_mat_base = (
            (area * 1.5 * P['perfil_pgc90_ml']) +
            (area * 2.1 * P['malla_5mm_m2']) +
            (area * 0.04 * P['cemento_gris_50kg'])
        ) * factor_mat
        
        # Cimentación (Viga Cinta)
        costo_cim = (ml * 0.20 * 0.25) * 350000 
        
        costo_mo = (area / 5.0 * P['dia_cuadrilla']) * factor_mo
        
        total = costo_mat_base + costo_cim + costo_mo
        return {
            "precio": total / (1 - margen),
            "utilidad": (total / (1 - margen)) - total,
            "desglose": {"mat": costo_mat_base + costo_cim, "mo": costo_mo}
        }

    # ---------------------------------------
    # LÍNEA CASA (Tradicional vs Serie M)
    # ---------------------------------------
    elif linea_negocio == "casa":
        area = input_data['area']
        estilo = input_data.get('estilo', 'Tradicional')
        
        # Factores de Diseño
        if estilo == 'Tradicional':
            fac_muros = 2.8 # Más muros internos
            fac_techo = 1.4 # Pendiente fuerte + Aleros
            costo_teja = 55000 # Teja PVC Colonial (Más cara)
            tipo_teja = "Teja PVC Colonial"
        else: # Serie M
            fac_muros = 2.6 # Optimizado
            fac_techo = 1.2 # Techo oculto
            costo_teja = 45000 # Teja PVC Termoacústica
            tipo_teja = "Teja PVC Termoacústica"

        costo_muros = area * fac_muros * 65000
        costo_cubierta = area * fac_techo * (P['perfil_pgc90_ml']*1.2 + costo_teja)
        costo_losa = area * 0.10 * 450000
        
        costo_mo = area * P['dia_cuadrilla'] # 1 día cuadrilla por m2 aprox global
        costo_acab = (area * P['valor_acabados_m2']) if incluye_acabados else 0
        
        total = costo_muros + costo_cubierta + costo_losa + costo_mo + costo_acab
        
        return {
            "precio": total / (1 - margen),
            "utilidad": (total / (1 - margen)) - total,
            "desglose": {"mat": costo_muros + costo_cubierta + costo_losa, "mo": costo_mo},
            "specs": {"teja": tipo_teja, "muros": f"Factor {fac_muros}"}
        }

    # ---------------------------------------
    # LÍNEA AGUA (Estanques)
    # ---------------------------------------
    elif linea_negocio == "agua":
        vol = input_data['vol']
        altura = 1.5
        radio = math.sqrt(vol / (math.pi * altura))
        area_muros = 2 * math.pi * radio * altura
        
        costo_mat = (area_muros * 4 * P['malla_5mm_m2']) + (area_muros * 0.06 * 450000) + 200000
        costo_mo = (area_muros / 2.0) * P['dia_cuadrilla']
        
        total = costo_mat + costo_mo
        return {
            "precio": total / (1 - margen),
            "utilidad": (total / (1 - margen)) - total,
            "desglose": {"mat": costo_mat, "mo": costo_mo}
        }

    return {"precio": 0}

# ==========================================
# 4. GENERADOR DE DOCUMENTOS (PDFs)
# ==========================================
class PDFDossier(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16); self.cell(0, 10, 'FERROTEK S.A.S - SUITE EMPRESARIAL', 0, 1, 'C')
        self.set_font('Arial', 'I', 10); self.cell(0, 10, 'Ingeniería Unibody & Construcción Monolítica', 0, 1, 'C'); self.ln(5)
    def footer(self):
        self.set_y(-15); self.set_font('Arial', 'I', 8); self.set_text_color(128)
        self.cell(0, 10, 'Ferrotek S.A.S - Innovación Colombiana', 0, 0, 'C')

def generar_catalogo_inteligente(tipo="master"):
    pdf = PDFDossier(); pdf.add_page()
    pdf.set_font('Arial', 'B', 24); pdf.set_text_color(0, 51, 102)
    titulo = "PORTAFOLIO GENERAL" if tipo == "master" else f"LINEA: {tipo.upper()}"
    pdf.cell(0, 20, titulo, 0, 1, 'C')
    pdf.set_font('Arial', 'I', 14); pdf.set_text_color(100)
    pdf.cell(0, 10, 'Sistema Constructivo Industrializado', 0, 1, 'C'); pdf.ln(10)
    pdf.set_text_color(0)
    
    # Contenido Dinámico según lo que pida el usuario
    if tipo == "master" or tipo == "casas":
        pdf.set_fill_color(230); pdf.rect(10, pdf.get_y(), 190, 10, 'F'); pdf.set_xy(10, pdf.get_y())
        pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, "LINEA VIVIENDA (2 ESTILOS)", 0, 1)
        pdf.set_font('Arial', '', 11)
        pdf.multi_cell(0, 6, "1. SERIE M (MODERNA): Cubos minimalistas, techo oculto, máxima eficiencia.\n2. SERIE TRADICIONAL: Techo a dos aguas (PVC Colonial), aleros y estética clásica.\nAmbas con la tecnología Ferrotek sismo-resistente.")
        pdf.ln(5)

    if tipo == "master" or tipo == "muros":
        pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, "LINEA MUROS", 0, 1)
        pdf.set_font('Arial', '', 11); pdf.multi_cell(0, 6, "Cerramientos perimetrales y fachadas térmicas.")
        pdf.ln(5)
        
    if tipo == "master" or tipo == "domos":
        pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, "LINEA DOMOS", 0, 1)
        pdf.set_font('Arial', '', 11); pdf.multi_cell(0, 6, "Bóvedas evolutivas con murete de 80cm para máxima altura.")
        pdf.ln(5)

    return bytes(pdf.output(dest='S'))

def generar_pdf_cotizacion(cliente, proyecto, datos, desc):
    pdf = PDFDossier(); pdf.add_page(); pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Cliente: {cliente} | Fecha: {datetime.now().strftime('%d/%m/%Y')}", 0, 1)
    pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, f"COTIZACION: {proyecto}", 0, 1)
    pdf.set_font('Arial', '', 11); pdf.multi_cell(0, 6, desc); pdf.ln(5)
    pdf.set_font('Arial', 'B', 16); pdf.cell(0, 15, f"INVERSION TOTAL: ${datos['precio']:,.0f}", 0, 1)
    return bytes(pdf.output(dest='S'))

# ==========================================
# 5. BARRA LATERAL (ACCESO SEGURO)
# ==========================================
with st.sidebar:
    st.markdown("### Acceso Corporativo")
    pwd = st.text_input("Clave de Acceso:", type="password", help="Solo personal autorizado")
    
    defaults = {
        'cemento_gris_50kg': 29500, 'cal_hidratada_25kg': 25000, 'arena_rio_m3': 98000, 
        'malla_5mm_m2': 28000, 'perfil_pgc90_ml': 18500, 'dia_cuadrilla': 250000, 
        'valor_acabados_m2': 450000, 'valor_acabados_vis_m2': 350000, 'aislante_m2': 12000 
    }
    if 'precios_reales' not in st.session_state: st.session_state['precios_reales'] = defaults
    if 'margen' not in st.session_state: st.session_state['margen'] = 30
    
    es_admin = (pwd == "ferrotek2026")
    if es_admin:
        st.success("🔓 Modo Gerente Activo")
        st.session_state['margen'] = st.slider("Margen Utilidad %", 10, 60, 30)
        with st.expander("Costos Base Insumos"):
            st.session_state['precios_reales'] = st.data_editor(st.session_state['precios_reales'], key="p_edit")
    else:
        st.caption("Ferrotek S.A.S © 2026 | Sistema de Gestión V8.0")

# ==========================================
# 6. INTERFAZ GRÁFICA (VISTAS)
# ==========================================
if 'view' not in st.session_state: st.session_state.view = 'home'
def set_view(name): st.session_state.view = name

# --- VISTA HOME ---
if st.session_state.view == 'home':
    st.title("🏗️ FERROTEK: Soluciones Industrializadas")
    
    st.markdown("### 📂 Centro de Documentación")
    col_d1, col_d2 = st.columns(2)
    with col_d1: 
        st.download_button("📘 Portafolio General (Master)", generar_catalogo_inteligente("master"), "Ferrotek_Master.pdf", "application/pdf", use_container_width=True)
    with col_d2: 
        st.download_button("📄 Brochure Casas (Tradicional + M)", generar_catalogo_inteligente("casas"), "Ferrotek_Casas.pdf", "application/pdf", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 🚀 Herramientas de Cotización")
    c1, c2, c3, c4 = st.columns(4)
    with c1: 
        st.subheader("🧱 Muros")
        st.button("Cotizar Muros", on_click=lambda: set_view('muros'), use_container_width=True)
    with c2: 
        st.subheader("🏠 Casas")
        st.button("Cotizar Casas", on_click=lambda: set_view('casas'), use_container_width=True)
    with c3: 
        st.subheader("🌾 Domos")
        st.button("Cotizar Domos", on_click=lambda: set_view('domos'), use_container_width=True)
    with c4: 
        st.subheader("💧 Agua")
        st.button("Cotizar Tanques", on_click=lambda: set_view('agua'), use_container_width=True)

# --- VISTA CASAS (COMPLETA) ---
elif st.session_state.view == 'casas':
    st.button("⬅️ Volver", on_click=lambda: set_view('home')); st.header("🏠 Línea Vivienda Ferrotek")
    c1, c2 = st.columns(2)
    with c1:
        # SELECTOR DE ESTILO (LA CLAVE DE LA VENTA)
        estilo = st.radio("Estilo Arquitectónico:", ["Tradicional (Techo 2 Aguas)", "Serie M (Moderna/Cúbica)"])
        
        if "Tradicional" in estilo:
            mod_sel = st.selectbox("Modelo Tradicional:", ["Modelo A (30m2 - 1 Hab)", "Modelo B (48m2 - 2 Hab)", "Modelo C (70m2 - 3 Hab)"])
            area = int(mod_sel.split()[2].replace("m2","").replace("(",""))
            tipo_estilo = "Tradicional"
            st.info("ℹ️ Techo PVC Colonial y Distribución Clásica.")
        else:
            mod_sel = st.selectbox("Modelo Serie M:", ["Modelo M-2 (45m2 - Minimalista)", "Modelo M-3 (70m2 - Familiar)"])
            area = 45 if "M-2" in mod_sel else 70
            tipo_estilo = "Serie M"
            st.success("ℹ️ Diseño Cúbico, Optimización Modular, Wet-Wall.")

        full = st.checkbox("Llave en Mano (Acabados)", True)
        data = calcular_proyecto({'area':area, 'estilo':tipo_estilo}, "casa", full)
        
        st.metric("Inversión Estimada", f"${data['precio']:,.0f}")
        
        if st.text_input("Cliente:"): 
            desc = f"Casa {mod_sel}. Estilo: {tipo_estilo}. Área: {area}m2. Cubierta: {data['specs']['teja']}."
            st.download_button("PDF Cotización", generar_pdf_cotizacion(st.session_state.get('c_name','Cli'), f"Casa {tipo_estilo}", data, desc), "cot.pdf")
            
    with c2:
        if "Tradicional" in estilo:
            try: st.image("vis_familiar.png", caption="Estilo Tradicional", use_container_width=True)
            except: pass
        else:
            img = "vivienda_suite.png" if "M-2" in mod_sel else "vivienda_master.png"
            try: st.image(img, caption=f"Estilo Serie M", use_container_width=True)
            except: pass

# --- VISTA MUROS ---
elif st.session_state.view == 'muros':
    st.button("⬅️ Volver", on_click=lambda: set_view('home')); st.header("🧱 Línea Muros")
    c1, c2 = st.columns(2)
    with c1:
        tipo = st.radio("Tipo:", ["Tipo 2 (Sencillo)", "Tipo 1 (Doble)"])
        ml = st.number_input("Largo (m):", 10.0); alt = st.number_input("Alto (m):", 2.2)
        data = calcular_proyecto({'ml':ml, 'altura':alt, 'tipo':tipo}, "muro")
        st.metric("Inversión", f"${data['precio']:,.0f}")
        if st.text_input("Cliente:"): 
            st.download_button("PDF Cotización", generar_pdf_cotizacion("Cli", "Muro", data, f"Muro {tipo} {ml}x{alt}m"), "cot.pdf")
    with c2: 
        st.info("Sencillo: Cerramiento 5cm. Doble: Fachada Térmica.")
        try: st.image("muro_perimetral.png", use_container_width=True)
        except: pass

# --- VISTA DOMOS ---
elif st.session_state.view == 'domos':
    st.button("⬅️ Volver", on_click=lambda: set_view('home')); st.header("🌾 Línea Domos")
    c1, c2 = st.columns(2)
    with c1:
        uso = st.selectbox("Uso:", ["Vivienda (6m)", "Garage (3.8m)", "Personalizado"])
        w = 6.0 if "Vivienda" in uso else 3.8 if "Garage" in uso else 5.0
        ancho = st.number_input("Frente:", 2.0, 15.0, w); fondo = st.number_input("Fondo:", 3.0, 50.0, 10.0)
        full = st.checkbox("Acabados", True if "Vivienda" in uso else False)
        data = calcular_proyecto({'ancho':ancho, 'fondo':fondo}, "domo", full)
        st.metric("Inversión", f"${data['precio']:,.0f}")
        st.success(f"Altura Central: {data['geo']['h']:.2f}m")
        st.caption("Incluye muretes base de 0.80m.")
        if st.text_input("Cliente:"): 
            st.download_button("PDF Cotización", generar_pdf_cotizacion("Cli", "Domo", data, f"Domo {ancho}x{fondo}m"), "cot.pdf")
    with c2: 
        try: st.image("Loft_rural.png", use_container_width=True)
        except: pass

# --- VISTA AGUA ---
elif st.session_state.view == 'agua':
    st.button("⬅️ Volver", on_click=lambda: set_view('home')); st.header("💧 Línea Agua")
    c1, c2 = st.columns(2)
    with c1:
        vol = st.slider("Litros:", 1000, 20000, 5000, 1000)
        data = calcular_proyecto({'vol': vol/1000}, "agua")
        st.metric("Precio", f"${data['precio']:,.0f}")
        if st.text_input("Cliente:"): 
            st.download_button("PDF Cotización", generar_pdf_cotizacion("Cli", "Tanque", data, f"Tanque {vol}L"), "cot.pdf")

# --- FÁBRICA ---
elif st.session_state.view == 'fabrica':
    st.button("⬅️ Volver"); st.header("🏭 Fábrica")
    if not es_admin: st.warning("Restringido"); st.stop()
    tipo = st.selectbox("Mezcla:", ["Mezcla A (Estructural)", "Mezcla B (Piel de Roca)", "Mezcla T (Térmica)"])
    qty = st.number_input("Bultos:", 1); res = calcular_produccion_lote(tipo, qty)
    st.table(pd.DataFrame(list(res.items()), columns=["Insumo", "Kg"]))