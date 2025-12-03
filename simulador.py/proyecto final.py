import pygame
import random
import math
import os
import json

# --- CONFIGURACION GENERAL ---
ANCHO, ALTO = 800, 600
FPS = 20
GROSOR_ORILLA = 20

COLOR_MENU = (100, 100, 100)
COLOR_BOTON = (0, 200, 0)
COLOR_BOTON_CARGAR = (200, 150, 0)
COLOR_TEXTO = (255, 255, 255)
COLOR_HUD = (0, 0, 0)
TAMANO_CORAZON = 10
USAR_IMAGEN_CORAZON = False
ARCHIVO_GUARDADO = "partida_guardada.json"

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()
IMAGES_DIR = os.path.join(BASE_DIR, "imagenes")

# ---LOGICA DEL JUEGO 

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

class Entidad:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def dibujar(self, surf):
        pass

class Planta(Entidad):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.tamano = 15; self.vida = 100
        self.imagen = cargar_imagen_segura(os.path.join(IMAGES_DIR, "planta.png"), tam=(15, 15), color=(0, 255, 0))
        self.rect = pygame.Rect(x, y, 15, 15)
    def crecer(self):
        self.vida -= 0.01
    def dibujar(self, surf):
        surf.blit(self.imagen, (self.x, self.y))

class Alga(Entidad):
    def __init__(self, x, y):
        super().__init__(x, y); self.tamano = 12
        self.imagen = cargar_imagen_segura(os.path.join(IMAGES_DIR, "alga.png"), tam=(12, 12), color=(0, 100, 0))
    def dibujar(self, surf):
        surf.blit(self.imagen, (self.x, self.y))

class Huevo(Entidad):
    def __init__(self, x, y):
        super().__init__(x, y); self.tamano = 15
        self.imagen = cargar_imagen_segura(os.path.join(IMAGES_DIR, "huevo.png"), tam=(15, 15))
        self.rect = self.imagen.get_rect(topleft=(x, y))
    def incubar(self, eco):
        pass 
    def dibujar(self, surf):
        surf.blit(self.imagen, (self.x, self.y))

class Animal(Entidad):
    def __init__(self, nombre, tipo, x, y, img_path, default_face_left=False):
        super().__init__(x, y)
        self.nombre = nombre
        self.tipo = tipo
        self.vida = 100
        self.tamano = 35
        self.velocidad = random.randint(1, 3)
        
        base = cargar_imagen_segura(img_path, tam=(35, 35))
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
            self.imagen = self.img_L
            self.mirando_izq = True
        elif dx > 0 and self.mirando_izq:
            self.imagen = self.img_R
            self.mirando_izq = False

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
        dibujar_corazones(surf, self.x, self.y, self.vida)
        txt = pygame.font.SysFont(None, 16).render(self.nombre, True, (0,0,0))
        surf.blit(txt, (self.x + 5, self.y + 35))

class Vaca(Animal):
    def __init__(self, x, y):
        super().__init__("Vaca", "herbivoro", x, y, os.path.join(IMAGES_DIR, "vaca.png"), True)
        self.leche = 0; self.cnt = 0
    def actualizar(self, eco):
        t = None
        if self.vida < 90 and eco.plantas:
            obj = min(eco.plantas, key=lambda p: distancia(self, p))
            if distancia(self, obj) < 15: eco.plantas.remove(obj); self.vida = min(100, self.vida+15)
            else: t = (obj.x, obj.y)
        self.mover(t[0] if t else None, t[1] if t else None, eco); self.envejecer()
        self.cnt+=1; 
        if self.cnt >= 100: self.leche = min(10, self.leche+1); self.cnt=0

class Gallina(Animal):
    def __init__(self, x, y):
        super().__init__("Gallina", "herbivoro", x, y, os.path.join(IMAGES_DIR, "gallina.png"), True)
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
        super().__init__("Zorro", "carnivoro", x, y, os.path.join(IMAGES_DIR, "zorro.png"), True)
    def actualizar(self, eco):
        p = [a for a in eco.animales if isinstance(a, Gallina)]; t = None
        if self.vida < 90 and p:
            obj = min(p, key=lambda x: distancia(self, x))
            if distancia(self, obj) < 15: obj.vida=0; self.vida = min(100, self.vida+20)
            else: t = (obj.x, obj.y)
        self.mover(t[0] if t else None, t[1] if t else None, eco); self.envejecer()

