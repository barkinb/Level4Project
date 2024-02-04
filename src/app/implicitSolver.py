import numpy as np
from scipy.optimize import least_squares


# Define the implicit equation function
def implicit_equation(x, y):
    return 4 * (676 * x ** 2 - 2548 * x * y - 698384 * x + 2401 * y ** 2 - 1250136 * y + 275528592)


# Define the fitting function with the implicit equation as a constraint
def fitting_function(coefficients, xy):
    x, y = xy.T  # Transpose to get the x and y values separately
    a0, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12, a13, a14 = coefficients
    return (a0 +
            a1 * x + a2 * y +
            a3 * x ** 2 + a4 * x * y + a5 * y ** 2 +
            a6 * x ** 3 + a7 * x ** 2 * y + a8 * x * y ** 2 + a9 * y ** 3 +
            a10 * x ** 4 + a11 * x ** 3 * y + a12 * x ** 2 * y ** 2 + a13 * x * y ** 3 + a14 * y ** 4)


# Define the constraint function
def constraint_function(coefficients, xy):
    x, y = xy.T  # Transpose to get the x and y values separately
    return implicit_equation(x, y) - fitting_function(coefficients, xy)


# Define the objective function with penalty term for constraints
def objective_function(coefficients, xy_values, axis_values):
    errors = axis_values - fitting_function(coefficients, xy_values)
    constraint_errors = constraint_function(coefficients, xy_values)
    return np.concatenate([errors, constraint_errors])


# Given points with their x, y coordinates and corresponding axis values
points = [
    (144, 150, 0.4),
    (81.5, 265.5, 0.1),
    (115.5, 181.5, 0.3)
]

# Extract x, y coordinates and corresponding axis values
xy_values = np.array([(point[0], point[1]) for point in points])
axis_values = np.array([point[2] for point in points])

# Initial guess for coefficients
initial_guess = [1.0] * 15  # Initial guess for 15 coefficients

# Optimize the coefficients while satisfying the implicit equation as a constraint
result = least_squares(objective_function, initial_guess, args=(xy_values, axis_values), bounds=(-np.inf, np.inf))

# Extract the optimized coefficients
popt = result.x

# Print the coefficients of the fitted function
print("Coefficients:", popt)

var = [1.57573196e+01, 1.93832974e+00, 9.99596299e-01, 9.99804881e-01,
       9.99463668e-01, 9.98948292e-01, 9.92744666e-01, 9.80113998e-01,
       9.62200430e-01, 9.77085313e-01, 7.30930079e-01, 3.46595049e-01,
       -3.65628120e-01, 3.91583118e-02, -2.87861718e-03]


def evaluate_axis_value(x, y, coefficients):
    a0, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12, a13, a14 = coefficients
    return (a0 +
            a1 * x + a2 * y +
            a3 * x ** 2 + a4 * x * y + a5 * y ** 2 +
            a6 * x ** 3 + a7 * x ** 2 * y + a8 * x * y ** 2 + a9 * y ** 3 +
            a10 * x ** 4 + a11 * x ** 3 * y + a12 * x ** 2 * y ** 2 + a13 * x * y ** 3 + a14 * y ** 4)


print(evaluate_axis_value(144, 150,popt))
