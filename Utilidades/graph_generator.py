from typing import Union, TYPE_CHECKING
import os
import subprocess
from datetime import datetime

if TYPE_CHECKING:
    from Modelo.partida import Carta, ListaCartas, Jugador, ListaGenerica, NodoCarta, NodoPila, NodoGenerico, PilaCartasMesa

COLOR_NAMES_MAP = {
    "#c72623": "Rojo",
    "#eFC12C": "Amarillo",
    "#15629b": "Azul",
    "#39843e": "Verde",
}

def get_color_name(hex_code: str) -> str:
    return COLOR_NAMES_MAP.get(hex_code, hex_code)

class AppendString:
    def __init__(self):
        self.content = ""

    def append(self, text: str):
        self.content += text + "\n"

    def get_content(self) -> str:
        return self.content

# Nodo simple para lista enlazada propia de IDs (strings)
class NodoID:
    def __init__(self, id_value: str):
        self.id_value = id_value
        self.siguiente = None

class ListaIDs:
    def __init__(self):
        self.primero = None
        self.ultimo = None

    def agregar(self, id_value: str):
        nuevo = NodoID(id_value)
        if self.primero is None:
            self.primero = nuevo
            self.ultimo = nuevo
        else:
            self.ultimo.siguiente = nuevo
            self.ultimo = nuevo

    def iterar(self):
        actual = self.primero
        while actual:
            yield actual.id_value
            actual = actual.siguiente

def invertir_pila_cartas(cima) -> 'NodoPila':
    # Invierte la pila simplemente retornando una nueva pila enlazada inversa
    # Implementamos una pila enlazada propia sin listas nativas:
    nuevo_cima = None
    actual = cima
    while actual:
        nodo_nuevo = NodoPila()
        nodo_nuevo.carta = actual.carta
        nodo_nuevo.siguiente = nuevo_cima
        nuevo_cima = nodo_nuevo
        actual = actual.siguiente
    return nuevo_cima

