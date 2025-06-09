#LISTA ENLAZADA - Jugadores

from Modelo.pila_cartas import PilaCartas

class Jugador:
    def __init__(self, nombre: str):
        self.nombre = nombre
        self.mazo = PilaCartas()  
        self.siguiente = None

    def __str__(self):
        return self.nombre



class NodoJugador:
    def __init__(self, jugador: Jugador):
        self.jugador = jugador
        self.siguiente = None


class ListaJugadores:
    def __init__(self):
        self.primero = None
        self.longitud = 0

    def insertar(self, jugador: Jugador):
        nuevo = NodoJugador(jugador)
        if not self.primero:
            self.primero = nuevo
            self.primero.siguiente = self.primero
        else:
            actual = self.primero
            while actual.siguiente != self.primero:
                actual = actual.siguiente
            actual.siguiente = nuevo
            nuevo.siguiente = self.primero
        self.longitud += 1

    def imprimir(self):
        if not self.primero:
            print("No hay jugadores.")
            return

        actual = self.primero
        i = 1
        while True:
            print(f"{i}. {actual.jugador}")
            actual = actual.siguiente
            i += 1
            if actual == self.primero:
                break
