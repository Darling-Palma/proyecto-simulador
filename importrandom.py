import pygame
import random
import math
import os

# -----------------------------------
# CONFIGURACIÓN INICIAL
# -----------------------------------
ANCHO, ALTO = 800, 600
FPS = 20
GROSOR_ORILLA = 20

pygame.init()
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Simulador de Ecosistema (Con Casa)")
reloj = pygame.time.Clock()
# --- Definición de rutas de imágenes ---
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()
IMAGES_DIR = os.path.join(BASE_DIR, "imagenes")
# ----------------------------------------------
# --- Nuevas configuraciones para Corazones y Botón ---
ESTADO_JUEGO = "MENU" # Nuevo estado para el control del juego
COLOR_MENU = (100, 100, 100)
COLOR_BOTON = (0, 200, 0)
COLOR_TEXTO = (255, 255, 255)
FUENTE_GRANDE = pygame.font.SysFont(None, 48)
FUENTE_MEDIANA = pygame.font.SysFont(None, 32)
fuente_nombre = pygame.font.SysFont(None, 16) # Fuente para nombres
# Cargar imagen de corazón (rojo/roto para simplificación)
TAMANO_CORAZON = 10
USAR_IMAGEN_CORAZON = False
IMAGEN_CORAZON_LLENO = None
IMAGEN_CORAZON_VACIO = None

# --- Carga de Corazones (movida aquí después de definir la función) ---
try:
    RUTA_CORAZON_LLENO = os.path.join(IMAGES_DIR, "corazon_lleno.png")
    RUTA_CORAZON_VACIO = os.path.join(IMAGES_DIR, "corazon_vacio.png")
    IMAGEN_CORAZON_LLENO = cargar_imagen_segura(RUTA_CORAZON_LLENO, tam=(TAMANO_CORAZON, TAMANO_CORAZON), color=(255, 0, 0))
    IMAGEN_CORAZON_VACIO = cargar_imagen_segura(RUTA_CORAZON_VACIO, tam=(TAMANO_CORAZON, TAMANO_CORAZON), color=(50, 0, 0))
    # Comprobar si la carga fue exitosa (si no, devuelve un Surface con color)
    if IMAGEN_CORAZON_LLENO.get_width() == TAMANO_CORAZON: # Un chequeo simple
        USAR_IMAGEN_CORAZON = True
except Exception:
    USAR_IMAGEN_CORAZON = False
# -----------------------------------------------------------------
# --- NUEVO: Cargar fondos ---
try:
    FONDO_JUEGO = cargar_imagen_segura(os.path.join(IMAGES_DIR, "fondo.png"), tam=(ANCHO, ALTO))
except Exception:
    FONDO_JUEGO = pygame.Surface((ANCHO, ALTO)); FONDO_JUEGO.fill((135, 206, 235))

try:
    FONDO_MENU = cargar_imagen_segura(os.path.join(IMAGES_DIR, "menu_fondo.png"), tam=(ANCHO, ALTO))
except Exception:
    FONDO_MENU = pygame.Surface((ANCHO, ALTO)); FONDO_MENU.fill(COLOR_MENU)
