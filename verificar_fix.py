import sys
import os
from time import sleep

# Asegurar que el backend sea importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from backend.app.config import ConfiguracionSimulacion
from backend.runtime.engines.threading_engine import ThreadingEngine

def test_engine():
    print("Iniciando prueba de ThreadingEngine (verificación de deadlock)...")
    config = ConfiguracionSimulacion(
        intervalo_tick=0.1,
        duracion_verde=5,
        duracion_amarillo=2,
        probabilidad_llegada=0.5
    )
    engine = ThreadingEngine(config)
    engine.start()
    
    try:
        for i in range(20):
            print(f"Tick {i}...", end=" ", flush=True)
            state = engine.step()
            print(f"OK (Fase: {state.fase}, Vehículos: {state.estadisticas['total_vehiculos']})")
    except Exception as e:
        print(f"\n[ERROR] Falló la simulación: {e}")
        sys.exit(1)
    finally:
        engine.stop()
        print("\nPrueba completada con éxito.")

if __name__ == "__main__":
    test_engine()
