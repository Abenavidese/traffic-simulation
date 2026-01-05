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
        self.canvas.bind("<Configure>", self._on_resize)
        
        # Dimensiones lógicas (base)
        self.logical_w = 600
        self.logical_h = 600
        self.scale = 1.0

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
        self.slider_prob.set(0.25)
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

        # Dibujar los elementos estáticos (calles) - Se dibuja en _on_resize
        # self._draw_static_elements()

        # --- Elementos Dinámicos ---
        # Diccionario para guardar las referencias de los semáforos en el canvas
        self.semaforos_graficos = {}
        # self._draw_traffic_lights() - Se dibuja en _on_resize

        # Próximo paso: Botones de Control

    def start_threading(self):
        """Inicia la simulación con el motor de hilos."""
        if self.running: return
        
        config = ConfiguracionSimulacion(
            intervalo_tick=self.slider_speed.get(),
            duracion_verde=self.slider_verde.get(),
            duracion_amarillo=max(2, int(self.slider_verde.get() * 0.3)),
            probabilidad_llegada=self.slider_prob.get(),
            capacidad_cruce_por_tick=3
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
            capacidad_cruce_por_tick=3
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
                # Asegurar que el objeto aún existe antes de actualizar
                try:
                    self.canvas.itemconfig(self.semaforos_graficos[via], fill=COLORS.get(color_name, "#ffffff"))
                except:
                    pass

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
                if i > 6: break # Límitar visualmente la cola para evitar superposición
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
                else:
                    # CASO "FANTASMA": Vehículo llegó e inmediatamente cruzó
                    # Lo creamos en la ENTRADA de la vía para que recorra todo el camino
                    start_pos = ENTRANCES[via]

                    self.visual_vehicles[v_id] = {
                        "x": start_pos[0], "y": start_pos[1], 
                        "tx": exit_pos[0], "ty": exit_pos[1], 
                        "via": via, "state": "CROSSING"
                    }

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
        """Mueve suavemente cada vehículo hacia su objetivo usando objetos persistentes."""
        if not self.running: return

        # Ya NO borramos todo con delete("auto") para evitar parpadeos y estelas

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

            # Actualizar gráficos (crear o mover)
            self._update_vehicle_graphics(v_id, v)

        # Eliminar vehículos que salieron
        for vid in to_remove:
            # Borrar gráficos del canvas
            if "gfx_ids" in self.visual_vehicles[vid]:
                for gfx_id in self.visual_vehicles[vid]["gfx_ids"]:
                    self.canvas.delete(gfx_id)
            del self.visual_vehicles[vid]

        self.root.after(self.fps_ms, self._animation_loop)

    def _update_vehicle_graphics(self, v_id, v_data):
        """Crea o actualiza los objetos gráficos de un vehículo."""
        x_log, y_log, via = v_data["x"], v_data["y"], v_data["via"]
        
        # Escalar coordenadas usando el nuevo sistema centrado
        x, y = self._to_screen(x_log, y_log)
        
        # Calcular dimensiones escaladas
        if via in ["NORTE", "SUR"]:
            w_base, h_base = 30, 45
        else:
            w_base, h_base = 45, 30
            
        w = w_base * self.scale
        h = h_base * self.scale
        
        # Calcular coords del cuerpo (bbox)
        items_coords = []
        
        # 1. Cuerpo
        items_coords.append((x - w/2, y - h/2, x + w/2, y + h/2))
        
        # 2 y 3. Faros
        f_size = 5 * self.scale
        offset_y_h = (h/2)
        offset_x_w = (w/2)
        offset_10 = 10 * self.scale
        offset_5 = 5 * self.scale

        if via == "NORTE":
            items_coords.append((x-offset_10, y+offset_y_h-f_size, x-offset_5, y+offset_y_h))
            items_coords.append((x+offset_5, y+offset_y_h-f_size, x+offset_10, y+offset_y_h))
        elif via == "SUR":
            items_coords.append((x-offset_10, y-offset_y_h, x-offset_5, y-offset_y_h+f_size))
            items_coords.append((x+offset_5, y-offset_y_h, x+offset_10, y-offset_y_h+f_size))
        elif via == "ESTE":
            items_coords.append((x-offset_x_w, y-offset_10, x-offset_x_w+f_size, y-offset_5))
            items_coords.append((x-offset_x_w, y+offset_5, x-offset_x_w+f_size, y+offset_10))
        elif via == "OESTE":
            items_coords.append((x+offset_x_w-f_size, y-offset_10, x+offset_x_w, y-offset_5))
            items_coords.append((x+offset_x_w-f_size, y+offset_5, x+offset_x_w, y+offset_10))

        # Crear o Actualizar
        if "gfx_ids" not in v_data:
            v_data["gfx_ids"] = []
            # Crear cuerpo
            body_id = self.canvas.create_rectangle(
                items_coords[0], 
                fill="#3498db", outline="white", width=max(1, 2*self.scale), 
                tags=("auto", f"veh_{v_id}")
            )
            v_data["gfx_ids"].append(body_id)
            
            # Crear faros
            for i in range(1, 3):
                light_id = self.canvas.create_oval(
                    items_coords[i], 
                    fill="yellow", outline="", 
                    tags=("auto", f"veh_{v_id}")
                )
                v_data["gfx_ids"].append(light_id)
        else:
            # Actualizar coords
            ids = v_data["gfx_ids"]
            if len(ids) == len(items_coords):
                for i, gfx_id in enumerate(ids):
                    self.canvas.coords(gfx_id, items_coords[i])
                    # Actualizar ancho de línea si cambia escala (opcional, pesado)
                    if i == 0: # Cuerpo
                        self.canvas.itemconfig(gfx_id, width=max(1, 2*self.scale))
            else:
                # Si por alguna razón no coinciden (ej. cambio de vía - raro), recrear todo
                for gfx_id in ids: self.canvas.delete(gfx_id)
                del v_data["gfx_ids"]
                self._update_vehicle_graphics(v_id, v_data)

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

    def _to_screen(self, lx, ly):
        """Convierte coords lógicas a pantalla (centrado y escalado)."""
        # (lx - 300) centra relativo al origen lógico (300, 300)
        # Luego escalamos y movemos al centro real del canvas
        sx = (lx - 300) * self.scale + self.center_x
        sy = (ly - 300) * self.scale + self.center_y
        return sx, sy

    def _on_resize(self, event):
        """Maneja el redimensionamiento de la ventana."""
        if event.width < 100 or event.height < 100: return
        
        # Guardar dimensiones actuales del canvas
        self.canvas_w = event.width
        self.canvas_h = event.height
        
        self.center_x = self.canvas_w / 2
        self.center_y = self.canvas_h / 2
        
        # Calcular escala basada en la altura (para que quepa verticalmente siempre)
        # Dejamos un margen del 10%
        target_h = self.logical_h
        self.scale = (self.canvas_h * 0.9) / target_h
        
        self.canvas.delete("all")
        self._draw_static_elements()
        self._draw_traffic_lights()

    def _draw_static_elements(self):
        """Dibuja las calles extendidas para llenar la pantalla."""
        s = self.scale
        # Ancho visual de la calle (sin escalar es 120)
        road_w = 120 * s
        half_road = road_w / 2
        
        # Colores
        color_asfalto = "#333333"
        color_linea = "#ffffff"
        color_linea_doble = "#ffcc00"
        color_cesped = "#2d5a27"
        color_vereda = "#999999"
        
        cx, cy = self.center_x, self.center_y
        w, h = self.canvas_w, self.canvas_h
        
        # 1. Fondo (Césped completo)
        self.canvas.create_rectangle(0, 0, w, h, fill=color_cesped, outline="")
        
        # 2. Asfalto (Cruces + Vías infinitas)
        # Vertical (Norte-Sur)
        self.canvas.create_rectangle(cx - half_road, 0, cx + half_road, h, fill=color_asfalto, outline="")
        # Horizontal (Este-Oeste)
        self.canvas.create_rectangle(0, cy - half_road, w, cy + half_road, fill=color_asfalto, outline="")
        
        # 3. Veredas (Esquinas del cruce)
        # Calculamos donde EMPIEZAN las veredas desde el centro
        corner_offset = half_road
        
        # Función para dibujar bloque de vereda y sus bordes
        def draw_corner(x_start, y_start, x_end, y_end):
            self.canvas.create_rectangle(x_start, y_start, x_end, y_end, fill=color_vereda, outline="#777777")
            
        # NO (Top-Left)
        draw_corner(0, 0, cx - corner_offset, cy - corner_offset)
        # NE (Top-Right)
        draw_corner(cx + corner_offset, 0, w, cy - corner_offset)
        # SO (Bottom-Left)
        draw_corner(0, cy + corner_offset, cx - corner_offset, h)
        # SE (Bottom-Right)
        draw_corner(cx + corner_offset, cy + corner_offset, w, h)

        # 4. Pasos de Cebra (Se mantienen en posición lógica fija relativa al centro)
        cw_dist = 60 * s # Distancia del centro al inicio de cebra (aprox 120/2)
        cw_len = 25 * s  # Largo de la cebra
        
        def draw_zebra(x, y, vertical=True):
            steps = 6
            step_w = road_w / steps
            for i in range(steps):
                if vertical:
                    off = i * step_w
                    self.canvas.create_rectangle(
                        x + off + 2*s, y, 
                        x + off + step_w - 2*s, y + cw_len, 
                        fill="white", outline=""
                    )
                else:
                    off = i * step_w
                    self.canvas.create_rectangle(
                        x, y + off + 2*s, 
                        x + cw_len, y + off + step_w - 2*s, 
                        fill="white", outline=""
                    )

        # Dibujar cebras (posicionadas usando offsets del centro)
        # Norte (Arriba del centro)
        draw_zebra(cx - half_road, cy - half_road - cw_len)
        # Sur (Abajo del centro)
        draw_zebra(cx - half_road, cy + half_road)
        # Este (Derecha del centro)
        draw_zebra(cx + half_road, cy - half_road, vertical=False)
        # Oeste (Izquierda del centro)
        draw_zebra(cx - half_road - cw_len, cy - half_road, vertical=False)
        
        # 5. Líneas de detención (Antes de las cebras)
        line_w = max(2, 4*s)
        # Norte
        self.canvas.create_line(cx - half_road, cy - half_road - cw_len - 5*s, cx + half_road, cy - half_road - cw_len - 5*s, fill=color_linea, width=line_w)
        # Sur
        self.canvas.create_line(cx - half_road, cy + half_road + cw_len + 5*s, cx + half_road, cy + half_road + cw_len + 5*s, fill=color_linea, width=line_w)
        # Este
        self.canvas.create_line(cx + half_road + cw_len + 5*s, cy - half_road, cx + half_road + cw_len + 5*s, cy + half_road, fill=color_linea, width=line_w)
        # Oeste
        self.canvas.create_line(cx - half_road - cw_len - 5*s, cy - half_road, cx - half_road - cw_len - 5*s, cy + half_road, fill=color_linea, width=line_w)

        # 6. Líneas Amarillas (Infinitas)
        ylw = max(1, 2*s)
        # Horizontal Oeste
        self.canvas.create_line(0, cy - 3*s, cx - half_road - cw_len - 10*s, cy - 3*s, fill=color_linea_doble, width=ylw)
        self.canvas.create_line(0, cy + 3*s, cx - half_road - cw_len - 10*s, cy + 3*s, fill=color_linea_doble, width=ylw)
        # Horizontal Este
        self.canvas.create_line(cx + half_road + cw_len + 10*s, cy - 3*s, w, cy - 3*s, fill=color_linea_doble, width=ylw)
        self.canvas.create_line(cx + half_road + cw_len + 10*s, cy + 3*s, w, cy + 3*s, fill=color_linea_doble, width=ylw)
        # Vertical Norte
        self.canvas.create_line(cx - 3*s, 0, cx - 3*s, cy - half_road - cw_len - 10*s, fill=color_linea_doble, width=ylw)
        self.canvas.create_line(cx + 3*s, 0, cx + 3*s, cy - half_road - cw_len - 10*s, fill=color_linea_doble, width=ylw)
        # Vertical Sur
        self.canvas.create_line(cx - 3*s, cy + half_road + cw_len + 10*s, cx - 3*s, h, fill=color_linea_doble, width=ylw)
        self.canvas.create_line(cx + 3*s, cy + half_road + cw_len + 10*s, cx + 3*s, h, fill=color_linea_doble, width=ylw)

    def _draw_traffic_lights(self):
        """Dibuja los semáforos usando el nuevo sistema de coordenadas."""
        s = self.scale
        # Posiciones lógicas originales
        POSITIONS = {
            "NORTE": (210, 175),
            "SUR":   (370, 405),
            "ESTE":  (405, 210),
            "OESTE": (175, 370)
        }
        self.semaforos_graficos = {}
        for via, (lx, ly) in POSITIONS.items():
            x, y = self._to_screen(lx, ly)
            
            r_luz = 20 * s
            
            self.canvas.create_rectangle(x-5*s, y-5*s, x+25*s, y+25*s, fill="#111111", outline="#555555")
            
            luz = self.canvas.create_oval(
                x, y, x+r_luz, y+r_luz,
                fill="#ff0000", outline="#333333", tags=f"luz_{via}"
            )
            self.semaforos_graficos[via] = luz
            
            self.canvas.create_text(
                x + 10*s, y - 15*s,
                text=via, fill="white", font=("Arial", max(6, int(8*s)), "bold")
            )

if __name__ == "__main__":
    root = tk.Tk()
    app = TrafficGUI(root)
    root.mainloop()
