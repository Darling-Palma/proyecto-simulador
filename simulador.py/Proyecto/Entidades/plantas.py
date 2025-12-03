import os
import pygame
from .entidad import Entidad
from ..logica.utilidades import cargar_imagen_segura

class Planta(Entidad):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.tamano = 15
        self.vida = 100
        self.imagen = cargar_imagen_segura(os.path.join(os.path.dirname(__file__), '..', 'imagenes', 'planta.png'), tam=(15,15), color=(0,255,0))
        self.rect = pygame.Rect(x, y, 15, 15)
    def crecer(self):
        self.vida -= 0.01
    def dibujar(self, surf):
        surf.blit(self.imagen, (self.x, self.y))

class Alga(Entidad):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.tamano = 12
        self.imagen = cargar_imagen_segura(os.path.join(os.path.dirname(__file__), '..', 'imagenes', 'alga.png'), tam=(12,12), color=(0,100,0))
    def dibujar(self, surf):
        surf.blit(self.imagen, (self.x, self.y))
