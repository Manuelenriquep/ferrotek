import math

# --- CONFIGURACIÓN DE PRECIOS BUCARAMANGA (2026) ---
PRECIOS = {
    # OBRA GRIS
    'cemento': 28000, 'cal': 8000, 'arena': 90000, 'triturado': 110000,
    'malla': 20000, 'varilla': 22000, 'alambron_kg': 6500, 'tubo': 85000,
    'perfil_c': 65000, 'teja_570': 240000, 'caballete': 25000, 'zaranda': 220000,
    
    # INSTALACIONES & ACABADOS
    'kit_bano': 1200000, 'kit_cocina': 600000, 'punto_elec': 40000,
    'microcemento': 28000, 'puerta_ext': 850000, 'puerta_int': 450000, 'ventana': 280000,
    
    # MANO DE OBRA
    'mo_casa': 180000, 'mo_estanque': 120000
}

def calcular_mezcla(area_m2, espesor_cm, tipo):
    volumen_m3 = area_m2 * (espesor_cm / 100)
    
    # RENDIMIENTOS ESTÁNDAR (La Cal es vital en ambos casos)
    # Casa: 1:3:3 (Cemento:Arena:Cal) -> Más Cal para manejabilidad en muros altos
    # Estanque: Mezcla más rica en cemento, pero CON CAL para impermeabilidad
    
    cemento = volumen_m3 * 8     # Bultos 50kg
    arena = volumen_m3 * 1.1     # m3
    cal = volumen_m3 * 25        # Bultos 10kg (Relleno de poros y plasticidad)
    
    costo = (cemento * PRECIOS['cemento']) + \
            (cal * PRECIOS['cal']) + \
            (arena * PRECIOS['arena'])
            
    return {'cemento': cemento, 'cal': cal, 'arena': arena, 'costo': costo}

def calcular_techo_casas(largo_casa):
    cant_tejas = math.ceil(largo_casa / 1.0) 
    cant_caballetes = math.ceil(largo_casa / 0.80)
    metros_perfil = largo_casa * 8
    cant_perfiles = math.ceil(metros_perfil / 6.0)
    costo = (cant_tejas * PRECIOS['teja_570']) + (cant_caballetes * PRECIOS['caballete']) + (cant_perfiles * PRECIOS['perfil_c'])
    return {'costo': costo, 'cantidades': {'tejas': cant_tejas, 'caballetes': cant_caballetes, 'perfiles': cant_perfiles}}

def calcular_carpinteria(modelo):
    if modelo == 1: p_ext, p_int, vent = 1, 1, 2
    elif modelo == 2: p_ext, p_int, vent = 2, 3, 4
    elif modelo == 3: p_ext, p_int, vent = 2, 5, 6
    else: p_ext, p_int, vent = 0, 0, 0
    costo = (p_ext * PRECIOS['puerta_ext']) + (p_int * PRECIOS['puerta_int']) + (vent * PRECIOS['ventana'])
    return {'costo': costo, 'cantidades': {'p_ext': p_ext, 'p_int': p_int, 'vent': vent}}

