import pygame
import random
import math
import os
import json

# capa logica
ANCHO, ALTO = 800, 600
FPS = 20
GROSOR_ORILLA = 20

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()

IMAGES_DIR = os.path.join(BASE_DIR, "imagenes")
SAVES_DIR = os.path.join(BASE_DIR, "saves")

if not os.path.exists(SAVES_DIR):
    os.makedirs(SAVES_DIR)

RUTAS = {
    "slot_1": os.path.join(SAVES_DIR, "slot_1.json"),
    "slot_2": os.path.join(SAVES_DIR, "slot_2.json"),
    "auto":    os.path.join(SAVES_DIR, "autosave.json")
}


def distancia(a, b):
    try:
        x1, y1 = (a.x, a.y) if hasattr(a, 'x') else (a['x'], a['y'])
        x2, y2 = (b.x, b.y) if hasattr(b, 'x') else (b['x'], b['y'])
        return math.sqrt((x1-x2)**2 + (y1-y2)**2)
    except: return float('inf')

def normalizar_vector(dx, dy):
    m = math.sqrt(dx**2 + dy**2)
    return (0, 0) if m == 0 else (dx/m, dy/m)

def generar_spawn_seguro(obs, tam):
    for _ in range(100):
        x, y = random.randint(0, ANCHO-tam), random.randint(0, ALTO-tam)
        if not any(pygame.Rect(x,y,tam,tam).colliderect(o) for o in obs): return x,y
    return 0,0

def generar_spawn_cerca(px, py, obs, tam, r=100):
    for _ in range(50):
        a, d = random.uniform(0, 6.28), random.uniform(tam, r)
        x, y = int(px+math.cos(a)*d), int(py+math.sin(a)*d)
        x, y = max(0, min(ANCHO-tam, x)), max(0, min(ALTO-tam, y))
        if not any(pygame.Rect(x,y,tam,tam).colliderect(o) for o in obs): return x,y
    return generar_spawn_seguro(obs, tam)


class Entidad:
    def __init__(self, x, y): self.x, self.y = x, y
    def dibujar(self, surf): pass
    def to_dict(self): return {"x": self.x, "y": self.y}

    @classmethod
    def from_dict(cls, data):
        return cls(data["x"], data["y"])

class Planta(Entidad):
    def __init__(self, x, y):
        super().__init__(x, y); self.tamano=15; self.vida=100
        self.img = cargar_imagen_segura(os.path.join(IMAGES_DIR, "planta.png"), tam=(15,15), color=(0,255,0))
        self.rect = pygame.Rect(x, y, 15, 15)
    def crecer(self): self.vida -= 0.01
    def dibujar(self, surf): surf.blit(self.img, (self.x, self.y))
    
    def to_dict(self):
        data = super().to_dict()
        data["vida"] = self.vida
        data["__class__"] = "Planta"
        return data

    @classmethod
    def from_dict(cls, data):
        p = cls(data["x"], data["y"])
        p.vida = data["vida"]
        return p

class Alga(Entidad):
    def __init__(self, x, y):
        super().__init__(x, y); self.tamano=12
        self.img = cargar_imagen_segura(os.path.join(IMAGES_DIR, "alga.png"), tam=(12,12), color=(0,100,0))
    def dibujar(self, surf): surf.blit(self.img, (self.x, self.y))
    
    def to_dict(self):
        data = super().to_dict()
        data["__class__"] = "Alga"
        return data

class Huevo(Entidad):
    def __init__(self, x, y):
        super().__init__(x, y); self.tamano=15
        self.img = cargar_imagen_segura(os.path.join(IMAGES_DIR, "huevo.png"), tam=(15,15))
        self.rect = self.img.get_rect(topleft=(x,y))
    def incubar(self, eco): pass
    def dibujar(self, surf): surf.blit(self.img, (self.x, self.y))
    
    def to_dict(self):
        data = super().to_dict()
        data["__class__"] = "Huevo"
        return data

