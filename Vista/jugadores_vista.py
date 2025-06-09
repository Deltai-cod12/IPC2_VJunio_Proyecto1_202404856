# vistas/jugadores_vista.py

def mostrar_jugadores(lista_jugadores):
    print("Jugadores cargados en el juego:")
    if not lista_jugadores or not lista_jugadores.primero:
        print("No hay jugadores cargados.")
        return

    actual = lista_jugadores.primero
    contador = 1
    while True:
        print(f"{contador}. {actual.jugador.nombre}")
        actual = actual.siguiente
        contador += 1
        if actual == lista_jugadores.primero:
            break
