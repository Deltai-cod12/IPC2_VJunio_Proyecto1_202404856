import xml.etree.ElementTree as ET
import os
from datetime import datetime


def save_game_log_to_xml(winner_info: str, steps_list: list[str], output_dir: str = "Utilidades"):

    root = ET.Element("partida_jugada")

    # Resumen
    resumen = ET.SubElement(root, "resumen")
    ganador_elem = ET.SubElement(resumen, "ganador")
    ganador_elem.text = winner_info

    total_pasos_elem = ET.SubElement(resumen, "total_pasos")
    total_pasos_elem.text = str(len(steps_list))

    # Pasos
    pasos_elem = ET.SubElement(root, "pasos")
    for i, step_desc in enumerate(steps_list):
        paso = ET.SubElement(pasos_elem, "paso", n=str(i + 1))
        paso.text = step_desc 

    tree = ET.ElementTree(root)
    ET.indent(tree, space="\t", level=0) 

    # Generar nombre de archivo unico
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"partida_jugada_{timestamp}.xml"
    filepath = os.path.join(output_dir, filename)

    try:
        tree.write(filepath, encoding="utf-8", xml_declaration=True)
        print(f"DEBUG: XML de partida guardado exitosamente en: {filepath}")
    except Exception as e:
        print(f"ERROR: No se pudo guardar el archivo XML de la partida: {e}")