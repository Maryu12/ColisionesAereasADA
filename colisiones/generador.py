# colisiones/generador.py
from typing import List
from random import Random

from .modelos import Avion


def generar_puntos(n: int, max_x: int, max_y: int, seed: int | None = None) -> List[Avion]:
    """
    Genera n aviones con coordenadas aleatorias en el rango [0, max_x] x [0, max_y].
    """
    rnd = Random(seed)
    puntos: List[Avion] = []

    for i in range(n):
        x = rnd.randint(0, max_x)
        y = rnd.randint(0, max_y)
        puntos.append(Avion(id=i, x=float(x), y=float(y)))

    return puntos
