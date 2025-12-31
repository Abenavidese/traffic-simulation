"""
Engine basado en hilos (threading).
Ejecuta semáforos como hilos compartiendo memoria.
"""
import threading
import random
from typing import Dict, List
from time import sleep

from .base import BaseEngine
from ..comms.messages import *
from ...core.common.tipos import Via, Color
from ...core.common.state import TrafficState
from ...core.common.stats import EstadisticasTrafico
from ...core.traffic.semaforo import Semaforo
from ...core.traffic.controlador import ControladorTrafico
from ...core.models.vehiculo import Vehiculo


class ThreadingEngine(BaseEngine):
    """
    Engine basado en threading.
    
    - Cada semáforo puede tener su propio hilo (opcional)
    - Usa locks para sincronización
    - Memoria compartida entre hilos
    """

    def __init__(self, config):
        """
        Inicializa el engine.
        
        Args:
            config: ConfiguracionSimulacion
        """
        self.config = config
        self._running = False
        self._lock = threading.RLock()  # Lock para sincronización
        self._condition = threading.Condition(self._lock)  # Para coordinación
        
        # Componentes del dominio
        self.controlador: ControladorTrafico = None
        self.semaforos: Dict[Via, Semaforo] = {}
        self.stats = EstadisticasTrafico()
        
        # Contador de vehículos
        self._next_vehicle_id = 0
        
        # Sistema de eventos y tránsito
        self._eventos_tick: List[Dict] = []
        self._vehiculos_en_transito: Dict[Via, List[Dict]] = {}

    def start(self) -> None:
        """Inicializa el sistema."""
        with self._lock:
            if self._running:
                return
            
            # Crear controlador
            self.controlador = ControladorTrafico(
                duracion_verde=self.config.duracion_verde,
                duracion_amarillo=self.config.duracion_amarillo,
            )
            
            # Crear semáforos para cada vía
            for via in Via:
                self.semaforos[via] = Semaforo(
                    via=via,
                    capacidad_por_tick=self.config.capacidad_cruce_por_tick,
                )
            
            self._running = True

    def step(self) -> TrafficState:
        """
        Ejecuta un tick de simulación.
        
        Returns:
            Estado actual del sistema
        """
        with self._lock:
            if not self._running:
                raise RuntimeError("Engine no está corriendo. Llama start() primero.")
            
            # Limpiar eventos del tick anterior
            self._eventos_tick = []
            self._vehiculos_en_transito = {}
            
            # Guardar colores anteriores para detectar cambios
            colores_anteriores = {via: sem.color for via, sem in self.semaforos.items()}
            
            # 1. Controlador decide el plan de luces
            plan = self.controlador.avanzar_tick()
            
            # 2. Aplicar colores a semáforos y detectar cambios
            for via, color in plan.items():
                color_anterior = colores_anteriores[via]
                self.semaforos[via].set_color(color)
                
                # Evento: Cambio de semáforo
                if color_anterior != color:
                    self._eventos_tick.append({
                        "tipo": "cambio_semaforo",
                        "via": via.name,
                        "color_anterior": color_anterior.name,
                        "color_nuevo": color.name,
                        "icono": self._get_icono_color(color.name)
                    })
            
            # 3. Simular llegada de vehículos (con eventos)
            self._simular_llegada_vehiculos()
            
            # 4. Ejecutar tick en cada semáforo (con eventos y tránsito)
            for via, semaforo in self.semaforos.items():
                vehiculos_cruzados = semaforo.tick()
                if vehiculos_cruzados:
                    # Registrar estadísticas
                    self.stats.registrar_vehiculos(vehiculos_cruzados, via.name)
                    
                    # Simular vehículos en tránsito (progreso de cruce)
                    for idx, vehiculo in enumerate(vehiculos_cruzados):
                        progreso = (idx + 1) / len(vehiculos_cruzados)
                        if via not in self._vehiculos_en_transito:
                            self._vehiculos_en_transito[via] = []
                        self._vehiculos_en_transito[via].append({
                            "id": vehiculo.id,
                            "progreso": progreso,
                        })
                        
                        # Evento: Vehículo despachado
                        self._eventos_tick.append({
                            "tipo": "vehiculo_despachado",
                            "via": via.name,
                            "vehiculo_id": vehiculo.id,
                            "icono": "🚗✓"
                        })
            
            # 5. Construir estado actual
            return self._construir_estado()

    def _simular_llegada_vehiculos(self) -> None:
        """Simula llegada aleatoria de vehículos a cada vía."""
        for via, semaforo in self.semaforos.items():
            if random.random() < self.config.probabilidad_llegada:
                vehiculo = Vehiculo(id=self._next_vehicle_id)
                self._next_vehicle_id += 1
                semaforo.agregar_vehiculo(vehiculo)
                
                # Evento: Vehículo llegó
                self._eventos_tick.append({
                    "tipo": "vehiculo_llego",
                    "via": via.name,
                    "vehiculo_id": vehiculo.id,
                    "icono": "🚗→"
                })

    def _get_icono_color(self, color: str) -> str:
        """Retorna el emoji correspondiente al color del semáforo."""
        return {"VERDE": "🟢", "AMARILLO": "🟡", "ROJO": "🔴"}.get(color, "⚪")

    def _construir_estado(self) -> TrafficState:
        """Construye el estado actual del sistema."""
        # Estado de luces
        luces = {
            via.name: semaforo.color.name
            for via, semaforo in self.semaforos.items()
        }
        
        # Tamaños de colas
        colas = {
            via.name: semaforo.tamano_cola
            for via, semaforo in self.semaforos.items()
        }
        
        # NUEVO: Detalles de vehículos en colas
        vehiculos_detalle = {
            via.name: semaforo.get_vehiculos_detalle()
            for via, semaforo in self.semaforos.items()
        }
        
        # NUEVO: Timing de fase
        timing_fase = self.controlador.get_timing_fase()
        
        # NUEVO: Configuración
        configuracion = {
            "duracion_verde": self.config.duracion_verde,
            "duracion_amarillo": self.config.duracion_amarillo,
            "capacidad_cruce": self.config.capacidad_cruce_por_tick,
            "probabilidad_llegada": self.config.probabilidad_llegada,
            "intervalo_tick": self.config.intervalo_tick,
        }
        
        # Información del sistema
        import sys
        info_sistema = {
            "motor": "Threading",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "gil_enabled": str(getattr(sys, '_is_gil_enabled', lambda: True)() if hasattr(sys, '_is_gil_enabled') else True),
        }
        
        return TrafficState(
            tick=self.controlador.tick_actual,
            ciclo=self.controlador.ciclo_actual,
            fase=self.controlador.fase_actual,
            luces=luces,
            colas=colas,
            estadisticas=self.stats.get_resumen(),
            info_sistema=info_sistema,
            # Nuevos campos
            vehiculos_detalle=vehiculos_detalle,
            vehiculos_en_transito={via.name: transito for via, transito in self._vehiculos_en_transito.items()},
            eventos_tick={"eventos": self._eventos_tick},
            timing_fase=timing_fase,
            configuracion=configuracion,
        )

    def get_state(self) -> TrafficState:
        """Obtiene el estado actual sin avanzar."""
        with self._lock:
            return self._construir_estado()

    def stop(self) -> None:
        """Detiene el engine."""
        with self._lock:
            self._running = False

    def is_running(self) -> bool:
        """Verifica si está corriendo."""
        with self._lock:
            return self._running

    def __repr__(self) -> str:
        return f"ThreadingEngine(running={self._running}, ciclo={self.controlador.ciclo_actual if self.controlador else 0})"
