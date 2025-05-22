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
