import tkinter as tk
import sys
import os
import platform
import multiprocessing

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
        self.tick_interval = 1.5 # Segundos entre procesos de lógica
        
        # --- Sistema de Animación Fluida ---
        self.visual_vehicles = {} # id -> {x, y, target_x, target_y, via, state}
        self.animation_speed = 4.0 # Píxeles por frame de animación
        self.fps_ms = 30           # ~33 FPS para fluidez
        
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
        self._bind_hover_effect(self.btn_threading, "#4CAF50", "#66BB6A")

        self.btn_multiproc = tk.Button(
            self.sidebar_frame, text="▶️ Iniciar Procesos", 
            command=self.start_multiprocessing, bg="#2196F3", fg="white", 
            font=("Arial", 10, "bold"), pady=10, relief=tk.FLAT, cursor="hand2"
        )
        self.btn_multiproc.pack(fill=tk.X, pady=5)
        self._bind_hover_effect(self.btn_multiproc, "#2196F3", "#42A5F5")

        self.btn_stop = tk.Button(
            self.sidebar_frame, text="⏹️ Detener", 
            command=self.stop_simulation, bg="#f44336", fg="white", 
            font=("Arial", 10, "bold"), pady=10, relief=tk.FLAT, cursor="hand2",
            state=tk.DISABLED
        )
        self.btn_stop.pack(fill=tk.X, pady=(20, 5))
        self._bind_hover_effect(self.btn_stop, "#f44336", "#ef5350")

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

        # --- Configuración Interactiva ---
        self.config_frame = tk.LabelFrame(
            self.sidebar_frame, text=" CONFIGURACIÓN ", 
            fg="white", bg="#3c3f41", font=("Arial", 10, "bold"),
            padx=10, pady=10, relief=tk.GROOVE
        )
        self.config_frame.pack(fill=tk.X, pady=10)

        # Slider para Duración Verde
        tk.Label(self.config_frame, text="Duración Verde (ticks):", fg="#aaaaaa", bg="#3c3f41", font=("Arial", 8)).pack(anchor=tk.W)
        self.slider_verde = tk.Scale(
            self.config_frame, from_=5, to=30, orient=tk.HORIZONTAL,
            bg="#3c3f41", fg="white", highlightthickness=0, troughcolor="#2b2b2b"
        )
        self.slider_verde.set(15)
        self.slider_verde.pack(fill=tk.X, pady=(0, 5))

        # Slider para Probabilidad de Llegada
        tk.Label(self.config_frame, text="Probabilidad Llegada:", fg="#aaaaaa", bg="#3c3f41", font=("Arial", 8)).pack(anchor=tk.W)
        self.slider_prob = tk.Scale(
            self.config_frame, from_=0.05, to=0.5, resolution=0.01, orient=tk.HORIZONTAL,
            bg="#3c3f41", fg="white", highlightthickness=0, troughcolor="#2b2b2b"
        )
        self.slider_prob.set(0.15)
        self.slider_prob.pack(fill=tk.X, pady=(0, 5))

        # Slider para Velocidad (Tick Interval)
        tk.Label(self.config_frame, text="Intervalo Tick (s):", fg="#aaaaaa", bg="#3c3f41", font=("Arial", 8)).pack(anchor=tk.W)
        self.slider_speed = tk.Scale(
            self.config_frame, from_=0.5, to=3.0, resolution=0.1, orient=tk.HORIZONTAL,
            bg="#3c3f41", fg="white", highlightthickness=0, troughcolor="#2b2b2b"
        )
        self.slider_speed.set(1.5)
        self.slider_speed.pack(fill=tk.X, pady=(0, 5))

        # --- Información del Sistema ---
        self.system_frame = tk.LabelFrame(
            self.sidebar_frame, text=" SISTEMA ", 
            fg="white", bg="#3c3f41", font=("Arial", 10, "bold"),
            padx=10, pady=10, relief=tk.GROOVE
        )
        self.system_frame.pack(fill=tk.X, pady=10)

        # Recopilar información del entorno
        py_version = platform.python_version()
        
        # Detección del GIL mejorada
        if hasattr(sys, "_is_gil_enabled"):
            gil_enabled = sys._is_gil_enabled()
            gil_status = "Habilitado" if gil_enabled else "Deshabilitado"
        else:
            # En versiones < 3.13 el GIL siempre está presente
            gil_status = "Habilitado (Versión Legacy)"
        
        os_name = platform.system()
        cpu_count = multiprocessing.cpu_count()

        # Mostrar información en el panel
        self._create_info_label(self.system_frame, "Python:", f"v{py_version}")
        self._create_info_label(self.system_frame, "GIL:", gil_status)
        self._create_info_label(self.system_frame, "SO:", os_name)
        self._create_info_label(self.system_frame, "Núcleos CPU:", str(cpu_count))

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
        
        config = ConfiguracionSimulacion(
            intervalo_tick=self.slider_speed.get(),
            duracion_verde=self.slider_verde.get(),
            duracion_amarillo=max(2, int(self.slider_verde.get() * 0.3)),
            probabilidad_llegada=self.slider_prob.get(),
            capacidad_cruce_por_tick=1
        )
        self.engine = ThreadingEngine(config)
        self.engine.start()
        
        self.running = True
        self.btn_threading.config(state=tk.DISABLED)
        self.btn_multiproc.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        
        # Bloquear sliders durante ejecución (opcional, para evitar inconsistencias)
        self._toggle_config_state(tk.DISABLED)
        
        # Iniciar el loop de actualización y animación
        self.update_loop()
        self._animation_loop()

    def start_multiprocessing(self):
        """Inicia la simulación con el motor de procesos."""
        if self.running: return

        config = ConfiguracionSimulacion(
            intervalo_tick=self.slider_speed.get(),
            duracion_verde=self.slider_verde.get(),
            duracion_amarillo=max(2, int(self.slider_verde.get() * 0.3)),
            probabilidad_llegada=self.slider_prob.get(),
            capacidad_cruce_por_tick=1
        )
        self.engine = MultiprocessingEngine(config)
        self.engine.start()

        self.running = True
        self.btn_threading.config(state=tk.DISABLED)
        self.btn_multiproc.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        
        self._toggle_config_state(tk.DISABLED)
        
        # Iniciar el loop de actualización y animación
        self.update_loop()
        self._animation_loop()

    def _toggle_config_state(self, state):
        """Habilita/Deshabilita los controles de configuración."""
        self.slider_verde.config(state=state)
        self.slider_prob.config(state=state)
        self.slider_speed.config(state=state)

    def stop_simulation(self):
        """Detiene la simulación."""
        if not self.running: return
        
        self.running = False
        if self.engine:
            self.engine.stop()
            self.engine = None

        # --- LIMPIEZA DE ESTADO ---
        self.visual_vehicles.clear()      # Eliminar rastro de autos antiguos
        self.canvas.delete("auto")        # Limpiar canvas inmediatamente
        self._reset_ui_stats()            # Reiniciar contadores visuales

        self.btn_threading.config(state=tk.NORMAL)
        self.btn_multiproc.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self._toggle_config_state(tk.NORMAL)

    def _reset_ui_stats(self):
        """Reinicia las etiquetas de estadísticas en la interfaz."""
        self.label_tick.config(text="0")
        self.label_ciclo.config(text="0")
        self.label_total.config(text="0")
        self.label_espera.config(text="0.00s")
        self.label_fase_nombre.config(text="ESPERANDO...")
        self.canvas_phase.coords(self.phase_bar, 0, 0, 0, 15)
        # Opcional: limpiar log (o dejarlo para historial)
        # self.log_list.delete(0, tk.END)

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
        """Sincroniza el estado del motor con el sistema de animación visual."""
        # 1. Actualizar colores de semáforos
        COLORS = {"VERDE": "#00FF00", "AMARILLO": "#FFFF00", "ROJO": "#FF0000"}
        for via, color_name in state.luces.items():
            if via in self.semaforos_graficos:
                self.canvas.itemconfig(self.semaforos_graficos[via], fill=COLORS.get(color_name, "#ffffff"))

        # Ajuste de coordenadas para que el FRENTE del auto se detenga en la línea
        OFFSET = 65 
        STOP_LINES = {
            "NORTE": 210, "SUR": 390, "ESTE": 390, "OESTE": 210
        }
        # Entradas y Salidas
        ENTRANCES = {
            "NORTE": (270, -100), "SUR": (330, 700), "ESTE": (700, 270), "OESTE": (-100, 330)
        }
        EXITS = {
            "NORTE": (270, 800), "SUR": (330, -200), "ESTE": (-200, 270), "OESTE": (800, 330)
        }

        active_ids = []
        
        # Procesar colas: Vehículos esperando o llegando
        for via, vehiculos in state.vehiculos_detalle.items():
            for i, v in enumerate(vehiculos):
                v_id = v.get('id', 0) if isinstance(v, dict) else getattr(v, 'id', 0)
                active_ids.append(v_id)
                
                # Posición objetivo en la cola
                if via == "NORTE": target = (270, STOP_LINES[via] - (i * OFFSET))
                elif via == "SUR": target = (330, STOP_LINES[via] + (i * OFFSET))
                elif via == "ESTE": target = (STOP_LINES[via] + (i * OFFSET), 270)
                elif via == "OESTE": target = (STOP_LINES[via] - (i * OFFSET), 330)
                
                if v_id not in self.visual_vehicles:
                    # Nuevo vehículo detectado
                    start_pos = ENTRANCES[via]
                    self.visual_vehicles[v_id] = {
                        "x": start_pos[0], "y": start_pos[1], 
                        "tx": target[0], "ty": target[1], 
                        "via": via, "state": "QUEUE"
                    }
                else:
                    # Si ya cruza, no lo regresamos a la cola (evita saltos visuales)
                    if self.visual_vehicles[v_id]["state"] != "CROSSING":
                        # Solo actualizar objetivo si sigue en cola
                        self.visual_vehicles[v_id]["tx"] = target[0]
                        self.visual_vehicles[v_id]["ty"] = target[1]
                        self.visual_vehicles[v_id]["state"] = "QUEUE"

        # Procesar cruzando: Vehículos despachados en este tick
        for via, vehiculos in state.vehiculos_en_transito.items():
            for v in vehiculos:
                v_id = v['id']
                active_ids.append(v_id)
                exit_pos = EXITS[via]
                
                if v_id in self.visual_vehicles:
                    self.visual_vehicles[v_id]["tx"] = exit_pos[0]
                    self.visual_vehicles[v_id]["ty"] = exit_pos[1]
                    self.visual_vehicles[v_id]["state"] = "CROSSING"

        # 3. Limpieza de "Fantasmas" y Sincronización Forzada
        # Si un auto no está en el backend pero sigue en nuestra lista visual como QUEUE,
        # significa que se despachó pero perdimos el evento o el tick. Forzamos su salida.
        for v_id, v_data in list(self.visual_vehicles.items()):
            if v_id not in active_ids:
                if v_data["state"] == "QUEUE":
                    # Forzar cruce si desapareció de la cola
                    v_data["state"] = "CROSSING"
                    v_data["tx"], v_data["ty"] = EXITS[v_data["via"]]
                # Si ya está en CROSSING, se borrará solo al llegar a la meta

        # 3. Actualizar estadísticas y Log
        self.label_tick.config(text=str(state.tick))
        self.label_ciclo.config(text=str(state.ciclo))
        self.label_total.config(text=str(state.estadisticas.get('total_vehiculos', 0)))
        self.label_espera.config(text=f"{state.estadisticas.get('tiempo_espera_promedio', 0):.2f}s")
        
        timing = state.timing_fase
        self.label_fase_nombre.config(text=timing['fase_actual'])
        progreso = timing['ticks_en_fase'] / timing['duracion_total']
        self.canvas_phase.coords(self.phase_bar, 0, 0, progreso * 200, 15)

        eventos = state.eventos_tick.get("eventos", [])
        for ev in eventos:
            msg = f"[{state.tick}] {ev.get('icono', '')} {ev['via']}: {ev['tipo'].replace('vehiculo_', '')}"
            self.log_list.insert(0, msg)
            if self.log_list.size() > 50: self.log_list.delete(50, tk.END)

    def _animation_loop(self):
        """Mueve suavemente cada vehículo hacia su objetivo."""
        if not self.running: return

        # Limpiar canvas dinámico
        self.canvas.delete("auto")

        to_remove = []
        for v_id, v in self.visual_vehicles.items():
            # Interpolar posición (Mover un paso hacia el objetivo)
            dx = v["tx"] - v["x"]
            dy = v["ty"] - v["y"]
            dist = (dx**2 + dy**2)**0.5

            if dist > self.animation_speed:
                v["x"] += (dx/dist) * self.animation_speed
                v["y"] += (dy/dist) * self.animation_speed
            else:
                v["x"] = v["tx"]
                v["y"] = v["ty"]
                # Si llegó a la salida, marcar para eliminar
                if v["state"] == "CROSSING" and dist < 1:
                    to_remove.append(v_id)

            # Dibujar el auto (Rectángulo azul con faros)
            self._render_vehicle(v["x"], v["y"], v["via"])

        for vid in to_remove:
            del self.visual_vehicles[vid]

        self.root.after(self.fps_ms, self._animation_loop)

    def _render_vehicle(self, x, y, via):
        """Dibuja un vehículo centrado en (x,y)."""
        color = "#3498db"
        if via in ["NORTE", "SUR"]:
            w, h = 30, 45
        else:
            w, h = 45, 30

        # Cuerpo
        self.canvas.create_rectangle(
            x - w/2, y - h/2, x + w/2, y + h/2,
            fill=color, outline="white", width=2, tags="auto"
        )
        
        # Faros
        f_size = 5
        if via == "NORTE": # Hacia el SUR
            self.canvas.create_oval(x-10, y+h/2-f_size, x-5, y+h/2, fill="yellow", tags="auto")
            self.canvas.create_oval(x+5, y+h/2-f_size, x+10, y+h/2, fill="yellow", tags="auto")
        elif via == "SUR":
            self.canvas.create_oval(x-10, y-h/2, x-5, y-h/2+f_size, fill="yellow", tags="auto")
            self.canvas.create_oval(x+5, y-h/2, x+10, y-h/2+f_size, fill="yellow", tags="auto")
        elif via == "ESTE":
            self.canvas.create_oval(x-w/2, y-10, x-w/2+f_size, y-5, fill="yellow", tags="auto")
            self.canvas.create_oval(x-w/2, y+5, x-w/2+f_size, y+10, fill="yellow", tags="auto")
        elif via == "OESTE":
            self.canvas.create_oval(x+w/2-f_size, y-10, x+w/2, y-5, fill="yellow", tags="auto")
            self.canvas.create_oval(x+w/2-f_size, y+5, x+w/2, y+10, fill="yellow", tags="auto")

    def _create_stat_label(self, text, initial_value):
        """Crea un par de etiquetas (nombre: valor) en el panel de estadísticas."""
        container = tk.Frame(self.stats_frame, bg="#3c3f41")
        container.pack(fill=tk.X, pady=2)
        
        tk.Label(container, text=text, fg="#aaaaaa", bg="#3c3f41", font=("Arial", 9)).pack(side=tk.LEFT)
        val_label = tk.Label(container, text=initial_value, fg="#4db6ac", bg="#3c3f41", font=("Arial", 9, "bold"))
        val_label.pack(side=tk.RIGHT)
        return val_label

    def _create_info_label(self, parent, text, value):
        """Crea un par de etiquetas (nombre: valor) en el panel de sistema."""
        container = tk.Frame(parent, bg="#3c3f41")
        container.pack(fill=tk.X, pady=1)
        
        tk.Label(container, text=text, fg="#aaaaaa", bg="#3c3f41", font=("Arial", 8)).pack(side=tk.LEFT)
        tk.Label(container, text=value, fg="#ffffff", bg="#3c3f41", font=("Arial", 8, "bold")).pack(side=tk.RIGHT)

    def _bind_hover_effect(self, button, normal_color, hover_color):
        """Añade un efecto de cambio de color al pasar el mouse por encima."""
        def on_enter(e):
            if button['state'] == tk.NORMAL:
                button['bg'] = hover_color
        def on_leave(e):
            if button['state'] == tk.NORMAL:
                button['bg'] = normal_color
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def _get_vehicle_color(self, vehiculo_id):
        """Devuelve azul estándar para todos."""
        return "#3498db"

    def _draw_traffic_lights(self):
        """Dibuja los 4 semáforos a la derecha de cada carril."""
        # Reposicionados para estar a la derecha de la vía que llega al cruce
        POSITIONS = {
            "NORTE": (210, 175), # Derecha bajando
            "SUR":   (370, 405), # Derecha subiendo
            "ESTE":  (405, 210), # Derecha yendo a izquierda
            "OESTE": (175, 370)  # Derecha yendo a derecha
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
        """Dibuja las calles y detalles urbanos (veredas, pasos de cebra)."""
        # Colores
        color_asfalto = "#333333"
        color_linea = "#ffffff"
        color_linea_doble = "#ffcc00"
        color_cesped = "#2d5a27"
        color_vereda = "#999999"

        w, h = 600, 600
        road_width = 120
        
        # 1. Fondo (Césped)
        self.canvas.create_rectangle(0, 0, w, h, fill=color_cesped, outline="")

        # 2. Veredas (Bloques en las esquinas)
        corner_size = (w/2) - (road_width/2)
        # Esquina NO
        self.canvas.create_rectangle(0, 0, corner_size, corner_size, fill=color_vereda, outline="#777777")
        # Esquina NE
        self.canvas.create_rectangle(w - corner_size, 0, w, corner_size, fill=color_vereda, outline="#777777")
        # Esquina SO
        self.canvas.create_rectangle(0, h - corner_size, corner_size, h, fill=color_vereda, outline="#777777")
        # Esquina SE
        self.canvas.create_rectangle(w - corner_size, h - corner_size, w, h, fill=color_vereda, outline="#777777")

        # 3. Asfalto (Calles)
        self.canvas.create_rectangle(0, corner_size, w, h - corner_size, fill=color_asfalto, outline="")
        self.canvas.create_rectangle(corner_size, 0, w - corner_size, h, fill=color_asfalto, outline="")

        # 4. Pasos de Cebra
        def draw_crosswalk(x1, y1, x2, y2, vertical=True):
            steps = 6
            for i in range(steps):
                if vertical:
                    offset = i * (road_width / steps)
                    self.canvas.create_rectangle(x1 + offset + 2, y1, x1 + offset + 15, y2, fill="white", outline="")
                else:
                    offset = i * (road_width / steps)
                    self.canvas.create_rectangle(x1, y1 + offset + 2, x2, y1 + offset + 15, fill="white", outline="")

        # Norte
        draw_crosswalk(corner_size, corner_size - 25, w - corner_size, corner_size - 10)
        # Sur
        draw_crosswalk(corner_size, h - corner_size + 10, w - corner_size, h - corner_size + 25)
        # Este
        draw_crosswalk(w - corner_size + 10, corner_size, w - corner_size + 25, h - corner_size, vertical=False)
        # Oeste
        draw_crosswalk(corner_size - 25, corner_size, corner_size - 10, h - corner_size, vertical=False)

        # 5. Líneas Amarillas (Doble línea central)
        # Horizontal
        self.canvas.create_line(0, h/2 - 2, corner_size - 30, h/2 - 2, fill=color_linea_doble, width=2)
        self.canvas.create_line(0, h/2 + 2, corner_size - 30, h/2 + 2, fill=color_linea_doble, width=2)
        self.canvas.create_line(w - corner_size + 30, h/2 - 2, w, h/2 - 2, fill=color_linea_doble, width=2)
        self.canvas.create_line(w - corner_size + 30, h/2 + 2, w, h/2 + 2, fill=color_linea_doble, width=2)
        
        # Vertical
        self.canvas.create_line(w/2 - 2, 0, w/2 - 2, corner_size - 30, fill=color_linea_doble, width=2)
        self.canvas.create_line(w/2 + 2, 0, w/2 + 2, corner_size - 30, fill=color_linea_doble, width=2)
        self.canvas.create_line(w/2 - 2, h - corner_size + 30, w/2 - 2, h, fill=color_linea_doble, width=2)
        self.canvas.create_line(w/2 + 2, h - corner_size + 30, w/2 + 2, h, fill=color_linea_doble, width=2)

        # 6. Líneas de detención (Anchas antes de la cebra)
        self.canvas.create_line(corner_size, corner_size - 5, w - corner_size, corner_size - 5, fill=color_linea, width=4)
        self.canvas.create_line(corner_size, h - corner_size + 5, w - corner_size, h - corner_size + 5, fill=color_linea, width=4)
        self.canvas.create_line(w - corner_size + 5, corner_size, w - corner_size + 5, h - corner_size, fill=color_linea, width=4)
        self.canvas.create_line(corner_size - 5, corner_size, corner_size - 5, h - corner_size, fill=color_linea, width=4)

if __name__ == "__main__":
    root = tk.Tk()
    app = TrafficGUI(root)
    root.mainloop()
