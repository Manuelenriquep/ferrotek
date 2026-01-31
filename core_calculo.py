import math

# --- CONFIGURACIÓN DE PRECIOS BUCARAMANGA (REALES 2026) ---
PRECIOS = {
    'cemento': 28000,       # Bulto 50kg
    'cal': 16000,           # Bulto 25kg (Vivacal)
    'arena': 90000,         # m3
    'triturado': 110000,    # m3
    
    # ESTRUCTURA METALICA
    'malla': 20000,         # Metro lineal (Panel $120k / 6m)
    'varilla': 22000,       # Barra 6m (Refuerzos)
    'tubo': 85000,          # Tubo 50x50mm (Muros y Vigas)
    'perfil_c': 65000,      # Perfil C (Correas Techo Nelta)
    
    # CUBIERTA & ACABADOS
    'teja_570': 240000,     # Teja Nelta Termoacústica 5.70m
    'caballete': 25000,     # Caballete Nelta
    'zaranda': 220000,      # Rollo de 30m x 0.90m
    
    # OTROS
    'kit_h_bano': 800000,   # Hidrosanitario
    'mano_obra_m2': 180000  # Todo costo
}

# --- 1. CÁLCULO MEZCLA FERROCEMENTO (1:3:3) ---
def calcular_mezcla(area_m2, espesor_cm=3.5):
    volumen_m3 = area_m2 * (espesor_cm / 100)
    cemento = volumen_m3 * 8
    cal = volumen_m3 * 10
    arena = volumen_m3 * 1.1
    costo = (cemento * PRECIOS['cemento']) + (cal * PRECIOS['cal']) + (arena * PRECIOS['arena'])
    return {'cemento': cemento, 'cal': cal, 'arena': arena, 'costo': costo}

# --- 2. CÁLCULO DE TECHO (NORMA NELTA) ---
def calcular_techo_casas(largo_casa):
    # Teja Nelta 5.70m (Se corta a la mitad = 2.85m por agua)
    # Pendiente ideal Nelta: 27% - 30%
    
    # 1. Cantidad de Tejas (Ancho útil 1.00m traslapado)
    cantidad_tejas = math.ceil(largo_casa / 1.0) 
    
    # 2. Caballetes (Largo útil 0.80m)
    cantidad_caballetes = math.ceil(largo_casa / 0.80)
    
    # 3. Estructura Techo (Correas Perfil C)
    # Norma Nelta: Apoyos máx cada 1.15m.
    # Para caída de 2.85m necesitamos 4 correas por lado (Cumbrera, 2 Medias, Alero)
    # Total filas de correas = 8
    metros_perfil_c = largo_casa * 8
    total_perfiles_c = math.ceil(metros_perfil_c / 6.0) # Barras de 6m
    
    costo_techo = (cantidad_tejas * PRECIOS['teja_570']) + \
                  (cantidad_caballetes * PRECIOS['caballete']) + \
                  (total_perfiles_c * PRECIOS['perfil_c'])
                  
    return {
        'detalle': f"Cubierta Nelta Termoacústica (Garantía 10 Años) + Estructura Perfil C",
        'tejas': cantidad_tejas,
        'perfiles': total_perfiles_c,
        'costo': costo_techo
    }

# --- 3. CÁLCULO ESTRUCTURAL (MUROS 50x50mm) ---
def calcular_estructura(area_m2, tipo, largo_casa=0):
    costo_extra = 0
    detalle = ""
    paneles_malla = math.ceil(area_m2 * 0.35)
    rollos_zaranda = math.ceil(area_m2 / 27) 
    
    if tipo == "vivienda":
        ancho = 5.00
        perimetro = (ancho + largo_casa) * 2
        
        # A. PARALES VERTICALES (Cada 50cm para rigidez)
        num_parales = math.ceil(perimetro / 0.50)
        # Se cortan de 3.0m (2.40m libres + 60cm anclaje/desperdicio)
        metros_parales = num_parales * 3.0
        
        # B. VIGAS DE AMARRE 50x50mm (Horizontal)
        # 1. Viga Inferior (Cimentación)
        # 2. Viga Superior (A 2.40m de altura - Corona)
        metros_vigas = perimetro * 2
        
        # C. TOTAL TUBERÍA 50x50mm
        total_metros_tubo = metros_parales + metros_vigas
        cant_tubos = math.ceil(total_metros_tubo / 6.0)
        
        # Factor desperdicio y refuerzos marcos (10%)
        cant_tubos = math.ceil(cant_tubos * 1.10)

        costo_est = cant_tubos * PRECIOS['tubo']
        datos_techo = calcular_techo_casas(largo_casa)
        costo_extra = datos_techo['costo']
        
        detalle = f"{cant_tubos} Tubos 50x50mm (Parales c/50cm + Viga Amarre 2.40m) + Techo Nelta"
        
    elif tipo == "boveda":
        cant_varillas = math.ceil(area_m2 * 1.5)
        costo_est = cant_varillas * PRECIOS['varilla']
        detalle = f"{cant_varillas} Varillas (Arcos 3.80m)"
        
    elif tipo == "estanque":
        cant_varillas = math.ceil(area_m2 * 2.2)
        costo_est = cant_varillas * PRECIOS['varilla']
        detalle = f"{cant_varillas} Varillas (Refuerzo Hidráulico)"

    costo_mallas = (paneles_malla * PRECIOS['malla'] * 6) + \
                   (rollos_zaranda * PRECIOS['zaranda'])
                   
    return {
        'costo': int(costo_est + costo_mallas + costo_extra),
        'detalle': detalle,
        'malla': paneles_malla,
        'zaranda': rollos_zaranda
    }

