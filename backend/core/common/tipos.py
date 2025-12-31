"""
Tipos y enumeraciones compartidas del sistema de tráfico.
Define los tipos fundamentales usados en todo el dominio.
"""
from enum import Enum, auto


class Via(Enum):
    """Representa las cuatro vías de la intersección."""
    NORTE = auto()
    SUR = auto()
    ESTE = auto()
    OESTE = auto()

    def __str__(self) -> str:
        return self.name


class Color(Enum):
    """Representa los estados posibles de un semáforo."""
    ROJO = auto()
    AMARILLO = auto()
    VERDE = auto()

    def __str__(self) -> str:
        return self.name
