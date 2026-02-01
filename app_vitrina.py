import streamlit as st
import core_planos
import os
import math
import json

st.set_page_config(page_title="Ferrotek | Catálogo Digital", page_icon="🏡", layout="wide")

# ==========================================
# 💾 GESTIÓN DE DATOS (BASE DE DATOS)
# ==========================================
ARCHIVO_DB = 'ferrotek_db.json'

DB_INICIAL = {
    "config": {
        "margen_utilidad": 0.30 
    },
    "precios": {
        'cemento': 28000,     'arena': 90000,       'triturado': 110000,
        'varilla': 24000,     'malla_electro': 180000, 
        'malla_zaranda': 280000, 
        
        # ESTRUCTURA STEEL FRAMING (Precios Mercado Aprox)
        'perfil_phr_c': 65000, # Paral Estructural
        'perfil_phr_u': 55000, # Canal/Pista Base
        
        'alambron': 8000,     'cal': 15000,
        
        'mo_m2_casa': 220000, 
        'mo_m2_tanque': 75000, 
        'mo_m2_boveda': 85000,
        
        'kit_techo_m2': 110000, 
        'kit_vidrios_peq': 3200000, 'kit_vidrios_med': 4800000, 'kit_vidrios_gra': 7500000,
        'kit_impermeabilizante': 450000,
        'kit_fachada_boveda': 2500000, 
        'kit_hidraulico_estanque': 300000
    },
    "receta_mezcla": {
        "muro_cemento_arena": 3.0,   
        "muro_cal_factor": 0.5,      
        "piso_cemento_arena": 2.0,   
        "piso_triturado": 3.0
    }
}

def cargar_db():
    if not os.path.exists(ARCHIVO_DB):
        with open(ARCHIVO_DB, 'w') as f:
            json.dump(DB_INICIAL, f)
        return DB_INICIAL
    with open(ARCHIVO_DB, 'r') as f:
        data = json.load(f)
        if "config" not in data: data["config"] = DB_INICIAL["config"]
        # Asegurar claves nuevas
        if "perfil_phr_u" not in data["precios"]: data["precios"]["perfil_phr_u"] = 55000
        return data

def guardar_db(nueva_db):
    with open(ARCHIVO_DB, 'w') as f:
        json.dump(nueva_db, f)

if 'db' not in st.session_state:
    st.session_state['db'] = cargar_db()

# ==========================================
# 🧠 CEREBRO DE CÁLCULO
# ==========================================
AREA_PANEL_ELECTRO = 13.0 
AREA_ROLLO_ZARANDA = 40.0 

