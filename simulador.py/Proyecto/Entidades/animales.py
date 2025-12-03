import os, random, pygame
from .entidad import Entidad
from ..logica.utilidades import cargar_imagen_segura, distancia, normalizar_vector, ANCHO, ALTO, generar_spawn_seguro
from .objetos import Huevo

class Animal(Entidad):
    def __init__(self, nombre, tipo, x, y, img_path, default_face_left=False):
        super().__init__(x, y)
        self.nombre = nombre
        self.tipo = tipo
        self.vida = 100
        self.tamano = 35
        self.velocidad = random.randint(1,3)
        base = cargar_imagen_segura(img_path, tam=(35,35))
        self.img_R = pygame.transform.flip(base, True, False) if default_face_left else base
        self.img_L = base if default_face_left else pygame.transform.flip(base, True, False)
        self.imagen = self.img_L if default_face_left else self.img_R
        self.mirando_izq = default_face_left
        self.target_x, self.target_y = random.randint(0, ANCHO), random.randint(0, ALTO)
        self.timer = 0
        self.rect = self.imagen.get_rect(topleft=(x, y))

    def mover(self, tx, ty, ecosistema):
        if tx is None:
            self.timer -= 1
            if self.timer <= 0 or distancia(self, (self.target_x, self.target_y)) < self.velocidad:
                self.target_x, self.target_y = random.randint(0, ANCHO), random.randint(0, ALTO)
                self.timer = random.randint(60, 180)
            tx, ty = self.target_x, self.target_y
        dx, dy = tx - self.x, ty - self.y
        if abs(dx) < 2 and abs(dy) < 2: return
        if dx < 0 and not self.mirando_izq:
            self.imagen = self.img_L; self.mirando_izq = True
        elif dx > 0 and self.mirando_izq:
            self.imagen = self.img_R; self.mirando_izq = False
        ndx, ndy = normalizar_vector(dx, dy)
        mx, my = ndx * self.velocidad, ndy * self.velocidad
        obstaculos = ecosistema.obtener_obstaculos()
        es_acuatico = self.tipo in ["Pez", "Rana"]
        if not any(pygame.Rect(self.x + mx, self.y, self.tamano, self.tamano).colliderect(o) for o in obstaculos) or es_acuatico:
            self.x += mx
        if not any(pygame.Rect(self.x, self.y + my, self.tamano, self.tamano).colliderect(o) for o in obstaculos) or es_acuatico:
            self.y += my
        if self.tipo != "Pez":
            self.x = max(0, min(ANCHO - self.tamano, self.x))
            self.y = max(0, min(ALTO - self.tamano, self.y))
        self.rect.topleft = (self.x, self.y)

    def envejecer(self):
        self.vida -= random.uniform(0.01, 0.04)
    def esta_vivo(self):
        return self.vida > 0
    def dibujar(self, surf):
        surf.blit(self.imagen, (self.x, self.y))

# Specific animals (abridged but functional)
class Vaca(Animal):
    def __init__(self, x, y):
        super().__init__("Vaca", "herbivoro", x, y, os.path.join(os.path.dirname(__file__), '..', 'imagenes', 'vaca.png'), True)
        self.leche = 0; self.cnt = 0
    def actualizar(self, eco):
        t = None
        if self.vida < 90 and eco.plantas:
            obj = min(eco.plantas, key=lambda p: distancia(self, p))
            if distancia(self, obj) < 15: eco.plantas.remove(obj); self.vida = min(100, self.vida+15)
            else: t = (obj.x, obj.y)
        self.mover(t[0] if t else None, t[1] if t else None, eco); self.envejecer()
        self.cnt+=1
        if self.cnt >= 100: self.leche = min(10, self.leche+1); self.cnt=0

class Gallina(Animal):
    def __init__(self, x, y):
        super().__init__("Gallina", "herbivoro", x, y, os.path.join(os.path.dirname(__file__), '..', 'imagenes', 'gallina.png'), True)
        self.cnt_h = random.randint(80, 200)
    def actualizar(self, eco):
        t = None
        if self.vida < 90 and eco.plantas:
            obj = min(eco.plantas, key=lambda p: distancia(self, p))
            if distancia(self, obj) < 15: eco.plantas.remove(obj); self.vida = min(100, self.vida+5)
            else: t = (obj.x, obj.y)
        self.mover(t[0] if t else None, t[1] if t else None, eco); self.envejecer()
        self.cnt_h -= 1
        if self.cnt_h <= 0: eco.huevos.append(Huevo(self.x, self.y)); self.cnt_h = random.randint(120, 250)

class Zorro(Animal):
    def __init__(self, x, y):
        super().__init__("Zorro", "carnivoro", x, y, os.path.join(os.path.dirname(__file__), '..', 'imagenes', 'zorro.png'), True)
    def actualizar(self, eco):
        p = [a for a in eco.animales if isinstance(a, Gallina)]; t = None
        if self.vida < 90 and p:
            obj = min(p, key=lambda x: distancia(self, x))
            if distancia(self, obj) < 15: obj.vida=0; self.vida = min(100, self.vida+20)
            else: t = (obj.x, obj.y)
        self.mover(t[0] if t else None, t[1] if t else None, eco); self.envejecer()

