import numpy as np
import math


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
    a0, a1, a2, a3, a4, a5, a6, a7 = coefficients

    if np.allclose(diffs, diffs[0]):  # Linear fitting
        return a0 + a1 * x + a2 * y

    if np.any(diffs != 0) and np.all(diffs[0] != 0):
        if np.all(x > 0) and np.all(y > 0):  # Check for positive x and y
            if np.allclose(np.log(diffs), np.log(diffs[0])):  # Logarithmic fitting
                return a0 + a1 * np.log(x) + a2 * np.log(y)

    # Third-order implicit fitting (default)
    return (a0 * x ** 3 + a1 * x ** 2 * y + a2 * x * y ** 2 + a3 * y ** 3 +
            a4 * x ** 2 + a5 * x * y + a6 * y ** 2 + a7)


def objective_function(coefficients, xy_values, axis_values, diffs):
    errors = axis_values - fitting_function(coefficients, xy_values, diffs)
    return errors
