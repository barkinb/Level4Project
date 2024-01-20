import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk, ImageDraw
import cv2
import numpy as np
from matplotlib.figure import Figure
from maths_functions import ni, basis


class NomogramApp:
    def __init__(self, root):
        self.button_status = tk.NORMAL

        self.root = root
        self.root.geometry("1280x800")
        self.root.title("Probabilistic Nomograms")
        self.canvas = None
        self.original_img = None

        self.create_toolbar()

    def select_image_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        try:
            if file_path:
                self.original_img = Image.open(file_path)

                canvas_width, canvas_height = 640, 480
                img_width, img_height = self.original_img.size
                aspect_ratio = img_width / img_height
                if img_width > canvas_width or img_height > canvas_height:
                    if canvas_width / aspect_ratio > canvas_height:
                        new_width = int(canvas_height * aspect_ratio)
                        new_height = canvas_height
                    else:
                        new_width = canvas_width
                        new_height = int(canvas_width / aspect_ratio)
                    self.original_img = self.original_img.resize((new_width, new_height), Image.LANCZOS)

                self.display_image(self.original_img)
                self.button_status = tk.NORMAL

        except Exception as e:
            messagebox.showerror("Error", e)

    def pick_axis(self):
        pass

    def display_image(self, image):
        if self.canvas:
            self.canvas.destroy()
        self.canvas = tk.Canvas(self.root, width=image.width, height=image.height, background="white")
        self.canvas.pack()
        photo = ImageTk.PhotoImage(image=image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.canvas.image = photo
        ##self.canvas.bind("<Button-1>", self.capture_axis_coordinates)

    def create_toolbar(self):
        # Create a frame to hold the toolbar buttons

        toolbar_frame = tk.Frame(self.root, bd=1, relief=tk.RAISED)

        icon_dimension = (32, 32)

        try:
            self.select_image = Image.open("icons/select_image_icon.png").resize(icon_dimension)
            self.new_axis = Image.open("icons/axis.png").resize(icon_dimension)


            self.select_icon = ImageTk.PhotoImage(self.select_image)
            self.axis_icon = ImageTk.PhotoImage(self.new_axis)

            self.select_button = tk.Button(toolbar_frame, image=self.select_icon, command=self.select_image_file)
            self.axis_button = tk.Button(toolbar_frame, image=self.axis_icon, command=self.pick_axis)

            self.select_button.pack(side=tk.LEFT, padx=2, pady=2)
            self.axis_button.pack(side=tk.LEFT, padx=2, pady=2)

            toolbar_frame.pack(side=tk.TOP, fill=tk.X)
        except Exception as e:
            print("Error loading icon images:", e)


if __name__ == "__main__":
    root = tk.Tk()
    app = NomogramApp(root)

    root.mainloop()
