# --- CEREBRO DE CÁLCULO FERROTEK v2.1 (Con Estanques y Bóvedas) ---
import math

# --- PRECIOS UNITARIOS BASE (¡ACTUALIZAR MENSUALMENTE!) ---
PRECIOS = {
    'cemento': 28000,     # Bulto 50kg Argis
    'arena': 90000,       # Metro cúbico lavado
    'triturado': 110000,  # Metro cúbico de 1/2"
    'varilla': 25000,     # Varilla 1/2" x 6m
    'malla': 180000,      # Malla electrosoldada (rollo/panel)
    'tubo_est': 150000,   # Tubo estructural cuadrado
    'alambron': 8000,     # Kilo
    'cal': 15000,         # Bulto Cal Hidratada (para estanques)
    # Factores de mano de obra y kits
    'mo_m2_casa': 450000, # Mano de obra x m2 (obra gris)
    'kit_techo_m2': 120000, # Nelta + perfiles x m2
    'kit_vidrios_global_peq': 3500000, # Ventanería modelo pequeño
    'kit_vidrios_global_med': 5000000, # Ventanería modelo mediano
    'kit_vidrios_global_gra': 8000000, # Ventanería modelo grande
    # Factores Bóvedas y Estanques
    'mo_m2_ferro': 350000, # Mano de obra especializada ferrocemento
    'kit_impermeabilizante': 450000,
    'kit_fachada_boveda': 2500000,
    'kit_hidraulico_estanque': 300000
}

def generar_presupuesto(tipo_proyecto, dimension_clave):
    datos_calculados = {}

    # 1. CÁLCULO DE MATERIALES FÍSICOS (Cantidades)
    materiales = calcular_materiales_fisicos(tipo_proyecto, dimension_clave)
    
    if not materiales:
        return None

    # 2. CÁLCULO FINANCIERO (Costos Directos)
    costo_directo = 0
    costo_directo += materiales.get('cemento', 0) * PRECIOS['cemento']
    costo_directo += materiales.get('arena', 0) * PRECIOS['arena']
    costo_directo += materiales.get('triturado', 0) * PRECIOS['triturado']
    costo_directo += materiales.get('varillas', 0) * PRECIOS['varilla']
    costo_directo += materiales.get('malla', 0) * PRECIOS['malla']
    costo_directo += materiales.get('tubos', 0) * PRECIOS['tubo_est']
    costo_directo += materiales.get('alambron', 0) * PRECIOS['alambron']
    costo_directo += materiales.get('cal', 0) * PRECIOS['cal']

    # Costos adicionales según tipo
    precio_venta_sugerido = 0

    if tipo_proyecto == "vivienda":
        area = materiales['info_area']
        costo_mo = area * PRECIOS['mo_m2_casa']
        costo_techo = area * PRECIOS['kit_techo_m2']
        kit_vidrio = 0
        if dimension_clave == 1: kit_vidrio = PRECIOS['kit_vidrios_global_peq']
        elif dimension_clave == 2: kit_vidrio = PRECIOS['kit_vidrios_global_med']
        elif dimension_clave == 3: kit_vidrio = PRECIOS['kit_vidrios_global_gra']
        costo_directo += costo_mo + costo_techo + kit_vidrio
        precio_venta_sugerido = costo_directo / (1 - 0.35)

    elif tipo_proyecto == "boveda":
        area = materiales['info_area']
        costo_mo = area * PRECIOS['mo_m2_ferro']
        costo_kits = PRECIOS['kit_impermeabilizante'] + PRECIOS['kit_fachada_boveda']
        costo_directo += costo_mo + costo_kits
        precio_venta_sugerido = costo_directo / (1 - 0.45)

    elif tipo_proyecto == "estanque":
        diametro = dimension_clave
        altura = 1.2
        perimetro = math.pi * diametro
        area_superficial_muro = perimetro * altura
        area_piso = math.pi * (diametro/2)**2
        area_total_trabajo = area_superficial_muro + area_piso
        costo_mo = area_total_trabajo * PRECIOS['mo_m2_ferro'] * 0.8
        costo_directo += costo_mo + PRECIOS['kit_hidraulico_estanque']
        precio_venta_sugerido = costo_directo / (1 - 0.30)

    # 3. EMPAQUETAR RESULTADOS
    datos_calculados = {
        'nombre': materiales['info_nombre'],
        'descripcion': materiales['info_desc'],
        'area': materiales.get('info_area', 0),
        'altura': materiales.get('info_altura', 0),
        'volumen_litros': materiales.get('info_volumen', 0),
        'lista_compras': materiales,
        'costo_directo': round(costo_directo, -3),
        'precio_venta': round(precio_venta_sugerido, -3)
    }

    return datos_calculados


