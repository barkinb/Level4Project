import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import cv2
import numpy as np


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
        self.lasso_points = None
        self.lasso_started = None
        self.root = root
        self.root.geometry("1280x800")
        self.root.title("Nomogram Image Processing")
        self.canvas = None
        self.original_img = None
        self.nomogram = None
        self.manual_drawn_contours = []
        self.create_toolbar()

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

            # Convert lasso points to a numpy array
            lasso_points_np = np.array(self.lasso_points, dtype=np.int32)

            # Create a mask image with zeros
            mask = np.zeros((self.original_img.size[1], self.original_img.size[0]), dtype=np.uint8)

            # Draw the lasso polygon on the mask
            cv2.fillPoly(mask, [lasso_points_np], color=(255, 255, 255))

            # Create an image with contours drawn on it
            contours_image = np.zeros_like(self.nomogram.img)
            for contour in self.nomogram.contours:
                area = cv2.contourArea(contour)
                if area > 100:  # You can adjust this threshold based on your needs
                    cv2.drawContours(contours_image, [contour], -1, (0, 255, 0), 2)

            # Mask the contours image with the lasso mask
            masked_contours = cv2.bitwise_and(contours_image, contours_image, mask=mask)

            # Convert the result to PIL Image
            contours_pil = Image.fromarray(cv2.cvtColor(masked_contours, cv2.COLOR_BGR2RGB))

            # Create a Tkinter PhotoImage object from the PIL Image
            photo = ImageTk.PhotoImage(image=contours_pil)

            # Update the existing canvas with the new image
            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            self.canvas.image = photo

    def create_toolbar(self):
        # Create a frame to hold the toolbar buttons

        toolbar_frame = tk.Frame(self.root, bd=1, relief=tk.RAISED)

        icon_dimension = (32, 32)

        try:
            self.select_image = Image.open("icons/select_image_icon.png").resize(icon_dimension)
            self.undo = Image.open("icons/undo.png").resize(icon_dimension)
            self.delete_all = Image.open("icons/remove.png").resize(icon_dimension)
            self.get_lasso = Image.open("icons/lasso.png").resize(icon_dimension)

            self.select_icon = ImageTk.PhotoImage(self.select_image)
            self.undo_icon = ImageTk.PhotoImage(self.undo)
            self.delete_icon = ImageTk.PhotoImage(self.delete_all)
            self.lasso_icon = ImageTk.PhotoImage(self.get_lasso)

            self.select_button = tk.Button(toolbar_frame, image=self.select_icon, command=self.select_image_file)
            self.undo_button = tk.Button(toolbar_frame, image=self.undo_icon, command=self.undo)
            self.delete_button = tk.Button(toolbar_frame, image=self.delete_icon, command=self.delete_all_contours)
            self.lasso_button = tk.Button(toolbar_frame, image=self.lasso_icon, command=self.start_axis_selection)

            self.select_button.pack(side=tk.LEFT, padx=2, pady=2)
            self.undo_button.pack(side=tk.LEFT, padx=2, pady=2)
            self.delete_button.pack(side=tk.LEFT, padx=2, pady=2)
            self.lasso_button.pack(side=tk.LEFT, padx=2, pady=2)

            toolbar_frame.pack(side=tk.TOP, fill=tk.X)
        except Exception as e:
            print("Error loading icon images:", e)


if __name__ == "__main__":
    root = tk.Tk()
    app = NomogramApp(root)

    root.mainloop()
