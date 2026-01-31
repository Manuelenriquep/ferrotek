import math

class SistemaFerrotek:
    def __init__(self):
        # --- BASE DE PRECIOS FERROTEK (Ajusta según tu ferretería) ---
        self.precios = {
            "tubo_50x50": 65000,          # Unidad 6m (Calibre 18)
            "malla_electro": 150000,      # Panel
            "rollo_zaranda": 180000,      # Rollo 30m
            "tornillo_hex_ciento": 15000, # Bolsa x 100 (Estructural)
            "tornillo_lenteja_ciento": 8000, # Bolsa x 100 (Para Malla)
            
            # --- TU FÓRMULA MAESTRA ---
            "cemento": 42000,             # Bulto 50kg
            "cal_bulto": 18000,           # Bulto 25kg (Hidratada)
            "arena_m3": 120000,           # m3 Arena Fina
            
            "teja_pvc_m2": 48000,         # m2 útil
            "perfileria_techo_m2": 25000, # m2
            "mano_obra_m2": 220000        # A todo costo obra gris
        }

    def calcular_modelo(self, tipo_modelo):
        """Calcula materiales usando fórmula 1:3:3 (Cemento:Cal:Arena)"""
        
        # 1. DEFINICIÓN DE GEOMETRÍA
        if tipo_modelo == "1_alcoba":
            nombre = "Modelo 1: Suite Rural (36m2)"
            area_piso = 36.0 
            perimetro_muros = 36.0 
            baños = 1
        elif tipo_modelo == "2_alcobas":
            nombre = "Modelo 2: La Cotidiana (64m2)"
            area_piso = 64.0 
            perimetro_muros = 52.0 
            baños = 2
        elif tipo_modelo == "3_alcobas":
            nombre = "Modelo 3: La Patriarca (85m2)"
            area_piso = 85.0 
            perimetro_muros = 72.0 
            baños = 3
        else:
            return None

        # 2. CÁLCULO ESTRUCTURA (ESQUELETO METALICO)
        altura_muro = 2.40
        num_parales = math.ceil(perimetro_muros / 0.60)
        ml_parales = num_parales * altura_muro
        ml_soleras = perimetro_muros * 3 
        
        total_tubos = math.ceil((ml_parales + ml_soleras) / 6 * 1.05) # +5% desperdicio
        
        # Tornillos Estructurales (Hexagonales)
        total_tornillos_hex = num_parales * 12 
        bolsas_hex = math.ceil(total_tornillos_hex / 100)

        # 3. CÁLCULO PIEL (MALLAS)
        area_muros_total = perimetro_muros * altura_muro
        
        # Malla Electro (Doble cara)
        paneles = math.ceil((area_muros_total * 2 * 1.1) / (6 * 2.35))
        
        # Malla Zaranda (Doble cara)
        rollos_zaranda = math.ceil((area_muros_total * 2) / 45)
        
        # Tornillos Malla (Lenteja)
        ml_totales_tubo = ml_parales + ml_soleras
        total_tornillos_lenteja = (ml_totales_tubo * 3.3) * 2
        bolsas_lenteja = math.ceil(total_tornillos_lenteja / 100)

        # 4. CÁLCULO MEZCLA (FÓRMULA: 1 CEM : 3 CAL : 3 ARENA)
        # Volumen de mezcla para muros (5cm espesor total)
        vol_mortero_muros = area_muros_total * 0.05
        
        # Rendimientos estimados para la fórmula rica en cal:
        cemento_muros = vol_mortero_muros * 6.0   # Bultos
        cal_muros = vol_mortero_muros * 12.0      # Bultos (la cal rinde menos por peso)
        arena_muros = vol_mortero_muros * 1.1     # m3
        
        # PISO (Concreto puro 1:2:3, sin cal)
        vol_piso = area_piso * 0.10
        cemento_piso = vol_piso * 7.0 
        arena_piso = vol_piso * 0.5
        
        total_cemento = math.ceil(cemento_muros + cemento_piso)
        total_cal = math.ceil(cal_muros)
        total_arena = round(arena_muros + arena_piso, 1)

        # 5. COSTOS
        area_techo = area_piso * 1.35
        costo_techo = area_techo * (self.precios["teja_pvc_m2"] + self.precios["perfileria_techo_m2"])

        costo_materiales = (
            (total_tubos * self.precios["tubo_50x50"]) +
            (bolsas_hex * self.precios["tornillo_hex_ciento"]) +      
            (bolsas_lenteja * self.precios["tornillo_lenteja_ciento"]) + 
            (paneles * self.precios["malla_electro"]) +
            (rollos_zaranda * self.precios["rollo_zaranda"]) +
            (total_cemento * self.precios["cemento"]) +
            (total_cal * self.precios["cal_bulto"]) +  
            (total_arena * self.precios["arena_m3"]) +
            costo_techo
        )
        
        costo_mo = area_piso * self.precios["mano_obra_m2"]
        costo_total = costo_materiales + costo_mo

        return {
            "Modelo": nombre,
            "Area": f"{area_piso} m2",
            "Configuracion": f"{int(tipo_modelo[0])} Alcobas / {baños} Baños",
            "Resumen_Estructura": {
                "Tubos_50x50": total_tubos,
                "Tornillos_Estructurales_HEX": f"{bolsas_hex} Bolsas"
            },
            "Resumen_Piel": {
                "Malla_Electro": paneles,
                "Zaranda_Rollos": rollos_zaranda,
                "Tornillos_Fijacion_LENTEJA": f"{bolsas_lenteja} Bolsas"
            },
            "Resumen_Mezcla_Impermeable": {
                "Cemento": f"{total_cemento} Bultos",
                "Cal_Hidratada": f"{total_cal} Bultos (25kg)",
                "Arena_Fina": f"{total_arena} m3"
            },
            "costo_total": costo_total,
            "precio_venta": costo_total * 1.30 
        }