def calcular_materiales(tipo, dimension, db):
    p = db['precios']
    r = db['receta_mezcla']
    cfg = db.get('config', {'margen_utilidad': 0.30})
    margen = cfg['margen_utilidad']
    
    lista_cantidades = {}
    lista_visible = {}    
    costo_extra = 0

    # --- A. CASAS (STEEL FRAMING HÍBRIDO) ---
    if tipo == "vivienda":
        ALTURA_SOLERA = 2.40 
        
        if dimension == 1:
            nombre = "Modelo 1: Loft (35m²)"
            area_piso = 35; perimetro_muros = 24
            kit_vidrio = p['kit_vidrios_peq']
        elif dimension == 2:
            nombre = "Modelo 2: Familiar (65m²)"
            area_piso = 65; perimetro_muros = 36
            kit_vidrio = p['kit_vidrios_med']
        elif dimension == 3:
            nombre = "Modelo 3: Hacienda (110m²)"
            area_piso = 110; perimetro_muros = 55
            ALTURA_SOLERA = 2.60
            kit_vidrio = p['kit_vidrios_gra']

        # 1. ESTRUCTURA (C + U)
        # Perfiles U (Pistas): Piso y Techo
        metros_U = perimetro_muros * 2 
        cant_U = math.ceil(metros_U / 6.0)

        # Perfiles C (Parales): Verticales cada 50cm
        num_parales = math.ceil(perimetro_muros / 0.50)
        verticales_C = math.ceil(num_parales / 2) # 1 barra 6m = 2 parales 3m
        
        # Blocking / Dinteles (Refuerzos horizontales con C)
        metros_blocking = perimetro_muros 
        blocking_C = math.ceil(metros_blocking / 6.0)
        
        total_C = verticales_C + blocking_C

        # 2. CONCRETO (Losa y Muros)
        vol_piso = area_piso * 0.08
        cem_piso = vol_piso * 7.5; arena_piso = vol_piso * 0.55; trit_piso = vol_piso * 0.85
        
        area_muros = perimetro_muros * ALTURA_SOLERA
        vol_muros = area_muros * 0.05
        cem_muro = vol_muros * 9.0; arena_muro = vol_muros * 1.1

        cem_tot = int(cem_piso + cem_muro)
        lista_cantidades = {
            'cemento': cem_tot,
            'arena': round(arena_piso + arena_muro, 1),
            'triturado': round(trit_piso, 1),
            'malla_electro': math.ceil((area_muros * 1.1 + area_piso) / AREA_PANEL_ELECTRO),
            'malla_zaranda': math.ceil((area_muros * 2 * 1.1) / AREA_ROLLO_ZARANDA),
            'perfil_phr_c': total_C, 
            'perfil_phr_u': cant_U,
            'varillas': int(perimetro_muros), # Refuerzos esquineros o anclajes
            'alambron': int(cem_tot * 0.3)
        }
        
        info = {
            'info_nombre': nombre, 
            'info_desc': f"Sistema Híbrido: Estructura PHR Galvanizada + Piel Ferrocemento. Altura {ALTURA_SOLERA}m.",
            'info_area': area_piso, 'info_altura': ALTURA_SOLERA
        }
        costo_extra = (area_piso * p['mo_m2_casa']) + (area_piso * p['kit_techo_m2']) + kit_vidrio

    # --- B. ESTANQUES ---
    elif tipo == "estanque":
        diametro = dimension; altura = 1.2; radio = diametro / 2
        area_total = (math.pi * (radio**2)) + ((math.pi * diametro) * altura)

        vol_tot = area_total * 0.06 
        cem = int(vol_tot * 8.5)
        if cem < 4: cem = 4
        
        lista_cantidades = {
            'cemento': cem, 
            'cal': int(cem * r['muro_cal_factor']), 
            'arena': round(vol_tot * 1.0, 1),
            'malla_electro': math.ceil((area_total * 1.15) / AREA_PANEL_ELECTRO),  
            'malla_zaranda': math.ceil((area_total * 2 * 1.15) / AREA_ROLLO_ZARANDA),   
            'varillas': int((math.pi * diametro * 7) / 6), 
            'alambron': int(cem * 0.4) 
        }
        info = {
            'info_nombre': f"Estanque Circular (Ø {diametro}m)", 
            'info_desc': "Técnica Sándwich: Malla Zaranda + Electro. Refuerzo Varilla.",
            'info_area': round(math.pi * radio**2, 1), 'info_altura': altura, 'info_volumen': int(math.pi * radio**2 * altura * 1000)
        }
        costo_extra = (area_total * p['mo_m2_tanque']) + p['kit_hidraulico_estanque']

    # --- C. BÓVEDAS ---
    elif tipo == "boveda":
        largo = dimension; ancho = 3.5
        perimetro_arco = 7.1 
        area_ferrocemento = (perimetro_arco * largo) + 14 
        area_piso = ancho * largo
        
        # Arcos estructurales (Curvados o facetados) usando Perfil C
        num_arcos = math.ceil(largo / 0.50) + 1 
        perfiles_arcos_C = math.ceil(num_arcos * 1.3) 
        
        # Largueros de unión (Perfil C)
        metros_largueros = largo * 5
        perfiles_largueros_C = math.ceil(metros_largueros / 6)
        
        # Base/Riel en el piso (Perfil U)
        metros_base = largo * 2
        perfiles_base_U = math.ceil(metros_base / 6)

        vol_tot = (area_piso * 0.07) + (area_ferrocemento * 0.035)
        cem = int(vol_tot * 8.5)

        lista_cantidades = {
            'cemento': cem, 
            'cal': int(cem * r['muro_cal_factor']),
            'arena': round(vol_tot, 1),
            'malla_electro': math.ceil(area_ferrocemento / AREA_PANEL_ELECTRO),
            'malla_zaranda': math.ceil((area_ferrocemento * 2) / AREA_ROLLO_ZARANDA),
            'perfil_phr_c': perfiles_arcos_C + perfiles_largueros_C,
            'perfil_phr_u': perfiles_base_U,
            'alambron': int(cem * 0.3)
        }
        info = {
            'info_nombre': f"Bóveda Glamping ({largo}m)", 
            'info_desc': f"Arcos PHR C Estructurales + Bases PHR U.",
            'info_area': round(area_piso, 1), 'info_altura': 2.8
        }
        costo_extra = (area_ferrocemento * p['mo_m2_boveda']) + p['kit_impermeabilizante'] + p['kit_fachada_boveda']

    # CÁLCULO FINAL
    costo_mat = sum([v * p[k] for k, v in lista_cantidades.items() if k in p and isinstance(v, (int, float))])
    costo_total = costo_mat + costo_extra
    precio_venta = costo_total / (1 - margen)
    
    # --- DICCIONARIO DE NOMBRES TÉCNICOS IDÓNEOS ---
    nombres_legibles = {
        'cemento': 'Cemento Gris Estructural (Bultos 50kg)',
        'arena': 'Arena de Río Lavada (m³)',
        'triturado': 'Triturado 1/2" (m³)',
        'malla_electro': 'Malla Electrosoldada 4mm 15x15 (Paneles)',
        'malla_zaranda': 'Malla Zaranda Galv. 1/2" Cal.22 (Rollos)',
        'perfil_phr_c': 'Perfil PHR C Galv 89x40 Cal 20 (6m)',  # <--- DESCRIPCIÓN TÉCNICA
        'perfil_phr_u': 'Perfil PHR U (Pista) 90x40 Cal 22 (6m)', # <--- DESCRIPCIÓN TÉCNICA
        'varillas': 'Varilla Corrugada 1/2" N-40 (6m)',
        'alambron': 'Alambrón Negro (kg)',
        'cal': 'Cal Hidratada (Bultos 25kg)'
    }
    
    for k, v in lista_cantidades.items():
        nombre_bonito = nombres_legibles.get(k, k)
        lista_visible[nombre_bonito] = v

    return {**info, 'lista_compras_interna': lista_cantidades, 'lista_visible': lista_visible, 
            'costo_directo': round(costo_total, -3), 'precio_venta': round(precio_venta, -3), 'margen_usado': margen}

