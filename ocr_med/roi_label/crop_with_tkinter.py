from tkinter import * 
import tkinter as tk
from tkinter import ttk, messagebox
#from tkinter.messagebox import askyesno 

import cv2
from PIL import Image, ImageTk
import os
import pytesseract
from pathlib import Path
import sys
import threading
from ocr_med.json_functions.file_functions import FileFunctions
import re

#pytesseract.pytesseract.tesseract_cmd = r'Tesseract/tesseract.exe'

class ImageCropper:
    def __init__(self, image):
        self.image = image
        self.new_image = image

        self.tkInter = tk.Tk()
        self.tkInter.title("Label interface")
        self.tkInter.geometry("350x150") 
        self.style = ttk.Style()
        
        self.input_text = StringVar() 
        self.ocr_text = StringVar()

        self.plot_roi_coordinates: StringVar = []
        self.roi_coordinates: StringVar = []
        self.ocr_value: StringVar = []
        self.image_roi: StringVar = []

        self.get_value = False
        self.exitFlag = False
        self.buttonState = None
        
        # Text box and enter button
        self.style.configure('TEntry', foreground='black') 
        self.user_input = ttk.Entry(self.tkInter, textvariable=self.input_text, justify=CENTER, font=("Helvetica", 10, 'bold'))    
        self.user_input.focus_force() 
        self.user_input.grid(row=0, column=0, columnspan=3, pady=10) 

        self.enter = ttk.Button(self.tkInter, text='Enter', command=lambda: self.callback_enter()) 
        self.enter.grid(row=0, column=3, pady=10)

        # Buttons for selecting the type of input
        self.button_template = ttk.Button(self.tkInter, text="Template Name", command=lambda: self.change_state(1))
        self.button_title = ttk.Button(self.tkInter, text="Title", command=lambda: self.change_state(2))
        self.button_key = ttk.Button(self.tkInter, text="Key", command=lambda: self.change_state(3))
        self.button_value = ttk.Button(self.tkInter, text="Value", command=lambda: self.change_state(4))
        self.button_template.grid(row=1, column=0)
        self.button_title.grid(row=1, column=1, padx=5, pady=10)
        self.button_key.grid(row=1, column=2, padx=5, pady=10)
        self.button_value.grid(row=1, column=3, padx=5, pady=10)

        # Label for status text at the bottom
        self.status_label = tk.Label(self.tkInter, text="", font=("Helvetica", 10), anchor=CENTER, padx=5, pady=10)
        self.status_label.grid(row=2, column=0, columnspan=4, pady=10)

        #zoom and scroll
        self.zoom = 1
        self.min_zoom = 1
        self.max_zoom = 5
        self.x_offset = 0
        self.y_offset = 0
        
        self.file_functions = FileFunctions()

 
    def show_success(self, message):
        self.status_label.config(text=message, fg="green")

    def show_error(self, message):
        self.status_label.config(text=message, fg="red")

    def show_error_message():
        messagebox.showerror("Error", "The title already exists. Please enter a new title.")

    def change_state(self, new_state):
        self.buttonState = new_state
        if new_state == 1:
            self.show_success("Template Name Mode")
        elif new_state == 2:
            self.show_success("Title Mode")
        elif new_state == 3:
            self.show_success("Header Mode")
        elif new_state == 4:
            self.show_success("Value Mode")
        else:
            self.show_success("Press Botton for Label")

    def callback_enter(self):
        self.get_value = True

    @property
    def get_button_state(self):
        return self.buttonState

    @property
    def get_exit_flag(self):
        return self.exitFlag
    
    @property
    def get_value_flag(self):
        return self.get_value
    
    @property
    def get_input_text(self):
        return self.input_text
    
    @property
    def get_ocr_text(self):
        return self.get_ocr_text
    
    @property
    def get_roi_coordinate(self):
        return self.get_roi_coordinate
    
    def set_get_value_flag(self, value):
        self.get_value = value

    def shape_selection(self, event, x, y, flags, param): 
        # Storing the (x1,y1) coordinates when left mouse button is pressed  
        if event == cv2.EVENT_LBUTTONDOWN: 
            self.roi_coordinates = [(x, y)] 
    
        # Storing the (x2,y2) coordinates when the left mouse button is released and make a rectangle on the selected region
        elif event == cv2.EVENT_LBUTTONUP: 
            self.roi_coordinates.append((x, y)) 
    
            # Drawing a rectangle around the region of interest (roi)
            cv2.rectangle(image, self.roi_coordinates[0], self.roi_coordinates[1], (0,255,255), 2) 
            cv2.imshow("Imported Image", image) 

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
            cv2.imshow("Imported Image", self.new_image) 
                
    def crop_image(self):
        # Function to capture ROI based on the current state
        image_copy = self.image.copy()
        cv2.namedWindow("Imported Image", cv2.WINDOW_GUI_EXPANDED) 
        cv2.setMouseCallback("Imported Image", self.scroll_zoom) 
        
        while True: 
        # Display the image and wait for a keypress 
            cv2.imshow("Imported Image", self.new_image) 
            key = cv2.waitKey(1) & 0xFF

    def main(self):
        while True:
            try:
                if self.get_value_flag:
                    if self.get_button_state == 1:
                        if self.get_input_text.get():
                            self.file_function.base_dict['template_name'] = self.get_input_text.get()
                            self.show_success("Add template name by typing")
                        else: 
                            self.show_error("Please identify template name by typing")
                    elif self.get_button_state == 2:
                        self.file_function.add_region()
                        if self.get_input_text.get():
                            self.file_function.add_title(self.get_input_text.get())
                            self.show_success("Successfully add title by typing")
                        else:
                            self.file_function.add_title(self.get_ocr_text)
                            self.show_success("Successfully add title by OCR croping")
                    elif self.get_button_state == 3:
                        if self.file_function.base_dict[self.file_function.latest_region]['title'] == None:
                            self.show_error("Please add a title before adding a header")
                        else:
                            if self.get_input_text.get():
                                self.file_function.add_key(self.get_input_text.get())
                                self.show_success("Successfully add key by typing")
                            else:
                                self.file_function.add_key(self.get_ocr_text)
                                self.show_success("Successfully add key by OCR croping")
                    elif self.get_button_state == 4:
                        if self.get_input_text.get():
                            self.show_error("Please crop from the image to get the value")
                        else:
                            self.file_function.add_value(self.get_roi_coordinate)
                            self.show_success("Successfully add ROI coordinates as value")
                    self.set_get_value_flag(False)
                if self.get_exit_flag:
                    sys.exit(0)
            except Exception as e:
                self.show_error(f"An error occurred: {e}, Please try again.")

       
