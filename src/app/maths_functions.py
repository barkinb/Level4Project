import numpy as np
import math
from scipy.optimize import least_squares


def ni(n, i):
    return math.factorial(n) / (math.factorial(i) * math.factorial(n - i))


def basis(n, i, t):
    j = np.array(ni(n, i) * (t ** i) * (1 - t) ** (n - i))
    return j


def calculate_angle(point1, point2):
    x, y = point1[0] - point2[0], point1[1] - point2[1]
    return math.atan2(y, x)


def fitting_function(coefficients, xy, diffs):
    x, y = xy.T
    if np.allclose(diffs, diffs[0]):  # Linear fitting
        print("Linear fitting")
        a0, a1, a2 = coefficients[0:2]
        return a0 + a1 * x + a2 * y
    elif np.allclose(np.log(diffs), np.log(diffs[0])):  # Logarithmic fitting
        print("Logarithmic fitting")
        a0, a1, a2 = coefficients[0:2]
        return a0 + a1 * np.log(x) + a2 * np.log(y)
    else:  # Polynomial fitting
        print("Polynomial fitting")
        a0, a1, a2, a3, a4, a5 = coefficients
        return (a0 + a1 * x + a2 * y +
                a3 * x ** 2 + a4 * x * y + a5 * y ** 2)

def objective_function(coefficients, xy_values, axis_values, diffs):
    errors = axis_values - fitting_function(coefficients, xy_values, diffs)
    return errors
