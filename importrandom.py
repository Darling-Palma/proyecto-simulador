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
