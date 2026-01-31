import math

# --- CONFIGURACIÓN DE PRECIOS BUCARAMANGA (2026) ---
PRECIOS = {
    # OBRA GRIS
    'cemento': 28000,       # Bulto 50kg
    'cal': 8000,            # Bulto 10kg
    'arena': 90000,         # m3
    'triturado': 110000,    # m3
    'malla': 20000,         # Metro lineal (Panel 120k)
    'varilla': 22000,       # Barra 6m
    'tubo': 85000,          # Tubo 50x50mm
    'perfil_c': 65000,      # Perfil C
    'teja_570': 240000,     # Teja Nelta
    'caballete': 25000,     
    'zaranda': 220000,      # Rollo 30m
    
    # INSTALACIONES & ACABADOS
    'kit_bano': 1200000, 'kit_cocina': 600000, 'punto_elec': 40000,
    'microcemento': 28000, 'puerta_ext': 850000, 'puerta_int': 450000, 'ventana': 280000,
    
    'mano_obra_m2': 180000
}

def calcular_mezcla(area_m2, espesor_cm=3.5):
    volumen_m3 = area_m2 * (espesor_cm / 100)
    cemento = volumen_m3 * 8
    cal = volumen_m3 * 25       # Bultos 10kg
    arena = volumen_m3 * 1.1
    costo = (cemento * PRECIOS['cemento']) + (cal * PRECIOS['cal']) + (arena * PRECIOS['arena'])
    return {'cemento': cemento, 'cal': cal, 'arena': arena, 'costo': costo}

def calcular_techo_casas(largo_casa):
    cant_tejas = math.ceil(largo_casa / 1.0) 
    cant_caballetes = math.ceil(largo_casa / 0.80)
    metros_perfil = largo_casa * 8
    cant_perfiles = math.ceil(metros_perfil / 6.0)
    
    costo = (cant_tejas * PRECIOS['teja_570']) + \
            (cant_caballetes * PRECIOS['caballete']) + \
            (cant_perfiles * PRECIOS['perfil_c'])
            
    return {'costo': costo, 'cantidades': {'tejas': cant_tejas, 'caballetes': cant_caballetes, 'perfiles': cant_perfiles}}

def calcular_carpinteria(modelo):
    if modelo == 1: p_ext, p_int, vent = 1, 1, 2
    elif modelo == 2: p_ext, p_int, vent = 2, 3, 4
    elif modelo == 3: p_ext, p_int, vent = 2, 5, 6
    else: p_ext, p_int, vent = 0, 0, 0
    costo = (p_ext * PRECIOS['puerta_ext']) + (p_int * PRECIOS['puerta_int']) + (vent * PRECIOS['ventana'])
    return {'costo': costo, 'cantidades': {'p_ext': p_ext, 'p_int': p_int, 'vent': vent}}

def calcular_estructura(area_m2, tipo, largo_casa=0):
    paneles_malla = math.ceil(area_m2 * 0.35)
    rollos_zaranda = math.ceil(area_m2 / 27) 
    cant_tubos = 0
    cant_varillas = 0
    datos_techo = {'costo': 0, 'cantidades': {}}

    if tipo == "vivienda":
        ancho = 5.00
        perimetro = (ancho + largo_casa) * 2
        total_metros_tubo = (math.ceil(perimetro/0.50) * 3.0) + (perimetro * 2)
        cant_tubos = math.ceil(math.ceil(total_metros_tubo / 6.0) * 1.10)
        costo_est = cant_tubos * PRECIOS['tubo']
        datos_techo = calcular_techo_casas(largo_casa)
        costo_extra = datos_techo['costo']
        detalle = f"{cant_tubos} Tubos 50x50mm + Techo Nelta"
        
    elif tipo == "boveda":
        # LÓGICA MURETE TELESCOPICO:
        # Arcos cada 50cm
        num_arcos = math.ceil(largo_casa / 0.50) + 1
        
        # 1. Varillas (Los Arcos Superiores) - 1 varilla de 6m por arco
        cant_varillas = num_arcos 
        # + Varillas longitudinales de unión (7 líneas a lo largo)
        metros_longitudinales = largo_casa * 7
        varillas_long = math.ceil(metros_longitudinales / 6.0)
        cant_varillas += varillas_long

        # 2. Tubos (Los Muretes de 0.90m)
        # Cada arco necesita 2 tubos de base (uno a cada lado)
        num_tubos_murete = num_arcos * 2
        metros_tubos_murete = num_tubos_murete * 0.90
        
        # 3. Viga de Piso (Donde se sueldan los muretes)
        # 2 líneas a lo largo de la bóveda
        metros_viga_piso = largo_casa * 2
        
        total_metros_tubo = metros_tubos_murete + metros_viga_piso
        cant_tubos = math.ceil(total_metros_tubo / 6.0)
        
        costo_est = (cant_varillas * PRECIOS['varilla']) + (cant_tubos * PRECIOS['tubo'])
        costo_extra = 0
        detalle = f"{cant_tubos} Tubos (Muretes .90) + {cant_varillas} Varillas (Arcos)"

    elif tipo == "estanque":
        cant_varillas = math.ceil(area_m2 * 2.2)
        costo_est = cant_varillas * PRECIOS['varilla']
        detalle = f"{cant_varillas} Varillas Refuerzo"
        costo_extra = 0

    costo_mallas = (paneles_malla * PRECIOS['malla'] * 6) + (rollos_zaranda * PRECIOS['zaranda'])
    
    return {
        'costo': int(costo_est + costo_mallas + costo_extra),
        'detalle': detalle,
        'cantidades': {
            'malla': paneles_malla, 'zaranda': rollos_zaranda, 
            'tubos': cant_tubos, 'varillas': cant_varillas,
            'techo': datos_techo.get('cantidades', {})
        }
    }

