# Controlador/partida_controlador.py

import xml.etree.ElementTree as ET
from Utilidades.game_loader import GameLoader
from Modelo.partida import Partida, ListaGenerica, PartidaConfigData, ShuffleInfo, Jugador, Carta
from typing import Union, Callable # Importa Callable para type hinting

class PartidaController:
    def __init__(self, view):
        self.view = view
        self.game_loader = GameLoader()
        self.game_template_partida: Union[Partida, None] = None
        self.current_partida: Union[Partida, None] = None
        self.game_running = False
        self._game_step_counter = 0 # Inicializar el contador de pasos del juego

    def _log_game_action(self, message: str):
        """
        Función interna que envuelve el log_message de la vista
        para añadir el contador de pasos si es un mensaje de acción de turno.
        """
        # Los mensajes de setup o shuffles (que inician con '>') no necesitan el contador de paso.
        # Los mensajes de la primera carta en mesa tampoco.
        if message.startswith('>') or message.startswith('La carta inicial es'):
            self.view.log_message(message)
        else:
            # Para los mensajes de acción de turno, se añade el prefijo "Paso X:"
            self.view.log_message(f"Paso {self._game_step_counter}: {message}")


    def load_game_configurations(self, filepath: str):
        """
        Carga las configuraciones del juego desde un archivo XML y las prepara.
        Habilita la selección de partida en la vista si la carga es exitosa.
        """
        self.view.log_message(f"Cargando configuraciones del juego desde: {filepath}")
        self.game_template_partida = self.game_loader.load_from_xml(filepath, self.view.log_message)
        
        if self.game_template_partida:
            available_partida_names_native_list = []
            current_partida_config_node = self.game_template_partida._all_partidas_config_data.primero
            while current_partida_config_node:
                partida_config_obj: PartidaConfigData = current_partida_config_node.data 
                available_partida_names_native_list.append(partida_config_obj.name)
                current_partida_config_node = current_partida_config_node.siguiente
            
            self.view.display_available_partidas(available_partida_names_native_list)
            self.view.log_message("Configuraciones del juego cargadas exitosamente. Seleccione una partida para iniciar.")
            print("DEBUG: Configuraciones del juego cargadas exitosamente.")
            self.view.enable_game_selection()
            self.view.clear_game_over_message()
        else:
            self.view.log_message("Fallo al cargar las configuraciones del juego.")
            print("DEBUG: Fallo al cargar las configuraciones del juego.")
            self.view.disable_game_controls()

    def select_partida(self, partida_name: str):
        """
        Selecciona una partida específica por su nombre de las configuraciones cargadas
        y la inicializa para empezar a jugar.
        """
        if not self.game_template_partida:
            self.view.log_message("Error: No hay configuraciones de juego cargadas. Cargue un XML primero.")
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
            print(f"DEBUG: Partida seleccionada: '{partida_name}'")
            
            self.start_game()
            self.game_running = True
            self.view.enable_play_button()
            self.view.clear_game_over_message()
            # Inicializar el contador de pasos de juego para la nueva partida
            self._game_step_counter = 1 
        else:
            self.view.log_message(f"Error: Partida '{partida_name}' no encontrada en las configuraciones.")
            print(f"DEBUG: Error: Partida '{partida_name}' no encontrada.")
            self.view.disable_play_button()

    def start_game(self):
        """
        Inicia la partida actual: aplica los shuffles, reparte las cartas iniciales
        y actualiza el display inicial del juego.
        """
        if not self.current_partida:
            self.view.log_message("Error: No hay partida seleccionada o inicializada para iniciar.")
            self.view.disable_game_controls()
            return

        self.view.log_message("\n--- Iniciando Simulación de Partida ---")
        self.view.log_message("Aplicando shuffles al mazo...")
        # Pasa _log_game_action para los mensajes de shuffle (sin contador de paso)
        self.current_partida.apply_shuffles(self._log_game_action) 
        self.view.log_message("Shuffles aplicados.")

        self.view.log_message("Repartiendo cartas iniciales...")
        # Pasa _log_game_action para los mensajes de reparto (incluyendo el Paso 1)
        self.current_partida.deal_initial_cards(self._log_game_action) 
        self.view.log_message("Reparto inicial completado.")
        
        self.update_game_display() 

        current_player_obj: Union[Jugador, None] = self.current_partida.jugadores.obtener_por_indice(self.current_partida.current_player_index)
        if current_player_obj:
            self.view.log_message(f"Partida lista. Turno de: {current_player_obj.nombre}")
            print(f"DEBUG: Partida lista. Turno de: {current_player_obj.nombre}")
        else:
            self.view.log_message("Error: No se pudo determinar el primer jugador del turno.")
            print("DEBUG: Error: No se pudo determinar el primer jugador del turno.")
        
        # Después de que la carta inicial (Paso 1) ha sido colocada,
        # el próximo turno real de juego es el Paso 2.
        self._game_step_counter = 2 

    def play_turn(self):
        """
        Maneja la lógica para un solo turno de juego, incluyendo la verificación de fin de partida.
        """
        if not self.game_running or not self.current_partida:
            self.view.log_message("El juego no está activo o no se ha cargado/seleccionado correctamente.")
            return

        # Ejecutar el turno del modelo, pasando _log_game_action como callback
        game_continues = self.current_partida.play_turn(self._log_game_action)
        self.update_game_display() 

        if not game_continues:
            self.game_running = False 
            
            final_message = ""
            winner_found = False
            if self.current_partida.jugadores.size > 0:
                current_player_node = self.current_partida.jugadores.primero
                while current_player_node:
                    player: Jugador = current_player_node.data
                    if player.mano.esta_vacia():
                        final_message = f"¡{player.nombre} ha ganado la partida!"
                        winner_found = True
                        break 
                    current_player_node = current_player_node.siguiente
            
            if not winner_found:
                final_message = "La partida termina en empate (mazo vacío y sin movimientos)."
            
            self.view.on_game_end(final_message) 
            self.view.log_message("\n--- ¡Fin de la Simulación de Partida! ---")
            self.view.log_message(final_message)

        else:
            # Si el juego continúa, incrementar el contador de pasos para el siguiente turno
            self._game_step_counter += 1
            # El log del "Siguiente turno para" ya está gestionado por el modelo o la actualización de UI
            # No se necesita un log adicional aquí como "Avanzando al siguiente turno..."

    def update_game_display(self):
        """
        Actualiza la vista con el estado actual del juego.
        """
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
            
            players_hands_display_list = []
            current_player_node = self.current_partida.jugadores.primero
            for _ in range(self.current_partida.jugadores.size):
                if current_player_node:
                    player_obj: 'Jugador' = current_player_node.data
                    players_hands_display_list.append(f"{player_obj.nombre}: {player_obj.mano.get_display_string()} (Puntos: {player_obj.puntos})")
                    current_player_node = current_player_node.siguiente
                else:
                    break
            self.view.update_players_hands_display(players_hands_display_list)