class Animal(Entidad):
    def __init__(self, nom, tipo, x, y, img, flip=False):
        super().__init__(x, y)
        self.nombre, self.tipo, self.vida = nom, tipo, 100
        self.tamano, self.velocidad = 35, random.randint(1, 3)
        base = cargar_imagen_segura(img, tam=(35,35))
        self.img_r = pygame.transform.flip(base, True, False) if flip else base
        self.img_l = base if flip else pygame.transform.flip(base, True, False)
        self.imagen, self.mirando_izq = (self.img_l, True) if flip else (self.img_r, False)
        self.tx, self.ty, self.timer = random.randint(0,ANCHO), random.randint(0,ALTO), 0
        self.rect = self.imagen.get_rect(topleft=(x,y))

    def mover(self, tx, ty, eco):
        if tx is None:
            self.timer -= 1
            if self.timer <= 0: self.tx, self.ty, self.timer = random.randint(0,ANCHO), random.randint(0,ALTO), random.randint(60,180)
            tx, ty = self.tx, self.ty
        dx, dy = tx - self.x, ty - self.y
        if abs(dx)<2 and abs(dy)<2: return
        if dx < 0: self.imagen, self.mirando_izq = self.img_l, True
        elif dx > 0: self.imagen, self.mirando_izq = self.img_r, False
        m = math.sqrt(dx**2 + dy**2); ndx, ndy = (0,0) if m==0 else (dx/m, dy/m)
        mx, my = ndx*self.velocidad, ndy*self.velocidad
        obs = eco.obtener_obstaculos(); es_acua = self.tipo in ["Pez","Rana"]
        if not any(pygame.Rect(self.x+mx, self.y, 35,35).colliderect(o) for o in obs) or es_acua: self.x += mx
        if not any(pygame.Rect(self.x, self.y+my, 35,35).colliderect(o) for o in obs) or es_acua: self.y += my
        if self.tipo != "Pez": self.x = max(0, min(ANCHO-35, self.x)); self.y = max(0, min(ALTO-35, self.y))
        self.rect.topleft = (self.x, self.y)

    def envejecer(self): self.vida -= random.uniform(0.01, 0.04)
    def esta_vivo(self): return self.vida > 0
    def dibujar(self, surf):
        surf.blit(self.imagen, (self.x, self.y))
        dibujar_corazones(surf, self.x, self.y, self.vida)
    def actualizar(self, eco): pass 

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "nombre": self.nombre,
            "tipo": self.tipo,
            "vida": self.vida,
            "velocidad": self.velocidad,
            "mirando_izq": self.mirando_izq,
            "tx": self.tx,
            "ty": self.ty,
            "timer": self.timer
        })
        return data

    @classmethod
    def from_dict(cls, data):
        raise NotImplementedError("from_dict debe ser implementado en subclases de Animal")


class Vaca(Animal):
    def __init__(self, x, y): super().__init__("Vaca", "herb", x, y, os.path.join(IMAGES_DIR, "vaca.png"), True); self.leche=0; self.c=0
    def actualizar(self, eco):
        t=None
        if self.vida<90 and eco.plantas:
            o=min(eco.plantas, key=lambda p:distancia(self,p))
            if distancia(self,o)<15: eco.plantas.remove(o); self.vida+=15
            else: t=(o.x,o.y)
        self.mover(t[0] if t else None, t[1] if t else None, eco); self.envejecer(); self.c+=1
        if self.c>=100: self.leche=min(10, self.leche+1); self.c=0
    
    def to_dict(self):
        data = super().to_dict()
        data.update({"leche": self.leche, "c": self.c, "__class__": "Vaca"})
        return data
    @classmethod
    def from_dict(cls, data):
        a = cls(data["x"], data["y"])
        a.__dict__.update(data)
        return a

class Gallina(Animal):
    def __init__(self, x, y): super().__init__("Gallina", "herb", x, y, os.path.join(IMAGES_DIR, "gallina.png"), True); self.ch=200
    def actualizar(self, eco):
        t=None
        if self.vida<90 and eco.plantas:
            o=min(eco.plantas, key=lambda p:distancia(self,p))
            if distancia(self,o)<15: eco.plantas.remove(o); self.vida+=5
            else: t=(o.x,o.y)
        self.mover(t[0] if t else None, t[1] if t else None, eco); self.envejecer(); self.ch-=1
        if self.ch<=0: eco.huevos.append(Huevo(self.x, self.y)); self.ch=250
    
    def to_dict(self):
        data = super().to_dict()
        data.update({"ch": self.ch, "__class__": "Gallina"})
        return data
    @classmethod
    def from_dict(cls, data):
        a = cls(data["x"], data["y"])
        a.__dict__.update(data)
        return a

