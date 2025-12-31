"""
Configuración de la simulación de tráfico.
Contiene todos los parámetros ajustables del sistema.
"""
from dataclasses import dataclass


@dataclass
class ConfiguracionSimulacion:
    """
    Parámetros de configuración para la simulación.
    
    Atributos de semáforos:
        duracion_verde: Ticks que dura la luz verde
        duracion_amarillo: Ticks que dura la luz amarilla
        capacidad_cruce_por_tick: Vehículos máximos que cruzan por tick
    
    Atributos de simulación:
        ticks_totales: Número total de ticks a simular
        intervalo_tick: Tiempo real entre ticks (segundos)
        probabilidad_llegada: Probabilidad de que llegue un vehículo por vía por tick
    
    Atributos de sistema:
        modo: 'threading' o 'multiprocessing'
        ciclos_minimos: Ciclos mínimos para completar la simulación
    """
    # Semáforos
    duracion_verde: int = 5
    duracion_amarillo: int = 2
    capacidad_cruce_por_tick: int = 2
    
    # Simulación
    ticks_totales: int = 100  # Suficiente para ~7 ciclos con config default
    intervalo_tick: float = 0.3  # 300ms entre ticks
    probabilidad_llegada: float = 0.6  # 60% de probabilidad
    
    # Sistema
    modo: str = "threading"  # 'threading' o 'multiprocessing'
    ciclos_minimos: int = 10
    
    # GUI
    mostrar_gui: bool = True
    ancho_ventana: int = 1000
    alto_ventana: int = 800

    @property
    def duracion_ciclo(self) -> int:
        """Calcula la duración de un ciclo completo en ticks."""
        return 2 * (self.duracion_verde + self.duracion_amarillo)

    def __repr__(self) -> str:
        return (
            f"ConfiguracionSimulacion(modo={self.modo}, "
            f"verde={self.duracion_verde}, amarillo={self.duracion_amarillo}, "
            f"ciclos_min={self.ciclos_minimos})"
        )


# Configuración por defecto
CONFIG_DEFAULT = ConfiguracionSimulacion()
