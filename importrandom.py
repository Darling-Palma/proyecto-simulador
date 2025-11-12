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
