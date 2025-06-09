import xml.etree.ElementTree as ET

from Controlador.mazo_controlador import MazoControlador
from Vista.mazo_vista import mostrar_mazo

from Controlador.jugadores_controlador import JugadoresControlador
from Vista.jugadores_vista import mostrar_jugadores


def main():
    ruta = "entrada.xml"

    # imprimir mazo
    print("=== MAZO DE CARTAS PARA EL JUEGO ===")
    controlador_mazo = MazoControlador()
    controlador_mazo.cargar_cartas(ruta)
    mostrar_mazo(controlador_mazo.mazo)

    # imprimir los jugadores
    print("\n=== JUGADORES CARGADOS PARA EL JUEGO ===")
    controlador_jugadores = JugadoresControlador()
    controlador_jugadores.cargar_jugadores(ruta)
    mostrar_jugadores(controlador_jugadores.jugadores)


if __name__ == "__main__":
    main()
