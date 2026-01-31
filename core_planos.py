def dibujar_planta(modelo):
    # Colores
    c_muro = "#2C3E50"
    c_fondo = "#F9F9F9"
    c_social = "#FCF3CF"
    c_hab = "#D5F5E3"
    c_bano = "#D6EAF8"
    c_cocina = "#FAD7A0"
    
    svg = ""
    
    # Función auxiliar para dibujar rectángulos con texto
    def rect(x, y, w, h, color, texto, subtexto=""):
        # Escala: Multiplicamos por 40 pixeles para que se vea bien
        scale = 40 
        rx, ry, rw, rh = x*scale, y*scale, w*scale, h*scale
        
        # Tamaño de letra dinámico
        font_s = "14" if w > 1.5 else "12"
        
        return f"""
        <g>
            <rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" 
                  style="fill:{color};stroke:{c_muro};stroke-width:2;fill-opacity:0.8" />
            <text x="{rx + rw/2}" y="{ry + rh/2 - 5}" font-family="Arial" font-size="{font_s}" 
                  fill="{c_muro}" font-weight="bold" text-anchor="middle">{texto}</text>
            <text x="{rx + rw/2}" y="{ry + rh/2 + 10}" font-family="Arial" font-size="10" 
                  fill="#555" text-anchor="middle">{subtexto}</text>
        </g>
        """

    if modelo == 1: # MODELO 1: SUITE (5x7)
        # Lienzo de 5x7 metros
        w_total, h_total = 5*40, 7*40
        svg += f'<svg width="100%" height="350" viewBox="0 0 {w_total} {h_total}" xmlns="http://www.w3.org/2000/svg">'
        
        # Distribución (Y crece hacia abajo)
        svg += rect(0, 0, 5, 1.5, c_cocina, "COCINA / ACCESO", "Kitchenette")
        svg += rect(0, 1.5, 5, 3.5, "#FFFFFF", "ZONA CAMA KING", "Vista al Ventanal")
        svg += rect(0, 5, 5, 2, c_bano, "BAÑO / VESTIER", "Oculto tras cabecero")
        
    elif modelo == 2: # MODELO 2: COTIDIANA (5x13)
        w_total, h_total = 5*40, 13*40
        svg += f'<svg width="100%" height="600" viewBox="0 0 {w_total} {h_total}" xmlns="http://www.w3.org/2000/svg">'
        
        svg += rect(0, 0, 5, 5, c_social, "SALA - COMEDOR", "Cocina Abierta")
        svg += rect(1.5, 5, 2, 4, "#EAEDED", "PASILLO", "Circulación")
        svg += rect(0, 5, 1.5, 2.5, c_bano, "BAÑO", "Social")
        svg += rect(3.5, 5, 1.5, 2.5, "#E8DAEF", "ESTUDIO", "Lavado")
        svg += rect(0, 9, 2.5, 4, c_hab, "HABITACIÓN 1", "3.00 x 2.50")
        svg += rect(2.5, 9, 2.5, 4, c_hab, "HABITACIÓN 2", "3.00 x 2.50")

    elif modelo == 3: # MODELO 3: HACIENDA (10x11)
        w_total, h_total = 10*40, 11*40
        svg += f'<svg width="100%" height="500" viewBox="0 0 {w_total} {h_total}" xmlns="http://www.w3.org/2000/svg">'
        
        # Ala Izquierda (Master)
        svg += rect(0, 0, 3, 6, "#E8DAEF", "MASTER SUITE", "Principal")
        svg += rect(0, 6, 3, 5, c_bano, "BAÑO / VESTIER", "Privado")
        
        # Centro (Social)
        svg += rect(3, 0, 4, 7, c_social, "GRAN SALÓN", "Techo Alto")
        svg += rect(3, 7, 4, 4, c_cocina, "COCINA ISLA", "Comedor")
        
        # Ala Derecha (Auxiliar)
        svg += rect(7, 0, 3, 4, c_hab, "HABITACIÓN 2", "Auxiliar")
        svg += rect(7, 4, 3, 3, c_bano, "BAÑO", "Compartido")
        svg += rect(7, 7, 3, 4, c_hab, "HABITACIÓN 3", "Auxiliar")

    svg += "</svg>"
    return svg