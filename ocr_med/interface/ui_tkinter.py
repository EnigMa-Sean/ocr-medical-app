import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from pdf2image import convert_from_path
import threading
import numpy as np
import cv2

from ocr_med.roi_label import crop_with_tkinter as cwt
from ocr_med.json_functions.file_functions import FileFunctions
from ocr_med.ocr import run_ocr

def initiate_ocr():
    image, folder_path, output_path, template_path, file_type_var, page_number = call_all_value_and_change_to_image()

    # Check if the folder path and Excel name are provided
    if not folder_path or not output_path:
        show_error("Please enter both folder path and Excel file name.")
    else:
        try:
            # Add Yun OCR Code here
            #print(f"OCR initiated for Folder: {folder_path}, Excel File: {excel_name}")
            success_message = f"OCR is finished and saved at {output_path}"  # Replace output_path with the actual path
            show_success(success_message)

        except Exception as e:
            show_error(f"Error during OCR process: {str(e)}")
    print(run_ocr(folder_path, template_path))

def label_function():
    folder_path = folder_path_entry.get()   #return type of file_path is string
    output_path = excel_name_entry.get()    #return type of output_path is string
    file_type_var = select_file_type()      #return type of file_type_var is string ("Image" or "PDF")
    # For multiple pages pdf
    page_number = page_number_entry.get()

    if file_type_var == "Image":
        # For image files
        image = cv2.imread(folder_path)
    elif file_type_var == "PDF":
        # For PDF files
        pdf_images = convert_pdf_to_images(folder_path)
        page_index = int(page_number) - 1  # Convert to zero-based index
        if 0 <= page_index < len(pdf_images):
            image = np.array(pdf_images[page_index])
    
    image = cv2.imread(folder_path)
    cropper = cwt.ImageCropper(image)

    # Add Jean label(or what ever u like to call) function here, and if want to change button name find this line
    cv2_thread =threading.Thread(target=cropper.crop_image)
    cv2_thread.start()
    main_thread = threading.Thread(target=cropper.main)
    main_thread.start()

    cropper.tkInter.mainloop()
    # label_button = tk.Button(left_frame, text="Start Label", command=label_function, bg=accent_color, fg="white", font=button_font, width=20)
    # and change text="Start Label" to text="What ever u like to call"

#This is the function for browse button in create template window 
def browse_template_path(template_entry):
    template_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    template_entry.delete(0, tk.END)
    template_entry.insert(0, template_path)
    return template_path

def browse_folder_path():
    folder_path = filedialog.askopenfilename(filetypes=[("Folder", "")])
    folder_path_entry.delete(0, tk.END)
    folder_path_entry.insert(0, folder_path)
    update_folder_label(folder_path)

def browse_excel_path():
    output_path = filedialog.askdirectory()
    excel_name_entry.delete(0, tk.END)
    excel_name_entry.insert(0, output_path)
    update_excel_label(output_path)
    #return output_path

def select_file_type():
    return file_type_var.get()

def display_file(file_path, page_number):
    try:
        file_type = select_file_type()

        if file_type == "Image":
            # For image files
            image = Image.open(file_path)
        elif file_type == "PDF":
            # For PDF files
            pdf_images = convert_pdf_to_images(file_path)
            if pdf_images:
                page_index = int(page_number) - 1  # Convert to zero-based index
                if 0 <= page_index < len(pdf_images):
                    image = pdf_images[page_index]
                else:
                    raise Exception("Invalid page number.")
            else:
                raise Exception("Error converting PDF to images.")
        else:
            raise Exception("Unsupported file type.")

        # Check the current orientation (landscape or portrait)
        orientation = current_orientation

        width = 420
        height = int(display_canvas_width * 1.414)  # A4 ratio

        # Display the image with the current orientation
        if orientation == "landscape":
            image = image.resize((height, width), Image.BILINEAR)
        elif orientation == "portrait":
            image = image.resize((width, height), Image.BILINEAR)

        img = ImageTk.PhotoImage(image)
        display_canvas.config(width=image.width, height=image.height)
        display_canvas.create_image(0, 0, anchor=tk.NW, image=img)
        display_canvas.image = img
        error_label.config(text="")
        show_success("File displayed successfully.")
    except Exception as e:
        show_error(f"Error displaying file: {str(e)}")