def calcular_estructura(area_m2, tipo, largo_casa=0, dimension_estanque=0):
    paneles_malla = math.ceil(area_m2 * 0.35)
    rollos_zaranda = math.ceil(area_m2 / 27) 
    cant_tubos, cant_varillas, cant_alambron = 0, 0, 0
    datos_techo = {'costo': 0, 'cantidades': {}}

    if tipo == "vivienda":
        ancho = 5.00
        perimetro = (ancho + largo_casa) * 2
        total_metros_tubo = (math.ceil(perimetro/0.50) * 3.0) + (perimetro * 2)
        cant_tubos = math.ceil(math.ceil(total_metros_tubo / 6.0) * 1.10)
        costo_est = cant_tubos * PRECIOS['tubo']
        datos_techo = calcular_techo_casas(largo_casa)
        costo_extra = datos_techo['costo']
        detalle = f"{cant_tubos} Tubos + Techo Nelta"
        
    elif tipo == "boveda":
        num_arcos = math.ceil(largo_casa / 0.50) + 1
        cant_varillas = num_arcos 
        metros_longitudinales = largo_casa * 7
        cant_varillas += math.ceil(metros_longitudinales / 6.0)
        num_tubos_murete = num_arcos * 2
        metros_tubos_murete = num_tubos_murete * 0.90
        metros_viga_piso = largo_casa * 2
        total_metros_tubo = metros_tubos_murete + metros_viga_piso
        cant_tubos = math.ceil(total_metros_tubo / 6.0)
        costo_est = (cant_varillas * PRECIOS['varilla']) + (cant_tubos * PRECIOS['tubo'])
        costo_extra = 0
        detalle = f"{cant_tubos} Tubos + {cant_varillas} Varillas"

    elif tipo == "estanque":
        if dimension_estanque <= 1.5:
            cant_alambron = math.ceil(area_m2 * 1.0) 
            costo_est = cant_alambron * PRECIOS['alambron_kg']
            detalle = f"{cant_alambron} Kg Alambrón (Ligero)"
            paneles_malla = math.ceil(area_m2 * 0.15)
        elif dimension_estanque <= 4:
            cant_alambron = math.ceil(area_m2 * 1.5) 
            costo_est = cant_alambron * PRECIOS['alambron_kg']
            detalle = f"{cant_alambron} Kg Alambrón (4.2mm)"
            paneles_malla = math.ceil(area_m2 * 0.15) 
        else:
            cant_varillas = math.ceil(area_m2 * 2.2)
            costo_est = cant_varillas * PRECIOS['varilla']
            detalle = f"{cant_varillas} Varillas Corrugadas"
        costo_extra = 0

    costo_mallas = (paneles_malla * PRECIOS['malla'] * 6) + (rollos_zaranda * PRECIOS['zaranda'])
    
    return {
        'costo': int(costo_est + costo_mallas + costo_extra),
        'detalle': detalle,
        'cantidades': {
            'malla': paneles_malla, 'zaranda': rollos_zaranda, 
            'tubos': cant_tubos, 'varillas': cant_varillas,
            'alambron': cant_alambron,
            'techo': datos_techo.get('cantidades', {})
        }
    }

