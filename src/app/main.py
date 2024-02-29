import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

import numpy
from tktooltip import ToolTip
from PIL import Image, ImageTk
import traceback
import cv2
from NomogramAxis import Axis
from utils.maths_functions import calculate_opencv_closest_point
from Isopleth import Isopleth

DEFAULT_CANVAS_WIDTH, DEFAULT_CANVAS_HEIGHT = 1250, 800
DEFAULT_CANVAS_IMAGE_OFFSET = 25
DEFAULT_BEZIER_CONTROL_SIZE = 5
DEFAULT_BEZIER_CONTROL_COLOUR = "orange"
DEFAULT_AXIS_CONTROL_SIZE = 2.5
DEFAULT_AXIS_CONTROL_COLOUR = "yellow"


class NomogramApp:
    def __init__(self, root_window):

        self.opencv_image_edges = None
        self.opencv_image_contours = None
        self.opencv_image_blurred = None
        self.opencv_image_gray = None
        self.save_distribution_button = None
        self.distribution_entry = None
        self.distribution_label = None
        self.axis_id_dropdown = None
        self.axis_entry_button = None
        self.isopleth_button = None
        self.bezier_button = None
        self.save_project_button = None
        self.load_project_button = None
        self.isopleth_icon = None
        self.axis_entry_icon = None
        self.bezier_icon = None
        self.select_button = None
        self.control_point_button = None
        self.control_point_icon = None
        self.select_icon = None
        self.isopleth_img = None
        self.axis_entry_img = None
        self.bezier_img = None
        self.control_point_img = None
        self.select_nomogram_img = None
        self.file_path = None
        self.time = None
        self.opencv_image_points = None
        self.opencv_image = None
        self.number_of_complete_axis = 0
        self.axis_id_variable = None
        self.axis_label = None
        self.title = None
        self.left_panel_canvas = None
        self.left_panel_inner_frame = None
        self.scrollbar = None
        self.left_panel_canvas = None
        self.left_panel_frame = None
        self.left_panel = None
        self.left_panel_content = None
        self.current_point_id = None
        self.start_y = None
        self.start_x = None
        self.root = root_window
        self.root.geometry("1440x900")
        self.root.title("Probabilistic Nomograms")
        self.canvas = None
        self.original_img = None
        self.control_points = {}
        self.axis_points = {}
        self.nomogram_axes = {}
        self.isopleths = {}
        self.create_toolbar()
        # self.create_left_panel()
        self.distributions = 0
        self.number_isopleths = 0
        #
        root_window.bind('<Control-l>', lambda event: self.select_image_file())
        root_window.bind('<Control-c>', lambda event: self.pick_control_point())
        root_window.bind('<Control-b>', lambda event: self.draw_bezier())
        root_window.bind('<Control-a>', lambda event: self.pick_axis_point())
        root_window.bind('<Control-i>', lambda event: self.create_isopleth())
        root_window.bind('<Control-n>', lambda event: self.add_new_axis_id())

    def create_toolbar(self):
        # Create a frame to hold the toolbar buttons

        toolbar_frame = tk.Frame(self.root, bd=1, relief=tk.RAISED)

        icon_dimension = (32, 32)

        try:
            self.select_nomogram_img = Image.open("icons/select_nomogram.png").resize(icon_dimension)
            self.control_point_img = Image.open("icons/bezier-tool.png").resize(icon_dimension)
            self.bezier_img = Image.open("icons/draw_bezier.png").resize(icon_dimension)
            self.axis_entry_img = Image.open("icons/bezier-axis_entry.png").resize(icon_dimension)
            self.isopleth_img = Image.open("icons/isopleth.png").resize(icon_dimension)

            self.select_icon = ImageTk.PhotoImage(self.select_nomogram_img)
            self.control_point_icon = ImageTk.PhotoImage(self.control_point_img)
            self.bezier_icon = ImageTk.PhotoImage(self.bezier_img)
            self.axis_entry_icon = ImageTk.PhotoImage(self.axis_entry_img)
            self.isopleth_icon = ImageTk.PhotoImage(self.isopleth_img)

            self.load_project_button = tk.Button(toolbar_frame, text="Load Project", command=self.load_project)
            self.save_project_button = tk.Button(toolbar_frame, text="Save Project", command=self.save_project)
            self.select_button = tk.Button(toolbar_frame, image=self.select_icon, command=self.select_image_file)
            self.control_point_button = tk.Button(toolbar_frame, image=self.control_point_icon,
                                                  command=self.pick_control_point)
            self.bezier_button = tk.Button(toolbar_frame, image=self.bezier_icon, command=self.draw_bezier)
            self.axis_entry_button = tk.Button(toolbar_frame, image=self.axis_entry_icon, command=self.pick_axis_point)
            self.isopleth_button = tk.Button(toolbar_frame, image=self.isopleth_icon, command=self.create_isopleth)

            self.load_project_button.pack(side=tk.LEFT, padx=50, pady=2, fill=tk.X)
            self.save_project_button.pack(side=tk.LEFT, padx=5, pady=2, fill=tk.X)
            self.select_button.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X)
            ToolTip(self.select_button, "Load Nomogram Image - shortcut : Control-l")
            self.control_point_button.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X)
            ToolTip(self.control_point_button, "Select Control Point - shortcut : Control-c")
            self.bezier_button.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X)
            ToolTip(self.bezier_button, "Draw Bezier Curve - shortcut : Control-b")
            self.axis_entry_button.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X)
            ToolTip(self.axis_entry_button, "Enter a Point on the Axis - shortcut : Control-a")
            self.isopleth_button.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X)
            ToolTip(self.isopleth_button, "Create an Isopleth - shortcut : Control-i")

            self.axis_label = tk.Label(toolbar_frame, text="Select Axis:")
            self.axis_label.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X)
            self.axis_id_variable = tk.StringVar(toolbar_frame)
            self.axis_id_variable.set("Select axis:")

            self.axis_id_dropdown = tk.OptionMenu(toolbar_frame, self.axis_id_variable, *["Select axis:"])
            self.axis_id_dropdown.pack(side=tk.LEFT, padx=5, pady=2, fill=tk.X)
            self.populate_axis_id_dropdown()
            self.distribution_label = tk.Label(toolbar_frame, text="Enter Distribution:")
            self.distribution_entry = tk.Entry(toolbar_frame)
            self.distribution_label.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X)
            self.distribution_entry.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X)
            self.save_distribution_button = tk.Button(toolbar_frame, text="Save Distribution",
                                                      command=self.save_distribution)
            self.save_distribution_button.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X)

            toolbar_frame.pack(side=tk.TOP, fill=tk.X)
        except Exception as e:
            print(traceback.print_exc(), f"{e}")

    def create_left_panel(self):
        self.left_panel_frame = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        self.left_panel_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.title = tk.Label(self.left_panel_frame, text="List of Points and Distributions")
        self.title.pack()
        self.left_panel_canvas = tk.Canvas(self.left_panel_frame)
        self.left_panel_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.left_panel_canvas.create_window((0, 0), window=self.left_panel_content, anchor=tk.NW)

        self.scrollbar = tk.Scrollbar(self.left_panel_frame, orient=tk.VERTICAL, command=self.left_panel_canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.left_panel_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.left_panel_content = tk.Frame(self.left_panel_canvas)
        self.left_panel_content.bind("<Configure>", lambda event: self.on_frame_configure())

    def update_left_panel_content(self):
        pass
        # for widget in self.left_panel_content.winfo_children():
        #     widget.destroy()
        # for axis_id, control_points in self.control_points.items():
        #     axis_label = tk.Label(self.left_panel_content, text=f"Axis ID: {axis_id}")
        #     axis_label.pack()
        #
        #     control_points_label = tk.Label(self.left_panel_content, text="Control Points:")
        #     control_points_label.pack()
        #     for i, (x, y) in enumerate(control_points):
        #         control_point_label = tk.Label(self.left_panel_content, text=f"  ({x}, {y})")
        #         control_point_label.pack()
        #
        #     if axis_id in self.axis_points:
        #         axis_values_label = tk.Label(self.left_panel_content, text="Axis Values:")
        #         axis_values_label.pack()
        #         for i, (x, y, value) in enumerate(self.axis_points[axis_id]):
        #             axis_value_label = tk.Label(self.left_panel_content, text=f"  ({x}, {y}, {value})")
        #             axis_value_label.pack()
        #
        #     if axis_id in self.nomogram_axes:
        #         distributions_label = tk.Label(self.left_panel_content, text="Distributions:")
        #         distributions_label.pack()
        #
        #         if self.nomogram_axes[axis_id].get_distribution() is not None:
        #             distribution = str(self.nomogram_axes[axis_id].get_distribution())
        #             distribution_label = tk.Label(self.left_panel_content, text=f"{distribution}")
        #             distribution_label.pack()
        #
        # self.left_panel_canvas.update_idletasks()
        # self.left_panel_canvas.configure(scroll region=self.left_panel_canvas.bbox("all"))
        # self.left_panel_content.pack()

    def on_frame_configure(self):
        self.left_panel_canvas.configure(scrollregion=self.left_panel_canvas.bbox("all"))

    def populate_axis_id_dropdown(self):
        if self.control_points:
            self.axis_id_dropdown['menu'].delete(0, 'end')
            self.axis_id_dropdown['menu'].add_separator()

        self.axis_id_dropdown['menu'].add_command(label="Add a new axis", command=self.add_new_axis_id)

    def set_axis_id(self, axis_id: str):
        self.axis_id_variable.set(axis_id)

    def add_new_axis_id(self, new_axis_id=None):
        if new_axis_id is None:
            new_axis_id = simpledialog.askstring("Add New Axis ID", "Enter a new axis ID:")
        if new_axis_id not in self.control_points:
            self.control_points[new_axis_id] = []
            self.axis_id_dropdown['menu'].add_command(label=new_axis_id,
                                                      command=lambda: self.set_axis_id(new_axis_id))
            self.axis_id_variable.set(new_axis_id)
        else:
            new_axis_id = messagebox.showerror("Error", "This Axis ID already exists")
            self.add_new_axis_id()

    def select_image_file(self, file_path=None):
        if file_path is None:
            self.file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        else:
            self.file_path = file_path
        try:
            if self.file_path:
                self.original_img = Image.open(self.file_path)
                canvas_width, canvas_height = DEFAULT_CANVAS_WIDTH, DEFAULT_CANVAS_HEIGHT
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
                    self.image_to_opencv((new_width, new_height))

        except Exception as e:
            print(traceback.print_exc(), f"{e}")

    def display_image(self, image: Image.Image):
        if self.canvas:
            self.canvas = None
            self.original_img = None

        self.canvas = tk.Canvas(self.root, width=image.width * 2,
                                height=image.height + 2 * DEFAULT_CANVAS_IMAGE_OFFSET,
                                background="white")
        self.canvas.pack()
        photo = ImageTk.PhotoImage(image=image)
        self.canvas.create_image(DEFAULT_CANVAS_IMAGE_OFFSET, DEFAULT_CANVAS_IMAGE_OFFSET, anchor=tk.NW, image=photo)
        self.canvas.image = photo

    def image_to_opencv(self, size):
        self.display_image(self.original_img)
        self.opencv_image = cv2.imread(self.file_path)
        self.opencv_image = cv2.resize(self.opencv_image, size)

        self.opencv_image_gray = cv2.cvtColor(self.opencv_image, cv2.COLOR_BGR2GRAY)
        self.opencv_image_blurred = cv2.GaussianBlur(self.opencv_image_gray, (5, 5), 0)
        self.opencv_image_edges = cv2.Canny(self.opencv_image_blurred, 50, 150)
        self.opencv_image_contours, _ = cv2.findContours(self.opencv_image_edges, cv2.RETR_EXTERNAL,
                                                         cv2.CHAIN_APPROX_SIMPLE)
        for contour in self.opencv_image_contours:
            contour += DEFAULT_CANVAS_IMAGE_OFFSET
        self.opencv_image_points = []
        for contour in self.opencv_image_contours:
            for point in contour:
                x, y = point[0]
                self.opencv_image_points.append((x, y))

    def pick_control_point(self):
        self.canvas.bind("<Button-1>", self.capture_bezier_coordinates)

    def pick_axis_point(self):
        self.canvas.bind("<Button-1>", self.capture_axis_point_coordinates)

    def capture_bezier_coordinates(self, event):
        axis_id = self.axis_id_variable.get()
        if axis_id == "Select axis:" or axis_id is None:
            messagebox.showerror("Error", "Please select an axis name")
        try:

            x, y = calculate_opencv_closest_point(self.opencv_image_points, self.canvas.canvasx(event.x),
                                                  self.canvas.canvasy(event.y))

            self.control_points[axis_id].append((x, y))

            control_point_id = f"control{axis_id}_{len(self.control_points[axis_id]) - 1}"

            self.canvas.create_oval(
                x - DEFAULT_BEZIER_CONTROL_SIZE, y - DEFAULT_BEZIER_CONTROL_SIZE, x + DEFAULT_BEZIER_CONTROL_SIZE,
                y + DEFAULT_BEZIER_CONTROL_SIZE,
                fill=DEFAULT_BEZIER_CONTROL_COLOUR, outline="black",
                tags=(control_point_id, "control_points", f"control_points_{axis_id}")
            )

            # Bind events only for the newly created control point
            self.adjust_point(control_point_id, axis_id)
            self.update_left_panel_content()
            if axis_id in self.nomogram_axes:  # if there is already a Bézier curve
                self.draw_bezier(axis_id)
                self.update_points(axis_id)
        finally:
            self.canvas.unbind("<Button-1>")

    def capture_axis_point_coordinates(self, event):
        axis_id = self.axis_id_variable.get()
        if axis_id == "Select axis:" or axis_id is None:
            messagebox.showerror("Error", "Please select an axis name")
        try:
            if self.nomogram_axes[axis_id].get_axis_drawn():
                x, y = calculate_opencv_closest_point(self.opencv_image_points, self.canvas.canvasx(event.x),
                                                      self.canvas.canvasy(event.y))
                point_value = simpledialog.askfloat("Enter Point Value", "Enter the value for the selected point:")

                if point_value is not None:
                    if axis_id not in self.control_points.keys():
                        messagebox.showwarning("Curve Not Found", f"Bezier curve for axis '{axis_id}' does not exist.")
                    elif axis_id not in self.axis_points.keys():
                        self.axis_points[axis_id] = []
                    self.axis_points[axis_id].append((x, y, point_value))
                    axis_point_id = f"axis{axis_id}_{len(self.axis_points[axis_id]) - 1}"

                    self.canvas.create_oval(
                        x - DEFAULT_AXIS_CONTROL_SIZE, y - DEFAULT_AXIS_CONTROL_SIZE, x + DEFAULT_AXIS_CONTROL_SIZE,
                        y + DEFAULT_AXIS_CONTROL_SIZE,
                        fill=DEFAULT_AXIS_CONTROL_COLOUR, outline="black",
                        tags=(axis_point_id, "axis_points", f"axis_points_{axis_id}")
                    )
                    self.adjust_point(axis_point_id, axis_id)
                    self.update_left_panel_content()
                    self.update_points(axis_id)

        finally:
            self.canvas.unbind("<Button-1>")

    def adjust_point(self, point_id: str, axis_id: str):
        self.canvas.tag_bind(point_id, "<Button-1>",
                             lambda event: self.start_adjust_point(event, point_id))
        self.canvas.tag_bind(point_id, "<B1-Motion>",
                             lambda event: self.drag_point(event, axis_id, point_id))
        self.canvas.tag_bind(point_id, "<ButtonRelease-1>",
                             lambda event: self.stop_drag_point(event, axis_id, point_id))

    def start_adjust_point(self, event, point_id: str):
        # Record the starting position of the control point
        # adapted from https://stackoverflow.com/questions/29789554/tkinter-draw-rectangle-using-a-mouse
        self.start_x, self.start_y = calculate_opencv_closest_point(self.opencv_image_points,
                                                                    self.canvas.canvasx(event.x),
                                                                    self.canvas.canvasy(event.y))
        self.current_point_id = point_id

    def drag_point(self, event, axis_id: str, point_id: str):
        cur_x, cur_y = calculate_opencv_closest_point(self.opencv_image_points, self.canvas.canvasx(event.x),
                                                      self.canvas.canvasy(event.y))
        if cur_x > DEFAULT_CANVAS_WIDTH:
            cur_x = DEFAULT_CANVAS_WIDTH
        elif cur_x < 0:
            cur_x = 0
        if cur_y > DEFAULT_CANVAS_HEIGHT:
            cur_y = DEFAULT_CANVAS_HEIGHT
        elif cur_y < 0:
            cur_y = 0
        delta_x = cur_x - self.start_x
        delta_y = cur_y - self.start_y

        # Move the control point and update the starting position
        self.canvas.move(point_id, delta_x, delta_y)
        self.start_x = cur_x
        self.start_y = cur_y

        point_index = int(point_id.split('_')[-1])
        if "control" in point_id:
            # Update the control point's position in the data structure
            self.control_points[axis_id][point_index] = (cur_x, cur_y)
            self.update_bezier(axis_id)

        elif "axis" in point_id:
            self.axis_points[axis_id][point_index] = (cur_x, cur_y, self.axis_points[axis_id][point_index][-1])

    def stop_drag_point(self, event, axis_id: str, point_id: str):
        # Update the control point's position in the data structure
        x, y = calculate_opencv_closest_point(self.opencv_image_points, self.canvas.canvasx(event.x),
                                              self.canvas.canvasy(event.y))
        point_index = int(point_id.split('_')[-1])

        if "control" in point_id:
            self.control_points[axis_id][point_index] = (x, y)
            self.update_bezier(axis_id)
            self.update_points(axis_id)
        elif "axis" in point_id:
            self.axis_points[axis_id][point_index] = (x, y, self.axis_points[axis_id][point_index][-1])
            self.update_points(axis_id)
        self.update_left_panel_content()

    def draw_bezier(self, bezier_axis_id=None):
        if bezier_axis_id is None:
            bezier_axis_id = self.axis_id_variable.get()
        if bezier_axis_id == "Select axis:":
            messagebox.showinfo("Error", "Please select an axis")
        # Check if a BezierCurve object already exists for the axis
        if bezier_axis_id in self.nomogram_axes:
            curve = self.nomogram_axes[bezier_axis_id]
            curve.control_points = self.control_points[bezier_axis_id]  # Update the control points
        else:
            # Create a new BezierCurve object
            self.nomogram_axes[bezier_axis_id] = Axis(bezier_axis_id, self.control_points[bezier_axis_id],
                                                      self.canvas)

        self.nomogram_axes[bezier_axis_id].draw()

    def update_bezier(self, axis_id: str):
        if axis_id not in self.control_points or axis_id not in self.nomogram_axes:
            pass
        else:
            self.draw_bezier(axis_id)

    def save_distribution(self, distribution_text=None):
        if distribution_text is None:
            distribution_text = self.distribution_entry.get()
        axis_id = self.axis_id_variable.get()
        if axis_id and distribution_text:
            try:
                self.nomogram_axes[axis_id].add_distribution(distribution_text)
            except ValueError:
                messagebox.showerror("Error", "Error : No Axis with this identifier exists")

        self.distributions += 1
        self.update_left_panel_content()

    def load_project(self):
        try:
            file_path_to_load = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
            if not file_path_to_load:
                messagebox.showinfo("Info", "Load operation canceled.")
                return

            with open(file_path_to_load, "r") as json_file:
                project_data = json.load(json_file)

            directory_path = os.path.dirname(file_path_to_load)
            self.select_image_file(os.path.join(directory_path, project_data.get("file_path")))

            control_points = project_data.get("control_points")
            axis_points = project_data.get("axis_points")
            distributions = project_data.get("distributions")
            for i in control_points.keys():
                self.add_new_axis_id(i)
                self.nomogram_axes[i] = Axis(i, control_points[i], self.canvas)
                self.nomogram_axes[i].draw()
                self.nomogram_axes[i].set_axis_points(axis_points[i])
                self.save_distribution(distributions[i])

        except Exception as e:
            print(traceback.print_exc(), f"{e}")
            messagebox.showerror("Error", str(e))

    def save_project(self):
        if not self.original_img:
            messagebox.showerror("Error", "No image loaded")
            return
        self.check_min_three_axis_generated()
        try:
            project_data = {
                "file_path": os.path.basename(self.file_path),
                "control_points": self.control_points,
                "axis_points": self.axis_points,
                "distributions": {axis_id: axis.get_distribution_str() for axis_id, axis in self.nomogram_axes.items()},
            }

            def convert(o):
                if isinstance(o, numpy.int64):
                    return int(o)
                elif isinstance(o, numpy.float64):
                    return float(o)
                elif isinstance(o, numpy.int32):
                    return int(o)

            file_path_to_save = filedialog.asksaveasfilename(defaultextension=".json",
                                                             filetypes=[("JSON files", "*.json")])
            if not file_path_to_save:
                return

            with open(file_path_to_save, "w") as json_file:
                json.dump(project_data, json_file, indent=4, default=convert)

        except Exception as e:
            print(traceback.print_exc(), f"{e}")
            messagebox.showerror("Error", f"Failed to save project: {e}")

    def update_points(self, axis_id: str):
        for i in self.nomogram_axes.keys():
            if self.nomogram_axes[i].axis_equation_produced:
                self.number_of_complete_axis += 1
        if axis_id in self.nomogram_axes:
            if axis_id in self.axis_points:
                self.nomogram_axes[axis_id].set_axis_points(self.axis_points[axis_id])
            if axis_id in self.control_points:
                self.nomogram_axes[axis_id].set_control_points(self.control_points[axis_id])

    def create_isopleth(self):

        isopleth_id = self.number_isopleths
        if len(self.control_points) == 0:
            messagebox.showerror("Error", "No Axis Exist")
            return False
        self.check_min_three_axis_generated()
        try:

            self.time = 0
            while self.time < 6:
                self.time += 1
                self.isopleths[isopleth_id] = Isopleth(isopleth_id, self.canvas, self.nomogram_axes)
                self.number_isopleths += 1
                self.root.after(1000, self.create_isopleth)

        except Exception as e:
            print(traceback.print_exc(), f"{e}")

    def delete_point(self, axis_id, point_id):
        point_index = int(point_id.split('_')[-1])
        self.canvas.delete(point_id)
        print(point_id)
        if "control" in point_id:
            self.control_points[axis_id].pop(point_index)
            self.update_bezier(axis_id)
        elif "axis" in point_id:
            self.axis_points[axis_id].pop(point_index)
        self.update_points(axis_id)
        self.canvas.unbind("<BackSpace>")

    def check_min_three_axis_generated(self) -> bool:
        if self.number_of_complete_axis < 3:
            messagebox.showerror("Error", "At least three axis must be created")
            return False
if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(width=False, height=False)  # disables windows resizing for consistency
    app = NomogramApp(root)

    root.mainloop()
