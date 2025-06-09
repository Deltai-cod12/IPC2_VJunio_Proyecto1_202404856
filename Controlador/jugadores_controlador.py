# CONTROLADOR - Lecutra de archivo xml para Jugadores

import xml.etree.ElementTree as ET
from Modelo.jugadores import Jugador, ListaJugadores

class JugadoresControlador:
    def __init__(self):
        self.jugadores = ListaJugadores()

    def cargar_jugadores(self, ruta_xml: str):
        try:
            tree = ET.parse(ruta_xml)
            root = tree.getroot()

            jugadores_xml = root.find("jugadores")
            if jugadores_xml is None:
                print("No se encontró la sección <jugadores> en el XML.")
                return

            contador = 0
            for jugador_elem in jugadores_xml.findall("jugador"):
                nombre = jugador_elem.text.strip()
                if nombre:
                    nuevo_jugador = Jugador(nombre)
                    self.jugadores.insertar(nuevo_jugador)
                    contador += 1
                if contador == 4:
                    break

            print(f"Jugadores cargados: {contador}")

        except Exception as e:
            print(f"Error al cargar jugadores: {e}")
