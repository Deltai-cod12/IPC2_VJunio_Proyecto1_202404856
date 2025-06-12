# Modelo/partida.py
from typing import Union

# Clase para representar una Carta
class Carta:
    def __init__(self, color: str, numero: int):
        self.color = color
        self.numero = numero

    def __str__(self):
        return f"{self.numero} ({self.color})"

    def __repr__(self): # Para una representación más útil en depuración
        return f"Carta(color='{self.color}', numero={self.numero})"

    def __eq__(self, other): # Para comparar cartas, útil en el TDA
        if not isinstance(other, Carta):
            return NotImplemented
        return self.color == other.color and self.numero == other.numero

# --- Inicio de Estructuras de Datos Personalizadas ---

# Nodo para la Lista Circular Simplemente Enlazada (Mazo)
class NodoCarta:
    def __init__(self, carta: Carta):
        self.carta = carta
        self.siguiente = None # Puntero al siguiente nodo

# Implementación de la Lista Circular Simplemente Enlazada (ListaCartas)
# Usada para el mazo de reserva
class ListaCartas:
    def __init__(self):
        self.primero = None # Primer nodo de la lista
        self.ultimo = None  # Último nodo de la lista (para inserciones O(1) al final)
        self.size = 0       # Contador de elementos

    def insertar(self, carta: Carta):
        nuevo_nodo = NodoCarta(carta)
        if not self.primero: # Si la lista está vacía
            self.primero = nuevo_nodo
            self.ultimo = nuevo_nodo
            self.ultimo.siguiente = self.primero # El último apunta a sí mismo (circular)
        else: # Si la lista ya tiene elementos
            self.ultimo.siguiente = nuevo_nodo    # El último actual apunta al nuevo
            nuevo_nodo.siguiente = self.primero   # El nuevo apunta al primero (circular)
            self.ultimo = nuevo_nodo              # El nuevo nodo es el último
        self.size += 1

    def get_display_string(self) -> str:
        if not self.primero:
            return "Mazo vacío."

        actual = self.primero
        cards_str_parts = ""
        nodes_displayed_count = 0

        max_iterations = self.size * 2 + 5 # Un margen de seguridad para bucles infinitos

        for _ in range(max_iterations):
            if actual is None:
                print("DEBUG_DISPLAY: get_display_string encontró None. Lista rota.")
                break

            if nodes_displayed_count == self.size and actual == self.primero:
                break

            if nodes_displayed_count > 0:
                cards_str_parts += " -> "
            cards_str_parts += str(actual.carta)

            nodes_displayed_count += 1
            actual = actual.siguiente

            if nodes_displayed_count > self.size and actual == self.primero:
                print(f"DEBUG_DISPLAY: Advertencia: Ciclo detectado y tamaño de lista excedido en display string. Nodos: {nodes_displayed_count}")
                break

        if nodes_displayed_count != self.size and self.size > 0:
            print(f"DEBUG_DISPLAY: Advertencia: get_display_string mostró {nodes_displayed_count} nodos, se esperaban {self.size}.")

        return cards_str_parts

    def clear(self):
        """
        Vacía la lista de cartas.
        """
        self.primero = None
        self.ultimo = None
        self.size = 0

    def shuffle_right(self, movimientos: int):
        """
        Mueve las últimas 'movimientos' cartas al principio de la lista, manteniendo su orden relativo.
        Simula un "shift" hacia la derecha.
        """
        if self.primero is None or self.size <= 1 or movimientos == 0:
            return

        movimientos_efectivos = movimientos % self.size
        if movimientos_efectivos == 0:
            return

        new_last_candidate = self.primero
        for _ in range(self.size - movimientos_efectivos - 1):
            if new_last_candidate is None:
                print("DEBUG: Error en shuffle_right: Mazo inesperadamente corto al buscar new_last_candidate.")
                return
            new_last_candidate = new_last_candidate.siguiente

        new_first_candidate = new_last_candidate.siguiente if new_last_candidate else None

        if new_first_candidate is None:
            print("DEBUG: Error en shuffle_right: new_first_candidate es None.")
            return

        self.primero = new_first_candidate
        self.ultimo = new_last_candidate
        self.ultimo.siguiente = self.primero

        print(f"DEBUG: Mazo después de RIGHT_SHUFFLE (size: {self.size}): {self.get_display_string()}")


    def half_shuffle(self):
        """
        Implementa el shuffle "medio" para lista circular simplemente enlazada.
        Divide el mazo de 51 cartas en 25 (seg1), 1 (pivote), 25 (seg2).
        Nuevo orden: Segmento 2 -> Pivote -> Segmento 1 (circular)
        """
        if self.size != 51:
            print(f"DEBUG: Half Shuffle solo aplica a mazos de 51 cartas. Tamaño actual: {self.size}. No se aplicó.")
            return

        print("DEBUG: Iniciando HALF_SHUFFLE (lista simplemente enlazada)...")

        seg1_fin = self.primero
        for _ in range(24):
            if seg1_fin is None:
                print("DEBUG: Error en half_shuffle: Mazo inesperadamente corto al buscar seg1_fin.")
                return
            seg1_fin = seg1_fin.siguiente

        if seg1_fin is None: # Seguridad
            print("DEBUG: Error en half_shuffle: seg1_fin es None.")
            return

        pivote_node = seg1_fin.siguiente # Nodo en la posición 25 (el 26º elemento)
        if pivote_node is None:
            print("DEBUG: Error en half_shuffle: pivote_node es None.")
            return

        seg2_inicio = pivote_node.siguiente # Nodo en la posición 26 (el 27º elemento)
        if seg2_inicio is None:
            print("DEBUG: Error en half_shuffle: seg2_inicio es None.")
            return

        seg2_fin = self.ultimo # El último nodo de la lista es el final del segmento 2

        seg1_fin.siguiente = None # Romper enlace entre seg1 y pivote
        pivote_node.siguiente = None # Romper enlace entre pivote y seg2

        seg2_fin.siguiente = pivote_node
        pivote_node.siguiente = self.primero # self.primero es seg1_inicio

        self.primero = seg2_inicio
        self.ultimo = seg1_fin
        self.ultimo.siguiente = self.primero

        print(f"DEBUG: Mazo después de HALF_SHUFFLE (size: {self.size}): {self.get_display_string()}")


    def faro_shuffle(self):
        """
        Implementación exacta del Faro Shuffle que reproduce el ordenamiento específico mostrado en el XML
        y en el ejemplo de 13 cartas proporcionado por el usuario.
        - Divide el mazo en 25 (mitad A) + 1 (pivote) + 25 (mitad B) cartas.
        - Subdivide cada mitad en 'impares' (posiciones 1-indexadas, que son índices pares 0-indexados)
        y 'pares' (posiciones 1-indexadas, que son índices impares 0-indexados) dentro de cada mitad.
        - Intercala en el orden: impares_A, pares_B, luego pivote, luego impares_B, pares_A.
        """
        if self.size != 51:
            print(f"DEBUG: Faro Shuffle requiere 51 cartas. Tamaño actual: {self.size}.")
            return

        print("DEBUG: Iniciando FARO_SHUFFLE (implementación exacta de la lógica de usuario)...")

        # Paso 1: Extraer todas las cartas del mazo actual a una ListaGenerica para fácil acceso por índice.
        temp_original_deck_lg = ListaGenerica()
        current_node_lc = self.primero
        for _ in range(self.size):
            if current_node_lc is None:
                print("DEBUG: Error en faro_shuffle: Mazo inesperadamente corto al copiar a temp_original_deck_lg.")
                return
            temp_original_deck_lg.agregar_final(current_node_lc.carta) # Agrega el objeto Carta
            current_node_lc = current_node_lc.siguiente

        self.clear() # Limpiar el mazo principal para reconstruirlo

        # Preparar las listas para los subgrupos usando ListaGenerica
        impares_A = ListaGenerica() 
        pares_A = ListaGenerica()   
        impares_B = ListaGenerica() 
        pares_B = ListaGenerica()   
        pivote_card: Union[Carta, None] = None

        # Paso 2: Separar en subgrupos según la lógica de posición 1-basada del usuario
        for current_idx_lg in range(temp_original_deck_lg.size): # Iterar por los índices 0-basados de temp_original_deck_lg
            posicion = current_idx_lg + 1 # Convertir a posición 1-basada para la lógica del usuario
            carta_a_procesar = temp_original_deck_lg.obtener_por_indice(current_idx_lg)
            if carta_a_procesar is None:
                print(f"DEBUG: Error: Carta en índice {current_idx_lg} es None durante la separación de Faro Shuffle.")
                return

            if posicion >= 1 and posicion <= 25: # Mitad A (original_index 0-24)
                if posicion % 2 == 1: # Posiciones impares de Mitad A (1, 3, ..., 25)
                    impares_A.agregar_final(carta_a_procesar)
                else: # Posiciones pares de Mitad A (2, 4, ..., 24)
                    pares_A.agregar_final(carta_a_procesar)
            elif posicion == 26: # Pivote (original_index 25)
                pivote_card = carta_a_procesar
            elif posicion >= 27 and posicion <= 51: # Mitad B (original_index 26-50)
                if posicion % 2 == 1: # Posiciones impares de Mitad B (27, 29, ..., 51)
                    impares_B.agregar_final(carta_a_procesar)
                else: # Posiciones pares de Mitad B (28, 30, ..., 50)
                    pares_B.agregar_final(carta_a_procesar)
        
        # Paso 3: Construir el nuevo mazo intercalando en una lista de Python
        new_ordered_cards_list = [] # Usamos una lista de Python para construir el orden final

        # Intercalado de impares_A y pares_B
        idx_imparesA = 0
        idx_paresB = 0
        while idx_imparesA < impares_A.size and idx_paresB < pares_B.size:
            new_ordered_cards_list.append(impares_A.obtener_por_indice(idx_imparesA))
            new_ordered_cards_list.append(pares_B.obtener_por_indice(idx_paresB))
            idx_imparesA += 1
            idx_paresB += 1
        
        # Añadir la carta restante de impares_A (si la hay, que debería ser 1)
        if idx_imparesA < impares_A.size:
            new_ordered_cards_list.append(impares_A.obtener_por_indice(idx_imparesA))

        # Añadir el pivote
        if pivote_card:
            new_ordered_cards_list.append(pivote_card)
        else:
            print("DEBUG: Advertencia: Pivote no encontrado para Faro Shuffle. Esto no debería ocurrir con un mazo de 51 cartas.")

        # Intercalado de impares_B y pares_A
        idx_imparesB = 0
        idx_paresA = 0
        while idx_imparesB < impares_B.size and idx_paresA < pares_A.size:
            new_ordered_cards_list.append(impares_B.obtener_por_indice(idx_imparesB))
            new_ordered_cards_list.append(pares_A.obtener_por_indice(idx_paresA))
            idx_imparesB += 1
            idx_paresA += 1

        # Añadir la carta restante de impares_B (si la hay, que debería ser 1)
        if idx_imparesB < impares_B.size:
            new_ordered_cards_list.append(impares_B.obtener_por_indice(idx_imparesB))
        
        # Paso 4: Insertar todas las cartas recopiladas en la lista enlazada circular self.mazo_reserva
        for card in new_ordered_cards_list:
            self.insertar(card) # Reconstruye la ListaCartas circular

        print(f"DEBUG: Mazo después de FARO_SHUFFLE (size: {self.size}): {self.get_display_string()}")


    def _insertar_nodo_existente(self, nodo_existente: NodoCarta):
        """
        Método auxiliar para insertar un NodoCarta que YA EXISTE en la lista simplemente enlazada.
        Es crucial reiniciar sus punteros internos antes de enlazarlo.
        """
        nodo_existente.siguiente = None # Limpiar punteros para evitar referencias cruzadas/incorrectas
        
        if not self.primero:
            self.primero = nodo_existente
            self.ultimo = nodo_existente
            self.ultimo.siguiente = self.primero # Circular
        else:
            self.ultimo.siguiente = nodo_existente
            nodo_existente.siguiente = self.primero # Circular
            self.ultimo = nodo_existente
        self.size += 1

    def pop_from_tail(self) -> Union[Carta, None]:
        if not self.primero:
            return None
        
        carta_extraida = self.ultimo.carta
        
        if self.size == 1:
            self.primero = None
            self.ultimo = None
        else:
            current = self.primero
            while current.siguiente != self.ultimo:
                current = current.siguiente
                if current is None: 
                    print("DEBUG: ERROR CRÍTICO: pop_from_tail encontró None durante la búsqueda del penúltimo nodo.")
                    return None
            
            new_last = current 
            new_last.siguiente = self.primero 
            self.ultimo = new_last 
        
        self.size -= 1
        print(f"DEBUG: Pop de cola: {carta_extraida}. Nuevo tamaño: {self.size}. Mazo: {self.get_display_string()}")
        return carta_extraida

    def pop_from_head(self) -> Union[Carta, None]:
        if not self.primero:
            return None
        
        carta_extraida = self.primero.carta
        
        if self.size == 1:
            self.primero = None
            self.ultimo = None
        else:
            self.primero = self.primero.siguiente 
            self.ultimo.siguiente = self.primero 
        
        self.size -= 1
        print(f"DEBUG: Pop de cabeza: {carta_extraida}. Nuevo tamaño: {self.size}. Mazo: {self.get_display_string()}")
        return carta_extraida

