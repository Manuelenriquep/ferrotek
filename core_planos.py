# GUARDA ESTO COMO: core_planos.py

def dibujar_planta(modelo):
    # Definición de Colores (Estilo Arquitectónico)
    c_muro = "#2C3E50"    # Azul oscuro para bordes
    c_fondo = "#F9F9F9"   # Fondo gris muy claro
    c_social = "#FCF3CF"  # Amarillo suave (Zona Social)
    c_hab = "#D5F5E3"     # Verde menta (Descanso)
    c_bano = "#D6EAF8"    # Azul claro (Baños)
    c_cocina = "#FAD7A0"  # Naranja suave (Servicios)
    
    svg = ""
    
    # Función para crear rectángulos (habitaciones)
    def rect(x, y, w, h, color, texto, subtexto=""):
        scale = 40 # Escala de pixeles
        rx, ry, rw, rh = x*scale, y*scale, w*scale, h*scale
        font_s = "14" if w > 1.5 else "11"
        
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

    # --- DIBUJO DEL MODELO 1: SUITE ---
    if modelo == 1: 
        w_total, h_total = 5*40, 7*40
        svg += f'<svg width="100%" height="320" viewBox="0 0 {w_total} {h_total}" xmlns="http://www.w3.org/2000/svg">'
        # Distribución
        svg += rect(0, 0, 5, 1.5, c_cocina, "COCINA / ACCESO", "Kitchenette")
        svg += rect(0, 1.5, 5, 3.5, "#FFFFFF", "CAMA KING", "Vista Panorámica")
        svg += rect(0, 5, 5, 2, c_bano, "BAÑO / VESTIER", "Oculto tras cabecero")

    # --- DIBUJO DEL MODELO 2: COTIDIANA ---
    elif modelo == 2: 
        w_total, h_total = 5*40, 13*40
        svg += f'<svg width="100%" height="550" viewBox="0 0 {w_total} {h_total}" xmlns="http://www.w3.org/2000/svg">'
        # Distribución
        svg += rect(0, 0, 5, 5, c_social, "SALA - COMEDOR", "Cocina Abierta")
        svg += rect(1.5, 5, 2, 4, "#EAEDED", "PASILLO", "Circulación")
        svg += rect(0, 5, 1.5, 2.5, c_bano, "BAÑO", "Social")
        svg += rect(3.5, 5, 1.5, 2.5, "#E8DAEF", "ESTUDIO", "Lavado")
        svg += rect(0, 9, 2.5, 4, c_hab, "HABITACIÓN 1", "3.00 x 2.50")
        svg += rect(2.5, 9, 2.5, 4, c_hab, "HABITACIÓN 2", "3.00 x 2.50")

    # --- DIBUJO DEL MODELO 3: PATRIARCA ---
    elif modelo == 3: 
        w_total, h_total = 10*40, 11*40
        svg += f'<svg width="100%" height="450" viewBox="0 0 {w_total} {h_total}" xmlns="http://www.w3.org/2000/svg">'
        # Ala Izquierda
        svg += rect(0, 0, 3, 6, "#E8DAEF", "MASTER SUITE", "Principal")
        svg += rect(0, 6, 3, 5, c_bano, "BAÑO / VESTIER", "Privado")
        # Centro
        svg += rect(3, 0, 4, 7, c_social, "GRAN SALÓN", "Techo Alto")
        svg += rect(3, 7, 4, 4, c_cocina, "COCINA ISLA", "Comedor")
        # Ala Derecha
        svg += rect(7, 0, 3, 4, c_hab, "HABITACIÓN 2", "Auxiliar")
        svg += rect(7, 4, 3, 3, c_bano, "BAÑO", "Compartido")
        svg += rect(7, 7, 3, 4, c_hab, "HABITACIÓN 3", "Auxiliar")

    svg += "</svg>"
    return svg