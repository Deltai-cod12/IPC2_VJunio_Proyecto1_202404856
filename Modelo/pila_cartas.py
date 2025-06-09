# LISTA ENLAZADA - pila de cartas

class NodoPila:
    def __init__(self, carta):
        self.carta = carta
        self.siguiente = None

class PilaCartas:
    def __init__(self):
        self.cima = None

    def esta_vacia(self):
        return self.cima is None

    def apilar(self, carta):
        nuevo = NodoPila(carta)
        nuevo.siguiente = self.cima
        self.cima = nuevo

    def desapilar(self):
        if self.esta_vacia():
            return None
        carta = self.cima.carta
        self.cima = self.cima.siguiente
        return carta

    def ver_cima(self):
        return self.cima.carta if self.cima else None

    def imprimir(self):
        actual = self.cima
        while actual:
            print(actual.carta)
            actual = actual.siguiente