def calcular_materiales_fisicos(tipo, dimension):
    lista = {}
    # --- A. CASAS MODULARES ---
    if tipo == "vivienda":
        if dimension == 1:
            lista = {'info_nombre': "Modelo 1: Loft (35m²)", 'info_desc': "Ideal para parejas o glamping de lujo. Espacio abierto optimizado.", 'info_area': 35, 'info_altura': 3.0, 'cemento': 75, 'arena': 5, 'triturado': 3, 'varillas': 18, 'malla': 12, 'tubos': 6, 'alambron': 10}
        elif dimension == 2:
            lista = {'info_nombre': "Modelo 2: Familiar (65m²)", 'info_desc': "Perfecta para familias pequeñas. 2 habitaciones y zona social amplia.", 'info_area': 65, 'info_altura': 3.2, 'cemento': 130, 'arena': 9, 'triturado': 5, 'varillas': 30, 'malla': 22, 'tubos': 10, 'alambron': 20}
        elif dimension == 3:
            lista = {'info_nombre': "Modelo 3: Hacienda (110m²)", 'info_desc': "La casa principal de la finca. 3 habitaciones, techos altos, gran presencia.", 'info_area': 110, 'info_altura': 4.5, 'cemento': 210, 'arena': 15, 'triturado': 9, 'varillas': 45, 'malla': 38, 'tubos': 16, 'alambron': 35}

    # --- B. ESTANQUES PISCÍCOLAS ---
    elif tipo == "estanque":
        diametro = dimension
        if diametro <= 0: return None # Seguridad
        altura = 1.2
        radio = diametro / 2
        perimetro = math.pi * diametro
        area_piso = math.pi * (radio**2)
        area_muro = perimetro * altura
        volumen_m3 = area_piso * altura
        volumen_litros = int(volumen_m3 * 1000)
        factor_cemento_x_m3_volumen = 1.5
        cemento_est = int(volumen_m3 * factor_cemento_x_m3_volumen)
        if cemento_est < 5: cemento_est = 5

        lista = {
            'info_nombre': f"Estanque Circular (Ø {diametro}m)",
            'info_desc': "Tanque en ferrocemento para piscicultura intensiva. Paredes lisas, alta durabilidad.",
            'info_area': round(area_piso, 1),
            'info_altura': altura,
            'info_volumen': volumen_litros,
            'cemento': cemento_est,
            'cal': int(cemento_est * 0.2),
            'arena': round(cemento_est * 0.06, 1),
            'malla': int(area_muro * 1.2) + int(area_piso * 0.8),
            'varillas': int(perimetro / 1.5),
            'alambron': int(cemento_est * 0.5)
        }

    # --- C. BÓVEDAS GLAMPING ---
    elif tipo == "boveda":
        largo = dimension
        if largo <= 0: return None # Seguridad
        ancho_std = 3.5
        altura_std = 2.8
        area_huella = largo * ancho_std
        cemento_bov = int(area_huella * 3.5)
        malla_bov = int(area_huella * 2.5)
        varillas_bov = int(largo * 4)
        desc = ""
        if largo == 3: desc = "Cápsula compacta para parejas. Cama Queen y visual panorámica."
        else: desc = "Suite profunda con espacio para sala de estar pequeña y baño al fondo."

        lista = {
            'info_nombre': f"Bóveda Glamping ({largo}m Profundidad)",
            'info_desc': desc,
            'info_area': round(area_huella, 1),
            'info_altura': altura_std,
            'cemento': cemento_bov,
            'arena': round(cemento_bov * 0.05, 1),
            'malla': malla_bov,
            'varillas': varillas_bov,
            'alambron': int(cemento_bov * 0.3),
            'tubos': 2
        }

    return lista