import pygame
import random
import math
import os

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

# ----------------------------------------------------

def distancia(a, b):
    # --- CORREGIDO: Acepta objetos o diccionarios ---
    try:
        ax = a.x if hasattr(a, 'x') else a['x']
        ay = a.y if hasattr(a, 'y') else a['y']
        bx = b.x if hasattr(b, 'x') else b['x']
        by = b.y if hasattr(b, 'y') else b['y']
        
        # Corrección: math.sqrt((ax - bx) ** 2 + (ay - by) ** 2)
        dist = math.sqrt((ax - bx) ** 2 + (ay - by) ** 2)
        return max(1, dist)
    except (AttributeError, KeyError):
        return float('inf')


def cargar_imagen_segura(ruta, tam=(40, 40), color=(200, 200, 200), flip_horizontal=False):
    try:
        img = pygame.image.load(ruta).convert_alpha() # Usar convert_alpha para transparencias
        img = pygame.transform.scale(img, tam)
        if flip_horizontal: # Aplicar flip si se solicita
            img = pygame.transform.flip(img, True, False)
        return img
    except Exception as e:
        print(f"[WARN] No se pudo cargar {ruta}: {e}. Usando color de fondo.")
        # --- CORREGIDO: No usar SRCALPHA para el fallback de color sólido ---
        surf = pygame.Surface(tam) 
        surf.fill(color)
        return surf

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

def normalizar_vector(dx, dy):
    # Corrección: math.sqrt(dx**2 + dy**2)
    magnitud = math.sqrt(dx**2 + dy**2)
    if magnitud == 0:
        return 0, 0
    return dx / magnitud, dy / magnitud

def generar_spawn_seguro(obstaculos_rects, tamano_entidad):
    while True:
        x = random.randint(0, ANCHO - tamano_entidad)
        y = random.randint(0, ALTO - tamano_entidad)
        spawn_rect = pygame.Rect(x, y, tamano_entidad, tamano_entidad)
        
        en_obstaculo = False
        for obstaculo in obstaculos_rects:
            if spawn_rect.colliderect(obstaculo):
                en_obstaculo = True
                break
        
        if not en_obstaculo:
            return x, y

# --- NUEVA FUNCIÓN: Generar spawn cerca de un punto ---
def generar_spawn_cerca(punto_x, punto_y, obstaculos_rects, tamano_entidad, radio_max=100):
    """Intenta encontrar un spawn seguro cerca de un punto, si falla, usa el spawn global."""
    for _ in range(50): # Intenta 50 veces
        angulo = random.uniform(0, 2 * math.pi)
        # Spawn un poco alejado (desde el tamaño de la entidad hasta el radio_max), no justo encima
        distancia_spawn = random.uniform(tamano_entidad / 2, radio_max) 
        x = int(punto_x + math.cos(angulo) * distancia_spawn)
        y = int(punto_y + math.sin(angulo) * distancia_spawn)

        # Asegurarse de que esté dentro de la pantalla
        x = max(0, min(ANCHO - tamano_entidad, x))
        y = max(0, min(ALTO - tamano_entidad, y))
        
        spawn_rect = pygame.Rect(x, y, tamano_entidad, tamano_entidad)
        
        en_obstaculo = False
        for obstaculo in obstaculos_rects:
            if spawn_rect.colliderect(obstaculo):
                en_obstaculo = True
                break
        
        if not en_obstaculo:
            return x, y # ¡Éxito!
    
    # Si falla 50 veces, usa el método antiguo para evitar un bucle infinito
    print("[WARN] No se pudo encontrar un spawn seguro cerca del punto, usando spawn aleatorio.")
    return generar_spawn_seguro(obstaculos_rects, tamano_entidad)

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

