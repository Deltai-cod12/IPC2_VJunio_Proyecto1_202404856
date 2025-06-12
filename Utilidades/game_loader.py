# Utilidades/game_loader.py

import xml.etree.ElementTree as ET
from typing import Union

# C.F. Importar directamente las clases personalizadas para usarlas en lugar de nativas
from Modelo.partida import Partida, ListaCartas, Carta, ListaGenerica, ShuffleInfo, PartidaConfigData 

class GameLoader:
    def __init__(self):
        pass

    def load_from_xml(self, filepath: str, log_callback=None) -> Union[Partida, None]:
        """
        Carga la configuración del juego desde un archivo XML.
        Retorna un objeto Partida que actúa como plantilla con la configuración inicial,
        o None si ocurre un error.
        """
        print(f"DEBUG: Intentando cargar XML desde: {filepath}")
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            
            new_partida_template = Partida() 

            # --- Cargar Mazo Inicial (como plantilla) ---
            cartas_root_element = root.find('mazo_disponible/cartas')
            if cartas_root_element:
                initial_deck_cards_template = ListaCartas()
                loaded_card_count = 0
                for carta_element in cartas_root_element.findall('carta'):
                    color = carta_element.get('color')
                    try:
                        numero = int(carta_element.text.strip())
                        if 1 <= numero <= 9:
                            carta = Carta(color, numero)
                            initial_deck_cards_template.insertar(carta)
                            loaded_card_count += 1
                            print(f"DEBUG: Carta XML cargada: {carta}") 
                        else:
                            if log_callback:
                                log_callback(f"Advertencia (XML): Carta con valor '{carta_element.text.strip()}' descartada (fuera de rango 1-9).")
                            print(f"DEBUG: Advertencia: Carta '{carta_element.text.strip()}' (color: {color}) fuera de rango.")
                    except (ValueError, TypeError):
                        if log_callback:
                            log_callback(f"Advertencia (XML): Carta con número inválido o faltante '{carta_element.text.strip()}' descartada.")
                        print(f"DEBUG: Advertencia: Carta '{carta_element.text.strip()}' (color: {color}) con número inválido.")
                
                new_partida_template.set_initial_deck_template(initial_deck_cards_template) 
                print(f"DEBUG: Total de {loaded_card_count} cartas cargadas en la plantilla del mazo inicial.")
            else:
                if log_callback:
                    log_callback("Advertencia (XML): No se encontró la sección 'mazo_disponible/cartas' en el XML.")
                print("DEBUG: ERROR: Sección 'mazo_disponible/cartas' no encontrada.")
                return None

            if new_partida_template._initial_deck_template.size != 51:
                if log_callback:
                    log_callback(f"Advertencia (XML): El mazo inicial tiene {new_partida_template._initial_deck_template.size} cartas. Se esperaban 51.")
                print(f"DEBUG: Advertencia: Tamaño del mazo inicial ({new_partida_template._initial_deck_template.size}) no es 51.")


            # --- Cargar Jugadores (solo nombres como plantilla) ---
            jugadores_element = root.find('jugadores')
            if jugadores_element:
                # C.F. Usar ListaGenerica en lugar de list nativa
                players_names_list_generica = ListaGenerica() 
                loaded_player_count = 0 
                for jugador_element in jugadores_element.findall('jugador'):
                    player_name_raw = jugador_element.text
                    player_name = str(player_name_raw).strip() if player_name_raw is not None else ""
                    
                    if player_name:
                        if loaded_player_count < 4: # Limitar a 4 jugadores
                            players_names_list_generica.agregar_final(player_name) 
                            loaded_player_count += 1
                            print(f"DEBUG: Jugador '{player_name}' cargado desde XML.") 
                        else:
                            print(f"DEBUG: Advertencia: Se ignoró el jugador '{player_name}' porque ya se cargaron 4 jugadores.")
                    else:
                        if log_callback:
                            log_callback(f"Advertencia (XML): Se encontró una etiqueta <jugador> con nombre vacío o nulo.")
                        print("DEBUG: Advertencia: Etiqueta <jugador> con nombre vacío.")
                
                # C.F. Pasar la ListaGenerica completa al set_player_names_template
                new_partida_template.set_player_names_template(players_names_list_generica) 
                print(f"DEBUG: Nombres de jugadores cargados desde XML: {players_names_list_generica.get_display_string()}")
            else:
                if log_callback:
                    log_callback("Advertencia (XML): No se encontró la sección 'jugadores' en el XML.")
                print("DEBUG: Advertencia: Sección 'jugadores' no encontrada.")


            # --- Cargar Partidas y Shuffles (todas las configs de shuffles disponibles) ---
            # C.F. Usar ListaGenerica para almacenar PartidaConfigData en lugar de un dict nativo
            all_partidas_configs_list_generica = ListaGenerica() 
            partidas_element = root.find('partidas')
            if partidas_element:
                print("DEBUG: Procesando configuraciones de partidas y shuffles...")
                for partida_element in partidas_element.findall('partida'):
                    partida_name = partida_element.get('nombre')
                    if partida_name:
                        # C.F. Usar ListaGenerica para shuffles de la partida actual
                        shuffles_for_current_partida_list_generica = ListaGenerica()
                        shuffles_element = partida_element.find('shuffles')
                        if shuffles_element:
                            print(f"DEBUG: Shuffles para partida '{partida_name}':")
                            for shuffle_element in shuffles_element.findall('shuffle'):
                                shuffle_type = shuffle_element.text.strip().upper()
                                x_value_str = shuffle_element.get('x')
                                
                                x_value = None
                                if x_value_str:
                                    try:
                                        x_value = int(x_value_str)
                                        if x_value < 1:
                                            if log_callback:
                                                log_callback(f"Advertencia (XML): Valor 'x' ({x_value}) para shuffle '{shuffle_type}' es inválido (debe ser >= 1). Se usará 0.")
                                            print(f"DEBUG: Advertencia: Shuffle '{shuffle_type}' tiene x={x_value}, debe ser >= 1. Usando 0.")
                                            x_value = 0 
                                    except ValueError:
                                        if log_callback:
                                            log_callback(f"Advertencia (XML): Atributo 'x' inválido para shuffle '{shuffle_type}'.")
                                        print(f"DEBUG: Advertencia: Shuffle '{shuffle_type}' tiene atributo 'x' inválido.")
                                
                                # C.F. Crear objeto ShuffleInfo en lugar de un dict nativo
                                shuffle_info_obj = ShuffleInfo(shuffle_type, x_value)
                                # C.F. Agregar a la ListaGenerica de shuffles para esta partida
                                shuffles_for_current_partida_list_generica.agregar_final(shuffle_info_obj)
                                print(f"DEBUG:   - Shuffle cargado: {shuffle_info_obj}") 
                            
                            # C.F. Crear PartidaConfigData y añadirla a la ListaGenerica
                            partida_config_data_obj = PartidaConfigData(partida_name, shuffles_for_current_partida_list_generica)
                            all_partidas_configs_list_generica.agregar_final(partida_config_data_obj)

                        else:
                            if log_callback:
                                log_callback(f"Advertencia (XML): No se encontró la sección 'shuffles' para la partida '{partida_name}'.")
                            print(f"DEBUG: Advertencia: Sección 'shuffles' no encontrada para partida '{partida_name}'.")
                    else:
                        if log_callback:
                            log_callback("Advertencia (XML): Se encontró una etiqueta <partida> sin atributo 'nombre'.")
                        print("DEBUG: Advertencia: Etiqueta <partida> sin atributo 'nombre'.")
            else:
                if log_callback:
                    log_callback("Advertencia (XML): No se encontró la sección 'partidas' en el XML.")
                print("DEBUG: Advertencia: Sección 'partidas' no encontrada.")
            
            # C.F. Asignar la ListaGenerica de configs al template de la partida
            new_partida_template._all_partidas_config_data = all_partidas_configs_list_generica
            # C.F. Para la depuración, obtener string de la ListaGenerica
            print(f"DEBUG: Todas las configuraciones de partidas cargadas: {new_partida_template._all_partidas_config_data.get_display_string()}")

            return new_partida_template

        except FileNotFoundError:
            if log_callback:
                log_callback(f"Error: El archivo no fue encontrado en la ruta: {filepath}")
            print(f"DEBUG: ERROR: Archivo XML no encontrado: {filepath}")
            return None
        except ET.ParseError as e:
            if log_callback:
                log_callback(f"Error al parsear el XML: {e}")
            print(f"DEBUG: ERROR al parsear XML: {e}")
            return None
        except Exception as e:
            if log_callback:
                log_callback(f"Ocurrió un error inesperado al cargar la configuración: {e}")
            print(f"DEBUG: ERROR inesperado al cargar configuración: {e}")
            return None
