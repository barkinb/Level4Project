from tkinter import Canvas
from maths_functions import calculate_angle, objective_function, fitting_function
from scipy.optimize import least_squares
from bezier import bezier
import numpy as np

NUMBER_OF_DETAIL = 50
DEFAULT_CURVE_WIDTH = 2
DEFAULT_CURVE_COLOUR = "#050505"

InvalidPointAmountError: ValueError = ValueError("Invalid Amount of Points")


class Axis:
    def __init__(self, name, control_points, canvas, width: int = DEFAULT_CURVE_WIDTH,
                 color: str = DEFAULT_CURVE_COLOUR) -> None:
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

    def axis_equation(self):
        pass

    def draw(self, canvas: Canvas) -> None:
        if self.curve is not None:
            canvas.delete(self.curve)

        x_coordinates, y_coordinates = zip(*self.control_points)
        fortran_array = np.asfortranarray([x_coordinates, y_coordinates])
        self.curve_points = bezier.Curve.from_nodes(fortran_array)
        parameters = np.linspace(0, 1, NUMBER_OF_DETAIL)

        points = self.curve_points.evaluate_multi(parameters)
        scaled_points = [(points[0][i], points[1][i]) for i in range(len(points[0]))]

        self.symbolic_axis_equation = self.curve_points.to_symbolic()
        self.implicit_axis_equation = self.curve_points.implicitize()
        print(x_coordinates, y_coordinates)
        print(fortran_array)
        print(self.implicit_axis_equation)
        print(self.symbolic_axis_equation)

        self.curve = canvas.create_line(*sum(scaled_points, ()), width=self.curve_width, fill=self.curve_colour)

    def add_axis_points(self, point):
        self.axis_points.append(point)

    def set_axis_points(self, axis_points):
        self.axis_points = axis_points

    def set_control_points(self, control_points):
        self.control_points = control_points

    def get_implicit_equation(self):
        return self.implicit_axis_equation

    def fit_axis_equation(self):

        initial_guess = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        xy_values = np.array([(point[0], point[1]) for point in self.axis_points])
        axis_values = np.array([point[2] for point in self.axis_points])
        diffs = np.diff(axis_values)

        result = least_squares(objective_function, initial_guess, args=(xy_values, axis_values,diffs))

        popt = result.x
        print("Coefficients:", popt)

        print(fitting_function(popt, xy_values, diffs))

    def __delete__(self, canvas):
        self.curve = None
        canvas.delete(self.curve)
