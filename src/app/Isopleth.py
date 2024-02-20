import numpy as np
import sympy
from bezier import bezier

NUMBER_OF_DETAIL = 50
DEFAULT_LINE_WIDTH = 2
DEFAULT_LINE_COLOUR = "green"

InvalidPointAmountError: ValueError = ValueError("Invalid Amount of Points")

class Isopleth:
    def __init__(self, number, control_points, canvas, width: int = DEFAULT_LINE_WIDTH,
                 colour: str = DEFAULT_LINE_COLOUR) -> None:

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
        self.id = number
        self.control_points = control_points
        self.no_points = len(self.control_points)
        self.canvas = canvas
        self.line = None

    def draw(self) -> None:
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
                                            fill=self.line_colour, tags=f"isopleth_{self.id}")

    def get_implicit_equation(self):
        # returns implicit equation
        return self.implicit_axis_equation

    def calculate_implicit_equation(self):
        return lambda x, y: self.implicit_axis_equation.subs([(self.x, x), (self.y, y)])


