import tkinter as tk
import cv2
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np

class Nomogram:
    def __init__(self):
        self.gray = None
        self.img = None
        self.contours = None
        self.axis_contours = None
        self.edges = None
        self.blurred = None

    def load_image(self, path):
        self.img = cv2.imread(path, -1)
        self.gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        self.blurred = cv2.GaussianBlur(self.gray, (5, 5), 0)
        self.edges = cv2.Canny(self.blurred, 50, 150)
        self.contours, _ = cv2.findContours(self.edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.axis_contours = [contour for contour in self.contours if cv2.contourArea(contour) > 100]

    def draw_nomogram(self):
        height, width = self.img.shape[:2]
        self.axis_img = np.zeros((height, width, 3), dtype=np.uint8)
        self.axis_img.fill(255)  # Fill with white background
        cv2.drawContours(self.axis_img, self.axis_contours, -1, (0, 0, 255), 2)
        return self.axis_img

class App:
    def __init__(self, root):
        self.current_contour = None
        self.nomogram = None
        self.root = root
        self.root.title("Nomogram Image Processing")

        self.load_button = tk.Button(self.root, text="Load Image", command=self.load_image)
        self.process_button = tk.Button(self.root, text="Process Image", command=self.process_image)
        self.undo_button = tk.Button(self.root, text="Undo Last Draw", command=self.undo_last_draw)
        self.delete_all_button = tk.Button(self.root, text="Delete All Contours", command=self.delete_all_contours)
        self.delete_manual_button = tk.Button(self.root, text="Delete Manual Contours",
                                              command=self.delete_manual_contours)
        self.draw_line_button = tk.Button(self.root, text="Draw Straight Line", command=self.start_drawing_line)

        self.load_button.pack()
        self.process_button.pack()
        self.undo_button.pack()
        self.delete_all_button.pack()
        self.delete_manual_button.pack()
        self.draw_line_button.pack()

        self.canvas = tk.Canvas(self.root, width=640, height=480, background="white")
        self.canvas.pack()

        self.process_button.config(state=tk.DISABLED)
        self.undo_button.config(state=tk.DISABLED)
        self.delete_all_button.config(state=tk.DISABLED)
        self.delete_manual_button.config(state=tk.DISABLED)
        self.draw_line_button.config(state=tk.DISABLED)
        self.drawing = False
        self.drawing_line = False
        self.prev_x, self.prev_y = 0, 0
        self.line_start_x, self.line_start_y = 0, 0

        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        try:
            if file_path:
                self.nomogram = Nomogram()
                self.nomogram.load_image(file_path)
                self.process_button.config(state=tk.NORMAL)
                self.draw_line_button.config(state=tk.NORMAL)
                self.delete_all_button.config(state=tk.NORMAL)
                self.delete_manual_button.config(state=tk.NORMAL)

                self.undo_button.config(state=tk.NORMAL)

        except Exception as e:
            tk.messagebox.showerror("Error", e)

    def process_image(self):
        if self.nomogram.img is not None:
            self.display_image()
        else:
            tk.messagebox.showerror("Error", "Please load an image first.")

    def display_image(self):
        if self.nomogram.img is not None:
            original_img = cv2.cvtColor(self.nomogram.img, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(original_img)
            canvas_width, canvas_height = self.canvas.winfo_width(), self.canvas.winfo_height()
            img_width, img_height = image.size
            scale_factor = min(canvas_width / img_width, canvas_height / img_height)
            new_width, new_height = int(img_width * scale_factor), int(img_height * scale_factor)
            image = image.resize((new_width, new_height))
            photo = ImageTk.PhotoImage(image=image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            self.canvas.image = photo
            self.draw_nomogram_on_image()

    def draw_nomogram_on_image(self):
        if self.nomogram.img is not None:
            axis_img = self.nomogram.draw_nomogram()
            if self.drawing_line:
                cv2.line(axis_img, (self.line_start_x, self.line_start_y), (self.prev_x, self.prev_y), (0, 255, 0),
                         2)
            if self.drawing:
                cv2.drawContours(axis_img, [self.current_contour], -1, (0, 0, 255), 2)
            axis_img = cv2.cvtColor(axis_img, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(axis_img)
            canvas_width, canvas_height = self.canvas.winfo_width(), self.canvas.winfo_height()
            img_width, img_height = image.size
            scale_factor = min(canvas_width / img_width, canvas_height / img_height)
            new_width, new_height = int(img_width * scale_factor), int(img_height * scale_factor)
            image = image.resize((new_width, new_height))
            photo = ImageTk.PhotoImage(image=image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            self.canvas.image = photo

    def start_draw(self, event):
        if self.drawing_line:
            return
        self.drawing = True
        self.current_contour = []
        self.prev_x, self.prev_y = event.x, event.y

    def draw(self, event):
        if self.drawing_line:
            return
        if self.drawing:
            x, y = event.x, event.y
            self.current_contour.append([[x, y]])
            self.canvas.create_line(self.prev_x, self.prev_y, x, y, fill='red', width=2)
            self.prev_x, self.prev_y = x, y

    def stop_draw(self, event):
        if self.drawing_line:
            return
        if self.drawing:
            self.drawing = False
            self.nomogram.axis_contours.append(self.current_contour)
            self.current_contour = []

    def start_drawing_line(self):
        self.drawing_line = True
        self.line_start_x, self.line_start_y = self.prev_x, self.prev_y

    def undo_last_draw(self):
        if self.nomogram.axis_contours:
            self.nomogram.axis_contours.pop()
            self.display_image()

    def delete_all_contours(self):
        self.nomogram.axis_contours = []
        self.display_image()

    def delete_manual_contours(self):
        if self.nomogram.axis_contours:
            del self.nomogram.axis_contours[-1]
            self.display_image()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    app = App(root)
    root.mainloop()