def convert_pdf_to_images(pdf_path):
    try:
        pdf_images = convert_from_path(pdf_path)
        return pdf_images
    except Exception as e:
        show_error(f"Error converting PDF to images: {str(e)}")
        return None

def show_success(message):
    error_label.config(text=message, fg="green", font=("Helvetica", 9))

def show_error(message):
    error_label.config(text=message, fg="red", font=("Helvetica", 9))

def update_folder_label(folder_path):
    last_two_dirs = "/".join(folder_path.split("/")[-2:])
    folder_label.config(text=f"Selected: {last_two_dirs}")
    
def update_excel_label(output_path):
    last_two_dirs = "/".join(output_path.split("/")[-2:])
    excel_label.config(text=f"Selected: {last_two_dirs}")

def display_selected_file():
    try:
        # Get the selected file path and page number
        selected_file_path, page_number = get_selected_file_info()

        # Check if a file path is provided
        if selected_file_path:
            # Display the selected file with the specified page number
            display_file(selected_file_path, page_number)
        else:
            show_error("No file path selected.")
    except Exception as e:
        show_error(f"Error displaying selected file: {str(e)}")

def get_selected_file_info():
    selected_file_path = folder_path_entry.get()
    page_number = page_number_entry.get()
    return selected_file_path, page_number

current_orientation = "portrait"

def toggle_orientation():
    global current_orientation
    # Toggle between portrait and landscape
    current_orientation = "landscape" if current_orientation == "portrait" else "portrait"
    # Update the display_file function to consider the current orientation when displaying the file
    display_file(folder_path_entry.get(), int(page_number_entry.get()))

def call_all_value_and_change_to_image():
    folder_path = folder_path_entry.get()   #return type of file_path is string
    output_path = excel_name_entry.get()    #return type of output_path is string
    file_type_var = select_file_type()      #return type of file_type_var is string ("Image" or "PDF")
    template_path = template_path_entry.get() #return type of template_path is string
    # For multiple pages pdf
    page_number = page_number_entry.get()

    if file_type_var == "Image":
        # For image files
        image = cv2.imread(folder_path)
    elif file_type_var == "PDF":
        # For PDF files
        pdf_images = convert_pdf_to_images(folder_path)
        page_index = int(page_number) - 1  # Convert to zero-based index
        if 0 <= page_index < len(pdf_images):
            image = np.array(pdf_images[page_index])
    return image, folder_path, output_path, template_path, file_type_var, page_number


# Create the main window with higher DPI
window = tk.Tk()
window.title("OCR Application")
window.geometry("690x540")  # Set the initial window size

# Set DPI (dots per inch) to improve appearance
window.tk.call('tk', 'scaling', 2.0)

# Define modern color scheme
background_color = "#F5F5F5"
accent_color = "#3498db"
text_color = "#2c3e50"

# Configure window background color
window.configure(bg=background_color)

# Create and pack a main frame
main_frame = ttk.Frame(window, padding="20")
main_frame.pack(fill=tk.BOTH, expand=True)

# Create and pack left frame for input elements
left_frame = ttk.Frame(main_frame, padding="10", style="left.TFrame")
left_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)

left_frame.grid_propagate(True)  # Prevent the frame from resizing

# Apply a separator between frames
ttk.Separator(main_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y)

# Create and pack right frame for image display
right_frame = ttk.Frame(main_frame, padding="10", style="right.TFrame")
right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Apply a modern style to the left frame
style = ttk.Style()
style.configure("left.TFrame", background=background_color)

# Create and pack widgets with modern styling for the left frame
title_font = ("Helvetica", 12, "bold")
button_font = ("Helvetica", 8)
label_font = ("Helvetica", 8)

# Right Frame Configuration
datapreview_label = tk.Label(right_frame, text="Data Preview", font=button_font, bg=background_color, fg=text_color)
datapreview_label.pack(pady=10)

display_canvas_width = 420
display_canvas_height = display_canvas_width * 1.414  # A4 ratio

