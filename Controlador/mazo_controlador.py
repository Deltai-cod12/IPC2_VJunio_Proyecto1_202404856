#CONTROLADOR- Mazo de cartas
import xml.etree.ElementTree as ET
from Modelo.mazo import Carta, ListaCartas

COLORES_VALIDOS = {"#c72623", "#efc12c", "#15629b", "#39843e"}

class MazoControlador:
    def __init__(self):
        self.mazo = ListaCartas()

    def cargar_cartas(self, ruta_xml):
        tree = ET.parse(ruta_xml)
        root = tree.getroot()

        cartas = root.find('mazo_disponible/cartas')

        contador = 0
        for carta_elem in cartas.findall('carta'):
            color = carta_elem.attrib.get('color', '').lower()
            try:
                numero = int(carta_elem.text.strip())
            except:
                continue

            if color in COLORES_VALIDOS and 1 <= numero <= 9:
                self.mazo.insertar(Carta(color, numero))
                contador += 1

            if contador == 51:
                break
        print(f"Cartas cargadas: {contador}")
