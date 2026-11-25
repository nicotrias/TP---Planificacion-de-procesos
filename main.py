"""Corre los tres algoritmos sobre cada perfil de carga y compara."""
from algoritmos import POLITICAS
from cargas import CARGAS
from motor import simular
from reporte import imprimir_resultado, tabla_comparativa


def main():
    for nombre, secuencia, detalle in CARGAS:
        print()
        print("#" * 72)
        print(f"# CARGA: {nombre}")
        print("#" * 72)

        carga = secuencia()
        resultados = [simular(carga, politica) for politica in POLITICAS]

        if detalle:
            for res in resultados:
                imprimir_resultado(res)
        print(tabla_comparativa(resultados))


if __name__ == "__main__":
    main()
