Backend – Simulación de Tráfico Concurrente (Hilos y Procesos)
1. Objetivo del proyecto

Este backend implementa una simulación de una intersección vial de cuatro vías (Norte, Sur, Este, Oeste) controlada por semáforos, con llegada de vehículos, control de fases y recopilación de estadísticas.

El sistema debe funcionar en dos modos de concurrencia:

Basado en hilos (threading)

Basado en procesos (multiprocessing)

La lógica del tráfico debe ser reutilizable, de modo que la única diferencia entre ambas versiones sea el motor de ejecución (engine).

2. Principios de diseño
2.1 Separación estricta de responsabilidades

Dominio (core/)
Contiene la lógica del tráfico.
❌ No conoce hilos ni procesos.
❌ No importa threading ni multiprocessing.

Infraestructura (runtime/)
Contiene la lógica de concurrencia.
✔ Decide si se usan hilos o procesos.
✔ Coordina la ejecución concurrente.

Aplicación (app/)
Configura y ejecuta la simulación.
✔ Selecciona el engine.
✔ Ejecuta los ticks.

2.2 Regla de oro

El dominio no debe cambiar cuando se cambia de hilos a procesos.

3. Estructura de carpetas
backend/
  core/
    models/
      vehiculo.py
    traffic/
      semaforo.py
      controlador.py
    common/
      tipos.py
      state.py
      stats.py

  runtime/
    engines/
      base.py
      threading_engine.py
      multiprocessing_engine.py
    comms/
      messages.py

  app/
    config.py
    sim.py

  tests/
    test_controlador.py
    test_semaforo.py

4. Descripción detallada por módulo
4.1 CORE – Dominio del sistema
core/common/tipos.py

Define tipos compartidos y estables del sistema.

Debe contener:

Enum Via → N, S, E, O

Enum Color → ROJO, AMARILLO, VERDE

📌 No debe contener lógica, solo definiciones.

core/models/vehiculo.py

Representa un vehículo individual.

Responsabilidades:

Guardar:

tiempo de llegada

inicio de espera

salida

Calcular:

tiempo total de espera

Debe permitir:

Marcar inicio de espera

Marcar salida

Calcular métricas sin depender del engine

core/traffic/semaforo.py

Modelo lógico de un semáforo por vía.

Responsabilidades:

Mantener una cola de vehículos

Mantener el estado del semáforo

Despachar vehículos cuando esté en VERDE

Debe:

Aceptar vehículos (enqueue)

Cambiar color (set_color)

En cada tick:

permitir pasar N vehículos si está VERDE

no permitir paso si está ROJO o AMARILLO

❌ No debe manejar hilos ni procesos
❌ No debe dormir ni sincronizar

core/traffic/controlador.py

Controlador central de tráfico.

Responsabilidades:

Decidir qué vías tienen luz verde

Evitar colisiones

Implementar fases seguras

Diseño recomendado:

Fase NS (N y S VERDE)

Transición AMARILLO

Fase EW (E y O VERDE)

Transición AMARILLO

Debe:

Avanzar por ticks

Contar ciclos completos

Retornar un plan Via → Color

core/common/stats.py

Agregador de estadísticas globales.

Responsabilidades:

Contar vehículos que cruzan

Acumular tiempos de espera

Calcular promedios

Debe:

Recibir vehículos que cruzaron por tick

Producir un resumen serializable

core/common/state.py

Representa una foto del estado actual del sistema.

Debe contener:

Número de ciclo

Número de tick

Estado de luces

Tamaño de colas

Estadísticas

Este objeto es:

La única salida del backend

Consumido por GUI, logs o tests

4.2 RUNTIME – Infraestructura concurrente
runtime/engines/base.py

Interfaz común para los engines.

Define el contrato obligatorio:

start() → inicializa recursos

step() → ejecuta un tick

get_state() → devuelve TrafficState

stop() → libera recursos

Todos los engines deben cumplir esta interfaz.

runtime/engines/threading_engine.py

Motor basado en hilos.

Responsabilidades:

Crear semáforos y controlador

Crear uno o más hilos

Sincronizar ejecución por tick

Debe usar:

Lock, Condition, Event u otros mecanismos

Memoria compartida

Debe garantizar:

Ejecución segura

Sincronización correcta

Actualización consistente del estado

runtime/engines/multiprocessing_engine.py

Motor basado en procesos.

Responsabilidades:

Crear procesos independientes

Comunicar estado mediante colas o pipes

Agregar resultados en el proceso principal

Debe usar:

multiprocessing.Queue, Pipe, Event, etc.

Comunicación explícita (no memoria compartida directa)

Debe garantizar:

Coordinación correcta

Serialización de datos

Cierre limpio de procesos

runtime/comms/messages.py

(Optativo pero recomendado)

Define estructuras de mensajes para multiprocessing.

Ejemplos:

Comandos a procesos:

cambiar color

ejecutar tick

detener proceso

Reportes desde procesos:

vehículos cruzados

tamaño de cola

métricas parciales

4.3 APP – Ejecución
app/config.py

Contiene parámetros de configuración:

Duración de luces

Número de ticks

Probabilidad de llegada de vehículos

Capacidad de cruce

Debe permitir modificar la simulación sin tocar código lógico.

app/sim.py

Punto de entrada del backend.

Responsabilidades:

Leer modo de ejecución (threading o multiprocessing)

Inicializar el engine

Ejecutar múltiples ticks (≥ 10 ciclos)

Mostrar resultados finales

Debe ser posible ejecutarlo con:

python -m backend.app.sim threading
python -m backend.app.sim multiprocessing

4.4 TESTS
tests/test_controlador.py

Verifica:

Alternancia correcta de fases

Conteo de ciclos

Estados válidos

tests/test_semaforo.py

Verifica:

Despacho correcto en verde

No despacho en rojo

Respeto de capacidad por tick

5. Flujo de ejecución (tick)

El controlador decide el plan de luces

El engine aplica el plan

Llegan vehículos

Semáforos ejecutan tick

Se actualizan estadísticas

Se construye TrafficState

6. Resultado esperado

Al finalizar la simulación:

Se completan al menos 10 ciclos

Se generan estadísticas válidas

Ambas versiones (hilos y procesos) producen resultados coherentes

El diseño permite agregar GUI sin modificar el backend

7. Criterios de evaluación cumplidos

✔ Programación orientada a objetos

✔ Concurrencia con hilos

✔ Concurrencia con procesos

✔ Sincronización explícita

✔ Arquitectura limpia y modular

✔ Código mantenible y extensible

8. Nota final

Este backend está diseñado para:

crecer sin romperse

facilitar el trabajo en equipo

demostrar comprensión real de concurrencia

Si una clase cambia de motor (hilos → procesos) y no hay que tocarla, el diseño es correcto.