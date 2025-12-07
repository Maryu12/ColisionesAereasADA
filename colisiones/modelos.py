# colisiones/modelos.py
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Avion:
    """
    Representa un avión/punto en el plano.
    id: identificador del avión
    x, y: coordenadas
    """
    id: int
    x: float
    y: float


@dataclass
class ResultadoColision:
    """
    Resultado del algoritmo:
    - distancia: mínima distancia entre aviones (euclídea)
    - pares: lista de pares (Avion, Avion) que están a esa distancia
    """
    distancia: float
    pares: List[Tuple[Avion, Avion]]
