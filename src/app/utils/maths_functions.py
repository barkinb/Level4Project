import numpy as np

from scipy.spatial.distance import cdist

def fitting_function(coefficients, xy, diffs):
    x, y = xy.T
    a0, a1, a2, a3, a4, a5, a6, a7 = coefficients

    if np.allclose(diffs, diffs[0]):  # Linear fitting
        return a0 + a1 * x + a2 * y

    if np.any(diffs != 0) and np.any(diffs[0] != 0):
        if np.allclose(np.log(diffs), np.log(diffs[0])):  # Logarithmic fitting
            return a0 + a1 * np.log(x) + a2 * np.log(y)

    # Third-order implicit fitting (default)
    return (a0 * x ** 3 + a1 * x ** 2 * y + a2 * x * y ** 2 + a3 * y ** 3 +
            a4 * x ** 2 + a5 * x * y + a6 * y ** 2 + a7)


def objective_function(coefficients, xy_values, axis_values, diffs):
    errors = axis_values - fitting_function(coefficients, xy_values, diffs)
    return errors


def calculate_opencv_closest_point(nodes, x, y):
    starting_point = x, y
    c_distances = cdist(np.asarray([x, y]).reshape(1, -1), nodes)
    if c_distances.min() > 50:
        return starting_point
    else:

        minimum_distance = c_distances.argmin()
        closest_point = nodes[minimum_distance]
        return closest_point
