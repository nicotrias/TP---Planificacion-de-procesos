"""Salida por pantalla: Gantt en texto, tabla por proceso y comparativa."""
from motor import calcular


def imprimir_resultado(res):
    m = calcular(res)
    print()
    print("=" * 72)
    print(f"ALGORITMO: {res.politica}")
    print("=" * 72)
    print()
    print(gantt(res))
    print()
    print("Leyenda: # ejecutando   o esperando E/S   . en READY   (vacio) fuera del sistema")
    print()
    print(tabla_procesos(res))
    print()
    print(f"Promedios: espera {m.espera:.2f} | retorno {m.retorno:.2f} | respuesta {m.respuesta:.2f}")
    print(f"Espera maxima: {m.espera_max} | CPU ocupada: {m.cpu_util:.1f}% | "
          f"despachos: {m.despachos} | desalojos: {m.desalojos} | "
          f"throughput: {m.throughput:.3f} proc/u")
    print(f"Orden de despacho: {' -> '.join(map(str, res.despachos))}")


def tabla_comparativa(resultados):
    filas = []
    for res in resultados:
        m = calcular(res)
        filas.append([
            res.politica,
            f"{m.espera:.2f}",
            f"{m.retorno:.2f}",
            f"{m.respuesta:.2f}",
            f"{m.cpu_util:.1f}%",
            m.despachos,
            m.desalojos,
            "-".join(map(str, res.despachos)),
        ])
    cab = ["Algoritmo", "Espera prom", "Retorno prom", "Respuesta prom",
           "CPU", "Despachos", "Desalojos", "Orden de despacho"]
    return ("\nTABLA COMPARATIVA (misma carga y mismas reglas para los tres)\n"
            + "=" * 72 + "\n" + _tabla(cab, filas, izquierda={0, 7}) + "\n")


def gantt(res):
    """Un caracter por unidad de tiempo. La ultima fila es el CPU."""
    ancho = max(2, len(str(max(p.pid for p in res.procesos))) + 1)
    etiqueta = max(len(p.nombre) for p in res.procesos) + 2

    lineas = [" " * etiqueta + "".join(f"{t:<{ancho}}" for t in range(res.makespan))]
    for p in res.procesos:
        fila = "".join(c * ancho for c in res.estados[p.pid])
        lineas.append(f"{p.nombre:<{etiqueta}}{fila}")
    fila_cpu = "".join(f"{x if x is not None else '-':<{ancho}}" for x in res.cpu)
    lineas.append(f"{'CPU':<{etiqueta}}{fila_cpu}")
    return "\n".join(lineas)


def tabla_procesos(res):
    filas = []
    for p in res.procesos:
        rafaga = sum(d for tipo, d in p.bursts if tipo == "CPU")
        filas.append([
            p.pid, p.nombre, p.llegada, rafaga, p.fin,
            p.fin - p.llegada, p.espera, p.espera_io,
            p.primer_despacho - p.llegada,
        ])
    cab = ["PID", "Proceso", "Llegada", "Rafaga", "Fin", "Retorno",
           "Espera", "E/S", "Respuesta"]
    return _tabla(cab, filas, izquierda={1})


def _tabla(cab, filas, izquierda=()):
    anchos = [max(len(str(f[i])) for f in [cab] + filas) for i in range(len(cab))]

    def linea(vals):
        celdas = [
            str(v).ljust(anchos[i]) if i in izquierda else str(v).rjust(anchos[i])
            for i, v in enumerate(vals)
        ]
        return "  ".join(celdas).rstrip()

    lineas = [linea(cab), "  ".join("-" * a for a in anchos)]
    lineas += [linea(f) for f in filas]
    return "\n".join(lineas)
