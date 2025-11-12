# -----------------------------------
# FUNCIONES ÚTILES
# -----------------------------------
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
        
        # --- LÓGICA DE GIRO --- (La carga es lógica)
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

        # --- LÓGICA DE GIRO CORREGIDA (Lógica de decisión) ---
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
        # ... Este código es de Sebastian (Visual), pero la clase lo necesita para funcionar. ...
        self.rect = self.imagen.get_rect(topleft=(self.x, self.y)) 
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
        
# -----------------------------------
# DICCIONARIO PARA CREACIÓN DINÁMICA DE ANIMALES
# (Necesario para el clic)
# -----------------------------------                                                  

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