def generar_presupuesto(tipo, dimension):
    ancho_std = 5.00 
    costo_hidro, costo_elec, costo_carp = 0, 0, 0
    lista_compras = {}
    
    if tipo == "vivienda":
        if dimension == 1: largo, area_piso, pts_elec, kits_bano = 7.00, 35.0, 18, 1
        elif dimension == 2: largo, area_piso, pts_elec, kits_bano = 13.00, 65.0, 30, 1.5
        elif dimension == 3: largo, area_piso, pts_elec, kits_bano = 22.00, 110.0, 50, 2
        
        nombre = f"Modelo {dimension} - Vivienda Rural"
        descripcion = "Llave en Mano (Inc. Carpintería y Redes)"
        
        costo_hidro = PRECIOS['kit_cocina'] + (PRECIOS['kit_bano'] * kits_bano)
        costo_elec = pts_elec * PRECIOS['punto_elec']
        carp = calcular_carpinteria(dimension)
        costo_carp = carp['costo']
        
        perimetro = (ancho_std + largo) * 2
        area_total_fc = perimetro * 2.4 
        
        lista_compras['hidro'] = {'baños': kits_bano, 'cocina': 1}
        lista_compras['elec'] = pts_elec
        lista_compras['carp'] = carp['cantidades']

    elif tipo == "estanque":
        radio = dimension / 2
        area_total_fc = (math.pi * (radio**2)) + (2 * math.pi * radio * 1.20)
        nombre = f"Estanque Tilapia D={dimension}m"
        descripcion = "Obra Gris + Impermeabilización"
        area_piso = math.pi * (radio**2)
        largo = 0

    elif tipo == "boveda":
        ancho_bov = 3.80
        # Altura Murete (0.90) + Radio Arco (1.90) = Perímetro Sección Transversal
        # Perimetro Arco = Pi * r = 5.97m.
        # Muretes = 0.90 * 2 = 1.80m.
        # Perímetro corte = 7.77m
        
        perimetro_corte = (math.pi * (ancho_bov/2)) + (0.90 * 2)
        area_techo_muros = perimetro_corte * dimension
        
        # Tapas: Area semicírculo + Area rectangulo base (3.80 x 0.90)
        area_tapa = (math.pi * ((ancho_bov/2)**2) / 2) + (ancho_bov * 0.90)
        area_tapas = area_tapa * 2
        
        area_total_fc = area_techo_muros + area_tapas
        area_piso = ancho_bov * dimension
        largo = dimension
        
        # Configuración Bodega vs Suite
        if dimension == 3:
            nombre = "Bóveda 3m (Bodega/Refugio)"
            descripcion = "Murete 90cm | Sin Baño"
            costo_elec = 3 * PRECIOS['punto_elec']
            costo_carp = PRECIOS['puerta_ext'] + PRECIOS['ventana'] # Puerta + Ventana
            lista_compras['elec'] = 3
            lista_compras['carp'] = {'p_ext': 1, 'p_int': 0, 'vent': 1}
        else:
            nombre = "Bóveda 6m (Glamping Suite)"
            descripcion = "Murete 90cm | Con Baño Privado"
            costo_elec = 8 * PRECIOS['punto_elec']
            # Puerta Principal + Puerta Baño + Ventana Grande + Kit Baño
            costo_carp = PRECIOS['puerta_ext'] + PRECIOS['puerta_int'] + (PRECIOS['ventana']*2)
            costo_hidro = PRECIOS['kit_bano']
            lista_compras['elec'] = 8
            lista_compras['carp'] = {'p_ext': 1, 'p_int': 1, 'vent': 2}
            lista_compras['hidro'] = {'baños': 1}

    mezcla = calcular_mezcla(area_total_fc)
    estructura = calcular_estructura(area_total_fc, tipo, largo)
    
    # PISO MICROCEMENTO
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

    mano_obra = area_total_fc * PRECIOS['mano_obra_m2']
    costo_directo = mezcla['costo'] + estructura['costo'] + mano_obra + \
                    costo_piso_concreto + costo_hidro + costo_elec + costo_carp
    precio_venta = costo_directo * 1.30

    total_cemento = mezcla['cemento'] + materiales_piso['cemento']
    total_arena = mezcla['arena'] + materiales_piso['arena']
    
    return {
        'nombre': nombre,
        'descripcion': descripcion,
        'area': round(area_piso if tipo == "vivienda" else area_total_fc, 1),
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
            'techo': estructura['cantidades'].get('techo', {}),
            'carpinteria': lista_compras.get('carp', {}),
            'hidro': lista_compras.get('hidro', {}),
            'elec': lista_compras.get('elec', 0),
            'area_piso': round(area_piso if tipo != "estanque" else 0, 1)
        }
    }