import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk

from Axis import BezierCurve
from DistributionParser import parse_distribution


class NomogramApp:
    def __init__(self, root):
        self.current_point_id = None
        self.start_y = None
        self.start_x = None
        self.button_status = tk.NORMAL
        self.root = root
        self.root.geometry("1280x800")
        self.root.title("Probabilistic Nomograms")
        self.canvas = None
        self.original_img = None
        self.control_points = {}
        self.axis_points = {}
        self.curve_objects = {}
        self.create_toolbar()
        self.distributions = {}

    def create_toolbar(self):
        # Create a frame to hold the toolbar buttons

        toolbar_frame = tk.Frame(self.root, bd=1, relief=tk.RAISED)

        icon_dimension = (32, 32)

        try:
            self.select_nomogram_img = Image.open("icons/select_nomogram.png").resize(icon_dimension)
            self.control_point_img = Image.open("icons/bezier-tool.png").resize(icon_dimension)
            self.bezier_img = Image.open("icons/draw_bezier.png").resize(icon_dimension)
            self.axis_entry_img = Image.open("icons/bezier-axis_entry.png").resize(icon_dimension)

            self.select_icon = ImageTk.PhotoImage(self.select_nomogram_img)
            self.control_point_icon = ImageTk.PhotoImage(self.control_point_img)
            self.bezier_icon = ImageTk.PhotoImage(self.bezier_img)
            self.axis_entry_icon = ImageTk.PhotoImage(self.axis_entry_img)

            self.select_button = tk.Button(toolbar_frame, image=self.select_icon, command=self.select_image_file)
            self.control_point_button = tk.Button(toolbar_frame, image=self.control_point_icon,
                                                  command=self.pick_control_point)
            self.bezier_button = tk.Button(toolbar_frame, image=self.bezier_icon, command=self.draw_bezier)
            self.axis_entry_button = tk.Button(toolbar_frame, image=self.axis_entry_icon, command=self.pick_axis_point)
            self.load_project_button = tk.Button(toolbar_frame, text="Load Project", command=self.load_project)
            self.save_project_button = tk.Button(toolbar_frame, text="Save Project", command=self.save_project)

            self.load_project_button.pack(side=tk.LEFT, padx=50, pady=2, fill=tk.X)
            self.save_project_button.pack(side=tk.LEFT, padx=50, pady=2, fill=tk.X)
            self.select_button.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X)
            self.control_point_button.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X)
            self.bezier_button.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X)
            self.axis_entry_button.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X)
            self.distribution_label = tk.Label(toolbar_frame, text="Enter Distribution:")
            self.distribution_entry = tk.Entry(toolbar_frame)
            self.distribution_label.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X)
            self.distribution_entry.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X)
            self.save_distribution_button = tk.Button(toolbar_frame, text="Save Distribution",
                                                      command=self.save_distribution)

            self.save_distribution_button.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X)
            toolbar_frame.pack(side=tk.TOP, fill=tk.X)
        except Exception as e:
            print("Error loading icon images:", e)

    def select_image_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        try:
            if file_path:
                self.original_img = Image.open(file_path)
                canvas_width, canvas_height = 1152, 720
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

        except Exception as e:
            messagebox.showerror("Error", e)

    def display_image(self, image):
        if self.canvas:
            self.canvas = None
            self.original_img = None
        self.canvas = tk.Canvas(self.root, width=image.width + 50, height=image.height + 50, background="white")
        self.canvas.pack()
        photo = ImageTk.PhotoImage(image=image)
        self.canvas.create_image(25, 25, anchor=tk.NW, image=photo)
        self.canvas.image = photo

    def pick_control_point(self):
        self.canvas.bind("<Button-1>", self.capture_bezier_coordinates)

    def capture_bezier_coordinates(self, event):
        axis_id = simpledialog.askstring("Enter Axis ID", "Enter an identifier for the axis:")
        if axis_id is not None:
            x, y = event.x, event.y

            if axis_id not in self.control_points:
                self.control_points[axis_id] = []
            self.control_points[axis_id].append((x, y))
            self.display_bezier_coordinates()

            point_size = 5
            control_point_id = f"control{axis_id}_{len(self.control_points[axis_id]) - 1}"

            self.canvas.create_oval(
                x - point_size, y - point_size, x + point_size, y + point_size,
                fill="red", outline="black", tags=(control_point_id, "control_point")
            )

            # Bind events only for the newly created control point
            self.move_point( control_point_id, axis_id)

        if axis_id in self.curve_objects:  # if there is already a bezier curve
            self.draw_bezier(axis_id)
        self.canvas.unbind("<Button-1>")

    def move_point(self, point_id, axis_id):
        self.canvas.tag_bind(point_id, "<Button-1>",
                             lambda event, axis=axis_id, id=point_id: self.start_drag(event, axis))
        self.canvas.tag_bind(point_id, "<B1-Motion>",
                             lambda event, axis=axis_id, id=point_id: self.drag(event, axis, id))
        self.canvas.tag_bind(point_id, "<ButtonRelease-1>",
                             lambda event, axis=axis_id, id=point_id: self.stop_drag(axis, id))

    def start_drag(self, event, point_id):
        # Record the starting position of the control point
        ## adapted from https://stackoverflow.com/questions/29789554/tkinter-draw-rectangle-using-a-mouse
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        self.current_point_id = point_id

    def drag(self, event, axis_id, point_id):
        # Move the control point based on the mouse movement
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        delta_x = cur_x - self.start_x
        delta_y = cur_y - self.start_y

        # Move the control point and update the starting position
        self.canvas.move(point_id, delta_x, delta_y)
        self.start_x = cur_x
        self.start_y = cur_y
        point_index = int(point_id.split('_')[-1])
        # Update the control point's position in the data structure
        if "control" in point_id:
            # Update the control point's position in the data structure

            self.control_points[axis_id][point_index] = (cur_x, cur_y)
            self.update_bezier(axis_id)

        elif "axis" in point_id:
            self.axis_points[axis_id][point_index] = (cur_x, cur_y, self.axis_points[axis_id][point_index][-1])

    def stop_drag(self, axis_id, point_id):
        # Update the control point's position in the data structure
        x, y = self.canvas.coords(point_id)[0], self.canvas.coords(point_id)[1]

        point_index = int(point_id.split('_')[-1])

        if "control" in point_id:
            self.control_points[axis_id][point_index] = (x, y)
            self.update_bezier(axis_id)
            self.display_bezier_coordinates()
        elif "axis" in point_id:
            self.axis_points[axis_id][point_index] = (x, y, self.axis_points[axis_id][point_index][-1])

            self.update_bezier(axis_id)
            self.display_axis_coordinates()

    def display_bezier_coordinates(self):
        # prints the control points to console
        if self.control_points:
            coordinates_str = ""
            for axis_id, coords in self.control_points.items():
                coordinates_str += f"{axis_id}:\n"
                coordinates_str += '\n'.join([f"  ({x}, {y})" for x, y in coords])
                coordinates_str += "\n\n"
            print(coordinates_str)

    def display_axis_coordinates(self):
        # prints the control points to console
        if self.axis_points:
            coordinates_str = ""
            for axis_id, coords in self.axis_points.items():
                coordinates_str += f"{axis_id}:\n"
                coordinates_str += '\n'.join([f"  ({x}, {y}, {point_value})" for x, y, point_value in coords])
                coordinates_str += "\n\n"
            print(coordinates_str)

    def draw_bezier(self, bezier_axis_id=None):
        if bezier_axis_id is None:
            bezier_axis_id = simpledialog.askstring("Enter Axis ID", "Enter the name of the axis you wish to draw:")
            if bezier_axis_id not in self.control_points:
                bezier_axis_id = simpledialog.askstring("Axis Not Found",
                                                        "Enter the name of the axis you wish to draw:")

        # Check if a BezierCurve object already exists for the axis
        if bezier_axis_id in self.curve_objects:
            curve = self.curve_objects[bezier_axis_id]
            curve.points = self.control_points[bezier_axis_id]  # Update the control points
        else:
            # Create a new BezierCurve object
            curve = BezierCurve(bezier_axis_id, self.control_points[bezier_axis_id], self.canvas)
            self.curve_objects[bezier_axis_id] = curve

        curve.draw(self.canvas)

    def update_bezier(self, axis_id):
        if axis_id not in self.control_points or axis_id not in self.curve_objects:
            pass
        else:
            self.draw_bezier(axis_id)

    def pick_axis_point(self):
        self.canvas.bind("<Button-1>", self.capture_axis_point_coordinates)

    def capture_axis_point_coordinates(self, event):
        axis_id = simpledialog.askstring("Enter Axis ID", "Enter the identifier for the axis:")
        if axis_id is not None:
            x, y = event.x, event.y

            point_value = simpledialog.askfloat("Enter Point Value", "Enter the value for the selected point:")
            # Unbind the callback to stop capturing coordinates
            self.canvas.unbind("<Button-1>")
            if point_value is not None:
                if axis_id not in self.control_points.keys():
                    messagebox.showwarning("Curve Not Found", f"Bezier curve for axis '{axis_id}' does not exist.")
                    pass
                elif axis_id not in self.axis_points.keys():
                    self.axis_points[axis_id] = []
                self.axis_points[axis_id].append((x, y, point_value))

                self.display_axis_coordinates()
                point_size = 2.5
                axis_point_id = f"axis{axis_id}_{len(self.axis_points[axis_id]) - 1}"

                self.canvas.create_oval(
                    x - point_size, y - point_size, x + point_size, y + point_size,
                    fill="red", outline="black", tags=(axis_point_id, "axis_point")
                )
                self.move_point( axis_point_id, axis_id)
            self.canvas.unbind("<Button-1>")

    def save_distribution(self):
        axis_id = simpledialog.askstring("Enter Axis ID", "Enter the identifier for the axis:")
        distribution = self.distribution_entry.get()
        if axis_id and distribution:
            self.distributions[axis_id] = parse_distribution(distribution)
            print(self.distributions[axis_id])
            messagebox.showinfo("Distribution Saved",
                                f"Statistical distribution '{distribution}' saved for axis '{axis_id}'.")

    def load_project(self):
        pass

    def save_project(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(width=False, height=False)  # disables windows resizing for consistency
    app = NomogramApp(root)

    root.mainloop()
