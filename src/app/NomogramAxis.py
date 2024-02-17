import traceback
from tkinter import messagebox
import numpy as np
import sympy
from bezier import bezier
from scipy.optimize import least_squares, fsolve

from src.app.utils.maths_functions import objective_function, fitting_function
from DistributionParser import parse_distribution

NUMBER_OF_DETAIL = 50
DEFAULT_CURVE_WIDTH = 2
DEFAULT_CURVE_COLOUR = "blue"
DEFAULT_POINT_SIZE = 20

InvalidPointAmountError: ValueError = ValueError("Invalid Amount of Points")


class Axis:
    def __init__(self, name, control_points, canvas, width: int = DEFAULT_CURVE_WIDTH,
                 colour: str = DEFAULT_CURVE_COLOUR) -> None:

        self.distribution_function = None
        self.distribution_params = None
        self.distribution_type = None
        self.statistics_curve = None
        self.scaled_points = None
        self.axis_equation_degree = None
        self.distribution = None
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

    def draw(self) -> None:
        if self.curve is not None:
            self.canvas.delete(self.curve)

        x_coordinates, y_coordinates = zip(*self.control_points)
        fortran_array = np.asfortranarray([x_coordinates, y_coordinates])
        self.curve_points = bezier.Curve.from_nodes(fortran_array)
        parameters = np.linspace(0, 1, NUMBER_OF_DETAIL)

        points = self.curve_points.evaluate_multi(parameters)
        self.scaled_points = [(points[0][i], points[1][i]) for i in range(len(points[0]))]

        self.implicit_axis_equation = self.curve_points.implicitize()
        self.curve = self.canvas.create_line(*sum(self.scaled_points, ()), width=self.curve_width,
                                             fill=self.curve_colour, tags=f"bezier_axis_curve_{self.name}")

    def add_axis_points(self, point):
        self.axis_points.append(point)

    def set_axis_points(self, axis_points):
        self.axis_points = axis_points
        if len(self.axis_points) > 2:
            self.fit_axis_equation()

    def set_control_points(self, control_points):
        self.control_points = control_points

    def get_implicit_equation(self):
        # calculates the implicit value
        return self.implicit_axis_equation

    def calculate_implicit_equation(self):
        return lambda x, y: self.implicit_axis_equation.subs([(self.x, x), (self.y, y)])

    def fit_axis_equation(self):

        self.initial_guess = [0.0] * 8
        self.xy_values = np.array([(point[0], point[1]) for point in self.axis_points])
        self.axis_values = np.array([point[2] for point in self.axis_points])
        self.diffs = np.diff(self.axis_values)

        result = least_squares(objective_function, self.initial_guess,
                               args=(self.xy_values, self.axis_values, self.diffs))

        popt = result.x
        self.axis_equation_coefficients = popt
        self.axis_equation_generated = True
        self.start_show_axis_points_canvas()

    def find_axis_point(self, axis_value):

        def equations(variables):
            x, y = variables
            # Evaluate the curve value and implicit value
            curve_value = fitting_function(self.axis_equation_coefficients, np.array([x, y]), self.diffs) - axis_value
            implicit_value = self.calculate_implicit_equation()(x, y)
            return [curve_value, implicit_value - axis_value]

        initial_guess = np.array([0, 0])
        solution = fsolve(equations, initial_guess)

        curve_value_at_solution = fitting_function(self.axis_equation_coefficients,
                                                   np.array([solution[0], solution[1]]), self.diffs)
        implicit_value_at_solution = self.calculate_implicit_equation()(solution[0], solution[1])
        tolerance = 1e-2

        if np.abs(curve_value_at_solution - axis_value) < tolerance and np.abs(
                implicit_value_at_solution - axis_value) < tolerance:
            return solution[0], solution[1]

        else:
            print("below tolerance")
            return solution[0], solution[1]

    def start_show_axis_points_canvas(self) -> None:

        if self.axis_equation_generated:
            self.estimated_show_axis_points()

    def estimated_show_axis_points(self) -> None:

        if self.axis_points_generated:
            self.canvas.delete(f"axis_values_{self.name}")
        if len(self.axis_points) > 2:
            self.draw_estimated_axis_points()

    def draw_estimated_axis_points(self):
        random_points = self.scaled_points[::5]  # will show 5 values guessed by the program
        for i, (x, y) in enumerate(random_points):
            x_float, y_float = float(x), float(y)
            # Calculate the corresponding axis value using your fitting function
            axis_value = fitting_function(self.axis_equation_coefficients, np.array([x, y]), self.diffs)

            # Display the axis value next to the point
            text_x = x_float + 5
            text_y = y_float - 5

            self.canvas.create_oval(x_float - 2.5, y_float - 2.5, x_float + 2.5, y_float + 2.5, fill="green",
                                    outline="orange", tags=f"axis_values_{self.name}")
            self.canvas.create_text(text_x, text_y, anchor="nw",
                                    text=f"Estimate {axis_value:.3f}", fill="black",
                                    tags=f"axis_values_{self.name}")

        self.axis_points_generated = True

    def add_distribution(self, distribution_str):

        try:
            self.canvas.delete(f"bezier_axis_curve_{self.name}")
            self.canvas.delete(f"axis_points_{self.name}")
            self.canvas.delete(f"control_points_{self.name}")
            self.canvas.delete(f"axis_values_{self.name}")
            if self.distribution is not None:
                self.canvas.delete(f"statistics_points_{self.name}")
            self.distribution = parse_distribution(distribution_str)
            self.distribution_type = self.distribution["type"]
            self.distribution_params = self.distribution["params"]
            self.distribution_function = self.distribution["function"]

            # distribution

            # Initialize probability_at_point as a NumPy array
            probability_at_point = np.zeros(len(self.scaled_points))

            for i in range(len(self.scaled_points)):
                scaled_point = self.scaled_points[i]

                # Use fitting_function to find the axis_value
                axis_value = fitting_function(self.axis_equation_coefficients, np.array([scaled_point]), self.diffs)

                # Use self.distribution.pdf to find the probability density at that point
                if self.distribution_type == "continuous":
                    probability_at_point[i] = self.distribution_function.pdf(axis_value, *self.distribution_params)
                elif self.distribution_type == "discrete":
                    probability_at_point[i] = self.distribution_function.pmf(axis_value, *self.distribution_params)

            # Find the maximum probability
            max_probability = np.max(probability_at_point)

            # Calculate scale_factor using NumPy element-wise operations
            scale_factor = DEFAULT_POINT_SIZE / max_probability

            for i in range(len(self.scaled_points)):
                scaled_point = self.scaled_points[i]

                # Calculate coordinates for the oval using NumPy element-wise operations
                x1 = scaled_point[0] - probability_at_point[i] * scale_factor / 2
                y1 = scaled_point[1] - probability_at_point[i] * scale_factor / 2
                x2 = scaled_point[0] + probability_at_point[i] * scale_factor / 2
                y2 = scaled_point[1] + probability_at_point[i] * scale_factor / 2

                # Create the oval on the canvas
                self.canvas.create_oval(x1, y1, x2, y2, fill="green",
                                        width=self.curve_width, tags=f"statistics_points_{self.name}")

        except Exception as e:
            print(traceback.print_exc())
            messagebox.showwarning(f"Error adding distribution: {e}")

    def show_distribution_info(self):
        try:
            if self.distribution:
                messagebox.showinfo("Distribution Info", str(self.distribution))
            else:
                messagebox.showwarning("No Distribution", "No distribution found for this axis")
        except Exception as e:
            messagebox.showwarning(f"Error adding distribution: {e}")

    def get_distribution(self):
        return self.distribution

    def __delete__(self, canvas):
        self.curve = None
        canvas.delete(self.curve)
