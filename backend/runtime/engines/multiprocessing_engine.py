"""
Engine basado en procesos (multiprocessing).
Ejecuta semáforos como procesos separados con comunicación explícita.
"""
import multiprocessing as mp
import random
from typing import Dict, List
from queue import Empty

from .base import BaseEngine
from ..comms.messages import *
from ...core.common.tipos import Via, Color
from ...core.common.state import TrafficState
from ...core.common.stats import EstadisticasTrafico
from ...core.traffic.semaforo import Semaforo
from ...core.traffic.controlador import ControladorTrafico
from ...core.models.vehiculo import Vehiculo


def worker_semaforo(via: Via, queue_comandos: mp.Queue, queue_respuestas: mp.Queue, capacidad: int):
    """
    Función worker que ejecuta en un proceso separado.
    
    Args:
        via: Vía del semáforo
        queue_comandos: Cola de entrada de comandos
        queue_respuestas: Cola de salida de respuestas
        capacidad: Capacidad de cruce por tick
    """
    semaforo = Semaforo(via=via, capacidad_por_tick=capacidad)
    
    while True:
        try:
            # Esperar comando
            comando: Comando = queue_comandos.get(timeout=1)
            
            if comando.tipo == TipoComando.DETENER:
                # Finalizar proceso
                break
            
            elif comando.tipo == TipoComando.CAMBIAR_COLOR:
                # Cambiar color del semáforo
                color = comando.payload
                semaforo.set_color(color)
                queue_respuestas.put(Respuesta(
                    tipo=TipoRespuesta.ACK,
                    via=via.name,
                ))
            
            elif comando.tipo == TipoComando.AGREGAR_VEHICULO:
                # Agregar vehículo
                vehiculo_id = comando.payload
                vehiculo = Vehiculo(id=vehiculo_id)
                semaforo.agregar_vehiculo(vehiculo)
                queue_respuestas.put(Respuesta(
                    tipo=TipoRespuesta.ACK,
                    via=via.name,
                ))
            
            elif comando.tipo == TipoComando.TICK:
                # Ejecutar tick
                vehiculos_cruzados = semaforo.tick()
                tiempos = [v.tiempo_espera_total for v in vehiculos_cruzados]
                
                # NUEVO: Serializar detalle para animación
                detalle = [
                    {"id": v.id, "tiempo_espera": v.tiempo_espera_total}
                    for v in vehiculos_cruzados
                ]
                
                msg = VehiculosDespachadosMsg(
                    via=via.name,
                    cantidad=len(vehiculos_cruzados),
                    tiempos_espera=tiempos,
                    vehiculos_detalle=detalle
                )
                queue_respuestas.put(Respuesta(
                    tipo=TipoRespuesta.VEHICULOS_DESPACHADOS,
                    via=via.name,
                    payload=msg,
                ))
            
            elif comando.tipo == TipoComando.OBTENER_ESTADO:
                # Usar el método oficial del dominio para el detalle de cola
                vehiculos_cola = semaforo.get_vehiculos_detalle()
                
                # Enviar estado
                estado = EstadoSemaforoMsg(
                    via=via.name,
                    color=semaforo.color.name,
                    tamano_cola=semaforo.tamano_cola,
                    vehiculos_cruzados=semaforo.vehiculos_cruzados_total,
                    vehiculos_cola=vehiculos_cola
                )
                queue_respuestas.put(Respuesta(
                    tipo=TipoRespuesta.ESTADO_SEMAFORO,
                    via=via.name,
                    payload=estado,
                ))
        
        except Empty:
            continue
        except Exception as e:
            queue_respuestas.put(Respuesta(
                tipo=TipoRespuesta.ERROR,
                via=via.name,
                payload=str(e),
                exito=False,
            ))