# ==========================================
# 🎨 INTERFAZ GRÁFICA
# ==========================================
st.markdown("""<style>
    .big-font { font-size:28px !important; color: #154360; font-weight: 800;}
    .sub-font { font-size:18px !important; color: #555; font-style: italic;}
    .price-tag { font-size:42px; color: #27AE60; font-weight: bold; background-color: #eafaf1; padding: 10px; border-radius: 8px; text-align: center;}
    .card { background-color: #ffffff; padding: 25px; border-radius: 15px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 6px solid #2980B9;}
</style>""", unsafe_allow_html=True)

# LOGIN ADMIN
es_admin = False
with st.sidebar:
    st.image("https://via.placeholder.com/300x100.png?text=FERROTEK+Admin", use_container_width=True)
    with st.expander("🔒 Zona Administrativa"):
        if st.text_input("Contraseña:", type="password") == "ferrotek2026":
            es_admin = True
            st.success("Modo Admin Activo")
    
    st.markdown("---")
    CAT_CASAS, CAT_ESTANQUES, CAT_BOVEDAS = "🏠 Casas Modulares", "🐟 Estanques Piscícolas", "⛺ Bóvedas Glamping"
    categoria = st.radio("Línea de Negocio:", [CAT_CASAS, CAT_ESTANQUES, CAT_BOVEDAS])

    datos = None; mod_sel=0; dim_sel=0
    
    if categoria == CAT_CASAS:
        mod_sel = st.selectbox("Modelo:", [1, 2, 3], format_func=lambda x: f"Modelo {x}")
        datos = calcular_materiales("vivienda", mod_sel, st.session_state['db'])
    elif categoria == CAT_ESTANQUES:
        dim_sel = st.select_slider("Diámetro (m):", [1, 2, 4, 8, 10, 12], value=8)
        datos = calcular_materiales("estanque", dim_sel, st.session_state['db'])
    elif categoria == CAT_BOVEDAS:
        dim_sel = st.radio("Profundidad (m):", [3, 6])
        datos = calcular_materiales("boveda", dim_sel, st.session_state['db'])

