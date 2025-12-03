import os, pygame
from .entidad import Entidad
from ..logica.utilidades import cargar_imagen_segura, GROSOR_ORILLA

class Huevo(Entidad):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.tamano = 15
        self.imagen = cargar_imagen_segura(os.path.join(os.path.dirname(__file__), '..', 'imagenes', 'huevo.png'), tam=(15,15))
        self.rect = self.imagen.get_rect(topleft=(x, y))
    def incubar(self, eco):
        # placeholder, incubacion manejada por ecosistema
        pass
    def dibujar(self, surf):
        surf.blit(self.imagen, (self.x, self.y))

class Arbol(Entidad):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.tamano = 40
        self.imagen = cargar_imagen_segura(os.path.join(os.path.dirname(__file__), '..', 'imagenes', 'arbol.png'), tam=(40,40))
        self.rect = self.imagen.get_rect(topleft=(x, y))
    def dibujar(self, surf):
        surf.blit(self.imagen, (self.x, self.y))

class Casa(Entidad):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.tamano = 100
        self.imagen = cargar_imagen_segura(os.path.join(os.path.dirname(__file__), '..', 'imagenes', 'casa.png'), tam=(100,100))
        self.rect = self.imagen.get_rect(topleft=(x, y))
    def dibujar(self, surf):
        surf.blit(self.imagen, (self.x, self.y))

class Lago:
    def __init__(self, x, y, w, h):
        self.rect_orilla = pygame.Rect(x, y, w, h)
        self.rect_agua = pygame.Rect(x + GROSOR_ORILLA, y + GROSOR_ORILLA, w - 2*GROSOR_ORILLA, h - 2*GROSOR_ORILLA)
        self.img_orilla = cargar_imagen_segura(os.path.join(os.path.dirname(__file__), '..', 'imagenes', 'orilla.png'), tam=(w,h), color=(210,180,140))
        self.img_agua = cargar_imagen_segura(os.path.join(os.path.dirname(__file__), '..', 'imagenes', 'lago.png'), tam=(self.rect_agua.width, self.rect_agua.height), color=(0,0,139))
    def dibujar(self, surf):
        surf.blit(self.img_orilla, self.rect_orilla)
        surf.blit(self.img_agua, self.rect_agua)
