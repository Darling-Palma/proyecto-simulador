import pygame, os, math, random

ANCHO, ALTO = 800, 600
FPS = 20
GROSOR_ORILLA = 20

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()
IMAGES_DIR = os.path.join(os.path.dirname(BASE_DIR), "imagenes")

ARCHIVO_GUARDADO = "partida_guardada.json"

def cargar_imagen_segura(ruta, tam=(40, 40), color=(200, 200, 200), flip_horizontal=False):
    try:
        img = pygame.image.load(ruta).convert_alpha()
        img = pygame.transform.scale(img, tam)
        if flip_horizontal:
            img = pygame.transform.flip(img, True, False)
        return img
    except Exception:
        surf = pygame.Surface(tam)
        surf.fill(color)
        return surf

def distancia(obj1, obj2):
    try:
        x1 = obj1.x if hasattr(obj1, 'x') else obj1[0]
        y1 = obj1.y if hasattr(obj1, 'y') else obj1[1]
        x2 = obj2.x if hasattr(obj2, 'x') else obj2[0]
        y2 = obj2.y if hasattr(obj2, 'y') else obj2[1]
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    except:
        return float('inf')

def normalizar_vector(dx, dy):
    m = math.sqrt(dx**2 + dy**2)
    return (0, 0) if m == 0 else (dx/m, dy/m)

def generar_spawn_seguro(obstaculos, tam):
    for _ in range(1000):
        x = random.randint(0, ANCHO - tam)
        y = random.randint(0, ALTO - tam)
        rect_prueba = pygame.Rect(x, y, tam, tam)
        if not any(rect_prueba.colliderect(obs) for obs in obstaculos):
            return x, y
    return 0, 0
