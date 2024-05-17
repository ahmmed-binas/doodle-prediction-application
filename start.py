import pickle
import os.path
import tkinter.messagebox
from tkinter import *
import tkinter as tk
from tkinter import simpledialog
import PIL
from tkinter import Tk, Canvas, Frame, Button, Label
from tkinter import colorchooser
import PIL.Image
import PIL.ImageDraw
from PIL import Image
import PIL.ImageDraw
import cv2 as cv
import numpy as np
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import BernoulliNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
import tkinter.filedialog


class DrawingClassifier:
    
    def __init__(self):
        self.class1, self.class2, self.class3 = None, None, None
        self.class1_counter, self.class2_counter, self.class3_counter = None, None, None
        self.clf = None
        self.proj_name = None
        self.root = None
        self.image1 = None
        self.status_label = None
        self.canvas = None
        self.drew = None
        self.brush_width = 13
        self.classes_prompt()
        self.init_gui()
    
    def classes_prompt(self):
        msg = Tk()
        msg.withdraw()

        self.proj_name = simpledialog.askstring("Project Name", "Please enter your project name below", parent=msg)
        if os.path.exists(self.proj_name):
            with open(f"{self.proj_name}/{self.proj_name}_data.pickle", "rb") as f:
                data = pickle.load(f)
            self.class1 = data['c1']
            self.class2 = data['c2']
            self.class3 = data['c3']
            self.class1_counter = data['c1c']
            self.class2_counter = data['c2c']
            self.class3_counter = data['c3c']
            self.clf = data['clf']
            self.proj_name = data['pname']
        else:
            self.class1 = simpledialog.askstring('Class 1', "What is the first class called?", parent=msg)
            self.class2 = simpledialog.askstring('Class 2', "What is the second class called?", parent=msg)
            self.class3 = simpledialog.askstring('Class 3', "What is the third class called?", parent=msg)
            
            self.class1_counter = 1
            self.class2_counter = 1
            self.class3_counter = 1
            self.clf = LinearSVC()

            os.mkdir(self.proj_name)
            os.chdir(self.proj_name)
            os.mkdir(self.class1)
            os.mkdir(self.class2)
            os.mkdir(self.class3)
            os.chdir("..")
    
    def init_gui(self):
        WIDTH = 1000
        HEIGHT = 1000
        BLACK = "#000000"  
        WHITE = "#FFFFFF"

        self.root = Tk()
        self.root.title(f"Ahmed's Drawing Classifier Experiment - {self.proj_name}")

        self.canvas = Canvas(self.root, width=500, height=300, bg=WHITE)  # Adjust width and height
        self.canvas.grid(row=0, column=0)  # Specify the row and column parameters for the grid


        self.image1 = PIL.Image.new("RGB", (WIDTH, HEIGHT), WHITE)
        self.draw = PIL.ImageDraw.Draw(self.image1)
        self.canvas.bind("<B1-Motion>", self.paint)

        btn_frame = Frame(self.root)
        btn_frame.grid(row=0, column=1, sticky="nsew")


        btn_style = {
            "font": ("Arial", 10),
            "bg": "darkblue",
            "fg": "black",
            "activebackground": "lightgreen",
            "activeforeground": "black",
            "width": 10
        }

        class1_btn = Button(btn_frame, text=self.class1, command=lambda: self.save(1), **btn_style)
        class1_btn.grid(row=0, column=0, sticky="ew")

        class2_btn = Button(btn_frame, text=self.class2, command=lambda: self.save(2), **btn_style)
        class2_btn.grid(row=1, column=0, sticky="ew")

        class3_btn = Button(btn_frame, text=self.class3, command=lambda: self.save(3), **btn_style)
        class3_btn.grid(row=2, column=0, sticky="ew")

        bm_btn = Button(btn_frame, text="Brush-", command=self.brushminus, **btn_style)
        bm_btn.grid(row=3, column=0, sticky="ew")

        clear_btn = Button(btn_frame, text="Erase All", command=self.clear, **btn_style)
        clear_btn.grid(row=4, column=0, sticky="ew")

        bp_btn = Button(btn_frame, text="Brush+", command=self.brushplus, **btn_style)
        bp_btn.grid(row=5, column=0, sticky="ew")

        train_btn = Button(btn_frame, text="Train Model", command=self.train_model, **btn_style)
        train_btn.grid(row=6, column=0, sticky="ew")

        save_btn = Button(btn_frame, text="Save", command=self.save_model, **btn_style)
        save_btn.grid(row=7, column=0, sticky="ew")

        load_btn = Button(btn_frame, text="Load Model", command=self.load_model, **btn_style)
        load_btn.grid(row=8, column=0, sticky="ew")

        change_btn = Button(btn_frame, text="Change Model", command=self.rotate_model, **btn_style)
        change_btn.grid(row=9, column=0, sticky="ew")

        predict_btn = Button(btn_frame, text="Predict!", command=self.predict, **btn_style)
        predict_btn.grid(row=10, column=0, sticky="ew")

        save_all_btn = Button(btn_frame, text="Save All", command=self.save_all, **btn_style)
        save_all_btn.grid(row=11, column=0, sticky="ew")

        self.status_label = Label(btn_frame, text=f"Current Model: {type(self.clf).__name__}")
        self.status_label.config(font=("Arial", 10))
        self.status_label.grid(row=12, column=0, sticky="ew")

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.attributes("-topmost", True)
        self.root.mainloop()



    def paint(self, event):
        x1, y1 = (event.x - 1), (event.y - 1)
        x2, y2 = (event.x + 1), (event.y + 1)
        BLACK = "#000000"  # Color representation of black

        # Draw a black rectangle on the canvas
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=BLACK, width=self.brush_width)
        
        # Draw a white rectangle in the image
        self.draw.rectangle([x1, y1, x2, y2], fill=BLACK)
        
        
        
    def save(self, class_num):
        self.image1.save("temp.png")
        img = PIL.Image.open("temp.png")
        img.thumbnail((50, 50), PIL.Image.LANCZOS)


        if class_num == 1:
            img.save(f"{self.proj_name}/{self.class1}/{self.class1_counter}.png", "PNG")
            self.class1_counter += 1

        elif class_num == 2:
            img.save(f"{self.proj_name}/{self.class2}/{self.class2_counter}.png", "PNG")
            self.class2_counter += 1
        
        elif class_num == 3:
            img.save(f"{self.proj_name}/{self.class3}/{self.class3_counter}.png", "PNG")
            self.class3_counter += 1
         
        self.clear()

    def brushminus(self):
        if self.brush_width > 1:
            self.brush_width -= 1

    def brushplus(self):
        self.brush_width += 1

    def clear(self):
        self.canvas.delete("all")
        self.draw.rectangle([(0, 0), (1000, 1000)], fill="white")


    def train_model(self):
        img_list = []
        class_list = []

        for x in range(1, self.class1_counter):
            img_path = f"{self.proj_name}/{self.class1}/{x}.png"
            img = cv.imread(img_path)
            if img is not None:
                img = img[:, :, 0].reshape(-1)
                img_list.append(img)
                class_list.append(1)
            else:
                print(f"Failed to load image: {img_path}")


        for x in range(1, self.class2_counter):
            img_path = f"{self.proj_name}/{self.class2}/{x}.png"
            img = cv.imread(img_path)
            if img is not None:
                img = img[:, :, 0].reshape(-1)
                img_list.append(img)
                class_list.append(2)
            else:
                print(f"Failed to load image: {img_path}")


        for x in range(1, self.class3_counter):
            img_path = f"{self.proj_name}/{self.class3}/{x}.png"
            img = cv.imread(img_path)
            if img is not None:
                img = img[:, :, 0].reshape(-1)
                img_list.append(img)
                class_list.append(3)
            else:
                print(f"Failed to load image: {img_path}")

        if not img_list:
            print("No images loaded. Check file paths or image loading process.")
            return

        img_list = np.array(img_list)
        class_list = np.array(class_list)

        img_list = img_list.reshape(img_list.shape[0], -1)
        
        self.clf.fit(img_list, class_list)
        tkinter.messagebox.showinfo("Ahmed's experiment is done", "Model successfully trained", parent=self.root)




    def save_model(self):
        file_path = tkinter.filedialog.asksaveasfilename(defaultextension='.pickle')
        with open(file_path, "wb") as f:
            pickle.dump(self.clf, f)
        tkinter.messagebox.showinfo("Ahmmed's drawing classifier", "Model Saved Successfully", parent=self.root)

        
    def predict(self):
        self.image1.save('temp.png')
        img = PIL.Image.open('temp.png')
        img.thumbnail((50, 50), PIL.Image.LANCZOS)
        img.save("predictshape.png", "PNG")
        
        img = cv.imread("predictshape.png")[:, :, 0]
        img = img.reshape(2500)
        prediction = self.clf.predict([img])
        if prediction[0] == 1:
            tkinter.messagebox.showinfo("Ahmmed's Drawing Classifier", f"The drawing is likely to be {self.class1}", parent=self.root)
        elif prediction[0] == 2:
            tkinter.messagebox.showinfo("Ahmmed's Drawing Classifier", f"The drawing is likely to be {self.class2}", parent=self.root)
        elif prediction[0] == 3:
            tkinter.messagebox.showinfo("Ahmmed's Drawing Classifier", f"The drawing is likely to be {self.class3}", parent=self.root)
            
                    
    def rotate_model(self):
            if isinstance(self.clf, LinearSVC):
                self.clf = KNeighborsClassifier()
            elif isinstance(self.clf, KNeighborsClassifier):
                self.clf = LogisticRegression()
            elif isinstance(self.clf, LogisticRegression):
                self.clf = DecisionTreeClassifier()
            elif isinstance(self.clf, DecisionTreeClassifier):
                self.clf = RandomForestClassifier()
            elif isinstance(self.clf, RandomForestClassifier):
                self.clf = GaussianNB()
            elif isinstance(self.clf, GaussianNB):
                self.clf = LinearSVC()
        
    def save_all(self):
        data = {
            "c1": self.class1,
            "c2": self.class2,
            "c3": self.class3,
            "c1c": self.class1_counter,
            "c2c": self.class2_counter,
            "c3c": self.class3_counter,
            "clf": self.clf,
            "pname": self.proj_name
        }
        with open(f"{self.proj_name}/{self.proj_name}_data.pickle", "wb") as f:
            pickle.dump(data, f)
        tkinter.messagebox.showinfo("Ahmmed's Drawing Classifier", "Project Successfully Saved!", parent=self.root)

        

    def load_model(self):
        file_path = tkinter.filedialog.askopenfilename()
        with open(file_path, "rb") as r:
            data = pickle.load(r)
        self.class1 = data["c1"]
        self.class2 = data["c2"]
        self.class3 = data["c3"]
        self.class1_counter = data["c1c"]
        self.class2_counter = data["c2c"]
        self.class3_counter = data["c3c"]
        self.clf = data["clf"]
        self.proj_name = data["pname"]
        tkinter.messagebox.showinfo("Ahmmed's Drawing Classifier", "Model Loaded!", parent=self.root)
        
            
    def on_closing(self):
        answer = tkinter.messagebox.askyesno("Quit?", "Do you want to save your work?", parent=self.root)
        if answer is True:
            self.save_all()
            self.root.destroy()
        elif answer is False:
            self.root.destroy()
            
                

DrawingClassifier()