class Pez(Animal):
    def __init__(self, x, y):
        super().__init__("Pez", "herbivoro", x, y, os.path.join(IMAGES_DIR, "pez.png"), True)
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
        super().__init__("Caballo", "herbivoro", x, y, os.path.join(IMAGES_DIR, "caballo.png"), True)
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
        super().__init__("Oso", "omnivoro", x, y, os.path.join(IMAGES_DIR, "oso.png"), True)
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
        super().__init__("Cerdo", "omnivoro", x, y, os.path.join(IMAGES_DIR, "cerdo.png"), True)
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
        super().__init__("Lobo", "carnivoro", x, y, os.path.join(IMAGES_DIR, "lobo.png"), False)
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
        super().__init__("Rana", "omnivoro", x, y, os.path.join(IMAGES_DIR, "rana.png"), True)
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

class Arbol(Entidad):
    def __init__(self, x, y):
        super().__init__(x, y); self.tamano = 40
        self.imagen = cargar_imagen_segura(os.path.join(IMAGES_DIR, "arbol.png"), tam=(40, 40))
        self.rect = self.imagen.get_rect(topleft=(x, y))
    def dibujar(self, surf): surf.blit(self.imagen, (self.x, self.y))

class Casa(Entidad):
    def __init__(self, x, y):
        super().__init__(x, y); self.tamano = 100
        self.imagen = cargar_imagen_segura(os.path.join(IMAGES_DIR, "casa.png"), tam=(100, 100))
        self.rect = self.imagen.get_rect(topleft=(x, y))
    def dibujar(self, surf): surf.blit(self.imagen, (self.x, self.y))

class Lago:
    def __init__(self, x, y, w, h):
        self.rect_orilla = pygame.Rect(x, y, w, h)
        self.rect_agua = pygame.Rect(x + GROSOR_ORILLA, y + GROSOR_ORILLA, w - 2*GROSOR_ORILLA, h - 2*GROSOR_ORILLA)
        self.img_orilla = cargar_imagen_segura(os.path.join(IMAGES_DIR, "orilla.png"), tam=(w, h), color=(210, 180, 140))
        self.img_agua = cargar_imagen_segura(os.path.join(IMAGES_DIR, "lago.png"), tam=(self.rect_agua.width, self.rect_agua.height), color=(0, 0, 139))
    def dibujar(self, surf):
        surf.blit(self.img_orilla, self.rect_orilla)
        surf.blit(self.img_agua, self.rect_agua)

