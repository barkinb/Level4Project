import tkinter
import traceback
from random import randint
from tkinter import messagebox
import numpy as np
import sympy
from bezier import bezier
from scipy.optimize import least_squares, fsolve

from src.app.utils.maths_functions import objective_function, fitting_function
from DistributionParser import parse_distribution

NUMBER_OF_DETAIL = 500  # multiple of 5
DEFAULT_CURVE_WIDTH = 2
DEFAULT_CURVE_COLOUR = "blue"
DEFAULT_POINT_SIZE = 20

InvalidPointAmountError: ValueError = ValueError("Invalid Amount of Points")


class Axis:

    def __init__(self, name: str, control_points: [], canvas: tkinter.Canvas, width: int = DEFAULT_CURVE_WIDTH,
                 colour: str = DEFAULT_CURVE_COLOUR) -> None:

        self.probability_at_point = None
        self.axis_drawn = False
        self.distribution_function = None
        self.distribution_params = None
        self.distribution_type = None
        self.statistics_curve = None
        self.scaled_points = None
        self.axis_equation_degree = None
        self.distribution = None
        self.axis_points_generated = False
        self.axis_equation_produced = False
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
        self.scaled_points_middle = None
        self.scaled_points_array = None

    def draw(self) -> bool:
        if len(self.control_points) >= 2:
            if self.curve is not None:
                self.canvas.delete(self.curve)

            x_coordinates, y_coordinates = zip(*self.control_points)
            fortran_array = np.asfortranarray([x_coordinates, y_coordinates])
            self.curve_points = bezier.Curve.from_nodes(fortran_array)
            parameters = np.linspace(0, 1, NUMBER_OF_DETAIL)
            points = self.curve_points.evaluate_multi(parameters)
            self.scaled_points = [(points[0][i], points[1][i]) for i in range(len(points[0]))]
            self.scaled_points_array = np.array(self.scaled_points, dtype='float64')
            self.scaled_points_middle = np.mean(self.scaled_points_array, axis=0)
            self.scaled_points_middle = (self.scaled_points_middle[0], self.scaled_points_middle[1])
            self.implicit_axis_equation = self.curve_points.implicitize()
            self.curve = self.canvas.create_line(*sum(self.scaled_points, ()), width=self.curve_width,
                                                 fill=self.curve_colour, tags=f"bezier_axis_curve_{self.name}")
            self.axis_drawn = True
            return True
        else:
            messagebox.showerror(title="Error", message="Please enter at least two control points to draw an overlay")
            return False

    def add_axis_points(self, point):
        self.axis_points.append(point)

    def set_axis_points(self, axis_points: []):
        self.axis_points = axis_points
        if len(self.axis_points) > 2:
            self.fit_axis_equation()

    def set_control_points(self, control_points: []):
        self.control_points = control_points

    def get_implicit_equation(self):
        # calculates the implicit value
        return self.implicit_axis_equation

    def calculate_implicit_equation(self):
        return lambda x, y: self.implicit_axis_equation.subs([(self.x, x), (self.y, y)])

    def fit_axis_equation(self):

        self.initial_guess = [0.0] * 8
        self.xy_values = np.array([(point[0], point[1]) for point in self.axis_points], dtype='float64')
        self.axis_values = np.array([point[2] for point in self.axis_points], dtype='float64')
        self.diffs = np.diff(self.axis_values)

        result = least_squares(objective_function, self.initial_guess,
                               args=(self.xy_values, self.axis_values, self.diffs))

        popt = result.x
        self.axis_equation_coefficients = popt
        self.axis_equation_produced = True
        self.start_show_axis_points_canvas()

    def scaled_points_midpoint(self):
        return self.scaled_points_middle

    def find_axis_point(self, axis_value: float):
        global solution
        try:

            def equations(variables):
                x, y = variables
                # Evaluate the curve value and implicit value
                curve_value = fitting_function(self.axis_equation_coefficients, np.array([x, y]),
                                               self.diffs)
                implicit_value = self.calculate_implicit_equation()(x, y)
                return np.array([curve_value - axis_value, implicit_value],dtype='float64')

            initial_guess = np.array([0, 0],dtype='float64')
            solution = fsolve(equations, initial_guess)


        except TypeError:
            print(traceback.print_last())
        return solution[0], solution[1]

    def start_show_axis_points_canvas(self) -> None:

        if self.axis_equation_produced:
            self.estimated_show_axis_points()

    def axis_equation_generated(self):
        return self.axis_equation_produced

    def estimated_show_axis_points(self) -> None:

        if self.axis_points_generated:
            self.canvas.delete(f"axis_values_{self.name}")
        if len(self.axis_points) > 2:
            self.draw_estimated_axis_points()

    def draw_estimated_axis_points(self):
        random_points = self.scaled_points[::(NUMBER_OF_DETAIL // 5)]  # will show 5 values guessed by the program
        for i, (x, y) in enumerate(random_points):
            x_float, y_float = float(x), float(y)
            # Calculate the corresponding axis value using your fitting function
            axis_value = self.find_value_at_point([x_float, y_float])

            # Display the axis value next to the point
            text_x = x_float + 5
            text_y = y_float - 5

            self.canvas.create_oval(x_float - 2.5, y_float - 2.5, x_float + 2.5, y_float + 2.5, fill="green",
                                    outline="orange", tags=f"axis_values_{self.name}")
            self.canvas.create_text(text_x, text_y, anchor="nw",
                                    text=f"Estimate {axis_value:.3f}", fill="black",
                                    tags=f"axis_values_{self.name}")

        self.axis_points_generated = True

    def find_value_at_point(self, point: []):
        return fitting_function(self.axis_equation_coefficients,
                                np.array(point), self.diffs)

    def add_distribution(self, distribution_str: str):
        if not self.axis_points_generated:
            messagebox.showinfo(title="Axis points not generated",
                                message="Please ensure axis points have been captured")
        if distribution_str == "None":
            self.distribution = None
            self.distribution_type = None
            self.distribution_params = None
            self.distribution_function = None
            self.canvas.delete(f"statistics_points_{self.name}")
        if self.axis_points_generated:
            try:

                if self.distribution is not None:
                    self.canvas.delete(f"statistics_points_{self.name}")
                self.distribution = parse_distribution(distribution_str)
                self.distribution_type = self.distribution["type"]
                self.distribution_params = self.distribution["params"]
                self.distribution_function = self.distribution["function"]

                self.probability_at_point = np.zeros(len(self.scaled_points))

                for i in range(len(self.scaled_points)):
                    scaled_point = self.scaled_points[i]

                    # Use fitting_function to find the axis_value

                    axis_value = self.find_value_at_point(scaled_point)

                    # Use self.distribution.pdf to find the probability density at that point
                    self.probability_at_point[i] = self.get_probability_at_point(axis_value)

                # Find the maximum probability
                max_probability = np.max(self.probability_at_point)

                # Calculate scale_factor using NumPy element-wise operations
                scale_factor = DEFAULT_POINT_SIZE / max_probability

                for i in range(len(self.scaled_points)):
                    scaled_point = self.scaled_points[i]

                    # Calculate coordinates for the oval using NumPy element-wise operations
                    x1 = scaled_point[0] - self.probability_at_point[i] * scale_factor / 2
                    y1 = scaled_point[1] - self.probability_at_point[i] * scale_factor / 2
                    x2 = scaled_point[0] + self.probability_at_point[i] * scale_factor / 2
                    y2 = scaled_point[1] + self.probability_at_point[i] * scale_factor / 2

                    # Create the oval on the canvas
                    self.canvas.create_oval(x1, y1, x2, y2, fill=self.curve_colour, outline=self.curve_colour,
                                            width=self.curve_width, tags=f"statistics_points_{self.name}")

            except Exception as e:
                print(traceback.print_exc())
                messagebox.showerror("Error", f"Error adding distribution: {e}")
            if self.distribution is not None:
                self.canvas.delete(f"axis_points_{self.name}")
                self.canvas.delete(f"control_points_{self.name}")
                self.canvas.delete(f"axis_values_{self.name}")

    def get_probability_at_point(self, value: float) -> float:
        if self.distribution_type == "continuous":
            return self.distribution_function.pdf(value, *self.distribution_params)
        elif self.distribution_type == "discrete":
            return self.distribution_function.pmf(int(value), *self.distribution_params)

    def get_distribution(self):
        return self.distribution

    def get_distribution_type(self):
        return self.distribution_type

    def get_distribution_function(self):
        return self.distribution_function

    def get_distribution_params(self):
        return self.distribution_params

    def get_random_point(self):
        if self.distribution is not None:
            point = self.get_distribution_function().rvs(self.get_distribution_params())[0]
            return self.find_axis_point(point)
        else:
            return self.scaled_points[randint(0, len(self.scaled_points) - 1)]

    def get_axis_drawn(self):
        return self.axis_drawn

    def __delete__(self, canvas):
        self.curve = None
        canvas.delete(self.curve)
