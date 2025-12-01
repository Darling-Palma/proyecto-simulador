import pygame
import random
import math
import os


# --- 1. CONFIGURACIÓN GLOBAL Y AYUDAS INICIALES ---

ANCHO, ALTO = 800, 600
FPS = 20
GROSOR_ORILLA = 20

# Inicialización de Pygame (siempre al inicio)
pygame.init()
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Simulador de Ecosistema (Con Casa)")
reloj = pygame.time.Clock()


# Intentar establecer rutas de imágenes
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()
IMAGES_DIR = os.path.join(BASE_DIR, "imagenes") 

ESTADO_JUEGO = "MENU" 
MODO_SPAWN_ACTIVO = False # Nuevo flag para el modo spawn

# Estilos de texto y color
COLOR_MENU = (100, 100, 100)
COLOR_BOTON = (0, 200, 0)
COLOR_TEXTO = (255, 255, 255)
FUENTE_GRANDE = pygame.font.SysFont(None, 48)
FUENTE_MEDIANA = pygame.font.SysFont(None, 32)
fuente_nombre = pygame.font.SysFont(None, 16) 

# Configuración de corazones
TAMANO_CORAZON = 10
USAR_IMAGEN_CORAZON = False
IMAGEN_CORAZON_LLENO = None
IMAGEN_CORAZON_VACIO = None

# --- Funciones de Utilidad (Helpers) ---

def distancia(cosa1, cosa2):
    """Calcula la distancia entre dos objetos con atributos x, y."""
    try:
        ax = cosa1.x
        ay = cosa1.y
        bx = cosa2.x
        by = cosa2.y
        
        distancia_x_temp = ax - bx
        distancia_y_temp = ay - by
        
        x_al_cuadrado = distancia_x_temp * distancia_x_temp
        y_al_cuadrado = distancia_y_temp * distancia_y_temp
        
        suma_total_cuadrados = x_al_cuadrado + y_al_cuadrado
        
        distancia_final = math.sqrt(suma_total_cuadrados)
        
        if distancia_final == 0:
            return 1.0
        
        return distancia_final
    except Exception:
        # En caso de error, devuelve un número gigante para evitar interacción
        return 999999999.0


def normalizar_vector(dx, dy):
    """Convierte un vector de movimiento en un vector unitario."""
    magnitud_temp = dx * dx + dy * dy
    magnitud = math.sqrt(magnitud_temp)
    
    if magnitud == 0:
        return 0.0, 0.0
        
    # División para normalizar (el estilo de novato no usa numpy)
    ndx = dx / magnitud
    ndy = dy / magnitud
    
    return ndx, ndy

def cargar_imagen_segura(ruta, tam=(40, 40), color=(200, 200, 200), flip_horizontal=False):
    """Carga y escala una imagen, o crea un sustituto si falla."""
    try:
        img_temp_cargada = pygame.image.load(ruta)
        img_temp = img_temp_cargada 
        img = pygame.transform.scale(img_temp, tam)
        
        if flip_horizontal == True: 
            img = pygame.transform.flip(img, True, False)
        
        return img
    except Exception:
        # Si falla, crea un cuadrado simple
        surf_error = pygame.Surface(tam) 
        surf_error.fill(color)
        return surf_error

def generar_spawn_seguro(lista_obstaculos_rects, tamano_entidad):
    """Intenta generar coordenadas que no colisionen con los obstáculos."""
    intentos_maximos = 1000 
    
    for intento_actual in range(intentos_maximos):
        
        x_aleatorio = random.randint(0, ANCHO - tamano_entidad)
        y_aleatorio = random.randint(0, ALTO - tamano_entidad)
        
        spawn_rect = pygame.Rect(x_aleatorio, y_aleatorio, tamano_entidad, tamano_entidad)
        
        esta_en_obstaculo = False
        
        for obstaculo in lista_obstaculos_rects:
            colisiona = spawn_rect.colliderect(obstaculo)
            if colisiona == True:
                esta_en_obstaculo = True
                break
        
        if esta_en_obstaculo == False:
            return x_aleatorio, y_aleatorio
    
    # Si falla, devuelve coordenadas por defecto
    return 10, 10

# --- Carga de recursos (para no romper el código) ---
try:
    RUTA_CORAZON_LLENO = os.path.join(IMAGES_DIR, "corazon_lleno.png")
    RUTA_CORAZON_VACIO = os.path.join(IMAGES_DIR, "corazon_vacio.png")
    tam_c = (TAMANO_CORAZON, TAMANO_CORAZON)
    IMAGEN_CORAZON_LLENO = cargar_imagen_segura(RUTA_CORAZON_LLENO, tam=tam_c, color=(255, 0, 0))
    IMAGEN_CORAZON_VACIO = cargar_imagen_segura(RUTA_CORAZON_VACIO, tam=tam_c, color=(50, 0, 0))
    if IMAGEN_CORAZON_LLENO.get_width() == TAMANO_CORAZON: 
        USAR_IMAGEN_CORAZON = True
except Exception:
    USAR_IMAGEN_CORAZON = False

try:
    path_fondo_juego = os.path.join(IMAGES_DIR, "fondo.png")
    FONDO_JUEGO = cargar_imagen_segura(path_fondo_juego, tam=(ANCHO, ALTO))
except Exception:
    FONDO_JUEGO_TEMP = pygame.Surface((ANCHO, ALTO))
    FONDO_JUEGO_TEMP.fill((135, 206, 235))
    FONDO_JUEGO = FONDO_JUEGO_TEMP

try:
    path_menu_fondo = os.path.join(IMAGES_DIR, "menu_fondo.png")
    FONDO_MENU = cargar_imagen_segura(path_menu_fondo, tam=(ANCHO, ALTO))
except Exception:
    FONDO_MENU_TEMP = pygame.Surface((ANCHO, ALTO))
    FONDO_MENU_TEMP.fill(COLOR_MENU)
    FONDO_MENU = FONDO_MENU_TEMP

# ==============================================================================
# ==============================================================================
############################## COMIENZA LA CAPA LÓGICA (MODELO/DATOS) ##############################
# ==============================================================================
# ==============================================================================

class Entidad:
    """Clase base simple para todos los objetos del mundo."""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def dibujar(self, superficie):
        pass

