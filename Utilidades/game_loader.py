import xml.etree.ElementTree as ET
from typing import Union
from Modelo.partida import Partida, ListaCartas, Carta, ListaGenerica, ShuffleInfo, PartidaConfigData 

class GameLoader:
    def __init__(self):
        pass

    def load_from_xml(self, filepath: str, log_callback=None) -> Union[Partida, None]:
        print(f"DEBUG: Intentando cargar XML desde: {filepath}")
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            
            new_partida_template = Partida() 

            cartas_root_element = root.find('mazo_disponible/cartas')
            if cartas_root_element:
                initial_deck_cards_template = ListaCartas()
                loaded_card_count = 0
                MAX_DECK_SIZE = 51 # Definimos el tamaño maximo del mazo

                for carta_element in cartas_root_element.findall('carta'):
                    # Si ya hemos cargado 51 cartas, ignorar las restantes
                    if loaded_card_count >= MAX_DECK_SIZE:
                        if log_callback:
                            log_callback(f"Advertencia (XML): El archivo contiene mas de {MAX_DECK_SIZE} cartas. Solo se tomaran las primeras {MAX_DECK_SIZE}.")
                        print(f"DEBUG: Advertencia: El archivo XML contiene mas de {MAX_DECK_SIZE} cartas. Se ignoran las adicionales.")
                        break 

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
                            log_callback(f"Advertencia (XML): Carta con numero invalido o faltante '{carta_element.text.strip()}' descartada.")
                        print(f"DEBUG: Advertencia: Carta '{carta_element.text.strip()}' (color: {color}) con numero invalido.")
                
                # Asigno la plantilla de mazo cargada a la partida
                new_partida_template.set_initial_deck_template(initial_deck_cards_template) 
                print(f"DEBUG: Mazo inicial de plantilla cargado con {new_partida_template._initial_deck_template.size} cartas (maximo {MAX_DECK_SIZE}).")
                print(f"DEBUG: Total de {new_partida_template._initial_deck_template.size} cartas cargadas en la plantilla del mazo inicial (maximo {MAX_DECK_SIZE}).")
            else:
                if log_callback:
                    log_callback("Advertencia (XML): No se encontro la seccion 'mazo_disponible/cartas' en el XML.")
                print("DEBUG: ERROR: Seccion 'mazo_disponible/cartas' no encontrada.")
                return None # Devolver None si no hay seccion de cartas

            # Cargamos los jugadores
            jugadores_element = root.find('jugadores')
            if jugadores_element:
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
                            print(f"DEBUG: Advertencia: Se ignoro el jugador '{player_name}' porque ya se cargaron 4 jugadores.")
                    else:
                        if log_callback:
                            log_callback(f"Advertencia (XML): Se encontro una etiqueta <jugador> con nombre vacio o nulo.")
                        print("DEBUG: Advertencia: Etiqueta <jugador> con nombre vacio.")
                
                new_partida_template.set_player_names_template(players_names_list_generica) 
                print(f"DEBUG: Nombres de jugadores plantilla establecidos: {players_names_list_generica.get_display_string()}")
                print(f"DEBUG: Nombres de jugadores cargados desde XML: {players_names_list_generica.get_display_string()}")
            else:
                if log_callback:
                    log_callback("Advertencia (XML): No se encontro la seccion 'jugadores' en el XML.")
                print("DEBUG: Advertencia: Seccion 'jugadores' no encontrada.")


            # Cargar Partidas y Shuffles
            all_partidas_configs_list_generica = ListaGenerica() 
            partidas_element = root.find('partidas')
            if partidas_element:
                print("DEBUG: Procesando configuraciones de partidas y shuffles...")
                for partida_element in partidas_element.findall('partida'):
                    partida_name = partida_element.get('nombre')
                    if partida_name:
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
                                                log_callback(f"Advertencia (XML): Valor 'x' ({x_value}) para shuffle '{shuffle_type}' es invalido (debe ser >= 1). Se usara 0.")
                                            print(f"DEBUG: Advertencia: Shuffle '{shuffle_type}' tiene x={x_value}, debe ser >= 1. Usando 0.")
                                            x_value = 0 
                                    except ValueError:
                                        if log_callback:
                                            log_callback(f"Advertencia (XML): Atributo 'x' invalido para shuffle '{shuffle_type}'.")
                                        print(f"DEBUG: Advertencia: Shuffle '{shuffle_type}' tiene atributo 'x' invalido.")
                                
                                shuffle_info_obj = ShuffleInfo(shuffle_type, x_value)
                                shuffles_for_current_partida_list_generica.agregar_final(shuffle_info_obj)
                                print(f"DEBUG:   - Shuffle cargado: {shuffle_info_obj}") 
                        else:
                            if log_callback:
                                log_callback(f"Advertencia (XML): No se encontro la seccion 'shuffles' para la partida '{partida_name}'.")
                            print(f"DEBUG: Advertencia: Seccion 'shuffles' no encontrada para partida '{partida_name}'.")
                        
                        # Esto para crear cada partida
                        partida_config_data_obj = PartidaConfigData(partida_name, shuffles_for_current_partida_list_generica)
                        all_partidas_configs_list_generica.agregar_final(partida_config_data_obj)

                    else:
                        if log_callback:
                            log_callback("Advertencia (XML): Se encontro una etiqueta <partida> sin atributo 'nombre'.")
                        print("DEBUG: Advertencia: Etiqueta <partida> sin atributo 'nombre'.")
            else:
                if log_callback:
                    log_callback("Advertencia (XML): No se encontro la seccion 'partidas' en el XML.")
                print("DEBUG: Advertencia: Seccion 'partidas' no encontrada.")
            
            new_partida_template._all_partidas_config_data = all_partidas_configs_list_generica
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
                log_callback(f"Ocurrio un error inesperado al cargar la configuracion: {e}")
            print(f"DEBUG: ERROR inesperado al cargar configuracion: {e}")
            return None
