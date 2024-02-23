import numpy as np
import sympy
from bezier import bezier
from scipy.optimize import least_squares, fsolve

from src.app.utils.maths_functions import objective_function, fitting_function


class BezierTest:
    def __init__(self):
        self.axis_equation_generated = None
        self.axis_equation_coefficients = None
        self.implicit_axis_equation = None
        self.curve = None
        self.x, self.y = sympy.symbols('x y')
        self.initial_guess = [0.0] * 8
        self.axis_points = (40, 664, 200.0), (41, 510, 400.0), (42, 356, 600.0), (41, 205, 800.0), (37.5, 429.5, 500.0), (41, 280, 700.0), (41, 587, 300.0), (37.5, 123.5, 900.0)
        self.xy_values = np.array([(point[0], point[1]) for point in self.axis_points])
        self.axis_values = np.array([point[2] for point in self.axis_points])
        self.diffs = np.diff(self.axis_values)

        result = least_squares(objective_function, self.initial_guess,
                               args=(self.xy_values, self.axis_values, self.diffs))

        popt = result.x
        self.axis_equation_coefficients = popt
        self.axis_equation_generated = True
        self.start_show_axis_points_canvas()

        nodes = np.asfortranarray(
            [(41, 50), (41, 739)]
        )
        self.curve = bezier.Curve.from_nodes(nodes)
        self.implicit_axis_equation = self.curve.implicitize()
        self.xy_values = np.array([(point[0], point[1]) for point in self.axis_points])
        self.axis_values = np.array([point[2] for point in self.axis_points])

    def find_axis_point(self, axis_value):
        def equations(variables):
            x, y = variables
            # Evaluate the curve value and implicit value
            curve_value = fitting_function(self.axis_equation_coefficients, np.array([x, y]), self.diffs) - axis_value
            implicit_value = self.calculate_implicit_equation()(x, y)
            return [curve_value, implicit_value - axis_value]

        initial_guess = np.array([0, 0])
        solution = fsolve(equations.flatten(), initial_guess)

        return solution[0], solution[1]

    def calculate_implicit_equation(self):
        return lambda x, y: self.implicit_axis_equation.subs([(self.x, x), (self.y, y)])

    def start_show_axis_points_canvas(self):
        pass

Bezier = BezierTest()
print(Bezier.find_axis_point(500))
