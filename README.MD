# 🚦 Simulación de Tráfico Paralelo

> **Práctica de Laboratorio #4 - Computación Paralela**  
> Sistema de control de tráfico vehicular usando paralelismo basado en procesos e hilos en Python 3.13t

[![Python 3.13t](https://img.shields.io/badge/Python-3.13t-blue.svg)](https://www.python.org/)
[![Free-Threading](https://img.shields.io/badge/GIL-Disabled-green.svg)]()
[![Status](https://img.shields.io/badge/Status-Completed-success.svg)]()

---

## 📋 Tabla de Contenidos

- [Descripción](#-descripción)
- [Características](#-características)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Arquitectura](#-arquitectura)
- [Datos Disponibles](#-datos-disponibles)
- [Documentación](#-documentación)
- [Resultados](#-resultados)
- [Desarrollo](#-desarrollo)

---

## 🎯 Descripción

Sistema completo de simulación de tráfico vehicular en una intersección de 4 vías (Norte, Sur, Este, Oeste) que:

- ✅ Implementa **paralelismo basado en hilos** (threading)
- ✅ Implementa **paralelismo basado en procesos** (multiprocessing)
- ✅ Aprovecha **Python 3.13t con GIL deshabilitado**
- ✅ Controla semáforos con sistema de fases seguro
- ✅ Simula llegada y despacho de vehículos
- ✅ Recopila estadísticas en tiempo real
- ✅ Rastrea eventos y vehículos en tránsito
- ⏳ GUI con Tkinter (en desarrollo)

---

## ✨ Características

### **Backend Completo** ✅

#### **Dos Motores de Paralelismo**
1. **Threading Engine** 🧵
   - Memoria compartida eficiente
   - Sincronización con `RLock` + `Condition`
   - Aprovecha múltiples cores con GIL=0

2. **Multiprocessing Engine** 🔄
   - Procesos independientes (1 por semáforo)
   - Comunicación vía `Queue` (IPC)
   - Siempre paralelo (independiente del GIL)

#### **Sistema de Control de Tráfico**
- 🚦 4 semáforos (uno por vía)
- 🔄 Sistema de fases: NS_VERDE → NS_AMARILLO → EW_VERDE → EW_AMARILLO
- ✅ Prevención de colisiones (vías perpendiculares nunca en verde)
- 📊 Estadísticas completas (vehículos, tiempos de espera)

#### **Datos Ricos para Frontend**
- 🚗 Posiciones individuales de vehículos en colas
- 💨 Vehículos en tránsito con progreso (0% → 100%)
- 📋 Log de eventos (llegadas, cruces, cambios de semáforo)
- ⏱️ Timing de fases (countdown, barras de progreso)
- ⚙️ Configuración expuesta

---

## 📦 Requisitos

### **Python 3.13t (Free-Threading)**

```bash
# Verificar versión
py -3.13t --version
# Debe mostrar: Python 3.13.x
```

### **Sistema Operativo**
- ✅ Windows 11 (probado)
- ✅ Windows 10
- ✅ Linux
- ✅ macOS

### **Hardware**
- Mínimo: 4 núcleos lógicos
- Recomendado: 8+ núcleos

---

## 🚀 Instalación

### **1. Clonar Repositorio**

```bash
git clone https://github.com/Abenavidese/traffic-simulation.git
cd traffic-simulation
```

### **2. Verificar Sistema**

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

### **3. No se requieren dependencias adicionales**
El proyecto usa solo la biblioteca estándar de Python.

---

## 🎮 Uso

### **Ejecución Básica**

#### **Threading (Recomendado con GIL=0)**
```bash
py -3.13t -X gil=0 -m backend.app.sim threading
```

#### **Multiprocessing**
```bash
py -3.13t -X gil=0 -m backend.app.sim multiprocessing
```

### **Con Parámetros Personalizados**

```bash
py -3.13t -X gil=0 -m backend.app.sim threading \
  --ciclos 10 \
  --verde 5 \
  --amarillo 2 \
  --intervalo 0.3
```

**Argumentos disponibles:**
- `--ciclos N` - Ciclos mínimos a ejecutar (default: 10)
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

### **Tests de Demostración**

#### **Test de Datos para Frontend**
```bash
py -3.13t -X gil=0 test_nuevos_datos.py
```

#### **Test de Eventos y Tránsito**
```bash
py -3.13t -X gil=0 test_eventos_transito.py
```

---

## 🏗️ Arquitectura

### **Estructura del Proyecto**

```
paralela-multi-hilos/
├── backend/
│   ├── core/              # Lógica de dominio (NO conoce concurrencia)
│   │   ├── common/
│   │   │   ├── tipos.py         # Enums (Via, Color)
│   │   │   ├── state.py         # TrafficState
│   │   │   └── stats.py         # EstadisticasTrafico
│   │   ├── models/
│   │   │   └── vehiculo.py      # Modelo de Vehículo
│   │   └── traffic/
│   │       ├── semaforo.py      # Lógica de semáforo
│   │       └── controlador.py   # Controlador de tráfico
│   │
│   ├── runtime/          # Motores de concurrencia
│   │   ├── engines/
│   │   │   ├── base.py              # Interfaz base
│   │   │   ├── threading_engine.py  # Motor de hilos
│   │   │   └── multiprocessing_engine.py  # Motor de procesos
│   │   └── comms/
│   │       └── messages.py          # Mensajes IPC
│   │
│   ├── app/              # Aplicación
│   │   ├── config.py        # Configuración
│   │   └── sim.py           # Punto de entrada
│   │
│   └── tests/            # Tests unitarios
│       ├── test_controlador.py
│       └── test_semaforo.py
│
├── frontend/             # GUI (en desarrollo)
│   ├── FRONTEND_GUIDE.md    # Guía de implementación
│   └── ui/
│       ├── app.py
│       ├── views/
│       └── render/
│
├── system_info.py       # Verificación del sistema
├── test_nuevos_datos.py # Test de datos
├── test_eventos_transito.py  # Test de eventos
├── README.MD            # Este archivo
└── IMPLEMENTATION.md    # Documentación de implementación
```

### **Principio de Diseño**

> **El dominio NO cambia cuando cambias de hilos a procesos**

- `core/` - Lógica pura, sin imports de threading/multiprocessing
- `runtime/` - Motores intercambiables
- `app/` - Configuración y ejecución

---

## 📊 Datos Disponibles

### **TrafficState - Fuente Única de Datos**

El backend expone **TODO** a través del objeto `TrafficState`:

```python
@dataclass
class TrafficState:
    # Básico
    tick: int                          # Número de tick
    ciclo: int                         # Ciclos completados
    fase: str                          # Fase actual
    luces: Dict[str, str]              # Via → Color
    colas: Dict[str, int]              # Via → Cantidad
    
    # Estadísticas
    estadisticas: Dict[str, any]       # Métricas
    info_sistema: Dict[str, str]       # Info del motor
    
    # Para Animaciones 🎨
    vehiculos_detalle: Dict[str, list]      # Posiciones en cola
    vehiculos_en_transito: Dict[str, list]  # Cruzando (0%-100%)
    eventos_tick: Dict[str, list]           # Log de eventos
    timing_fase: Dict[str, int]             # Countdown
    configuracion: Dict[str, any]           # Parámetros
```

### **Ejemplo de Acceso**

```python
from backend.runtime.engines.threading_engine import ThreadingEngine
from backend.app.config import ConfiguracionSimulacion

# Crear engine
config = ConfiguracionSimulacion()
engine = ThreadingEngine(config)
engine.start()

# Ejecutar tick
state = engine.step()

# Acceder a datos
print(f"Tick: {state.tick}")
print(f"Luces: {state.luces}")
print(f"Vehículos en NORTE: {state.vehiculos_detalle['NORTE']}")
print(f"Eventos: {state.eventos_tick['eventos']}")
```

### **Guía Completa de Datos**

Para documentación detallada de todos los campos disponibles, ver:
- 📖 [`frontend/FRONTEND_GUIDE.md`](frontend/FRONTEND_GUIDE.md) - Guía de implementación frontend

---

## 📚 Documentación

### **Documentos Principales**

| Documento | Descripción |
|-----------|-------------|
| [`IMPLEMENTATION.md`](IMPLEMENTATION.md) | Guía de implementación completa |
| [`frontend/FRONTEND_GUIDE.md`](frontend/FRONTEND_GUIDE.md) | Guía de datos para frontend |

### **Documentos Técnicos**

Disponibles en `.gemini/antigravity/brain/[conversation-id]/`:
- `walkthrough.md` - Resumen de implementación
- `analisis_comparativo.md` - Threading vs Multiprocessing
- `analisis_datos_frontend.md` - Análisis de datos para GUI
- `resumen_mejoras_backend.md` - Resumen de mejoras
- `eventos_y_transito_completado.md` - Sistema de eventos

---

## 🧪 Resultados

### **Threading Engine (GIL=0)**

```
✅ Ciclos completados: 10
✅ Ticks ejecutados: 140
✅ Vehículos cruzados: 336
⏱️ Tiempo total: 28.10s
🚀 Rendimiento: 4.98 ticks/segundo
```

### **Multiprocessing Engine**

```
✅ Ciclos completados: 10
✅ Ticks ejecutados: 140
✅ Vehículos cruzados: 333
⏱️ Tiempo total: 28.34s
🚀 Rendimiento: 4.94 ticks/segundo
```

### **Conclusión**

Con **Python 3.13t y GIL deshabilitado**:
- ✅ Threading es ~0.8% más rápido
- ✅ Ambos funcionan correctamente
- ✅ Sin colisiones detectadas
- ✅ Threading más simple de implementar

---

## 👨‍💻 Desarrollo

### **Estructura de Clases Core**

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
```

#### **`semaforo.py`** - Semáforo
```python
class Semaforo:
    def tick(self) -> List[Vehiculo]:
        """Despacha vehículos si está en VERDE"""
    
    def get_vehiculos_detalle(self) -> list:
        """Retorna lista detallada para frontend"""
```

#### **`controlador.py`** - Controlador
```python
class ControladorTrafico:
    def avanzar_tick(self) -> Dict[Via, Color]:
        """Avanza fase y retorna plan de colores"""
    
    def get_timing_fase(self) -> dict:
        """Info de timing para countdown"""
```

### **Tests Unitarios**

```bash
# Instalar pytest
pip install pytest

# Ejecutar tests
py -3.13t -m pytest backend/tests/ -v
```

### **Sistema de Eventos**

El sistema rastrea 3 tipos de eventos:

1. **Llegadas** 🚗→
```python
{"tipo": "vehiculo_llego", "via": "NORTE", "vehiculo_id": 15}
```

2. **Cruces** 🚗✓
```python
{"tipo": "vehiculo_despachado", "via": "SUR", "vehiculo_id": 12}
```

3. **Cambios de Semáforo** 🟢🟡🔴
```python
{"tipo": "cambio_semaforo", "via": "ESTE", 
 "color_anterior": "VERDE", "color_nuevo": "AMARILLO"}
```

---

## 🎯 Características Implementadas

| Característica | Estado | Notas |
|----------------|--------|-------|
| Core Domain | ✅ | Todas las entidades |
| Threading Engine | ✅ | Con sincronización RLock |
| Multiprocessing Engine | ✅ | Con Queue IPC |
| Control de Fases | ✅ | Sin colisiones |
| Estadísticas | ✅ | Completas |
| Sistema de Eventos | ✅ | Log completo |
| Vehículos en Tránsito | ✅ | Con progreso |
| Timing de Fases | ✅ | Countdown |
| Tests Unitarios | ✅ | Core completos |
| Info del Sistema | ✅ | Python, GIL, CPU |
| GUI Tkinter | ⏳ | En desarrollo |
| Informe Final | ⏳ | Pendiente |

---

## 🔧 Configuración

### **Parámetros Disponibles**

```python
# En backend/app/config.py
ConfiguracionSimulacion(
    # Semáforos
    duracion_verde=5,              # Ticks en verde
    duracion_amarillo=2,           # Ticks en amarillo
    capacidad_cruce_por_tick=2,    # Vehículos/tick
    
    # Simulación
    probabilidad_llegada=0.6,      # 60% por tick
    intervalo_tick=0.3,            # 300ms entre ticks
    ciclos_minimos=10,             # Mínimo a simular
    
    # Motor
    modo="threading",              # "threading" o "multiprocessing"
)
```

---

## 📈 Comparación de Rendimiento

| Aspecto | Threading | Multiprocessing |
|---------|-----------|-----------------|
| **Rendimiento** | 4.98 t/s | 4.94 t/s |
| **Complejidad** | Baja | Alta |
| **Memoria** | Compartida | Separada |
| **Escalabilidad** | Media* | Alta |
| **Debugging** | Fácil | Difícil |
| **Portabilidad** | Media** | Alta |

*Con GIL=0  
**Requiere Python 3.13t

---

##🤝 Contribuciones

Este es un proyecto académico de la **Universidad de Cuenca**.

**Autor:** Computación Paralela - Práctica #4  
**Instructor:** Ing. Gabriel León Paredes, PhD.

---

## 📄 Licencia

Proyecto académico - Universidad de Cuenca

---

## 🚀 Próximos Pasos

1. ✅ Backend completo
2. ⏳ Implementar GUI con Tkinter
3. ⏳ Ejecutar simulación completa (10+ ciclos)
4. ⏳ Análisis comparativo detallado
5. ⏳ Generar informe técnico
6. ⏳ Documentar resultados

---

## 📞 Soporte

Para preguntas o problemas:
1. Revisar [`IMPLEMENTATION.md`](IMPLEMENTATION.md)
2. Revisar [`frontend/FRONTEND_GUIDE.md`](frontend/FRONTEND_GUIDE.md)
3. Verificar con `system_info.py`
4. Abrir un issue en GitHub

---

**Hecho con ❤️ y Python 3.13t (free-threading)**

**Repositorio:** [github.com/Abenavidese/traffic-simulation](https://github.com/Abenavidese/traffic-simulation)