# Custom Generic Node - Reemplazo de nodos para listas nativas de Python (ej. para jugadores, nombres, shuffles)
# Se mantiene doblemente enlazado para ListaGenerica, ya que la restricción es para ListaCartas.
class NodoGenerico:
    def __init__(self, data):
        self.data = data
        self.siguiente = None
        self.anterior = None 

# Custom Generic Doubly Linked List - Reemplazo de listas nativas de Python
# Se mantiene doblemente enlazada para ListaGenerica.
class ListaGenerica:
    def __init__(self):
        self.primero = None
        self.ultimo = None
        self.size = 0

    def agregar_final(self, data):
        nuevo_nodo = NodoGenerico(data)
        if not self.primero:
            self.primero = nuevo_nodo
            self.ultimo = nuevo_nodo
        else:
            self.ultimo.siguiente = nuevo_nodo
            nuevo_nodo.anterior = self.ultimo
            self.ultimo = nuevo_nodo
        self.size += 1

    def obtener_por_indice(self, index: int):
        if index < 0 or index >= self.size:
            return None 
        
        current = self.primero
        for i in range(index):
            if current is None: 
                return None
            current = current.siguiente
        return current.data

    def get_display_string(self) -> str:
        if self.size == 0:
            return "Lista vacía."
        
        current = self.primero
        items_str = ""
        count = 0
        while current and count < self.size: 
            items_str += str(current.data)
            current = current.siguiente
            count += 1
            if current and count < self.size: 
                items_str += " -> "
        return items_str

    def clear(self):
        self.primero = None
        self.ultimo = None
        self.size = 0

    def contains(self, item) -> bool:
        current = self.primero
        while current:
            if current.data is item: 
                return True
            if current.data == item: 
                return True
            current = current.siguiente
        return False

