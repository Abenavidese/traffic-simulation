# 🎨 Frontend Implementation Guide

> Guía completa de implementación del frontend para la simulación de tráfico paralelo

---

## 📋 Tabla de Contenidos

- [Arquitectura](#-arquitectura)
- [Flujo de Datos](#-flujo-de-datos)
- [TrafficState: La Fuente de Verdad](#-trafficstate-la-fuente-de-verdad)
- [Componentes a Implementar](#-componentes-a-implementar)
- [Ejemplos de Uso](#-ejemplos-de-uso)
- [Tips y Mejores Prácticas](#-tips-y-mejores-prácticas)

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                   GUI (Tkinter)                         │
│  ┌───────────┐  ┌───────────┐  ┌──────────────┐       │
│  │  Canvas   │  │  Stats    │  │   Controls   │       │
│  │  View     │  │  Panel    │  │   Panel      │       │
│  └─────┬─────┘  └─────┬─────┘  └──────┬───────┘       │
│        │              │               │                 │
│        └──────────────┼───────────────┘                 │
│                       │                                 │
│              ┌────────▼────────┐                        │
│              │  Main App       │                        │
│              │  (app.py)       │                        │
│              └────────┬────────┘                        │
└───────────────────────┼──────────────────────────────────┘
                        │
                ┌───────▼────────┐
                │  Engine        │ ← Threading/Multiprocessing
                │  (Backend)     │
                └───────┬────────┘
                        │
                ┌───────▼────────┐
                │ TrafficState   │ ← Única fuente de datos
                └────────────────┘
```

---

## 🔄 Flujo de Datos

### **1. El Backend genera el estado**

```python
# En backend/runtime/engines/threading_engine.py
state = engine.step()  # Ejecuta 1 tick
# state es un objeto TrafficState
```

### **2. El Frontend consume el estado**

```python
# En frontend/ui/app.py
def update():
    state = engine.step()          # Obtener estado
    render_canvas(state)           # Dibujar
    update_stats(state)            # Actualizar stats
    update_controls(state)         # Actualizar controles
    root.after(interval, update)   # Siguiente tick
```

### **3. Un ciclo completo**

```
Backend: step() → TrafficState
   ↓
Frontend: recibe TrafficState
   ↓
Canvas: dibuja intersección
   ↓
Stats: actualiza números
   ↓
Controls: actualiza estado
   ↓
Espera intervalo_tick
   ↓
Repite
```

---

## 📦 TrafficState: La Fuente de Verdad

**Ubicación:** [`backend/core/common/state.py`](../backend/core/common/state.py)

`TrafficState` es el **único objeto** que el frontend necesita. Contiene TODO el estado del sistema.

### **Estructura Completa**

```python
@dataclass
class TrafficState:
    # ══════════════════════════════════════════
    # BÁSICO: Información temporal
    # ══════════════════════════════════════════
    tick: int                          # Número de tick actual
    ciclo: int                         # Ciclos completados
    fase: str                          # Fase actual del controlador
    
    # ══════════════════════════════════════════
    # SEMÁFOROS: Estado de luces
    # ══════════════════════════════════════════
    luces: Dict[str, str]              # Via → Color
    
    # ══════════════════════════════════════════
    # COLAS: Tamaños de colas por vía
    # ══════════════════════════════════════════
    colas: Dict[str, int]              # Via → Cantidad
    
    # ══════════════════════════════════════════
    # ESTADÍSTICAS: Métricas acumuladas
    # ══════════════════════════════════════════
    estadisticas: Dict[str, any]       # Varios
    
    # ══════════════════════════════════════════
    # SISTEMA: Info del motor y Python
    # ══════════════════════════════════════════
    info_sistema: Dict[str, str]       # Metadata
    
    # ══════════════════════════════════════════
    # 🆕 VEHÍCULOS DETALLADOS
    # ══════════════════════════════════════════
    vehiculos_detalle: Dict[str, list] # Via → [Vehículo]
    
    # ══════════════════════════════════════════
    # 🆕 VEHÍCULOS EN TRÁNSITO
    # ══════════════════════════════════════════
    vehiculos_en_transito: Dict[str, list]  # Via → [Progreso]
    
    # ══════════════════════════════════════════
    # 🆕 EVENTOS DEL TICK
    # ══════════════════════════════════════════
    eventos_tick: Dict[str, list]      # {"eventos": [...]}
    
    # ══════════════════════════════════════════
    # 🆕 TIMING DE FASE
    # ══════════════════════════════════════════
    timing_fase: Dict[str, int]        # Info de timing
    
    # ══════════════════════════════════════════
    # 🆕 CONFIGURACIÓN
    # ══════════════════════════════════════════
    configuracion: Dict[str, any]      # Parámetros
```

---

## 📊 Datos Disponibles - Referencia Completa

### **1. Información Temporal** ⏰

**Origen:** `ControladorTrafico.tick_actual`, `ControladorTrafico.ciclo_actual`

```python
state.tick    # int: 45
state.ciclo   # int: 3
state.fase    # str: "NS_VERDE" | "NS_AMARILLO" | "EW_VERDE" | "EW_AMARILLO"
```

**Cómo usar en frontend:**
```python
# Mostrar en UI
label_tick.config(text=f"Tick: {state.tick}")
label_ciclo.config(text=f"Ciclo: {state.ciclo}")
label_fase.config(text=f"Fase: {state.fase}")
```

---

### **2. Estado de Semáforos** 🚦

**Origen:** `Semaforo.color` para cada vía

```python
state.luces = {
    "NORTE": "VERDE",   # str: "VERDE" | "AMARILLO" | "ROJO"
    "SUR": "VERDE",
    "ESTE": "ROJO",
    "OESTE": "ROJO"
}
```

**Cómo usar en frontend:**
```python
# Dibujar semáforos en canvas
COLORES = {"VERDE": "#00FF00", "AMARILLO": "#FFFF00", "ROJO": "#FF0000"}

for via, color in state.luces.items():
    x, y = POSICIONES_SEMAFOROS[via]
    canvas.create_oval(
        x, y, x+30, y+30,
        fill=COLORES[color],
        tags=f"semaforo_{via}"
    )
```

---

### **3. Tamaños de Colas** 📏

**Origen:** `Semaforo.tamano_cola` para cada vía

```python
state.colas = {
    "NORTE": 5,   # int: cantidad de vehículos esperando
    "SUR": 3,
    "ESTE": 0,
    "OESTE": 2
}
```

**Cómo usar en frontend:**
```python
# Mostrar contador de vehículos
for via, cantidad in state.colas.items():
    label = labels_cola[via]
    label.config(text=f"{via}: {cantidad} 🚗")
    
# O dibujar en canvas
canvas.create_text(x, y, text=f"{cantidad} vehículos")
```

---

### **4. Estadísticas Acumuladas** 📊

**Origen:** `EstadisticasTrafico.get_resumen()`

```python
state.estadisticas = {
    "total_vehiculos": 245,              # int: total cruzados
    "tiempo_espera_promedio": 1.234,     # float: segundos
    "tiempo_espera_total": 302.33,       # float: segundos
    "vehiculos_por_via": {               # Dict[str, int]
        "NORTE": 62,
        "SUR": 58,
        "ESTE": 64,
        "OESTE": 61
    }
}
```

**Cómo usar en frontend:**
```python
# Panel de estadísticas
stats = state.estadisticas
label_total.config(text=f"Total: {stats['total_vehiculos']}")
label_promedio.config(text=f"Espera: {stats['tiempo_espera_promedio']:.2f}s")

# Gráfico de barras por vía
for via, count in stats['vehiculos_por_via'].items():
    altura = count * 2  # Escalar
    canvas.create_rectangle(x, y-altura, x+20, y, fill="blue")
```

---

### **5. Información del Sistema** 💻

**Origen:** Engine (info del runtime)

```python
state.info_sistema = {
    "motor": "Threading",                    # str: "Threading" | "Multiprocessing"
    "python_version": "3.13.11",            # str
    "gil_enabled": "False",                 # str: "True" | "False"
    "procesos_activos": 4  # Solo en multiprocessing
}
```

**Cómo usar en frontend:**
```python
# Mostrar en barra de estado
info = state.info_sistema
status_bar.config(
    text=f"Motor: {info['motor']} | Python: {info['python_version']} | GIL: {info['gil_enabled']}"
)
```

---

### **6. Vehículos Detallados** 🚗🔍

**Origen:** `Semaforo.get_vehiculos_detalle()`

```python
state.vehiculos_detalle = {
    "NORTE": [
        {"id": 15, "posicion": 0, "esperando_desde": 0.52},
        {"id": 23, "posicion": 1, "esperando_desde": 1.14},
        {"id": 31, "posicion": 2, "esperando_desde": 1.78}
    ],
    "SUR": [
        {"id": 18, "posicion": 0, "esperando_desde": 0.31}
    ],
    "ESTE": [],
    "OESTE": []
}
```

**Campos por vehículo:**
- `id` (int): Identificador único
- `posicion` (int): Posición en cola (0 = primero)
- `esperando_desde` (float): Tiempo esperando en segundos

**Cómo usar en frontend:**
```python
# Dibujar cada vehículo en su posición
for via, vehiculos in state.vehiculos_detalle.items():
    x_base, y_base = POSICIONES_COLA[via]
    
    for vehiculo in vehiculos:
        # Calcular posición según índice
        offset = vehiculo['posicion'] * ESPACIADO
        x = x_base + offset * dx[via]
        y = y_base + offset * dy[via]
        
        # Dibujar vehículo
        canvas.create_rectangle(
            x, y, x+20, y+10,
            fill="blue",
            tags=f"vehiculo_{vehiculo['id']}"
        )
        
        # Tooltip con tiempo de espera
        canvas.create_text(
            x+10, y-5,
            text=f"#{vehiculo['id']}\n{vehiculo['esperando_desde']:.1f}s",
            font=("Arial", 8)
        )
```

---

### **7. Vehículos en Tránsito** 🚗💨

**Origen:** Engine (vehículos actualmente cruzando)

```python
state.vehiculos_en_transito = {
    "ESTE": [
        {"id": 8, "progreso": 0.5},    # 50% del cruce
        {"id": 12, "progreso": 1.0}    # 100% (casi saliendo)
    ],
    "OESTE": [
        {"id": 9, "progreso": 0.3}     # 30% del cruce
    ]
}
```

**Campos por vehículo:**
- `id` (int): Identificador único
- `progreso` (float): 0.0 → 1.0 (0% → 100%)

**Cómo usar en frontend:**
```python
# Animar vehículos cruzando la intersección
for via, vehiculos in state.vehiculos_en_transito.items():
    inicio_x, inicio_y = INICIO_CRUCE[via]
    fin_x, fin_y = FIN_CRUCE[via]
    
    for v in vehiculos:
        # Interpolar posición según progreso
        x = inicio_x + (fin_x - inicio_x) * v['progreso']
        y = inicio_y + (fin_y - inicio_y) * v['progreso']
        
        # Dibujar vehículo en movimiento
        canvas.create_oval(
            x-5, y-5, x+5, y+5,
            fill="green",
            tags=f"transito_{v['id']}"
        )
        
        # Opcional: estela de movimiento
        if v['progreso'] > 0.2:
            canvas.create_line(
                inicio_x, inicio_y, x, y,
                fill="lightgreen", width=2, dash=(2,2)
            )
```

---

### **8. Eventos del Tick** 📋

**Origen:** Engine (eventos del tick actual)

```python
state.eventos_tick = {
    "eventos": [
        {
            "tipo": "vehiculo_llego",
            "via": "NORTE",
            "vehiculo_id": 15,
            "icono": "🚗→"
        },
        {
            "tipo": "vehiculo_despachado",
            "via": "SUR",
            "vehiculo_id": 12,
            "icono": "🚗✓"
        },
        {
            "tipo": "cambio_semaforo",
            "via": "ESTE",
            "color_anterior": "VERDE",
            "color_nuevo": "AMARILLO",
            "icono": "🟡"
        }
    ]
}
```

**Tipos de eventos:**
1. **`vehiculo_llego`**: Un vehículo llegó a una cola
2. **`vehiculo_despachado`**: Un vehículo cruzó la intersección
3. **`cambio_semaforo`**: Un semáforo cambió de color

**Cómo usar en frontend:**
```python
# Feed de eventos en tiempo real
eventos = state.eventos_tick.get("eventos", [])

for evento in eventos:
    tipo = evento['tipo']
    icono = evento['icono']
    
    if tipo == "vehiculo_llego":
        mensaje = f"{icono} Vehículo #{evento['vehiculo_id']} llegó a {evento['via']}"
    elif tipo == "vehiculo_despachado":
        mensaje = f"{icono} Vehículo #{evento['vehiculo_id']} cruzó desde {evento['via']}"
    elif tipo == "cambio_semaforo":
        mensaje = f"{icono} {evento['via']}: {evento['color_anterior']} → {evento['color_nuevo']}"
    
    # Agregar a listbox o text widget
    event_feed.insert(0, mensaje)  # Más reciente arriba
    event_feed.config(fg="green" if "✓" in icono else "black")
    
    # Opcional: notificación toast
    if tipo == "cambio_semaforo":
        mostrar_toast(mensaje, duracion=1000)
```

---

### **9. Timing de Fase** ⏱️

**Origen:** `ControladorTrafico.get_timing_fase()`

```python
state.timing_fase = {
    "fase_actual": "EW_VERDE",      # str: nombre de la fase
    "ticks_en_fase": 2,             # int: ticks transcurridos
    "ticks_restantes": 3,           # int: ticks que faltan
    "duracion_total": 5             # int: duración total
}
```

**Cómo usar en frontend:**
```python
timing = state.timing_fase

# Barra de progreso
progreso = timing['ticks_en_fase'] / timing['duracion_total']
progressbar['value'] = progreso * 100

# Visual con bloques
bloques_hechos = "█" * timing['ticks_en_fase']
bloques_pendientes = "░" * timing['ticks_restantes']
label_timing.config(text=f"[{bloques_hechos}{bloques_pendientes}]")

# Countdown numérico
tiempo_restante = timing['ticks_restantes'] * state.configuracion['intervalo_tick']
label_countdown.config(text=f"Cambia en: {tiempo_restante:.1f}s")

# Porcentaje
porcentaje = progreso * 100
label_porcentaje.config(text=f"{porcentaje:.0f}%")
```

---

### **10. Configuración** ⚙️

**Origen:** `ConfiguracionSimulacion`

```python
state.configuracion = {
    "duracion_verde": 5,              # int: ticks
    "duracion_amarillo": 2,           # int: ticks
    "capacidad_cruce": 2,             # int: vehículos/tick
    "probabilidad_llegada": 0.6,      # float: 0.0-1.0
    "intervalo_tick": 0.3             # float: segundos
}
```

**Cómo usar en frontend:**
```python
config = state.configuracion

# Panel de configuración (solo lectura)
label_verde.config(text=f"Verde: {config['duracion_verde']} ticks")
label_amarillo.config(text=f"Amarillo: {config['duracion_amarillo']} ticks")
label_capacidad.config(text=f"Capacidad: {config['capacidad_cruce']} veh/tick")
label_prob.config(text=f"Prob. llegada: {config['probabilidad_llegada']*100:.0f}%")

# Calcular FPS para animaciones
fps = 1.0 / config['intervalo_tick']  # ~3.33 FPS con intervalo 0.3
```

---

## 🎨 Componentes a Implementar

### **1. Canvas View (Vista de Intersección)**

**Archivo:** `frontend/ui/views/canvas_view.py`

**Responsabilidad:** Dibujar la intersección, semáforos y vehículos

```python
class CanvasView:
    def __init__(self, parent):
        self.canvas = tk.Canvas(parent, width=600, height=600, bg="white")
        self.canvas.pack()
    
    def render(self, state: TrafficState):
        """Dibuja todo basado en el estado."""
        self.canvas.delete("all")  # Limpiar
        
        # 1. Dibujar carreteras
        self._draw_roads()
        
        # 2. Dibujar semáforos con colores
        self._draw_lights(state.luces)
        
        # 3. Dibujar vehículos en colas
        self._draw_queued_vehicles(state.vehiculos_detalle)
        
        # 4. Dibujar vehículos en tránsito
        self._draw_transit_vehicles(state.vehiculos_en_transito)
        
        # 5. Mostrar contadores
        self._draw_counters(state.colas)
```

**Datos usados:**
- `state.luces` → Colores de semáforos
- `state.vehiculos_detalle` → Vehículos en cola
- `state.vehiculos_en_transito` → Vehículos cruzando
- `state.colas` → Contadores

---

### **2. Stats Panel (Panel de Estadísticas)**

**Archivo:** `frontend/ui/views/stats_panel.py`

**Responsabilidad:** Mostrar estadísticas en tiempo real

```python
class StatsPanel:
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.labels = {}
        # ... crear labels
    
    def update(self, state: TrafficState):
        """Actualiza las estadísticas."""
        stats = state.estadisticas
        
        # Actualizar labels
        self.labels['total'].config(text=f"Total: {stats['total_vehiculos']}")
        self.labels['promedio'].config(text=f"Espera: {stats['tiempo_espera_promedio']:.2f}s")
        
        # Actualizar por vía
        for via, count in stats['vehiculos_por_via'].items():
            self.labels[via].config(text=f"{via}: {count}")
```

**Datos usados:**
- `state.estadisticas` → Todas las métricas
- `state.info_sistema` → Info del motor

---

### **3. Controls Panel (Panel de Controles)**

**Archivo:** `frontend/ui/views/controls_panel.py`

**Responsabilidad:** Controles y configuración

```python
class ControlsPanel:
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        # ... crear botones y labels
    
    def update(self, state: TrafficState):
        """Actualiza info de estado."""
        # Tick y ciclo
        self.label_tick.config(text=f"Tick: {state.tick}")
        self.label_ciclo.config(text=f"Ciclo: {state.ciclo}")
        
        # Fase con barra de progreso
        timing = state.timing_fase
        progreso = timing['ticks_en_fase'] / timing['duracion_total']
        self.progressbar['value'] = progreso * 100
        
        # Configuración
        config = state.configuracion
        self.label_config.config(
            text=f"Verde:{config['duracion_verde']} Amarillo:{config['duracion_amarillo']}"
        )
```

**Datos usados:**
- `state.tick`, `state.ciclo`, `state.fase`
- `state.timing_fase` → Barra de progreso
- `state.configuracion` → Info

---

### **4. Event Feed (Log de Eventos)**

**Archivo:** `frontend/ui/views/event_feed.py`

**Responsabilidad:** Mostrar eventos en tiempo real

```python
class EventFeed:
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.listbox = tk.Listbox(self.frame, height=10)
        self.listbox.pack()
    
    def update(self, state: TrafficState):
        """Agrega nuevos eventos."""
        eventos = state.eventos_tick.get("eventos", [])
        
        for evento in eventos:
            mensaje = self._format_event(evento)
            self.listbox.insert(0, mensaje)  # Más reciente arriba
            
        # Limitar a 50 eventos
        if self.listbox.size() > 50:
            self.listbox.delete(50, tk.END)
    
    def _format_event(self, evento):
        tipo = evento['tipo']
        icono = evento['icono']
        
        if tipo == "vehiculo_llego":
            return f"{icono} Veh #{evento['vehiculo_id']} → {evento['via']}"
        elif tipo == "vehiculo_despachado":
            return f"{icono} Veh #{evento['vehiculo_id']} cruzó {evento['via']}"
        else:
            return f"{icono} {evento['via']}: {evento['color_anterior']}→{evento['color_nuevo']}"
```

**Datos usados:**
- `state.eventos_tick` → Lista de eventos

---

## 💡 Ejemplos de Uso

### **Ejemplo 1: Aplicación Básica**

```python
import tkinter as tk
from backend.app.config import ConfiguracionSimulacion
from backend.runtime.engines.threading_engine import ThreadingEngine

class TrafficApp:
    def __init__(self, root):
        self.root = root
        
        # Crear engine
        self.config = ConfiguracionSimulacion(intervalo_tick=0.3)
        self.engine = ThreadingEngine(self.config)
        self.engine.start()
        
        # UI
        self.label_tick = tk.Label(root, text="Tick: 0")
        self.label_tick.pack()
        
        # Loop
        self.update_loop()
    
    def update_loop(self):
        # Obtener estado
        state = self.engine.step()
        
        # Actualizar UI
        self.label_tick.config(text=f"Tick: {state.tick}")
        
        # Siguiente tick
        self.root.after(300, self.update_loop)
    
    def on_close(self):
        self.engine.stop()

root = tk.Tk()
app = TrafficApp(root)
root.protocol("WM_DELETE_WINDOW", app.on_close)
root.mainloop()
```

---

### **Ejemplo 2: Dibujar Semáforos**

```python
def draw_lights(canvas, state):
    POSITIONS = {
        "NORTE": (280, 200),
        "SUR": (320, 400),
        "ESTE": (400, 320),
        "OESTE": (200, 280)
    }
    
    COLORS = {
        "VERDE": "#00FF00",
        "AMARILLO": "#FFFF00",
        "ROJO": "#FF0000"
    }
    
    for via, (x, y) in POSITIONS.items():
        color = state.luces[via]
        canvas.create_oval(
            x, y, x+40, y+40,
            fill=COLORS[color],
            outline="black",
            width=2
        )
        canvas.create_text(x+20, y-10, text=via, font=("Arial", 10))
```

---

### **Ejemplo 3: Animar Vehículos en Tránsito**

```python
def draw_transit(canvas, state):
    ROUTES = {
        "NORTE": ((300, 100), (300, 300)),  # y aumenta
        "SUR": ((300, 500), (300, 300)),     # y disminuye
        "ESTE": ((500, 300), (300, 300)),    # x disminuye
        "OESTE": ((100, 300), (300, 300))    # x aumenta
    }
    
    for via, vehiculos in state.vehiculos_en_transito.items():
        (x0, y0), (x1, y1) = ROUTES[via]
        
        for v in vehiculos:
            # Interpolar
            x = x0 + (x1 - x0) * v['progreso']
            y = y0 + (y1 - y0) * v['progreso']
            
            # Dibujar
            canvas.create_rectangle(
                x-10, y-5, x+10, y+5,
                fill="blue",
                outline="darkblue"
            )
```

---

## 🎯 Tips y Mejores Prácticas

### **1. Rendimiento**

```python
# ✅ Bueno: Borrar solo elementos específicos
canvas.delete("vehiculos")  # Con tags

# ❌ Malo: Borrar todo cada frame
canvas.delete("all")  # Más lento
```

### **2. Animaciones Suaves**

```python
# Usar interpolación para transiciones
def smooth_move(current, target, speed=0.1):
    return current + (target - current) * speed

# Aplicar en cada frame
x = smooth_move(x_actual, x_objetivo)
```

### **3. Gestión de Memoria**

```python
# Limitar históricos
if len(event_list) > 100:
    event_list = event_list[:100]  # Solo últimos 100
```

### **4. Colores y Temas**

```python
THEME = {
    "bg": "#1E1E1E",
    "fg": "#FFFFFF",
    "accent": "#007ACC",
    "success": "#4EC9B0",
    "warning": "#DCDCAA",
    "error": "#F48771"
}
```

---

## 📚 Recursos Adicionales

- [Tkinter Canvas Docs](https://docs.python.org/3/library/tkinter.html#canvas-objects)
- [Tkinter Colors](https://www.tcl.tk/man/tcl8.4/TkCmd/colors.html)
- [Backend README](../README.MD)

---

## 🚀 Checklist de Implementación

- [ ] Crear `app.py` (aplicación principal)
- [ ] Implementar `canvas_view.py` (intersección)
- [ ] Implementar `stats_panel.py` (estadísticas)
- [ ] Implementar `controls_panel.py` (controles)
- [ ] Implementar `event_feed.py` (log de eventos)
- [ ] Agregar animaciones de vehículos
- [ ] Agregar barra de progreso de fase
- [ ] Testing con ambos engines (threading/multiprocessing)

---

**¡Todo listo para implementar el frontend!** 🎨

Tienes acceso completo a todos los datos necesarios a través de `TrafficState`.
