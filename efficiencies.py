import numpy
import math

def spillover(n: int, d: float, f: float) -> float:
    """Computes the spillover efficiency"""
    psi0 = math.atan(d/(2*f))
    return 1 - math.pow(math.cos(psi0), n+1)

def phase(p: int) -> float:
    """Computes the phase efficiency"""
    delta = 2*math.pi/p
    return math.pow(math.sin(delta/2)/(delta/2), 2)

def illumination(n: int, d: float, f: float) -> float:
    """Computes the illumination efficiency"""
    psi0 = math.atan(d/(2*f))
    numerator1 = 2 - 2*math.pow(math.cos(psi0), n/2 + 2)
    denominator1 = n + 4
    numerator2 = 1 - math.pow(math.cos(psi0), n + 1)
    denominator2 = n + 1
    return math.pow(numerator1/denominator1, 2)/(numerator2/denominator2)
