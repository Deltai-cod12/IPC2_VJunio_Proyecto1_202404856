from typing import Union, TYPE_CHECKING
import os
import subprocess # Necesario para llamar a dot (Graphviz)
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
    """Devuelve el nombre del color en español para un codigo hexadecimal dado."""
    return COLOR_NAMES_MAP.get(hex_code, hex_code) 

def generate_game_graph(
    historial_cartas_mesa: 'PilaCartasMesa', # Nuevo parámetro: la pila de cartas en la mesa
    mazo_reserva: 'ListaCartas',
    jugadores: 'ListaGenerica', 
    partida_name: str = "Reporte", # Añadido para el nombre del archivo
    output_dir: str = "Reportes"
) -> Union[str, None]: # Retorna la ruta del archivo generado o None
    
    dot_content = []
    dot_content.append('digraph ReporteMazo {')
    dot_content.append('  rankdir=LR;') # Orientación de izquierda a derecha
    dot_content.append('  splines=ortho;') # Líneas ortogonales para los bordes
    dot_content.append('  node [shape=box, style="filled", fontcolor=white];')
    dot_content.append('  bgcolor=lightgray;')
    dot_content.append('  graph [pad="0.5", nodesep="0.5", ranksep="0.75"];') 
    dot_content.append('  compound=true;') # Permite los bordes entre clústeres

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Area de juego - Modificado para trabajar con PilaCartasMesa
    dot_content.append('  subgraph cluster_area_juego {')
    dot_content.append('    label="Historial de Cartas en Mesa";') # Etiqueta más descriptiva
    dot_content.append('    color=darkslategray;')
    dot_content.append('    fillcolor="gray";')
    dot_content.append('    style="filled";')

    if not historial_cartas_mesa.esta_vacia():
        cards_in_pile_temp = []
        current_node_in_pile = historial_cartas_mesa.cima  # CORRECCIÓN AQUÍ: usar 'cima', no '_top'
        while current_node_in_pile:
            cards_in_pile_temp.append(current_node_in_pile.carta)  # CORRECCIÓN AQUÍ: usar 'carta', no 'data'
            current_node_in_pile = current_node_in_pile.siguiente 

        # Invierte la lista para obtener el orden de la carta más antigua a la más reciente (de izquierda a derecha en el grafo LR)
        cards_in_pile_display_order = list(reversed(cards_in_pile_temp))

        prev_node_name = None
        for i, card in enumerate(cards_in_pile_display_order):
            card_id = f"mesa_card_{i}"
            card_label_base = f"{card.numero} ({get_color_name(card.color)})"
            
            node_label = card_label_base
            node_fontcolor = "white"
            node_shape = "box"
            node_peripheries = 1

            if i == len(cards_in_pile_display_order) - 1: # Es la carta más reciente (la que está actualmente en la mesa)
                node_label = f"Mesa: {card_label_base} (Actual)"
                node_fontcolor = "black" # Cambia el color del texto para la carta actual
                node_peripheries = 2 # Borde doble para la carta actual
            
            dot_content.append(f'    {card_id} [label="{node_label}", fillcolor="{card.color}", fontcolor="{node_fontcolor}", shape="{node_shape}", peripheries="{node_peripheries}"];')

            if prev_node_name:
                # Enlaza la carta anterior (más antigua) con la actual (más reciente)
                dot_content.append(f'    {prev_node_name} -> {card_id} [style="bold", color="black"];')
            prev_node_name = card_id

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

    node_ids_mazo = []
    
    if mazo_reserva.primero is not None and mazo_reserva.size > 0:
        current_node_mazo: 'NodoCarta' = mazo_reserva.primero
        visited_nodes_addresses_mazo = set() 
        
        print(f"DEBUG_GRAPH: Processing Mazo de Reserva. Reported size: {mazo_reserva.size}. First node card: {current_node_mazo.carta} (ID: {id(current_node_mazo)})")

        for i in range(mazo_reserva.size):
            if current_node_mazo is None:
                print(f"DEBUG_GRAPH: WARNING: current_node_mazo is None unexpectedly before processing {mazo_reserva.size} cards (index {i}). Breaking loop.")
                break
            if id(current_node_mazo) in visited_nodes_addresses_mazo:
                print(f"DEBUG_GRAPH: WARNING: Cycle detected (node already visited) in mazo_reserva at index {i}. Breaking loop to avoid infinite loop.")
                break

            card = current_node_mazo.carta
            # Usar una combinacion de indice y ID de objeto para asegurar unicidad del nodo DOT
            node_id = f"mazo_node_{i}_{id(current_node_mazo)}" 
            card_label = f"{card.numero} ({get_color_name(card.color)})"
            dot_content.append(f'    {node_id} [label="{card_label}", fillcolor="{card.color}"];')
            node_ids_mazo.append(node_id)
            visited_nodes_addresses_mazo.add(id(current_node_mazo))
            current_node_mazo = current_node_mazo.siguiente

        print(f"DEBUG_GRAPH: Mazo de Reserva nodes collected: {len(node_ids_mazo)}. Sample IDs: {node_ids_mazo[:5]}...")

        # Conexiones secuenciales dentro del mazo
        if len(node_ids_mazo) > 1:
            for i in range(len(node_ids_mazo) - 1):
                dot_content.append(f'    {node_ids_mazo[i]} -> {node_ids_mazo[i+1]};')
        else:
            print("DEBUG_GRAPH: Skipping sequential connections for Mazo de Reserva (0 or 1 node found).")

        # Conexion circular del mazo
        if len(node_ids_mazo) > 1 and \
            mazo_reserva.ultimo is not None and mazo_reserva.primero is not None and \
            mazo_reserva.ultimo.siguiente == mazo_reserva.primero:
            dot_content.append(f'    {node_ids_mazo[-1]} -> {node_ids_mazo[0]} [dir=forward, style=dashed, arrowhead=normal, color=darkgrey];')
            print("DEBUG_GRAPH: Added circular connection for Mazo de Reserva.")
        else:
            print("DEBUG_GRAPH: Skipping circular connection for Mazo de Reserva (not enough nodes or not truly circular at end).")

    else:
        dot_content.append('    mazo_vacio [label="Mazo Vacio", style="dashed", color="darkslategray", fontcolor="black"];')
        print("DEBUG_GRAPH: Mazo de Reserva is empty.")
    dot_content.append('  }')


    # Mazo de los Jugadores
    current_player_node_lg: 'NodoGenerico' = jugadores.primero
    player_index = 0
    while current_player_node_lg:
        player: 'Jugador' = current_player_node_lg.data
        
        dot_content.append(f'  subgraph cluster_jugador_{player_index} {{')
        dot_content.append(f'    label="Mano de {player.nombre}";')
        dot_content.append('    color=darkslategray;')
        dot_content.append('    fillcolor="gray";')
        dot_content.append('    style="filled";')

        current_card_node_pila: 'NodoPila' = player.mano.cima 
        node_ids_mano = [] 
        card_in_hand_index = 0

        if current_card_node_pila:
            while current_card_node_pila:
                card = current_card_node_pila.carta
                
                node_id = f"jugador_{player_index}_card_{card_in_hand_index}_{id(current_card_node_pila)}" 
                card_label = f"{card.numero} ({get_color_name(card.color)})"
                dot_content.append(f'    {node_id} [label="{card_label}", fillcolor="{card.color}"];')
                node_ids_mano.append(node_id) 
                
                current_card_node_pila = current_card_node_pila.siguiente
                card_in_hand_index += 1

            
            if len(node_ids_mano) > 1:
                for i in range(len(node_ids_mano) - 1):
                    dot_content.append(f'    {node_ids_mano[i]} -> {node_ids_mano[i+1]};')
            else:
                print(f"DEBUG_GRAPH: Skipping sequential connections for {player.nombre}'s hand (0 or 1 card).")

        else:
            dot_content.append(f'    mano_vacia_{player_index} [label="Mano Vacia", style="dashed", color="darkslategray", fontcolor="black"];')
            print(f"DEBUG_GRAPH: {player.nombre}'s hand is empty.")
        
        dot_content.append('  }')
        
        current_player_node_lg = current_player_node_lg.siguiente
        player_index += 1

    dot_content.append('}')

    # Generar archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"estado_juego_{timestamp}"
    
    dot_filepath = os.path.join(output_dir, f"{base_filename}.dot")
    # PDF
    pdf_filepath = os.path.join(output_dir, f"{base_filename}.pdf") 
    # PNG
    png_filepath = os.path.join(output_dir, f"{base_filename}.png") 

    try:
        # Guardar el contenido DOT en un archivo .dot
        with open(dot_filepath, "w") as f:
            f.write("\n".join(dot_content))
        print(f"DEBUG_GRAPH: Archivo DOT generado en: {dot_filepath}")

        result_png = subprocess.run(['dot', '-Tpng', dot_filepath, '-o', png_filepath], check=True, capture_output=True)
        print(f"DEBUG_GRAPH: Grafico PNG generado en: {png_filepath}")
        if result_png.stdout:
            print(f"DEBUG_GRAPH: dot (PNG) stdout: {result_png.stdout.decode()}")
        if result_png.stderr:
            print(f"DEBUG_GRAPH: dot (PNG) stderr: {result_png.stderr.decode()}")
        
        result_pdf = subprocess.run(['dot', '-Tpdf', dot_filepath, '-o', pdf_filepath], check=True, capture_output=True)
        print(f"DEBUG_GRAPH: Reporte PDF generado en: {pdf_filepath}")
        if result_pdf.stdout:
            print(f"DEBUG_GRAPH: dot (PDF) stdout: {result_pdf.stdout.decode()}")
        if result_pdf.stderr:
            print(f"DEBUG_GRAPH: dot (PDF) stderr: {result_pdf.stderr.decode()}")

    except FileNotFoundError:
        print(f"ERROR_GRAPH: El comando 'dot' de Graphviz no fue encontrado.")
        print("Asegurate de que Graphviz este instalado y su directorio bin este en tu PATH del sistema.")
    except subprocess.CalledProcessError as e:
        print(f"ERROR_GRAPH: Error al ejecutar el comando 'dot' de Graphviz (codigo de salida {e.returncode}).")
        print(f"dot stdout: {e.stdout.decode() if e.stdout else 'N/A'}")
        print(f"dot stderr: {e.stderr.decode() if e.stderr else 'N/A'}")
    except Exception as e:
        print(f"ERROR_GRAPH: No se pudo generar el grafico Graphviz: {e}")