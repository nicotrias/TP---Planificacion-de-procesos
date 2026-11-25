"""Politicas de planificacion.

Cada politica solo decide a quien le toca el CPU. No sabe nada del reloj, de
las colas ni de las metricas: eso es el motor.

Todas comparan lo que el planificador conoce en el momento de decidir: la
rafaga de CPU actual que le queda a cada proceso (PCB.restante).
"""
from dataclasses import dataclass
from typing import Callable

from pcb import PCB


@dataclass(frozen=True)
class Politica:
    nombre: str
    elegir: Callable[[list], PCB]
    expropiativa: bool
    descripcion: str


def fcfs(listos):
    """First Come First Served: el primero de la cola. No expropiativo."""
    return listos[0]


def menor_rafaga(listos):
    """El de menor rafaga actual restante.

    Desempate: por llegada y despues por PID, para que la simulacion sea
    reproducible (si no, dos corridas iguales darian resultados distintos).
    """
    return min(listos, key=lambda p: (p.restante, p.llegada, p.pid))


POLITICAS = [
    Politica("FCFS", fcfs, False, "no expropiativo, orden de llegada"),
    Politica("SJF", menor_rafaga, False, "no expropiativo, rafaga mas corta"),
    Politica("SRTF", menor_rafaga, True,
             "expropiativo: desaloja si aparece uno mas corto"),
]