# VISTAS
pestanas = ["👁️ Vitrina Comercial"]
if es_admin: pestanas += ["💰 Costos", "⚙️ Precios/Receta", "📈 Margen Ganancia"]
tabs = st.tabs(pestanas)

# 1. VITRINA
with tabs[0]:
    if datos:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown(f'<p class="big-font">{datos.get("info_nombre")}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="sub-font">{datos.get("info_desc")}</p>', unsafe_allow_html=True)
            
            img_base = f"render_modelo{mod_sel}" if categoria == CAT_CASAS else (f"render_boveda{dim_sel}" if categoria == CAT_BOVEDAS else "render_estanque")
            found_img = False
            for ext in [".png", ".jpg", ".jpeg"]:
                if os.path.exists(img_base + ext):
                    st.image(img_base + ext, use_container_width=True); found_img=True; break
            
            if not found_img: 
                st.warning(f"⚠️ FOTO PENDIENTE: Carga '{img_base}.png'")

            if categoria != CAT_ESTANQUES:
                st.caption("📐 Esquema de Distribución")
                try: st.markdown(core_planos.dibujar_planta(mod_sel if categoria == CAT_CASAS else 1), unsafe_allow_html=True)
                except: pass

        with c2:
            st.markdown(f'<div class="card"><h3 style="text-align:center;">Precio Llave en Mano</h3><div class="price-tag">${datos["precio_venta"]:,.0f}</div></div>', unsafe_allow_html=True)
            m1, m2 = st.columns(2)
            val = datos.get('info_volumen', datos.get('info_area'))
            unit = 'L' if categoria==CAT_ESTANQUES else 'm²'
            m1.metric("Área/Vol", f"{val} {unit}")
            
            if categoria == CAT_CASAS:
                precio_m2 = datos["precio_venta"] / datos["info_area"]
                st.caption(f"Valor aprox por m²: ${precio_m2:,.0f} COP")
            
            if categoria != CAT_ESTANQUES:
                st.info(f"🏗️ **Estructura:** Perfil PHR C + U Galvanizado (Sistema Híbrido).")

# 2. ADMIN
if es_admin:
    with tabs[1]:
        st.subheader("📊 Estructura de Costos")
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Costo Directo", f"${datos['costo_directo']:,.0f}")
        utilidad = datos['precio_venta'] - datos['costo_directo']
        kpi2.metric("Utilidad Bruta", f"${utilidad:,.0f}")
        kpi3.metric("Margen Actual", f"{int(datos['margen_usado']*100)}%")
        
        st.write("📋 **Lista de Materiales (Especificaciones Técnicas):**")
        st.dataframe(datos['lista_visible'], width=600) # Un poco más ancho para que quepan los nombres

    with tabs[2]:
        st.subheader("⚙️ Configuración")
        col_p, col_r = st.columns(2)
        with col_p:
            st.write("**Precios Unitarios:**")
            new_prices = st.data_editor(st.session_state['db']['precios'], height=400)
        with col_r:
            st.write("**🧪 Receta:**")
            new_receta = st.data_editor(st.session_state['db']['receta_mezcla'])
        
        if st.button("💾 Guardar Cambios"):
            st.session_state['db']['precios'] = new_prices
            st.session_state['db']['receta_mezcla'] = new_receta
            guardar_db(st.session_state['db'])
            st.success("¡Guardado!")
            st.rerun()

    with tabs[3]:
        st.subheader("📈 Estrategia de Precios")
        current_margen = st.session_state['db'].get('config', {}).get('margen_utilidad', 0.30)
        new_margen = st.slider("Margen de Utilidad (%)", 10, 60, int(current_margen*100)) / 100.0
        
        c1, c2 = st.columns(2)
        costo = datos['costo_directo']
        precio_simulado = costo / (1 - new_margen)
        c1.metric("Precio Simulado", f"${precio_simulado:,.0f}")
        
        if st.button("💾 Actualizar Margen"):
            if "config" not in st.session_state['db']: st.session_state['db']["config"] = {}
            st.session_state['db']["config"]["margen_utilidad"] = new_margen
            guardar_db(st.session_state['db'])
            st.success("Margen actualizado")
            st.rerun()