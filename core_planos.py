def dibujar_planta(modelo):
    # Colores
    c_muro = "#2C3E50"    
    c_fondo = "#F9F9F9"   
    c_social = "#FCF3CF"  
    c_hab = "#D5F5E3"     
    c_bano = "#D6EAF8"    
    c_cocina = "#FAD7A0"  
    
    # 1. Definir tamaño del lienzo
    if modelo == 1: w, h = 5, 7
    elif modelo == 2: w, h = 5, 13
    elif modelo == 3: w, h = 10, 11
    else: w, h = 5, 5
    
    # --- AQUÍ ESTABA EL ERROR ---
    # Antes tenías: svg = "" (Esto estaba mal)
    # AHORA DEBE DECIR ESTO:
    svg = f'<svg width="100%" height="{h*45}" viewBox="0 0 {w*40} {h*40}" xmlns="http://www.w3.org/2000/svg">'
    # ----------------------------

    # Función auxiliar para dibujar
    def rect(x, y, w_rect, h_rect, color, texto, subtexto=""):
        scale = 40 
        rx, ry, rw, rh = x*scale, y*scale, w_rect*scale, h_rect*scale
        font_s = "14" if w_rect > 1.5 else "11"
        return f"""
        <g>
            <rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" 
                  style="fill:{color};stroke:{c_muro};stroke-width:2;fill-opacity:0.9" />
            <text x="{rx + rw/2}" y="{ry + rh/2 - 7}" font-family="sans-serif" font-size="{font_s}" 
                  fill="{c_muro}" font-weight="bold" text-anchor="middle">{texto}</text>
            <text x="{rx + rw/2}" y="{ry + rh/2 + 10}" font-family="sans-serif" font-size="10" 
                  fill="#555" text-anchor="middle">{subtexto}</text>
        </g>
        """

    # 2. Dibujar distribución
    if modelo == 1: 
        svg += rect(0, 0, 5, 1.5, c_cocina, "COCINA / ACCESO", "Kitchenette")
        svg += rect(0, 1.5, 5, 3.5, "#FFFFFF", "CAMA KING", "Vista Panorámica")
        svg += rect(0, 5, 5, 2, c_bano, "BAÑO / VESTIER", "Oculto tras cabecero")

    elif modelo == 2: 
        svg += rect(0, 0, 5, 5, c_social, "SALA - COMEDOR", "Cocina Abierta")
        svg += rect(1.5, 5, 2, 4, "#EAEDED", "PASILLO", "Circulación")
        svg += rect(0, 5, 1.5, 2.5, c_bano, "BAÑO", "Social")
        svg += rect(3.5, 5, 1.5, 2.5, "#E8DAEF", "ESTUDIO", "Lavado")
        svg += rect(0, 9, 2.5, 4, c_hab, "HABITACIÓN 1", "3.00 x 2.50")
        svg += rect(2.5, 9, 2.5, 4, c_hab, "HABITACIÓN 2", "3.00 x 2.50")

    elif modelo == 3: 
        svg += rect(0, 0, 3, 6, "#E8DAEF", "MASTER SUITE", "Principal")
        svg += rect(0, 6, 3, 5, c_bano, "BAÑO / VESTIER", "Privado")
        svg += rect(3, 0, 4, 7, c_social, "GRAN SALÓN", "Techo Alto")
        svg += rect(3, 7, 4, 4, c_cocina, "COCINA ISLA", "Comedor")
        svg += rect(7, 0, 3, 4, c_hab, "HABITACIÓN 2", "Auxiliar")
        svg += rect(7, 4, 3, 3, c_bano, "BAÑO", "Compartido")
        svg += rect(7, 7, 3, 4, c_hab, "HABITACIÓN 3", "Auxiliar")

    # 3. Cierre
    svg += "</svg>"
    
    return svg