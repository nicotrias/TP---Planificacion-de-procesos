# Simulador de planificación de CPU

Trabajo Práctico Integrador — Sistemas Operativos — 2C 2026

Simulador de un planificador de CPU de un solo núcleo que compara **FCFS, SJF y
SRTF** sobre la misma carga, con ráfagas de E/S, y emite métricas de rendimiento
y el diagrama de Gantt de cada corrida.

## Requisitos

Python 3.10 o superior. Sin dependencias externas.

## Cómo correrlo

```
python main.py
```

La salida muestra, para cada perfil de carga, la tabla comparativa de los tres
algoritmos. Para la carga mixta se imprime además el detalle por proceso y el
Gantt de cada política.

Leyenda del Gantt: `#` ejecutando, `o` esperando E/S, `.` en READY, espacio
fuera del sistema. La última fila indica qué proceso usó el CPU en cada unidad
de tiempo (`-` = CPU ocioso).

## Estructura

| Archivo | Rol |
|---|---|
| `pcb.py` | PCB y estados del proceso |
| `algoritmos.py` | Políticas FCFS, SJF y SRTF |
| `motor.py` | Reloj, colas, transiciones y métricas |
| `reporte.py` | Gantt en texto y tablas |
| `cargas.py` | Perfiles de carga de prueba |
| `main.py` | Corre los tres algoritmos sobre cada perfil |

La separación es deliberada: el motor implementa el mecanismo (reloj, colas,
contabilidad) y las políticas solo deciden a quién le toca el CPU. Agregar una
política nueva no requiere tocar el motor.

## Perfiles de carga

| Perfil | Qué representa |
|---|---|
| Mixta | Tareas cortas, largas y con acceso a disco |
| Uniforme | Todas las ráfagas iguales, sin E/S (grupo de control) |
| Mucha E/S | Ráfagas de CPU cortas y E/S largas |

## Validación

`secuencia_anexo5()` reproduce el ejemplo FCFS del Anexo 5 del apunte. Para
correrlo aislado:

```python
from cargas import secuencia_anexo5
from algoritmos import POLITICAS
from motor import simular
from reporte import imprimir_resultado

imprimir_resultado(simular(secuencia_anexo5(), POLITICAS[0]))
```

El motor verifica en cada corrida que `espera + CPU + E/S = fin - llegada` para
cada proceso y que el tiempo ocupado coincida con `makespan - ocioso`. Si alguna
de esas condiciones falla, la simulación se detiene con un error explícito.