# --- 4. CONTROLADOR PRINCIPAL ---
def generar_presupuesto(tipo, dimension):
    ancho_std = 5.00 
    costo_hidrosanitario = 0
    descripcion = ""
    
    if tipo == "vivienda":
        if dimension == 1: 
            largo, area_piso = 7.00, ancho_std * 7.00
            nombre = "Modelo 1: Suite (35 m²)"
            descripcion = "1 Hab / 1 Baño | Techo Nelta"
            costo_hidrosanitario = PRECIOS['kit_h_bano'] * 1
        elif dimension == 2: 
            largo, area_piso = 13.00, ancho_std * 13.00
            nombre = "Modelo 2: Cotidiana (65 m²)"
            descripcion = "2 Hab / 1.5 Baños | Techo Nelta"
            costo_hidrosanitario = PRECIOS['kit_h_bano'] * 1.5
        elif dimension == 3: 
            largo, area_piso = 22.00, 110.0
            nombre = "Modelo 3: Patriarca (110 m²)"
            descripcion = "3 Hab / 2 Baños | Techo Nelta"
            costo_hidrosanitario = PRECIOS['kit_h_bano'] * 2
        
        perimetro = (ancho_std + largo) * 2
        area_total_fc = perimetro * 2.4 
        
    elif tipo == "estanque":
        radio = dimension / 2
        altura = 1.20
        area_total_fc = (math.pi * (radio**2)) + (2 * math.pi * radio * 1.20)
        nombre = f"Estanque Tilapia D={dimension}m"
        descripcion = "Altura 1.20m | Piso FC"
        largo = 0

    elif tipo == "boveda":
        ancho_bov = 3.80
        radio = ancho_bov / 2
        area_total_fc = (math.pi * radio * dimension) + (math.pi * (radio**2)) + (ancho_bov * dimension)
        nombre = f"Bóveda {dimension}m Fondo"
        descripcion = "Ancho 3.80m | Inc. Piso/Tapas"
        area_piso = ancho_bov * dimension
        largo = dimension

    mezcla = calcular_mezcla(area_total_fc)
    estructura = calcular_estructura(area_total_fc, tipo, largo)
    
    costo_piso_concreto = 0
    if tipo in ["vivienda", "boveda"]:
        if tipo == "vivienda": area_real_piso = area_piso
        else: area_real_piso = ancho_bov * dimension
        vol_piso = area_real_piso * 0.08 
        costo_piso_concreto = vol_piso * (PRECIOS['cemento']*7 + PRECIOS['arena']*0.6 + PRECIOS['triturado']*0.8)

    mano_obra = area_total_fc * PRECIOS['mano_obra_m2']
    costo_directo = mezcla['costo'] + estructura['costo'] + mano_obra + costo_piso_concreto + costo_hidrosanitario
    precio_venta = costo_directo * 1.30

    return {
        'nombre': nombre,
        'descripcion': descripcion,
        'area': round(area_piso if tipo == "vivienda" else area_total_fc, 1),
        'costo_directo': int(costo_directo),
        'precio_venta': int(precio_venta),
        'materiales': {
            'cemento': round(mezcla['cemento'],1),
            'cal': round(mezcla['cal'],1),
            'arena': round(mezcla['arena'],1),
            'estructura': estructura['detalle'],
            'malla': estructura['malla'],
            'zaranda': estructura['zaranda']
        }
    }