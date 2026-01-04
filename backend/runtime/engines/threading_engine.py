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
    
    - Cada semáforo ejecuta en su su propio hilo (threading.Thread)
    - Usa Barrier para sincronización estricta de ticks
    - Memoria compartida protegida por RLock
    """

    def __init__(self, config):
        self.config = config
        self._running = False
        self._lock = threading.RLock()
        
        # Sincronización robusta con Barrier
        # 4 hilos de semáforo + 1 hilo principal = 5
        self._barrier = threading.Barrier(5)
        self._threads: Dict[Via, threading.Thread] = {}
        
        self.controlador: ControladorTrafico = None
        self.semaforos: Dict[Via, Semaforo] = {}
        self.stats = EstadisticasTrafico()
        self._next_vehicle_id = 0
        self._eventos_tick: List[Dict] = []
        self._vehiculos_en_transito: Dict[Via, List[Dict]] = {}

    def _worker_semaforo(self, via: Via):
        semaforo = self.semaforos[via]
        print(f"[THREAD] Iniciado hilo para {via.name}")
        
        while self._running:
            try:
                # 1. Esperar a que el hilo principal inicie el tick
                self._barrier.wait(timeout=5)
                
                # 2. Realizar el trabajo del semáforo
                vehiculos_cruzados = semaforo.tick()
                
                if vehiculos_cruzados:
                    with self._lock:
                        self.stats.registrar_vehiculos(vehiculos_cruzados, via.name)
                        for idx, vehiculo in enumerate(vehiculos_cruzados):
                            progreso = (idx + 1) / len(vehiculos_cruzados)
                            if via not in self._vehiculos_en_transito:
                                self._vehiculos_en_transito[via] = []
                            self._vehiculos_en_transito[via].append({
                                "id": vehiculo.id, "progreso": progreso
                            })
                            self._eventos_tick.append({
                                "tipo": "vehiculo_despachado", "via": via.name,
                                "vehiculo_id": vehiculo.id, "icono": "🚗✓"
                            })

                # 3. Esperar a que todos terminen para cerrar el tick
                self._barrier.wait(timeout=5)
            except threading.BrokenBarrierError:
                if not self._running: break
                self._barrier.reset()
            except Exception as e:
                print(f"[THREAD ERROR] {via.name}: {e}")
                if not self._running: break

    def start(self) -> None:
        with self._lock:
            if self._running: return
            self._running = True
            self.controlador = ControladorTrafico(
                duracion_verde=self.config.duracion_verde,
                duracion_amarillo=self.config.duracion_amarillo,
            )
            for via in Via:
                self.semaforos[via] = Semaforo(via=via, capacidad_por_tick=self.config.capacidad_cruce_por_tick)
                thread = threading.Thread(target=self._worker_semaforo, args=(via,), daemon=True)
                self._threads[via] = thread
                thread.start()
            
            sleep(0.1) # Dar tiempo a los hilos para llegar a su primera barrera

    def step(self) -> TrafficState:
        with self._lock:
            if not self._running: raise RuntimeError("Engine no está corriendo.")
            self._eventos_tick = []
            self._vehiculos_en_transito = {}
            
            plan = self.controlador.avanzar_tick()
            for via, color in plan.items():
                self.semaforos[via].set_color(color)
            
            self._simular_llegada_vehiculos()
            
            try:
                # Sincronizar inicio de tick en hilos
                self._barrier.wait(timeout=2)
                # Sincronizar fin de tick en hilos
                self._barrier.wait(timeout=2)
            except threading.BrokenBarrierError:
                print("[WARNING] Barrera rota, reiniciando...")
                self._barrier.reset()
            
            return self._construir_estado()

    def _simular_llegada_vehiculos(self) -> None:
        for via, semaforo in self.semaforos.items():
            if random.random() < self.config.probabilidad_llegada:
                vehiculo = Vehiculo(id=self._next_vehicle_id)
                self._next_vehicle_id += 1
                semaforo.agregar_vehiculo(vehiculo)
                self._eventos_tick.append({
                    "tipo": "vehiculo_llego", "via": via.name,
                    "vehiculo_id": vehiculo.id, "icono": "🚗→"
                })

    def _construir_estado(self) -> TrafficState:
        import sys
        info_sistema = {
            "motor": "Threading (Barrier Sync)",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
            "gil_enabled": str(getattr(sys, '_is_gil_enabled', lambda: True)() if hasattr(sys, '_is_gil_enabled') else True),
            "hilos_activos": len(self._threads) + 1
        }
        return TrafficState(
            tick=self.controlador.tick_actual,
            ciclo=self.controlador.ciclo_actual,
            fase=self.controlador.fase_actual,
            luces={v.name: s.color.name for v, s in self.semaforos.items()},
            colas={v.name: s.tamano_cola for v, s in self.semaforos.items()},
            estadisticas=self.stats.get_resumen(),
            info_sistema=info_sistema,
            vehiculos_detalle={v.name: s.get_vehiculos_detalle() for v, s in self.semaforos.items()},
            vehiculos_en_transito={v.name: t for v, t in self._vehiculos_en_transito.items()},
            eventos_tick={"eventos": self._eventos_tick},
            timing_fase=self.controlador.get_timing_fase(),
            configuracion={
                "duracion_verde": self.config.duracion_verde,
                "duracion_amarillo": self.config.duracion_amarillo,
                "capacidad_cruce": self.config.capacidad_cruce_por_tick,
                "probabilidad_llegada": self.config.probabilidad_llegada,
                "intervalo_tick": self.config.intervalo_tick,
            }
        )

    def get_state(self) -> TrafficState:
        with self._lock: return self._construir_estado()

    def stop(self) -> None:
        with self._lock:
            self._running = False
            try:
                self._barrier.abort()
            except: pass
            for thread in self._threads.values():
                thread.join(timeout=0.1)

    def is_running(self) -> bool:
        with self._lock: return self._running

    def __repr__(self) -> str:
        return f"ThreadingEngine(running={self._running}, threads={len(self._threads)})"