class Persona(Animal):
    def __init__(self, x, y):
        super().__init__("Jugador", "humano", x, y, os.path.join(IMAGES_DIR, "persona.png"))
        self.inventario = {"huevos": 0, "leche": 0}
        self.tamano = 40
        self.obj_drag = None
        self.velocidad = 10
    def mover(self, keys, eco):
        mx, my = 0, 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: mx = -self.velocidad
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: mx = self.velocidad
        if keys[pygame.K_w] or keys[pygame.K_UP]: my = -self.velocidad
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: my = self.velocidad
        
        if mx < 0 and not self.mirando_izq: self.imagen = self.img_L; self.mirando_izq = True
        elif mx > 0 and self.mirando_izq: self.imagen = self.img_R; self.mirando_izq = False
        
        obs = eco.obtener_obstaculos()
        if not any(pygame.Rect(self.x+mx, self.y, self.tamano, self.tamano).colliderect(o) for o in obs): self.x += mx
        if not any(pygame.Rect(self.x, self.y+my, self.tamano, self.tamano).colliderect(o) for o in obs): self.y += my
        
        self.x = max(0, min(ANCHO-self.tamano, self.x))
        self.y = max(0, min(ALTO-self.tamano, self.y))
        self.rect.topleft = (self.x, self.y)

    def recoger(self, eco):
        for h in eco.huevos[:]:
            if self.rect.colliderect(h.rect): eco.huevos.remove(h); self.inventario["huevos"] += 1
        for a in eco.animales:
            if isinstance(a, Vaca) and distancia(self, a) < 50 and a.leche > 0:
                self.inventario["leche"] += 1; a.leche = 0
    
    def intentar_arrastrar(self, pos, eco):
        for a in eco.animales:
            if a.rect.collidepoint(pos) and distancia(self, a) < 100:
                self.obj_drag = a; break
    def soltar(self): self.obj_drag = None

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
        for a in self.animales: a.actualizar(self)
        for p in self.plantas: p.crecer()
        for h in self.huevos[:]: h.incubar(self)
            
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
    eco.casa = Casa(ANCHO - 120, 20)
    eco.lago = Lago(ANCHO//2 - 150, ALTO - 200, 300, 150)
    
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
            if cls == Rana: x, y = random.randint(0, ANCHO), random.randint(0, ALTO)
            else: x, y = generar_spawn_seguro(obs, 35)
            if x != 0 or y != 0:
                eco.agregar_animal(cls(x, y))
            
    for _ in range(4):
        r = eco.lago.rect_agua
        x, y = random.randint(r.x, r.right-30), random.randint(r.y, r.bottom-30)
        eco.agregar_animal(Pez(x, y))
    return eco

# --- CAPA DE PERSISTENCIA 

def guardar_partida(ecosistema, persona):
    datos = {
        "persona": {
            "x": persona.x,
            "y": persona.y,
            "inventario": persona.inventario,
            "mirando_izq": persona.mirando_izq
        },
        "animales": [],
        "plantas": [],
        "arboles": []
    }

    for a in ecosistema.animales:
        info_animal = {
            "clase": type(a).__name__,
            "x": a.x, "y": a.y,
            "vida": a.vida,
            "leche": getattr(a, 'leche', 0),
            "reproduccion_contador": getattr(a, 'reproduccion_contador', 0)
        }
        datos["animales"].append(info_animal)

    for p in ecosistema.plantas:
        datos["plantas"].append({"x": p.x, "y": p.y, "vida": p.vida})

    for ar in ecosistema.arboles:
        datos["arboles"].append({"x": ar.x, "y": ar.y})
    
    with open(ARCHIVO_GUARDADO, "w") as f:
        json.dump(datos, f)

def cargar_partida():
    if not os.path.exists(ARCHIVO_GUARDADO):
        return None, None
    
    with open(ARCHIVO_GUARDADO, "r") as f:
        datos = json.load(f)

    nuevo_eco = Ecosistema()
    nuevo_eco.casa = Casa(ANCHO - 120, 20)
    nuevo_eco.lago = Lago(ANCHO//2 - 150, ALTO - 200, 300, 150)

    for p_dat in datos["plantas"]:
        planta = Planta(p_dat["x"], p_dat["y"])
        planta.vida = p_dat["vida"]
        nuevo_eco.plantas.append(planta)

    for ar_dat in datos["arboles"]:
        nuevo_eco.arboles.append(Arbol(ar_dat["x"], ar_dat["y"]))

    clase_map = {
        "Vaca": Vaca, "Gallina": Gallina, "Zorro": Zorro,
        "Caballo": Caballo, "Oso": Oso, "Cerdo": Cerdo,
        "Lobo": Lobo, "Rana": Rana, "Pez": Pez
    }

    for a_dat in datos["animales"]:
        Clase = clase_map.get(a_dat["clase"])
        if Clase:
            nuevo_animal = Clase(a_dat["x"], a_dat["y"])
            nuevo_animal.vida = a_dat["vida"]
            if "leche" in a_dat: nuevo_animal.leche = a_dat["leche"]
            if "reproduccion_contador" in a_dat: nuevo_animal.reproduccion_contador = a_dat["reproduccion_contador"]
            nuevo_eco.agregar_animal(nuevo_animal)

    nueva_persona = Persona(datos["persona"]["x"], datos["persona"]["y"])
    nueva_persona.inventario = datos["persona"]["inventario"]
    nueva_persona.mirando_izq = datos["persona"]["mirando_izq"]
    
    return nuevo_eco, nueva_persona



# --- VISTA 


pygame.init()
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Simulador de Ecosistema")
reloj = pygame.time.Clock()

FUENTE_GRANDE = pygame.font.SysFont(None, 48)
FUENTE_MEDIANA = pygame.font.SysFont(None, 32)
fuente_nombre = pygame.font.SysFont(None, 16)
FUENTE_INSTRUCCIONES = pygame.font.SysFont(None, 24)

try:
    img_lleno = cargar_imagen_segura(os.path.join(IMAGES_DIR, "corazon_lleno.png"), tam=(10, 10), color=(255, 0, 0))
    img_vacio = cargar_imagen_segura(os.path.join(IMAGES_DIR, "corazon_vacio.png"), tam=(10, 10), color=(50, 0, 0))
    if img_lleno.get_width() == 10:
        USAR_IMAGEN_CORAZON = True
    
    FONDO_JUEGO = cargar_imagen_segura(os.path.join(IMAGES_DIR, "fondo.png"), tam=(ANCHO, ALTO))
    FONDO_MENU = cargar_imagen_segura(os.path.join(IMAGES_DIR, "menu_fondo.png"), tam=(ANCHO, ALTO))
except:
    USAR_IMAGEN_CORAZON = False
    FONDO_JUEGO = pygame.Surface((ANCHO, ALTO)); FONDO_JUEGO.fill((135, 206, 235))
    FONDO_MENU = pygame.Surface((ANCHO, ALTO)); FONDO_MENU.fill(COLOR_MENU)

def dibujar_corazones(superficie, x, y, vida, max_corazones=3):
    llenos = int((vida / 100) * max_corazones)
    start_x = x + 35 // 2 - (max_corazones * 12) // 2
    for i in range(max_corazones):
        cx, cy = start_x + i * 12, y - 18
        if i < llenos:
            if USAR_IMAGEN_CORAZON: superficie.blit(img_lleno, (cx, cy))
            else: pygame.draw.circle(superficie, (255, 0, 0), (cx+5, cy+5), 5)
        else:
            if USAR_IMAGEN_CORAZON: superficie.blit(img_vacio, (cx, cy))
            else: pygame.draw.circle(superficie, (50, 0, 0), (cx+5, cy+5), 5)

class MenuPrincipal:
    def __init__(self):
        self.btn_jugar = pygame.Rect(ANCHO//2 - 100, ALTO//2 - 40, 200, 50)
        self.btn_cargar = pygame.Rect(ANCHO//2 - 100, ALTO//2 + 30, 200, 50)

    def dibujar(self, surf):
        surf.blit(FONDO_MENU, (0, 0))
        t = FUENTE_GRANDE.render("Simulador de Ecosistema", True, COLOR_TEXTO)
        surf.blit(t, t.get_rect(center=(ANCHO//2, ALTO//3 - 30)))
        
        pygame.draw.rect(surf, COLOR_BOTON, self.btn_jugar, border_radius=10)
        t1 = FUENTE_MEDIANA.render("NUEVA PARTIDA", True, COLOR_TEXTO)
        surf.blit(t1, t1.get_rect(center=self.btn_jugar.center))
        
        if os.path.exists(ARCHIVO_GUARDADO):
            pygame.draw.rect(surf, COLOR_BOTON_CARGAR, self.btn_cargar, border_radius=10)
            t2 = FUENTE_MEDIANA.render("CARGAR PARTIDA", True, COLOR_TEXTO)
            surf.blit(t2, t2.get_rect(center=self.btn_cargar.center))
        
        instrucciones = [
            "CONTROLES:",
            "- WASD: Moverse | E: Recoger",
            "- ESPACIO: Modo Spawn | G: Guardar",
            "- Arrastrar Animales: Clic + Mover"
        ]
        y_pos = ALTO - 130
        for linea in instrucciones:
            txt = FUENTE_INSTRUCCIONES.render(linea, True, COLOR_TEXTO)
            surf.blit(txt, (ANCHO//2 - txt.get_width()//2, y_pos))
            y_pos += 25

    def click(self, pos):
        if self.btn_jugar.collidepoint(pos):
            return "NUEVA"
        if os.path.exists(ARCHIVO_GUARDADO) and self.btn_cargar.collidepoint(pos):
            return "CARGAR"
        return "MENU"

def manejar_clic_animal(pos, eco):
    x, y = pos[0]-17, pos[1]-17
    rect = pygame.Rect(x, y, 35, 35)
    
    obs = eco.obtener_obstaculos()
    if any(rect.colliderect(o) for o in obs): return 
    
    en_agua = eco.lago.rect_agua.colliderect(rect)
    cls = random.choice([Vaca, Gallina, Zorro, Caballo, Oso, Cerdo, Lobo, Rana])
    
    if en_agua: eco.agregar_animal(Pez(x, y))
    else: eco.agregar_animal(cls(x, y))

# --- BUCLE PRINCIPAL ---
ecosistema = None
persona = None
menu = MenuPrincipal()
estado = "MENU"
modo_spawn = False
corriendo = True
mensaje_guardado = 0

while corriendo:
    for e in pygame.event.get():
        if e.type == pygame.QUIT: corriendo = False
        
        if estado == "MENU":
            if e.type == pygame.MOUSEBUTTONDOWN:
                accion = menu.click(e.pos)
                if accion == "NUEVA":
                    ecosistema = inicializar()
                    persona = Persona(ANCHO//2, ALTO//2)
                    estado = "JUGANDO"
                elif accion == "CARGAR":
                    eco_cargado, per_cargado = cargar_partida()
                    if eco_cargado:
                        ecosistema = eco_cargado
                        persona = per_cargado
                        estado = "JUGANDO"
            
        elif estado == "JUGANDO":
            if e.type == pygame.MOUSEBUTTONDOWN:
                if persona.rect.collidepoint(e.pos): persona.intentar_arrastrar(e.pos, ecosistema)
                elif modo_spawn and e.button == 1: manejar_clic_animal(e.pos, ecosistema)
            
            if e.type == pygame.MOUSEBUTTONUP: persona.soltar()
            if e.type == pygame.MOUSEMOTION and persona.obj_drag:
                persona.obj_drag.x, persona.obj_drag.y = e.pos[0]-20, e.pos[1]-20
                persona.obj_drag.rect.topleft = (persona.obj_drag.x, persona.obj_drag.y)
            
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE: modo_spawn = not modo_spawn
                if e.key == pygame.K_e: persona.recoger(ecosistema)
                if e.key == pygame.K_g: 
                    guardar_partida(ecosistema, persona)
                    mensaje_guardado = 60 

    if estado == "JUGANDO":
        persona.mover(pygame.key.get_pressed(), ecosistema)
        ecosistema.actualizar()
        ventana.blit(FONDO_JUEGO, (0, 0))
        ecosistema.dibujar(ventana)
        persona.dibujar(ventana)
        
        info = fuente_nombre.render(f"Huevos: {persona.inventario['huevos']} | Leche: {persona.inventario['leche']}", True, COLOR_HUD)
        ventana.blit(info, (10, 10))
        
        txt_animales = fuente_nombre.render(f"Animales: {len(ecosistema.animales)}", True, COLOR_HUD)
        ventana.blit(txt_animales, (10, 30))
        
        modo = fuente_nombre.render(f"SPAWN: {'ON' if modo_spawn else 'OFF'} | G: Guardar", True, (0,150,0) if modo_spawn else (50,50,50))
        ventana.blit(modo, (ANCHO - 200, 10))

        if mensaje_guardado > 0:
            msg = FUENTE_MEDIANA.render("PARTIDA GUARDADA", True, (255, 255, 0))
            ventana.blit(msg, (ANCHO//2 - msg.get_width()//2, ALTO - 50))
            mensaje_guardado -= 1
        
    elif estado == "MENU":
        menu.dibujar(ventana)

    pygame.display.flip()
    reloj.tick(FPS)

pygame.quit()