# Pila de Cartas (NodoPila y PilaCartas ya son estructuras customizadas, es una pila simplemente enlazada)
class NodoPila:
    def __init__(self, carta: Carta):
        self.carta = carta
        self.siguiente = None

class PilaCartas:
    def __init__(self):
        self.cima = None
        self.size = 0

    def apilar(self, carta: Carta):
        nuevo_nodo = NodoPila(carta)
        nuevo_nodo.siguiente = self.cima
        self.cima = nuevo_nodo
        self.size += 1

    def desapilar(self) -> Union[Carta, None]:
        if not self.cima:
            return None
        carta_extraida = self.cima.carta
        self.cima = self.cima.siguiente
        self.size -= 1
        return carta_extraida

    def ver_cima(self) -> Union[Carta, None]:
        if not self.cima:
            return None
        return self.cima.carta

    def esta_vacia(self) -> bool:
        return self.cima is None
    
    def get_display_string(self) -> str:
        if self.esta_vacia():
            return "Pila vacía."
        
        actual = self.cima
        cards_str_parts = ""
        first = True
        while actual:
            if not first:
                cards_str_parts += " -> "
            cards_str_parts += str(actual.carta)
            first = False
            actual = actual.siguiente
        return cards_str_parts

    def clear(self): 
        """
        Vacía la pila de cartas.
        """
        self.cima = None
        self.size = 0

