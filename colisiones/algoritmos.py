# colisiones/algoritmos.py
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt, fabs
from typing import List, Tuple

from .modelos import Avion, ResultadoColision


ParAviones = Tuple[Avion, Avion]


def _dist2(a: Avion, b: Avion) -> float:
    """Distancia entre dos aviones."""
    dx = a.x - b.x
    dy = a.y - b.y
    return dx * dx + dy * dy


def fuerza_bruta(puntos: List[Avion]) -> ResultadoColision:
   
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


@dataclass
class _ResultadoInterno:
    distancia2: float
    pares: List[ParAviones]


def _par_mas_cercano_dyv_rec(px: List[Avion], py: List[Avion]) -> _ResultadoInterno:
    
    n = len(px)

    
    if n <= 3:
        res = fuerza_bruta(px)
        return _ResultadoInterno(res.distancia ** 2, res.pares)

    mid = n // 2
    mid_x = px[mid].x

    izquierda_x = px[:mid]
    derecha_x = px[mid:]

    
    izquierda_y: List[Avion] = []
    derecha_y: List[Avion] = []
    for p in py:
        if p.x <= mid_x:
            izquierda_y.append(p)
        else:
            derecha_y.append(p)

    
    res_izq = _par_mas_cercano_dyv_rec(izquierda_x, izquierda_y)
    res_der = _par_mas_cercano_dyv_rec(derecha_x, derecha_y)

   
    if res_izq.distancia2 < res_der.distancia2:
        mejor = _ResultadoInterno(res_izq.distancia2, list(res_izq.pares))
    elif res_der.distancia2 < res_izq.distancia2:
        mejor = _ResultadoInterno(res_der.distancia2, list(res_der.pares))
    else:
        mejor = _ResultadoInterno(
            res_izq.distancia2, list(res_izq.pares) + list(res_der.pares)
        )

    d = sqrt(mejor.distancia2)

   
    strip: List[Avion] = [p for p in py if fabs(p.x - mid_x) < d]

    
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
  
    if len(puntos) < 2:
        return ResultadoColision(float("inf"), [])

    px = sorted(puntos, key=lambda p: p.x)
    py = sorted(puntos, key=lambda p: p.y)

    res_int = _par_mas_cercano_dyv_rec(px, py)
    return ResultadoColision(sqrt(res_int.distancia2), res_int.pares)


# colisiones segun el umbral

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

        
            if d2 < mejor_dist2:
                mejor_dist2 = d2

      
            if d2 <= umbral2:
                pares_riesgo.append((puntos[i], puntos[j]))

    return sqrt(mejor_dist2), pares_riesgo
