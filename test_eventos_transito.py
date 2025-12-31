"""
Script de prueba para ver EVENTOS y VEHÍCULOS EN TRÁNSITO.
"""
import sys
sys.path.insert(0, 'C:\\Users\\EleXc\\Music\\paralela-multi-hilos')

from backend.app.config import ConfiguracionSimulacion
from backend.runtime.engines.threading_engine import ThreadingEngine


def main():
    print("=" * 80)
    print("🎬 TEST: EVENTOS Y VEHÍCULOS EN TRÁNSITO")
    print("=" * 80)
    
    # Configuración
    config = ConfiguracionSimulacion(
        duracion_verde=3,
        duracion_amarillo=1,
        ciclos_minimos=1,
        intervalo_tick=0.1,
        probabilidad_llegada=0.8,  # Mayor probabilidad para más eventos
    )
    
    # Crear engine
    engine = ThreadingEngine(config)
    engine.start()
    print("\n✓ Engine iniciado\n")
    
    # Ejecutar 10 ticks y mostrar eventos
    print("🎭 SIMULACIÓN (10 ticks):\n")
    
    for tick in range(1, 11):
        state = engine.step()
        
        print(f"{'─'*80}")
        print(f"Tick {tick} | Fase: {state.fase} | Ciclo: {state.ciclo}")
        print(f"{'─'*80}")
        
        # Mostrar semáforos
        print("🚦 Semáforos:", end=" ")
        for via, color in state.luces.items():
            emoji = {"VERDE": "🟢", "AMARILLO": "🟡", "ROJO": "🔴"}[color]
            print(f"{emoji}{via[:1]}", end=" ")
        print()
        
        # EVENTOS DEL TICK
        eventos = state.eventos_tick.get("eventos", [])
        if eventos:
            print(f"\n📋 Eventos ({len(eventos)}):")
            for evento in eventos:
                tipo = evento['tipo']
                icono = evento.get('icono', '•')
                
                if tipo == "vehiculo_llego":
                    print(f"  {icono} Vehículo #{evento['vehiculo_id']} llegó a {evento['via']}")
                elif tipo == "vehiculo_despachado":
                    print(f"  {icono} Vehículo #{evento['vehiculo_id']} cruzó desde {evento['via']}")
                elif tipo == "cambio_semaforo":
                    print(f"  {icono} {evento['via']}: {evento['color_anterior']} → {evento['color_nuevo']}")
        else:
            print("\n📋 Eventos: (ninguno)")
        
        # VEHÍCULOS EN TRÁNSITO
        transito = state.vehiculos_en_transito
        if transito:
            print(f"\n🚗 Vehículos en tránsito:")
            for via, vehiculos in transito.items():
                print(f"  {via}:")
                for v in vehiculos:
                    barra = "█" * int(v['progreso'] * 10) + "░" * (10 - int(v['progreso'] * 10))
                    print(f"    Veh #{v['id']}: [{barra}] {v['progreso']*100:.0f}%")
        
        # Timing de fase
        timing = state.timing_fase
        barra_fase = "█" * timing['ticks_en_fase'] + "░" * timing['ticks_restantes']
        print(f"\n⏱️ Fase: [{barra_fase}] {timing['ticks_en_fase']}/{timing['duracion_total']}")
        
        print()
    
    print("=" * 80)
    print("✅ PRUEBA COMPLETADA")
    print("=" * 80)
    
    # Resumen final
    state_final = engine.get_state()
    print(f"\n📊 Resumen Final:")
    print(f"  Total vehículos cruzados: {state_final.estadisticas['total_vehiculos']}")
    print(f"  Tiempo espera promedio: {state_final.estadisticas['tiempo_espera_promedio']:.3f}s")
    print(f"  Vehículos por vía:")
    for via, count in state_final.estadisticas['vehiculos_por_via'].items():
        print(f"    {via}: {count}")
    
    engine.stop()
    print("\n✓ Engine detenido\n")


if __name__ == "__main__":
    main()