class Zorro(Animal):
    def __init__(self, x, y): super().__init__("Zorro", "carn", x, y, os.path.join(IMAGES_DIR, "zorro.png"), True)
    def actualizar(self, eco):
        p=[a for a in eco.animales if isinstance(a, Gallina)]; t=None
        if self.vida<90 and p:
            o=min(p, key=lambda x:distancia(self,x))
            if distancia(self,o)<15: o.vida=0; self.vida+=20
            else: t=(o.x,o.y)
        self.mover(t[0] if t else None, t[1] if t else None, eco); self.envejecer()

    def to_dict(self):
        data = super().to_dict()
        data["__class__"] = "Zorro"
        return data
    @classmethod
    def from_dict(cls, data):
        a = cls(data["x"], data["y"])
        a.__dict__.update(data)
        return a

class Pez(Animal):
    def __init__(self, x, y): super().__init__("Pez", "herb", x, y, os.path.join(IMAGES_DIR, "pez.png"), True); self.tamano=30
    def mover(self, tx, ty, eco):
        r=eco.lago.rect_agua
        if tx is None:
            self.timer-=1
            if self.timer<=0: self.tx, self.ty, self.timer = random.randint(r.x, r.right-30), random.randint(r.y, r.bottom-30), 100
            tx,ty = self.tx, self.ty
        super().mover(tx, ty, eco)
    def actualizar(self, eco):
        t=None
        if self.vida<90 and eco.algas:
            o=min(eco.algas, key=lambda a:distancia(self,a))
            if distancia(self,o)<15: eco.algas.remove(o); self.vida+=10
            else: t=(o.x,o.y)
        self.mover(t[0] if t else None, t[1] if t else None, eco); self.envejecer()
    
    def to_dict(self):
        data = super().to_dict()
        data["__class__"] = "Pez"
        return data
    @classmethod
    def from_dict(cls, data):
        a = cls(data["x"], data["y"])
        a.__dict__.update(data)
        return a

class Caballo(Animal):
    def __init__(self, x, y): super().__init__("Caballo", "herb", x, y, os.path.join(IMAGES_DIR, "caballo.png"), True); self.rep=400
    def actualizar(self, eco):
        t=None
        if self.vida<90 and eco.plantas:
            o=min(eco.plantas, key=lambda p:distancia(self,p))
            if distancia(self,o)<15: eco.plantas.remove(o); self.vida+=15
            else: t=(o.x,o.y)
        self.mover(t[0] if t else None, t[1] if t else None, eco); self.envejecer(); self.rep-=1
        if self.rep<=0:
            if random.random()<0.08: x,y=generar_spawn_seguro(eco.obtener_obstaculos(),35); eco.agregar_animal(Caballo(x,y))
            self.rep=400
    
    def to_dict(self):
        data = super().to_dict()
        data.update({"rep": self.rep, "__class__": "Caballo"})
        return data
    @classmethod
    def from_dict(cls, data):
        a = cls(data["x"], data["y"])
        a.__dict__.update(data)
        return a

class Oso(Animal):
    def __init__(self, x, y): super().__init__("Oso", "omni", x, y, os.path.join(IMAGES_DIR, "oso.png"), True)
    def actualizar(self, eco):
        p=[a for a in eco.animales if isinstance(a, Gallina)]; t=None
        if self.vida<90:
            if p and random.random()<0.5:
                o=min(p, key=lambda x:distancia(self,x))
                if distancia(self,o)<18: o.vida=0; self.vida+=15
                else: t=(o.x,o.y)
            elif eco.plantas:
                o=min(eco.plantas, key=lambda x:distancia(self,x))
                if distancia(self,o)<15: eco.plantas.remove(o); self.vida+=10
                else: t=(o.x,o.y)
        self.mover(t[0] if t else None, t[1] if t else None, eco); self.envejecer()
    
    def to_dict(self):
        data = super().to_dict()
        data["__class__"] = "Oso"
        return data
    @classmethod
    def from_dict(cls, data):
        a = cls(data["x"], data["y"])
        a.__dict__.update(data)
        return a

