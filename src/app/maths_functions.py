import numpy as np
import math
def ni(n,i):
    return np.math.factorial(n) / (np.math.factorial(i) * np.math.factorial(n-i))

def basis(n,i,t):
    j = np.array(ni(n,i) * (t**i) * (1-t) ** (n-i))
    return j

def calculate_angle(point1,point2):
    x, y = point1[0] - point2[0], point1[1] - point2[1]
    return math.atan2(y, x)

