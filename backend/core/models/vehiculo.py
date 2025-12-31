"""
Modelo de vehículo individual.
Responsable de rastrear tiempos de llegada, espera y salida.
"""
from dataclasses import dataclass, field
from time import time
from typing import Optional


@dataclass
class Vehiculo:
    """
    Representa un vehículo en el sistema de tráfico.
    
    Atributos:
        id: Identificador único del vehículo
        tiempo_llegada: Timestamp cuando el vehículo llegó a la cola
        tiempo_inicio_espera: Timestamp cuando comenzó a esperar
        tiempo_salida: Timestamp cuando el vehículo cruzó la intersección
    """
    id: int
    tiempo_llegada: float = field(default_factory=time)
    tiempo_inicio_espera: Optional[float] = None
    tiempo_salida: Optional[float] = None

    def marcar_inicio_espera(self) -> None:
        """Marca el momento en que el vehículo comienza a esperar."""
        if self.tiempo_inicio_espera is None:
            self.tiempo_inicio_espera = time()

    def marcar_salida(self) -> None:
        """Marca el momento en que el vehículo cruza la intersección."""
        if self.tiempo_salida is None:
            self.tiempo_salida = time()

    @property
    def tiempo_espera_total(self) -> float:
        """
        Calcula el tiempo total de espera del vehículo.
        
        Returns:
            Tiempo en segundos. 0 si no ha comenzado a esperar.
        """
        if self.tiempo_inicio_espera is None:
            return 0.0
        
        tiempo_fin = self.tiempo_salida if self.tiempo_salida else time()
        return tiempo_fin - self.tiempo_inicio_espera

    def __repr__(self) -> str:
        estado = "esperando" if self.tiempo_salida is None else "cruzó"
        return f"Vehiculo(id={self.id}, {estado})"