# -----------------------------------
# CLASE ANIMAL
# -----------------------------------
class Animal(Entidad):
    def __init__(self, nombre, tipo, x, y, imagen_path, default_face_left=False):
        super().__init__(x, y)
        self.nombre = nombre
        self.tipo = tipo
        self.vida = 100
        self.velocidad = random.randint(1, 3)
        self.tamano = 35
        self.reproduccion_contador = random.randint(200, 400)
        
        # --- LÓGICA DE GIRO ---
        imagen_base = cargar_imagen_segura(imagen_path, tam=(self.tamano, self.tamano))
        
        if default_face_left:
            self.imagen_original_derecha = pygame.transform.flip(imagen_base, True, False)
            self.imagen_original_izquierda = imagen_base
            self.mirando_izquierda = True
            self.imagen = self.imagen_original_izquierda
        else:
            self.imagen_original_derecha = imagen_base
            self.imagen_original_izquierda = pygame.transform.flip(imagen_base, True, False)
            self.mirando_izquierda = False
            self.imagen = self.imagen_original_derecha
        # ----------------------------

        self.target_x = random.randint(0, ANCHO)
        self.target_y = random.randint(0, ALTO)
        self.cambio_objetivo_timer = random.randint(60, 180)


    def mover(self, target_x, target_y, ecosistema):
        if target_x is None or target_y is None:
            self.cambio_objetivo_timer -= 1
            obj_simple = {'x': self.target_x, 'y': self.target_y}
            if self.cambio_objetivo_timer <= 0 or distancia(self, obj_simple) < self.velocidad:
                self.target_x = random.randint(0, ANCHO)
                self.target_y = random.randint(0, ALTO)
                self.cambio_objetivo_timer = random.randint(60, 180)
            
            target_x = self.target_x
            target_y = self.target_y

        dx_raw = target_x - self.x
        dy_raw = target_y - self.y

        if abs(dx_raw) < self.velocidad / 2 and abs(dy_raw) < self.velocidad / 2:
            return

        # --- LÓGICA DE GIRO CORREGIDA ---
        if dx_raw < 0 and not self.mirando_izquierda:
            self.imagen = self.imagen_original_izquierda
            self.mirando_izquierda = True
        elif dx_raw > 0 and self.mirando_izquierda:
            self.imagen = self.imagen_original_derecha
            self.mirando_izquierda = False
        # -------------------------------

        ndx, ndy = normalizar_vector(dx_raw, dy_raw)
        move_x = ndx * self.velocidad
        move_y = ndy * self.velocidad

        if ecosistema.lago:
            obstaculos_rects = [ecosistema.lago.rect_orilla]
            for arbol in ecosistema.arboles:
                obstaculos_rects.append(arbol.rect)
            if ecosistema.casa:
                obstaculos_rects.append(ecosistema.casa.rect)

            futuro_rect_x = pygame.Rect(self.x + move_x, self.y, self.tamano, self.tamano)
            for obstaculo in obstaculos_rects:
                if futuro_rect_x.colliderect(obstaculo):
                    if not isinstance(self, (Rana, Pez)): 
                        move_x = 0
                        self.cambio_objetivo_timer = 0
                        break

            futuro_rect_y = pygame.Rect(self.x, self.y + move_y, self.tamano, self.tamano)
            for obstaculo in obstaculos_rects:
                if futuro_rect_y.colliderect(obstaculo):
                    if not isinstance(self, (Rana, Pez)):
                        move_y = 0
                        self.cambio_objetivo_timer = 0
                        break
        
        self.x += move_x
        self.y += move_y
        
        if not isinstance(self, Pez):
            self.x = max(0, min(ANCHO - self.tamano, self.x))
            self.y = max(0, min(ALTO - self.tamano, self.y))

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
class Vaca(Animal):
    def __init__(self, x, y):
        ruta_img = os.path.join(IMAGES_DIR, "vaca.png")
        super().__init__("Vaca", "herbivoro", x, y, ruta_img, default_face_left=True)
        self.leche = 0
        self.contador_leche = 0

    def actualizar(self, ecosistema):
        plantas = ecosistema.plantas
        target_x, target_y = None, None
        
        if self.vida < 90 and plantas:
            objetivo = min(plantas, key=lambda p: distancia(self, p))
            if distancia(self, objetivo) < 15:
                ecosistema.plantas.remove(objetivo)
                self.vida = min(100, self.vida + 15)
            else:
                target_x, target_y = objetivo.x, objetivo.y
        
        super().mover(target_x, target_y, ecosistema)
        self.envejecer()
        
        self.contador_leche += 1
        if self.contador_leche >= 100:
            self.leche = min(10, self.leche + 1)
            self.contador_leche = 0

class Gallina(Animal):
    def __init__(self, x, y):
        ruta_img = os.path.join(IMAGES_DIR, "gallina.png")
        super().__init__("Gallina", "herbivoro", x, y, ruta_img, default_face_left=True)
        self.contador_huevo = random.randint(80, 200)

    def actualizar(self, ecosistema):
        plantas = ecosistema.plantas
        target_x, target_y = None, None
        
        if self.vida < 90 and plantas:
            objetivo = min(plantas, key=lambda p: distancia(self, p))
            if distancia(self, objetivo) < 15:
                ecosistema.plantas.remove(objetivo)
                self.vida = min(100, self.vida + 5)
            else:
                target_x, target_y = objetivo.x, objetivo.y
        
        super().mover(target_x, target_y, ecosistema)
        self.envejecer()
        self.contador_huevo -= 1
        if self.contador_huevo <= 0:
            ecosistema.huevos.append(Huevo(self.x, self.y))
            self.contador_huevo = random.randint(120, 250)

