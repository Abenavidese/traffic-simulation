"""
Script de prueba para verificar los nuevos datos del backend.
Muestra todos los campos disponibles en TrafficState.
"""
import sys
sys.path.insert(0, 'C:\\Users\\EleXc\\Music\\paralela-multi-hilos')

from backend.app.config import ConfiguracionSimulacion
from backend.runtime.engines.threading_engine import ThreadingEngine
import json


def main():
    print("=" * 70)
    print("TEST: Verificación de Nuevos Datos para Frontend")
    print("=" * 70)
    
    # Crear configuración
    config = ConfiguracionSimulacion(
        duracion_verde=3,
        duracion_amarillo=1,
        ciclos_minimos=1,
        intervalo_tick=0.1,
    )
    
    # Crear engine
    engine = ThreadingEngine(config)
    engine.start()
    print("\n✓ Engine iniciado\n")
    
    # Ejecutar algunos ticks
    for i in range(5):
        state = engine.step()
    
    print("🔍 Analizando TrafficState después de 5 ticks...\n")
    
    # Convertir a dict para mejor visualización
    state_dict = state.to_dict()
    
    # Mostrar datos BÁSICOS
    print("📊 DATOS BÁSICOS (existentes):")
    print(f"  Tick: {state_dict['tick']}")
    print(f"  Ciclo: {state_dict['ciclo']}")
    print(f"  Fase: {state_dict['fase']}")
    print(f"  Luces: {state_dict['luces']}")
    print(f"  Colas: {state_dict['colas']}")
    
    # Mostrar datos NUEVOS
    print("\n🎨 DATOS NUEVOS (para animaciones):\n")
    
    print("1️⃣ VEHÍCULOS DETALLADOS:")
    for via, vehiculos in state_dict['vehiculos_detalle'].items():
        print(f"   {via}: {len(vehiculos)} vehículos en cola")
        for v in vehiculos[:3]:  # Mostrar solo los primeros 3
            print(f"      - ID:{v['id']}, Pos:{v['posicion']}, Esperando:{v['esperando_desde']:.2f}s")
        if len(vehiculos) > 3:
            print(f"      ... y {len(vehiculos) - 3} más")
    
    print("\n2️⃣ TIMING DE FASE:")
    timing = state_dict['timing_fase']
    print(f"   Fase: {timing['fase_actual']}")
    print(f"   Ticks en fase: {timing['ticks_en_fase']}")
    print(f"   Ticks restantes: {timing['ticks_restantes']}")
    print(f"   Duración total: {timing['duracion_total']}")
    barra = "█" * timing['ticks_en_fase'] + "░" * timing['ticks_restantes']
    print(f"   Progreso: [{barra}]")
    
    print("\n3️⃣ CONFIGURACIÓN:")
    for key, value in state_dict['configuracion'].items():
        print(f"   {key}: {value}")
    
    print("\n4️⃣ VEHÍCULOS EN TRÁNSITO:")
    print(f"   {state_dict['vehiculos_en_transito']}")
    print("   (TODO: Para implementar vehículos cruzando)")
    
    print("\n5️⃣ EVENTOS DEL TICK:")
    print(f"   {state_dict['eventos_tick']}")
    print("   (TODO: Para log de eventos)")
    
    print("\n" + "=" * 70)
    print("✅ TODOS LOS DATOS ESTÁN DISPONIBLES PARA EL FRONTEND")
    print("=" * 70)
    
    print("\n📋 Resumen de capacidades frontend:\n")
    print("✅ Mostrar vehículos individuales con posiciones")
    print("✅ Barra de progreso de fase actual")
    print("✅ Countdown hasta cambio de semáforo")
    print("✅ Mostrar tiempo de espera por vehículo")
    print("✅ Panel de configuración")
    print("⏳ Animar vehículos cruzando (pendiente)")
    print("⏳ Log de eventos (pendiente)")
    
    # Detener engine
    engine.stop()
    print("\n✓ Engine detenido")


if __name__ == "__main__":
    main()
