import pygame, os
from ..logica.utilidades import ANCHO, ALTO, FPS, ARCHIVO_GUARDADO, cargar_imagen_segura, IMAGES_DIR
from ..logica.ecosistema import inicializar
from ..entidades.animales import Pez
from ..entidades.objetos import Casa, Lago
from ..entidades.animales import Vaca, Gallina, Zorro, Caballo, Oso, Cerdo, Lobo, Rana
from ..entidades.plantas import Planta, Alga
from ..entidades.animales import Animal
from ..entidades.objetos import Huevo
from ..persistencia.guardado import guardar_partida, cargar_partida

# Fonts and basic UI constants
COLOR_MENU = (100,100,100)
COLOR_BOTON = (0,200,0)
COLOR_BOTON_CARGAR = (200,150,0)
COLOR_TEXTO = (255,255,255)
COLOR_HUD = (0,0,0)

def dibujar_corazones(superficie, x, y, vida, max_corazones=3, usar_img=None):
    llenos = int((vida / 100) * max_corazones)
    start_x = x + 35 // 2 - (max_corazones * 12) // 2
    for i in range(max_corazones):
        cx, cy = start_x + i * 12, y - 18
        if i < llenos:
            if usar_img: superficie.blit(usar_img[0], (cx, cy))
            else: pygame.draw.circle(superficie, (255,0,0), (cx+5, cy+5), 5)
        else:
            if usar_img: superficie.blit(usar_img[1], (cx, cy))
            else: pygame.draw.circle(superficie, (50,0,0), (cx+5, cy+5), 5)

class MenuPrincipal:
    def __init__(self):
        self.btn_jugar = pygame.Rect(ANCHO//2 - 100, ALTO//2 - 40, 200, 50)
        self.btn_cargar = pygame.Rect(ANCHO//2 - 100, ALTO//2 + 30, 200, 50)
    def dibujar(self, surf, fuente_grande, fuente_mediana, fondo):
        surf.blit(fondo, (0,0))
        t = fuente_grande.render('Simulador de Ecosistema', True, COLOR_TEXTO)
        surf.blit(t, t.get_rect(center=(ANCHO//2, ALTO//3 - 30)))
        pygame.draw.rect(surf, COLOR_BOTON, self.btn_jugar, border_radius=10)
        t1 = fuente_mediana.render('NUEVA PARTIDA', True, COLOR_TEXTO)
        surf.blit(t1, t1.get_rect(center=self.btn_jugar.center))
        if os.path.exists(ARCHIVO_GUARDADO):
            pygame.draw.rect(surf, COLOR_BOTON_CARGAR, self.btn_cargar, border_radius=10)
            t2 = fuente_mediana.render('CARGAR PARTIDA', True, COLOR_TEXTO)
            surf.blit(t2, t2.get_rect(center=self.btn_cargar.center))
    def click(self, pos):
        if self.btn_jugar.collidepoint(pos):
            return 'NUEVA'
        if os.path.exists(ARCHIVO_GUARDADO) and self.btn_cargar.collidepoint(pos):
            return 'CARGAR'
        return 'MENU'

def main():
    pygame.init()
    ventana = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption('Simulador de Ecosistema')
    reloj = pygame.time.Clock()
    FUENTE_GRANDE = pygame.font.SysFont(None, 48)
    FUENTE_MEDIANA = pygame.font.SysFont(None, 32)
    FUENTE_INSTRUCCIONES = pygame.font.SysFont(None, 24)

    # Fondo simples
    FONDO_JUEGO = pygame.Surface((ANCHO, ALTO)); FONDO_JUEGO.fill((135,206,235))
    FONDO_MENU = pygame.Surface((ANCHO, ALTO)); FONDO_MENU.fill(COLOR_MENU)

    menu = MenuPrincipal()
    estado = 'MENU'
    modo_spawn = False
    mensaje_guardado = 0
    ecosistema = None
    persona = None

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); return
            if estado == 'MENU':
                if e.type == pygame.MOUSEBUTTONDOWN:
                    accion = menu.click(e.pos)
                    if accion == 'NUEVA':
                        ecosistema = inicializar()
                        # crear persona simple
                        from ..entidades.animales import Animal
                        persona = Animal('Jugador','humano', ANCHO//2, ALTO//2, os.path.join(IMAGES_DIR, 'persona.png'))
                        persona.tamano = 40; persona.velocidad = 10; persona.inventario = {'huevos':0, 'leche':0}; persona.mirando_izq = False
                        estado = 'JUGANDO'
                    elif accion == 'CARGAR':
                        datos = cargar_partida()
                        if datos:
                            ecosistema = inicializar()
                            persona = Animal('Jugador','humano', datos['persona']['x'], datos['persona']['y'], os.path.join(IMAGES_DIR,'persona.png'))
                            persona.inventario = datos['persona'].get('inventario', {})
                            estado = 'JUGANDO'
            elif estado == 'JUGANDO':
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_SPACE: modo_spawn = not modo_spawn
                    if e.key == pygame.K_e and persona:
                        for h in ecosistema.huevos[:]:
                            if persona.rect.colliderect(h.rect):
                                ecosistema.huevos.remove(h); persona.inventario['huevos'] += 1
                    if e.key == pygame.K_g and persona:
                        guardar_partida(ecosistema, persona)
                        mensaje_guardado = 60
                if e.type == pygame.MOUSEBUTTONDOWN and estado == 'JUGANDO' and modo_spawn:
                    from ..vista.helpers import manejar_clic_animal
                    manejar_clic_animal(e.pos, ecosistema)

        if estado == 'JUGANDO' and persona:
            keys = pygame.key.get_pressed()
            mx = (keys[pygame.K_d] - keys[pygame.K_a]) * getattr(persona,'velocidad',5)
            my = (keys[pygame.K_s] - keys[pygame.K_w]) * getattr(persona,'velocidad',5)
            persona.x = max(0, min(ANCHO-getattr(persona,'tamano',35), persona.x + mx))
            persona.y = max(0, min(ALTO-getattr(persona,'tamano',35), persona.y + my))
            if hasattr(persona,'rect'): persona.rect.topleft = (persona.x, persona.y)
            ecosistema.actualizar()

        ventana.blit(FONDO_JUEGO, (0,0))
        if estado == 'MENU':
            menu.dibujar(ventana, FUENTE_GRANDE, FUENTE_MEDIANA, FONDO_MENU)
        elif estado == 'JUGANDO' and ecosistema:
            ecosistema.dibujar(ventana)
            if persona:
                try:
                    persona_surface = pygame.Surface((getattr(persona,'tamano',40), getattr(persona,'tamano',40)))
                    persona_surface.fill((255,255,0))
                    ventana.blit(persona_surface, (persona.x, persona.y))
                except:
                    pass
            if mensaje_guardado > 0:
                msg = FUENTE_MEDIANA.render('PARTIDA GUARDADA', True, (255,255,0))
                ventana.blit(msg, (ANCHO//2 - msg.get_width()//2, ALTO - 50))
                mensaje_guardado -= 1

        pygame.display.flip()
        reloj.tick(FPS)

if __name__ == '__main__':
    main()
