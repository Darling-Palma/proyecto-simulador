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
            col = color if existe else (100,100,100) # Gris si no hay partida
            label = texto if existe else f"{texto} (Vacío)"
            if "Auto" in texto: label = "Cargar AutoSave" if existe else "AutoSave (Vacío)"
            pygame.draw.rect(surf, col, rect, border_radius=10)
            txt = F_M.render(label, True, COLOR_TEXTO)
            surf.blit(txt, txt.get_rect(center=rect.center))

        dibujar_boton(self.btn_slot1, "Jugar Slot 1", COLOR_BOTON, RUTAS["slot_1"])
        dibujar_boton(self.btn_slot2, "Jugar Slot 2", COLOR_BOTON, RUTAS["slot_2"])
        dibujar_boton(self.btn_auto,  "Cargar Auto", COLOR_BOTON_CARGAR, RUTAS["auto"])
        
        inst = ["WASD: Mover | E: Recoger | G: Guardar", "Espacio: Spawn Mode | Clic+Arrastrar: Mover"]
        y = ALTO - 80
        for l in inst:
            txt = F_N.render(l, True, COLOR_TEXTO)
            surf.blit(txt, (ANCHO//2 - txt.get_width()//2, y)); y+=20

    def click(self, pos):
        # Esta función devuelve: ACCIÓN, RUTA (Lógica del menú)
        if self.btn_slot1.collidepoint(pos): return "JUGAR", RUTAS["slot_1"]
        if self.btn_slot2.collidepoint(pos): return "JUGAR", RUTAS["slot_2"]
        if self.btn_auto.collidepoint(pos):  return "CARGAR_AUTO", RUTAS["auto"]
        return None, None
