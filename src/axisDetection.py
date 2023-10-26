import tkinter as tk
import cv2
from tkinter import ttk, filedialog
from PIL import Image, ImageTk


class Nomogram:
    def __init__(self, path):
        self.img = cv2.imread(path, -1)
        self.gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

    def Contours(self):
        self.blurred = cv2.GaussianBlur(self.gray, (5, 5), 0)
        self.edges = cv2.Canny(self.blurred, 50, 150)
        self.contours, self._ = cv2.findContours(self.edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.axis_contours = []
        for contour in self.contours:
            if cv2.contourArea(contour) > 100:
                self.axis_contours.append(contour)

    def draw_contours(self):
        cv2.drawContours(self.img, self.axis_contours, -1, (0, 0, 255), 2)
        cv2.imshow('Axis detector', self.img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


image1 = Nomogram("nomograms/meyer_nomogram.png")
image2 = Nomogram("nomograms/Nomogram-for-calculation-of-standard-water-Note-Developed-by-Phyllis-Meyer-Gaspar-PhD.png")
image3 = Nomogram("nomograms/tutorial1a_page-0001.jpg")

images = [image1, image2, image3]
for image in images:
    image.Contours()
    image.draw_contours()
