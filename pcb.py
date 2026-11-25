"""PCB (Process Control Block): la estructura con la que el SO representa un proceso.

Campos: PID, nombre, tiempo de llegada, rafaga y estado. El resto son los
acumuladores que necesita el simulador para calcular las metricas.
"""
from dataclasses import dataclass
from enum import Enum


class Estado(Enum):
    NUEVO = "NEW"              # creado, todavia no llego su instante de llegada
    LISTO = "READY"            # esperando en la cola de preparados
    EJECUTANDO = "RUNNING"     # usando el CPU
    ESPERANDO = "WAITING"      # bloqueado por una operacion de E/S
    TERMINADO = "TERMINATED"   # ya no vuelve a ejecutarse


@dataclass
class PCB:
    pid: int
    nombre: str
    llegada: int                     # instante en que entra al sistema
    bursts: list                     # [("CPU", 7), ("IO", 3), ("CPU", 4)]

    estado: Estado = Estado.NUEVO
    indice_burst: int = 0            # posicion dentro de la lista de rafagas
    restante: int = 0                # lo que falta de la rafaga actual

    cpu: int = 0                     # tiempo total usando el CPU
    espera: int = 0                  # tiempo total en READY  -> Waiting Time
    espera_io: int = 0               # tiempo total bloqueado
    primer_despacho: int | None = None   # para Response Time
    fin: int | None = None               # para Turnaround
    despertar: int = 0               # instante en que termina la E/S