class Zorro(Animal):
    def __init__(self, x, y):
        ruta_img = os.path.join(IMAGES_DIR, "zorro.png")
        super().__init__("Zorro", "carnivoro", x, y, ruta_img, default_face_left=True)
        self.velocidad = 3

    def actualizar(self, ecosistema):
        presas = [a for a in ecosistema.animales if isinstance(a, Gallina) and a.esta_vivo()]
        
        target_x, target_y = None, None
        if self.vida < 90 and presas:
            objetivo = min(presas, key=lambda p: distancia(self, p))
            if distancia(self, objetivo) < 15:
                objetivo.vida = 0
                self.vida = min(100, self.vida + 20)
                target_x = self.x + random.randint(-50, 50)
                target_y = self.y + random.randint(-50, 50)
            else:
                target_x, target_y = objetivo.x, objetivo.y
        
        super().mover(target_x, target_y, ecosistema)
        self.envejecer()

class Caballo(Animal):
    def __init__(self, x, y):
        ruta_img = os.path.join(IMAGES_DIR, "caballo.png")
        super().__init__("Caballo", "herbivoro", x, y, ruta_img, default_face_left=True)
        self.velocidad = random.randint(2, 4)

    def actualizar(self, ecosistema):
        plantas = ecosistema.plantas
        target_x, target_y = None, None
        
        if self.vida < 90 and plantas:
            objetivo = min(plantas, key=lambda p: distancia(self, p))
            if distancia(self, objetivo) < 15:
                ecosistema.plantas.remove(objetivo)
                self.vida = min(100, self.vida + 15)
            else:
                target_x, target_y = objetivo.x, objetivo.y
        
        super().mover(target_x, target_y, ecosistema)
        self.envejecer()
        
        self.reproduccion_contador -= 1
        if self.reproduccion_contador <= 0:
            if random.random() < 0.08:
                obstaculos = [ecosistema.lago.rect_orilla] + [a.rect for a in ecosistema.arboles]
                if ecosistema.casa: obstaculos.append(ecosistema.casa.rect)
                x, y = generar_spawn_seguro(obstaculos, self.tamano)
                ecosistema.agregar_animal(Caballo(x, y))
            self.reproduccion_contador = random.randint(300, 500)

class Pez(Animal):
    def __init__(self, x, y):
        ruta_img = os.path.join(IMAGES_DIR, "pez.png")
        super().__init__("Pez", "herbivoro", x, y, ruta_img, default_face_left=True)
        self.velocidad = random.randint(1, 2)
        self.target_x = x
        self.target_y = y
        self.cambio_objetivo_timer = random.randint(60, 180)

    def mover(self, target_x, target_y, ecosistema):
        if target_x is None or target_y is None:
            self.cambio_objetivo_timer -= 1
            obj_simple = {'x': self.target_x, 'y': self.target_y}
            if self.cambio_objetivo_timer <= 0 or distancia(self, obj_simple) < self.velocidad:
                lago_agua_rect = ecosistema.lago.rect_agua
                self.target_x = random.randint(lago_agua_rect.x, lago_agua_rect.right - self.tamano)
                self.target_y = random.randint(lago_agua_rect.y, lago_agua_rect.bottom - self.tamano)
                self.cambio_objetivo_timer = random.randint(60, 180)
            target_x, target_y = self.target_x, self.target_y

        dx_raw = target_x - self.x
        dy_raw = target_y - self.y

        if abs(dx_raw) < self.velocidad / 2 and abs(dy_raw) < self.velocidad / 2:
            return

        if dx_raw < 0 and not self.mirando_izquierda:
            self.imagen = self.imagen_original_izquierda
            self.mirando_izquierda = True
        elif dx_raw > 0 and self.mirando_izquierda:
            self.imagen = self.imagen_original_derecha
            self.mirando_izquierda = False
            
        ndx, ndy = normalizar_vector(dx_raw, dy_raw)
        move_x = ndx * self.velocidad
        move_y = ndy * self.velocidad

        self.x += move_x
        self.y += move_y

        lago_agua_rect = ecosistema.lago.rect_agua
        self.x = max(lago_agua_rect.x, min(self.x, lago_agua_rect.right - self.tamano))
        self.y = max(lago_agua_rect.y, min(self.y, lago_agua_rect.bottom - self.tamano))
        
    def actualizar(self, ecosistema):
        algas_cercanas = ecosistema.algas
        target_x, target_y = None, None
        
        if self.vida < 90 and algas_cercanas:
            objetivo = min(algas_cercanas, key=lambda a: distancia(self, a))
            if distancia(self, objetivo) < 15:
                ecosistema.algas.remove(objetivo)
                self.vida = min(100, self.vida + 10)
                target_x, target_y = None, None
            else:
                target_x, target_y = objetivo.x, objetivo.y
        
        self.mover(target_x, target_y, ecosistema)
        self.envejecer()