class Jugador:
    def __init__(self, nombre: str):
        if not isinstance(nombre, str):
            print(f"DEBUG: ADVERTENCIA CRÍTICA - Jugador recibió un nombre no-string: {nombre}, tipo: {type(nombre)}. Forzando a string.")
            self.nombre = str(nombre) 
        else:
            self.nombre = nombre
        self.mano = PilaCartas()
        self.puntos = 0

    def __str__(self):
        return f"Jugador: {self.nombre} (Cartas: {self.mano.size})"

    def agregar_carta_a_mano(self, carta: Carta):
        self.mano.apilar(carta)

    def jugar_carta_de_mano(self, carta_en_mesa: Carta) -> Union[Carta, None]:
        """
        Intenta jugar la primera carta de la mano del jugador que coincida
        en número O en color con la carta en la mesa.
        Retorna la carta jugada o None si no hay compatible.
        """
        print(f"DEBUG: {self.nombre} intentando jugar una carta compatible con {carta_en_mesa}.")
        print(f"DEBUG: Mano antes de buscar: {self.mano.get_display_string()}")

        temp_hand_list = [] # Usamos una lista de Python para facilitar la búsqueda y eliminación
        while not self.mano.esta_vacia():
            card = self.mano.desapilar()
            if card:
                temp_hand_list.append(card)

        card_to_play_index = -1 

        # Itera a través de cada carta en la mano para encontrar la primera que cumpla la condición.
        for i, card_in_hand in enumerate(temp_hand_list):
            # Condición: ¿La carta coincide en número O en color?
            if card_in_hand.numero == carta_en_mesa.numero or \
                card_in_hand.color == carta_en_mesa.color:
                card_to_play_index = i
                break # Se encontró una carta compatible, se elige esta y se detiene la búsqueda.

        best_match_card = None
        if card_to_play_index != -1:
            best_match_card = temp_hand_list.pop(card_to_play_index)
            print(f"DEBUG: Se encontró y jugó carta compatible: {best_match_card}.")
        else:
            print("DEBUG: No se encontró carta compatible por número o color en la mano.")

        # Reconstruir la mano (pila) con las cartas restantes
        self.mano.clear() 
        # Apilar las cartas de nuevo en orden inverso para mantener el orden relativo original en la pila
        for card in reversed(temp_hand_list):
            self.mano.apilar(card)

        print(f"DEBUG: Mano después de jugar/buscar: {self.mano.get_display_string()}")
        return best_match_card

    def _can_play_card(self, carta_en_mesa: Carta) -> bool:
        """
        Verifica si el jugador tiene alguna carta compatible con la carta en mesa,
        buscando si alguna carta coincide en número O en color.
        Retorna True si encuentra una, False en caso contrario. No modifica la mano.
        """
        actual = self.mano.cima 
        while actual:
            card = actual.carta
            if card.numero == carta_en_mesa.numero or \
                card.color == carta_en_mesa.color:
                return True 
            actual = actual.siguiente
        return False

    def ver_mano(self) -> str:
        return f"Mano de {self.nombre}: {self.mano.get_display_string()}"

