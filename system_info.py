"""
Script de verificación del sistema.
Muestra información sobre Python, GIL, CPU y plataforma.
"""
import sys
import platform
import os
from multiprocessing import cpu_count


def obtener_info_sistema() -> dict:
    """
    Recopila información del sistema.
    
    Returns:
        Diccionario con información del sistema
    """
    info = {
        "python_version": sys.version,
        "python_version_short": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": platform.platform(),
        "system": platform.system(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": cpu_count(),
    }
    
    # Detectar estado del GIL
    # En Python 3.13+ con free-threading build (3.13t)
    if hasattr(sys, '_is_gil_enabled'):
        # Python 3.13t con soporte free-threading
        info["gil_enabled"] = sys._is_gil_enabled() if callable(sys._is_gil_enabled) else sys._is_gil_enabled
        info["free_threading_available"] = True
        info["python_build"] = "3.13t (free-threading)"
    else:
        # Python normal con GIL obligatorio
        info["gil_enabled"] = True
        info["free_threading_available"] = False
        info["python_build"] = "Standard (GIL obligatorio)"
    
    return info


def mostrar_info_sistema() -> None:
    """Imprime la información del sistema de forma legible."""
    info = obtener_info_sistema()
    
    print("=" * 70)
    print("INFORMACIÓN DEL SISTEMA - SIMULACIÓN DE TRÁFICO PARALELO")
    print("=" * 70)
    print(f"\n🐍 Python:")
    print(f"  Versión: {info['python_version_short']}")
    print(f"  Build: {info['python_build']}")
    print(f"  Ejecutable: {sys.executable}")
    
    print(f"\n🔒 Global Interpreter Lock (GIL):")
    if info['free_threading_available']:
        estado_gil = "DESHABILITADO ✓" if not info['gil_enabled'] else "HABILITADO"
        print(f"  Estado: {estado_gil}")
        print(f"  Free-threading disponible: Sí")
    else:
        print(f"  Estado: HABILITADO (obligatorio)")
        print(f"  Free-threading disponible: No")
    
    print(f"\n💻 Hardware:")
    print(f"  Sistema Operativo: {info['system']}")
    print(f"  Plataforma: {info['platform']}")
    print(f"  Procesador: {info['processor']}")
    print(f"  Núcleos (lógicos): {info['cpu_count']}")
    
    print(f"\n📊 Implicaciones para la práctica:")
    if info['free_threading_available'] and not info['gil_enabled']:
        print("  ✓ Threading puede aprovechar múltiples cores verdaderamente")
        print("  ✓ Ideal para comparar threading vs multiprocessing")
    elif info['free_threading_available'] and info['gil_enabled']:
        print("  ⚠ GIL habilitado - threading limitado a 1 core")
        print("  ℹ Ejecuta con: py -3.13t -X gil=0 para deshabilitar GIL")
    else:
        print("  ⚠ Threading limitado por GIL - solo 1 thread activo a la vez")
        print("  ✓ Multiprocessing puede usar todos los cores")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    mostrar_info_sistema()
