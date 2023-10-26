import tkinter as tk
import cv2
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
directory = 'src/nomograms'
img = cv2.imread('nomograms/tutorial1a_page-0001.jpg', -1)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
edges = cv2.Canny(blurred, 50, 150)
contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
axis_contours = []
for contour in contours:
    if cv2.contourArea(contour) > 100:
        axis_contours.append(contour)
cv2.drawContours(img, axis_contours, -1, (0, 0, 255), 2)
cv2.imshow('Detected Axes', img)
cv2.waitKey(0)
cv2.destroyAllWindows()

