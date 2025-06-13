import xml.etree.ElementTree as ET
from Utilidades.game_loader import GameLoader
from Utilidades.game_saver import save_game_log_to_xml
from Utilidades.graph_generator import generate_game_graph 
from Modelo.partida import (
    Partida, ListaGenerica, PartidaConfigData, ShuffleInfo,
    Jugador, Carta, PilaCartasMesa, PilaStr
)
from typing import Union, Callable


class PartidaController:
    def __init__(self, view):
        self.view = view
        self.game_loader = GameLoader()
        self.game_template_partida: Union[Partida, None] = None
        self.current_partida: Union[Partida, None] = None
        self.game_running = False
        self.game_log_history: PilaStr = PilaStr()  # CAMBIO
        self.pila_historial_mesa: PilaCartasMesa = PilaCartasMesa()

    def _log_game_action(self, message: str):
        self.game_log_history.push(message)  # CAMBIO
        total_logs = len(self.game_log_history.obtener_como_lista())  # Obtener tamaño
        self.view.log_message(f"Paso {total_logs}: {message}")

    def load_game_configurations(self, filepath: str):
        self.view.log_message(f"Cargando configuraciones desde: {filepath}")
        self.game_template_partida = self.game_loader.load_from_xml(filepath, self.view.log_message)
        
        if self.game_template_partida:
            available_partida_names_list = ListaGenerica()  # CAMBIO

            current_partida_config_node = self.game_template_partida._all_partidas_config_data.primero
            while current_partida_config_node:
                partida_config_obj: PartidaConfigData = current_partida_config_node.data 
                available_partida_names_list.agregar_final(partida_config_obj.name)
                current_partida_config_node = current_partida_config_node.siguiente
            
            # Convertir ListaGenerica a lista nativa para mostrar en la interfaz
            self.view.display_available_partidas(available_partida_names_list.obtener_como_lista())  # CAMBIO
            self.view.log_message("Configuraciones cargadas exitosamente. Seleccione una partida.")
            self.view.enable_game_selection()
            self.view.clear_game_over_message()
        else:
            self.view.log_message("Fallo al cargar las configuraciones.")
            self.view.disable_game_controls()

    def select_partida(self, partida_name: str):
        if not self.game_template_partida:
            self.view.log_message("Error: No hay configuraciones cargadas.")
            self.view.disable_game_controls()
            return

        selected_partida_config: Union[PartidaConfigData, None] = None
        current_node = self.game_template_partida._all_partidas_config_data.primero
        while current_node:
            partida_config_obj: PartidaConfigData = current_node.data
            if partida_config_obj.name == partida_name:
                selected_partida_config = partida_config_obj
                break 
            current_node = current_node.siguiente

        if selected_partida_config:
            self.current_partida = Partida()
            self.current_partida.reset_game_state(
                partida_name,
                selected_partida_config.shuffles_list,  
                self.game_template_partida._initial_deck_template, 
                self.game_template_partida.get_player_names_template() 
            )
            self.view.log_message(f"Partida seleccionada: '{partida_name}'")
            self.game_log_history.clear() 
            self.start_game()
            self.game_running = True
            self.view.enable_play_button()
            self.view.clear_game_over_message()
        else:
            self.view.log_message(f"Error: Partida '{partida_name}' no encontrada.")
            self.view.disable_play_button()

    def start_game(self):
        if not self.current_partida:
            self.view.log_message("Error: No hay partida seleccionada para iniciar.")
            self.view.disable_game_controls()
            return

        self.view.log_message("\n--- Iniciando Simulacion de Partida ---")
        self.view.log_message("Aplicando shuffles...")
        self.current_partida.apply_shuffles(lambda msg: self.view.log_message(msg)) 
        self.view.log_message("Reparto inicial de cartas...")
        self.current_partida.deal_initial_cards(self._log_game_action) 
        self.view.log_message("Reparto inicial completado.")
        
        self.update_game_display() 

        current_player_obj: Union[Jugador, None] = self.current_partida.jugadores.obtener_por_indice(self.current_partida.current_player_index)
        if current_player_obj:
            self.view.log_message(f"Partida lista. Turno de: {current_player_obj.nombre}")
        else:
            self.view.log_message("Error: No se pudo determinar el primer jugador.")

    def play_turn(self):
        if not self.game_running or not self.current_partida:
            self.view.log_message("El juego no esta activo.")
            return

        game_continues = self.current_partida.play_turn(self._log_game_action)
        self.update_game_display() 

        if not game_continues:
            self.game_running = False 
            final_message_ui = ""
            final_message_xml = ""
            winner_info = "Empate" 
            
            if self.current_partida.jugadores.size > 0:
                current_player_node = self.current_partida.jugadores.primero
                while current_player_node:
                    player: Jugador = current_player_node.data
                    if player.mano.esta_vacia():
                        winner_info = player.nombre
                        final_message_ui = f"¡{player.nombre} ha ganado la partida!"
                        final_message_xml = f"El jugador {player.nombre} ha ganado"
                        break 
                    current_player_node = current_player_node.siguiente
            
            if not winner_info or winner_info == "Empate":
                final_message_ui = "La partida termina en empate."
                final_message_xml = "La partida termina en empate." 
                winner_info = "Empate"

            self._log_game_action(final_message_xml) 
            self.view.on_game_end(final_message_ui) 
            self.view.log_message("\n--- ¡Fin de la Simulacion de Partida! ---")
            save_game_log_to_xml(winner_info, self.game_log_history, output_dir="Utilidades") 
            self.game_log_history.clear() 

    def update_game_display(self):
        if self.current_partida:
            current_player_name = "N/A"
            current_player_obj: Union[Jugador, None] = self.current_partida.jugadores.obtener_por_indice(self.current_partida.current_player_index)
            if current_player_obj:
                current_player_name = current_player_obj.nombre
            
            card_on_table: Union[Carta, None] = self.current_partida.get_card_on_table_for_display()
            card_on_table_str = str(card_on_table) if card_on_table else "N/A"
            mazo_reserva_info = self.current_partida.get_mazo_display_string()

            self.view.update_game_state_display(
                current_player_name=current_player_name,
                card_on_table=card_on_table_str,
                mazo_reserva_info=mazo_reserva_info
            )
            
            players_hands_display = ListaGenerica()  # CAMBIO

            current_player_node = self.current_partida.jugadores.primero
            while current_player_node:
                player_obj: 'Jugador' = current_player_node.data
                players_hands_display.agregar(
                    f"{player_obj.nombre}: {player_obj.mano.get_display_string()} (Puntos: {player_obj.puntos})"
                )
                current_player_node = current_player_node.siguiente

            # Pasamos a lista nativa solo al final para actualizar vista
            self.view.update_players_hands_display(players_hands_display.obtener_como_lista())  # CAMBIO

    def generate_game_graph_report(self):
        if not self.current_partida:
            self.view.log_message("Error: No hay partida activa para generar el grafico.")
            return

        self.view.log_message("Generando grafico del estado actual del juego...")

        historial_cartas_mesa = self.current_partida.pila_historial_mesa 
        mazo_reserva = self.current_partida.mazo_reserva
        jugadores_list_generica = self.current_partida.jugadores

        try:
            generate_game_graph(
                historial_cartas_mesa=historial_cartas_mesa,
                mazo_reserva=mazo_reserva,
                jugadores=jugadores_list_generica
            )
            self.view.log_message("Grafico generado exitosamente en la carpeta 'Reportes'.")
        except Exception as e:
            self.view.log_message(f"Error al generar el grafico: {e}. Asegurese de que Graphviz este instalado y en su PATH.")
