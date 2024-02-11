from tkinter import Canvas

import numpy as np
import sympy
from bezier import bezier
from scipy.optimize import least_squares, fsolve

from maths_functions import objective_function, fitting_function

NUMBER_OF_DETAIL = 50
DEFAULT_CURVE_WIDTH = 2
DEFAULT_CURVE_COLOUR = "blue"

InvalidPointAmountError: ValueError = ValueError("Invalid Amount of Points")


class Axis:
    def __init__(self, name, control_points, canvas, width: int = DEFAULT_CURVE_WIDTH,
                 colour: str = DEFAULT_CURVE_COLOUR) -> None:
        self.axis_points_generated = False
        self.axis_equation_generated = False
        self.axis_equation_coefficients = None
        self.colour = colour
        self.width = width
        self.initial_guess = None
        self.xy_values = None
        self.x, self.y = sympy.symbols('x y')

        self.axis_values = None
        self.diffs = None
        self.axis_equation = None
        self.axis_points = []
        self.symbolic_axis_equation = None
        self.implicit_axis_equation = None
        self.curve_points = None
        self.curve_colour = DEFAULT_CURVE_COLOUR
        self.curve_width = DEFAULT_CURVE_WIDTH
        self.name = name
        self.control_points = control_points
        self.no_points = len(self.control_points)
        self.canvas = canvas
        self.curve = None

    def draw(self, canvas: Canvas) -> None:
        if self.curve is not None:
            canvas.delete(self.curve)

        x_coordinates, y_coordinates = zip(*self.control_points)
        fortran_array = np.asfortranarray([x_coordinates, y_coordinates])
        self.curve_points = bezier.Curve.from_nodes(fortran_array)
        parameters = np.linspace(0, 1, NUMBER_OF_DETAIL)

        points = self.curve_points.evaluate_multi(parameters)
        self.scaled_points = [(points[0][i], points[1][i]) for i in range(len(points[0]))]

        self.symbolic_axis_equation = self.curve_points.to_symbolic()
        self.implicit_axis_equation = self.curve_points.implicitize()
        self.curve = canvas.create_line(*sum(self.scaled_points, ()), width=self.curve_width, fill=self.curve_colour)

    def add_axis_points(self, point):
        self.axis_points.append(point)

    def set_axis_points(self, axis_points):
        self.axis_points = axis_points
        if len(self.axis_points) > 0:
            self.fit_axis_equation()

    def set_control_points(self, control_points):
        self.control_points = control_points

    def get_implicit_equation(self):
        # calculates the implicit value
        return self.implicit_axis_equation

    def calculate_implicit_equation(self):
        return lambda x, y: self.implicit_axis_equation.subs([(self.x, x), (self.y, y)])

    def fit_axis_equation(self):

        self.initial_guess = [0.0]*8
        self.xy_values = np.array([(point[0], point[1]) for point in self.axis_points])
        self.axis_values = np.array([point[2] for point in self.axis_points])
        self.diffs = np.diff(self.axis_values)

        result = least_squares(objective_function, self.initial_guess,
                               args=(self.xy_values, self.axis_values, self.diffs))

        popt = result.x
        self.axis_equation_coefficients = popt
        self.axis_equation_generated = True

    def find_axis_point(self, axis_value):
        def equations(variables):
            x, y = variables
            # evaluate the axis value
            curve_value = fitting_function(self.axis_equation_coefficients, np.array([x, y]), self.diffs) - axis_value
            # get the implicit equation value from the Bézier curve
            implicit_value = self.calculate_implicit_equation()(x, y)
            return np.concatenate([curve_value, [implicit_value - axis_value]])

        initial_guess = np.array([0, 0])
        solution = fsolve(equations, initial_guess, args=axis_value)
        self.axis_equation_generated = True
        return solution[0], solution[1]

    def start_show_axis_points_canvas(self) -> None:

        if self.axis_equation_generated:
            self.estimated_show_axis_points()

    def estimated_show_axis_points(self) -> None:

        if self.axis_points_generated:
            self.canvas.delete(f"axis_values_{self.name}")
        self.draw_estimated_axis_points()

    def draw_estimated_axis_points(self):
        random_points = self.scaled_points[::10] # will show 5 values guessed by the program
        for i, (x, y) in enumerate(random_points):
            x_float, y_float = float(x), float(y)
            # Calculate the corresponding axis value using your fitting function
            axis_value = fitting_function(self.axis_equation_coefficients, np.array([(x, y)]), self.diffs)[0]

            # Display the axis value next to the point
            text_x = x_float + 5
            text_y = y_float - 5

            self.canvas.create_oval(x_float - 2.5, y_float - 2.5, x_float + 2.5, y_float + 2.5, fill="green",
                                    outline="orange", tags=f"axis_values_{self.name}")
            self.canvas.create_text(text_x, text_y, anchor="nw",
                                    text=f"{axis_value}", fill="black",
                                    tags=f"axis_values_{self.name}")
        self.axis_points_generated = True
    def __delete__(self, canvas):
        self.curve = None
        canvas.delete(self.curve)
