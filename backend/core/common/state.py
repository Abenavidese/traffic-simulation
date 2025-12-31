"""
Estado del sistema de tráfico.
Representa una instantánea completa del sistema en un momento dado.
"""
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class TrafficState:
    """
    Representa el estado completo del sistema en un tick.
    
    Este es el único objeto que sale del backend y es consumido por:
    - GUI para renderizar
    - Logs para debugging
    - Tests para validación
    """
    # Información temporal
    tick: int
    ciclo: int
    fase: str
    
    # Estado de las luces (Via -> Color)
    luces: Dict[str, str] = field(default_factory=dict)
    
    # Tamaño de las colas por vía
    colas: Dict[str, int] = field(default_factory=dict)
    
    # Estadísticas acumuladas
    estadisticas: Dict[str, any] = field(default_factory=dict)
    
    # Información del sistema
    info_sistema: Dict[str, str] = field(default_factory=dict)
    
    # NUEVOS: Datos para animaciones frontend 🎨
    # Detalles individuales de vehículos en colas
    vehiculos_detalle: Dict[str, list] = field(default_factory=dict)
    
    # Vehículos actualmente cruzando la intersección
    vehiculos_en_transito: Dict[str, list] = field(default_factory=dict)
    
    # Eventos ocurridos en este tick
    eventos_tick: Dict[str, list] = field(default_factory=dict)
    
    # Información de timing de fase actual
    timing_fase: Dict[str, int] = field(default_factory=dict)
    
    # Configuración de la simulación
    configuracion: Dict[str, any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """
        Convierte el estado a un diccionario serializable.
        
        Returns:
            Diccionario con todo el estado
        """
        return {
            "tick": self.tick,
            "ciclo": self.ciclo,
            "fase": self.fase,
            "luces": self.luces,
            "colas": self.colas,
            "estadisticas": self.estadisticas,
            "info_sistema": self.info_sistema,
            # Nuevos campos
            "vehiculos_detalle": self.vehiculos_detalle,
            "vehiculos_en_transito": self.vehiculos_en_transito,
            "eventos_tick": self.eventos_tick,
            "timing_fase": self.timing_fase,
            "configuracion": self.configuracion,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TrafficState":
        """
        Crea un TrafficState desde un diccionario.
        
        Args:
            data: Diccionario con los datos del estado
            
        Returns:
            Instancia de TrafficState
        """
        return cls(
            tick=data.get("tick", 0),
            ciclo=data.get("ciclo", 0),
            fase=data.get("fase", ""),
            luces=data.get("luces", {}),
            colas=data.get("colas", {}),
            estadisticas=data.get("estadisticas", {}),
            info_sistema=data.get("info_sistema", {}),
            # Nuevos campos con defaults
            vehiculos_detalle=data.get("vehiculos_detalle", {}),
            vehiculos_en_transito=data.get("vehiculos_en_transito", {}),
            eventos_tick=data.get("eventos_tick", {}),
            timing_fase=data.get("timing_fase", {}),
            configuracion=data.get("configuracion", {}),
        )

    def __repr__(self) -> str:
        return f"TrafficState(tick={self.tick}, ciclo={self.ciclo}, fase={self.fase})"
