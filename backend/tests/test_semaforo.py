"""
Tests para el semáforo.
Verifica el despacho correcto de vehículos según el color.
"""
import pytest
from backend.core.traffic.semaforo import Semaforo
from backend.core.common.tipos import Via, Color
from backend.core.models.vehiculo import Vehiculo


class TestSemaforo:
    """Tests para Semaforo."""

    def test_inicializacion(self):
        """Verifica inicialización correcta."""
        semaforo = Semaforo(Via.NORTE, capacidad_por_tick=2)
        assert semaforo.via == Via.NORTE
        assert semaforo.color == Color.ROJO
        assert semaforo.tamano_cola == 0
        assert semaforo.vehiculos_cruzados_total == 0

    def test_agregar_vehiculo(self):
        """Verifica que se pueden agregar vehículos a la cola."""
        semaforo = Semaforo(Via.SUR)
        vehiculo = Vehiculo(id=1)
        
        semaforo.agregar_vehiculo(vehiculo)
        assert semaforo.tamano_cola == 1
        assert vehiculo.tiempo_inicio_espera is not None

    def test_no_despacho_en_rojo(self):
        """Verifica que no se despachan vehículos en rojo."""
        semaforo = Semaforo(Via.ESTE)
        semaforo.agregar_vehiculo(Vehiculo(id=1))
        semaforo.agregar_vehiculo(Vehiculo(id=2))
        
        semaforo.set_color(Color.ROJO)
        cruzados = semaforo.tick()
        
        assert len(cruzados) == 0
        assert semaforo.tamano_cola == 2

    def test_no_despacho_en_amarillo(self):
        """Verifica que no se despachan vehículos en amarillo."""
        semaforo = Semaforo(Via.OESTE)
        semaforo.agregar_vehiculo(Vehiculo(id=1))
        
        semaforo.set_color(Color.AMARILLO)
        cruzados = semaforo.tick()
        
        assert len(cruzados) == 0
        assert semaforo.tamano_cola == 1

    def test_despacho_en_verde(self):
        """Verifica que se despachan vehículos en verde."""
        semaforo = Semaforo(Via.NORTE, capacidad_por_tick=2)
        semaforo.agregar_vehiculo(Vehiculo(id=1))
        semaforo.agregar_vehiculo(Vehiculo(id=2))
        semaforo.agregar_vehiculo(Vehiculo(id=3))
        
        semaforo.set_color(Color.VERDE)
        cruzados = semaforo.tick()
        
        # Debe despachar máximo 2 (capacidad)
        assert len(cruzados) == 2
        assert semaforo.tamano_cola == 1
        assert semaforo.vehiculos_cruzados_total == 2

    def test_respeto_capacidad(self):
        """Verifica que se respeta la capacidad por tick."""
        semaforo = Semaforo(Via.SUR, capacidad_por_tick=1)
        for i in range(5):
            semaforo.agregar_vehiculo(Vehiculo(id=i))
        
        semaforo.set_color(Color.VERDE)
        cruzados = semaforo.tick()
        
        # Solo debe despachar 1
        assert len(cruzados) == 1
        assert semaforo.tamano_cola == 4

    def test_marca_salida_vehiculos(self):
        """Verifica que los vehículos despachados tienen marca de salida."""
        semaforo = Semaforo(Via.ESTE)
        vehiculo = Vehiculo(id=1)
        semaforo.agregar_vehiculo(vehiculo)
        
        semaforo.set_color(Color.VERDE)
        cruzados = semaforo.tick()
        
        assert len(cruzados) == 1
        assert cruzados[0].tiempo_salida is not None

    def test_multiples_ticks_verde(self):
        """Verifica múltiples ticks consecutivos en verde."""
        semaforo = Semaforo(Via.NORTE, capacidad_por_tick=2)
        for i in range(6):
            semaforo.agregar_vehiculo(Vehiculo(id=i))
        
        semaforo.set_color(Color.VERDE)
        
        cruzados1 = semaforo.tick()
        cruzados2 = semaforo.tick()
        cruzados3 = semaforo.tick()
        
        assert len(cruzados1) == 2
        assert len(cruzados2) == 2
        assert len(cruzados3) == 2
        assert semaforo.tamano_cola == 0
        assert semaforo.vehiculos_cruzados_total == 6

    def test_cambio_color_durante_operacion(self):
        """Verifica cambio de color durante operación."""
        semaforo = Semaforo(Via.OESTE)
        semaforo.agregar_vehiculo(Vehiculo(id=1))
        semaforo.agregar_vehiculo(Vehiculo(id=2))
        
        # Tick en rojo - no despacha
        semaforo.set_color(Color.ROJO)
        assert len(semaforo.tick()) == 0
        
        # Cambiar a verde - ahora sí despacha
        semaforo.set_color(Color.VERDE)
        cruzados = semaforo.tick()
        assert len(cruzados) == 2
