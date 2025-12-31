"""
Interfaz base para los engines de ejecución.
Define el contrato que deben cumplir todos los engines.
"""
from abc import ABC, abstractmethod
from ...core.common.state import TrafficState


class BaseEngine(ABC):
    """
    Interfaz abstracta para engines de simulación.
    
    Todos los engines (threading, multiprocessing) deben implementar estos métodos.
    """

    @abstractmethod
    def start(self) -> None:
        """
        Inicializa los recursos del engine.
        
        - Crea semáforos, controlador, estadísticas
        - Inicia procesos/hilos si es necesario
        - Prepara mecanismos de comunicación
        """
        pass

    @abstractmethod
    def step(self) -> TrafficState:
        """
        Ejecuta un tick completo de simulación.
        
        Returns:
            TrafficState con el estado actual del sistema
        """
        pass

    @abstractmethod
    def get_state(self) -> TrafficState:
        """
        Obtiene el estado actual sin avanzar la simulación.
        
        Returns:
            TrafficState con el estado actual
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """
        Detiene el engine y libera recursos.
        
        - Detiene procesos/hilos
        - Cierra colas, pipes
        - Limpia recursos
        """
        pass

    @abstractmethod
    def is_running(self) -> bool:
        """
        Verifica si el engine está activo.
        
        Returns:
            True si está corriendo, False en caso contrario
        """
        pass
