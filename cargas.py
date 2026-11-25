"""Secuencias de prueba.

Formato de cada proceso: lista de rafagas que alterna CPU y E/S, siempre
empezando por CPU. Las duraciones son unidades de tiempo de simulacion.

Los perfiles buscan responder que algoritmo conviene segun el tipo de carga:
  - mixta:    tareas cortas, largas y con acceso a disco (el caso de la nube)
  - uniforme: todas las rafagas iguales, sin E/S (grupo de control)
  - io:       mucho bloqueo, el CPU se queda sin trabajo
"""
from pcb import PCB


def secuencia_ejemplo():
    """Carga mixta: tareas cortas, largas y con acceso a disco."""
    return [
        PCB(pid=1, nombre="P1", llegada=0,
            bursts=[("CPU", 7), ("IO", 3), ("CPU", 4)]),
        PCB(pid=2, nombre="P2", llegada=2,
            bursts=[("CPU", 3)]),
        PCB(pid=3, nombre="P3", llegada=4,
            bursts=[("CPU", 2), ("IO", 2), ("CPU", 2)]),
        PCB(pid=4, nombre="P4", llegada=6,
            bursts=[("CPU", 6)]),
        PCB(pid=5, nombre="P5", llegada=8,
            bursts=[("CPU", 1)]),
    ]


def secuencia_uniforme():
    """Seis tareas de 5 unidades, sin E/S. Grupo de control.

    Como todas las rafagas son iguales, SJF y SRTF no tienen nada que
    optimizar: los tres algoritmos DEBEN dar exactamente lo mismo.
    """
    return [
        PCB(pid=i + 1, nombre=f"P{i+1}", llegada=i, bursts=[("CPU", 5)])
        for i in range(6)
    ]


def secuencia_io():
    """Carga con mucho bloqueo por E/S.

    Las rafagas de CPU son cortas y las de E/S largas, asi que el CPU pasa
    ratos sin nadie listo. Sirve para ver como el orden de despacho cambia
    el solapamiento entre CPU y E/S.
    """
    return [
        PCB(pid=1, nombre="P1", llegada=0,
            bursts=[("CPU", 4), ("IO", 8), ("CPU", 2)]),
        PCB(pid=2, nombre="P2", llegada=0,
            bursts=[("CPU", 1), ("IO", 6), ("CPU", 2)]),
        PCB(pid=3, nombre="P3", llegada=1,
            bursts=[("CPU", 2), ("IO", 5), ("CPU", 1)]),
        PCB(pid=4, nombre="P4", llegada=2,
            bursts=[("CPU", 1), ("IO", 7), ("CPU", 1)]),
        PCB(pid=5, nombre="P5", llegada=4,
            bursts=[("CPU", 2), ("IO", 4), ("CPU", 2)]),
    ]


def secuencia_anexo5():
    """Ejemplo FCFS del Anexo 5 del apunte (pag. 144).

    La columna 'inicio' de la tabla se toma tal cual como tiempo de llegada.
    """
    return [
        PCB(pid=1, nombre="P1", llegada=1,
            bursts=[("CPU", 2), ("IO", 2), ("CPU", 3), ("IO", 1)]),
        PCB(pid=2, nombre="P2", llegada=3,
            bursts=[("CPU", 3), ("IO", 1), ("CPU", 2), ("IO", 4), ("CPU", 2)]),
        PCB(pid=3, nombre="P3", llegada=4,
            bursts=[("CPU", 2), ("IO", 3), ("CPU", 2)]),
    ]


# (nombre para mostrar, funcion que arma la carga, mostrar Gantt por algoritmo)
CARGAS = [
    ("Mixta (demo)", secuencia_ejemplo, True),
    ("Uniforme (control)", secuencia_uniforme, False),
    ("Con mucha E/S", secuencia_io, False),
]
