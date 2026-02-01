import streamlit as st
import core_planos
import os
import math
import json

st.set_page_config(page_title="Ferrotek | Catálogo 2026", page_icon="🏗️", layout="wide")

# ==========================================
# 💾 GESTIÓN DE DATOS
# ==========================================
ARCHIVO_DB = 'ferrotek_db.json'

DB_INICIAL = {
    "config": {
        "margen_utilidad": 0.30 
    },
    "precios": {
        'cemento': 28000,     'arena': 90000,       'triturado': 110000,
        'varilla': 24000,     
        'malla_electro': 210000, 
        'malla_zaranda': 280000, 
        
        'perfil_phr_c': 65000, 
        'perfil_phr_u': 55000, 
        'pintura_asfaltica': 45000, 
        'esmalte_negro': 70000,
        'vinilo_madera_m2': 55000, # <--- NUEVO: Precio m2 Vinilo PVC
        'pegante_boxer': 60000,    # <--- NUEVO: Galón de Boxer
        
        'alambron': 8000,     'cal': 15000,
        
        'mo_m2_casa': 220000, 
        'mo_m2_tanque': 75000, 
        'mo_m2_boveda': 85000,
        'mo_m2_muro': 45000, 
        
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
        # Actualización de precios nuevos si no existen
        if "vinilo_madera_m2" not in data["precios"]: data["precios"]["vinilo_madera_m2"] = 55000
        if "pegante_boxer" not in data["precios"]: data["precios"]["pegante_boxer"] = 60000
        if "esmalte_negro" not in data["precios"]: data["precios"]["esmalte_negro"] = 70000
        
        if data["precios"].get("mo_m2_muro") == 65000: data["precios"]["mo_m2_muro"] = 45000
        if data["precios"].get("malla_electro") == 180000: data["precios"]["malla_electro"] = 210000
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

def calcular_materiales(tipo, dimension, db, extra_param=None):
    p = db['precios']
    r = db['receta_mezcla']
    cfg = db.get('config', {'margen_utilidad': 0.30})
    margen = cfg['margen_utilidad']
    
    lista_cantidades = {}
    lista_visible = {}    
    costo_mo_total = 0
    costo_otros = 0
    dias_obra = 0
    info = {}

    # --- A. CASAS ---
    if tipo == "vivienda":
        # Extraer parámetros de acabado
        es_madera = (extra_param == "Tipo Cabaña (Perfiles Madera)") if extra_param else False
        
        ALTURA_SOLERA = 2.40 
        if dimension == 1:
            nombre = "Modelo 1: Loft (35m²)"; area_piso = 35; perimetro_muros = 24; kit_vidrio = p['kit_vidrios_peq']; dias_obra = 20
        elif dimension == 2:
            nombre = "Modelo 2: Familiar (65m²)"; area_piso = 65; perimetro_muros = 36; kit_vidrio = p['kit_vidrios_med']; dias_obra = 35
        elif dimension == 3:
            nombre = "Modelo 3: Hacienda (110m²)"; area_piso = 110; perimetro_muros = 55; ALTURA_SOLERA = 2.60; kit_vidrio = p['kit_vidrios_gra']; dias_obra = 50

        metros_U = perimetro_muros * 2; cant_U = math.ceil(metros_U / 6.0)
        num_parales = math.ceil(perimetro_muros / 0.50); verticales_C = math.ceil(num_parales / 2)
        metros_blocking = perimetro_muros; blocking_C = math.ceil(metros_blocking / 6.0)
        total_C = verticales_C + blocking_C

        vol_piso = area_piso * 0.08
        cem_piso = vol_piso * 7.5; arena_piso = vol_piso * 0.55; trit_piso = vol_piso * 0.85
        area_muros = perimetro_muros * ALTURA_SOLERA
        vol_muros = area_muros * 0.05
        cem_muro = vol_muros * 9.0; arena_muro = vol_muros * 1.1
        cem_tot = int(cem_piso + cem_muro)
        
        galones_asfalto = math.ceil(perimetro_muros / 15.0)
        
        # LÓGICA DE ACABADO ESTRUCTURAL
        galones_esmalte = 0
        m2_vinilo = 0
        galones_boxer = 0
        
        if es_madera:
            # 1 m2 de vinilo cubre aprox 11 ml de perfil (ancho 9cm). 
            # Total metros lineales de estructura visible (aprox 70% de verticales)
            metros_lineales_visibles = total_C * 6.0 * 0.7 
            m2_vinilo = math.ceil(metros_lineales_visibles * 0.09 * 1.1) # 10% desperdicio
            galones_boxer = math.ceil(m2_vinilo / 15.0) # 1 galon rinde 15m2 pegado
        else:
            # Pintura Negra
            galones_esmalte = math.ceil(total_C / 15.0)

        lista_cantidades = {
            'cemento': cem_tot, 'arena': round(arena_piso + arena_muro, 1), 'triturado': round(trit_piso, 1),
            'malla_electro': math.ceil((area_muros * 1.1 + area_piso) / AREA_PANEL_ELECTRO),
            'malla_zaranda': math.ceil((area_muros * 2 * 1.1) / AREA_ROLLO_ZARANDA),
            'perfil_phr_c': total_C, 'perfil_phr_u': cant_U,
            'pintura_asfaltica': galones_asfalto,
            'esmalte_negro': galones_esmalte,
            'vinilo_madera_m2': m2_vinilo,  # <--- NUEVO
            'pegante_boxer': galones_boxer, # <--- NUEVO
            'varillas': int(perimetro_muros), 'alambron': int(cem_tot * 0.3)
        }
        
        estilo = "Acabado Cabaña (Estructura Tipo Madera)" if es_madera else "Acabado Industrial (Estructura Negra)"
        info = {'info_nombre': nombre, 'info_desc': estilo, 'info_area': area_piso, 'info_altura': ALTURA_SOLERA}
        costo_mo_total = area_piso * p['mo_m2_casa']
        costo_otros = (area_piso * p['kit_techo_m2']) + kit_vidrio

    # --- B. ESTANQUES ---
    elif tipo == "estanque":
        diametro = dimension; altura = 1.2; radio = diametro / 2
        area_total = (math.pi * (radio**2)) + ((math.pi * diametro) * altura)
        vol_tot = area_total * 0.06; cem = int(vol_tot * 8.5); cem = 4 if cem < 4 else cem
        dias_obra = math.ceil(area_total / 5.0)
        
        lista_cantidades = {
            'cemento': cem, 'cal': int(cem * r['muro_cal_factor']), 'arena': round(vol_tot * 1.0, 1),
            'malla_electro': math.ceil((area_total * 1.15) / AREA_PANEL_ELECTRO),
            'malla_zaranda': math.ceil((area_total * 2 * 1.15) / AREA_ROLLO_ZARANDA),
            'varillas': int((math.pi * diametro * 7) / 6), 'alambron': int(cem * 0.4)
        }
        info = {'info_nombre': f"Estanque Circular (Ø {diametro}m)", 'info_desc': "Técnica Sándwich.", 'info_area': round(math.pi * radio**2, 1), 'info_altura': altura, 'info_volumen': int(math.pi * radio**2 * altura * 1000)}
        costo_mo_total = area_total * p['mo_m2_tanque']
        costo_otros = p['kit_hidraulico_estanque']

    # --- C. BÓVEDAS ---
    elif tipo == "boveda":
        largo = dimension; ancho = 3.5; perimetro_arco = 7.1 
        area_ferrocemento = (perimetro_arco * largo) + 14; area_piso = ancho * largo
        dias_obra = math.ceil(largo * 1.5)
        
        num_arcos = math.ceil(largo / 0.50) + 1; perfiles_arcos_C = math.ceil(num_arcos * 1.3)
        metros_largueros = largo * 5; perfiles_largueros_C = math.ceil(metros_largueros / 6)
        metros_base = largo * 2; perfiles_base_U = math.ceil(metros_base / 6)
        vol_tot = (area_piso * 0.07) + (area_ferrocemento * 0.035)
        cem = int(vol_tot * 8.5)
        galones_asfalto = math.ceil(metros_base / 15.0)

        lista_cantidades = {
            'cemento': cem, 'cal': int(cem * r['muro_cal_factor']), 'arena': round(vol_tot, 1),
            'malla_electro': math.ceil(area_ferrocemento / AREA_PANEL_ELECTRO),
            'malla_zaranda': math.ceil((area_ferrocemento * 2) / AREA_ROLLO_ZARANDA),
            'perfil_phr_c': perfiles_arcos_C + perfiles_largueros_C, 'perfil_phr_u': perfiles_base_U,
            'pintura_asfaltica': galones_asfalto,
            'alambron': int(cem * 0.3)
        }
        info = {'info_nombre': f"Bóveda Glamping ({largo}m)", 'info_desc': f"Arcos PHR C.", 'info_area': round(area_piso, 1), 'info_altura': 2.8}
        costo_mo_total = area_ferrocemento * p['mo_m2_boveda']
        costo_otros = p['kit_impermeabilizante'] + p['kit_fachada_boveda']

    # --- D. MUROS PERIMETRALES ---
    elif tipo == "cerramiento":
        largo = dimension
        altura = extra_param['h'] if extra_param else 2.20
        es_reforzado = (extra_param['tipo'] == "Reforzado (Doble Membrana)")
        distancia_postes = extra_param.get('distancia', 2.0)
        
        rendimiento_diario = 6.0 if es_reforzado else 10.0
        dias_obra = math.ceil(largo / rendimiento_diario)
        area_muro = largo * altura
        
        num_postes = math.ceil(largo / distancia_postes) + 1
        postes_por_barra = 2.0 if altura <= 2.30 else 1.0
        perfiles_postes = math.ceil(num_postes / postes_por_barra) 
        perfiles_U = math.ceil(largo / 6.0) if es_reforzado else 0
        
        factor_electro = 2.0 if es_reforzado else 1.0
        cant_electro = math.ceil((area_muro * factor_electro) / AREA_PANEL_ELECTRO)
        cant_zaranda = math.ceil((area_muro * 2) / AREA_ROLLO_ZARANDA)

        vol_dados = num_postes * (0.4 * 0.4 * 0.6) 
        cem_dados = vol_dados * 7.0; arena_dados = vol_dados * 0.6; trit_dados = vol_dados * 0.7
        espesor = 0.06 if es_reforzado else 0.05
        vol_mortero = area_muro * espesor
        cem_mortero = vol_mortero * 9.0; arena_mortero = vol_mortero * 1.1
        cem_tot = int(cem_dados + cem_mortero)
        
        galones_asfalto = math.ceil(num_postes / 25.0) 
        galones_esmalte = math.ceil(num_postes / 15.0) 

        lista_cantidades = {
            'cemento': cem_tot,
            'cal': int(cem_mortero * r['muro_cal_factor']),
            'arena': round(arena_dados + arena_mortero, 1),
            'triturado': round(trit_dados, 1),
            'malla_electro': cant_electro, 
            'malla_zaranda': cant_zaranda, 
            'perfil_phr_c': perfiles_postes,
            'perfil_phr_u': perfiles_U, 
            'pintura_asfaltica': galones_asfalto,
            'esmalte_negro': galones_esmalte,
            'alambron': int(cem_tot * 0.2)
        }
        
        desc_tipo = "Doble Membrana" if es_reforzado else "Sencillo (1 Malla)"
        info = {
            'info_nombre': f"Muro {largo} ML - {desc_tipo}", 
            'info_desc': f"Acabado Industrial (Negro Mate + Crema Natural).",
            'info_area': area_muro, 'info_altura': altura
        }
        costo_mo_total = area_muro * p['mo_m2_muro']
        costo_otros = 0

    # CÁLCULO FINAL
    costo_mat = sum([v * p[k] for k, v in lista_cantidades.items() if k in p and isinstance(v, (int, float))])
    costo_total = costo_mat + costo_mo_total + costo_otros
    precio_venta = costo_total / (1 - margen)
    
    nombres_legibles = {
        'cemento': 'Cemento Gris (Bultos)',
        'arena': 'Arena de Río (m³)',
        'triturado': 'Triturado 1/2 (m³)',
        'malla_electro': 'Malla Electrosoldada 5mm (Paneles)', 
        'malla_zaranda': 'Malla Zaranda Fina 5x5 (Rollos)',
        'perfil_phr_c': 'Perfil PHR C Galv 89x38 (6m)', 
        'perfil_phr_u': 'Perfil PHR U (Pista) 90x40 (6m)', 
        'pintura_asfaltica': 'Pintura Asfáltica (Cimentación)',
        'esmalte_negro': 'Esmalte Negro Mate (Acabado)',
        'vinilo_madera_m2': 'Vinilo PVC Tipo Madera (m²)', # <---
        'pegante_boxer': 'Pegante Boxer (Galones)',        # <---
        'varillas': 'Varilla Corrugada 1/2" (6m)',
        'alambron': 'Alambrón (kg)',
        'cal': 'Cal Hidratada (Bultos)'
    }
    
    for k, v in lista_cantidades.items():
        nombre_bonito = nombres_legibles.get(k, k)
        lista_visible[nombre_bonito] = v

    return {**info, 
            'lista_compras_interna': lista_cantidades, 
            'lista_visible': lista_visible, 
            'costo_materiales': round(costo_mat, -3),
            'costo_mano_obra': round(costo_mo_total, -3),
            'costo_otros': round(costo_otros, -3),
            'costo_total': round(costo_total, -3), 
            'precio_venta': round(precio_venta, -3), 
            'margen_usado': margen,
            'dias_estimados': dias_obra}

# ==========================================
# 🎨 INTERFAZ GRÁFICA
# ==========================================
st.markdown("""<style>
    .big-font { font-size:28px !important; color: #154360; font-weight: 800;}
    .sub-font { font-size:18px !important; color: #555; font-style: italic;}
    .price-tag { font-size:42px; color: #27AE60; font-weight: bold; background-color: #eafaf1; padding: 10px; border-radius: 8px; text-align: center;}
    .card { background-color: #ffffff; padding: 25px; border-radius: 15px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 6px solid #2980B9;}
    .metric-card { background-color: #f8f9fa; border: 1px solid #ddd; padding: 15px; border-radius: 5px; text-align:center;}
</style>""", unsafe_allow_html=True)

# LOGIN ADMIN
es_admin = False
with st.sidebar:
    st.title("🏗️ FERROTEK")
    st.caption("Catálogo Digital 2026")
    
    with st.expander("🔒 Zona Administrativa"):
        if st.text_input("Contraseña:", type="password") == "ferrotek2026":
            es_admin = True
            st.success("Modo Admin Activo")
    
    st.markdown("---")
    
    CAT_CASAS = "🏠 Casas Modulares"
    CAT_ESTANQUES = "🐟 Estanques Piscícolas"
    CAT_BOVEDAS = "⛺ Bóvedas Glamping"
    CAT_MUROS = "🧱 Muros Perimetrales"
    
    categoria = st.radio("Línea de Negocio:", [CAT_CASAS, CAT_ESTANQUES, CAT_BOVEDAS, CAT_MUROS])

    datos = None; mod_sel=0; dim_sel=0; extra_h=2.20; tipo_m="Económico"; dist_p=2.0; acab_casas="Industrial"
    
    if categoria == CAT_CASAS:
        mod_sel = st.selectbox("Modelo:", [1, 2, 3], format_func=lambda x: f"Modelo {x}")
        # SELECTOR DE ACABADO PARA CASAS
        acab_casas = st.radio("Estilo de Estructura:", ["Tipo Industrial (Pintura Negra)", "Tipo Cabaña (Perfiles Madera)"])
        datos = calcular_materiales("vivienda", mod_sel, st.session_state['db'], extra_param=acab_casas)
        
    elif categoria == CAT_ESTANQUES:
        dim_sel = st.select_slider("Diámetro (m):", [1, 2, 4, 8, 10, 12], value=8)
        datos = calcular_materiales("estanque", dim_sel, st.session_state['db'])
    elif categoria == CAT_BOVEDAS:
        dim_sel = st.radio("Profundidad (m):", [3, 6])
        datos = calcular_materiales("boveda", dim_sel, st.session_state['db'])
    elif categoria == CAT_MUROS:
        col_tipo, col_dist = st.columns(2)
        with col_tipo:
            tipo_m = st.radio("Estructura:", ["Sencillo (1 Malla)", "Reforzado (2 Mallas)"])
        if es_admin:
            with col_dist:
                dist_p = st.radio("Separación Postes (Admin):", [1.5, 2.0, 3.0], index=1, format_func=lambda x: f"{x} m")
        else:
             dist_p = 2.0

        c_m1, c_m2 = st.columns(2)
        with c_m1: dim_sel = st.number_input("Longitud (m):", min_value=10, value=50, step=10)
        with c_m2: extra_h = st.number_input("Altura (m):", min_value=1.5, value=2.20, step=0.1)
        
        datos = calcular_materiales("cerramiento", dim_sel, st.session_state['db'], extra_param={'h': extra_h, 'tipo': tipo_m, 'distancia': dist_p})

# VISTAS
pestanas = ["👁️ Vitrina Comercial"]
if es_admin: pestanas += ["💰 Costos & Nómina", "📚 Guía Técnica", "⚙️ Configuración", "📈 Margen"]
tabs = st.tabs(pestanas)

# 1. VITRINA
with tabs[0]:
    if datos:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown(f'<p class="big-font">{datos.get("info_nombre")}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="sub-font">{datos.get("info_desc")}</p>', unsafe_allow_html=True)
            
            if categoria == CAT_CASAS:
                if "Madera" in acab_casas:
                    st.success("🪵 **Estilo Cabaña:** Estructura con enchape vinílico tipo madera.")
                else:
                    st.info("🎨 **Estilo Industrial:** Estructura en negro mate de alto contraste.")
            
            if categoria == CAT_MUROS:
                 st.info("🎨 **Acabado:** Muro Natural (Arena/Cal) + Estructura Negra Mate.")
            else:
                img_base = f"render_modelo{mod_sel}" if categoria == CAT_CASAS else (f"render_boveda{dim_sel}" if categoria == CAT_BOVEDAS else "render_estanque")
                found_img = False
                for ext in [".png", ".jpg", ".jpeg"]:
                    if os.path.exists(img_base + ext):
                        st.image(img_base + ext, use_container_width=True); found_img=True; break
                if not found_img: st.warning(f"⚠️ FOTO PENDIENTE")

            if categoria == CAT_CASAS:
                try: st.markdown(core_planos.dibujar_planta(mod_sel), unsafe_allow_html=True)
                except: pass

        with c2:
            st.markdown(f'<div class="card"><h3 style="text-align:center;">Precio Llave en Mano</h3><div class="price-tag">${datos["precio_venta"]:,.0f}</div></div>', unsafe_allow_html=True)
            
            if categoria == CAT_MUROS:
                 st.metric("Metros Lineales", f"{dim_sel} ml")
                 precio_ml = datos["precio_venta"] / dim_sel
                 st.caption(f"Costo por ML: ${precio_ml:,.0f}")
                 st.caption(f"⏱️ Tiempo Estimado: {datos['dias_estimados']} días aprox.")
                 if extra_h == 2.0:
                     st.info("💡 **Tip:** Puedes pedir este muro a **2.20m** por el mismo precio.")
            else:
                m1, m2 = st.columns(2)
                val = datos.get('info_volumen', datos.get('info_area'))
                unit = 'L' if categoria==CAT_ESTANQUES else 'm²'
                m1.metric("Área/Vol", f"{val} {unit}")
                m2.metric("Altura", f"{datos['info_altura']} m")
            
            if categoria != CAT_ESTANQUES:
                st.info(f"🏗️ **Sistema:** Estructura PHR C Galvanizada + Piel Ferrocemento.")

# 2. ADMIN
if es_admin:
    with tabs[1]: # COSTOS NUEVO
        st.subheader("📊 Desglose Financiero del Proyecto")
        
        c_mat, c_mo, c_tot = st.columns(3)
        c_mat.markdown(f"<div class='metric-card'><h4>🧱 Materiales</h4><h2>${datos['costo_materiales']:,.0f}</h2></div>", unsafe_allow_html=True)
        c_mo.markdown(f"<div class='metric-card'><h4>👷‍♂️ Mano de Obra</h4><h2>${datos['costo_mano_obra']:,.0f}</h2><p>Estimado {datos['dias_estimados']} días</p></div>", unsafe_allow_html=True)
        c_tot.markdown(f"<div class='metric-card'><h4>💰 Costo Directo Total</h4><h2>${datos['costo_total']:,.0f}</h2></div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        kpi1, kpi2 = st.columns(2)
        utilidad = datos['precio_venta'] - datos['costo_total']
        kpi1.metric("💵 Utilidad Bruta", f"${utilidad:,.0f}")
        kpi2.metric("📈 Margen Real", f"{int(datos['margen_usado']*100)}%")
        
        st.write("📋 **Lista de Compras (Incluye Acabados):**")
        st.dataframe(datos['lista_visible'], width=600)

    with tabs[2]: # MANUAL TÉCNICO
        st.header("📚 Guía de Construcción Híbrida")
        
        with st.expander("🪵 ACABADO TIPO MADERA (CASAS)"):
            st.markdown("""
            **MATERIALES**
            * **Vinilo PVC:** Piso flexible 2mm o 3mm (No Click).
            * **Pegante:** Boxer (Solución de caucho). NO usar el adhesivo del vinilo.

            **INSTALACIÓN**
            1. Limpiar el perfil con varsol.
            2. Aplicar Boxer en el perfil y en la tira de vinilo.
            3. Dejar secar 10-15 min (al tacto).
            4. Pegar y martillar con mazo de goma.
            """)
            
        with st.expander("🧱 OPTIMIZACIÓN DE MUROS"):
            st.markdown("""
            * **Postes:** Cada 2.00 metros.
            * **Malla:** 5mm (Panel 6m).
            """)

    with tabs[3]: # CONFIG
        col_p, col_r = st.columns(2)
        with col_p:
            st.write("**Precios:**")
            new_prices = st.data_editor(st.session_state['db']['precios'], height=400)
        with col_r:
            st.write("**Receta:**")
            new_receta = st.data_editor(st.session_state['db']['receta_mezcla'])
        if st.button("💾 Guardar DB"):
            st.session_state['db']['precios'] = new_prices; st.session_state['db']['receta_mezcla'] = new_receta
            guardar_db(st.session_state['db']); st.success("Guardado!"); st.rerun()

    with tabs[4]: # MARGEN
        curr = st.session_state['db'].get('config', {}).get('margen_utilidad', 0.30)
        new_m = st.slider("Margen %", 10, 60, int(curr*100)) / 100.0
        c1, c2 = st.columns(2)
        c1.metric("Precio Simulado", f"${datos['costo_total']/(1-new_m):,.0f}")
        if st.button("Actualizar Margen"):
            if "config" not in st.session_state['db']: st.session_state['db']["config"] = {}
            st.session_state['db']["config"]["margen_utilidad"] = new_m
            guardar_db(st.session_state['db']); st.rerun()