import os
import cv2
from pdf2image import convert_from_path
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'Tesseract/tesseract.exe'       

# Defining the event listener (callback function)
def shape_selection(event, x, y, flags, param): 
    # making coordinates global
    global coordinates 
  
    # Storing the (x1,y1) coordinates when left mouse button is pressed  
    if event == cv2.EVENT_LBUTTONDOWN: 
        coordinates = [(x, y)] 
  
    # Storing the (x2,y2) coordinates when the left mouse button is released and make a rectangle on the selected region
    elif event == cv2.EVENT_LBUTTONUP: 
        coordinates.append((x, y)) 
  
        # Drawing a rectangle around the region of interest (roi)
        cv2.rectangle(image, coordinates[0], coordinates[1], (0,255,255), 2) 
        cv2.imshow("image", image) 

def pdf2image(pdf_path, jpeg_path, file_name):
    pages = convert_from_path(os.path.join(pdf_path, file_name + '.pdf'))
    for i, page in enumerate(pages):
        page.save(os.path.join(jpeg_path, file_name + '.jpg'), 'JPEG')
    

# load the image, clone it, and setup the mouse callback function 
if __name__ == '__main__':

    from pathlib import Path

    ROOT_PATH :str = Path(__file__).parents[2]
    PDF_LOCATION :str =  os.path.join(ROOT_PATH, "data\pdf")
    JPG_LOCATION :str =  os.path.join(ROOT_PATH, "data\jpg")

    file_name = 'GCA RE'

    pdf2image(PDF_LOCATION, JPG_LOCATION, 'GCA RE')
    print(JPG_LOCATION)
    input_img = cv2.imread(os.path.join(JPG_LOCATION, file_name+'.jpg')) # image read
    # input_img = cv2.resize(input_img,(1500,800)) # resizing image
    #img_gray =  cv2.cvtColor(input_img, cv2.COLOR_BGR2GRAY) # convert image to grayscale if needed

    list_coordinates = []
    list_text = []
    coordinates = []
    image = input_img #img_gray
    image_copy = image.copy()
    cv2.namedWindow("image") 
    cv2.setMouseCallback("image", shape_selection) 
  
    # keep looping until the 'q' key is pressed 
    while True: 
        # display the image and wait for a keypress 
        cv2.imshow("image", image) 
        key = cv2.waitKey(1) & 0xFF
    
        if key==13: # If 'enter' is pressed, apply OCR
            if len(coordinates) == 2:
                image_roi = image_copy[coordinates[0][1]:coordinates[1][1], 
                                        coordinates[0][0]:coordinates[1][0]]
                text = pytesseract.image_to_string(image_roi, lang='eng', config='--psm 4')
                list_coordinates.append(coordinates)
                list_text.append(text)

        if key==27:
            break
        
        if key == ord("c"): # Clear the selection when 'c' is pressed 
            image = image_copy.copy() 
    
    # closing all open windows 
    # cv2.destroyAllWindows()  
    print(list_coordinates)
    print(list_text)