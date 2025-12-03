from ..entidades.plantas import Planta, Alga
from ..entidades.objetos import Arbol, Casa, Lago, Huevo
from ..entidades.animales import *
from ..logica.utilidades import generar_spawn_seguro
import random

class Ecosistema:
    def __init__(self):
        self.animales = []
        self.plantas = []
        self.algas = []
        self.arboles = []
        self.huevos = []
        self.casa = None
        self.lago = None

    def agregar_animal(self, a): self.animales.append(a)
    def obtener_obstaculos(self):
        obs = [a.rect for a in self.arboles]
        if self.casa: obs.append(self.casa.rect)
        if self.lago: obs.append(self.lago.rect_orilla)
        return obs

    def actualizar(self):
        self.animales = [a for a in self.animales if a.esta_vivo()]
        for a in self.animales: 
            a.actualizar(self)
        for p in self.plantas: 
            p.crecer()
        for h in self.huevos[:]:
            h.incubar(self) if hasattr(h, 'incubar') else None

        if len(self.plantas) < 50:
            x, y = generar_spawn_seguro(self.obtener_obstaculos(), 10)
            self.plantas.append(Planta(x, y))

        if len(self.huevos) >= 5:
            for _ in range(5): self.huevos.pop(0)
            x, y = generar_spawn_seguro(self.obtener_obstaculos(), 35)
            self.agregar_animal(Gallina(x, y))

    def dibujar(self, surf):
        if self.lago: self.lago.dibujar(surf)
        for x in self.algas + self.plantas + self.huevos + self.arboles: x.dibujar(surf)
        if self.casa: self.casa.dibujar(surf)
        for a in self.animales: a.dibujar(surf)

def inicializar():
    eco = Ecosistema()
    eco.casa = Casa(800 - 120, 20)
    eco.lago = Lago(800//2 - 150, 600 - 200, 300, 150)
    for p in [(50, 50), (150, 100), (300, 30), (700, 400)]:
        eco.arboles.append(Arbol(*p))
    obs = eco.obtener_obstaculos()
    for _ in range(30):
        x,y = generar_spawn_seguro(obs, 10)
        eco.plantas.append(Planta(x, y))
    clases = [Vaca, Gallina, Zorro, Caballo, Oso, Cerdo, Lobo, Rana]
    cantidades = [3, 5, 1, 2, 1, 2, 1, 2]
    for cls, cant in zip(clases, cantidades):
        for _ in range(cant):
            x, y = 0, 0
            if cls == Rana: x, y = random.randint(0, 800), random.randint(0, 600)
            else: x, y = generar_spawn_seguro(obs, 35)
            if x != 0 or y != 0:
                eco.agregar_animal(cls(x, y))
    for _ in range(4):
        r = eco.lago.rect_agua
        x, y = random.randint(r.x, r.right-30), random.randint(r.y, r.bottom-30)
        eco.agregar_animal(Pez(x, y))
    return eco
