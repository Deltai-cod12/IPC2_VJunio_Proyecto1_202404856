# MODELO - Modelo de mazo de cartas
class Carta:
    def __init__(self, color: str, numero: int):
        self.color = color
        self.numero = numero

    def __str__(self):
        return f"{self.numero} ({self.color})"


class NodoCarta:
    def __init__(self, carta: Carta):
        self.carta = carta
        self.siguiente = None


class ListaCartas:
    def __init__(self):
        self.primero = None

    def insertar(self, carta: Carta):
        nuevo = NodoCarta(carta)
        if not self.primero:
            self.primero = nuevo
            self.primero.siguiente = self.primero
        else:
            actual = self.primero
            while actual.siguiente != self.primero:
                actual = actual.siguiente
            actual.siguiente = nuevo
            nuevo.siguiente = self.primero

    def imprimir(self):
        if not self.primero:
            print("El mazo está vacío.")
            return

        actual = self.primero
        while True:
            print(actual.carta)
            actual = actual.siguiente
            if actual == self.primero:
                break