def generate_game_graph(
    historial_cartas_mesa: 'PilaCartasMesa',
    mazo_reserva: 'ListaCartas',
    jugadores: 'ListaGenerica', 
    partida_name: str = "Reporte",
    output_dir: str = "Reportes"
) -> Union[str, None]:

    dot_content = AppendString()

    dot_content.append('digraph ReporteMazo {')
    dot_content.append('  rankdir=LR;')
    dot_content.append('  splines=ortho;')
    dot_content.append('  node [shape=box, style="filled", fontcolor=white];')
    dot_content.append('  bgcolor=lightgray;')
    dot_content.append('  graph [pad="0.5", nodesep="0.5", ranksep="0.75"];')
    dot_content.append('  compound=true;')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Área de juego
    dot_content.append('  subgraph cluster_area_juego {')
    dot_content.append('    label="Historial de Cartas en Mesa";')
    dot_content.append('    color=darkslategray;')
    dot_content.append('    fillcolor="gray";')
    dot_content.append('    style="filled";')

    if not historial_cartas_mesa.esta_vacia():
        # Invertir pila sin listas nativas
        pila_invertida = invertir_pila_cartas(historial_cartas_mesa.cima)

        prev_node_name = None
        index = 0
        actual = pila_invertida
        while actual:
            card = actual.carta
            card_id = f"mesa_card_{index}"
            card_label_base = f"{card.numero} ({get_color_name(card.color)})"

            node_label = card_label_base
            node_fontcolor = "white"
            node_shape = "box"
            node_peripheries = 1

            # Última carta (top original) es la primera en la pila invertida
            if actual.siguiente is None:
                node_label = f"Mesa: {card_label_base} (Actual)"
                node_fontcolor = "black"
                node_peripheries = 2

            dot_content.append(f'    {card_id} [label="{node_label}", fillcolor="{card.color}", fontcolor="{node_fontcolor}", shape="{node_shape}", peripheries="{node_peripheries}"];')

            if prev_node_name:
                dot_content.append(f'    {prev_node_name} -> {card_id} [style="bold", color="black"];')
            prev_node_name = card_id

            actual = actual.siguiente
            index += 1
    else:
        dot_content.append('    mesa_vacia [label="Mesa Vacia", style="dashed", color="darkslategray", fontcolor="black"];')
    dot_content.append('  }')

    # Mazo reserva
    dot_content.append('  subgraph cluster_mazo_reserva {')
    dot_content.append('    label="Mazo de Reserva";')
    dot_content.append('    color=darkslategray;')
    dot_content.append('    fillcolor="gray";')
    dot_content.append('    style="filled";')
    dot_content.append('    rank="same";')

    node_ids_mazo = ListaIDs()

    if mazo_reserva.primero is not None and mazo_reserva.size > 0:
        current_node_mazo = mazo_reserva.primero
        nodos_visitados = set()
        i = 0

        # Recorremos tamaño pero sin usar set, hacemos conteo max
        # para evitar ciclos infinitos
        max_nodos = mazo_reserva.size

        while current_node_mazo is not None and i < max_nodos:
            card = current_node_mazo.carta
            node_id = f"mazo_node_{i}_{id(current_node_mazo)}"
            card_label = f"{card.numero} ({get_color_name(card.color)})"
            dot_content.append(f'    {node_id} [label="{card_label}", fillcolor="{card.color}"];')
            node_ids_mazo.agregar(node_id)

            current_node_mazo = current_node_mazo.siguiente
            i += 1

        # Unir nodos en la lista enlazada propia
        ids_iter = node_ids_mazo.primero
        while ids_iter is not None and ids_iter.siguiente is not None:
            dot_content.append(f'    {ids_iter.id_value} -> {ids_iter.siguiente.id_value};')
            ids_iter = ids_iter.siguiente

        # Si el mazo es circular, unir último al primero (checamos que ultimo.siguiente == primero)
        if mazo_reserva.ultimo is not None and mazo_reserva.primero is not None and mazo_reserva.ultimo.siguiente == mazo_reserva.primero:
            if node_ids_mazo.primero and node_ids_mazo.ultimo:
                dot_content.append(f'    {node_ids_mazo.ultimo.id_value} -> {node_ids_mazo.primero.id_value} [dir=forward, style=dashed, arrowhead=normal, color=darkgrey];')

    else:
        dot_content.append('    mazo_vacio [label="Mazo Vacio", style="dashed", color="darkslategray", fontcolor="black"];')
    dot_content.append('  }')

    # Mazo de los jugadores
    current_player_node_lg = jugadores.primero
    player_index = 0
    while current_player_node_lg:
        player = current_player_node_lg.data

        dot_content.append(f'  subgraph cluster_jugador_{player_index} {{')
        dot_content.append(f'    label="Mano de {player.nombre}";')
        dot_content.append('    color=darkslategray;')
        dot_content.append('    fillcolor="gray";')
        dot_content.append('    style="filled";')

        node_ids_mano = ListaIDs()
        current_card_node_pila = player.mano.cima
        card_in_hand_index = 0

        while current_card_node_pila:
            card = current_card_node_pila.carta
            node_id = f"jugador_{player_index}_card_{card_in_hand_index}_{id(current_card_node_pila)}"
            card_label = f"{card.numero} ({get_color_name(card.color)})"
            dot_content.append(f'    {node_id} [label="{card_label}", fillcolor="{card.color}"];')
            node_ids_mano.agregar(node_id)

            current_card_node_pila = current_card_node_pila.siguiente
            card_in_hand_index += 1

        if node_ids_mano.primero is None:
            dot_content.append(f'    mano_vacia_{player_index} [label="Mano Vacia", style="dashed", color="darkslategray", fontcolor="black"];')
        else:
            ids_iter = node_ids_mano.primero
            while ids_iter is not None and ids_iter.siguiente is not None:
                dot_content.append(f'    {ids_iter.id_value} -> {ids_iter.siguiente.id_value};')
                ids_iter = ids_iter.siguiente

        dot_content.append('  }')

        current_player_node_lg = current_player_node_lg.siguiente
        player_index += 1

    dot_content.append('}')

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"estado_juego_{timestamp}"

    dot_filepath = os.path.join(output_dir, f"{base_filename}.dot")
    pdf_filepath = os.path.join(output_dir, f"{base_filename}.pdf")
    png_filepath = os.path.join(output_dir, f"{base_filename}.png")

    try:
        with open(dot_filepath, "w") as f:
            f.write(dot_content.get_content())

        subprocess.run(['dot', '-Tpng', dot_filepath, '-o', png_filepath], check=True)
        subprocess.run(['dot', '-Tpdf', dot_filepath, '-o', pdf_filepath], check=True)

    except FileNotFoundError:
        print("ERROR_GRAPH: El comando 'dot' de Graphviz no fue encontrado. Asegurese que Graphviz esté instalado y en el PATH.")
    except subprocess.CalledProcessError as e:
        print(f"ERROR_GRAPH: Error ejecutando 'dot' (codigo {e.returncode}).")
    except Exception as e:
        print(f"ERROR_GRAPH: No se pudo generar el grafico: {e}")

    return pdf_filepath