class Cerdo(Animal):
    def __init__(self, x, y): super().__init__("Cerdo", "omni", x, y, os.path.join(IMAGES_DIR, "cerdo.png"), True)
    def actualizar(self, eco):
        t=None
        if self.vida<90:
            if eco.huevos:
                o=min(eco.huevos, key=lambda x:distancia(self,x))
                if distancia(self,o)<20: eco.huevos.remove(o); self.vida+=15
                else: t=(o.x,o.y)
            elif eco.plantas:
                o=min(eco.plantas, key=lambda x:distancia(self,x))
                if distancia(self,o)<15: eco.plantas.remove(o); self.vida+=10
                else: t=(o.x,o.y)
        self.mover(t[0] if t else None, t[1] if t else None, eco); self.envejecer()
    
    def to_dict(self):
        data = super().to_dict()
        data["__class__"] = "Cerdo"
        return data
    @classmethod
    def from_dict(cls, data):
        a = cls(data["x"], data["y"])
        a.__dict__.update(data)
        return a

class Lobo(Animal):
    def __init__(self, x, y): super().__init__("Lobo", "carn", x, y, os.path.join(IMAGES_DIR, "lobo.png"), False); self.velocidad=4
    def actualizar(self, eco):
        p=[a for a in eco.animales if a.tipo=="herb" and not isinstance(a, Pez)]; t=None
        if self.vida<90 and p:
            o=min(p, key=lambda x:distancia(self,x))
            if distancia(self,o)<25: o.vida=0; self.vida+=30
            else: t=(o.x,o.y)
        self.mover(t[0] if t else None, t[1] if t else None, eco); self.envejecer()

    def to_dict(self):
        data = super().to_dict()
        data["__class__"] = "Lobo"
        return data
    @classmethod
    def from_dict(cls, data):
        a = cls(data["x"], data["y"])
        a.__dict__.update(data)
        return a

class Rana(Animal):
    def __init__(self, x, y): super().__init__("Rana", "omni", x, y, os.path.join(IMAGES_DIR, "rana.png"), True)
    def actualizar(self, eco):
        self.timer-=1
        if self.timer<=0:
            if eco.lago.rect_agua.collidepoint(self.x, self.y): self.tx,self.ty=random.randint(0,ANCHO),random.randint(0,ALTO)
            else: r=eco.lago.rect_agua; self.tx,self.ty=random.randint(r.x,r.right),random.randint(r.y,r.bottom)
            self.timer=150
        self.mover(None, None, eco); self.envejecer()
    
    def to_dict(self):
        data = super().to_dict()
        data["__class__"] = "Rana"
        return data
    @classmethod
    def from_dict(cls, data):
        a = cls(data["x"], data["y"])
        a.__dict__.update(data)
        return a

CLASE_MAP = {
    "Vaca": Vaca, "Gallina": Gallina, "Zorro": Zorro, "Pez": Pez, "Caballo": Caballo,
    "Oso": Oso, "Cerdo": Cerdo, "Lobo": Lobo, "Rana": Rana, "Persona": 'Persona' 
}

class Arbol(Entidad):
    def __init__(self, x, y):
        super().__init__(x, y); self.tamano=40
        self.img = cargar_imagen_segura(os.path.join(IMAGES_DIR, "arbol.png"), tam=(40,40))
        self.rect = self.img.get_rect(topleft=(x,y))
    def dibujar(self, surf): surf.blit(self.img, (self.x, self.y))
    
    def to_dict(self):
        data = super().to_dict()
        data["__class__"] = "Arbol"
        return data

class Casa(Entidad):
    def __init__(self, x, y):
        super().__init__(x, y); self.tamano=100
        self.img = cargar_imagen_segura(os.path.join(IMAGES_DIR, "casa.png"), tam=(100,100))
        self.rect = self.img.get_rect(topleft=(x,y))
    def dibujar(self, surf): surf.blit(self.img, (self.x, self.y))

    def to_dict(self):
        data = super().to_dict()
        data["__class__"] = "Casa"
        return data