class Oso(Animal):
    def __init__(self, x, y):
        ruta_img = os.path.join(IMAGES_DIR, "oso.png")
        super().__init__("Oso", "omnívoro", x, y, ruta_img, default_face_left=True)
        self.velocidad = random.randint(1, 2)

    def actualizar(self, ecosistema):
        presas = [a for a in ecosistema.animales if isinstance(a, Gallina) and a.esta_vivo()]
        plantas = ecosistema.plantas
        target_x, target_y = None, None
        
        if self.vida < 90:
            if presas and random.random() < 0.5:
                objetivo = min(presas, key=lambda p: distancia(self, p))
                if distancia(self, objetivo) < 18:
                    objetivo.vida = 0
                    self.vida = min(100, self.vida + 15)
                else:
                    target_x, target_y = objetivo.x, objetivo.y
            elif plantas:
                objetivo = min(plantas, key=lambda p: distancia(self, p))
                if distancia(self, objetivo) < 15:
                    ecosistema.plantas.remove(objetivo)
                    self.vida = min(100, self.vida + 10)
                else:
                    target_x, target_y = objetivo.x, objetivo.y
        
        super().mover(target_x, target_y, ecosistema)
        self.envejecer()

class Cerdo(Animal):
    def __init__(self, x, y):
        ruta_img = os.path.join(IMAGES_DIR, "cerdo.png")
        super().__init__("Cerdo", "herbivoro", x, y, ruta_img, default_face_left=True)

    def actualizar(self, ecosistema):
        plantas = ecosistema.plantas
        target_x, target_y = None, None
        
        if self.vida < 90 and plantas:
            objetivo = min(plantas, key=lambda p: distancia(self, p))
            if distancia(self, objetivo) < 15:
                ecosistema.plantas.remove(objetivo)
                self.vida = min(100, self.vida + 10)
            else:
                target_x, target_y = objetivo.x, objetivo.y

        super().mover(target_x, target_y, ecosistema)
        self.envejecer()

class Lobo(Animal):
    def __init__(self, x, y):
        ruta_img = os.path.join(IMAGES_DIR, "lobo.png")
        super().__init__("Lobo", "carnivoro", x, y, ruta_img, default_face_left=False) # Funciona bien
        self.velocidad = random.randint(2, 3)

    def actualizar(self, ecosistema):
        presas = [a for a in ecosistema.animales if isinstance(a, Gallina) and a.esta_vivo()]
        
        target_x, target_y = None, None
        if self.vida < 90 and presas:
            objetivo = min(presas, key=lambda p: distancia(self, p))
            if distancia(self, objetivo) < 15:
                objetivo.vida = 0
                self.vida = min(100, self.vida + 25)
                target_x = self.x + random.randint(-50, 50)
                target_y = self.y + random.randint(-50, 50)
            else:
                target_x, target_y = objetivo.x, objetivo.y
        
        super().mover(target_x, target_y, ecosistema)
        self.envejecer()

class Rana(Animal):
    def __init__(self, x, y):
        ruta_img = os.path.join(IMAGES_DIR, "rana.png")
        super().__init__("Rana", "carnivoro", x, y, ruta_img, default_face_left=False) # Funciona bien

    def actualizar(self, ecosistema):
        mariposas = [a for a in ecosistema.animales if isinstance(a, Mariposa) and a.esta_vivo()]
        
        target_x, target_y = None, None
        if self.vida < 90 and mariposas:
            objetivo = min(mariposas, key=lambda m: distancia(self, m))
            if distancia(self, objetivo) < 20:
                objetivo.vida = 0
                self.vida = min(100, self.vida + 15)
                target_x = self.x + random.randint(-50, 50)
                target_y = self.y + random.randint(-50, 50)
            else:
                target_x, target_y = objetivo.x, objetivo.y
        
        super().mover(target_x, target_y, ecosistema)
        self.envejecer()

class Mariposa(Animal):
    def __init__(self, x, y):
        ruta_img = os.path.join(IMAGES_DIR, "mariposa.png")
        super().__init__("Mariposa", "herbivoro", x, y, ruta_img, default_face_left=True)

    def actualizar(self, ecosistema):
        plantas = ecosistema.plantas
        target_x, target_y = None, None
        
        if self.vida < 90 and plantas:
            objetivo = min(plantas, key=lambda p: distancia(self, p))
            if distancia(self, objetivo) < 15:
                ecosistema.plantas.remove(objetivo)
                self.vida = min(100, self.vida + 5)
            else:
                target_x, target_y = objetivo.x, objetivo.y
        
        super().mover(target_x, target_y, ecosistema)
        self.envejecer()
        
