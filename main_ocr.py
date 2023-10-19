import cv2 
import itertools
import numpy as np 
import pandas as pd
from pdf2image import convert_from_path
import pytesseract
import re
import os
import matplotlib.pyplot as plt

pytesseract.pytesseract.tesseract_cmd = r'Tesseract/tesseract.exe'       

def pdf_to_img(pdf_path):
    jpg_img = convert_from_path(pdf_path)
    pdf = os.path.splitext(pdf_path)[0]
    for i in range(len(jpg_img)):
        jpg_img[i].save(pdf+'.jpg', 'JPEG')

def detect_tables(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5,5), 0)
    edged = cv2.Canny(blurred, 30, 150)
    contours, hierarchy = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rects = []
    rects_coord = []
    for contour in contours: 
        # Approximate the contour to a polygon 
        polygon = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
        if len(polygon) == 4 and abs(1 - cv2.contourArea(polygon) / (cv2.boundingRect(polygon)[2] * cv2.boundingRect(polygon)[3])) < 0.1: 
            rects.append(polygon)
            x, y, w, h = cv2.boundingRect(polygon)
            rects_coord.append([x, y, w, h])
    rects_coord = sorted(rects_coord, key=lambda x: x[1])
    return rects, rects_coord

def enhance_table_lines(table):
    thresh,table_bin = cv2.threshold(table,128,255,cv2.THRESH_BINARY)
    table_bin = 255-table_bin
    # plotting = plt.imshow(table_bin,cmap='gray')
    # plt.title("Inverted Image with global thresh holding")
    # plt.show()

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, np.array(table).shape[1]//150))
    eroded_image = cv2.erode(table_bin, vertical_kernel, iterations=5)
    vertical_lines = cv2.dilate(eroded_image, vertical_kernel, iterations=5)

    # plt.imshow(vertical_lines, cmap='gray')
    # plt.show()

    hor_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (np.array(table).shape[1]//150, 1))
    table_2 = cv2.erode(table_bin, hor_kernel, iterations=5)
    horizontal_lines = cv2.dilate(table_2, hor_kernel, iterations=5)

    # plt.imshow(horizontal_lines, cmap='gray')
    # plt.show()

    vertical_horizontal_lines = cv2.addWeighted(vertical_lines, 0.5, horizontal_lines, 0.5, 0.0)
    vertical_horizontal_lines = cv2.erode(~vertical_horizontal_lines, kernel, iterations=3)

    thresh, vertical_horizontal_lines = cv2.threshold(vertical_horizontal_lines,128,255, cv2.THRESH_BINARY)
    b_table = cv2.bitwise_not(cv2.bitwise_xor(table,vertical_horizontal_lines))
    # plotting = plt.imshow(b_table,cmap='gray')
    # plt.show()

    return vertical_horizontal_lines

def detect_blocks(table):
    vertical_horizontal_lines = cv2.cvtColor(table, cv2.COLOR_BGR2GRAY)
    table_blurred = cv2.GaussianBlur(vertical_horizontal_lines, (3, 3), 0) 
    table_edges = cv2.Canny(table_blurred, 50, 150) 

    table_contours, table_hierarchy = cv2.findContours(table_edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    table_cordinates = []
    table_rects = []
    table_rects_coord = []

    for table_contour in table_contours: 
        # Approximate the contour to a polygon 
        table_polygon = cv2.approxPolyDP(table_contour, 0.01 * cv2.arcLength(table_contour, True), True)
        if len(table_polygon) == 4 and abs(1 - cv2.contourArea(table_polygon) / (cv2.boundingRect(table_polygon)[2] * cv2.boundingRect(table_polygon)[3])) < 0.1: 
            table_rects.append(table_polygon)
            table_x, table_y, table_w, table_h = cv2.boundingRect(table_polygon)
            table_rects_coord.append([table_x, table_y, table_w, table_h])
        else:
            print('Cannot find blocks within the table')
    
    return table_rects, table_rects_coord

def img_to_text(table, table_rects_coord):
    result_text = []
    for num_table in range(len(table_rects_coord)):
        block = table[table_rects_coord[num_table][1]:table_rects_coord[num_table][1]+table_rects_coord[num_table][3],
                        table_rects_coord[num_table][0]:table_rects_coord[num_table][0]+table_rects_coord[num_table][2]]
        cv2.imshow("output", block)
        cv2.waitKey(0)
        text = pytesseract.image_to_string(block, lang='eng', config='--psm 4')
        text = re.sub(r'\n', ' ', text)
        result_text.append(text)
    result_text = [result_text[i] for i in range(len(result_text)) if (i==0) or result_text[i] != result_text[i-1]]
    result_text = list(reversed(result_text))
    return result_text

def export_to_csv(result_text, result_dict):
    if len(result_text) == 18:
        region = 'Patient Demographics'
        result_dict[region] = None
        patient_demo_keys = list(itertools.islice(result_text, 0, len(result_text), 2))
        patient_demo_values = list(itertools.islice(result_text, 1, len(result_text), 2))
        patient_demo_dict = dict(zip(patient_demo_keys, patient_demo_values))
        result_dict.update(patient_demo_dict)
    elif len(result_text) == 4:
        result_dict.update({'': None})
        region = 'Medical History'
        result_dict[region] = None
        medical_history_keys = list(itertools.islice(result_text, 0, len(result_text), 2))
        medical_history_values = list(itertools.islice(result_text, 1, len(result_text), 2))
        medical_history_dict = dict(zip(medical_history_keys, medical_history_values))
        result_dict.update(medical_history_dict)
    elif len(result_text) == 10:
        history_keys = list(itertools.islice(result_text, 0, len(result_text), 2))
        history_values = list(itertools.islice(result_text, 1, len(result_text), 2))
        history_dict = dict(zip(history_keys, history_values))
        result_dict.update(history_dict)
    elif len(result_text) == 1:
        result_dict.update({None: None})
        region = 'Clinical Summary'
        result_dict[region] = None
        result_dict['Details'] = result_text[0]
    else:
        print('Cannot find matched template')

    result_df = pd.DataFrame.from_dict(result_dict, orient='index')
    result_df.to_csv('ocr_result.csv', header=False)

if __name__ == '__main__':
    pdf_path = 'pdf_files/document_template.pdf'
    pdf_to_img(pdf_path)

    # img_path = 'images/noise_img.jpg'
    # img = cv2.imread(img_path)
    # rects, rects_coord = detect_tables(img)

    # result_dict = {}
    # for i_table in range(len(rects)):
    #     table = img[rects_coord[i_table][1]:rects_coord[i_table][1]+rects_coord[i_table][3], rects_coord[i_table][0]:rects_coord[i_table][0]+rects_coord[i_table][2]]
    #     cv2.imshow("output", table)
    #     cv2.waitKey(0)
    #     vertical_horizontal_lines = enhance_table_lines(table)
    #     table_rects, table_rects_coord = detect_blocks(vertical_horizontal_lines)
    #     result_text = img_to_text(table, table_rects_coord)
    #     export_to_csv(result_text, result_dict)
            
    #     print(result_text)