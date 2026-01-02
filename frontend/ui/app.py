import tkinter as tk
import sys
import os

# Asegurar que el backend sea importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.app.config import ConfiguracionSimulacion
from backend.runtime.engines.threading_engine import ThreadingEngine
from backend.runtime.engines.multiprocessing_engine import MultiprocessingEngine

class TrafficGUI:
    """Clase principal de la interfaz gráfica."""
    
    def __init__(self, root):
        self.root = root
        self.root.title(" Simulación de Tráfico - Cuenca")
        self.root.geometry("900x700")
        self.root.configure(bg="#2b2b2b")
        
        # Estado de la simulación
        self.engine = None
        self.running = False
        
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

        # Botones de inicio
        self.btn_threading = tk.Button(
            self.sidebar_frame, text="▶️ Iniciar Hilos", 
            command=self.start_threading, bg="#4CAF50", fg="white", 
            font=("Arial", 10, "bold"), pady=10, relief=tk.FLAT, cursor="hand2"
        )
        self.btn_threading.pack(fill=tk.X, pady=5)

        self.btn_multiproc = tk.Button(
            self.sidebar_frame, text="▶️ Iniciar Procesos", 
            command=self.start_multiprocessing, bg="#2196F3", fg="white", 
            font=("Arial", 10, "bold"), pady=10, relief=tk.FLAT, cursor="hand2"
        )
        self.btn_multiproc.pack(fill=tk.X, pady=5)

        self.btn_stop = tk.Button(
            self.sidebar_frame, text="⏹️ Detener", 
            command=self.stop_simulation, bg="#f44336", fg="white", 
            font=("Arial", 10, "bold"), pady=10, relief=tk.FLAT, cursor="hand2",
            state=tk.DISABLED
        )
        self.btn_stop.pack(fill=tk.X, pady=(20, 5))

        # --- Panel de Estadísticas ---
        self.stats_frame = tk.LabelFrame(
            self.sidebar_frame, text=" ESTADÍSTICAS ", 
            fg="white", bg="#3c3f41", font=("Arial", 10, "bold"),
            padx=10, pady=10, relief=tk.GROOVE
        )
        self.stats_frame.pack(fill=tk.X, pady=20)

        # Labels de estadísticas
        self.label_tick = self._create_stat_label("Tick:", "0")
        self.label_ciclo = self._create_stat_label("Ciclo:", "0")
        self.label_total = self._create_stat_label("Total Veh.:", "0")
        self.label_espera = self._create_stat_label("Espera Prom.:", "0.00s")

        # --- Barra de Progreso de Fase ---
        self.phase_frame = tk.LabelFrame(self.sidebar_frame, text=" FASE ACTUAL ", fg="white", bg="#3c3f41", font=("Arial", 10, "bold"), padx=10, pady=10)
        self.phase_frame.pack(fill=tk.X, pady=10)
        
        self.label_fase_nombre = tk.Label(self.phase_frame, text="ESPERANDO...", fg="#ffcc00", bg="#3c3f41", font=("Arial", 9, "bold"))
        self.label_fase_nombre.pack()
        
        self.canvas_phase = tk.Canvas(self.phase_frame, height=15, bg="#2b2b2b", highlightthickness=0)
        self.canvas_phase.pack(fill=tk.X, pady=5)
        self.phase_bar = self.canvas_phase.create_rectangle(0, 0, 0, 15, fill="#4db6ac", outline="")

        # --- Log de Eventos ---
        self.log_frame = tk.LabelFrame(self.sidebar_frame, text=" EVENTOS (LOG) ", fg="white", bg="#3c3f41", font=("Arial", 10, "bold"), padx=5, pady=5)
        self.log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_list = tk.Listbox(self.log_frame, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 8), borderwidth=0, highlightthickness=0)
        self.log_list.pack(fill=tk.BOTH, expand=True)

        # Dibujar los elementos estáticos (calles)
        self._draw_static_elements()

        # --- Elementos Dinámicos ---
        # Diccionario para guardar las referencias de los semáforos en el canvas
        self.semaforos_graficos = {}
        self._draw_traffic_lights()

        # Próximo paso: Botones de Control

    def start_threading(self):
        """Inicia la simulación con el motor de hilos."""
        if self.running: return
        
        config = ConfiguracionSimulacion(intervalo_tick=0.3)
        self.engine = ThreadingEngine(config)
        self.engine.start()
        
        self.running = True
        self.btn_threading.config(state=tk.DISABLED)
        self.btn_multiproc.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        
        # Iniciar el loop de actualización
        self.update_loop()

    def start_multiprocessing(self):
        """Inicia la simulación con el motor de procesos."""
        if self.running: return

        config = ConfiguracionSimulacion(intervalo_tick=0.3)
        self.engine = MultiprocessingEngine(config)
        self.engine.start()

        self.running = True
        self.btn_threading.config(state=tk.DISABLED)
        self.btn_multiproc.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        
        # Iniciar el loop de actualización
        self.update_loop()

    def stop_simulation(self):
        """Detiene la simulación."""
        if not self.running: return
        
        self.running = False
        if self.engine:
            self.engine.stop()
            self.engine = None

        self.btn_threading.config(state=tk.NORMAL)
        self.btn_multiproc.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)

    def update_loop(self):
        """Loop principal de actualización de la GUI."""
        if not self.running:
            return

        # 1. Obtener el nuevo estado del backend
        state = self.engine.step()

        # 2. Actualizar visualización
        self._update_ui(state)

        # 3. Programar el siguiente tick (según configuración del backend)
        interval_ms = int(state.configuracion.get('intervalo_tick', 0.3) * 1000)
        self.root.after(interval_ms, self.update_loop)

    def _update_ui(self, state):
        """Actualiza todos los elementos gráficos con el nuevo estado."""
        # Limpiar elementos dinámicos
        self.canvas.delete("vehiculo")
        self.canvas.delete("transito")

        # 1. Actualizar colores de semáforos
        COLORS = {"VERDE": "#00FF00", "AMARILLO": "#FFFF00", "ROJO": "#FF0000"}
        for via, color_name in state.luces.items():
            if via in self.semaforos_graficos:
                self.canvas.itemconfig(self.semaforos_graficos[via], fill=COLORS.get(color_name, "#ffffff"))

        # 2. Dibujar vehículos en las colas
        self._draw_vehicles(state.vehiculos_detalle)
        
        # 3. Dibujar vehículos CRUZANDO (Movimiento)
        self._draw_transit(state.vehiculos_en_transito)

        # 4. Actualizar estadísticas
        stats = state.estadisticas
        self.label_tick.config(text=str(state.tick))
        self.label_ciclo.config(text=str(state.ciclo))
        self.label_total.config(text=str(stats.get('total_vehiculos', 0)))
        espera = stats.get('tiempo_espera_promedio', 0)
        self.label_espera.config(text=f"{espera:.2f}s")
        
        # 5. Actualizar Barra de Fase y Nombre
        timing = state.timing_fase
        self.label_fase_nombre.config(text=timing['fase_actual'])
        progreso = timing['ticks_en_fase'] / timing['duracion_total']
        self.canvas_phase.coords(self.phase_bar, 0, 0, progreso * 200, 15) # 200 es aprox el ancho

        # 6. Actualizar Log de Eventos
        eventos = state.eventos_tick.get("eventos", [])
        for ev in eventos:
            msg = f"[{state.tick}] {ev.get('icono', '')} {ev['via']}: {ev['tipo'].replace('vehiculo_', '')}"
            self.log_list.insert(0, msg)
            if self.log_list.size() > 50: self.log_list.delete(50, tk.END)

    def _create_stat_label(self, text, initial_value):
        """Crea un par de etiquetas (nombre: valor) en el panel de estadísticas."""
        container = tk.Frame(self.stats_frame, bg="#3c3f41")
        container.pack(fill=tk.X, pady=2)
        
        tk.Label(container, text=text, fg="#aaaaaa", bg="#3c3f41", font=("Arial", 9)).pack(side=tk.LEFT)
        val_label = tk.Label(container, text=initial_value, fg="#4db6ac", bg="#3c3f41", font=("Arial", 9, "bold"))
        val_label.pack(side=tk.RIGHT)
        return val_label

    def _draw_transit(self, vehiculos_en_transito):
        """Anima los vehículos que están cruzando la intersección."""
        # Rutas de cruce: (x_start, y_start, x_end, y_end)
        ROUTES = {
            "NORTE": (300, 230, 300, 370), # Baja
            "SUR":   (300, 370, 300, 230), # Sube
            "ESTE":  (370, 300, 230, 300), # Va a la izquierda
            "OESTE": (230, 300, 370, 300)  # Va a la derecha
        }

        for via, vehiculos in vehiculos_en_transito.items():
            if via not in ROUTES: continue
            x1, y1, x2, y2 = ROUTES[via]
            
            for v in vehiculos:
                prog = v['progreso']
                # Interpolar posición
                x = x1 + (x2 - x1) * prog
                y = y1 + (y2 - y1) * prog
                
                self.canvas.create_oval(
                    x-10, y-10, x+10, y+10,
                    fill="#2ecc71", outline="white", width=2,
                    tags="transito"
                )

    def _draw_vehicles(self, vehiculos_detalle):
        """Dibuja los vehículos esperando en cada vía."""
        # Configuración de dibujo de colas
        # x_start, y_start, dx, dy (dirección de la fila)
        OFFSET = 25 # Espacio entre autos
        QUEUE_CFG = {
            "NORTE": (285, 230, 0, -OFFSET), # Hacia arriba
            "SUR":   (285, 360, 0, OFFSET),  # Hacia abajo
            "ESTE":  (360, 285, OFFSET, 0),  # Hacia la derecha
            "OESTE": (230, 285, -OFFSET, 0)  # Hacia la izquierda
        }

        for via, vehiculos in vehiculos_detalle.items():
            if via not in QUEUE_CFG: continue
            
            x0, y0, dx, dy = QUEUE_CFG[via]
            
            for i, v in enumerate(vehiculos):
                # Calcular posición basada en el índice en la cola
                x = x0 + (i * dx)
                y = y0 + (i * dy)
                
                # Dibujar un rectángulo azul para el vehículo
                # Ancho y alto según orientación
                if via in ["NORTE", "SUR"]:
                    w_car, h_car = 30, 20
                else:
                    w_car, h_car = 20, 30

                self.canvas.create_rectangle(
                    x, y, x + w_car, y + h_car,
                    fill="#3498db", outline="white",
                    tags="vehiculo"
                )

    def _draw_traffic_lights(self):
        """Dibuja los 4 semáforos en sus posiciones iniciales (Rojo)."""
        # Posiciones estratégicas en las esquinas de la intersección
        # Ajustadas para estar a la derecha de cada vía de entrada
        POSITIONS = {
            "NORTE": (370, 180),
            "SUR":   (190, 380),
            "ESTE":  (380, 370),
            "OESTE": (180, 190)
        }

        for via, (x, y) in POSITIONS.items():
            # Dibujar el "poste" o fondo del semáforo
            self.canvas.create_rectangle(x-5, y-5, x+25, y+25, fill="#111111", outline="#555555")
            
            # Dibujar la luz (inicialmente roja)
            luz = self.canvas.create_oval(
                x, y, x+20, y+20,
                fill="#ff0000", # Rojo
                outline="#333333",
                tags=f"luz_{via}"
            )
            
            # Guardar referencia para actualizar el color después
            self.semaforos_graficos[via] = luz
            
            # Etiqueta de la vía
            self.canvas.create_text(
                x+10, y-15,
                text=via,
                fill="white",
                font=("Arial", 8, "bold")
            )

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
