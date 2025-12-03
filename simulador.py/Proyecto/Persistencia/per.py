import json, os
from ..entidades.objetos import Casa, Lago, Arbol
from ..entidades.plantas import Planta
from ..entidades.animales import Vaca, Gallina, Zorro, Caballo, Oso, Cerdo, Lobo, Rana, Pez
from ..logica.utilidades import ARCHIVO_GUARDADO

clase_map = {
    'Vaca': Vaca, 'Gallina': Gallina, 'Zorro': Zorro,
    'Caballo': Caballo, 'Oso': Oso, 'Cerdo': Cerdo,
    'Lobo': Lobo, 'Rana': Rana, 'Pez': Pez
}

def guardar_partida(ecosistema, persona):
    datos = {
        'persona': {
            'x': persona.x, 'y': persona.y,
            'inventario': getattr(persona, 'inventario', {}),
            'mirando_izq': getattr(persona, 'mirando_izq', False)
        },
        'animales': [], 'plantas': [], 'arboles': []
    }
    for a in ecosistema.animales:
        datos['animales'].append({
            'clase': type(a).__name__, 'x': a.x, 'y': a.y,
            'vida': a.vida,
            'leche': getattr(a, 'leche', 0),
            'reproduccion_contador': getattr(a, 'reproduccion_contador', 0)
        })
    for p in ecosistema.plantas:
        datos['plantas'].append({'x': p.x, 'y': p.y, 'vida': p.vida})
    for ar in ecosistema.arboles:
        datos['arboles'].append({'x': ar.x, 'y': ar.y})
    with open(ARCHIVO_GUARDADO, 'w') as f:
        json.dump(datos, f)

def cargar_partida():
    if not os.path.exists(ARCHIVO_GUARDADO):
        return None, None
    with open(ARCHIVO_GUARDADO, 'r') as f:
        datos = json.load(f)
    nuevo_eco = object()  
    return datos
