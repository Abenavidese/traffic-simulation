"""
Tests para el controlador de tráfico.
Verifica la alternancia correcta de fases y conteo de ciclos.
"""
import pytest
from backend.core.traffic.controlador import ControladorTrafico
from backend.core.common.tipos import Via, Color


class TestControladorTrafico:
    """Tests para ControladorTrafico."""

    def test_inicializacion(self):
        """Verifica que el controlador se inicializa correctamente."""
        controlador = ControladorTrafico(duracion_verde=5, duracion_amarillo=2)
        assert controlador.ciclo_actual == 0
        assert controlador.tick_actual == 0
        assert controlador.fase_actual == "NS_VERDE"

    def test_fase_ns_verde(self):
        """Verifica que la fase NS verde funciona correctamente."""
        controlador = ControladorTrafico(duracion_verde=3, duracion_amarillo=1)
        plan = controlador.avanzar_tick()
        
        # Norte y Sur deben estar en verde
        assert plan[Via.NORTE] == Color.VERDE
        assert plan[Via.SUR] == Color.VERDE
        assert plan[Via.ESTE] == Color.ROJO
        assert plan[Via.OESTE] == Color.ROJO

    def test_transicion_a_amarillo(self):
        """Verifica la transición de verde a amarillo."""
        controlador = ControladorTrafico(duracion_verde=2, duracion_amarillo=1)
        
        # Avanzar durante verde
        controlador.avanzar_tick()
        controlador.avanzar_tick()
        
        # Siguiente tick debe ser amarillo
        plan = controlador.avanzar_tick()
        assert plan[Via.NORTE] == Color.AMARILLO
        assert plan[Via.SUR] == Color.AMARILLO

    def test_alternancia_ew(self):
        """Verifica que se alterna a fase EW."""
        controlador = ControladorTrafico(duracion_verde=2, duracion_amarillo=1)
        
        # NS verde (2 ticks) + NS amarillo (1 tick)
        for _ in range(3):
            controlador.avanzar_tick()
        
        # Ahora debe estar en EW verde
        plan = controlador.avanzar_tick()
        assert plan[Via.ESTE] == Color.VERDE
        assert plan[Via.OESTE] == Color.VERDE
        assert plan[Via.NORTE] == Color.ROJO
        assert plan[Via.SUR] == Color.ROJO

    def test_ciclo_completo(self):
        """Verifica que se cuenta un ciclo completo correctamente."""
        controlador = ControladorTrafico(duracion_verde=2, duracion_amarillo=1)
        
        assert controlador.ciclo_actual == 0
        
        # Un ciclo completo = NS_VERDE + NS_AMARILLO + EW_VERDE + EW_AMARILLO
        # = 2 + 1 + 2 + 1 = 6 ticks
        for _ in range(6):
            controlador.avanzar_tick()
        
        # Debe haber completado 1 ciclo y volver a NS_VERDE
        assert controlador.ciclo_actual == 1
        assert controlador.fase_actual == "NS_VERDE"

    def test_multiples_ciclos(self):
        """Verifica conteo de múltiples ciclos."""
        controlador = ControladorTrafico(duracion_verde=1, duracion_amarillo=1)
        
        # Ciclo = 1+1+1+1 = 4 ticks
        # Ejecutar 3 ciclos = 12 ticks
        for _ in range(12):
            controlador.avanzar_tick()
        
        assert controlador.ciclo_actual == 3
        assert controlador.tick_actual == 12

    def test_no_colision(self):
        """Verifica que nunca hay dos vías perpendiculares en verde."""
        controlador = ControladorTrafico(duracion_verde=3, duracion_amarillo=2)
        
        for _ in range(20):  # Varios ciclos
            plan = controlador.avanzar_tick()
            
            # Si NS está en verde, EW debe estar en rojo
            if plan[Via.NORTE] == Color.VERDE:
                assert plan[Via.ESTE] == Color.ROJO
                assert plan[Via.OESTE] == Color.ROJO
            
            # Si EW está en verde, NS debe estar en rojo
            if plan[Via.ESTE] == Color.VERDE:
                assert plan[Via.NORTE] == Color.ROJO
                assert plan[Via.SUR] == Color.ROJO
