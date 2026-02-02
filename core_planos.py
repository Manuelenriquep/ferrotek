import math

class CoreFerrotek:
    def __init__(self, precios, margen_utilidad):
        self.p = precios
        self.MARGEN = 1 - margen_utilidad
        self.H_VISTA = 2.20
        self.H_MALLA = 2.35

    def calcular_muro_perimetral(self, ml):
        """Muro 2.20m - Sistema Raíz con Zapata Continua"""
        cant_postes = math.ceil(ml / 1.5) + 1
        acero = (cant_postes * 2.8 * self.p['perfil_2_pulg_mt']) + (ml * 3 * 8500)
        area = ml * self.H_MALLA
        mallas = (area * self.p['malla_5mm_m2']) + (area * 2 * self.p['malla_zaranda_m2'])
        mezcla = (ml * self.H_VISTA * 0.04 * 1.1) * (5*self.p['cemento_bulto'] + 5*self.p['cal_bulto'] + self.p['arena_m3'])
        costo_dir = acero + mallas + mezcla + (ml * 0.85 * self.p['valor_jornal'])
        return round(costo_dir / self.MARGEN, -3)

    def calcular_vivienda_unibody(self, area_m2):
        """Casas: Fachada Doble / Internos Simple (Matriz 1:3:3)"""
        perim = math.sqrt(area_m2) * 4
        div_int = perim * 0.6
        area_ext = perim * 2.4
        mallas_ext = area_ext * (self.p['malla_5mm_m2'] + 2*self.p['malla_zaranda_m2'])
        area_int = div_int * 2.4
        mallas_int = area_int * (self.p['malla_5mm_m2'] + self.p['malla_zaranda_m2'])
        mezcla_muros = (area_ext + area_int) * 0.04 * (5*self.p['cemento_bulto'] + 5*self.p['cal_bulto'] + self.p['arena_m3'])
        pisos_tech = area_m2 * (0.2*self.p['aditivo_F1_kg'] + 0.1*self.p['sellado_FX_galon'])
        estructura = (perim + div_int) * 1.5 * self.p['perfil_2_pulg_mt']
        techo = area_m2 * 85000 
        costo_dir = mallas_ext + mallas_int + mezcla_muros + pisos_tech + estructura + techo + (area_m2 * 2.8 * self.p['valor_jornal'])
        return round(costo_dir / self.MARGEN, -3)

    def calcular_boveda_v58(self, largo_m):
        """Bóveda Ferrotek: Base Perfil C18 + Arcos de Varilla (3.80m x 2.40m)"""
        ancho = 3.80
        altura = 2.40
        area_suelo = ancho * largo_m
        perimetro_base = (ancho + largo_m) * 2
        
        # 1. Base Guía: Perfil C Calibre 18 (Primeros 90cm de altura)
        costo_perfil_c = perimetro_base * 0.9 * 11500 # Valor est. perfil C18
        
        # 2. Arcos: Varilla corrugada cada 0.60m naciente del Perfil C
        num_arcos = math.ceil(largo_m / 0.6)
        longitud_arco = 5.20 # Longitud curva aprox para 3.80m de luz y 2.40m alto
        acero_arcos = (num_arcos * longitud_arco) * 8500 # Precio varilla
        
        # 3. Piel: Malla 5mm + Zaranda Doble + Mezcla 1:3:3
        area_curva = (longitud_arco * largo_m)
        mallas = area_curva * (self.p['malla_5mm_m2'] + 2*self.p['malla_zaranda_m2'])
        mezcla = area_curva * 0.045 * (5*self.p['cemento_bulto'] + 5*self.p['cal_bulto'] + self.p['arena_m3'])
        
        costo_dir = costo_perfil_c + acero_arcos + mallas + mezcla + (20 * self.p['valor_jornal'])
        return round(costo_dir / self.MARGEN, -3)