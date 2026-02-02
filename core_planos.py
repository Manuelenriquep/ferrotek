import math

class CoreFerrotek:
    """
    Núcleo de Ingeniería Ferrotek v56.0
    Basado en 20 años de investigación en morteros y estructuras Unibody.
    """
    
    def __init__(self, precios):
        self.p = precios # Recibe el diccionario de precios desde la DB
        self.H_VISTA = 2.20
        self.H_MALLA = 2.35
        self.ZAPATA_RAIZ = 0.15 # 15cm excedentes para enterrar

    def calcular_cerramiento_perimetral(self, ml):
        """Muro de Cerramiento con Sistema Raíz y Matriz 1:3:3"""
        # Estructura: Postes de 2" cada 1.50m
        cant_postes = math.ceil(ml / 1.5) + 1
        mts_perfil = cant_postes * (self.H_VISTA + 0.6) # Incluye dado de concreto
        costo_acero = mts_perfil * self.p['perfil_2_pulg_mt']
        
        # Blindaje: Malla 5mm + Zaranda (Simple Membrana para cerramiento)
        area_malla = ml * self.H_MALLA
        costo_mallas = (area_malla * self.p['malla_5mm_m2']) + (area_malla * 2 * self.p['malla_zaranda_m2'])
        
        # Matriz: 1 Cemento, 3 Arena, 3 Cal (4cm espesor)
        vol_mezcla = (ml * self.H_VISTA * 0.04) * 1.10 # 10% desperdicio
        costo_mezcla = vol_mezcla * (5 * self.p['cemento_bulto'] + 5 * self.p['cal_bulto'] + self.p['arena_m3'])
        
        # Mano de Obra: Rendimiento industrializado
        costo_mo = (ml * 0.8) * self.p['valor_jornal']
        
        directo = costo_acero + costo_mallas + costo_mezcla + costo_mo
        return {"total": directo, "ml": directo/ml, "postes": cant_postes}

    def calcular_muros_vivienda(self, perimetro_ext, divisiones_int):
        """Lógica Unificada: Fachada (Doble Membrana) vs Internos (Simple)"""
        
        # 1. FACHADAS (Doble Membrana - Confort Térmico)
        area_ext = perimetro_ext * self.H_VISTA
        mallas_ext = area_ext * (self.p['malla_5mm_m2'] + 2 * self.p['malla_zaranda_m2'])
        mortero_ext = (area_ext * 0.05) * (5 * self.p['cemento_bulto'] + 5 * self.p['cal_bulto'] + self.p['arena_m3'])
        
        # 2. INTERNOS (Membrana Simple - Ganancia de Área)
        area_int = divisiones_int * self.H_VISTA
        mallas_int = area_int * (self.p['malla_5mm_m2'] + self.p['malla_zaranda_m2'])
        mortero_int = (area_int * 0.035) * (5 * self.p['cemento_bulto'] + 5 * self.p['cal_bulto'] + self.p['arena_m3'])
        
        # 3. ESTRUCTURA COMPLETA (Postes 2" @ 1.5m)
        cant_postes = math.ceil((perimetro_ext + divisiones_int) / 1.5)
        costo_acero = (cant_postes * 3.0) * self.p['perfil_2_pulg_mt']
        
        total_muros = mallas_ext + mortero_ext + mallas_int + mortero_int + costo_acero
        return total_muros

    def calcular_piso_polimerico(self, area_m2):
        """Matriz 2:1 con Polímeros y Sellado en Poliuretano"""
        # Cemento rico + Aditivo F1 + Sellado FX
        costo_quimicos = area_m2 * (0.25 * self.p['aditivo_F1_kg'] + 0.12 * self.p['sellado_FX_galon'])
        vol_mezcla = (area_m2 * 0.05) * (10 * self.p['cemento_bulto'] + self.p['arena_m3'])
        return costo_quimicos + vol_mezcla