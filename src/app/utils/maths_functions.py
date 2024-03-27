import numpy as np
from scipy.spatial.distance import cdist


def fitting_function(coefficients, xy, eq_type):
    """Calculates the fitting at a point"""
    x,y = xy.T
    a0, a1, a2, a3, a4, a5, a6, a7 = coefficients
    if eq_type == 'lin':
        return a0 * x + a1 * y + a2
    if eq_type == 'log':
        return a0 * np.log(x) + a1 * np.log(y) + a2
    else:
        return (a0 * x ** 3 + a1 * x ** 2 * y + a2 * x * y ** 2 + a3 * y ** 3 +
                a4 * x ** 2 + a5 * x * y + a6 * y ** 2 + a7)

def objective_function(coefficients, xy_values, axis_values, eq_type):
    """Objective function for a given set of points and the inaccuracy in the
    calculated value and the true value on
    the nomogram."""
    errors = axis_values - fitting_function(coefficients, xy_values, eq_type)
    return errors

def get_closest_point(nodes, x, y, allow_out_of_bounds=False) -> (float, float):
    """Finds the closest point in the given set of points and returns the closest point within a 50 pixel radius"""
    starting_point = x, y
    c_distances = cdist(np.asarray([x, y]).reshape(1, -1), nodes)
    if c_distances.min() > 50:
        if allow_out_of_bounds:
            return starting_point
    else:

        minimum_distance = c_distances.argmin()
        closest_point = nodes[minimum_distance]
        return closest_point


def standard_deviation(value, mean, length) -> float:
    """Calculates the standard deviation of a given probabilistic value"""
    return np.sqrt(np.sum((value - mean) ** 2) / length)
