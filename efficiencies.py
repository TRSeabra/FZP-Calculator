import numpy as np
import math
from scipy.integrate import quad

def spillover(n: int, d: float, f: float) -> float:
    """Computes the spillover efficiency"""
    psi0 = math.atan(d/(2*f))
    return 1 - math.pow(math.cos(psi0), n+1)

def phase(p: int) -> float:
    """Computes the phase efficiency"""
    delta = 2*math.pi/p
    return math.pow(math.sin(delta/2)/(delta/2), 2)

def illumination(n: int, d: float, f: float) -> float:
    """Computes the illumination efficiency """
    psi0 = math.atan(d / (2 * f))
    numerator = (1 - math.pow(math.cos(psi0), (n / 2) + 2)) / ((n / 2) + 2)
    denominator = (1 - math.pow(math.cos(psi0), n + 1)) / (2 * (n + 1))
    return math.pow(numerator, 2) / denominator

def illumination_numerical(n: int, d: float, f:float) -> float:
    psi0 = math.atan(d/(2*f))
    def E(theta):
        return math.sqrt(2 * (n + 1)) * (math.cos(theta) ** (n / 2))
    numerator_integral, _ = quad(lambda theta: E(theta) * math.sin(theta), 0, psi0)
    denominator_integral, _ = quad(lambda theta: (E(theta) ** 2) * math.sin(theta), 0, psi0)
    return (numerator_integral ** 2) / (denominator_integral * (1 - math.cos(psi0)))

def blockage(radii: list[float], d) -> float:
    """Computes the blockage efficiency"""
    total_area = math.pi * math.pow(d/2, 2)
    covered_area = 0
    for i in range(len(radii)-1):
        inner_radius = radii[i]
        outer_radius = radii[i+1]
        # Only consider even-numbered zones
        if i % 2 == 0:
            covered_area += math.pi*((outer_radius**2) - (inner_radius**2))
    return covered_area/total_area

def get_patern(feed_hpbw: float) -> int:
    """Returns the value n that better approximates the feed's gain profile by 2(n+1)cos(theta)^n"""
    n = 1
    hpbw_aprox = 2*math.degrees(math.acos(math.pow(2, -1/n)))
    while True:
        n += 1
        hpbw_next = 2*math.degrees(math.acos(math.pow(2, -1/n)))
        if math.fabs(hpbw_next-feed_hpbw) > math.fabs(hpbw_aprox-feed_hpbw):
            return n-1
        hpbw_aprox = hpbw_next
