from tkinter import Canvas
from math import sqrt
from maths_functions import *
from bezier import bezier


##DISCLAIMER = a portion of code in this file originates from https://github.com/otto-kokstein/bezierve-v2
NUMBER_OF_DETAIL = 10000
DEFAULT_CURVE_WIDTH = 2
DEFAULT_CURVE_COLOUR = "#050505"

InvalidPointAmountError: ValueError = ValueError("Invalid Amount of Points")


class BezierCurve:
    def __init__(self, name, points, canvas, width: int = DEFAULT_CURVE_WIDTH,
                 color: str = DEFAULT_CURVE_COLOUR) -> None:

        self.curve_points = None
        self.curve_colour = DEFAULT_CURVE_COLOUR
        self.curve_width = DEFAULT_CURVE_WIDTH
        self.name = name
        self.points = points
        self.no_points = len(self.points)
        self.canvas = canvas

        self.curve = None

    def draw(self, canvas: Canvas) -> None:
        ##self.sort_points()
        if self.curve is not None:
            self.canvas.delete(self.curve)
        curve_points = []

        x_coordinates, y_coordinates = zip(*self.points)
        fortran_array = np.asfortranarray([x_coordinates, y_coordinates])
        self.curve_points = bezier.Curve.from_nodes(fortran_array)
        parameters = np.linspace(0, 1, NUMBER_OF_DETAIL)

        points = self.curve_points.evaluate_multi(parameters)
        scaled_points = [(points[0][i],points[1][i]) for i in range(len(points[0]))]
        # x,y = []

        print(points)
        print(scaled_points)
        self.curve = canvas.create_line(*sum(scaled_points, ()), width=self.curve_width, fill=self.curve_colour)



        # self.curve = canvas.create_line(
        #     *self.curve_points, width=self.curve_width, fill=self.curve_colour
        #
        # )

    def sort_points(self):

        initial_point = self.points[0]

        # calculate all angles and sort
        sorted_points = sorted(self.points, key=lambda p: calculate_angle(p, initial_point))

        unique_points = [sorted_points[0]] + [p for i, p in enumerate(sorted_points[1:]) if p != sorted_points[i]]

        self.points = unique_points

    def calculate_max_4_control_points(self, t: float):
        point_x = 0.0
        point_y = 0.0
        n = self.no_points
        # print(n)
        # if n >= 2:
        #     for i in range(n):
        #         point_x += self.points[i][0] * (t ** i) * ((1 - t) ** (n - i)) * ni(n, i)
        #         point_y += self.points[i][1] * (t ** i) * ((1 - t) ** (n - i)) * ni(n, i)

        if n == 2:
            point_x = (1 - t) * self.points[0][0] + t * self.points[
                1
            ][0]
            point_y = (1 - t) * self.points[0][1] + t * self.points[
                1
            ][1]

        elif n == 3:
            point_x = (1 - t) * (
                    (1 - t) * self.points[0][0]
                    + t * self.points[1][0]
            ) + t * (
                              (1 - t) * self.points[1][0]
                              + t * self.points[2][0]
                      )

            point_y = (1 - t) * (
                    (1 - t) * self.points[0][1]
                    + t * self.points[1][1]
            ) + t * (
                              (1 - t) * self.points[1][1]
                              + t * self.points[2][1]
                      )

        elif n == 4:
            point_x = (
                    (1 - t) ** 3 * self.points[0][0]
                    + 3 * (1 - t) ** 2 * t * self.points[1][0]
                    + 3 * (1 - t) * t ** 2 * self.points[2][0]
                    + t ** 3 * self.points[3][0]
            )

            point_y = (
                    (1 - t) ** 3 * self.points[0][1]
                    + 3 * (1 - t) ** 2 * t * self.points[1][1]
                    + 3 * (1 - t) * t ** 2 * self.points[2][1]
                    + t ** 3 * self.points[3][1]
            )

        else:
            raise InvalidPointAmountError

        return round(point_x), round(point_y)

    def __delete__(self, canvas):
        self.curve = None
        canvas.delete(self.curve)
