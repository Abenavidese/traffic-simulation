"""
Estructuras de mensajes para comunicación entre procesos.
Usado por el multiprocessing engine.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from enum import Enum, auto


class TipoComando(Enum):
    """Tipos de comandos que se pueden enviar a procesos."""
    CAMBIAR_COLOR = auto()
    AGREGAR_VEHICULO = auto()
    TICK = auto()
    DETENER = auto()
    OBTENER_ESTADO = auto()


class TipoRespuesta(Enum):
    """Tipos de respuestas desde procesos."""
    VEHICULOS_DESPACHADOS = auto()
    ESTADO_SEMAFORO = auto()
    ACK = auto()
    ERROR = auto()


@dataclass
class Comando:
    """
    Comando enviado a un proceso de semáforo.
    
    Atributos:
        tipo: Tipo de comando
        via: Vía del semáforo destino
        payload: Datos adicionales (color, vehículo, etc.)
    """
    tipo: TipoComando
    via: str
    payload: Optional[any] = None

    def __repr__(self) -> str:
        return f"Comando({self.tipo.name}, via={self.via})"


@dataclass
class Respuesta:
    """
    Respuesta desde un proceso de semáforo.
    
    Atributos:
        tipo: Tipo de respuesta
        via: Vía que responde
        payload: Datos de respuesta
        exito: Si la operación fue exitosa
    """
    tipo: TipoRespuesta
    via: str
    payload: Optional[any] = None
    exito: bool = True

    def __repr__(self) -> str:
        return f"Respuesta({self.tipo.name}, via={self.via}, exito={self.exito})"


@dataclass
class EstadoSemaforoMsg:
    """
    Mensaje con el estado de un semáforo.
    Serializable para enviar entre procesos.
    """
    via: str
    color: str
    tamano_cola: int
    vehiculos_cruzados: int
    vehiculos_cola: List[dict] = field(default_factory=list) # Lista de diccionarios con info de autos

    def to_dict(self) -> dict:
        """Convierte a diccionario."""
        return {
            "via": self.via,
            "color": self.color,
            "tamano_cola": self.tamano_cola,
            "vehiculos_cruzados": self.vehiculos_cruzados,
            "vehiculos_cola": self.vehiculos_cola,
        }


@dataclass
class VehiculosDespachadosMsg:
    """
    Mensaje con vehículos despachados en un tick.
    """
    via: str
    cantidad: int
    tiempos_espera: List[float]
    vehiculos_detalle: List[dict] = field(default_factory=list) # Detalle para animación

    def to_dict(self) -> dict:
        """Convierte a diccionario."""
        return {
            "via": self.via,
            "cantidad": self.cantidad,
            "tiempos_espera": self.tiempos_espera,
            "vehiculos_detalle": self.vehiculos_detalle,
        }
