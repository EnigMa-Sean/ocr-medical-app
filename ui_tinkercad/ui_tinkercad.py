import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from pdf2image import convert_from_path

def initiate_ocr():
    folder_path = folder_path_entry.get()
    excel_name = excel_name_entry.get()

    # Check if the folder path and Excel name are provided
    if not folder_path or not excel_name:
        show_error("Please enter both folder path and Excel file name.")
    else:
        try:
            # Perform OCR process here
            # Add Yun OCR Code here
            #print(f"OCR initiated for Folder: {folder_path}, Excel File: {excel_name}")
            success_message = f"OCR is finished and saved at {excel_name}"  # Replace output_path with the actual path
            show_success(success_message)

        except Exception as e:
            show_error(f"Error during OCR process: {str(e)}")



def create_template_window():
    template_window = tk.Toplevel(window)
    template_window.title("Create Template")
    template_window.geometry("500x500")

    # Buttons in a grid layout
    loadtemplate_button = tk.Button(template_window, text="Load Template", command=lambda: label_function_example("Select Template"), width=15)
    loadtemplate_button.grid(row=0, column=2, padx=10, pady=10)

    header_button = tk.Button(template_window, text="Header", command=lambda: label_function_example("Header"), width=15)
    header_button.grid(row=1, column=1, padx=10, pady=10)

    value_button = tk.Button(template_window, text="Value", command=lambda: label_function_example("Value"), width=15)
    value_button.grid(row=1, column=2, padx=10, pady=10)

    save_button = tk.Button(template_window, text="Save to Template", command=lambda: label_function_example("Save"), width=15)
    save_button.grid(row=1, column=3, padx=10, pady=10)


def label_function_example(label_type):
     print(f"Label Function Called for {label_type}")

#Add Save to Template function here (Header, Value, Save) and change in line 30 33 36 

def show_success(message):
    error_label.config(text=message, fg="green")

def browse_folder_path():
    folder_path = filedialog.askopenfilename(filetypes=[("Folder", "")])
    folder_path_entry.delete(0, tk.END)
    folder_path_entry.insert(0, folder_path)
    update_folder_label(folder_path)

def browse_excel_path():
    excel_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx;*.xls")])
    excel_name_entry.delete(0, tk.END)
    excel_name_entry.insert(0, excel_path)

def select_file_type():
    return file_type_var.get()

def display_file(file_path):
    try:
        file_type = select_file_type()

        if file_type == "Image":
            # For image files
            image = Image.open(file_path)
        elif file_type == "PDF":
            # For PDF files
            pdf_images = convert_pdf_to_images(file_path)
            if pdf_images:
                image = pdf_images[0]
            else:
                raise Exception("Error converting PDF to images.")
        else:
            raise Exception("Unsupported file type.")

        # Display the image
        image = image.resize((500, 705), Image.BILINEAR)
        img = ImageTk.PhotoImage(image)
        display_canvas.config(width=500, height= 705)
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
    error_label.config(text=message, fg="green")

def show_error(message):
    error_label.config(text=message, fg="red")

def update_folder_label(folder_path):
    folder_label.config(text=f"Selected Folder: {folder_path}")

def label_function():
    # Add Jean label function here
    print("Label Function Called")

def display_selected_file():
    try:
        # Get the selected file path
        selected_file_path = folder_path_entry.get()

        # Check if a file path is provided
        if selected_file_path:
            # Display the selected file
            display_file(selected_file_path)
        else:
            show_error("No file path selected.")
    except Exception as e:
        show_error(f"Error displaying selected file: {str(e)}")

# Create the main window with higher DPI 
window = tk.Tk()
window.title("OCR Application")
window.geometry("800x300")  # Set the initial window size

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
title_font = ("Helvetica", 20, "bold")
button_font = ("Helvetica", 12)

#Right Frame configuration
datapreview_label = tk.Label(right_frame, text="Data Preview", font=button_font, bg=background_color, fg=text_color)
datapreview_label.pack(pady=10)

display_canvas = tk.Canvas(right_frame, width=500, height=705, bg=background_color)
display_canvas.pack(pady=10)

#Left Frame configuration
title_label = tk.Label(left_frame, text="OCR Application", font=title_font, bg=background_color, fg=text_color)
title_label.pack(pady=10)

folder_path_label = tk.Label(left_frame, text="1. Select Your file for OCR:", font=button_font, bg=background_color, fg=text_color)
folder_path_label.pack()

folder_path_entry = tk.Entry(left_frame, width=40, font=("Helvetica", 10))
folder_path_entry.pack(pady=5)

browse_button = tk.Button(left_frame, text="Browse", command=browse_folder_path, bg=accent_color, fg="white", font=button_font, width=20)
browse_button.pack(pady=5)

folder_label = tk.Label(left_frame, text="Selected File:", font=("Helvetica", 10), bg=background_color, fg=text_color)
folder_label.pack(pady=5)

excel_name_label = tk.Label(left_frame, text="2. Select Excel file for saving result:", font=button_font, bg=background_color, fg=text_color)
excel_name_label.pack()

excel_name_entry = tk.Entry(left_frame, width=40, font=("Helvetica", 10))
excel_name_entry.pack(pady=5)

browse_excel_button = tk.Button(left_frame, text="Browse", command=browse_excel_path, bg=accent_color, fg="white", font=button_font, width=20)
browse_excel_button.pack(pady=5)

file_type_label = tk.Label(left_frame, text="3. Select File Type (Image or PDF):", font=button_font, bg=background_color, fg=text_color)
file_type_label.pack()

file_type_var = tk.StringVar()
file_type_var.set("Image")

file_type_menu = tk.OptionMenu(left_frame, file_type_var, "Image", "PDF")
file_type_menu.config(bg=accent_color, fg="white", font=button_font)
file_type_menu.pack(pady=5)

# Create a button for the "Display Selected File" function
display_file_button = tk.Button(left_frame, text="Display Selected File", command=display_selected_file, bg=accent_color, fg="white", font=button_font, width=20)
display_file_button.pack(pady=10)
display_file_button.config(command=display_selected_file)

# Create a button for the "Create Template" function
create_template_button = tk.Button(left_frame, text="Template", command=create_template_window, bg=accent_color, fg="white", font=button_font, width=20)
create_template_button.pack(pady=5)

# Create a button for the label function
label_button = tk.Button(left_frame, text="Label", command=label_function, bg=accent_color, fg="white", font=button_font, width=20)
label_button.pack(pady=5)

# Create a button for the ocr function
ocr_button = tk.Button(left_frame, text="Initiate OCR", command=initiate_ocr, bg=accent_color, fg="white", font=button_font, width=20)
ocr_button.pack(pady=5)

# Bind the select_file_type function to the Configure event of file_type_menu
file_type_menu.bind("<Configure>", lambda event: select_file_type())

# Create an error label for displaying error messages
error_label = tk.Label(left_frame, text="", font=("Helvetica", 10), bg=background_color, fg="red")
error_label.pack(pady=5)


# Start the Tkinter event loop
window.mainloop()