class Lago:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.rect_orilla = pygame.Rect(x,y,w,h); self.rect_agua = pygame.Rect(x+20,y+20,w-40,h-40)
        self.img_o = cargar_imagen_segura(os.path.join(IMAGES_DIR, "orilla.png"), tam=(w,h), color=(210,180,140))
        self.img_a = cargar_imagen_segura(os.path.join(IMAGES_DIR, "lago.png"), tam=(w-40,h-40), color=(0,0,139))
    def dibujar(self, surf): surf.blit(self.img_o, self.rect_orilla); surf.blit(self.img_a, self.rect_agua)

    def to_dict(self):
        return {"x": self.x, "y": self.y, "w": self.w, "h": self.h}

    @classmethod
    def from_dict(cls, data):
        return cls(data["x"], data["y"], data["w"], data["h"])


class Persona(Animal):
    def __init__(self, x, y):
        super().__init__("Yo", "humano", x, y, os.path.join(IMAGES_DIR, "persona.png"))
        self.inventario = {"huevos":0, "leche":0}; self.tamano=40; self.obj_drag=None; self.velocidad=8
    def mover(self, k, eco):
        mx, my = 0, 0
        if k[pygame.K_a] or k[pygame.K_LEFT]: mx = -self.velocidad
        if k[pygame.K_d] or k[pygame.K_RIGHT]: mx = self.velocidad
        if k[pygame.K_w] or k[pygame.K_UP]: my = -self.velocidad
        if k[pygame.K_s] or k[pygame.K_DOWN]: my = self.velocidad
        if mx<0: self.imagen, self.mirando_izq = self.img_l, True
        elif mx>0: self.imagen, self.mirando_izq = self.img_r, False
        obs = eco.obtener_obstaculos()
        if not any(pygame.Rect(self.x+mx, self.y, 40,40).colliderect(o) for o in obs): self.x+=mx
        if not any(pygame.Rect(self.x, self.y+my, 40,40).colliderect(o) for o in obs): self.y+=my
        self.x=max(0,min(ANCHO-40,self.x)); self.y=max(0,min(ALTO-40,self.y)); self.rect.topleft=(self.x,self.y)
    def recoger(self, eco):
        for h in eco.huevos[:]:
            if self.rect.colliderect(h.rect): eco.huevos.remove(h); self.inventario["huevos"]+=1
        for a in eco.animales:
            if isinstance(a, Vaca) and distancia(self,a)<50 and a.leche>0: self.inventario["leche"]+=1; a.leche=0
    def intentar_arrastrar(self, pos, eco):
        for a in eco.animales:
            if a.rect.collidepoint(pos) and distancia(self, a)<100: self.obj_drag=a; break
    def soltar(self): self.obj_drag = None
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "inventario": self.inventario.copy(),
            "__class__": "Persona"
        })
        return data

    @classmethod
    def from_dict(cls, data):
        p = cls(data["x"], data["y"])
        for key in ["vida", "velocidad", "mirando_izq", "tx", "ty", "timer"]:
            setattr(p, key, data.get(key, getattr(p, key)))
        p.inventario = data.get("inventario", {"huevos": 0, "leche": 0})
        p.rect.topleft = (p.x, p.y)
        return p