# ----------------------------
# --- Nueva función para dibujar corazones ---
def dibujar_corazones(superficie, x, y, vida_porcentaje, max_corazones=3):
    """Dibuja corazones para representar la vida."""
    corazones_llenos = math.ceil(vida_porcentaje / 100 * max_corazones)
    
    start_x = x + 35 // 2 - (max_corazones * TAMANO_CORAZON + (max_corazones - 1) * 2) // 2
    
    for i in range(max_corazones):
        corazon_x = start_x + i * (TAMANO_CORAZON + 2)
        corazon_y = y - 8 - TAMANO_CORAZON
        
        if i < corazones_llenos:
            if USAR_IMAGEN_CORAZON:
                superficie.blit(IMAGEN_CORAZON_LLENO, (corazon_x, corazon_y))
            else:
                pygame.draw.circle(superficie, (255, 0, 0), (corazon_x + TAMANO_CORAZON // 2, corazon_y + TAMANO_CORAZON // 2), TAMANO_CORAZON // 2)
        else:
            if USAR_IMAGEN_CORAZON:
                superficie.blit(IMAGEN_CORAZON_VACIO, (corazon_x, corazon_y)) # CORRECCIÓN: Usar corazon_x, corazon_y sin desplazamiento
            else:
                pygame.draw.circle(superficie, (50, 0, 0), (corazon_x + TAMANO_CORAZON // 2, corazon_y + TAMANO_CORAZON // 2), TAMANO_CORAZON // 2)
                pygame.draw.circle(superficie, (255, 255, 255), (corazon_x + TAMANO_CORAZON // 2, corazon_y + TAMANO_CORAZON // 2), TAMANO_CORAZON // 2, 1)

# -----------------------------------
# CLASES BASE
# -----------------------------------
class Entidad:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def dibujar(self, superficie):
        pass
def envejecer(self):
        self.vida -= random.uniform(0.01, 0.04)

    def esta_vivo(self):
        return self.vida > 0

    def dibujar(self, superficie):
        # *** AGREGADO PARA EL CLIC: Definir el rect ***
        self.rect = self.imagen.get_rect(topleft=(self.x, self.y)) 
        # **********************************************
        superficie.blit(self.imagen, (self.x, self.y))
        dibujar_corazones(superficie, self.x, self.y, self.vida)
        texto_nombre = fuente_nombre.render(self.nombre, True, (0, 0, 0))
        
        texto_rect = texto_nombre.get_rect(centerx=self.x + self.tamano // 2)
        texto_rect.y = self.y + self.tamano + 2
        superficie.blit(texto_nombre, texto_rect)

# -----------------------------------
# CLASES DE ANIMALES
# -----------------------------------
# -----------------------------------
# PLANTA (CON IMAGEN)
# -----------------------------------
class Planta(Entidad):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.tamano = 15
        ruta_img = os.path.join(IMAGES_DIR, "planta.png")
        self.imagen = cargar_imagen_segura(ruta_img, tam=(self.tamano, self.tamano), color=(34, 139, 34))
        self.rect = pygame.Rect(x - self.tamano // 2, y - self.tamano // 2, self.tamano, self.tamano)

    def dibujar(self, superficie):
        superficie.blit(self.imagen, (self.x, self.y))

# -----------------------------------
# FLOR (NUEVA CLASE PARA DECORACIÓN)
# -----------------------------------
class Flor(Entidad):
    def __init__(self, x, y):
        super().__init__(x, y)
        flor_options = {
            "flor_roja.png": (15, 20), 
            "flor_azul.png": (30, 30),
            "flor_amarilla.png": (15, 20)
        }
        
        flor_elegida = random.choice(list(flor_options.keys()))
        tamano_elegido = flor_options[flor_elegida]
        
        self.tamano = max(tamano_elegido)
        ruta_img = os.path.join(IMAGES_DIR, flor_elegida)
        self.imagen = cargar_imagen_segura(ruta_img, tam=tamano_elegido, color=(255, 100, 100))
        self.rect = pygame.Rect(x - self.tamano // 2, y - self.tamano // 2, tamano_elegido[0], tamano_elegido[1])

    def dibujar(self, superficie):
        superficie.blit(self.imagen, (self.x, self.y))

# -----------------------------------
# ALGA (CON IMAGEN)
# -----------------------------------
class Alga(Entidad):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.tamano = 12
        ruta_img = os.path.join(IMAGES_DIR, "alga.png")
        self.imagen = cargar_imagen_segura(ruta_img, tam=(self.tamano, self.tamano), color=(40, 120, 50))
        self.rect = pygame.Rect(x - self.tamano // 2, y - self.tamano // 2, self.tamano, self.tamano)

    def dibujar(self, superficie):
        superficie.blit(self.imagen, (self.x, self.y))
# -----------------------------------
# ÁRBOL
# -----------------------------------
class Arbol(Entidad):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.tamano = 40
        ruta_img = os.path.join(IMAGES_DIR, "arbol.png")
        self.imagen = cargar_imagen_segura(ruta_img, tam=(self.tamano, self.tamano), color=(139, 69, 19))
        self.rect = pygame.Rect(x, y, self.tamano, self.tamano)

    def dibujar(self, superficie):
        superficie.blit(self.imagen, (self.x, self.y))
# -----------------------------------
# NUEVO: CLASE CASA
# -----------------------------------
class Casa(Entidad):
    def __init__(self, x, y, tamano=60):
        super().__init__(x, y)
        self.tamano = tamano
        ruta_img = os.path.join(IMAGES_DIR, "casa.png")
        self.imagen = cargar_imagen_segura(ruta_img, tam=(self.tamano, self.tamano), color=(160, 82, 45)) # Color sienna
        self.rect = pygame.Rect(x, y, self.tamano, self.tamano)

    def dibujar(self, superficie):
        superficie.blit(self.imagen, (self.x, self.y))
