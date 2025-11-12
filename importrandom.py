# -----------------------------------
# FUNCIONES ÚTILES
# -----------------------------------
def distancia(a, b):
    # --- CORREGIDO: Acepta objetos o diccionarios ---
    try:
        ax = a.x if hasattr(a, 'x') else a['x']
        ay = a.y if hasattr(a, 'y') else a['y']
        bx = b.x if hasattr(b, 'x') else b['x']
        by = b.y if hasattr(b, 'y') else b['y']
        
        # Corrección: math.sqrt((ax - bx) ** 2 + (ay - by) ** 2)
        dist = math.sqrt((ax - bx) ** 2 + (ay - by) ** 2)
        return max(1, dist)
    except (AttributeError, KeyError):
        return float('inf')


def cargar_imagen_segura(ruta, tam=(40, 40), color=(200, 200, 200), flip_horizontal=False):
    try:
        img = pygame.image.load(ruta).convert_alpha() # Usar convert_alpha para transparencias
        img = pygame.transform.scale(img, tam)
        if flip_horizontal: # Aplicar flip si se solicita
            img = pygame.transform.flip(img, True, False)
        return img
    except Exception as e:
        print(f"[WARN] No se pudo cargar {ruta}: {e}. Usando color de fondo.")
        # --- CORREGIDO: No usar SRCALPHA para el fallback de color sólido ---
        surf = pygame.Surface(tam) 
        surf.fill(color)
        return surf

def normalizar_vector(dx, dy):
    # Corrección: math.sqrt(dx**2 + dy**2)
    magnitud = math.sqrt(dx**2 + dy**2)
    if magnitud == 0:
        return 0, 0
    return dx / magnitud, dy / magnitud

def generar_spawn_seguro(obstaculos_rects, tamano_entidad):
    while True:
        x = random.randint(0, ANCHO - tamano_entidad)
        y = random.randint(0, ALTO - tamano_entidad)
        spawn_rect = pygame.Rect(x, y, tamano_entidad, tamano_entidad)
        
        en_obstaculo = False
        for obstaculo in obstaculos_rects:
            if spawn_rect.colliderect(obstaculo):
                en_obstaculo = True
                break
        
        if not en_obstaculo:
            return x, y
