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
