import os
import cv2
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract
from ocr_med.json_functions.file_functions import FileFunctions

ROOT_PATH :str = Path(__file__).parents[2]
pytesseract.pytesseract.tesseract_cmd = r'Tesseract/tesseract.exe'       

class CropROT:
    def __init__(self):
        self.file_functions = FileFunctions()
        self.pdf_path = os.path.join(ROOT_PATH, "data\pdf")
        self.jpeg_path = os.path.join(ROOT_PATH, "data\jpg")

        self.list_coordinates = []
        self.list_text = []
        self.coordinates = []
        self.image = None
        self.image_copy = None

    # Defining the event listener (callback function)
    def shape_selection(self, event, x, y, flags, param): 
        # Storing the (x1,y1) coordinates when left mouse button is pressed  
        if event == cv2.EVENT_LBUTTONDOWN: 
            self.coordinates = [(x, y)] 
    
        # Storing the (x2,y2) coordinates when the left mouse button is released and make a rectangle on the selected region
        elif event == cv2.EVENT_LBUTTONUP: 
            self.coordinates.append((x, y)) 
    
            # Drawing a rectangle around the region of interest (roi)
            cv2.rectangle(self.image, self.coordinates[0], self.coordinates[1], (0,255,255), 2) 
            cv2.imshow("image", self.image) 

    def pdf2image(self, file_name):
        pages = convert_from_path(os.path.join(self.pdf_path, file_name + '.pdf'))
        for i, page in enumerate(pages):
            page.save(os.path.join(self.jpeg_path, file_name + '.jpg'), 'JPEG')


    def start_crop(self):
        cv2.namedWindow("image") 
        cv2.setMouseCallback("image", self.shape_selection)

        while True:
            cv2.imshow("image", self.image)
            key = cv2.waitKey(1) & 0xFF

            if key==13: # If 'enter' is pressed, apply OCR
                if len(self.coordinates) == 2:
                    image_roi = self.image_copy[self.coordinates[0][1]:self.coordinates[1][1], 
                                            self.coordinates[0][0]:self.coordinates[1][0]]
                    text = pytesseract.image_to_string(image_roi, lang='eng', config='--psm 4')
                    self.list_coordinates.append(self.coordinates)
                    self.list_text.append(text)
            if key==27:
                break
            if key == ord("c"):
                self.image = self.image_copy.copy()
        
    
# load the image, clone it, and setup the mouse callback function 
if __name__ == '__main__':

    crop_roi = CropROT()
    file_name = 'GCA RE'

    crop_roi.pdf2image(file_name=file_name)
    input_img = cv2.imread(os.path.join(crop_roi.jpeg_path, file_name+'.jpg')) # image read
    # input_img = cv2.resize(input_img,(1500,800)) # resizing image
    #img_gray =  cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY) # convert image to grayscale if needed

    crop_roi.image = input_img #img_gray
    crop_roi.image_copy = crop_roi.image.copy()
    crop_roi.start_crop()
    print(crop_roi.list_coordinates)
    print(crop_roi.list_text)