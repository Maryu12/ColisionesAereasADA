# colisiones/algoritmos.py
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt, fabs
from typing import List, Tuple

from .modelos import Avion, ResultadoColision


ParAviones = Tuple[Avion, Avion]


def _dist2(a: Avion, b: Avion) -> float:
    """Distancia euclídea al cuadrado entre dos aviones."""
    dx = a.x - b.x
    dy = a.y - b.y
    return dx * dx + dy * dy


def fuerza_bruta(puntos: List[Avion]) -> ResultadoColision:
    """
    Algoritmo de fuerza bruta O(n^2).
    Útil para comparar y como caso base del divide y vencerás.
    """
    n = len(puntos)
    if n < 2:
        return ResultadoColision(float("inf"), [])

    mejor_dist2 = float("inf")
    pares: List[ParAviones] = []

    for i in range(n):
        for j in range(i + 1, n):
            d2 = _dist2(puntos[i], puntos[j])
            if d2 < mejor_dist2:
                mejor_dist2 = d2
                pares = [(puntos[i], puntos[j])]
            elif d2 == mejor_dist2:
                pares.append((puntos[i], puntos[j]))

    return ResultadoColision(sqrt(mejor_dist2), pares)


# ===== Divide y Vencerás (versión interna usando dist^2) =====

@dataclass
class _ResultadoInterno:
    distancia2: float
    pares: List[ParAviones]


def _par_mas_cercano_dyv_rec(px: List[Avion], py: List[Avion]) -> _ResultadoInterno:
    """
    px: puntos ordenados por x
    py: mismos puntos ordenados por y
    """
    n = len(px)

    # Caso base: pocos puntos -> fuerza bruta
    if n <= 3:
        res = fuerza_bruta(px)
        return _ResultadoInterno(res.distancia ** 2, res.pares)

    mid = n // 2
    mid_x = px[mid].x

    izquierda_x = px[:mid]
    derecha_x = px[mid:]

    # separar py en izquierda/derecha manteniendo el orden por y
    izquierda_y: List[Avion] = []
    derecha_y: List[Avion] = []
    for p in py:
        if p.x <= mid_x:
            izquierda_y.append(p)
        else:
            derecha_y.append(p)

    # Recursión en izquierda y derecha
    res_izq = _par_mas_cercano_dyv_rec(izquierda_x, izquierda_y)
    res_der = _par_mas_cercano_dyv_rec(derecha_x, derecha_y)

    # Elegimos el mejor de ambos lados
    if res_izq.distancia2 < res_der.distancia2:
        mejor = _ResultadoInterno(res_izq.distancia2, list(res_izq.pares))
    elif res_der.distancia2 < res_izq.distancia2:
        mejor = _ResultadoInterno(res_der.distancia2, list(res_der.pares))
    else:
        mejor = _ResultadoInterno(
            res_izq.distancia2, list(res_izq.pares) + list(res_der.pares)
        )

    d = sqrt(mejor.distancia2)

    # Construimos la franja (strip) alrededor de la línea vertical x = mid_x
    strip: List[Avion] = [p for p in py if fabs(p.x - mid_x) < d]

    # En la franja, cada punto solo se compara con los siguientes mientras
    # la diferencia en y sea menor que d
    m = len(strip)
    for i in range(m):
        j = i + 1
        while j < m and (strip[j].y - strip[i].y) < d:
            d2 = _dist2(strip[i], strip[j])
            if d2 < mejor.distancia2:
                mejor.distancia2 = d2
                mejor.pares = [(strip[i], strip[j])]
                d = sqrt(d2)
            elif d2 == mejor.distancia2:
                mejor.pares.append((strip[i], strip[j]))
            j += 1

    return mejor


def par_mas_cercano_dyv(puntos: List[Avion]) -> ResultadoColision:
    """
    Versión divide y vencerás O(n log n).
    Devuelve la distancia mínima y los pares a esa distancia.
    """
    if len(puntos) < 2:
        return ResultadoColision(float("inf"), [])

    px = sorted(puntos, key=lambda p: p.x)
    py = sorted(puntos, key=lambda p: p.y)

    res_int = _par_mas_cercano_dyv_rec(px, py)
    return ResultadoColision(sqrt(res_int.distancia2), res_int.pares)


# ===== TODAS LAS COLISIONES SEGÚN UMBRAL =====

def pares_en_riesgo(puntos: List[Avion], umbral: float) -> tuple[float, List[ParAviones]]:

    n = len(puntos)
    if n < 2:
        return float("inf"), []

    umbral2 = umbral * umbral
    mejor_dist2 = float("inf")
    pares_riesgo: List[ParAviones] = []

    for i in range(n):
        for j in range(i + 1, n):
            d2 = _dist2(puntos[i], puntos[j])

            # actualizar distancia mínima global
            if d2 < mejor_dist2:
                mejor_dist2 = d2

            # guardar todos los pares dentro del umbral
            if d2 <= umbral2:
                pares_riesgo.append((puntos[i], puntos[j]))

    return sqrt(mejor_dist2), pares_riesgo
