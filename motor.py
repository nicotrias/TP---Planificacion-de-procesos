"""Motor de simulacion: hace de kernel.

Avanza el reloj de a una unidad, admite llegadas, mueve procesos entre estados
y acumula las metricas. No conoce ningun algoritmo: la decision de a quien le
toca el CPU la toma la politica que recibe por parametro.

Cada unidad de tiempo se procesa siempre con el mismo orden de eventos:
  1. admision de llegadas
  2. vuelta a READY de los que terminaron su E/S
  3. desalojo (solo politicas expropiativas)
  4. despacho si el CPU quedo libre
  5. ejecucion y contabilizacion de [ahora, ahora + 1)
  6. transicion al terminar la rafaga (siguiente E/S o fin del proceso)
"""
from collections import deque
from copy import deepcopy
from dataclasses import dataclass

from pcb import PCB, Estado


@dataclass
class Resultado:
    politica: str
    procesos: list
    cpu: list          # pid que uso el CPU en cada unidad (None = ocioso)
    estados: dict      # pid -> un caracter por unidad de tiempo
    despachos: list    # orden en que se asigno el CPU
    desalojos: int
    ocioso: int
    makespan: int


@dataclass
class Metricas:
    espera: float
    retorno: float
    respuesta: float
    espera_max: int
    cpu_util: float
    throughput: float
    despachos: int
    desalojos: int


def simular(procesos, politica):
    carga = deepcopy(procesos)      # cada algoritmo parte de la misma carga
    pendientes = sorted(carga, key=lambda p: (p.llegada, p.pid))
    listos = deque()                # cola de preparados (READY)
    bloqueados = []                 # esperando E/S (WAITING)

    estados = {p.pid: [] for p in carga}
    cpu = []
    despachos = []
    desalojos = 0
    ocioso = 0
    ahora = 0
    corriendo = None

    while pendientes or listos or bloqueados or corriendo is not None:
        # 1. admision
        while pendientes and pendientes[0].llegada <= ahora:
            p = pendientes.pop(0)
            p.estado = Estado.LISTO
            p.restante = p.bursts[0][1]
            listos.append(p)

        # 2. fin de E/S: vuelven a la cola de preparados con su proxima rafaga
        for p in [p for p in bloqueados if p.despertar <= ahora]:
            bloqueados.remove(p)
            p.indice_burst += 1
            if p.indice_burst >= len(p.bursts):
                # la E/S era la ultima operacion del proceso
                p.estado = Estado.TERMINADO
                p.fin = p.despertar
                continue
            p.estado = Estado.LISTO
            p.restante = p.bursts[p.indice_burst][1]
            listos.append(p)

        # 3. desalojo
        if politica.expropiativa and corriendo is not None and listos:
            candidato = politica.elegir(listos)
            if candidato.restante < corriendo.restante:
                corriendo.estado = Estado.LISTO
                listos.append(corriendo)
                corriendo = None
                desalojos += 1

        # 4. despacho
        if corriendo is None and listos:
            corriendo = politica.elegir(listos)
            listos.remove(corriendo)
            corriendo.estado = Estado.EJECUTANDO
            if corriendo.primer_despacho is None:
                corriendo.primer_despacho = ahora
            despachos.append(corriendo.pid)

        # 5. se contabiliza la unidad de tiempo [ahora, ahora + 1)
        for p in listos:
            p.espera += 1
        for p in bloqueados:
            p.espera_io += 1
        for p in carga:
            estados[p.pid].append(_char(p.estado))

        if corriendo is None:
            cpu.append(None)
            ocioso += 1
        else:
            corriendo.cpu += 1
            corriendo.restante -= 1
            cpu.append(corriendo.pid)

        # 6. se agoto la rafaga de CPU
        if corriendo is not None and corriendo.restante == 0:
            if not _avanzar(corriendo, ahora, bloqueados):
                corriendo = None

        ahora += 1

    res = Resultado(
        politica=politica.nombre,
        procesos=carga,
        cpu=cpu,
        estados=estados,
        despachos=despachos,
        desalojos=desalojos,
        ocioso=ocioso,
        makespan=ahora,
    )
    validar(res)
    return res


def _char(estado):
    """Como se dibuja cada estado en el diagrama de Gantt."""
    return {
        Estado.NUEVO: " ",
        Estado.LISTO: ".",
        Estado.EJECUTANDO: "#",
        Estado.ESPERANDO: "o",
        Estado.TERMINADO: " ",
    }[estado]


def _avanzar(p, ahora, bloqueados):
    """Termino la rafaga de CPU en el instante 'ahora + 1'.

    Devuelve True si el proceso sigue en el CPU (rafaga de CPU seguida).
    """
    while True:
        p.indice_burst += 1
        if p.indice_burst >= len(p.bursts):
            p.estado = Estado.TERMINADO
            p.fin = ahora + 1
            return False
        tipo, duracion = p.bursts[p.indice_burst]
        if tipo == "CPU":
            p.restante = duracion
            return True
        p.estado = Estado.ESPERANDO
        p.despertar = ahora + 1 + duracion
        bloqueados.append(p)
        return False


def calcular(res):
    n = len(res.procesos)
    return Metricas(
        espera=sum(p.espera for p in res.procesos) / n,
        retorno=sum(p.fin - p.llegada for p in res.procesos) / n,
        respuesta=sum(p.primer_despacho - p.llegada for p in res.procesos) / n,
        espera_max=max(p.espera for p in res.procesos),
        cpu_util=(res.makespan - res.ocioso) / res.makespan * 100,
        throughput=n / res.makespan,
        despachos=len(res.despachos),
        desalojos=res.desalojos,
    )


def validar(res):
    """Dos invariantes que tienen que cerrar siempre.

    Si alguno falla, hay un error en la contabilidad del motor.
    """
    for p in res.procesos:
        total = p.espera + p.cpu + p.espera_io
        estancia = p.fin - p.llegada
        if total != estancia:
            raise AssertionError(
                f"PID {p.pid}: espera+CPU+E/S={total} pero fin-llegada={estancia}"
            )
    ocupado = sum(p.cpu for p in res.procesos)
    if ocupado != res.makespan - res.ocioso:
        raise AssertionError("El tiempo ocupado no coincide con el makespan")
