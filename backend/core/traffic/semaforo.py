"""
Semáforo individual para una vía.
Responsable de mantener cola de vehículos y despachar según el color.
"""
from collections import deque
from typing import List

from ..common.tipos import Color, Via
from ..models.vehiculo import Vehiculo


class Semaforo:
    """
    Representa un semáforo en una intersección.
    
    Gestiona la cola de vehículos y el despacho según el estado del semáforo.
    No contiene lógica de concurrencia - solo lógica de dominio.
    """

    def __init__(self, via: Via, capacidad_por_tick: int = 2):
        """
        Inicializa el semáforo.
        
        Args:
            via: Dirección de la vía (Norte, Sur, Este, Oeste)
            capacidad_por_tick: Número máximo de vehículos que pueden cruzar por tick
        """
        self.via = via
        self.color = Color.ROJO
        self.cola: deque[Vehiculo] = deque()
        self.capacidad_por_tick = capacidad_por_tick
        self._vehiculos_cruzados_total = 0

    def set_color(self, color: Color) -> None:
        """Cambia el color del semáforo."""
        self.color = color

    def agregar_vehiculo(self, vehiculo: Vehiculo) -> None:
        """
        Agrega un vehículo a la cola.
        
        Args:
            vehiculo: Vehículo a agregar
        """
        vehiculo.marcar_inicio_espera()
        self.cola.append(vehiculo)

    def tick(self) -> List[Vehiculo]:
        """
        Ejecuta un tick de simulación.
        
        - Si está en VERDE: despacha hasta N vehículos
        - Si está en ROJO o AMARILLO: no despacha ninguno
        
        Returns:
            Lista de vehículos que cruzaron en este tick
        """
        vehiculos_despachados = []

        if self.color == Color.VERDE:
            # Despachar hasta la capacidad permitida
            for _ in range(min(self.capacidad_por_tick, len(self.cola))):
                vehiculo = self.cola.popleft()
                vehiculo.marcar_salida()
                vehiculos_despachados.append(vehiculo)
                self._vehiculos_cruzados_total += 1

        return vehiculos_despachados

    @property
    def tamano_cola(self) -> int:
        """Retorna el tamaño actual de la cola."""
        return len(self.cola)

    @property
    def vehiculos_cruzados_total(self) -> int:
        """Retorna el total de vehículos que han cruzado."""
        return self._vehiculos_cruzados_total

    def get_estado(self) -> dict:
        """
        Retorna el estado actual del semáforo.
        
        Returns:
            Diccionario con el estado del semáforo
        """
        return {
            "via": self.via.name,
            "color": self.color.name,
            "tamano_cola": self.tamano_cola,
            "vehiculos_cruzados": self._vehiculos_cruzados_total,
        }

    def __repr__(self) -> str:
        return f"Semaforo({self.via.name}, {self.color.name}, cola={self.tamano_cola})"