CLASES_ANIMALES = {
    'Vaca': Vaca,
    'Gallina': Gallina,
    'Zorro': Zorro,
    'Caballo': Caballo,
    'Pez': Pez,
    'Oso': Oso,
    'Cerdo': Cerdo,
    'Lobo': Lobo,
    'Rana': Rana,
    'Mariposa': Mariposa
}

# -----------------------------------
# HUEVO
# -----------------------------------
class Huevo(Entidad):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.tiempo = random.randint(200, 400)
        self.tamano = 8
        self.color = (255, 255, 200)

    def actualizar(self, ecosistema):
        self.tiempo -= 1
        if self.tiempo <= 0:
            obstaculos = [ecosistema.lago.rect_orilla] + [a.rect for a in ecosistema.arboles]
            if ecosistema.casa: obstaculos.append(ecosistema.casa.rect)
            x, y = generar_spawn_seguro(obstaculos, 35)
            ecosistema.agregar_animal(Gallina(x, y))
            if self in ecosistema.huevos:
                ecosistema.huevos.remove(self)

    def dibujar(self, superficie):
        pygame.draw.ellipse(superficie, self.color, (self.x, self.y, self.tamano, self.tamano + 5))
        texto = fuente_nombre.render("Huevo", True, (0, 0, 0))
        superficie.blit(texto, (self.x, self.y - 10))

# -----------------------------------
# PLANTA 
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
# FLOR 
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
# ALGA 
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

# -----------------------------------
# LAGO
# -----------------------------------
class Lago(Entidad):
    def __init__(self, x, y, ancho, alto):
        super().__init__(x, y)
        
        self.rect_orilla = pygame.Rect(x, y, ancho, alto) 
        self.rect_agua = pygame.Rect(
            x + GROSOR_ORILLA, 
            y + GROSOR_ORILLA, 
            ancho - GROSOR_ORILLA * 2, 
            alto - GROSOR_ORILLA * 2
        )

        ruta_orilla = os.path.join(IMAGES_DIR, "orilla.png")
        color_fondo_orilla = (210, 180, 140)
        self.imagen_orilla = cargar_imagen_segura(ruta_orilla, tam=(ancho, alto), color=color_fondo_orilla)

        ruta_agua = os.path.join(IMAGES_DIR, "lago.png")
        color_fondo_agua = (0, 0, 139)
        self.imagen_agua = cargar_imagen_segura(ruta_agua, tam=(self.rect_agua.width, self.rect_agua.height), color=color_fondo_agua)

    def dibujar(self, superficie):
        superficie.blit(self.imagen_orilla, (self.rect_orilla.x, self.rect_orilla.y))
        superficie.blit(self.imagen_agua, (self.rect_agua.x, self.rect_agua.y))