def main():
    while True:
        try:
            if label_functions.get_value_flag:
                if label_functions.get_button_state == 1:
                    if label_functions.get_input_text.get():
                        file_functions.base_dict['template_name'] = label_functions.get_input_text.get()
                        label_functions.show_success("Add template name by typing")
                    else: 
                        label_functions.show_error("Please identify template name by typing")
                elif label_functions.get_button_state == 2:
                    file_functions.add_region()
                    if label_functions.get_input_text.get():
                        file_functions.add_title(label_functions.get_input_text.get())
                        label_functions.show_success("Successfully add title by typing")
                    else:
                        file_functions.add_title(label_functions.get_ocr_text)
                        label_functions.show_success("Successfully add title by OCR croping")
                elif label_functions.get_button_state == 3:
                    if file_functions.base_dict[file_functions.latest_region]['title'] == None:
                        label_functions.show_error("Please add a title before adding a header")
                    else:
                        if label_functions.get_input_text.get():
                            file_functions.add_key(label_functions.get_input_text.get())
                            label_functions.show_success("Successfully add key by typing")
                        else:
                            file_functions.add_key(label_functions.get_ocr_text)
                            label_functions.show_success("Successfully add key by OCR croping")
                elif label_functions.get_button_state == 4:
                    if label_functions.get_input_text.get():
                        label_functions.show_error("Please crop from the image to get the value")
                    else:
                        file_functions.add_value(label_functions.get_roi_coordinate)
                        label_functions.show_success("Successfully add ROI coordinates as value")
                label_functions.set_get_value_flag(False)
            if label_functions.get_exit_flag:
                sys.exit(0)
        except Exception as e:
            label_functions.show_error(f"An error occurred: {e}, Please try again.")

        

if __name__ == "__main__":
    ROOT_PATH :str = Path(__file__).parents[2]
    PDF_LOCATION :str =  os.path.join(ROOT_PATH, "data\pdf")
    JPG_LOCATION :str =  os.path.join(ROOT_PATH, "data\jpg")

    file_name = 'GCA RE'
    input_img = cv2.imread(os.path.join(JPG_LOCATION, file_name+'.jpg')) 
    # input_img = cv2.resize(input_img, (675, 826))
    image = input_img 

    label_functions = ImageCropper(image)
    file_functions = FileFunctions()

    cv2_thread =threading.Thread(target=label_functions.crop_image)
    cv2_thread.start()
    main_thread = threading.Thread(target=main)
    main_thread.start()

    label_functions.tkInter.mainloop()
    
    
    
    
