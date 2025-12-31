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
            
            # 1. Controlador decide el plan de luces
            plan = self.controlador.avanzar_tick()
            
            # 2. Aplicar colores a semáforos
            for via, color in plan.items():
                self.semaforos[via].set_color(color)
            
            # 3. Simular llegada de vehículos
            self._simular_llegada_vehiculos()
            
            # 4. Ejecutar tick en cada semáforo
            for via, semaforo in self.semaforos.items():
                vehiculos_cruzados = semaforo.tick()
                if vehiculos_cruzados:
                    self.stats.registrar_vehiculos(vehiculos_cruzados, via.name)
            
            # 5. Construir estado actual
            return self._construir_estado()

    def _simular_llegada_vehiculos(self) -> None:
        """Simula llegada aleatoria de vehículos a cada vía."""
        for via, semaforo in self.semaforos.items():
            if random.random() < self.config.probabilidad_llegada:
                vehiculo = Vehiculo(id=self._next_vehicle_id)
                self._next_vehicle_id += 1
                semaforo.agregar_vehiculo(vehiculo)

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
