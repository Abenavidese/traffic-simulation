import tkinter as tk
import sys
import os

# Asegurar que el backend sea importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

class TrafficGUI:
    """Clase principal de la interfaz gráfica."""
    
    def __init__(self, root):
        self.root = root
        self.root.title(" Simulación de Tráfico - Cuenca")
        self.root.geometry("900x700")
        self.root.configure(bg="#2b2b2b")
        
        # --- Contenedores Principales ---
        # Frame izquierdo para el canvas (Simulación)
        self.canvas_frame = tk.Frame(self.root, bg="#2b2b2b", padx=10, pady=10)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Frame derecho para controles y stats
        self.sidebar_frame = tk.Frame(self.root, bg="#3c3f41", width=250, padx=10, pady=10)
        self.sidebar_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.sidebar_frame.pack_propagate(False) # Mantener ancho fijo

        # --- Componentes Iniciales ---
        # El Canvas donde dibujaremos la intersección
        self.canvas = tk.Canvas(
            self.canvas_frame, 
            bg="#1e1e1e", 
            highlightthickness=0,
            width=600, 
            height=600
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Etiqueta de título en la barra lateral
        self.sidebar_title = tk.Label(
            self.sidebar_frame, 
            text="PANEL DE CONTROL", 
            fg="white", 
            bg="#3c3f41", 
            font=("Arial", 12, "bold")
        )
        self.sidebar_title.pack(pady=(0, 20))

        # Dibujar los elementos estáticos (calles)
        self._draw_static_elements()

        # Próximo paso: Semáforos Gráficos

    def _draw_static_elements(self):
        """Dibuja las calles y líneas de la intersección."""
        # Colores
        color_asfalto = "#333333"
        color_linea = "#ffffff"
        color_linea_doble = "#ffcc00" # Amarillo para la doble línea central

        w, h = 600, 600
        road_width = 120 # Ancho de la calle
        
        # 1. Fondo de asfalto (Intersección central)
        # Calle Horizontal
        self.canvas.create_rectangle(0, (h/2) - (road_width/2), w, (h/2) + (road_width/2), fill=color_asfalto, outline="")
        # Calle Vertical
        self.canvas.create_rectangle((w/2) - (road_width/2), 0, (w/2) + (road_width/2), h, fill=color_asfalto, outline="")

        # 2. Líneas Centrales (Doble línea amarilla)
        # Horizontal
        self.canvas.create_line(0, h/2 - 2, w, h/2 - 2, fill=color_linea_doble, width=2)
        self.canvas.create_line(0, h/2 + 2, w, h/2 + 2, fill=color_linea_doble, width=2)
        
        # Vertical
        self.canvas.create_line(w/2 - 2, 0, w/2 - 2, h, fill=color_linea_doble, width=2)
        self.canvas.create_line(w/2 + 2, 0, w/2 + 2, h, fill=color_linea_doble, width=2)

        # 3. Líneas de detención (Blancas)
        # Norte
        self.canvas.create_line(w/2 - road_width/2, h/2 - road_width/2 - 5, w/2 + road_width/2, h/2 - road_width/2 - 5, fill=color_linea, width=4)
        # Sur
        self.canvas.create_line(w/2 - road_width/2, h/2 + road_width/2 + 5, w/2 + road_width/2, h/2 + road_width/2 + 5, fill=color_linea, width=4)
        # Este
        self.canvas.create_line(w/2 + road_width/2 + 5, h/2 - road_width/2, w/2 + road_width/2 + 5, h/2 + road_width/2, fill=color_linea, width=4)
        # Oeste
        self.canvas.create_line(w/2 - road_width/2 - 5, h/2 - road_width/2, w/2 - road_width/2 - 5, h/2 + road_width/2, fill=color_linea, width=4)

if __name__ == "__main__":
    root = tk.Tk()
    app = TrafficGUI(root)
    root.mainloop()
