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
