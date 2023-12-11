from tkinter import * 
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.messagebox import askyesno 

import cv2
from PIL import Image, ImageTk
import os
import pytesseract
from pathlib import Path
import re

import threading
from ocr_med.json_functions.file_functions import FileFunctions

pytesseract.pytesseract.tesseract_cmd = r'Tesseract/tesseract.exe'

class ImageCropper:
    def __init__(self, root, image):
        self.root = root
        self.image = image
        self.new_image = image

        self.input_text = StringVar() 
        self.ocr_text = StringVar()

        self.plot_roi_coordinates:StringVar = []
        self.roi_coordinates:StringVar = []
        self.ocr_value:StringVar = []
        self.image_roi:StringVar = []

        self.get_value:bool = False
        self.buttonState:int = None
        
        self.style = ttk.Style()
        # Text box and enter button
        self.style.configure('TEntry', foreground = 'black') 
        self.entry1 = ttk.Entry(self.root, textvariable = self.input_text, justify = CENTER, font = ('courier', 15, 'bold'))    
        self.entry1.focus_force() 
        self.entry1.pack(side = TOP, ipadx = 30, ipady = 10) 
        self.enter = ttk.Button(self.root, text = 'Enter', command = lambda : self.callback_enter()) 
        self.enter.pack(side = TOP, pady = 10) 

        # Buttons for selecting the type of input
        self.button_template = ttk.Button(self.root, text="Template Name", command=lambda: self.change_state(1))
        self.button_title = ttk.Button(self.root, text="Title", command=lambda: self.change_state(2))
        self.button_header = ttk.Button(self.root, text="Header", command=lambda: self.change_state(3))
        self.button_value = ttk.Button(self.root, text="Value", command=lambda: self.change_state(4))
        self.button_template.pack(side=tk.LEFT, padx=5)
        self.button_title.pack(side=tk.LEFT, padx=5)
        self.button_header.pack(side=tk.LEFT, padx=5)
        self.button_value.pack(side=tk.LEFT, padx=5)

        #zoom and scroll
        self.zoom = 1
        self.min_zoom = 1
        self.max_zoom = 5
        self.x_offset = 0
        self.y_offset = 0

    def change_state(self, new_state):
        self.buttonState = new_state

    def callback_enter(self):
        self.get_value = True

    def set_get_value_flag(self, value):
        self.get_value = value

    def button_state(self):
        return self.buttonState

    @property
    def get_value_flag(self):
        return self.get_value

    def show_error_message():
        messagebox.showerror("Error", "The title already exists. Please enter a new title.")

    def shape_selection(self, event, x, y, flags, param): 
        # Storing the (x1,y1) coordinates when left mouse button is pressed  
        if event == cv2.EVENT_LBUTTONDOWN: 
            self.roi_coordinates = [(x, y)] 
    
        # Storing the (x2,y2) coordinates when the left mouse button is released and make a rectangle on the selected region
        elif event == cv2.EVENT_LBUTTONUP: 
            self.roi_coordinates.append((x, y)) 
    
            # Drawing a rectangle around the region of interest (roi)
            cv2.rectangle(image, self.roi_coordinates[0], self.roi_coordinates[1], (0,255,255), 2) 
            cv2.imshow("Image", image) 


    def crop_image(self):
        # Function to capture ROI based on the current state
        image_copy = self.image.copy()
        cv2.namedWindow("Image", cv2.WINDOW_GUI_EXPANDED) 
        # cv2.setMouseCallback("Image", self.shape_selection) 
        cv2.setMouseCallback("Image", self.scroll_zoom)

        while True: 
        # display the image and wait for a keypress 
            cv2.imshow("Image", self.new_image) 
            key = cv2.waitKey(1) & 0xFF

            if key==13: # If 'enter' is pressed, apply OCR
                if len(self.roi_coordinates) == 2:
                    self.image_roi = image_copy[self.roi_coordinates[0][1]:self.roi_coordinates[1][1], 
                                        self.roi_coordinates[0][0]:self.roi_coordinates[1][0]]
                    self.ocr_text = pytesseract.image_to_string(self.image_roi, lang='eng', config='--psm 4')
                    self.ocr_text = re.sub(r'\n', '', self.ocr_text)
                    print(self.ocr_text)
                    self.get_value = True
            
            if key==27: # ESC
                print(file_functions.base_dict)
                file_functions.save_template_json()
                break
            
            if key == ord("c"): # Clear the selection when 'c' is pressed 
                self.new_image = image_copy.copy() 

        cv2.destroyAllWindows()

    def scroll_zoom(self, event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEWHEEL:
            if flags > 0:
                self.zoom *= 1.1
                self.zoom = min(self.zoom, self.max_zoom)
            else:
                self.zoom /= 1.1
                self.zoom = max(self.zoom, self.min_zoom)
            img = self.image.copy()

            new_width = round(img.shape[1] / self.zoom)
            new_height = round(img.shape[0] / self.zoom)
            self.x_offset = round(x - (x / self.zoom))
            self.y_offset = round(y - (y / self.zoom))
            img = img[
                self.y_offset : self.y_offset + new_height,
                self.x_offset : self.x_offset + new_width,]
            self.new_image = cv2.resize(img, (self.image.shape[1], self.image.shape[0]))

        if event == cv2.EVENT_LBUTTONDOWN: 
            self.plot_roi_coordinates = [(x, y)]
            if self.zoom > 1:
                origin_x = round((x / self.zoom) + self.x_offset)
                origin_y = round((y / self.zoom) + self.y_offset)
                self.origin_roi_coordinates = [(origin_x, origin_y)]
            else:
                origin_x = x
                origin_y = y
            self.roi_coordinates = [(origin_x, origin_y)] 
    
        # Storing the (x2,y2) coordinates when the left mouse button is released and make a rectangle on the selected region
        elif event == cv2.EVENT_LBUTTONUP: 
            self.plot_roi_coordinates.append((x, y))
            if self.zoom > 1:
                origin_x = round((x / self.zoom) + self.x_offset)
                origin_y = round((y / self.zoom) + self.y_offset)
            else:
                origin_x = x
                origin_y = y
            self.roi_coordinates.append((origin_x, origin_y)) 
    
            # Drawing a rectangle around the region of interest (roi)
            # print(self.roi_coordinates)

            cv2.rectangle(self.new_image, self.plot_roi_coordinates[0], self.plot_roi_coordinates[1], (0,255,255), 2) 
            cv2.imshow("Image", self.new_image) 
                

def add_value_to_json():
    while True:
        #print(app.button_state())
        if(app.get_value_flag):
            if app.button_state() == 1:
                file_functions.base_dict['template_name'] = app.input_text.get()
                app.set_get_value_flag(False)
            elif app.button_state() == 2:
                file_functions.add_region()
                file_functions.add_title(app.input_text.get())
                app.set_get_value_flag(False)
            elif app.button_state() == 3:
                file_functions.add_key(app.ocr_text)
                app.set_get_value_flag(False)
            elif app.button_state() == 4:
                file_functions.add_value(app.roi_coordinates)
                app.set_get_value_flag(False)
            else:
                print("Error")
                app.set_get_value_flag(False)
    

if __name__ == "__main__":
    ROOT_PATH :str = Path(__file__).parents[2]
    PDF_LOCATION :str =  os.path.join(ROOT_PATH, "data\pdf")
    JPG_LOCATION :str =  os.path.join(ROOT_PATH, "data\jpg")

    file_name = 'GCA RE'
    input_img = cv2.imread(os.path.join(JPG_LOCATION, file_name+'.jpg')) 
    # input_img = cv2.resize(input_img, (675, 826))
    image = input_img 

    root = tk.Tk()
    app = ImageCropper(root, image)
    file_functions = FileFunctions()

    cv2_thread =threading.Thread(target=app.crop_image)
    cv2_thread.start()
    add_value_thread = threading.Thread(target=add_value_to_json)
    add_value_thread.start()

    root.mainloop()
    
    
    
    
