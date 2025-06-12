# Vista/mazo_vista.py
import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext
from typing import Union, TYPE_CHECKING
import os
import re # ¡Nueva importación para expresiones regulares!

# Importaciones para el tipo de datos, solo para Type Hinting (no importa el objeto real en la vista)
if TYPE_CHECKING:
    from Controlador.partida_controlador import PartidaController
    from Modelo.partida import ListaCartas, Carta, Jugador, ListaGenerica

# Mapeo de códigos hexadecimales a nombres de colores en español para la VISTA
COLOR_NAMES_MAP = {
    "#c72623": "Rojo",
    "#eFC12C": "Amarillo",
    "#15629b": "Azul",
    "#39843e": "Verde",
}

class MazoView:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Card Clash: IPC2 Edition")
        self.controller: Union['PartidaController', None] = None

        self.setup_ui()
        self.disable_game_controls() # Deshabilitar controles al inicio hasta cargar XML

    def set_controller(self, controller: 'PartidaController'):
        self.controller = controller

    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Sección de Carga de Configuración
        config_frame = ttk.LabelFrame(main_frame, text="Configuración del Juego", padding="10")
        config_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        ttk.Button(config_frame, text="Cargar Configuraciones XML", command=self.load_xml_command).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.partida_selection_label = ttk.Label(config_frame, text="Seleccionar Partida:")
        self.partida_selection_label.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.partida_combobox = ttk.Combobox(config_frame, state="disabled") # Inicia deshabilitado
        self.partida_combobox.grid(row=0, column=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.partida_combobox.bind("<<ComboboxSelected>>", self.on_partida_selected)
        config_frame.columnconfigure(2, weight=1)

        # Sección de Estado del Mazo
        deck_frame = ttk.LabelFrame(main_frame, text="Mazo de Reserva", padding="10")
        deck_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.deck_display_label = ttk.Label(deck_frame, text="Mazo: Vacío", wraplength=700)
        self.deck_display_label.pack(fill=tk.BOTH, expand=True)

        # Sección de Estado de la Mesa y Turno
        game_state_frame = ttk.LabelFrame(main_frame, text="Estado del Juego", padding="10")
        game_state_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        game_state_frame.columnconfigure(0, weight=1)
        game_state_frame.columnconfigure(1, weight=1)
        game_state_frame.columnconfigure(2, weight=1)
        game_state_frame.columnconfigure(3, weight=1)

        ttk.Label(game_state_frame, text="Carta en Mesa:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.card_on_table_label = ttk.Label(game_state_frame, text="N/A", font=("Arial", 12, "bold"))
        self.card_on_table_label.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)

        ttk.Label(game_state_frame, text="Turno de:").grid(row=0, column=2, padx=5, pady=2, sticky=tk.W)
        self.current_player_label = ttk.Label(game_state_frame, text="N/A", font=("Arial", 12, "bold"))
        self.current_player_label.grid(row=0, column=3, padx=5, pady=2, sticky=tk.W)
        
        self.play_turn_button = ttk.Button(game_state_frame, text="Siguiente Turno", command=self.next_turn_command, state=tk.DISABLED) # Inicia deshabilitado
        self.play_turn_button.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky=(tk.W, tk.E))

        # Etiqueta para mensajes de fin de juego (mostrada en el centro, debajo de los controles de juego)
        self.game_over_label = ttk.Label(main_frame, text="", foreground="red", font=("Arial", 16, "bold"), anchor="center")
        self.game_over_label.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Sección de Manos de Jugadores (usando PanedWindow para redimensionar)
        # Se ha ajustado la fila para que esté debajo del game_over_label
        player_hands_pane = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)
        player_hands_pane.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(4, weight=2) # Darle más peso a las manos

        self.player_hand_labels = {}
        for i in range(4): # Crear 4 frames para los jugadores
            player_frame = ttk.LabelFrame(player_hands_pane, text=f"Jugador {i+1} Mano", padding="5")
            player_hands_pane.add(player_frame, weight=1) # Cada jugador frame ocupa el mismo espacio

            hand_label = ttk.Label(player_frame, text="Mano: Vacía", wraplength=680)
            hand_label.pack(fill=tk.BOTH, expand=True)
            self.player_hand_labels[f"player_{i}"] = hand_label

        # Sección de Registro de Actividad
        log_frame = ttk.LabelFrame(main_frame, text="Registro de Actividad", padding="10")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(5, weight=1) # Darle peso para que se expanda

        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=10, state=tk.DISABLED, font=("Courier New", 10))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        # Scrollbar ya integrado en ScrolledText, no necesita añadirse manualmente

    # --- Métodos de Interfaz (comandos del controlador) ---
    def load_xml_command(self):
        filepath = filedialog.askopenfilename(
            title="Seleccionar archivo XML de configuración",
            filetypes=[("Archivos XML", "*.xml")]
        )
        if filepath and self.controller:
            self.controller.load_game_configurations(filepath)

    def on_partida_selected(self, event):
        selected_partida_name = self.partida_combobox.get()
        if selected_partida_name and self.controller:
            self.log_message(f"Partida '{selected_partida_name}' seleccionada.")
            self.controller.select_partida(selected_partida_name) 
        else:
            self.log_message("Por favor, selecciona una partida válida.")

    def next_turn_command(self):
        """
        Acción para el botón "Siguiente Turno".
        Delega la ejecución del turno al controlador.
        """
        if self.controller:
            self.controller.play_turn() # El controlador maneja si el juego está activo y los logs

    # --- Métodos de Control de Estado de Widgets ---
    def enable_game_selection(self):
        """Habilita el combobox para seleccionar la partida."""
        self.partida_combobox.config(state="readonly")

    def disable_game_selection(self):
        """Deshabilita el combobox de selección de partida."""
        self.partida_combobox.config(state="disabled")

    def enable_play_button(self):
        """Habilita el botón de Siguiente Turno."""
        self.play_turn_button.config(state=tk.NORMAL)

    def disable_play_button(self):
        """Deshabilita el botón de Siguiente Turno."""
        self.play_turn_button.config(state=tk.DISABLED)

    def disable_game_controls(self):
        """Deshabilita todos los controles de juego (combobox y botón de turno)."""
        self.disable_game_selection()
        self.disable_play_button()

    def clear_game_over_message(self):
        """Limpia el mensaje de fin de juego."""
        self.game_over_label.config(text="")

    # --- Métodos de Actualización de la Vista (Reciben datos del controlador) ---
    def log_message(self, message: str):
        """
        Agrega un mensaje al área de log y hace que se desplace automáticamente.
        """
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END) # Auto-scroll al final
        self.log_text.config(state=tk.DISABLED)

    def display_available_partidas(self, partida_names: list[str]):
        """
        Actualiza los nombres de las partidas disponibles en el combobox.
        """
        self.partida_combobox['values'] = partida_names
        if partida_names:
            self.partida_combobox.set("Seleccionar una partida...") # Placeholder
        else:
            self.partida_combobox.set("No hay partidas disponibles")
            self.partida_combobox['values'] = []
            self.disable_game_selection()

    # --- NUEVOS MÉTODOS DE FORMATEO EN LA VISTA ---
    def _format_single_card_string_for_display(self, card_str: str) -> str:
        """
        Toma una cadena de carta como 'N (#HEXCODE)' y la convierte a 'N (NOMBRE_COLOR)'.
        Utiliza expresiones regulares para extraer el número y el código hexadecimal.
        """
        # Expresión regular para capturar el número y el código hexadecimal
        # Ejemplo: "4 (#c72623)" -> grupo 1: "4", grupo 2: "#c72623"
        match = re.match(r"(\d+)\s+\((#[0-9a-fA-F]{6})\)", card_str)
        if match:
            numero = match.group(1)
            hex_code = match.group(2)
            # Busca el nombre del color en el mapa, si no lo encuentra, usa el hex original
            color_name = COLOR_NAMES_MAP.get(hex_code, hex_code) 
            return f"{numero} ({color_name})"
        return card_str # Retorna la cadena original si no coincide el patrón

    def _format_list_of_cards_string_for_display(self, list_str: str) -> str:
        """
        Toma una cadena de texto que representa una lista de cartas (ej. 'Mazo: C1 -> C2')
        o una mano de jugador (ej. 'Mano de Juana: C1 -> C2')
        y aplica el formateo de nombre de color a cada carta.
        """
        if not list_str or "Vacío" in list_str or "N/A" in list_str:
            return list_str

        # Intentar separar el prefijo (ej. "Mazo: " o "Mano de Jugador:") de la lista de cartas
        prefix = ""
        card_list_raw = list_str

        # Si la cadena contiene ':', intentamos dividirla en prefijo y lista de cartas
        if ":" in list_str:
            parts = list_str.split(":", 1) # Divide solo por el primer ':'
            if len(parts) == 2:
                potential_prefix = parts[0].strip()
                potential_card_list = parts[1].strip()
                
                # Una heurística para determinar si es un prefijo real
                # Si la segunda parte contiene un '(', es probable que sea una lista de cartas
                if '(' in potential_card_list:
                    prefix = potential_prefix + ": "
                    card_list_raw = potential_card_list
                # Si no, asumimos que toda la cadena es una lista de cartas sin prefijo especial
                # o el ':' no es un separador de prefijo
                else:
                    prefix = ""
                    card_list_raw = list_str # Tratar toda la cadena como lista de cartas

        # Divide la lista de cartas raw por el separador " -> "
        cards_str_parts = card_list_raw.split(" -> ")
        
        # Formatea cada parte de la carta individualmente
        formatted_cards = [self._format_single_card_string_for_display(p.strip()) for p in cards_str_parts if p.strip()] # Filtra cadenas vacías

        # Reconstruye la cadena con el prefijo y las cartas formateadas
        return prefix + " -> ".join(formatted_cards)


    def update_game_state_display(self, current_player_name: str, card_on_table: str, mazo_reserva_info: str):
        """
        Actualiza los labels principales de la interfaz de usuario con la información actual del juego.
        Ahora, aplica el formateo de color a las cadenas de cartas recibidas.
        """
        self.current_player_label.config(text=f"Turno de: {current_player_name}")
        
        # Formatear la carta en mesa
        formatted_card_on_table = self._format_single_card_string_for_display(card_on_table)
        self.card_on_table_label.config(text=f"Carta en mesa: {formatted_card_on_table}")
        
        # Formatear la información del mazo de reserva
        formatted_mazo_reserva_info = self._format_list_of_cards_string_for_display(mazo_reserva_info)
        self.deck_display_label.config(text=f"Mazo de Reserva: {formatted_mazo_reserva_info}")

    def update_players_hands_display(self, players_hands_list: list[str]):
        """
        Actualiza los labels que muestran las manos de cada jugador.
        Ahora, aplica el formateo de color a cada cadena de mano recibida.
        """
        for i in range(len(players_hands_list)):
            if f"player_{i}" in self.player_hand_labels:
                # Formatear la cadena de la mano del jugador
                formatted_hand_str = self._format_list_of_cards_string_for_display(players_hands_list[i])
                self.player_hand_labels[f"player_{i}"].config(text=formatted_hand_str)
            
        # Limpiar/ocultar etiquetas de jugadores no usados o si el número de jugadores cambió
        for i in range(len(players_hands_list), 4): # Asumiendo un máximo de 4 jugadores UI
            if f"player_{i}" in self.player_hand_labels:
                self.player_hand_labels[f"player_{i}"].config(text="Mano: N/A")

    def on_game_end(self, message: str):
        """
        Método llamado por el controlador cuando la partida termina.
        Muestra un mensaje de fin de partida y deshabilita el botón de siguiente turno.
        """
        self.log_message(message) # También registrar en el log
        self.game_over_label.config(text=message, foreground="red") # Mostrar mensaje de fin de juego de forma destacada
        self.disable_play_button() # Deshabilitar el botón "Siguiente Turno" para evitar más jugadas