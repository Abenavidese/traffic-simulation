"""
Punto de entrada de la simulación.
Permite ejecutar la simulación en modo threading o multiprocessing.

Uso:
    python -m backend.app.sim threading
    python -m backend.app.sim multiprocessing
    py -3.13t -X gil=0 -m backend.app.sim threading
"""
import sys
import argparse
from time import sleep, time

from .config import ConfiguracionSimulacion
from ..runtime.engines.threading_engine import ThreadingEngine
from ..runtime.engines.multiprocessing_engine import MultiprocessingEngine


def mostrar_estado(state, intervalo_tiempo: float = None):
    """Muestra el estado actual en consola."""
    print(f"\n{'='*70}")
    print(f"Tick: {state.tick} | Ciclo: {state.ciclo} | Fase: {state.fase}")
    print(f"{'='*70}")
    
    print(f"\n🚦 Semáforos:")
    for via, color in state.luces.items():
        cola = state.colas.get(via, 0)
        emoji = "🟢" if color == "VERDE" else "🟡" if color == "AMARILLO" else "🔴"
        print(f"  {emoji} {via:6} - {color:9} | Cola: {cola:3} vehículos")
    
    print(f"\n📊 Estadísticas:")
    stats = state.estadisticas
    print(f"  Total vehículos cruzados: {stats.get('total_vehiculos', 0)}")
    print(f"  Tiempo espera promedio: {stats.get('tiempo_espera_promedio', 0):.3f}s")
    
    vehiculos_via = stats.get('vehiculos_por_via', {})
    if vehiculos_via:
        print(f"  Vehículos por vía:")
        for via, count in vehiculos_via.items():
            print(f"    {via}: {count}")
    
    print(f"\n💻 Sistema:")
    for key, value in state.info_sistema.items():
        print(f"  {key}: {value}")
    
    if intervalo_tiempo:
        print(f"\n⏱️ Tiempo de ejecución: {intervalo_tiempo:.3f}s")


def ejecutar_simulacion(modo: str, config: ConfiguracionSimulacion):
    """
    Ejecuta la simulación con el modo especificado.
    
    Args:
        modo: 'threading' o 'multiprocessing'
        config: Configuración de la simulación
    """
    # Crear engine según el modo
    if modo == "threading":
        print("\n🧵 Iniciando simulación con THREADING...")
        engine = ThreadingEngine(config)
    elif modo == "multiprocessing":
        print("\n🔄 Iniciando simulación con MULTIPROCESSING...")
        engine = MultiprocessingEngine(config)
    else:
        raise ValueError(f"Modo inválido: {modo}. Use 'threading' o 'multiprocessing'")
    
    # Iniciar engine
    engine.start()
    print(f"✓ Engine iniciado correctamente\n")
    
    # Calcular ticks necesarios
    ticks_por_ciclo = config.duracion_ciclo
    ticks_necesarios = config.ciclos_minimos * ticks_por_ciclo
    
    print(f"Configuración:")
    print(f"  - Duración verde: {config.duracion_verde} ticks")
    print(f"  - Duración amarillo: {config.duracion_amarillo} ticks")
    print(f"  - Ticks por ciclo: {ticks_por_ciclo}")
    print(f"  - Ciclos mínimos: {config.ciclos_minimos}")
    print(f"  - Ticks totales: {ticks_necesarios}")
    print(f"  - Probabilidad llegada: {config.probabilidad_llegada * 100:.0f}%")
    
    # Ejecutar simulación
    inicio = time()
    tick_count = 0
    
    try:
        while engine.controlador.ciclo_actual < config.ciclos_minimos:
            # Ejecutar tick
            state = engine.step()
            tick_count += 1
            
            # Mostrar estado cada 5 ticks
            if tick_count % 5 == 0:
                mostrar_estado(state)
            
            # Pausar entre ticks
            sleep(config.intervalo_tick)
        
        # Estado final
        state_final = engine.get_state()
        fin = time()
        
        print(f"\n{'='*70}")
        print(f"✅ SIMULACIÓN COMPLETADA")
        print(f"{'='*70}")
        mostrar_estado(state_final, fin - inicio)
        
        print(f"\n🏁 Resumen:")
        print(f"  - Ciclos completados: {state_final.ciclo}")
        print(f"  - Ticks ejecutados: {tick_count}")
        print(f"  - Tiempo total: {fin - inicio:.2f}s")
        print(f"  - Ticks/segundo: {tick_count / (fin - inicio):.2f}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Simulación interrumpida por el usuario")
    finally:
        # Detener engine
        engine.stop()
        print("\n✓ Engine detenido\n")


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description="Simulación de tráfico paralelo - Laboratorio de Computación Paralela"
    )
    parser.add_argument(
        "modo",
        choices=["threading", "multiprocessing"],
        help="Modo de ejecución paralela"
    )
    parser.add_argument(
        "--verde",
        type=int,
        default=5,
        help="Duración de luz verde en ticks (default: 5)"
    )
    parser.add_argument(
        "--amarillo",
        type=int,
        default=2,
        help="Duración de luz amarilla en ticks (default: 2)"
    )
    parser.add_argument(
        "--ciclos",
        type=int,
        default=10,
        help="Número mínimo de ciclos a ejecutar (default: 10)"
    )
    parser.add_argument(
        "--intervalo",
        type=float,
        default=0.3,
        help="Tiempo entre ticks en segundos (default: 0.3)"
    )
    
    args = parser.parse_args()
    
    # Crear configuración
    config = ConfiguracionSimulacion(
        modo=args.modo,
        duracion_verde=args.verde,
        duracion_amarillo=args.amarillo,
        ciclos_minimos=args.ciclos,
        intervalo_tick=args.intervalo,
    )
    
    # Mostrar información del sistema
    from ...system_info import mostrar_info_sistema
    mostrar_info_sistema()
    
    # Ejecutar simulación
    ejecutar_simulacion(args.modo, config)


if __name__ == "__main__":
    main()