class Ecosistema:
    def __init__(self):
        self.animales, self.plantas, self.algas, self.arboles, self.huevos = [], [], [], [], []
        self.casa, self.lago = None, None
    def agregar_animal(self, a): self.animales.append(a)
    def obtener_obstaculos(self):
        return [a.rect for a in self.arboles] + ([self.casa.rect] if self.casa else []) + ([self.lago.rect_orilla] if self.lago else [])
    
    def actualizar(self):
        self.animales = [a for a in self.animales if a.esta_vivo()]
        for a in self.animales: a.actualizar(self)
        for p in self.plantas: p.crecer()
        for h in self.huevos[:]: h.incubar(self)
        if len(self.plantas)<50: x,y=generar_spawn_seguro(self.obtener_obstaculos(),10); self.plantas.append(Planta(x,y))
        if len(self.huevos)>=5:
            for _ in range(5): self.huevos.pop(0)
            x,y=generar_spawn_seguro(self.obtener_obstaculos(),35); self.agregar_animal(Gallina(x,y))
            
    def dibujar(self, surf):
        if self.lago: self.lago.dibujar(surf)
        for x in self.algas + self.plantas + self.huevos + self.arboles: x.dibujar(surf)
        if self.casa: self.casa.dibujar(surf)
        for a in self.animales: a.dibujar(surf)
        
    def to_dict(self, persona):
        return {
            "persona": persona.to_dict(),
            "animales": [a.to_dict() for a in self.animales if a != persona],
            "plantas": [p.to_dict() for p in self.plantas],
            "algas": [a.to_dict() for a in self.algas],
            "arboles": [t.to_dict() for t in self.arboles],
            "huevos": [h.to_dict() for h in self.huevos],
            "casa": self.casa.to_dict() if self.casa else None,
            "lago": self.lago.to_dict() if self.lago else None,
        }

    @classmethod
    def from_dict(cls, data):
        eco = cls()
        
        if data.get("casa"): eco.casa = Casa.from_dict(data["casa"])
        if data.get("lago"): eco.lago = Lago.from_dict(data["lago"])
        
        for item in data.get("animales", []):
            animal_cls = CLASE_MAP.get(item["__class__"])
            if animal_cls: eco.animales.append(animal_cls.from_dict(item))
            
        for item in data.get("plantas", []):
            eco.plantas.append(Planta.from_dict(item))
            
        for item in data.get("algas", []):
            eco.algas.append(Alga.from_dict(item))

        for item in data.get("arboles", []):
            eco.arboles.append(Arbol.from_dict(item))

        for item in data.get("huevos", []):
            eco.huevos.append(Huevo.from_dict(item))

        return eco