class Pez(Animal):
    def __init__(self, x, y):
        super().__init__("Pez", "herbivoro", x, y, os.path.join(os.path.dirname(__file__), '..', 'imagenes', 'pez.png'), True)
        self.tamano = 30
    def mover(self, tx, ty, eco):
        r = eco.lago.rect_agua
        if tx is None:
            self.timer -= 1
            if self.timer <= 0:
                self.target_x, self.target_y = random.randint(r.x, r.right-30), random.randint(r.y, r.bottom-30)
                self.timer = random.randint(60, 180)
            tx, ty = self.target_x, self.target_y
        dx, dy = tx - self.x, ty - self.y
        if abs(dx) < 1 and abs(dy) < 1: return
        if dx < 0 and not self.mirando_izq: self.imagen = self.img_L; self.mirando_izq = True
        elif dx > 0 and self.mirando_izq: self.imagen = self.img_R; self.mirando_izq = False
        ndx, ndy = normalizar_vector(dx, dy)
        self.x = max(r.x, min(self.x + ndx * self.velocidad, r.right - 30))
        self.y = max(r.y, min(self.y + ndy * self.velocidad, r.bottom - 30))
        self.rect.topleft = (self.x, self.y)
    def actualizar(self, eco):
        t = None
        if self.vida < 90 and eco.algas:
            obj = min(eco.algas, key=lambda a: distancia(self, a))
            if distancia(self, obj) < 15: eco.algas.remove(obj); self.vida = min(100, self.vida+10)
            else: t = (obj.x, obj.y)
        self.mover(t[0] if t else None, t[1] if t else None, eco); self.envejecer()

class Caballo(Animal):
    def __init__(self, x, y):
        super().__init__("Caballo", "herbivoro", x, y, os.path.join(os.path.dirname(__file__), '..', 'imagenes', 'caballo.png'), True)
        self.reproduccion_contador = random.randint(300, 500)
    def actualizar(self, eco):
        t = None
        if self.vida < 90 and eco.plantas:
            obj = min(eco.plantas, key=lambda p: distancia(self, p))
            if distancia(self, obj) < 15: eco.plantas.remove(obj); self.vida = min(100, self.vida+15)
            else: t = (obj.x, obj.y)
        self.mover(t[0] if t else None, t[1] if t else None, eco); self.envejecer()
        self.reproduccion_contador -= 1
        if self.reproduccion_contador <= 0:
            if random.random() < 0.08:
                x, y = generar_spawn_seguro(eco.obtener_obstaculos(), 35)
                eco.agregar_animal(Caballo(x, y))
            self.reproduccion_contador = random.randint(300, 500)

class Oso(Animal):
    def __init__(self, x, y):
        super().__init__("Oso", "omnivoro", x, y, os.path.join(os.path.dirname(__file__), '..', 'imagenes', 'oso.png'), True)
    def actualizar(self, eco):
        p = [a for a in eco.animales if isinstance(a, Gallina)]; t = None
        if self.vida < 90:
            if p and random.random() < 0.5:
                obj = min(p, key=lambda x: distancia(self, x))
                if distancia(self, obj) < 18: obj.vida = 0; self.vida += 15
                else: t = (obj.x, obj.y)
            elif eco.plantas:
                obj = min(eco.plantas, key=lambda x: distancia(self, x))
                if distancia(self, obj) < 15: eco.plantas.remove(obj); self.vida += 10
                else: t = (obj.x, obj.y)
        self.mover(t[0] if t else None, t[1] if t else None, eco); self.envejecer()

class Cerdo(Animal):
    def __init__(self, x, y):
        super().__init__("Cerdo", "omnivoro", x, y, os.path.join(os.path.dirname(__file__), '..', 'imagenes', 'cerdo.png'), True)
    def actualizar(self, eco):
        t = None
        if self.vida < 90:
            if eco.huevos:
                obj = min(eco.huevos, key=lambda x: distancia(self, x))
                if distancia(self, obj) < 20: eco.huevos.remove(obj); self.vida += 15
                else: t = (obj.x, obj.y)
            elif eco.plantas:
                obj = min(eco.plantas, key=lambda x: distancia(self, x))
                if distancia(self, obj) < 15: eco.plantas.remove(obj); self.vida += 10
                else: t = (obj.x, obj.y)
        self.mover(t[0] if t else None, t[1] if t else None, eco); self.envejecer()

class Lobo(Animal):
    def __init__(self, x, y):
        super().__init__("Lobo", "carnivoro", x, y, os.path.join(os.path.dirname(__file__), '..', 'imagenes', 'lobo.png'), False)
        self.velocidad = 4
    def actualizar(self, eco):
        p = [a for a in eco.animales if a.tipo == "herbivoro" and not isinstance(a, Pez)]; t = None
        if self.vida < 90 and p:
            obj = min(p, key=lambda x: distancia(self, x))
            if distancia(self, obj) < 25: obj.vida = 0; self.vida += 30
            else: t = (obj.x, obj.y)
        self.mover(t[0] if t else None, t[1] if t else None, eco); self.envejecer()

class Rana(Animal):
    def __init__(self, x, y):
        super().__init__("Rana", "omnivoro", x, y, os.path.join(os.path.dirname(__file__), '..', 'imagenes', 'rana.png'), True)
    def actualizar(self, eco):
        self.timer -= 1
        if self.timer <= 0:
            if eco.lago.rect_agua.collidepoint(self.x, self.y):
                self.target_x, self.target_y = random.randint(0, ANCHO), random.randint(0, ALTO)
            else:
                r = eco.lago.rect_agua
                self.target_x, self.target_y = random.randint(r.x, r.right), random.randint(r.y, r.bottom)
            self.timer = random.randint(100, 200)
        self.mover(None, None, eco); self.envejecer()
