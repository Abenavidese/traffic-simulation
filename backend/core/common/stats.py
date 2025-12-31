"""
Agregador de estadísticas del sistema de tráfico.
Responsable de recopilar y calcular métricas de la simulación.
"""
from typing import List, Dict
from ..models.vehiculo import Vehiculo


class EstadisticasTrafico:
    """
    Recopila y agrega estadísticas de la simulación.
    
    Rastrea:
    - Total de vehículos que cruzaron
    - Tiempos de espera acumulados
    - Promedios
    """

    def __init__(self):
        """Inicializa el agregador de estadísticas."""
        self._vehiculos_cruzados: List[Vehiculo] = []
        self._tiempo_espera_acumulado = 0.0
        self._vehiculos_por_via: Dict[str, int] = {
            "NORTE": 0,
            "SUR": 0,
            "ESTE": 0,
            "OESTE": 0,
        }

    def registrar_vehiculos(self, vehiculos: List[Vehiculo], via: str) -> None:
        """
        Registra vehículos que cruzaron en un tick.
        
        Args:
            vehiculos: Lista de vehículos que cruzaron
            via: Nombre de la vía (NORTE, SUR, ESTE, OESTE)
        """
        for vehiculo in vehiculos:
            self._vehiculos_cruzados.append(vehiculo)
            self._tiempo_espera_acumulado += vehiculo.tiempo_espera_total
            if via in self._vehiculos_por_via:
                self._vehiculos_por_via[via] += 1

    @property
    def total_vehiculos(self) -> int:
        """Retorna el total de vehículos que cruzaron."""
        return len(self._vehiculos_cruzados)

    @property
    def tiempo_espera_promedio(self) -> float:
        """
        Calcula el tiempo promedio de espera.
        
        Returns:
            Tiempo promedio en segundos. 0 si no hay vehículos.
        """
        if self.total_vehiculos == 0:
            return 0.0
        return self._tiempo_espera_acumulado / self.total_vehiculos

    @property
    def tiempo_espera_total(self) -> float:
        """Retorna el tiempo total de espera acumulado."""
        return self._tiempo_espera_acumulado

    def get_vehiculos_por_via(self) -> Dict[str, int]:
        """
        Retorna el conteo de vehículos por vía.
        
        Returns:
            Diccionario con conteo por vía
        """
        return self._vehiculos_por_via.copy()

    def get_resumen(self) -> dict:
        """
        Genera un resumen serializable de las estadísticas.
        
        Returns:
            Diccionario con todas las estadísticas
        """
        return {
            "total_vehiculos": self.total_vehiculos,
            "tiempo_espera_promedio": round(self.tiempo_espera_promedio, 3),
            "tiempo_espera_total": round(self.tiempo_espera_total, 3),
            "vehiculos_por_via": self.get_vehiculos_por_via(),
        }

    def reset(self) -> None:
        """Reinicia todas las estadísticas."""
        self._vehiculos_cruzados.clear()
        self._tiempo_espera_acumulado = 0.0
        self._vehiculos_por_via = {
            "NORTE": 0,
            "SUR": 0,
            "ESTE": 0,
            "OESTE": 0,
        }

    def __repr__(self) -> str:
        return f"EstadisticasTrafico(vehiculos={self.total_vehiculos}, espera_prom={self.tiempo_espera_promedio:.2f}s)"
