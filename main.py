# main.py

import tkinter as tk
from Vista.mazo_vista import MazoView
from Controlador.partida_controlador import PartidaController

def main():
    root = tk.Tk()
    view = MazoView(root)
    controller = PartidaController(view)
    view.set_controller(controller)

    # Mensaje inicial de bienvenida o estado
    view.log_message("Aplicación 'Card Clash: IPC2 Edition' iniciada.")
    view.log_message("Por favor, cargue un archivo XML de configuración para empezar.")


    root.mainloop()

if __name__ == "__main__":
    main()
