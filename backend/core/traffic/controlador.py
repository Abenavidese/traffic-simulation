"""
Controlador central de tráfico.
Responsable de coordinar las fases de los semáforos y evitar colisiones.
"""
from typing import Dict

from ..common.tipos import Color, Via


class ControladorTrafico:
    """
    Coordina los semáforos de la intersección.
    
    Implementa un sistema de fases que alterna entre:
    - Fase NS: Norte y Sur en VERDE
    - Transición: AMARILLO
    - Fase EW: Este y Oeste en VERDE
    - Transición: AMARILLO
    
    Garantiza que no haya colisiones.
    """

    def __init__(
        self,
        duracion_verde: int = 5,
        duracion_amarillo: int = 2,
    ):
        """
        Inicializa el controlador.
        
        Args:
            duracion_verde: Ticks que dura la luz verde
            duracion_amarillo: Ticks que dura la luz amarilla
        """
        self.duracion_verde = duracion_verde
        self.duracion_amarillo = duracion_amarillo
        
        # Estado interno
        self._tick_actual = 0
        self._ciclo_actual = 0
        self._fase_actual = "NS_VERDE"  # Fases: NS_VERDE, NS_AMARILLO, EW_VERDE, EW_AMARILLO
        self._ticks_en_fase = 0
        
        # Duración total de un ciclo completo
        self._duracion_ciclo = 2 * (duracion_verde + duracion_amarillo)

    def avanzar_tick(self) -> Dict[Via, Color]:
        """
        Avanza un tick en la simulación.
        
        Returns:
            Diccionario con el plan de colores para cada vía
        """
        self._tick_actual += 1
        self._ticks_en_fase += 1
        
        # Determinar si hay que cambiar de fase
        if self._fase_actual == "NS_VERDE" and self._ticks_en_fase >= self.duracion_verde:
            self._fase_actual = "NS_AMARILLO"
            self._ticks_en_fase = 0
        elif self._fase_actual == "NS_AMARILLO" and self._ticks_en_fase >= self.duracion_amarillo:
            self._fase_actual = "EW_VERDE"
            self._ticks_en_fase = 0
        elif self._fase_actual == "EW_VERDE" and self._ticks_en_fase >= self.duracion_verde:
            self._fase_actual = "EW_AMARILLO"
            self._ticks_en_fase = 0
        elif self._fase_actual == "EW_AMARILLO" and self._ticks_en_fase >= self.duracion_amarillo:
            self._fase_actual = "NS_VERDE"
            self._ticks_en_fase = 0
            self._ciclo_actual += 1  # Completamos un ciclo completo
        
        # Generar plan de colores según la fase
        return self._generar_plan()

    def _generar_plan(self) -> Dict[Via, Color]:
        """
        Genera el plan de colores para la fase actual.
        
        Returns:
            Diccionario mapeando cada vía a su color
        """
        if self._fase_actual == "NS_VERDE":
            return {
                Via.NORTE: Color.VERDE,
                Via.SUR: Color.VERDE,
                Via.ESTE: Color.ROJO,
                Via.OESTE: Color.ROJO,
            }
        elif self._fase_actual == "NS_AMARILLO":
            return {
                Via.NORTE: Color.AMARILLO,
                Via.SUR: Color.AMARILLO,
                Via.ESTE: Color.ROJO,
                Via.OESTE: Color.ROJO,
            }
        elif self._fase_actual == "EW_VERDE":
            return {
                Via.NORTE: Color.ROJO,
                Via.SUR: Color.ROJO,
                Via.ESTE: Color.VERDE,
                Via.OESTE: Color.VERDE,
            }
        else:  # EW_AMARILLO
            return {
                Via.NORTE: Color.ROJO,
                Via.SUR: Color.ROJO,
                Via.ESTE: Color.AMARILLO,
                Via.OESTE: Color.AMARILLO,
            }

    @property
    def ciclo_actual(self) -> int:
        """Retorna el número de ciclos completos."""
        return self._ciclo_actual

    @property
    def tick_actual(self) -> int:
        """Retorna el número total de ticks."""
        return self._tick_actual

    @property
    def fase_actual(self) -> str:
        """Retorna la fase actual."""
        return self._fase_actual

    def get_info(self) -> dict:
        """
        Retorna información del estado del controlador.
        
        Returns:
            Diccionario con información del controlador
        """
        return {
            "tick": self._tick_actual,
            "ciclo": self._ciclo_actual,
            "fase": self._fase_actual,
            "ticks_en_fase": self._ticks_en_fase,
        }


    def get_timing_fase(self) -> dict:
        """
        Retorna información de timing de la fase actual.
        
        Útil para mostrar barras de progreso o countdown en la GUI.
        
        Returns:
            Diccionario con:
            - fase_actual: Nombre de la fase
            - ticks_en_fase: Ticks transcurridos en la fase
            - ticks_restantes: Ticks que faltan para cambiar
            - duracion_total: Duración total de la fase
        """
        # Determinar duración según la fase
        if "VERDE" in self._fase_actual:
            duracion = self.duracion_verde
        else:  # AMARILLO
            duracion = self.duracion_amarillo
        
        return {
            "fase_actual": self._fase_actual,
            "ticks_en_fase": self._ticks_en_fase,
            "ticks_restantes": max(0, duracion - self._ticks_en_fase),
            "duracion_total": duracion,
        }

    def __repr__(self) -> str:
        return f"ControladorTrafico(ciclo={self._ciclo_actual}, fase={self._fase_actual})"