display_canvas = tk.Canvas(right_frame, width=display_canvas_width, height=display_canvas_height, bg=background_color)
display_canvas.pack(pady=10)

orientation_button = tk.Button(right_frame, text="Toggle Orientation", command=toggle_orientation, bg=accent_color, fg="white", font=button_font, width=20)
orientation_button.pack(pady=5)

# Left Frame Configuration
title_label = tk.Label(left_frame, text="OCR Application", font=label_font, bg=background_color, fg=text_color)
title_label.pack(pady=10)

folder_path_label = tk.Label(left_frame, text="1. Select Your file for OCR:", font=label_font, bg=background_color, fg=text_color)
folder_path_label.pack()

folder_path_entry = tk.Entry(left_frame, width=40, font=("Helvetica", 8))
folder_path_entry.pack(pady=5)

browse_button = tk.Button(left_frame, text="Browse", command=browse_folder_path, bg=accent_color, fg="white", font=button_font, width=20)
browse_button.pack(pady=5)

folder_label = tk.Label(left_frame, text="Selected File:", font=label_font, bg=background_color, fg=text_color)
folder_label.pack(pady=5)

file_type_label = tk.Label(left_frame, text="2. Select File Type (Image or PDF), For PDF input selected pages below(default is page 1):", font=button_font, bg=background_color, fg=text_color)
file_type_label.pack()

file_type_var = tk.StringVar()
file_type_var.set("Image")

file_type_menu = tk.OptionMenu(left_frame, file_type_var, "Image", "PDF")
file_type_menu.config(bg=accent_color, fg="white", font=button_font)
file_type_menu.pack(pady=5)

page_number_entry = tk.Entry(left_frame, width=5, font=("Helvetica", 8), justify=tk.CENTER)
page_number_entry.pack(pady=5)
page_number_entry.insert(0, "1")  # Set default value to 1

excel_name_label = tk.Label(left_frame, text="3. Select Folder for saving result:", font=label_font, bg=background_color, fg=text_color)
excel_name_label.pack()

excel_name_entry = tk.Entry(left_frame, width=40, font=("Helvetica", 8))
excel_name_entry.pack(pady=5)

excel_label = tk.Label(left_frame, text="Selected Folder:", font=label_font, bg=background_color, fg=text_color)
excel_label.pack(pady=5)

browse_excel_button = tk.Button(left_frame, text="Browse", command=browse_excel_path, bg=accent_color, fg="white", font=button_font, width=20)
browse_excel_button.pack(pady=5)

template_label = tk.Label(left_frame, text="4. Select Template or Create New template", font=label_font, bg=background_color, fg=text_color)
template_label.pack(pady=5)

template_path_entry = tk.Entry(left_frame, width=40, font=("Helvetica", 8))
template_path_entry.pack(pady=5)

browse_template_button = tk.Button(left_frame, text="Browse Existed Template", command=lambda: browse_template_path(template_path_entry), bg=accent_color, fg="white", font=button_font, width=20)
browse_template_button.pack(pady=5)

header_button = tk.Button(left_frame, text="Create New Template", command=lambda: label_function(), bg=accent_color, fg="white", font=button_font, width=20)
header_button.pack(pady=5)

# Menu button
menu_label = tk.Label(left_frame, text="Menu", font=button_font, bg=background_color, fg=text_color)
menu_label.pack()

# Create a button for the "Display Selected File" function
display_file_button = tk.Button(left_frame, text="Preview Selected File", command=display_selected_file, bg=accent_color, fg="white", font=button_font, width=20)
display_file_button.pack(pady=5)
display_file_button.config(command=display_selected_file)

# Create a button for the OCR function
ocr_button = tk.Button(left_frame, text="Initiate OCR", command=initiate_ocr, bg=accent_color, fg="white", font=button_font, width=20)
ocr_button.pack(pady=5)

# Bind the select_file_type function to the Configure event of file_type_menu
file_type_menu.bind("<Configure>", lambda event: select_file_type())

# Create an error label for displaying error messages
error_label = tk.Label(left_frame, text="", font=label_font, bg=background_color, fg="red")
error_label.pack(pady=5)

# Start the Tkinter event loop
window.mainloop()