class MultiprocessingEngine(BaseEngine):
    """
    Engine basado en multiprocessing.
    
    - Cada semáforo se ejecuta en un proceso separado
    - Usa Queue para comunicación
    - No hay memoria compartida directa
    """

    def __init__(self, config):
        """
        Inicializa el engine.
        
        Args:
            config: ConfiguracionSimulacion
        """
        self.config = config
        self._running = False
        
        # Componentes del dominio (proceso principal)
        self.controlador: ControladorTrafico = None
        self.stats = EstadisticasTrafico()
        
        # Comunicación multiproceso
        self.queues_comandos: Dict[Via, mp.Queue] = {}
        self.queue_respuestas: mp.Queue = None
        self.procesos: Dict[Via, mp.Process] = {}
        
        # Estado de semáforos (cache en proceso principal)
        self.estados_semaforos: Dict[Via, EstadoSemaforoMsg] = {}
        
        # Contador de vehículos
        self._next_vehicle_id = 0
        
        # Sistema de eventos y tránsito
        self._eventos_tick: List[Dict] = []
        self._vehiculos_en_transito: Dict[str, List[Dict]] = {}

    def start(self) -> None:
        """Inicializa el sistema."""
        if self._running:
            return
        
        # Crear controlador (en proceso principal)
        self.controlador = ControladorTrafico(
            duracion_verde=self.config.duracion_verde,
            duracion_amarillo=self.config.duracion_amarillo,
        )
        
        # Crear colas
        self.queue_respuestas = mp.Queue()
        
        # Crear proceso para cada semáforo
        for via in Via:
            queue_cmd = mp.Queue()
            self.queues_comandos[via] = queue_cmd
            
            proceso = mp.Process(
                target=worker_semaforo,
                args=(via, queue_cmd, self.queue_respuestas, self.config.capacidad_cruce_por_tick),
                daemon=True,
            )
            proceso.start()
            self.procesos[via] = proceso
            
            # Inicializar estado en cache
            self.estados_semaforos[via] = EstadoSemaforoMsg(
                via=via.name,
                color="ROJO",
                tamano_cola=0,
                vehiculos_cruzados=0,
            )
        
        self._running = True

    def step(self) -> TrafficState:
        """Tick de simulación con captura de eventos y tránsito."""
        if not self._running:
            raise RuntimeError("Engine no está corriendo.")
        
        # Limpiar datos del tick anterior
        self._eventos_tick = []
        self._vehiculos_en_transito = {}
        
        # Guardar colores anteriores
        colores_anteriores = {via: self.estados_semaforos[via].color for via in Via}
        
        # 1. Controlador decide el plan de luces
        plan = self.controlador.avanzar_tick()
        
        # 2. Enviar comandos de cambio de color y detectar eventos
        for via, color in plan.items():
            color_anterior = colores_anteriores[via]
            self.queues_comandos[via].put(Comando(
                tipo=TipoComando.CAMBIAR_COLOR, via=via.name, payload=color
            ))
            
            if color_anterior != color.name:
                self._eventos_tick.append({
                    "tipo": "cambio_semaforo", "via": via.name,
                    "color_anterior": color_anterior, "color_nuevo": color.name,
                    "icono": self._get_icono_color(color.name)
                })
        
        self._esperar_respuestas(len(Via), TipoRespuesta.ACK)
        
        # 3. Simular llegada de vehículos
        self._simular_llegada_vehiculos()
        
        # 4. Enviar comando TICK
        for via in Via:
            self.queues_comandos[via].put(Comando(tipo=TipoComando.TICK, via=via.name))
        
        # 5. Recopilar respuestas y generar tránsito
        respuestas = self._esperar_respuestas(len(Via), TipoRespuesta.VEHICULOS_DESPACHADOS)
        for resp in respuestas:
            if resp.payload:
                msg: VehiculosDespachadosMsg = resp.payload
                # Registrar en stats
                vehiculos_sim = [Vehiculo(id=v['id']) for v in msg.vehiculos_detalle]
                self.stats.registrar_vehiculos(vehiculos_sim, msg.via)
                
                # Tránsito para animación
                if msg.vehiculos_detalle:
                    self._vehiculos_en_transito[msg.via] = []
                    for idx, v_info in enumerate(msg.vehiculos_detalle):
                        progreso = (idx + 1) / len(msg.vehiculos_detalle)
                        self._vehiculos_en_transito[msg.via].append({
                            "id": v_info['id'], "progreso": progreso
                        })
                        self._eventos_tick.append({
                            "tipo": "vehiculo_despachado", "via": msg.via,
                            "vehiculo_id": v_info['id'], "icono": "🚗✓"
                        })
        
        # 6. Obtener estado de semáforos
        self._actualizar_estados_semaforos()
        
        return self._construir_estado()

    def _get_icono_color(self, color: str) -> str:
        return {"VERDE": "🟢", "AMARILLO": "🟡", "ROJO": "🔴"}.get(color, "⚪")

    def _simular_llegada_vehiculos(self) -> None:
        """Simula llegada aleatoria de vehículos."""
        for via in Via:
            if random.random() < self.config.probabilidad_llegada:
                v_id = self._next_vehicle_id
                self.queues_comandos[via].put(Comando(
                    tipo=TipoComando.AGREGAR_VEHICULO,
                    via=via.name,
                    payload=v_id,
                ))
                self._next_vehicle_id += 1
                self._eventos_tick.append({
                    "tipo": "vehiculo_llego", "via": via.name,
                    "vehiculo_id": v_id, "icono": "🚗→"
                })

    def _esperar_respuestas(self, cantidad: int, tipo_esperado: TipoRespuesta) -> List[Respuesta]:
        """Espera N respuestas de un tipo específico."""
        respuestas = []
        while len(respuestas) < cantidad:
            try:
                resp: Respuesta = self.queue_respuestas.get(timeout=2)
                if resp.tipo == tipo_esperado:
                    respuestas.append(resp)
            except:
                break
        return respuestas

    def _actualizar_estados_semaforos(self) -> None:
        """Solicita y actualiza el estado de todos los semáforos."""
        for via in Via:
            self.queues_comandos[via].put(Comando(
                tipo=TipoComando.OBTENER_ESTADO,
                via=via.name,
            ))
        
        respuestas = self._esperar_respuestas(len(Via), TipoRespuesta.ESTADO_SEMAFORO)
        for resp in respuestas:
            if resp.payload:
                via_enum = Via[resp.via]
                self.estados_semaforos[via_enum] = resp.payload

    def _construir_estado(self) -> TrafficState:
        """Construye el estado actual del sistema."""
        luces = {
            via.name: self.estados_semaforos[via].color
            for via in Via
        }
        
        colas = {
            via.name: self.estados_semaforos[via].tamano_cola
            for via in Via
        }
        
        # NUEVO: Timing de fase
        timing_fase = self.controlador.get_timing_fase()
        
        # NUEVO: Configuración
        configuracion = {
            "duracion_verde": self.config.duracion_verde,
            "duracion_amarillo": self.config.duracion_amarillo,
            "capacidad_cruce": self.config.capacidad_cruce_por_tick,
            "probabilidad_llegada": self.config.probabilidad_llegada,
            "intervalo_tick": self.config.intervalo_tick,
        }
        
        import sys
        info_sistema = {
            "motor": "Multiprocessing",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "procesos_activos": sum(1 for p in self.procesos.values() if p.is_alive()),
        }
        
        return TrafficState(
            tick=self.controlador.tick_actual,
            ciclo=self.controlador.ciclo_actual,
            fase=self.controlador.fase_actual,
            luces=luces,
            colas=colas,
            estadisticas=self.stats.get_resumen(),
            info_sistema=info_sistema,
            # Detalles recuperados del cache de estados
            vehiculos_detalle={
                via.name: self.estados_semaforos[via].vehiculos_cola
                for via in Via
            },
            vehiculos_en_transito=self._vehiculos_en_transito,
            eventos_tick={"eventos": self._eventos_tick},
            timing_fase=timing_fase,
            configuracion=configuracion,
        )

    def get_state(self) -> TrafficState:
        """Obtiene el estado actual sin avanzar."""
        self._actualizar_estados_semaforos()
        return self._construir_estado()

    def stop(self) -> None:
        """Detiene el engine y todos los procesos."""
        if not self._running:
            return
        
        # Enviar comando de detener a todos
        for via in Via:
            self.queues_comandos[via].put(Comando(
                tipo=TipoComando.DETENER,
                via=via.name,
            ))
        
        # Esperar a que terminen
        for proceso in self.procesos.values():
            proceso.join(timeout=2)
            if proceso.is_alive():
                proceso.terminate()
        
        self._running = False

    def is_running(self) -> bool:
        """Verifica si está corriendo."""
        return self._running

    def __repr__(self) -> str:
        return f"MultiprocessingEngine(running={self._running}, procesos={len(self.procesos)})"