class PartidaConfigData:
    def __init__(self, name: str, shuffles_list: ListaGenerica):
        self.name = name
        self.shuffles_list = shuffles_list 

class ShuffleInfo:
    def __init__(self, type_str: str, x_val: Union[int, None]):
        self.type = type_str
        self.x = x_val

    def __str__(self):
        x_display = "None" if self.x is None else str(self.x)
        return f"{{'type': '{self.type}', 'x': {x_display}}}"

class Partida:
    def __init__(self):
        self.mazo_reserva: ListaCartas = ListaCartas()
        self.carta_en_mesa: Union[Carta, None] = None
        self.jugadores: ListaGenerica = ListaGenerica() 
        self._initial_player_names_template: ListaGenerica = ListaGenerica()
        self._initial_deck_template: ListaCartas = ListaCartas()
        self.current_player_index: int = 0
        self.shuffles_config: ListaGenerica = ListaGenerica()
        self._all_partidas_config_data: ListaGenerica = ListaGenerica() 
        self.partida_name: str = "Partida no definida" 

    def set_initial_deck_template(self, initial_cards: ListaCartas):
        self._initial_deck_template.clear() 
        if initial_cards.primero is None:
            print("DEBUG: Mazo inicial de plantilla vacío o nulo.")
            return

        current_node = initial_cards.primero
        count = 0
        max_iterations = initial_cards.size * 2 + 5 

        for _ in range(max_iterations): 
            if current_node is None:
                print(f"DEBUG: Advertencia: Nodo None en initial_cards durante set_initial_deck_template antes de {initial_cards.size} elementos.")
                break
            
            self._initial_deck_template.insertar(Carta(current_node.carta.color, current_node.carta.numero)) 
            current_node = current_node.siguiente
            count += 1
            
            if count == initial_cards.size and current_node == initial_cards.primero:
                break
            if current_node == initial_cards.primero and count >= initial_cards.size: 
                break

        print(f"DEBUG: Mazo inicial de plantilla cargado con {self._initial_deck_template.size} cartas (esperado: {initial_cards.size}).")


    def _get_copy_from_template_deck(self, template_deck: ListaCartas) -> ListaCartas:
        new_deck = ListaCartas()
        if not template_deck.primero:
            print("DEBUG: La plantilla del mazo inicial (pasada como argumento) está vacía. No se puede crear una copia.")
            return new_deck

        current_node = template_deck.primero
        count = 0
        max_iterations = template_deck.size * 2 + 5 
        
        for _ in range(max_iterations): 
            if current_node is None:
                print(f"DEBUG: Advertencia: Nodo None en template_deck durante _get_copy_from_template_deck antes de {template_deck.size} elementos.")
                break
            
            new_deck.insertar(Carta(current_node.carta.color, current_node.carta.numero)) 
            current_node = current_node.siguiente
            count += 1
            
            if count == template_deck.size and current_node == template_deck.primero:
                break
            if current_node == template_deck.primero and count >= template_deck.size: 
                break

        print(f"DEBUG: Copia del mazo inicial (desde plantilla externa) creada con {new_deck.size} cartas (esperado: {template_deck.size}).")
        return new_deck

    def set_player_names_template(self, player_names_list_generica: ListaGenerica):
        self._initial_player_names_template.clear() 
        current_name_node = player_names_list_generica.primero
        while current_name_node:
            self._initial_player_names_template.agregar_final(current_name_node.data)
            current_name_node = current_name_node.siguiente
        print(f"DEBUG: Nombres de jugadores plantilla establecidos: {self._initial_player_names_template.get_display_string()}")
    
    def get_player_names_template(self) -> ListaGenerica:
        copy_list = ListaGenerica()
        current_node = self._initial_player_names_template.primero
        while current_node:
            copy_list.agregar_final(current_node.data)
            current_node = current_node.siguiente
        return copy_list


    def reset_game_state(self, 
                        partida_name: str, 
                        shuffles_config: ListaGenerica, 
                        initial_deck_template: ListaCartas, 
                        player_names_template: ListaGenerica): 
        print(f"DEBUG: Reseteando estado de juego para partida '{partida_name}'.")
        self.partida_name = partida_name
        
        self.mazo_reserva = self._get_copy_from_template_deck(initial_deck_template)
        print(f"DEBUG: Mazo de reserva después de copiar plantilla: {self.mazo_reserva.get_display_string()}")
        
        self.jugadores.clear() 
        current_name_node = player_names_template.primero
        while current_name_node:
            self.jugadores.agregar_final(Jugador(current_name_node.data))
            current_name_node = current_name_node.siguiente
        
        player_names_debug_list = ListaGenerica()
        current_player_node = self.jugadores.primero
        while current_player_node:
            player_names_debug_list.agregar_final(current_player_node.data.nombre)
            current_player_node = current_player_node.siguiente
        print(f"DEBUG: Jugadores inicializados: {player_names_debug_list.get_display_string()}")

        self.carta_en_mesa = None
        self.current_player_index = 0
        
        self.shuffles_config.clear() 
        current_shuffle_node = shuffles_config.primero
        while current_shuffle_node:
            self.shuffles_config.agregar_final(current_shuffle_node.data)
            current_shuffle_node = current_shuffle_node.siguiente
        
        print(f"DEBUG: Configuración de shuffles para esta partida: {self.shuffles_config.get_display_string()}")


    def apply_shuffles(self, log_callback=None):
        if self.mazo_reserva.size == 0:
            if log_callback:
                log_callback("Error: No hay mazo de reserva para aplicar shuffles o está vacío.")
            print("DEBUG: Mazo de reserva vacío para shuffles.")
            return

        if self.shuffles_config.size == 0:
            if log_callback:
                log_callback("No hay shuffles definidos para aplicar en esta partida.")
            print("DEBUG: No hay shuffles definidos.")
            return

        print("DEBUG: Iniciando aplicación de shuffles...")
        current_shuffle_info_node = self.shuffles_config.primero
        while current_shuffle_info_node:
            shuffle_info = current_shuffle_info_node.data
            shuffle_type = shuffle_info.type
            x_value = shuffle_info.x

            if shuffle_type == "RIGHT":
                if log_callback:
                    log_callback(f"Aplicando RIGHT_SHUFFLE (x={x_value})...")
                print(f"DEBUG: Aplicando RIGHT_SHUFFLE (x={x_value})...")
                self.mazo_reserva.shuffle_right(x_value)
            elif shuffle_type == "HALF_SHUFFLE":
                if log_callback:
                    log_callback("Aplicando HALF_SHUFFLE...")
                print("DEBUG: Aplicando HALF_SHUFFLE...")
                self.mazo_reserva.half_shuffle()
            elif shuffle_type == "FARO_SHUFFLE":
                if log_callback:
                    log_callback("Aplicando FARO_SHUFFLE...")
                print("DEBUG: Aplicando FARO_SHUFFLE...")
                self.mazo_reserva.faro_shuffle()
            else:
                if log_callback:
                    log_callback(f"Tipo de shuffle desconocido: {shuffle_type}")
                print(f"DEBUG: Tipo de shuffle desconocido: {shuffle_type}")

            if log_callback:
                log_callback("Mazo después del shuffle:")
                log_callback(self.mazo_reserva.get_display_string())
            print(f"DEBUG: Mazo después del shuffle: {self.mazo_reserva.get_display_string()}")

            current_shuffle_info_node = current_shuffle_info_node.siguiente
        print("DEBUG: Todos los shuffles aplicados.")


    def deal_initial_cards(self, log_callback=None):
        """
        Reparte las cartas iniciales a los jugadores en bloques consecutivos de 7 cartas desde la cola.
        La primera carta en mesa se coloca de la mano del primer jugador.
        Luego, el turno avanza al siguiente jugador.
        """
        if log_callback:
            log_callback("Repartiendo 7 cartas a cada jugador en bloques consecutivos...")
        print("DEBUG: Iniciando reparto de cartas iniciales (consecutivo por jugador).")

        cards_to_deal_per_player = 7

        current_player_node = self.jugadores.primero
        while current_player_node:
            player: Jugador = current_player_node.data
            print(f"DEBUG: Repartiendo {cards_to_deal_per_player} cartas a {player.nombre} (consecutivamente desde la cola)...")

            for i in range(cards_to_deal_per_player):
                card = self.mazo_reserva.pop_from_tail()
                if card:
                    player.agregar_carta_a_mano(card)
                    print(f"DEBUG: {player.nombre} recibió carta {card}.")
                else:
                    if log_callback:
                        log_callback(f"Advertencia: Mazo vacío. {player.nombre} no recibió sus {cards_to_deal_per_player - i} cartas restantes.")
                    print(f"DEBUG: Advertencia: Mazo vacío. {player.nombre} no recibió sus {cards_to_deal_per_player - i} cartas restantes.")
                    break

            if log_callback:
                log_callback(f"Mano de {player.nombre}: {player.mano.get_display_string()}")
            print(f"DEBUG: Mano final de {player.nombre} después de reparto: {player.mano.get_display_string()}")
            current_player_node = current_player_node.siguiente

        # La primera carta en mesa es de la mano del primer jugador
        first_player: Jugador = self.jugadores.obtener_por_indice(0)
        if first_player and not first_player.mano.esta_vacia():
            # Desapilar la primera carta de la mano del primer jugador para ponerla en la mesa
            self.carta_en_mesa = first_player.mano.desapilar()
            if self.carta_en_mesa:
                if log_callback:
                    log_callback(f"Primera carta en mesa (del jugador {first_player.nombre}): {self.carta_en_mesa}")
                print(f"DEBUG: Primera carta colocada en mesa (del jugador {first_player.nombre}): {self.carta_en_mesa}")
            else:
                if log_callback:
                    log_callback(f"Advertencia: La mano de {first_player.nombre} se vació inesperadamente al intentar poner la primera carta en mesa.")
                print(f"DEBUG: Advertencia: Mano de {first_player.nombre} vacía al colocar carta en mesa.")
        else:
            if log_callback:
                log_callback("Error: No se pudo colocar la primera carta en la mesa (el primer jugador no tiene cartas o no existe).")
            print("DEBUG: ERROR: No se pudo colocar la primera carta en mesa desde el primer jugador.")
        
        # Después de que el primer jugador pone la carta inicial, el turno pasa al siguiente
        self.current_player_index = (self.current_player_index + 1) % self.jugadores.size
        next_player_for_first_turn: Jugador = self.jugadores.obtener_por_indice(self.current_player_index)
        if next_player_for_first_turn and log_callback:
            log_callback(f"El primer turno de juego es para: {next_player_for_first_turn.nombre}")
        print(f"DEBUG: Después de colocar la primera carta, el turno inicial de juego es para: {next_player_for_first_turn.nombre}")


    def get_mazo_display_string(self) -> str:
        return self.mazo_reserva.get_display_string()

    def get_card_on_table_for_display(self) -> Union[Carta, None]:
        return self.carta_en_mesa

    def get_players_for_display(self) -> ListaGenerica:
        return self.jugadores

    def play_turn(self, log_callback=None) -> bool:
        if self.jugadores.size == 0: # No hay jugadores, la partida no puede continuar
            if log_callback:
                log_callback("Partida terminada: No hay jugadores.")
            return False

        current_player: Jugador = self.jugadores.obtener_por_indice(self.current_player_index)
        if current_player is None:
            if log_callback:
                log_callback("Error: Jugador actual no encontrado.")
            return False

        if log_callback:
            log_callback(f"\nTurno de {current_player.nombre}. Carta en mesa: {self.carta_en_mesa}")
            log_callback(f"Mano de {current_player.nombre}: {current_player.mano.get_display_string()}")

        card_played_this_turn = None 
        
        # 1. Intento inicial de jugar una carta de la mano actual
        played_card_initial_attempt = current_player.jugar_carta_de_mano(self.carta_en_mesa)

        if played_card_initial_attempt:
            # El jugador pudo jugar una carta desde el principio
            card_played_this_turn = played_card_initial_attempt
            if log_callback:
                log_callback(f"{current_player.nombre} jugó: {card_played_this_turn}")
            print(f"DEBUG: {current_player.nombre} jugó: {card_played_this_turn}. Mano restante: {current_player.mano.get_display_string()}")
        else:
            # 2. El jugador no pudo jugar inicialmente, debe robar
            if self.mazo_reserva.size > 0: 
                card_drawn = self.mazo_reserva.pop_from_tail() 
                if card_drawn:
                    current_player.agregar_carta_a_mano(card_drawn)
                    if log_callback:
                        log_callback(f"{current_player.nombre} no pudo jugar y robó: {card_drawn}")
                    print(f"DEBUG: {current_player.nombre} robó carta: {card_drawn}. Nueva mano: {current_player.mano.get_display_string()}")

                    # 3. Después de robar, intentar jugar de nuevo con la mano actualizada
                    played_card_after_draw = current_player.jugar_carta_de_mano(self.carta_en_mesa)
                    if played_card_after_draw:
                        card_played_this_turn = played_card_after_draw
                        if log_callback:
                            log_callback(f"{current_player.nombre} robó y luego jugó: {card_played_this_turn}")
                        print(f"DEBUG: {current_player.nombre} robó y luego jugó: {card_played_this_turn}. Mano restante: {current_player.mano.get_display_string()}")
                    else:
                        # Robó, pero aún no pudo jugar. El turno finaliza aquí sin jugar carta.
                        if log_callback:
                            log_callback(f"{current_player.nombre} robó, pero aún no pudo jugar. Pasa turno.")
                        print(f"DEBUG: {current_player.nombre} robó, pero aún no pudo jugar. Pasa turno.")
                else: 
                    if log_callback:
                        log_callback(f"Advertencia: Mazo de reserva vacío al intentar robar. {current_player.nombre} pasa turno.")
                    print(f"DEBUG: Advertencia: Mazo de reserva vacío al intentar robar.")
            else:
                if log_callback:
                    log_callback(f"{current_player.nombre} no pudo jugar y el mazo de reserva está vacío. Pasa turno.")
                print(f"DEBUG: Mazo de reserva vacío. {current_player.nombre} pasa turno.")

        # Actualizar la carta en mesa si se jugó una carta en este turno
        if card_played_this_turn:
            self.carta_en_mesa = card_played_this_turn

        # Verificar condición de victoria (solo si se jugó una carta y la mano está vacía)
        if card_played_this_turn and current_player.mano.esta_vacia():
            if log_callback:
                log_callback(f"¡{current_player.nombre} se ha quedado sin cartas! ¡{current_player.nombre} es el ganador!")
            print(f"DEBUG: ¡{current_player.nombre} ha ganado!")
            return False 

        # Verificar si la partida se estanca (mazo vacío Y ningún jugador puede hacer un movimiento)
        if self.mazo_reserva.size == 0 and not card_played_this_turn:
            all_players_cannot_play = True
            for i in range(self.jugadores.size):
                player_to_check: Jugador = self.jugadores.obtener_por_indice(i)
                if player_to_check and self.carta_en_mesa and player_to_check._can_play_card(self.carta_en_mesa):
                    all_players_cannot_play = False
                    break
            
            if all_players_cannot_play:
                if log_callback:
                    log_callback("El mazo de reserva está vacío y ningún jugador puede hacer un movimiento. La partida termina en empate.")
                print("DEBUG: Mazo de reserva vacío y ningún jugador puede moverse. Fin de la partida (empate).")
                return False

        # Avanzar al siguiente jugador.
        self.current_player_index = (self.current_player_index + 1) % self.jugadores.size
        next_player: Jugador = self.jugadores.obtener_por_indice(self.current_player_index)
        if next_player and log_callback:
            log_callback(f"Siguiente turno para: {next_player.nombre}")
        
        return True 