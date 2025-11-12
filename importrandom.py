import pygame
import random
import math

# -----------------------------
# Configuración inicial
# -----------------------------
ANCHO, ALTO = 800, 600
TAM_CELDA = 40
FILAS = ALTO // TAM_CELDA
COLUMNAS = ANCHO // TAM_CELDA

FPS = 10  # frames por segundo

# Animales se mueven solo cada X frames
FRAMES_PARA_MOVER = 4

# Plantas se reproducen solo cada X frames
FRAMES_PARA_PROPAGAR = 15
PROBABILIDAD_PROPAGACION = 0.2  # 20% de probabilidad por ciclo

# Colores
NEGRO = (0, 0, 0)
VERDE = (34, 139, 34)
AZUL = (0, 0, 255)
ROJO = (255, 0, 0)
BLANCO = (255, 255, 255)

# -----------------------------
# Capa lógica avanzada
# -----------------------------

class SerVivo:
    def __init__(self, x, y, energia=10, edad_max=50):
        self.x = x
        self.y = y
        self.energia = energia
        self.vivo = True
        self.edad = 0
        self.edad_max = edad_max

    def envejecer(self):
        self.edad += 1
        if self.edad >= self.edad_max or self.energia <= 0:
            self.vivo = False

class Planta(SerVivo):
    def __init__(self, x, y):
        super().__init__(x, y, energia=5, edad_max=200)
        self.contador_crecimiento = 0

    def crecer(self):
        self.contador_crecimiento += 1
        if self.contador_crecimiento >= FRAMES_PARA_PROPAGAR:
            self.contador_crecimiento = 0
            if random.random() < PROBABILIDAD_PROPAGACION:
                return Planta(random.randint(0, COLUMNAS-1), random.randint(0, FILAS-1))
        return None

class Animal(SerVivo):
    def __init__(self, x, y, energia=10, edad_max=50, energia_reproduccion=20, prob_reproduccion=0.2):
        super().__init__(x, y, energia, edad_max)
        self.energia_reproduccion = energia_reproduccion
        self.prob_reproduccion = prob_reproduccion
        self.contador_movimiento = 0

    def mover_hacia(self, objetivo):
        self.contador_movimiento += 1
        if self.contador_movimiento < FRAMES_PARA_MOVER:
            return
        self.contador_movimiento = 0
        dx = objetivo.x - self.x
        dy = objetivo.y - self.y
        if dx != 0: dx = dx // abs(dx)
        if dy != 0: dy = dy // abs(dy)
        self.x = max(0, min(COLUMNAS-1, self.x + dx))
        self.y = max(0, min(FILAS-1, self.y + dy))
        self.energia -= 1
        self.envejecer()

    def mover_aleatorio(self):
        self.contador_movimiento += 1
        if self.contador_movimiento < FRAMES_PARA_MOVER:
            return
        self.contador_movimiento = 0
        dx = random.choice([-1, 0, 1])
        dy = random.choice([-1, 0, 1])
        self.x = max(0, min(COLUMNAS-1, self.x + dx))
        self.y = max(0, min(FILAS-1, self.y + dy))
        self.energia -= 1
        self.envejecer()

    def comer(self, lista_objetivos):
        for obj in lista_objetivos:
            if self.x == obj.x and self.y == obj.y and obj.vivo:
                obj.vivo = False
                self.energia += 10
                break

    def puede_reproducir(self):
        return self.energia >= self.energia_reproduccion and random.random() < self.prob_reproduccion

class Herbivoro(Animal):
    def buscar_alimento(self, plantas):
        vivos = [p for p in plantas if p.vivo]
        if not vivos: return None
        return min(vivos, key=lambda p: math.hypot(p.x - self.x, p.y - self.y))

class Carnivoro(Animal):
    def buscar_alimento(self, herbivoros):
        vivos = [h for h in herbivoros if h.vivo]
        if not vivos: return None
        return min(vivos, key=lambda h: math.hypot(h.x - self.x, h.y - self.y))

