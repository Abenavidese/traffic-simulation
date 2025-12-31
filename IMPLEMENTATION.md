# 🚦 Simulación de Tráfico Paralelo

> **Práctica de Laboratorio #4 - Computación Paralela**  
> Sistema de control de tráfico vehicular usando paralelismo basado en procesos e hilos

[![Python 3.13t](https://img.shields.io/badge/Python-3.13t-blue.svg)](https://www.python.org/)
[![Free-Threading](https://img.shields.io/badge/GIL-Disabled-green.svg)]()
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)]()

---

## 📋 Tabla de Contenidos

- [Objetivos](#-objetivos)
- [Características](#-características)
- [Arquitectura](#-arquitectura)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Componentes](#-componentes)
- [Cómo Funciona](#-cómo-funciona)
- [Resultados](#-resultados)
- [Próximos Pasos](#-próximos-pasos)

---

## 🎯 Objetivos

- ✅ Diseñar e implementar una aplicación concurrente que simule un sistema urbano de control de tráfico vehicular
- ✅ Aplicar paralelismo basado en procesos e hilos en Python
- ✅ Analizar diferencias de rendimiento y sincronización entre `threading` y `multiprocessing`
- ✅ Considerar el impacto del Global Interpreter Lock (GIL)
- ✅ Utilizar mecanismos de sincronización (Lock, Queue, Barrier, etc.)
- ⏳ Incorporar interfaz gráfica (GUI) con Tkinter

---

## ✨ Características

### **Backend Completo** ✅
- 🧵 Motor de **Threading** con GIL deshabilitado (aprovecha múltiples cores)
- 🔄 Motor de **Multiprocessing** con procesos independientes
- 🚗 Simulación de vehículos con llegadas aleatorias
- 🚦 Sistema de fases para evitar colisiones
- 📊 Estadísticas en tiempo real (vehículos, tiempos de espera)
- 💻 Detección automática del sistema (Python, GIL, CPU)

### **Arquitectura Limpia**
- 📦 Separación estricta: Dominio ↔ Runtime ↔ App
- 🔧 Configuración centralizada
- 🧪 Tests unitarios
- 📝 Documentación completa

---

## 🏗️ Arquitectura

```
backend/
├── core/           # Lógica de dominio (NO conoce concurrencia)
│   ├── common/     # Tipos, estado, estadísticas
│   ├── models/     # Vehículo
│   └── traffic/    # Semáforo, Controlador
│
├── runtime/        # Motores de concurrencia
│   ├── engines/    # Threading, Multiprocessing, Base
│   └── comms/      # Mensajes IPC
│
└── app/            # Aplicación
    ├── config.py   # Configuración
    └── sim.py      # Punto de entrada
```

### **Principio de Diseño**
> **El dominio NO cambia cuando cambias de hilos a procesos**

---

## 📦 Instalación

### **Requisitos**
- Python 3.13t (free-threading build)
- Windows/Linux/macOS

### **Verificar Python 3.13t**
```bash
py -3.13t --version
# Debe mostrar: Python 3.13.x
```

### **Clonar Repositorio**
```bash
git clone https://github.com/Abenavidese/traffic-simulation.git
cd traffic-simulation
```

### **Verificar Sistema**
```bash
py -3.13t -X gil=0 system_info.py
```

**Salida esperada:**
```
🐍 Python:
  Versión: 3.13.11
  Build: 3.13t (free-threading)

🔒 Global Interpreter Lock (GIL):
  Estado: DESHABILITADO ✓
  Free-threading disponible: Sí

💻 Hardware:
  Núcleos (lógicos): 24
```

---

## 🚀 Uso

### **Ejecución Básica**

#### **Threading (con GIL deshabilitado)**
```bash
py -3.13t -X gil=0 -m backend.app.sim threading
```

#### **Multiprocessing**
```bash
py -3.13t -X gil=0 -m backend.app.sim multiprocessing
```

### **Parámetros Personalizados**

```bash
py -3.13t -X gil=0 -m backend.app.sim threading \
  --ciclos 10 \
  --verde 5 \
  --amarillo 2 \
  --intervalo 0.3
```

**Argumentos disponibles:**
- `--ciclos N` - Número mínimo de ciclos a ejecutar (default: 10)
- `--verde N` - Duración de luz verde en ticks (default: 5)
- `--amarillo N` - Duración de luz amarilla en ticks (default: 2)
- `--intervalo S` - Tiempo entre ticks en segundos (default: 0.3)

### **Salida de Ejemplo**

```
======================================================================
Tick: 5 | Ciclo: 0 | Fase: NS_AMARILLO
======================================================================

🚦 Semáforos:
  🟡 NORTE  - AMARILLO  | Cola:   1 vehículos
  🟡 SUR    - AMARILLO  | Cola:   1 vehículos
  🔴 ESTE   - ROJO      | Cola:   3 vehículos
  🔴 OESTE  - ROJO      | Cola:   2 vehículos

📊 Estadísticas:
  Total vehículos cruzados: 6
  Tiempo espera promedio: 0.000s
  Vehículos por vía:
    NORTE: 3
    SUR: 3

💻 Sistema:
  motor: Threading
  python_version: 3.13.11
  gil_enabled: False
```

---

## 🔧 Componentes

### **1. Core Domain (Lógica Pura)**

#### **`tipos.py`** - Enumeraciones
```python
class Via(Enum):
    NORTE, SUR, ESTE, OESTE

class Color(Enum):
    ROJO, AMARILLO, VERDE
```

#### **`vehiculo.py`** - Modelo de Vehículo
```python
@dataclass
class Vehiculo:
    id: int
    tiempo_llegada: float
    tiempo_inicio_espera: Optional[float]
    tiempo_salida: Optional[float]
    
    @property
    def tiempo_espera_total(self) -> float
```

#### **`semaforo.py`** - Semáforo
```python
class Semaforo:
    def tick(self) -> List[Vehiculo]:
        """
        - VERDE: Despacha hasta N vehículos
        - ROJO/AMARILLO: No despacha
        """
```

#### **`controlador.py`** - Controlador de Tráfico
```python
class ControladorTrafico:
    def avanzar_tick(self) -> Dict[Via, Color]:
        """
        Fases:
        NS_VERDE → NS_AMARILLO → EW_VERDE → EW_AMARILLO
        """
```

#### **`stats.py`** - Estadísticas
```python
class EstadisticasTrafico:
    - total_vehiculos
    - tiempo_espera_promedio
    - vehiculos_por_via
```

#### **`state.py`** - Estado del Sistema
```python
@dataclass
class TrafficState:
    tick: int
    ciclo: int
    fase: str
    luces: Dict[str, str]
    colas: Dict[str, int]
    estadisticas: dict
    info_sistema: dict
```

---

### **2. Runtime (Motores de Concurrencia)**

#### **`base.py`** - Interfaz Base
```python
class BaseEngine(ABC):
    @abstractmethod
    def start(self) -> None
    
    @abstractmethod
    def step(self) -> TrafficState
    
    @abstractmethod
    def stop(self) -> None
```

#### **`threading_engine.py`** - Motor de Hilos 🧵

**Características:**
- ✅ Memoria compartida
- ✅ Sincronización con `RLock` + `Condition`
- ✅ Aprovecha múltiples cores con GIL=0

**Flujo:**
```python
1. Controlador decide plan
2. Aplica colores (memoria compartida)
3. Simula llegadas
4. Ejecuta ticks
5. Recopila estadísticas
```

#### **`multiprocessing_engine.py`** - Motor de Procesos 🔄

**Características:**
- ✅ Procesos independientes (1 por semáforo)
- ✅ Comunicación vía `Queue` (IPC)
- ✅ Sistema de comandos/respuestas

**Arquitectura:**
```
Proceso Principal
  ├─→ Queue → Worker Semáforo Norte
  ├─→ Queue → Worker Semáforo Sur
  ├─→ Queue → Worker Semáforo Este
  └─→ Queue → Worker Semáforo Oeste
       │
       └← Queue Respuestas
```

**Comandos:**
- `CAMBIAR_COLOR` - Actualizar color
- `AGREGAR_VEHICULO` - Añadir vehículo
- `TICK` - Ejecutar tick
- `OBTENER_ESTADO` - Solicitar estado
- `DETENER` - Finalizar worker

---

### **3. App (Aplicación)**

#### **`config.py`** - Configuración
```python
@dataclass
class ConfiguracionSimulacion:
    duracion_verde: int = 5
    duracion_amarillo: int = 2
    capacidad_cruce_por_tick: int = 2
    probabilidad_llegada: float = 0.6
    ciclos_minimos: int = 10
    intervalo_tick: float = 0.3
    modo: str = "threading"
```

#### **`sim.py`** - Punto de Entrada
- CLI con `argparse`
- Visualización en consola
- Estadísticas en tiempo real
- Resumen final con métricas

---

## 🔍 Cómo Funciona

### **Ciclo de Simulación (1 Tick)**

```mermaid
graph TD
    A[Controlador decide plan] --> B{Motor?}
    B -->|Threading| C1[Aplica colores en memoria]
    B -->|Multiprocessing| C2[Envía comandos via Queue]
    C1 --> D[Simula llegada vehículos]
    C2 --> D
    D --> E[Semáforos ejecutan tick]
    E --> F[Recopila estadísticas]
    F --> G[Construye TrafficState]
```

### **Sistema de Fases**

```
Tick 0-4:   NS_VERDE    (Norte/Sur 🟢, Este/Oeste 🔴)
Tick 5-6:   NS_AMARILLO (Norte/Sur 🟡, Este/Oeste 🔴)
Tick 7-11:  EW_VERDE    (Este/Oeste 🟢, Norte/Sur 🔴)
Tick 12-13: EW_AMARILLO (Este/Oeste 🟡, Norte/Sur 🔴)
Tick 14:    → Ciclo completo ✓ → Vuelve a NS_VERDE
```

**Garantía:** Nunca hay vías perpendiculares en verde simultáneamente.

---

## 📊 Resultados

### **Threading Engine (GIL=0)**
```
✅ Ciclos completados: 2
✅ Ticks ejecutados: 28
✅ Vehículos cruzados: 60
✅ Tiempo total: 4.22s
✅ Ticks/segundo: 6.64
✅ GIL: Deshabilitado
✅ Cores usados: 24
```

### **Multiprocessing Engine**
```
✅ Ciclos completados: 2
✅ Ticks ejecutados: 28
✅ Vehículos cruzados: 53
✅ Tiempo total: 4.32s
✅ Ticks/segundo: 6.49
✅ Procesos activos: 4
```

### **Observaciones**
- ✅ Ambos motores funcionan correctamente
- ✅ Rendimiento similar (threading ligeramente más rápido con GIL=0)
- ✅ Sin colisiones detectadas
- ✅ Estadísticas coherentes

---

## 🎨 Integración Frontend-Backend

### **Arquitectura de Integración**

El frontend **NO ejecuta** el backend como comando externo. En lugar de eso, **importa y usa los engines directamente**.

#### **❌ NO Hacer Esto:**
```bash
# NO ejecutar como subprocess
subprocess.run(["py", "-3.13t", "-X", "gil=0", "-m", "backend.app.sim", "threading"])
```

#### **✅ Hacer Esto:**
```python
# SÍ importar directamente
from backend.runtime.engines.threading_engine import ThreadingEngine

engine = ThreadingEngine(config)
engine.start()
state = engine.step()  # Recibir datos
```

---

### **Ejemplo Completo de Integración**

```python
# frontend/ui/app.py
import tkinter as tk
from backend.app.config import ConfiguracionSimulacion
from backend.runtime.engines.threading_engine import ThreadingEngine
from backend.runtime.engines.multiprocessing_engine import MultiprocessingEngine

class TrafficGUI:
    def __init__(self, root):
        self.root = root
        self.engine = None
        self.running = False
        
        # Botones de control
        self.btn_threading = tk.Button(
            root, 
            text="▶️ Threading", 
            command=self.start_threading,
            font=("Arial", 12)
        )
        self.btn_threading.pack(pady=5)
        
        self.btn_multiproc = tk.Button(
            root,
            text="▶️ Multiprocessing",
            command=self.start_multiprocessing,
            font=("Arial", 12)
        )
        self.btn_multiproc.pack(pady=5)
        
        self.btn_stop = tk.Button(
            root,
            text="⏹️ Detener",
            command=self.stop,
            state='disabled',
            font=("Arial", 12)
        )
        self.btn_stop.pack(pady=5)
        
        # Canvas para visualización
        self.canvas = tk.Canvas(root, width=600, height=600, bg="#1E1E1E")
        self.canvas.pack()
        
        # Labels de estadísticas
        self.label_stats = tk.Label(root, text="", font=("Arial", 10))
        self.label_stats.pack()
    
    def start_threading(self):
        """Iniciar simulación con Threading"""
        config = ConfiguracionSimulacion(
            duracion_verde=5,
            duracion_amarillo=2,
            intervalo_tick=0.3,
            ciclos_minimos=100
        )
        
        # Crear y arrancar engine
        self.engine = ThreadingEngine(config)
        self.engine.start()
        
        # Actualizar UI
        self.running = True
        self.btn_threading.config(state='disabled')
        self.btn_multiproc.config(state='disabled')
        self.btn_stop.config(state='normal')
        
        # Empezar loop de actualización
        self.update_loop()
    
    def start_multiprocessing(self):
        """Iniciar simulación con Multiprocessing"""
        config = ConfiguracionSimulacion(
            duracion_verde=5,
            duracion_amarillo=2,
            intervalo_tick=0.3,
            ciclos_minimos=100
        )
        
        self.engine = MultiprocessingEngine(config)
        self.engine.start()
        
        self.running = True
        self.btn_threading.config(state='disabled')
        self.btn_multiproc.config(state='disabled')
        self.btn_stop.config(state='normal')
        
        self.update_loop()
    
    def update_loop(self):
        """Loop principal - ejecuta cada tick"""
        if not self.running:
            return
        
        # ════════════════════════════════════════════
        # AQUÍ RECIBES TODOS LOS DATOS ← IMPORTANTE
        # ════════════════════════════════════════════
        state = self.engine.step()
        
        # Renderizar en canvas
        self.render(state)
        
        # Actualizar estadísticas
        self.update_stats(state)
        
        # Siguiente tick
        interval_ms = int(state.configuracion['intervalo_tick'] * 1000)
        self.root.after(interval_ms, self.update_loop)
    
    def render(self, state):
        """Dibuja la simulación basado en el estado"""
        self.canvas.delete("all")
        
        # Dibujar carreteras
        self.draw_roads()
        
        # Dibujar semáforos con colores actuales
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
            self.canvas.create_oval(
                x, y, x+40, y+40,
                fill=COLORS[color],
                outline="white",
                width=2
            )
            self.canvas.create_text(
                x+20, y-15,
                text=via,
                fill="white",
                font=("Arial", 10, "bold")
            )
        
        # Dibujar vehículos en colas
        QUEUE_POSITIONS = {
            "NORTE": (300, 150),
            "SUR": (300, 450),
            "ESTE": (450, 300),
            "OESTE": (150, 300)
        }
        
        for via, vehiculos in state.vehiculos_detalle.items():
            base_x, base_y = QUEUE_POSITIONS[via]
            
            for v in vehiculos[:5]:  # Mostrar máximo 5
                offset = v['posicion'] * 20
                
                if via == "NORTE":
                    x, y = base_x, base_y - offset
                elif via == "SUR":
                    x, y = base_x, base_y + offset
                elif via == "ESTE":
                    x, y = base_x + offset, base_y
                else:  # OESTE
                    x, y = base_x - offset, base_y
                
                # Dibujar vehículo
                self.canvas.create_rectangle(
                    x-8, y-5, x+8, y+5,
                    fill="#007ACC",
                    outline="white"
                )
        
        # Dibujar vehículos en tránsito
        for via, vehiculos in state.vehiculos_en_transito.items():
            for v in vehiculos:
                # Calcular posición según progreso
                # (implementar interpolación)
                pass
        
        # Mostrar eventos recientes
        eventos = state.eventos_tick.get("eventos", [])
        y_offset = 50
        for evento in eventos[:5]:  # Últimos 5
            self.canvas.create_text(
                10, y_offset,
                text=f"{evento['icono']} {self.format_event(evento)}",
                fill="lightgreen",
                anchor='w',
                font=("Arial", 9)
            )
            y_offset += 20
    
    def draw_roads(self):
        """Dibuja las carreteras"""
        # Carretera horizontal
        self.canvas.create_rectangle(
            0, 250, 600, 350,
            fill="#333333",
            outline=""
        )
        # Carretera vertical
        self.canvas.create_rectangle(
            250, 0, 350, 600,
            fill="#333333",
            outline=""
        )
        # Líneas centrales
        for i in range(0, 600, 40):
            self.canvas.create_rectangle(
                i, 295, i+20, 305,
                fill="yellow"
            )
            self.canvas.create_rectangle(
                295, i, 305, i+20,
                fill="yellow"
            )
    
    def update_stats(self, state):
        """Actualiza el panel de estadísticas"""
        stats = state.estadisticas
        text = (
            f"Tick: {state.tick} | Ciclo: {state.ciclo} | Fase: {state.fase}\n"
            f"Total: {stats['total_vehiculos']} | "
            f"Espera Promedio: {stats['tiempo_espera_promedio']:.2f}s\n"
            f"Motor: {state.info_sistema['motor']} | "
            f"GIL: {state.info_sistema['gil_enabled']}"
        )
        self.label_stats.config(text=text)
    
    def format_event(self, evento):
        """Formatea evento para mostrar"""
        if evento['tipo'] == 'vehiculo_llego':
            return f"Veh #{evento['vehiculo_id']} → {evento['via']}"
        elif evento['tipo'] == 'vehiculo_despachado':
            return f"Veh #{evento['vehiculo_id']} cruzó {evento['via']}"
        else:
            return f"{evento['via']}: {evento['color_anterior']}→{evento['color_nuevo']}"
    
    def stop(self):
        """Detener simulación"""
        self.running = False
        if self.engine:
            self.engine.stop()
        self.btn_threading.config(state='normal')
        self.btn_multiproc.config(state='normal')
        self.btn_stop.config(state='disabled')
    
    def on_close(self):
        """Cleanup al cerrar ventana"""
        self.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("🚦 Simulación de Tráfico Paralelo")
    root.geometry("620x800")
    app = TrafficGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
```

---

### **Flujo de Ejecución**

```
1. Usuario abre GUI
   ↓
2. Usuario presiona "▶️ Threading" o "▶️ Multiprocessing"
   ↓
3. GUI crea el engine correspondiente
   engine = ThreadingEngine(config)
   ↓
4. GUI inicia el engine
   engine.start()
   ↓
5. GUI entra en update_loop()
   ↓
6. Cada tick:
   │
   ├─→ state = engine.step()  ← Ejecutar 1 tick del backend
   │
   ├─→ render(state)          ← Dibujar en canvas
   │
   ├─→ update_stats(state)    ← Actualizar estadísticas
   │
   └─→ root.after(interval)   ← Esperar y repetir
```

---

### **Ventajas de Este Enfoque**

| Ventaja | Descripción |
|---------|-------------|
| ✅ **Simplicidad** | Solo importas el engine, no necesitas subprocess |
| ✅ **Rapidez** | Sin overhead de comunicación entre procesos |
| ✅ **Directo** | Recibes objetos Python nativos (TrafficState) |
| ✅ **Fácil Debug** | Todo en el mismo proceso (para threading) |
| ✅ **Type Safety** | Los IDEs autocompletarán los campos |
| ✅ **Sin Parsing** | No necesitas parsear JSON o texto |

---

### **Datos Disponibles en Cada Tick**

Cada vez que llamas `state = engine.step()`, recibes:

```python
state.tick                    # int: Número de tick
state.ciclo                   # int: Ciclo actual
state.fase                    # str: Fase actual
state.luces                   # Dict: Via → Color
state.colas                   # Dict: Via → Cantidad
state.vehiculos_detalle       # Dict: Via → [Vehiculos]
state.vehiculos_en_transito   # Dict: Via → [Progreso]
state.eventos_tick            # Dict: {"eventos": [...]}
state.timing_fase             # Dict: Countdown info
state.configuracion           # Dict: Parámetros
state.estadisticas            # Dict: Métricas
state.info_sistema            # Dict: Info motor
```

**Ver documentación completa:** [`frontend/FRONTEND_GUIDE.md`](frontend/FRONTEND_GUIDE.md)

---

## ✅ Estado del Proyecto

| Componente | Estado | Notas |
|------------|--------|-------|
| Core Domain | ✅ | Todas las entidades implementadas |
| Threading Engine | ✅ | Con sincronización RLock |
| Multiprocessing Engine | ✅ | Con comunicación Queue IPC |
| Configuración | ✅ | Parámetros centralizados |
| CLI | ✅ | Con visualización en consola |
| Detección Sistema | ✅ | Python, GIL, CPU |
| Tests Unitarios | ⏳ | Creados, pendiente pytest |
| GUI Tkinter | ⏳ | Estructura creada |
| Informe Técnico | ⏳ | Pendiente |

---

## 🚀 Próximos Pasos

1. **Instalar pytest** y ejecutar tests unitarios
   ```bash
   pip install pytest
   py -3.13t -m pytest backend/tests/ -v
   ```

2. **Implementar GUI con Tkinter**
   - Visualización gráfica de la intersección
   - Panel de estadísticas
   - Panel de controles

3. **Ejecutar simulación completa** (10+ ciclos)
   ```bash
   py -3.13t -X gil=0 -m backend.app.sim threading --ciclos 10
   py -3.13t -X gil=0 -m backend.app.sim multiprocessing --ciclos 10
   ```

4. **Generar análisis comparativo**
   - Rendimiento (ticks/segundo)
   - Uso de CPU
   - Complejidad de implementación
   - Ventajas/desventajas

5. **Documentar resultados**
   - Capturas de pantalla
   - Gráficos de rendimiento
   - Conclusiones

---

## 📚 Referencias

- [README.MD](README.MD) - Especificación arquitectural original
- [system_info.py](system_info.py) - Script de verificación del sistema
- [Tests](backend/tests/) - Tests unitarios

---

## 👥 Autor

**Computación Paralela - Práctica #4**  
Universidad de Cuenca  
Ing. Gabriel León Paredes, PhD.

---

## 📄 Licencia

Este proyecto es parte de una práctica académica.

---

## 🤝 Contribuciones

Si encuentras bugs o mejoras, abre un issue o pull request en el repositorio.

**Repositorio:** [github.com/Abenavidese/traffic-simulation](https://github.com/Abenavidese/traffic-simulation)

---

**Hecho con ❤️ y Python 3.13t (free-threading)**