class Planta(Entidad):
    def __init__(self, x_p, y_p):
        super().__init__(x_p, y_p)
        self.tamano = random.randint(5, 12)
        self.crecimiento = 100 
        self.vida = 100
        self.color = (0, random.randint(150, 200), 0) # Verde variado
        self.rect = pygame.Rect(self.x, self.y, self.tamano, self.tamano)

    def crecer(self):
        self.crecimiento += random.uniform(0.1, 0.5)
        if self.crecimiento > 150:
            self.crecimiento = 150
        
        self.vida -= 0.01 # Lenta degradación

    def dibujar(self, superficie):
        self.rect = pygame.draw.circle(superficie, self.color, (int(self.x), int(self.y)), self.tamano // 2)

class Alga(Entidad):
    def __init__(self, x_a, y_a):
        super().__init__(x_a, y_a)
        self.tamano = random.randint(6, 15)
        self.vida = 100
        self.color = (0, random.randint(100, 150), 100) # Azul-Verdoso para alga
        self.rect = pygame.Rect(self.x, self.y, self.tamano, self.tamano)
        
    def crecer(self):
        self.vida += 0.05
        if self.vida > 100:
            self.vida = 100

    def dibujar(self, superficie):
        self.rect = pygame.draw.circle(superficie, self.color, (int(self.x), int(self.y)), self.tamano // 2)

class Huevo(Entidad):
    def __init__(self, x_h, y_h):
        super().__init__(x_h, y_h)
        self.tamano = 15
        self.tiempo_incubacion = random.randint(300, 600)
        self.imagen = cargar_imagen_segura(os.path.join(IMAGES_DIR, "huevo.png"), tam=(self.tamano, self.tamano))
        self.rect = self.imagen.get_rect(topleft=(self.x, self.y))

    def incubar(self, ecosistema_ref):
        self.tiempo_incubacion -= 1
        
        if self.tiempo_incubacion <= 0:
            # Creación de una nueva gallina
            nueva_gallina = Gallina(self.x, self.y)
            ecosistema_ref.animales.append(nueva_gallina)
            return True # Retorna True para ser eliminado
        return False

    def dibujar(self, superficie):
        self.rect = self.imagen.get_rect(topleft=(self.x, self.y)) 
        superficie.blit(self.imagen, (self.x, self.y))


class Animal(Entidad):
    """Clase base para todos los animales, con lógica de movimiento y vida."""
    def __init__(self, nombre_animal, tipo_animal, x_ini, y_ini, imagen_ruta, default_face_left=False):
        super().__init__(x_ini, y_ini)
        self.nombre = nombre_animal
        self.tipo = tipo_animal
        self.vida = 100.0 # Usar flotante para precisión
        self.velocidad = random.randint(1, 3)
        self.tamano = 35
        self.reproduccion_contador = random.randint(200, 400)
        
        imagen_base = cargar_imagen_segura(imagen_ruta, tam=(self.tamano, self.tamano))
        
        # Lógica de giro de imágenes
        if default_face_left == True:
            self.imagen_original_derecha = pygame.transform.flip(imagen_base, True, False)
            self.imagen_original_izquierda = imagen_base
            self.mirando_izquierda = True
            self.imagen = self.imagen_original_izquierda
        else:
            self.imagen_original_derecha = imagen_base
            self.imagen_original_izquierda = pygame.transform.flip(imagen_base, True, False)
            self.mirando_izquierda = False
            self.imagen = self.imagen_original_derecha
        

        self.target_x = random.randint(0, ANCHO)
        self.target_y = random.randint(0, ALTO)
        self.cambio_objetivo_timer = random.randint(60, 180)


    def mover(self, target_x_param, target_y_param, ecosistema_ref):
        
        target_x_real = target_x_param
        target_y_real = target_y_param
        
        if target_x_real is None or target_y_real is None:
            self.cambio_objetivo_timer -= 1
            
            obj_simple = Entidad(self.target_x, self.target_y)
            
            # Chequeo para cambiar de objetivo
            if self.cambio_objetivo_timer <= 0:
                self.target_x = random.randint(0, ANCHO)
                self.target_y = random.randint(0, ALTO)
                self.cambio_objetivo_timer = random.randint(60, 180)
            
            dist_al_objetivo = distancia(self, obj_simple)
            if dist_al_objetivo < self.velocidad * 2:
                self.target_x = random.randint(0, ANCHO)
                self.target_y = random.randint(0, ALTO)
                self.cambio_objetivo_timer = random.randint(60, 180)
            
            target_x_real = self.target_x
            target_y_real = self.target_y

        dx_raw = target_x_real - self.x
        dy_raw = target_y_real - self.y

        distancia_para_parar = self.velocidad / 2
        
        if abs(dx_raw) < distancia_para_parar and abs(dy_raw) < distancia_para_parar:
            return

        
        # Lógica de giro de imagen
        if dx_raw < 0 and self.mirando_izquierda == False:
            self.imagen = self.imagen_original_izquierda
            self.mirando_izquierda = True
        
        if dx_raw > 0 and self.mirando_izquierda == True:
            self.imagen = self.imagen_original_derecha
            self.mirando_izquierda = False
        

        ndx, ndy = normalizar_vector(dx_raw, dy_raw)
        
        move_x = ndx * self.velocidad
        move_y = ndy * self.velocidad

        # Múltiples comprobaciones de colisión con obstáculos (lago, árboles, casa)
        obstaculos_rects = []
        if ecosistema_ref.lago is not None:
            obstaculos_rects.append(ecosistema_ref.lago.rect_orilla)
        for arbol in ecosistema_ref.arboles:
            obstaculos_rects.append(arbol.rect)
        if ecosistema_ref.casa is not None:
            obstaculos_rects.append(ecosistema_ref.casa.rect)
        
        # Chequeo si es un animal acuático/anfibio
        es_acua_anfibio = (self.tipo == "Pez" or self.tipo == "Rana")
        
        # Chequeo de colisión en X
        futuro_rect_x = pygame.Rect(self.x + move_x, self.y, self.tamano, self.tamano)
        for obstaculo in obstaculos_rects:
            if futuro_rect_x.colliderect(obstaculo):
                if es_acua_anfibio == False:
                    move_x = 0
                    self.cambio_objetivo_timer = 0
                    break

        # Chequeo de colisión en Y
        futuro_rect_y = pygame.Rect(self.x, self.y + move_y, self.tamano, self.tamano)
        for obstaculo in obstaculos_rects:
            if futuro_rect_y.colliderect(obstaculo):
                if es_acua_anfibio == False:
                    move_y = 0
                    self.cambio_objetivo_timer = 0
                    break
        
        self.x += move_x
        self.y += move_y
        
        
        # Chequeo de límites de pantalla
        if self.tipo != "Pez":
            if self.x < 0:
                self.x = 0
            if self.x > ANCHO - self.tamano:
                self.x = ANCHO - self.tamano
                
            if self.y < 0:
                self.y = 0
            if self.y > ALTO - self.tamano:
                self.y = ALTO - self.tamano

    def envejecer(self):
        self.vida -= random.uniform(0.01, 0.04)
        
    def esta_vivo(self):
        if self.vida > 0.0:
            return True
        else:
            return False

    def dibujar(self, superficie):
        # La implementación de dibujo está más abajo, en la Capa Vista


# --- Clases de Animales Específicas ---

class Vaca(Animal):
    def __init__(self, x_v, y_v):
        ruta_img = os.path.join(IMAGES_DIR, "vaca.png")
        super().__init__("Vaca", "herbivoro", x_v, y_v, ruta_img, default_face_left=True)
        self.leche = 0
        self.contador_leche = 0
        self.tamano = 45 # Vaca es más grande

    def actualizar(self, ecosistema_ref):
        plantas_disponibles = ecosistema_ref.plantas
        target_x_mov, target_y_mov = None, None
        
        # Lógica de hambre y búsqueda de comida
        if self.vida < 90:
            # Buscar planta más cercana
            objetivo_cercano = None
            distancia_minima = 99999999.0
            for planta_actual in plantas_disponibles:
                dist_actual = distancia(self, planta_actual)
                if dist_actual < distancia_minima:
                    distancia_minima = dist_actual
                    objetivo_cercano = planta_actual

            if objetivo_cercano is not None:
                distancia_actual = distancia(self, objetivo_cercano)
                
                if distancia_actual < 15: # Está cerca, come
                    ecosistema_ref.plantas.remove(objetivo_cercano)
                    self.vida = min(self.vida + 15, 100) # Evita sobrepasar 100
                else:
                    target_x_mov = objetivo_cercano.x
                    target_y_mov = objetivo_cercano.y
        
        super().mover(target_x_mov, target_y_mov, ecosistema_ref)
        self.envejecer()
        
        # Lógica de producción de leche
        self.contador_leche += 1
        if self.contador_leche >= 100:
            self.leche = min(self.leche + 1, 10)
            self.contador_leche = 0

class Gallina(Animal):
    def __init__(self, x_g, y_g):
        ruta_img = os.path.join(IMAGES_DIR, "gallina.png")
        super().__init__("Gallina", "herbivoro", x_g, y_g, ruta_img, default_face_left=True)
        self.contador_huevo = random.randint(80, 200)

    def actualizar(self, ecosistema_ref):
        plantas_disponibles = ecosistema_ref.plantas
        target_x_mov, target_y_mov = None, None
        
        # Lógica de comida (similar a Vaca)
        if self.vida < 90 and len(plantas_disponibles) > 0:
            objetivo_cercano = None
            distancia_minima = 99999999.0
            for planta_actual in plantas_disponibles:
                dist_actual = distancia(self, planta_actual)
                if dist_actual < distancia_minima:
                    distancia_minima = dist_actual
                    objetivo_cercano = planta_actual
                    
            if objetivo_cercano is not None:
                if distancia(self, objetivo_cercano) < 15:
                    ecosistema_ref.plantas.remove(objetivo_cercano)
                    self.vida = min(self.vida + 5, 100)
                else:
                    target_x_mov = objetivo_cercano.x
                    target_y_mov = objetivo_cercano.y
        
        super().mover(target_x_mov, target_y_mov, ecosistema_ref)
        self.envejecer()
        
        # Lógica de puesta de huevo
        self.contador_huevo -= 1
        if self.contador_huevo <= 0:
            huevo_nuevo = Huevo(self.x, self.y)
            ecosistema_ref.huevos.append(huevo_nuevo)
            self.contador_huevo = random.randint(120, 250)

class Zorro(Animal):
    def __init__(self, x_z, y_z):
        ruta_img = os.path.join(IMAGES_DIR, "zorro.png")
        super().__init__("Zorro", "carnivoro", x_z, y_z, ruta_img, default_face_left=True)
        self.velocidad = 3

    def actualizar(self, ecosistema_ref):
        presas_posibles = [a for a in ecosistema_ref.animales if a.nombre == "Gallina" and a.esta_vivo()]
        target_x_mov, target_y_mov = None, None
        
        if self.vida < 90 and len(presas_posibles) > 0:
            # Buscar gallina más cercana
            objetivo_cercano = None
            distancia_minima = 99999999.0
            for presa_actual in presas_posibles:
                dist_actual = distancia(self, presa_actual)
                if dist_actual < distancia_minima:
                    distancia_minima = dist_actual
                    objetivo_cercano = presa_actual
                    
            if objetivo_cercano is not None:
                if distancia(self, objetivo_cercano) < 15: # Alcanzó a la presa
                    objetivo_cercano.vida = 0
                    self.vida = min(self.vida + 20, 100)
                    # Moverse un poco para alejarse de la comida
                    target_x_mov = self.x + random.randint(-50, 50)
                    target_y_mov = self.y + random.randint(-50, 50)
                else:
                    target_x_mov = objetivo_cercano.x
                    target_y_mov = objetivo_cercano.y
        
        super().mover(target_x_mov, target_y_mov, ecosistema_ref)
        self.envejecer()

class Caballo(Animal):
    def __init__(self, x_c, y_c):
        ruta_img = os.path.join(IMAGES_DIR, "caballo.png")
        super().__init__("Caballo", "herbivoro", x_c, y_c, ruta_img, default_face_left=True)
        self.velocidad = random.randint(2, 4)

    def actualizar(self, ecosistema_ref):
        plantas_disponibles = ecosistema_ref.plantas
        target_x_mov, target_y_mov = None, None
        
        if self.vida < 90 and len(plantas_disponibles) > 0:
            objetivo_cercano = None
            distancia_minima = 99999999.0
            for planta_actual in plantas_disponibles:
                dist_actual = distancia(self, planta_actual)
                if dist_actual < distancia_minima:
                    distancia_minima = dist_actual
                    objetivo_cercano = planta_actual
                    
            if objetivo_cercano is not None:
                if distancia(self, objetivo_cercano) < 15:
                    ecosistema_ref.plantas.remove(objetivo_cercano)
                    self.vida = min(self.vida + 15, 100)
                else:
                    target_x_mov = objetivo_cercano.x
                    target_y_mov = objetivo_cercano.y
        
        super().mover(target_x_mov, target_y_mov, ecosistema_ref)
        self.envejecer()
        
        self.reproduccion_contador -= 1
        
        if self.reproduccion_contador <= 0:
            if random.random() < 0.08:
                # Lógica para generar Caballo cerca
                obstaculos = ecosistema_ref.obtener_obstaculos()
                x_spawn, y_spawn = generar_spawn_seguro(obstaculos, self.tamano)
                nuevo_caballo = Caballo(x_spawn, y_spawn)
                ecosistema_ref.agregar_animal(nuevo_caballo)
            self.reproduccion_contador = random.randint(300, 500)

class Pez(Animal):
    def __init__(self, x_p, y_p):
        ruta_img = os.path.join(IMAGES_DIR, "pez.png")
        super().__init__("Pez", "herbivoro", x_p, y_p, ruta_img, default_face_left=True)
        self.velocidad = random.randint(1, 2)
        self.tamano = 30 # Peces son más pequeños
        self.target_x = x_p
        self.target_y = y_p

    def mover(self, target_x_param, target_y_param, ecosistema_ref):
        # Implementación de movimiento DENTRO del lago (sobreescribe el mover base)
        target_x_real, target_y_real = target_x_param, target_y_param
        lago_agua_rect = ecosistema_ref.lago.rect_agua
        
        if target_x_real is None or target_y_real is None:
            self.cambio_objetivo_timer -= 1
            if self.cambio_objetivo_timer <= 0:
                # Nuevo objetivo dentro del área de agua
                self.target_x = random.randint(lago_agua_rect.x, lago_agua_rect.right - self.tamano)
                self.target_y = random.randint(lago_agua_rect.y, lago_agua_rect.bottom - self.tamano)
                self.cambio_objetivo_timer = random.randint(60, 180)
            target_x_real, target_y_real = self.target_x, self.target_y

        dx_raw = target_x_real - self.x
        dy_raw = target_y_real - self.y
        
        if abs(dx_raw) < 1.0 and abs(dy_raw) < 1.0: return
        
        # Lógica de giro (simple)
        if dx_raw < 0 and self.mirando_izquierda == False:
            self.imagen = self.imagen_original_izquierda
            self.mirando_izquierda = True
        
        if dx_raw > 0 and self.mirando_izquierda == True:
            self.imagen = self.imagen_original_derecha
            self.mirando_izquierda = False
            
        ndx, ndy = normalizar_vector(dx_raw, dy_raw)
        move_x = ndx * self.velocidad
        move_y = ndy * self.velocidad

        self.x += move_x
        self.y += move_y

        # Asegurar que no salga del lago (corrección estricta)
        self.x = max(lago_agua_rect.x, min(self.x, lago_agua_rect.right - self.tamano))
        self.y = max(lago_agua_rect.y, min(self.y, lago_agua_rect.bottom - self.tamano))
        
    def envejecer(self):
        # Envejecimiento más lento para peces (menos desgaste de vida)
        self.vida -= random.uniform(0.005, 0.02)

    def actualizar(self, ecosistema_ref):
        algas_cercanas = ecosistema_ref.algas
        target_x_mov, target_y_mov = None, None
        
        if self.vida < 90 and len(algas_cercanas) > 0:
            objetivo_cercano = None
            distancia_minima = 99999999.0
            for alga_actual in algas_cercanas:
                dist_actual = distancia(self, alga_actual)
                if dist_actual < distancia_minima:
                    distancia_minima = dist_actual
                    objetivo_cercano = alga_actual
                    
            if objetivo_cercano is not None:
                if distancia(self, objetivo_cercano) < 15:
                    ecosistema_ref.algas.remove(objetivo_cercano)
                    self.vida = min(self.vida + 10, 100)
                else:
                    target_x_mov = objetivo_cercano.x
                    target_y_mov = objetivo_cercano.y
        
        self.mover(target_x_mov, target_y_mov, ecosistema_ref)
        self.envejecer()


class Oso(Animal):
    def __init__(self, x_o, y_o):
        ruta_img = os.path.join(IMAGES_DIR, "oso.png")
        super().__init__("Oso", "omnivoro", x_o, y_o, ruta_img, default_face_left=True)
        self.velocidad = random.randint(1, 2)
        self.tamano = 40 # Oso un poco más grande

    def actualizar(self, ecosistema_ref):
        # El oso es oportunista: 50% carne, 50% planta
        presas_posibles = [a for a in ecosistema_ref.animales if a.nombre == "Gallina" and a.esta_vivo()]
        plantas_disponibles = ecosistema_ref.plantas
        target_x_mov, target_y_mov = None, None
        
        if self.vida < 90:
            azar = random.random()
            
            if azar < 0.5 and len(presas_posibles) > 0:
                # Buscar carne
                objetivo_cercano = min(presas_posibles, key=lambda p: distancia(self, p))
                
                if distancia(self, objetivo_cercano) < 18:
                    objetivo_cercano.vida = 0
                    self.vida = min(self.vida + 15, 100)
                else:
                    target_x_mov, target_y_mov = objetivo_cercano.x, objetivo_cercano.y
                        
            elif len(plantas_disponibles) > 0:
                # Buscar plantas
                objetivo_cercano = min(plantas_disponibles, key=lambda p: distancia(self, p))
                
                if distancia(self, objetivo_cercano) < 15:
                    ecosistema_ref.plantas.remove(objetivo_cercano)
                    self.vida = min(self.vida + 10, 100)
                else:
                    target_x_mov, target_y_mov = objetivo_cercano.x, objetivo_cercano.y
        
        super().mover(target_x_mov, target_y_mov, ecosistema_ref)
        self.envejecer()

class Cerdo(Animal):
    def __init__(self, x_ce, y_ce):
        ruta_img = os.path.join(IMAGES_DIR, "cerdo.png")
        super().__init__("Cerdo", "omnivoro", x_ce, y_ce, ruta_img, default_face_left=True)
        self.tamano = 38
        self.velocidad = random.randint(1, 2)

    def actualizar(self, ecosistema_ref):
        # El Cerdo come plantas y escombros (huevos)
        plantas_disponibles = ecosistema_ref.plantas
        huevos_disponibles = ecosistema_ref.huevos
        
        target_x_mov, target_y_mov = None, None
        
        if self.vida < 90:
            
            # Prioridad 1: Huevos (fácil proteína)
            if len(huevos_disponibles) > 0:
                objetivo_cercano = min(huevos_disponibles, key=lambda h: distancia(self, h))
                
                if distancia(self, objetivo_cercano) < 20:
                    ecosistema_ref.huevos.remove(objetivo_cercano)
                    self.vida = min(self.vida + 15, 100)
                else:
                    target_x_mov, target_y_mov = objetivo_cercano.x, objetivo_cercano.y
                    
            # Prioridad 2: Plantas
            elif len(plantas_disponibles) > 0:
                objetivo_cercano = min(plantas_disponibles, key=lambda p: distancia(self, p))
                
                if distancia(self, objetivo_cercano) < 15:
                    ecosistema_ref.plantas.remove(objetivo_cercano)
                    self.vida = min(self.vida + 10, 100)
                else:
                    target_x_mov, target_y_mov = objetivo_cercano.x, objetivo_cercano.y

        
        super().mover(target_x_mov, target_y_mov, ecosistema_ref)
        self.envejecer()

class Lobo(Animal):
    def __init__(self, x_l, y_l):
        ruta_img = os.path.join(IMAGES_DIR, "lobo.png")
        super().__init__("Lobo", "carnivoro", x_l, y_l, ruta_img, default_face_left=True)
        self.velocidad = 4 # Más rápido para cazar

    def actualizar(self, ecosistema_ref):
        # El Lobo ataca cualquier herbívoro terrestre (Vaca, Caballo, Gallina)
        presas_posibles = [a for a in ecosistema_ref.animales if a.tipo == "herbivoro" and a.nombre != "Pez" and a.esta_vivo()]
        target_x_mov, target_y_mov = None, None
        
        if self.vida < 90 and len(presas_posibles) > 0:
            objetivo_cercano = min(presas_posibles, key=lambda p: distancia(self, p))
            
            if distancia(self, objetivo_cercano) < 25: # Rango de ataque mayor
                objetivo_cercano.vida = 0
                self.vida = min(self.vida + 30, 100) # Gana más vida
                # Se aleja para digerir
                target_x_mov = self.x + random.randint(-80, 80)
                target_y_mov = self.y + random.randint(-80, 80)
            else:
                target_x_mov = objetivo_cercano.x
                target_y_mov = objetivo_cercano.y
        
        super().mover(target_x_mov, target_y_mov, ecosistema_ref)
        self.envejecer()
        
class Rana(Animal):
    def __init__(self, x_r, y_r):
        ruta_img = os.path.join(IMAGES_DIR, "rana.png")
        super().__init__("Rana", "omnivoro", x_r, y_r, ruta_img, default_face_left=True)
        self.tamano = 25
        self.en_agua = False

    def mover(self, target_x_param, target_y_param, ecosistema_ref):
        # Movimiento simple, sin colisiones con árboles/casa para simplificar su lógica anfibia
        dx_raw = self.target_x - self.x
        dy_raw = self.target_y - self.y

        if abs(dx_raw) < 1.0 and abs(dy_raw) < 1.0:
            self.cambio_objetivo_timer = 0 # Fuerza cambio de objetivo
            return
            
        ndx, ndy = normalizar_vector(dx_raw, dy_raw)
        self.x += ndx * self.velocidad
        self.y += ndy * self.velocidad

        # Chequeo de límites de pantalla
        self.x = max(0, min(self.x, ANCHO - self.tamano))
        self.y = max(0, min(self.y, ALTO - self.tamano))


    def actualizar(self, ecosistema_ref):
        
        # Define si está en agua o tierra
        self.en_agua = ecosistema_ref.lago.rect_agua.collidepoint(self.x + self.tamano/2, self.y + self.tamano/2)
        
        self.cambio_objetivo_timer -= 1
        
        if self.cambio_objetivo_timer <= 0:
            if self.en_agua == True:
                # Objetivo en tierra (saltar fuera)
                self.target_x = random.randint(0, ANCHO)
                self.target_y = random.randint(0, ALTO)
                while ecosistema_ref.lago.rect_agua.collidepoint(self.target_x, self.target_y):
                     self.target_x = random.randint(0, ANCHO)
                     self.target_y = random.randint(0, ALTO)
            else:
                # Objetivo en agua (saltar al agua)
                rect_agua = ecosistema_ref.lago.rect_agua
                self.target_x = random.randint(rect_agua.x, rect_agua.right)
                self.target_y = random.randint(rect_agua.y, rect_agua.bottom)
            
            self.cambio_objetivo_timer = random.randint(100, 200)

        super().mover(None, None, ecosistema_ref)
        self.envejecer()


# --- Objetos Estructurales del Mundo ---

class Arbol(Entidad):
    def __init__(self, x_a, y_a):
        super().__init__(x_a, y_a)
        self.tamano = random.randint(40, 60)
        self.imagen = cargar_imagen_segura(os.path.join(IMAGES_DIR, "arbol.png"), tam=(self.tamano, self.tamano), color=(139, 69, 19))
        self.rect = self.imagen.get_rect(topleft=(self.x, self.y))
        
    def dibujar(self, superficie):
        self.rect = self.imagen.get_rect(topleft=(self.x, self.y)) 
        superficie.blit(self.imagen, (self.x, self.y))
        # Dibujar un rect de colisión simple y bajo para la persona
        pygame.draw.rect(superficie, (0, 0, 0, 0), self.rect, 1) # Invisible, solo para depuración

class Casa(Entidad):
    def __init__(self, x_c, y_c):
        super().__init__(x_c, y_c)
        self.ancho = 100
        self.alto = 100
        self.imagen = cargar_imagen_segura(os.path.join(IMAGES_DIR, "casa.png"), tam=(self.ancho, self.alto), color=(150, 150, 150))
        self.rect = self.imagen.get_rect(topleft=(self.x, self.y))
        
    def dibujar(self, superficie):
        self.rect = self.imagen.get_rect(topleft=(self.x, self.y)) 
        superficie.blit(self.imagen, (self.x, self.y))


class Lago(Entidad):
    def __init__(self, x_l, y_l, ancho_l, alto_l):
        super().__init__(x_l, y_l)
        self.ancho = ancho_l
        self.alto = alto_l
        
        # Rectángulo de la orilla (área total)
        self.rect_orilla = pygame.Rect(self.x, self.y, self.ancho, self.alto)
        
        # Rectángulo del agua (área interior)
        self.rect_agua = pygame.Rect(
            self.x + GROSOR_ORILLA, 
            self.y + GROSOR_ORILLA, 
            self.ancho - 2 * GROSOR_ORILLA, 
            self.alto - 2 * GROSOR_ORILLA
        )

    def dibujar(self, superficie):
        # Dibujar Orilla (marrón)
        pygame.draw.rect(superficie, (139, 69, 19), self.rect_orilla)
        
        # Dibujar Agua (azul)
        pygame.draw.rect(superficie, (0, 191, 255), self.rect_agua)

# --- Clase de Control del Jugador ---

class Persona(Animal): # Hereda de Animal para el movimiento y dibujo
    def __init__(self, x, y):
        ruta_img = os.path.join(IMAGES_DIR, "persona.png")
        super().__init__("Jugador", "humano", x, y, ruta_img, default_face_left=False)
        self.velocidad = 3
        self.inventario = {"huevos": 0, "leche": 0}
        self.tamano = 40
        self.esta_arrastrando = False
        self.objeto_arrastrando = None

    def mover(self, teclas_presionadas, ecosistema_ref):
        # Movimiento basado en teclas (WASD o flechas)
        move_x = 0
        move_y = 0
        
        if teclas_presionadas[pygame.K_LEFT] or teclas_presionadas[pygame.K_a]:
            move_x = -self.velocidad
        if teclas_presionadas[pygame.K_RIGHT] or teclas_presionadas[pygame.K_d]:
            move_x = self.velocidad
        if teclas_presionadas[pygame.K_UP] or teclas_presionadas[pygame.K_w]:
            move_y = -self.velocidad
        if teclas_presionadas[pygame.K_DOWN] or teclas_presionadas[pygame.K_s]:
            move_y = self.velocidad

        # Lógica de giro de imagen
        if move_x < 0 and self.mirando_izquierda == False:
            self.imagen = self.imagen_original_izquierda
            self.mirando_izquierda = True
        
        if move_x > 0 and self.mirando_izquierda == True:
            self.imagen = self.imagen_original_derecha
            self.mirando_izquierda = False


        # Comprobación de colisiones con obstáculos (Casa y Arboles)
        obstaculos = [a.rect for a in ecosistema_ref.arboles]
        if ecosistema_ref.casa is not None:
            obstaculos.append(ecosistema_ref.casa.rect)
        if ecosistema_ref.lago is not None:
            obstaculos.append(ecosistema_ref.lago.rect_orilla)

        # Chequeo de colisión en X
        futuro_rect_x = pygame.Rect(self.x + move_x, self.y, self.tamano, self.tamano)
        for obstaculo in obstaculos:
            if futuro_rect_x.colliderect(obstaculo):
                move_x = 0
                break

        # Chequeo de colisión en Y
        futuro_rect_y = pygame.Rect(self.x, self.y + move_y, self.tamano, self.tamano)
        for obstaculo in obstaculos:
            if futuro_rect_y.colliderect(obstaculo):
                move_y = 0
                break

        self.x += move_x
        self.y += move_y
        
        # Chequeo de límites de pantalla
        self.x = max(0, min(self.x, ANCHO - self.tamano))
        self.y = max(0, min(self.y, ALTO - self.tamano))

    def recoger(self, ecosistema_ref):
        # Recoger Huevos
        huevos_a_recoger = []
        for huevo in ecosistema_ref.huevos:
            if self.rect.colliderect(huevo.rect):
                huevos_a_recoger.append(huevo)

        for huevo in huevos_a_recoger:
            ecosistema_ref.huevos.remove(huevo)
            self.inventario["huevos"] += 1

        # Recoger Leche (de la Vaca más cercana)
        vacas = [a for a in ecosistema_ref.animales if isinstance(a, Vaca) and a.leche > 0]
        if vacas:
            vaca_cercana = min(vacas, key=lambda v: distancia(self, v))
            if distancia(self, vaca_cercana) < 50: # Rango de interacción
                if vaca_cercana.leche > 0:
                    self.inventario["leche"] += 1
                    vaca_cercana.leche -= 1
    
    def intentar_arrastrar(self, mouse_pos, ecosistema_ref):
        if self.objeto_arrastrando is None:
            for animal in ecosistema_ref.animales:
                if animal.rect.collidepoint(mouse_pos):
                    if distancia(self, animal) < 100: # Solo si está cerca
                        self.esta_arrastrando = True
                        self.objeto_arrastrando = animal
                        break
    
    def soltar_objeto(self):
        self.esta_arrastrando = False
        self.objeto_arrastrando = None

# --- Clase Ecosistema (Contenedor y Lógica Central) ---

class Ecosistema:
    def __init__(self):
        self.animales = []
        self.plantas = []
        self.algas = []
        self.arboles = []
        self.huevos = []
        self.casa = None
        self.lago = None
        self.turno = 0

    def agregar_animal(self, animal):
        self.animales.append(animal)
        
    def obtener_obstaculos(self):
        """Devuelve una lista de todos los rects que bloquean el paso."""
        obstaculos = [a.rect for a in self.arboles]
        if self.casa is not None:
            obstaculos.append(self.casa.rect)
        if self.lago is not None:
            obstaculos.append(self.lago.rect_orilla)
        return obstaculos


    def actualizar(self):
        self.turno += 1
        
        # 1. Actualizar Animales (Mover, Comer, Envejecer)
        animales_vivos = []
        for animal in self.animales:
            animal.actualizar(self)
            if animal.esta_vivo() == True:
                animales_vivos.append(animal)
        self.animales = animales_vivos
        
        # 2. Actualizar Plantas y Algas (Crecer)
        plantas_vivas = []
        for planta in self.plantas:
            planta.crecer()
            if planta.vida > 0:
                plantas_vivas.append(planta)
        self.plantas = plantas_vivas
        
        algas_vivas = []
        for alga in self.algas:
            alga.crecer()
            if alga.vida > 0:
                algas_vivas.append(alga)
        self.algas = algas_vivas

        # 3. Actualizar Huevos (Incubar)
        huevos_pendientes = []
        for huevo in self.huevos:
            eclosiono = huevo.incubar(self)
            if eclosiono == False:
                huevos_pendientes.append(huevo)
        self.huevos = huevos_pendientes
        
        # 4. Spawns Automáticos (si la población es baja)
        if len(self.plantas) < 50:
            x, y = generar_spawn_seguro(self.obtener_obstaculos(), 10)
            self.plantas.append(Planta(x, y))
        
        if len(self.algas) < 5:
            # Spawn dentro del lago
            if self.lago is not None:
                rect_agua = self.lago.rect_agua
                x = random.randint(rect_agua.x, rect_agua.right)
                y = random.randint(rect_agua.y, rect_agua.bottom)
                self.algas.append(Alga(x, y))

    def dibujar(self, superficie):
        # La implementación del dibujo está más abajo, en la Capa Vista
        pass 


def inicializar_ecosistema_completo():
    """Función para crear el ecosistema y poblarlo."""
    eco = Ecosistema()
    
    # 1. Crear Estructuras
    eco.casa = Casa(ANCHO - 120, 20)
    
    # Lago rectangular grande
    lago_x = ANCHO // 2 - 150
    lago_y = ALTO - 200
    eco.lago = Lago(lago_x, lago_y, 300, 150)
    
    obstaculos = eco.obtener_obstaculos()

    # 2. Spawn de Arboles (Fijos)
    arbol_posiciones = [
        (50, 50), (150, 100), (300, 30), (700, 400)
    ]
    for x, y in arbol_posiciones:
        eco.arboles.append(Arbol(x, y))

    # 3. Spawn Inicial de Plantas (30)
    for _ in range(30):
        x, y = generar_spawn_seguro(obstaculos, 10)
        eco.plantas.append(Planta(x, y))

    # 4. Spawn Inicial de Algas (5, dentro del lago)
    if eco.lago is not None:
        rect_agua = eco.lago.rect_agua
        for _ in range(5):
            x = random.randint(rect_agua.x, rect_agua.right)
            y = random.randint(rect_agua.y, rect_agua.bottom)
            eco.algas.append(Alga(x, y))

    # 5. Spawn Inicial de Animales
    animales_a_spawnear = {
        Vaca: 3, Gallina: 5, Zorro: 1, Caballo: 2, Oso: 1, Cerdo: 2, Lobo: 1, Rana: 2, Pez: 4
    }
    
    for especie, cantidad in animales_a_spawnear.items():
        for _ in range(cantidad):
            
            es_pez = (especie == Pez)
            es_rana = (especie == Rana) # Rana se spwanea en tierra o cerca del lago
            
            if es_pez == True:
                # Spawn en el agua
                rect_agua = eco.lago.rect_agua
                x = random.randint(rect_agua.x, rect_agua.right - 35)
                y = random.randint(rect_agua.y, rect_agua.bottom - 35)
            
            elif es_rana == True:
                 # Spawn cerca del lago o en el borde
                lago_orilla = eco.lago.rect_orilla
                x = random.randint(lago_orilla.x - 50, lago_orilla.right + 50)
                y = random.randint(lago_orilla.y - 50, lago_orilla.bottom + 50)
                
                # Chequeo simple de límites de pantalla
                x = max(0, min(x, ANCHO - 35))
                y = max(0, min(y, ALTO - 35))
                
            else:
                # Spawn en tierra
                x, y = generar_spawn_seguro(obstaculos, 35)

            eco.agregar_animal(especie(x, y))

    return eco

# ==============================================================================
# ==============================================================================
############################## COMIENZA LA CAPA VISTA Y CONTROL (PYGAME/DIBUJO) ##############################
# ==============================================================================
# ==============================================================================

def dibujar_corazones(superficie, pos_x, pos_y, vida_porcentaje_entidad, max_corazones=3):
    """Dibuja un indicador de vida en forma de corazones."""
    
    porcentaje_calc = vida_porcentaje_entidad / 100.0
    corazones_llenos_float = porcentaje_calc * max_corazones
    corazones_llenos = int(corazones_llenos_float)
    
    # Corrección manual de redondeo
    if (corazones_llenos_float - corazones_llenos) > 0.1:
        corazones_llenos = corazones_llenos + 1
    if corazones_llenos > max_corazones:
        corazones_llenos = max_corazones
        
    total_ancho = max_corazones * TAMANO_CORAZON + (max_corazones - 1) * 2
    offset_inicial_x = 35 // 2
    offset_final_x = offset_inicial_x - total_ancho // 2
    start_x = pos_x + offset_final_x
    
    
    for i in range(max_corazones):
        
        corazon_x = start_x + i * (TAMANO_CORAZON + 2)
        corazon_y = pos_y - 8 - TAMANO_CORAZON
        
        color_corazon = (255, 0, 0) if USAR_IMAGEN_CORAZON == False else (0, 0, 0)

        if i < corazones_llenos:
            if USAR_IMAGEN_CORAZON == True:
                superficie.blit(IMAGEN_CORAZON_LLENO, (corazon_x, corazon_y))
            else:
                pygame.draw.circle(superficie, color_corazon, (corazon_x + TAMANO_CORAZON // 2, corazon_y + TAMANO_CORAZON // 2), TAMANO_CORAZON // 2)
        else:
            if USAR_IMAGEN_CORAZON == True:
                superficie.blit(IMAGEN_CORAZON_VACIO, (corazon_x, corazon_y)) 
            else:
                pygame.draw.circle(superficie, (50, 0, 0), (corazon_x + TAMANO_CORAZON // 2, corazon_y + TAMANO_CORAZON // 2), TAMANO_CORAZON // 2)
                pygame.draw.circle(superficie, (255, 255, 255), (corazon_x + TAMANO_CORAZON // 2, corazon_y + TAMANO_CORAZON // 2), TAMANO_CORAZON // 2, 1)

# Se agrega el método dibujar a la clase Animal y Persona
Animal.dibujar = lambda self, superficie: (
    superficie.blit(self.imagen, (self.x, self.y)),
    setattr(self, 'rect', self.imagen.get_rect(topleft=(self.x, self.y))),
    dibujar_corazones(superficie, self.x, self.y, self.vida),
    superficie.blit(fuente_nombre.render(self.nombre, True, (0, 0, 0)), 
                    fuente_nombre.render(self.nombre, True, (0, 0, 0)).get_rect(centerx=self.x + self.tamano // 2, y=self.y + self.tamano + 2))
)

# Se agrega el método dibujar a la clase Ecosistema
def ecosistema_dibujar(self, superficie):
    # 1. Dibujar Fondo (Tierra)
    superficie.blit(FONDO_JUEGO, (0, 0)) 
    
    # 2. Dibujar Estructuras Fijas
    self.lago.dibujar(superficie)
    
    # 3. Dibujar Algas (dentro del lago)
    for alga in self.algas:
        alga.dibujar(superficie)
        
    # 4. Dibujar Plantas y Huevos (orden importante para superposición)
    for planta in self.plantas:
        planta.dibujar(superficie)
    
    for huevo in self.huevos:
        huevo.dibujar(superficie)

    # 5. Dibujar Arboles
    for arbol in self.arboles:
        arbol.dibujar(superficie)
        
    # 6. Dibujar Casa (último para que quede encima)
    self.casa.dibujar(superficie)
    
    # 7. Dibujar Animales (incluyendo a Pez, Gallina, etc.)
    for animal in self.animales:
        animal.dibujar(superficie)

Ecosistema.dibujar = ecosistema_dibujar # Asignación del método

class MenuPrincipal:
    """Clase simple para manejar la pantalla de inicio."""
    def __init__(self):
        self.boton_rect = pygame.Rect(ANCHO // 2 - 100, ALTO // 2 + 50, 200, 50)

    def dibujar(self, superficie):
        superficie.blit(FONDO_MENU, (0, 0))
        
        # Título
        texto_titulo = FUENTE_GRANDE.render("Simulador de Ecosistema Básico", True, COLOR_TEXTO)
        superficie.blit(texto_titulo, texto_titulo.get_rect(center=(ANCHO // 2, ALTO // 2 - 50)))

        # Botón
        pygame.draw.rect(superficie, COLOR_BOTON, self.boton_rect)
        texto_boton = FUENTE_MEDIANA.render("INICIAR SIMULACIÓN", True, COLOR_TEXTO)
        superficie.blit(texto_boton, texto_boton.get_rect(center=self.boton_rect.center))
        
    def manejar_clic(self, pos):
        if self.boton_rect.collidepoint(pos):
            return "JUGANDO"
        return "MENU"

# --- BUCLE PRINCIPAL Y LÓGICA DE EVENTOS ---

def manejar_clic_animal(pos):
    """Maneja el clic en modo SPAWN para agregar un animal."""
    global ecosistema
    
    # Determinar qué animal spawnear según la posición (simplificación del menú)
    x_spawn, y_spawn = pos[0] - 35 // 2, pos[1] - 35 // 2
    
    # Intentar spawnear un animal al azar (para mantenerlo básico)
    opciones = [Vaca, Gallina, Zorro, Caballo, Oso, Cerdo, Lobo, Rana]
    
    # Si el clic es en el agua, spawnea un pez
    if ecosistema.lago.rect_agua.collidepoint(pos):
        nueva_entidad = Pez(x_spawn, y_spawn)
    else:
        # En tierra: elige al azar un animal terrestre
        EspecieElegida = random.choice(opciones)
        nueva_entidad = EspecieElegida(x_spawn, y_spawn)
        
    ecosistema.agregar_animal(nueva_entidad)

# --- Inicialización del juego y del jugador
ecosistema = inicializar_ecosistema_completo()
persona = Persona(ANCHO // 2, ALTO // 2)
menu = MenuPrincipal()

ejecutando = True
while ejecutando:
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
            
        if ESTADO_JUEGO == "MENU":
            if evento.type == pygame.MOUSEBUTTONDOWN:
                ESTADO_JUEGO = menu.manejar_clic(evento.pos)
        
        elif ESTADO_JUEGO == "JUGANDO":
            # Eventos del Jugador
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if persona.rect.collidepoint(evento.pos):
                    persona.intentar_arrastrar(evento.pos, ecosistema)
                elif MODO_SPAWN_ACTIVO:
                    manejar_clic_animal(evento.pos)
                    
            if evento.type == pygame.MOUSEBUTTONUP:
                persona.soltar_objeto()
                
            if evento.type == pygame.MOUSEMOTION and persona.esta_arrastrando:
                # Mueve el objeto arrastrado a la posición del ratón (desplazado)
                if persona.objeto_arrastrando is not None:
                    obj = persona.objeto_arrastrando
                    obj.x = evento.pos[0] - obj.tamano // 2
                    obj.y = evento.pos[1] - obj.tamano // 2

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    global MODO_SPAWN_ACTIVO
                    MODO_SPAWN_ACTIVO = not MODO_SPAWN_ACTIVO
                if evento.key == pygame.K_e:
                    persona.recoger(ecosistema)
    
    
    if ESTADO_JUEGO == "JUGANDO":
        
        # 1. Movimiento del Jugador y Objetos Arrastrados
        teclas = pygame.key.get_pressed()
        persona.mover(teclas, ecosistema)
        
        # 2. Lógica del Ecosistema
        ecosistema.actualizar()

        # 3. Dibujo (Orden de capas)
        ecosistema.dibujar(ventana)
        persona.dibujar(ventana)

        # 4. Dibujo de HUD/Texto de Estado
        texto_inventario = fuente_nombre.render(
            f"Huevos: {persona.inventario['huevos']} | Leche: {persona.inventario['leche']}", 
            True, (0, 0, 0)
        )
        ventana.blit(texto_inventario, (10, 10))
        
        texto_estado = fuente_nombre.render(
            f"Turno: {ecosistema.turno} | Animales: {len(ecosistema.animales)} | Plantas: {len(ecosistema.plantas)}",
            True, (0, 0, 0)
        )
        ventana.blit(texto_estado, (10, 30))
        
        # Indicador de modo SPAWN
        color_modo = (0, 150, 0) if MODO_SPAWN_ACTIVO else (150, 0, 0)
        texto_modo = fuente_nombre.render(f"MODO SPAWN (ESPACIO): {'ACTIVO' if MODO_SPAWN_ACTIVO else 'INACTIVO'}", True, color_modo)
        ventana.blit(texto_modo, (ANCHO - texto_modo.get_width() - 10, 10))


    elif ESTADO_JUEGO == "MENU":
        menu.dibujar(ventana)

    pygame.display.flip()
    reloj.tick(FPS)

pygame.quit()
