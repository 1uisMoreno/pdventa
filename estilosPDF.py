def diccionario_colores(color): 
    colores = {
        'Negro' : (0,0,0), 
        'Blanco' : (255,255,255),
        'Azul Fuerte' : (0,112,192),
        'Azul Bajo' : (0,176,240),
        'Azul Cielo Tabla': (222,234,246),
        'Azul Inicio Tabla':(0,170,230),
        'Rojo':(200,0,0)
        }

    return colores[color]

def color_contorno(hoja, color):
    cr, cg, cb = diccionario_colores(color)
    hoja.set_draw_color(r= cr, g = cg, b= cb)
    
def color_fondo(hoja,color):
    cr, cg, cb = diccionario_colores(color)
    hoja.set_fill_color(r= cr, g = cg, b= cb)

def color_texto(hoja, color):
    cr, cg, cb = diccionario_colores(color)
    hoja.set_text_color(r= cr, g = cg, b= cb)
    
def tamaño_texto(hoja, size):
    hoja.set_font_size(size)

def fuente_texto(hoja, estilo, fuente='Arial'):
    hoja.set_font(fuente, style=estilo)