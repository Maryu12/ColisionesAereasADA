# colisiones/main.py
from __future__ import annotations

import sys
from time import perf_counter

from .generador import generar_puntos
from .algoritmos import fuerza_bruta, par_mas_cercano_dyv


def pedir_entero(mensaje: str, minimo: int = 1) -> int:
    """Pide un entero válido por consola."""
    while True:
        try:
            valor = int(input(mensaje))
            if valor >= minimo:
                return valor
            else:
                print(f"Por favor, ingresa un número entero >= {minimo}.")
        except ValueError:
            print("Entrada inválida. Intenta de nuevo.")


def pedir_flotante(mensaje: str, minimo: float = 0.0) -> float:
    """Pide un número flotante válido por consola."""
    while True:
        try:
            valor = float(input(mensaje))
            if valor >= minimo:
                return valor
            else:
                print(f"Ingresa un número >= {minimo}.")
        except ValueError:
            print("Entrada inválida. Intenta de nuevo.")


def main(argv: list[str]) -> None:
    # ==============================
    # INTERACCIÓN CON EL USUARIO
    # ==============================
    print("=== Sistema de Detección de Colisiones Aéreas ===\n")

    n = pedir_entero("¿Cuántos aviones quieres generar? (ej: 100): ")
    umbral = pedir_flotante("¿Cuál será el umbral de colisión? (ej: 50.0): ")

    max_x = max_y = 1000  # siempre trabajamos en plano 1000x1000

    print(f"\nGenerando {n} aviones en un plano {max_x}x{max_y}...")
    puntos = generar_puntos(n=n, max_x=max_x, max_y=max_y, seed=42)

    # ==============================
    # Fuerza bruta
    # ==============================
    t0 = perf_counter()
    res_bruta = fuerza_bruta(puntos)
    t1 = perf_counter()

    # ==============================
    # Divide y vencerás
    # ==============================
    t2 = perf_counter()
    res_dyv = par_mas_cercano_dyv(puntos)
    t3 = perf_counter()

    print("\n=== Resultados generales ===")
    print(f"Distancia mínima (fuerza bruta): {res_bruta.distancia:.6f}")
    print(f"Tiempo fuerza bruta: {t1 - t0:.6f} s")

    print(f"\nDistancia mínima (divide y vencerás): {res_dyv.distancia:.6f}")
    print(f"Tiempo divide y vencerás: {t3 - t2:.6f} s")

    # ==============================
    # ANÁLISIS DE POSIBLE COLISIÓN
    # ==============================
    print("\n=== Análisis de posible colisión ===")
    print(f"Umbral de colisión definido: {umbral}")

    if not res_dyv.pares:
        print("No hay suficientes aviones para el análisis.")
        return

    if res_dyv.distancia <= umbral:
        print(f"⚠️  Distancia mínima {res_dyv.distancia:.4f} <= umbral → POSIBLE COLISIÓN DETECTADA")

        # mostrar máximo 5 pares
        pares = res_dyv.pares[:5]

        for idx, (a, b) in enumerate(pares, start=1):
            print(f"#{idx}: Avión {a.id} ({a.x}, {a.y})  <->  Avión {b.id} ({b.x}, {b.y})")

        if len(res_dyv.pares) > 5:
            print(f"... y {len(res_dyv.pares) - 5} pares adicionales con la misma distancia mínima.")

    else:
        print(f"Distancia mínima {res_dyv.distancia:.4f} > umbral → No hay riesgo de colisión.")

    print("\nAnálisis completado.\n")


if __name__ == "__main__":
    main(sys.argv)