# -----------------------------------
# PERSONA
# -----------------------------------
class Persona(Entidad):
    def __init__(self, x, y):
        super().__init__(x, y)
        ruta_img = os.path.join(IMAGES_DIR, "persona.png")
        self.tamano = 35
        
        # --- LÓGICA DE GIRO ---
        # Asumimos que la imagen de persona mira a la derecha
        self.imagen_original_derecha = cargar_imagen_segura(ruta_img, tam=(self.tamano, self.tamano))
        self.imagen_original_izquierda = pygame.transform.flip(self.imagen_original_derecha, True, False)
        self.imagen = self.imagen_original_derecha
        self.mirando_izquierda = False
        # ----------------------------

        self.velocidad = 5
        self.inventario = {"leche": 0, "huevos": 0}


    def mover(self, teclas, ecosistema):
        target_x_offset, target_y_offset = 0, 0

        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            target_x_offset -= self.velocidad
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            target_x_offset += self.velocidad
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            target_y_offset -= self.velocidad
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            target_y_offset += self.velocidad
        
        # --- Lógica de giro de imagen para Persona ---
        if target_x_offset < 0 and not self.mirando_izquierda:
            self.imagen = self.imagen_original_izquierda
            self.mirando_izquierda = True
        elif target_x_offset > 0 and self.mirando_izquierda:
            self.imagen = self.imagen_original_derecha
            self.mirando_izquierda = False
        # -------------------------------------------

        # Normalizar el movimiento si se mueve en diagonal para que no vaya más rápido
        if target_x_offset != 0 and target_y_offset != 0:
            # Corrección: **2 en lugar de *2
            factor = self.velocidad / math.sqrt(target_x_offset**2 + target_y_offset**2)
            target_x_offset *= factor
            target_y_offset *= factor

        move_x = target_x_offset
        move_y = target_y_offset

        if move_x != 0 or move_y != 0:
            obstaculos_rects = [ecosistema.lago.rect_orilla]
            for arbol in ecosistema.arboles:
                obstaculos_rects.append(arbol.rect)
            if ecosistema.casa:
                obstaculos_rects.append(ecosistema.casa.rect)

            futuro_rect_x = pygame.Rect(self.x + move_x, self.y, self.tamano, self.tamano)
            for obstaculo in obstaculos_rects:
                if futuro_rect_x.colliderect(obstaculo):
                    move_x = 0
                    break

            futuro_rect_y = pygame.Rect(self.x, self.y + move_y, self.tamano, self.tamano)
            for obstaculo in obstaculos_rects:
                if futuro_rect_y.colliderect(obstaculo):
                    move_y = 0
                    break
            
            self.x += move_x
            self.y += move_y

        self.x = max(0, min(ANCHO - self.tamano, self.x))
        self.y = max(0, min(ALTO - self.tamano, self.y))

    def recoger(self, ecosistema):
        for animal in ecosistema.animales:
            if isinstance(animal, Vaca) and distancia(self, animal) < 30 and animal.leche > 0:
                self.inventario["leche"] += animal.leche
                animal.leche = 0
        for huevo in ecosistema.huevos[:]:
            if distancia(self, huevo) < 25:
                ecosistema.huevos.remove(huevo)
                self.inventario["huevos"] += 1

    def dibujar(self, superficie):
        superficie.blit(self.imagen, (self.x, self.y))
        texto_nombre = fuente_nombre.render("Persona", True, (0, 0, 0))
        
        texto_rect = texto_nombre.get_rect(centerx=self.x + self.tamano // 2)
        texto_rect.y = self.y + self.tamano + 2
        superficie.blit(texto_nombre, texto_rect)

# -----------------------------------
# ECOSISTEMA
# -----------------------------------
class Ecosistema:
    def __init__(self):
        self.animales = []
        self.plantas = []
        self.huevos = []
        self.algas = []
        self.arboles = []
        self.flores = []
        self.casa = None
        
        self.lago = Lago(x=500, y=350, ancho=250, alto=200)
        self.fondo = FONDO_JUEGO

    def agregar_animal(self, animal):
        self.animales.append(animal)

    def agregar_planta(self, planta):
        self.plantas.append(planta)

    def agregar_arbol(self, arbol):
        self.arboles.append(arbol)
        
    def agregar_flor(self, flor):
        self.flores.append(flor)
        
    def agregar_casa(self, casa):
        self.casa = casa

    def actualizar(self):
        for animal in self.animales:
            animal.actualizar(self)
        for huevo in self.huevos[:]:
            huevo.actualizar(self)
        
        self.animales = [a for a in self.animales if a.esta_vivo()]
        
        obstaculos_spawn = [self.lago.rect_orilla] + [a.rect for a in self.arboles]
        if self.casa:
            obstaculos_spawn.append(self.casa.rect)
        
        if random.random() < 0.25: 
            x, y = generar_spawn_seguro(obstaculos_spawn, Planta(0,0).tamano)
            self.plantas.append(Planta(x, y))
            
        if random.random() < 0.05:
            lago_agua = self.lago.rect_agua
            x = random.randint(lago_agua.x, lago_agua.right - Alga(0,0).tamano)
            y = random.randint(lago_agua.y, lago_agua.bottom - Alga(0,0).tamano)
            self.algas.append(Alga(x, y))

    def dibujar(self, superficie):
        superficie.blit(self.fondo, (0, 0))
        self.lago.dibujar(superficie)
        
        if self.casa:
            self.casa.dibujar(superficie)
        
        for arbol in self.arboles:
            arbol.dibujar(superficie)
        for alga in self.algas:
            alga.dibujar(superficie)
        for planta in self.plantas:
            planta.dibujar(superficie)
        for flor in self.flores:
            flor.dibujar(superficie)
        for animal in self.animales:
            animal.dibujar(superficie) # El método dibujar de Animal ya define self.rect

# -----------------------------------
# CREAR MUNDO
# -----------------------------------
def crear_mundo():
    global persona
    
    ecosistema = Ecosistema()

    lago_orilla_rect = ecosistema.lago.rect_orilla
    lago_agua_rect = ecosistema.lago.rect_agua
    tamano_animal_std = 35
    tamano_persona = 35
    tamano_arbol = 40
    tamano_casa = 60

    obstaculos_totales = [lago_orilla_rect]
    
    CASA_X, CASA_Y = 100, 100
    casa = Casa(CASA_X, CASA_Y, tamano_casa)
    ecosistema.agregar_casa(casa)
    obstaculos_totales.append(casa.rect)

    for _ in range(15):
        x, y = generar_spawn_seguro(obstaculos_totales, tamano_arbol)
        arbol = Arbol(x, y)
        ecosistema.agregar_arbol(arbol)
        obstaculos_totales.append(arbol.rect)

    spawn_cerca_x = CASA_X + (tamano_casa // 2)
    spawn_cerca_y = CASA_Y + tamano_casa + 5 
    
    # --- CORRECCIÓN DEL ERROR: Llamar a la función correcta ---
    spawn_x, spawn_y = generar_spawn_cerca(spawn_cerca_x, spawn_cerca_y, obstaculos_totales, tamano_persona, radio_max=70)
    persona = Persona(spawn_x, spawn_y)

    # Animales terrestres
    for _ in range(3):
        x, y = generar_spawn_seguro(obstaculos_totales, tamano_animal_std)
        ecosistema.agregar_animal(Vaca(x, y))
    for _ in range(4):
        x, y = generar_spawn_seguro(obstaculos_totales, tamano_animal_std)
        ecosistema.agregar_animal(Gallina(x, y))
    for _ in range(2):
        x, y = generar_spawn_seguro(obstaculos_totales, tamano_animal_std)
        ecosistema.agregar_animal(Zorro(x, y))
    for _ in range(2):
        x, y = generar_spawn_seguro(obstaculos_totales, tamano_animal_std)
        ecosistema.agregar_animal(Caballo(x, y))
    for _ in range(1):
        x, y = generar_spawn_seguro(obstaculos_totales, tamano_animal_std)
        ecosistema.agregar_animal(Oso(x, y))
    for _ in range(1):
        x, y = generar_spawn_seguro(obstaculos_totales, tamano_animal_std)
        ecosistema.agregar_animal(Cerdo(x, y))
    for _ in range(1):
        x, y = generar_spawn_seguro(obstaculos_totales, tamano_animal_std)
        ecosistema.agregar_animal(Lobo(x, y))
    for _ in range(2):
        x, y = generar_spawn_seguro(obstaculos_totales, tamano_animal_std)
        ecosistema.agregar_animal(Mariposa(x, y))

    # Animales anfibios
    for _ in range(2):
        x, y = generar_spawn_seguro(obstaculos_totales, tamano_animal_std)
        ecosistema.agregar_animal(Rana(x, y))

    # Peces
    tamano_pez = tamano_animal_std
    for _ in range(4): 
        spawn_x = random.randint(lago_agua_rect.x, lago_agua_rect.right - tamano_pez)
        spawn_y = random.randint(lago_agua_rect.y, lago_agua_rect.bottom - tamano_pez)
        ecosistema.agregar_animal(Pez(spawn_x, spawn_y))

    # Plantas, Algas y Flores iniciales
    for _ in range(40):
        x, y = generar_spawn_seguro(obstaculos_totales, Planta(0,0).tamano)
        ecosistema.agregar_planta(Planta(x, y))
    
    for _ in range(50): 
        x, y = generar_spawn_seguro(obstaculos_totales, Flor(0,0).tamano)
        ecosistema.agregar_flor(Flor(x, y))

    for _ in range(15):
        x = random.randint(lago_agua_rect.x, lago_agua_rect.right - Alga(0,0).tamano)
        y = random.randint(lago_agua_rect.y, lago_agua_rect.bottom - Alga(0,0).tamano)
        ecosistema.algas.append(Alga(x, y))
        
    return ecosistema, persona

# Inicialización del mundo (se reinicia al iniciar)
ecosistema, persona = crear_mundo()

# --- NUEVA VARIABLE GLOBAL PARA CONTROLAR EL MODO DE CLIC ---
MODO_SPAWN_ACTIVO = False

# -----------------------------------
# FUNCIONES DE MENÚ
# -----------------------------------
def dibujar_menu(superficie):
    superficie.blit(FONDO_MENU, (0, 0))
    
    # Título
    titulo = FUENTE_GRANDE.render("Bienvenido al simulador de granja", True, COLOR_TEXTO)
    titulo_rect = titulo.get_rect(center=(ANCHO // 2, ALTO // 3))
    # Sombra
    sombra = FUENTE_GRANDE.render("Bienvenido al simulador de granja", True, (0,0,0))
    superficie.blit(sombra, (titulo_rect.x + 2, titulo_rect.y + 2))
    superficie.blit(titulo, titulo_rect)
    
    # Botón de inicio
    boton_ancho, boton_alto = 200, 70
    boton_x = ANCHO // 2 - boton_ancho // 2
    boton_y = ALTO // 2 # Centrado verticalmente
    
    boton_rect = pygame.Rect(boton_x, boton_y, boton_ancho, boton_alto)
    pygame.draw.rect(superficie, COLOR_BOTON, boton_rect, border_radius=10)
    
    texto_boton = FUENTE_MEDIANA.render("INICIAR", True, COLOR_TEXTO)
    texto_boton_rect = texto_boton.get_rect(center=boton_rect.center)
    superficie.blit(texto_boton, texto_boton_rect)
    
    # --- NUEVO: Instrucciones ---
    texto_inst_1 = fuente_nombre.render("Mover: Flechas o WASD", True, COLOR_TEXTO)
    texto_inst_2 = fuente_nombre.render("Recoger: Tecla 'E'", True, COLOR_TEXTO)
    
    # Posición en la esquina inferior derecha
    superficie.blit(texto_inst_1, (ANCHO - texto_inst_1.get_width() - 15, ALTO - 50))
    superficie.blit(texto_inst_2, (ANCHO - texto_inst_2.get_width() - 15, ALTO - 30))
    
    return boton_rect

def manejar_menu_eventos(evento, boton_rect):
    global ESTADO_JUEGO
    if evento.type == pygame.MOUSEBUTTONDOWN:
        if boton_rect.collidepoint(evento.pos):
            global ecosistema, persona
            ecosistema, persona = crear_mundo()
            ESTADO_JUEGO = "JUGANDO"

# --- NUEVA FUNCIÓN PARA MANEJAR EL CLIC ---
def manejar_clic_animal(posicion_clic):
    global ecosistema
    
    for animal in ecosistema.animales:
        # Verifica si el clic (posicion_clic) colisiona con el área del animal (animal.rect)
        if hasattr(animal, 'rect') and animal.rect.collidepoint(posicion_clic):
            
            # Obtiene la clase del animal que fue clickeado (ej: Vaca, Lobo, Pez)
            clase_animal = animal.__class__
            
            # Lógica especial para Peces: deben spawnear en el lago
            if isinstance(animal, Pez):
                lago_agua_rect = ecosistema.lago.rect_agua
                tamano_pez = animal.tamano # Usamos el tamaño del animal
                x_spawn = random.randint(lago_agua_rect.x, lago_agua_rect.right - tamano_pez)
                y_spawn = random.randint(lago_agua_rect.y, lago_agua_rect.bottom - tamano_pez)
                
            # Lógica para animales terrestres: usan generar_spawn_cerca
            else:
                obstaculos = [ecosistema.lago.rect_orilla] + [a.rect for a in ecosistema.arboles]
                if ecosistema.casa: obstaculos.append(ecosistema.casa.rect)
                # Intenta spawnear cerca del animal clickeado
                x_spawn, y_spawn = generar_spawn_cerca(animal.x, animal.y, obstaculos, animal.tamano, radio_max=50)
            
            # Crea y añade un nuevo animal de la misma clase
            nuevo_animal = clase_animal(x_spawn, y_spawn)
            ecosistema.agregar_animal(nuevo_animal)
            
            # Solo crea uno y sale del bucle
            return True 
    return False

# -----------------------------------
# BUCLE PRINCIPAL
# -----------------------------------
ejecutando = True
while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
            
        if ESTADO_JUEGO == "MENU":
            if 'boton_rect_menu' in locals():
                manejar_menu_eventos(evento, boton_rect_menu)
        elif ESTADO_JUEGO == "JUGANDO":
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_e:
                    persona.recoger(ecosistema)
                # *** CAMBIO SOLICITADO: Alternar MODO_SPAWN_ACTIVO con ESPACIO ***
                if evento.key == pygame.K_SPACE:
                    MODO_SPAWN_ACTIVO = not MODO_SPAWN_ACTIVO

            # *** NUEVO: Manejar el clic del ratón si el modo está activo ***
            if evento.type == pygame.MOUSEBUTTONDOWN and MODO_SPAWN_ACTIVO:
                # Botón 1 es el clic izquierdo
                if evento.button == 1: 
                    manejar_clic_animal(evento.pos)

    if ESTADO_JUEGO == "JUGANDO":
        teclas = pygame.key.get_pressed()
        persona.mover(teclas, ecosistema)
        
        ecosistema.actualizar()

        ecosistema.dibujar(ventana)
        persona.dibujar(ventana)

        fuente = pygame.font.SysFont(None, 24)
        texto = fuente.render(f"Huevos: {persona.inventario['huevos']} | Leche: {persona.inventario['leche']}", True, (0, 0, 0))
        ventana.blit(texto, (10, 10))
        
        # *** NUEVO: Indicador de modo SPAWN ***
        color_modo = (0, 150, 0) if MODO_SPAWN_ACTIVO else (150, 0, 0)
        texto_modo = f"MODO SPAWN: {'ACTIVO (Click en Animal)' if MODO_SPAWN_ACTIVO else 'INACTIVO (Presiona ESPACIO)'}"
        texto_spawn = fuente.render(texto_modo, True, color_modo)
        ventana.blit(texto_spawn, (10, 35))
        
    elif ESTADO_JUEGO == "MENU":
        boton_rect_menu = dibujar_menu(ventana) 

    pygame.display.flip()
    reloj.tick(FPS)

pygame.quit()
