import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk, ImageDraw
import cv2
import numpy as np
from matplotlib.figure import Figure
from maths_functions import ni,basis


class Nomogram:
    def __init__(self):
        self.thresholded_image = None
        self.thresholded_value = None
        self.hierarchy = None
        self.width = None
        self.height = None
        self.gray = None
        self.img = None
        self.contours = None

    def set_attributes(self, path):
        self.img = cv2.imread(path, -1)
        self.gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        self.thresholded_value, self.thresholded_image = cv2.threshold(self.gray, 100, 255, cv2.THRESH_BINARY_INV)
        self.contours, self.hierarchy = cv2.findContours(self.thresholded_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.height, self.width = self.img.shape[:2]


class NomogramApp:
    def __init__(self, root):
        self.button_status = tk.NORMAL

        self.root = root
        self.root.geometry("1280x800")
        self.root.title("Probabilistic Nomograms")
        self.canvas = None
        self.original_img = None
        self.nomogram = None

        self.axis_coordinates = {}
        self.create_toolbar()
        self.bezier_control_points = []


    def select_image_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        try:
            if file_path:
                self.nomogram = Nomogram()
                self.nomogram.set_attributes(file_path)
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
                self.axis_coordinates = {} ## resets coordinates when a new image is loaded
                self.manual_drawn_contours = []
                self.lasso_points = None
                self.lasso_started = None
                self.button_status = tk.NORMAL

        except Exception as e:
            messagebox.showerror("Error", e)

    def display_image(self, image):
        if self.canvas:
            self.canvas.destroy()
        self.canvas = tk.Canvas(self.root, width=image.width, height=image.height, background="white")
        self.canvas.pack()
        photo = ImageTk.PhotoImage(image=image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.canvas.image = photo
        self.canvas.bind("<Button-1>", self.capture_axis_coordinates)

    def capture_axis_coordinates(self, event):
        axis_id = simpledialog.askstring("Enter Axis ID", "Enter an identifier for the axis:")
        if axis_id is not None:
            x, y = event.x, event.y
            value = simpledialog.askfloat("Enter Value", f"Enter the axis value for {axis_id}:")
            if value is not None:
                if axis_id not in self.axis_coordinates:
                    self.axis_coordinates[axis_id] = []
                self.axis_coordinates[axis_id].append((x, y, value))
                self.display_axis_coordinates()

    def display_axis_coordinates(self):
        # Display the axis coordinates in a label or messagebox
        if self.axis_coordinates:
            coordinates_str = ""
            for axis_id, coords in self.axis_coordinates.items():
                coordinates_str += f"{axis_id}:\n"
                coordinates_str += '\n'.join([f"  ({x}, {y}): {value}" for x, y, value in coords])
                coordinates_str += "\n\n"
            messagebox.showinfo("Axis Coordinates", f"Axis Coordinates:\n{coordinates_str}")

    def undo(self):
        print("hi")

    def delete_all_contours(self):
        print("hi")

    def start_axis_selection(self):

        self.lasso_started = False
        self.lasso_points = []

        # bind mouse events
        self.canvas.bind("<Button-1>", self.start_lasso_selection)
        self.canvas.bind("<B1-Motion>", self.continue_lasso_selection)
        self.canvas.bind("<ButtonRelease-1>", self.end_lasso_selection)

    def start_normal_selection(self):
        self.canvas.bind("<Button-1>",self.draw_normal_distribution)

    def start_lasso_selection(self, event):

        self.lasso_started = True  # state
        x, y = event.x, event.y
        self.lasso_points = [(x, y)]

    def continue_lasso_selection(self, event):
        # continue lasso selection by drawing lines on  canvas
        if self.lasso_started:
            x, y = event.x, event.y

            self.lasso_points.append((x, y))
            if len(self.lasso_points) > 1:
                x1, y1 = self.lasso_points[-2]
                x2, y2 = self.lasso_points[-1]
                self.canvas.create_line(x1, y1, x2, y2, fill="red", width=2)

    def end_lasso_selection(self, event):
        if self.lasso_started:
            self.lasso_started = False

    def draw_bezier(self):
        axis_id = simpledialog.askstring("Enter Axis ID", "Enter an identifier for the axis to draw:")
        while axis_id not in self.axis_coordinates:
            axis_id = simpledialog.askstring("No Coordinates for Axis ID", "Enter an identifier for the axis to draw:")

        control_points = self.axis_coordinates[axis_id]

        if len(control_points) < 2:
            messagebox.showerror("Error", "Need at least 2 control points to draw a Bezier curve.")
            return

        self.bezier_control_points.extend(control_points)

        # Draw the Bezier curve on the canvas
        if len(self.bezier_control_points) >= 4:
            self.canvas.create_line(self.bezier_control_points, fill="green", width=2)

    def draw_normal_distribution(self,event):
        mouse_x, mouse_y = event.x, event.y

        std_dev = 1

        print(self.canvas.winfo_height())

        self.plot_normal_distribution(mouse_x, std_dev)

    def pick_axis(self):
        self.canvas.bind("<Button-1>", self.capture_axis_coordinates)
    def create_toolbar(self):
        # Create a frame to hold the toolbar buttons

        toolbar_frame = tk.Frame(self.root, bd=1, relief=tk.RAISED)

        icon_dimension = (32, 32)

        try:
            self.select_image = Image.open("icons/select_image_icon.png").resize(icon_dimension)
            self.undo = Image.open("icons/undo.png").resize(icon_dimension)
            self.delete_all = Image.open("icons/remove.png").resize(icon_dimension)
            self.get_lasso = Image.open("icons/lasso.png").resize(icon_dimension)
            self.new_axis = Image.open("icons/axis.png").resize(icon_dimension)
            self.normal_img = Image.open("icons/normal.png").resize(icon_dimension)
            self.bezier_img = Image.open("icons/bezier.png").resize(icon_dimension)

            self.select_icon = ImageTk.PhotoImage(self.select_image)
            self.undo_icon = ImageTk.PhotoImage(self.undo)
            self.delete_icon = ImageTk.PhotoImage(self.delete_all)
            self.lasso_icon = ImageTk.PhotoImage(self.get_lasso)
            self.axis_icon = ImageTk.PhotoImage(self.new_axis)
            self.normal_icon = ImageTk.PhotoImage(self.normal_img)
            self.bezier_icon = ImageTk.PhotoImage(self.bezier_img)

            self.select_button = tk.Button(toolbar_frame, image=self.select_icon, command=self.select_image_file)
            self.undo_button = tk.Button(toolbar_frame, image=self.undo_icon, command=self.undo)
            self.delete_button = tk.Button(toolbar_frame, image=self.delete_icon, command=self.delete_all_contours)
            self.lasso_button = tk.Button(toolbar_frame, image=self.lasso_icon, command=self.start_axis_selection)
            self.axis_button = tk.Button(toolbar_frame,image=self.axis_icon,command=self.pick_axis)
            self.bezier_button = tk.Button(toolbar_frame,image=self.bezier_icon,command=self.draw_bezier)
            self.normal_button = tk.Button(toolbar_frame,image=self.normal_icon,command=self.start_normal_selection)

            self.select_button.pack(side=tk.LEFT, padx=2, pady=2)
            self.undo_button.pack(side=tk.LEFT, padx=2, pady=2)
            self.delete_button.pack(side=tk.LEFT, padx=2, pady=2)
            self.lasso_button.pack(side=tk.LEFT, padx=2, pady=2)
            self.axis_button.pack(side=tk.LEFT,padx=2,pady=2)
            self.bezier_button.pack(side=tk.LEFT, padx=2, pady=2)
            self.normal_button.pack(side=tk.LEFT,padx=2,pady=2)

            toolbar_frame.pack(side=tk.TOP, fill=tk.X)
        except Exception as e:
            print("Error loading icon images:", e)

    def plot_normal_distribution(self,mean,std_dev):
        x_values = np.linspace(mean - 4 * std_dev, mean + 4 * std_dev, 100)
        y_values = (1 / (std_dev * np.sqrt(2 * np.pi))) * np.exp(-(x_values - mean) ** 2 / (2 * std_dev ** 2))
        axis_length = self.canvas.winfo_height
        y_values = y_values / np.max(y_values) * axis_length # Normalize the y-values

        coords = [(x, axis_length - y) for x, y in zip(x_values, y_values)]
        self.canvas.create_line(coords, fill="blue", width=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = NomogramApp(root)

    root.mainloop()
