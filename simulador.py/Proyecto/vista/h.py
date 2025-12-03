import random, os
from ..entidades.animales import Vaca, Gallina, Zorro, Caballo, Oso, Cerdo, Lobo, Rana, Pez
from ..logica.utilidades import ANCHO, ALTO, generar_spawn_seguro

def manejar_clic_animal(pos, eco):
    x, y = pos[0]-17, pos[1]-17
    rect = None
    try:
        import pygame
        rect = pygame.Rect(x, y, 35, 35)
    except:
        pass
    obs = eco.obtener_obstaculos()
    en_agua = False
    try:
        en_agua = eco.lago.rect_agua.colliderect(rect)
    except:
        en_agua = False
    cls = random.choice([Vaca, Gallina, Zorro, Caballo, Oso, Cerdo, Lobo, Rana])
    if en_agua: eco.agregar_animal(Pez(x, y))
    else: eco.agregar_animal(cls(x, y))