def inicializar():
    eco = Ecosistema()
    eco.casa = Casa(ANCHO-120, 20); eco.lago = Lago(ANCHO//2-150, ALTO-200, 300, 150)
    for p in [(50,50), (150,100), (300,30), (700,400)]: eco.arboles.append(Arbol(*p))
    obs = eco.obtener_obstaculos()
    for _ in range(30): x,y=generar_spawn_seguro(obs,10); eco.plantas.append(Planta(x,y))
    clases = [Vaca, Gallina, Zorro, Caballo, Oso, Cerdo, Lobo, Rana]; cant = [3, 5, 1, 2, 1, 2, 1, 2]
    for cls, c in zip(clases, cant):
        for _ in range(c):
            x,y = (random.randint(0,ANCHO), random.randint(0,ALTO)) if cls==Rana else generar_spawn_seguro(obs,35)
            if x!=0: eco.agregar_animal(cls(x,y))
    for _ in range(4):
        r=eco.lago.rect_agua; x,y=random.randint(r.x,r.right-30),random.randint(r.y,r.bottom-30); eco.agregar_animal(Pez(x,y))
    return eco

def manejar_clic_animal(pos, eco):
    x, y = pos[0]-17, pos[1]-17
    rect = pygame.Rect(x, y, 35, 35)
    obs = eco.obtener_obstaculos()
    if any(rect.colliderect(o) for o in obs): return 
    
    en_agua = eco.lago.rect_agua.colliderect(rect)
    cls = random.choice([Vaca, Gallina, Zorro, Caballo, Oso, Cerdo, Lobo, Rana])
    if en_agua: eco.agregar_animal(Pez(x, y))
    else: eco.agregar_animal(cls(x, y))




# capa vista





COLOR_MENU = (100, 100, 100)
COLOR_BOTON = (0, 200, 0)
COLOR_BOTON_CARGAR = (200, 150, 0)
COLOR_TEXTO = (255, 255, 255)
COLOR_HUD = (0, 0, 0)

pygame.init()
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Simulador Ecosistema Completo")
reloj = pygame.time.Clock()

F_G = pygame.font.SysFont(None, 48)
F_M = pygame.font.SysFont(None, 32)
F_N = pygame.font.SysFont(None, 16)
F_I = pygame.font.SysFont(None, 24)


def cargar_imagen_segura(ruta, tam=(40, 40), color=(200, 200, 200), flip=False):
    try:
        img = pygame.image.load(ruta)
        img = pygame.transform.scale(img, tam)
        if flip: img = pygame.transform.flip(img, True, False)
        return img
    except:
        s = pygame.Surface(tam); s.fill(color); return s


try:
    FONDO_JUEGO = cargar_imagen_segura(os.path.join(IMAGES_DIR, "fondo.png"), tam=(ANCHO, ALTO))
    FONDO_MENU = cargar_imagen_segura(os.path.join(IMAGES_DIR, "menu_fondo.png"), tam=(ANCHO, ALTO))
    IMG_CORAZON_LLENO = cargar_imagen_segura(os.path.join(IMAGES_DIR, "corazon_lleno.png"), tam=(10, 10), color=(255, 0, 0))
    IMG_CORAZON_VACIO = cargar_imagen_segura(os.path.join(IMAGES_DIR, "corazon_vacio.png"), tam=(10, 10), color=(50, 0, 0))
    USAR_IMAGEN_CORAZON = (IMG_CORAZON_LLENO.get_width() == 10)
except:
    USAR_IMAGEN_CORAZON = False
    FONDO_JUEGO = pygame.Surface((ANCHO, ALTO)); FONDO_JUEGO.fill((135, 206, 235))
    FONDO_MENU = pygame.Surface((ANCHO, ALTO)); FONDO_MENU.fill(COLOR_MENU)

def dibujar_corazones(surf, x, y, vida, max_c=3):
    llenos = int((vida / 100) * max_c)
    sx = x + 35 // 2 - (max_c * 12) // 2
    for i in range(max_c):
        cx, cy = sx + i * 12, y - 18
        if i < llenos:
            if USAR_IMAGEN_CORAZON: surf.blit(IMG_CORAZON_LLENO, (cx, cy))
            else: pygame.draw.circle(surf, (255, 0, 0), (cx+5, cy+5), 5)
        else:
            if USAR_IMAGEN_CORAZON: surf.blit(IMG_CORAZON_VACIO, (cx, cy))
            else: pygame.draw.circle(surf, (50, 0, 0), (cx+5, cy+5), 5)

class MenuPrincipal:
    def __init__(self):
        self.btn_slot1 = pygame.Rect(ANCHO//2 - 100, 180, 200, 50)
        self.btn_slot2 = pygame.Rect(ANCHO//2 - 100, 250, 200, 50)
        self.btn_auto  = pygame.Rect(ANCHO//2 - 100, 320, 200, 50)

    def dibujar(self, surf):
        surf.blit(FONDO_MENU, (0, 0))
        t = F_G.render("Simulador de Ecosistema", True, COLOR_TEXTO)
        surf.blit(t, t.get_rect(center=(ANCHO//2, 100)))
        
        def dibujar_boton(rect, texto, color, archivo):
            existe = os.path.exists(archivo)
            col = color if existe else (100,100,100) 
            label = texto if existe else f"{texto} (Vacío)"
            if "Auto" in texto: label = "Cargar AutoSave" if existe else "AutoSave (Vacío)"
            pygame.draw.rect(surf, col, rect, border_radius=10)
            txt = F_M.render(label, True, COLOR_TEXTO)
            surf.blit(txt, txt.get_rect(center=rect.center))

        dibujar_boton(self.btn_slot1, "Jugar 1", COLOR_BOTON, RUTAS["slot_1"])
        dibujar_boton(self.btn_slot2, "Jugar 2", COLOR_BOTON, RUTAS["slot_2"])
        dibujar_boton(self.btn_auto,  "Cargar Auto", COLOR_BOTON_CARGAR, RUTAS["auto"])
        
        inst = ["WASD: Mover | E: Recoger | G: Guardar", "Espacio: Spawn Mode | Clic+Arrastrar: Mover"]
        y = ALTO - 80
        for l in inst:
            txt = F_N.render(l, True, COLOR_TEXTO)
            surf.blit(txt, (ANCHO//2 - txt.get_width()//2, y)); y+=20

    def click(self, pos):
        if self.btn_slot1.collidepoint(pos): return "JUGAR", RUTAS["slot_1"]
        if self.btn_slot2.collidepoint(pos): return "JUGAR", RUTAS["slot_2"]
        if self.btn_auto.collidepoint(pos):  return "CARGAR_AUTO", RUTAS["auto"]
        return None, None
    




# capa de persistencia





class Persistencia:
    def __init__(self, archivo="partida.json"):
        self.archivo = archivo
    
    def guarda(self, ecosistema, persona):
        try:
            with open(self.archivo, 'w', encoding='utf-8') as fos:
                json.dump(
                    ecosistema.to_dict(persona),
                    fos,
                    indent=2,
                    ensure_ascii=False
                )
        except Exception as e:
            raise Exception(f"Error al guardar: {e}")
    
    def rescatar(self):
        try:
            if not os.path.exists(self.archivo):
                return None, None
            
            with open(self.archivo, 'r', encoding='utf-8') as fis:
                data = json.load(fis)

                persona = Persona.from_dict(data["persona"])

                ecosistema = Ecosistema.from_dict(data)

                return ecosistema, persona
        
        except Exception as e:
            raise Exception(f"Error al rescatar: {e}")

def guardar_partida(ecosistema, persona, ruta):
    """Función global para guardar una partida en una ruta específica."""
    try:
        Persistencia(ruta).guarda(ecosistema, persona)
        return True
    except Exception as e:
        print(f"Error al guardar partida: {e}")
        return False

def cargar_partida(ruta):
    """Función global para cargar una partida desde una ruta específica."""
    try:
        eco, per = Persistencia(ruta).rescatar()
        return eco, per
    except Exception as e:
        print(f"Error al cargar partida: {e}")
        return None, None


# bucle 

ecosistema, persona = None, None
menu = MenuPrincipal()
estado = "MENU"
modo_spawn = False
corriendo = True
mensaje_guardado = 0
slot_actual = None


EVENTO_AUTOSAVE = pygame.USEREVENT + 1
pygame.time.set_timer(EVENTO_AUTOSAVE, 30000)

while corriendo:
    for e in pygame.event.get():
        if e.type == pygame.QUIT: corriendo = False
        

        if e.type == EVENTO_AUTOSAVE and estado == "JUGANDO":
            guardar_partida(ecosistema, persona, RUTAS["auto"])
            mensaje_guardado = 30 

        if estado == "MENU":
            if e.type == pygame.MOUSEBUTTONDOWN:
                accion, ruta = menu.click(e.pos)
                
                if accion == "JUGAR":
                    slot_actual = ruta
                    eco_c, per_c = cargar_partida(ruta) 
                    if eco_c and per_c: 
                        ecosistema, persona = eco_c, per_c
                    else: 
                        ecosistema, persona = inicializar(), Persona(ANCHO//2, ALTO//2) 
                    estado = "JUGANDO"
                
                elif accion == "CARGAR_AUTO":
                    eco_c, per_c = cargar_partida(ruta) 
                    if eco_c and per_c:
                        ecosistema, persona = eco_c, per_c
                        slot_actual = RUTAS["auto"]
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
                if e.key == pygame.K_ESCAPE: estado = "MENU"
                if e.key == pygame.K_g and slot_actual: 
                    guardar_partida(ecosistema, persona, slot_actual) 
                    mensaje_guardado = 60

    if estado == "JUGANDO":
        persona.mover(pygame.key.get_pressed(), ecosistema) 
        ecosistema.actualizar() 

        
        ventana.blit(FONDO_JUEGO, (0, 0))
        ecosistema.dibujar(ventana)
        persona.dibujar(ventana)
        
        for a in ecosistema.animales:
            if a != persona:
                txt = F_N.render(a.nombre, True, (0,0,0))
                ventana.blit(txt, (a.x+5, a.y+35))

        info = F_N.render(f"Huevos: {persona.inventario['huevos']} | Leche: {persona.inventario['leche']}", True, COLOR_HUD)
        ventana.blit(info, (10, 10))
        
        s_name = "Slot 1" if "slot_1" in str(slot_actual) else "Slot 2" if "slot_2" in str(slot_actual) else "AutoSave"
        ventana.blit(F_N.render(f"Jugando: {s_name}", True, (0,0,255)), (10, 30))
        
        modo = F_N.render(f"SPAWN: {'ON' if modo_spawn else 'OFF'} | G: Guardar | ESC: Salir", True, (0,150,0) if modo_spawn else (50,50,50))
        ventana.blit(modo, (ANCHO - 250, 10))

        if mensaje_guardado > 0:
            msg = F_M.render("PARTIDA GUARDADA", True, (255, 255, 0))
            ventana.blit(msg, (ANCHO//2 - msg.get_width()//2, ALTO - 50))
            mensaje_guardado -= 1
        
    elif estado == "MENU":
        menu.dibujar(ventana) 

    pygame.display.flip()
    reloj.tick(FPS)

pygame.quit()
