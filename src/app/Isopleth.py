import threading
import tkinter
import numpy as np
import sympy
from bezier import bezier
from scipy.optimize import fsolve

NUMBER_OF_DETAIL = 1000
DEFAULT_LINE_WIDTH = 2
DEFAULT_LINE_COLOUR = "red"

InvalidPointAmountError: ValueError = ValueError("Invalid Amount of Points")


class Isopleth:
    def __init__(self, number: int, canvas: tkinter.Canvas, nomogram_axes: {}, width: int = DEFAULT_LINE_WIDTH,
                 colour: str = DEFAULT_LINE_COLOUR) -> None:
        self.t = 0
        self.intersections = None
        self.scaled_points = None
        self.colour = colour
        self.width = width
        self.initial_guess = None
        self.xy_values = None
        self.x, self.y = sympy.symbols('x y')
        self.axis_values = None
        self.diffs = None
        self.symbolic_axis_equation = None
        self.implicit_axis_equation = None
        self.line_points = None
        self.line_colour = DEFAULT_LINE_COLOUR
        self.line_width = DEFAULT_LINE_WIDTH
        self.isopleth_id = number
        self.canvas = canvas
        self.line = None
        self.nomogram_axes = nomogram_axes
        self.control_points = []
        self.produce_control_points()

    def produce_control_points(self):
        # Clear existing control points and related canvas elements
        self.control_points = []
        self.canvas.delete("axis_points")
        self.canvas.delete("control_points")
        self.canvas.delete("axis_values")

        leftmost_midpoint = None
        rightmost_midpoint = None
        for axis_id, axis in self.nomogram_axes.items():
            midpoint = axis_id, axis.scaled_points_midpoint()
            if leftmost_midpoint is None or midpoint[1][0] < leftmost_midpoint[1][0]:
                leftmost_midpoint = midpoint
            if rightmost_midpoint is None or midpoint[1][0] > rightmost_midpoint[1][0]:
                rightmost_midpoint = midpoint

        self.control_points.append(self.nomogram_axes[leftmost_midpoint[0]].get_random_point())
        self.control_points.append(self.nomogram_axes[rightmost_midpoint[0]].get_random_point())

        self.draw()
    def draw(self) -> None:

        self.canvas.delete("isopleth")
        if self.line is not None:
            self.canvas.delete(self.line)

        x_coordinates, y_coordinates = zip(*self.control_points)
        fortran_array = np.asfortranarray([x_coordinates, y_coordinates])
        self.line_points = bezier.Curve.from_nodes(fortran_array)
        parameters = np.linspace(0, 1, NUMBER_OF_DETAIL)

        points = self.line_points.evaluate_multi(parameters)
        self.scaled_points = [(points[0][i], points[1][i]) for i in range(len(points[0]))]

        self.implicit_axis_equation = self.line_points.implicitize()
        self.line = self.canvas.create_line(*sum(self.scaled_points, ()), width=self.line_width,
                                            fill=self.line_colour, tags=("isopleth", f"isopleth_{self.isopleth_id}"))

        self.intersections = self.find_isopleth_intersections()
        for i in self.intersections:
            axis_id, x, y = i[0], i[1][0], i[1][1]
            axis_value = self.nomogram_axes[axis_id].find_axis_value_at_point([x, y])
            if self.nomogram_axes[axis_id].get_distribution() is not None:
                probability_density = self.nomogram_axes[axis_id].get_probability_at_point(axis_value)
                # Display axis value and probability density near the intersection point with tags
                self.canvas.create_text(x + 50, y + 50, anchor="nw", fill="black",
                                        text=f"Axis Value: {axis_value:.3f}, "
                                             f"pdf: {probability_density:.3f}",
                                        tags=("isopleth", f"axis_values_{axis_id}"))
            else:
                self.canvas.create_text(x + 50, y + 50, anchor="nw", fill="black",
                                        text=f"Axis Value: {axis_value:.3f}",
                                        tags=("isopleth", f"axis_values_{axis_id}"))
        self.t += 1
        while self.t < 10:
            threading.Timer(2.5, self.draw).start()
    def calculate_implicit_equation(self):
        return lambda x, y: self.implicit_axis_equation.subs([(self.x, x), (self.y, y)])

    def find_isopleth_intersections(self):

        intersections = []
        for axis_id, axis in self.nomogram_axes.items():
            if axis.axis_equation_generated():

                def equations(variables):
                    x, y = variables[0], variables[1]
                    # Evaluate the curve value and implicit value
                    curve_implicit = axis.calculate_implicit_equation()(x, y)
                    implicit_value = self.calculate_implicit_equation()(x, y)
                    return np.array([curve_implicit - implicit_value, implicit_value], dtype="float64")

                initial_guess = np.array([axis.get_random_point()[0], axis.get_random_point()[1]])
                solution = fsolve(equations, initial_guess)
                intersections.append([axis_id, solution])

        return intersections
