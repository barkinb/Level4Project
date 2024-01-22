from tkinter import Canvas
from math import sqrt
from maths_functions import *
##DISCLAIMER = a portion of code in this file originates from https://github.com/otto-kokstein/bezierve-v2
NUMBER_OF_DETAIL = 10000
DEFAULT_CURVE_WIDTH = 3
DEFAULT_CURVE_COLOUR = "#050505"

InvalidPointAmountError: ValueError = ValueError("Invalid Amount of Points")

class BezierCurve:
    def __init__(self, name, points, canvas, width: int = DEFAULT_CURVE_WIDTH, color: str = DEFAULT_CURVE_COLOUR) -> None:

        self.curve_colour = DEFAULT_CURVE_COLOUR
        self.curve_width = DEFAULT_CURVE_WIDTH
        self.name = name
        self.points = points
        self.canvas = canvas
        self.curve = None

    def draw(self,canvas: Canvas) -> None:
        #self.sort_points()
        if self.curve is not None:
            self.canvas.delete(self.curve)
        curve_points = []
        for i in range(NUMBER_OF_DETAIL):
            t = i / (NUMBER_OF_DETAIL - 1)

            point_x, point_y = self.calculate_curve_point(t)
            curve_points.append([point_x, point_y])

        self.curve = canvas.create_line(
            *curve_points, width=self.curve_width, fill=self.curve_colour

        )
    def sort_points(self):

        initial_point = self.points[0]

        # calculate all angles and sort
        sorted_points = sorted(self.points, key=lambda p: calculate_angle(p, initial_point))

        unique_points = [sorted_points[0]] + [p for i, p in enumerate(sorted_points[1:]) if p != sorted_points[i]]

        self.points = unique_points
    def calculate_curve_point(self, t: float) :
        point_x = 0.0
        point_y = 0.0

        if len(self.points) == 2:
            point_x = (1 - t) * self.points[0][0] + t * self.points[
                1
            ][0]
            point_y = (1 - t) * self.points[0][1] + t * self.points[
                1
            ][1]

        elif len(self.points) == 3:
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

        elif len(self.points) == 4:
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

        return (round(point_x), round(point_y))

    def __delete__(self, canvas):
        self.curve = None
        canvas.delete(self.curve)