def generar_presupuesto(tipo, dimension):
    ancho_std = 5.00 
    costo_hidro, costo_elec, costo_carp = 0, 0, 0
    lista_compras = {}
    precio_mo = PRECIOS['mo_estanque'] if tipo == "estanque" else PRECIOS['mo_casa']
    espesor_muro = 3.5
    volumen_litros = 0
    altura_util = 0

    if tipo == "vivienda":
        if dimension == 1: largo, area_piso, pts_elec, kits_bano = 7.00, 35.0, 18, 1
        elif dimension == 2: largo, area_piso, pts_elec, kits_bano = 13.00, 65.0, 30, 1.5
        elif dimension == 3: largo, area_piso, pts_elec, kits_bano = 22.00, 110.0, 50, 2
        nombre, descripcion = f"Modelo {dimension}", "Llave en Mano"
        costo_hidro = PRECIOS['kit_cocina'] + (PRECIOS['kit_bano'] * kits_bano)
        costo_elec = pts_elec * PRECIOS['punto_elec']
        carp = calcular_carpinteria(dimension)
        costo_carp = carp['costo']
        perimetro = (ancho_std + largo) * 2
        area_total_fc = perimetro * 2.4 
        lista_compras['hidro'] = {'baños': kits_bano, 'cocina': 1}
        lista_compras['elec'] = pts_elec
        lista_compras['carp'] = carp['cantidades']
        altura_util = 2.40

    elif tipo == "estanque":
        espesor_muro = 2.5
        altura_util = 1.20 
        radio = dimension / 2
        volumen_m3 = math.pi * (radio**2) * altura_util
        volumen_litros = volumen_m3 * 1000
        area_total_fc = (math.pi * (radio**2)) + (2 * math.pi * radio * altura_util)
        
        nombre = f"Estanque D={dimension}m ({int(volumen_litros):,} Litros)"
        descripcion = f"Mezcla con Cal Hidrófuga | Vol: {volumen_m3:.1f} m³"
        area_piso = math.pi * (radio**2)
        largo = 0

    elif tipo == "boveda":
        espesor_muro = 3.0 
        ancho_bov = 3.80
        perimetro_corte = (math.pi * (ancho_bov/2)) + (0.90 * 2)
        area_techo_muros = perimetro_corte * dimension
        area_tapa = (math.pi * ((ancho_bov/2)**2) / 2) + (ancho_bov * 0.90)
        area_tapas = area_tapa * 2
        area_total_fc = area_techo_muros + area_tapas
        area_piso = ancho_bov * dimension
        largo = dimension
        altura_util = 2.80 
        
        if dimension == 3:
            nombre, descripcion = "Bóveda 3m (Bodega)", "Murete 90cm | Sin Baño"
            costo_elec, costo_carp = 3 * PRECIOS['punto_elec'], PRECIOS['puerta_ext'] + PRECIOS['ventana']
            lista_compras['elec'], lista_compras['carp'] = 3, {'p_ext': 1, 'p_int': 0, 'vent': 1}
        else:
            nombre, descripcion = "Bóveda 6m (Suite)", "Murete 90cm | Con Baño"
            costo_elec, costo_carp = 8 * PRECIOS['punto_elec'], PRECIOS['puerta_ext'] + PRECIOS['puerta_int'] + (PRECIOS['ventana']*2)
            costo_hidro = PRECIOS['kit_bano']
            lista_compras['elec'], lista_compras['carp'], lista_compras['hidro'] = 8, {'p_ext': 1, 'p_int': 1, 'vent': 2}, {'baños': 1}

    # SIN ADITIVO, SOLO CAL
    mezcla = calcular_mezcla(area_total_fc, espesor_muro, tipo)
    
    dim_est = dimension if tipo == "estanque" else 0
    estructura = calcular_estructura(area_total_fc, tipo, largo, dim_est)
    
    costo_piso_concreto = 0
    materiales_piso = {'cemento':0, 'arena':0, 'triturado':0}
    if tipo in ["vivienda", "boveda"]:
        if tipo == "vivienda": area_real_piso = area_piso
        else: area_real_piso = ancho_bov * dimension
        vol_piso = area_real_piso * 0.08 
        c_piso, a_piso, t_piso = vol_piso*7, vol_piso*0.6, vol_piso*0.8
        materiales_piso = {'cemento': c_piso, 'arena': a_piso, 'triturado': t_piso}
        base = vol_piso * (PRECIOS['cemento']*7 + PRECIOS['arena']*0.6 + PRECIOS['triturado']*0.8)
        acabado = area_real_piso * PRECIOS['microcemento']
        costo_piso_concreto = base + acabado

    if tipo == "estanque" and dimension <= 1.5:
        costo_mano_obra = 250000 
    else:
        costo_mano_obra = area_total_fc * precio_mo

    costo_directo = mezcla['costo'] + estructura['costo'] + costo_mano_obra + \
                    costo_piso_concreto + costo_hidro + costo_elec + costo_carp
    
    margen = 1.30
    if tipo == "estanque" and dimension <= 1.5:
        margen = 1.25
        
    precio_venta = costo_directo * margen

    total_cemento = mezcla['cemento'] + materiales_piso['cemento']
    total_arena = mezcla['arena'] + materiales_piso['arena']
    
    return {
        'nombre': nombre,
        'descripcion': descripcion,
        'area': round(area_piso if tipo == "vivienda" else area_total_fc, 1),
        'volumen_litros': int(volumen_litros),
        'altura': altura_util,
        'costo_directo': int(costo_directo),
        'precio_venta': int(precio_venta),
        'lista_compras': {
            'cemento': round(total_cemento, 1),
            'cal': round(mezcla['cal'], 1),
            'arena': round(total_arena, 1),
            'triturado': round(materiales_piso['triturado'], 1),
            'malla': estructura['cantidades']['malla'],
            'zaranda': estructura['cantidades']['zaranda'],
            'tubos': estructura['cantidades']['tubos'],
            'varillas': estructura['cantidades']['varillas'],
            'alambron': estructura['cantidades'].get('alambron', 0),
            'techo': estructura['cantidades'].get('techo', {}),
            'carpinteria': lista_compras.get('carp', {}),
            'hidro': lista_compras.get('hidro', {}),
            'elec': lista_compras.get('elec', 0),
            'area_piso': round(area_piso if tipo != "estanque" else 0, 1)
        }
    }