# -----------------------------
# Ecosistema ajustado
# -----------------------------

class Ecosistema:
    def __init__(self, num_plantas, num_herbivoros, num_carnivoros):
        self.plantas = [Planta(random.randint(0, COLUMNAS-1), random.randint(0, FILAS-1)) for _ in range(num_plantas)]
        self.herbivoros = [Herbivoro(random.randint(0, COLUMNAS-1), random.randint(0, FILAS-1)) for _ in range(num_herbivoros)]
        self.carnivoros = [Carnivoro(random.randint(0, COLUMNAS-1), random.randint(0, FILAS-1)) for _ in range(num_carnivoros)]

    def actualizar(self):
        # Plantas crecen lentamente
        nuevas_plantas = []
        for p in self.plantas:
            nueva = p.crecer()
            if nueva:
                nuevas_plantas.append(nueva)
        self.plantas.extend(nuevas_plantas)

        # Herbívoros
        nuevas_herbivoros = []
        for h in self.herbivoros:
            if h.vivo:
                planta = h.buscar_alimento(self.plantas)
                if planta:
                    h.mover_hacia(planta)
                    h.comer(self.plantas)
                else:
                    h.mover_aleatorio()
                if h.vivo and h.puede_reproducir():
                    h.energia //= 2
                    nuevas_herbivoros.append(Herbivoro(h.x, h.y))
        self.herbivoros.extend(nuevas_herbivoros)

        # Carnívoros
        nuevas_carnivoros = []
        for c in self.carnivoros:
            if c.vivo:
                presa = c.buscar_alimento(self.herbivoros)
                if presa:
                    c.mover_hacia(presa)
                    c.comer(self.herbivoros)
                else:
                    c.mover_aleatorio()
                if c.vivo and c.puede_reproducir():
                    c.energia //= 2
                    nuevas_carnivoros.append(Carnivoro(c.x, c.y))
        self.carnivoros.extend(nuevas_carnivoros)

        # Eliminar muertos
        self.plantas = [p for p in self.plantas if p.vivo]
        self.herbivoros = [h for h in self.herbivoros if h.vivo]
        self.carnivoros = [c for c in self.carnivoros if c.vivo]

# -----------------------------
# Visualización
# -----------------------------

def dibujar_ecosistema(screen, ecosistema):
    screen.fill(NEGRO)

    for p in ecosistema.plantas:
        color_intensidad = max(50, min(255, int(255 * (p.edad / p.edad_max))))
        pygame.draw.rect(screen, (0, color_intensidad, 0), (p.x*TAM_CELDA, p.y*TAM_CELDA, TAM_CELDA, TAM_CELDA))

    for h in ecosistema.herbivoros:
        color_intensidad = max(50, min(255, int(255 * (h.energia / 20))))
        pygame.draw.rect(screen, (0, 0, color_intensidad), (h.x*TAM_CELDA+5, h.y*TAM_CELDA+5, TAM_CELDA-10, TAM_CELDA-10))

    for c in ecosistema.carnivoros:
        color_intensidad = max(50, min(255, int(255 * (c.energia / 20))))
        pygame.draw.rect(screen, (color_intensidad, 0, 0), (c.x*TAM_CELDA+10, c.y*TAM_CELDA+10, TAM_CELDA-20, TAM_CELDA-20))

    font = pygame.font.SysFont(None, 24)
    texto = font.render(f"Plantas: {len(ecosistema.plantas)}  Herbívoros: {len(ecosistema.herbivoros)}  Carnívoros: {len(ecosistema.carnivoros)}", True, BLANCO)
    screen.blit(texto, (10, 10))
    pygame.display.flip()

# -----------------------------
# Ejecución principal
# -----------------------------

def main():
    pygame.init()
    screen = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Simulador Realista Ajustado")
    clock = pygame.time.Clock()

    ecosistema = Ecosistema(num_plantas=40, num_herbivoros=15, num_carnivoros=8)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        ecosistema.actualizar()
        dibujar_ecosistema(screen, ecosistema)
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()

