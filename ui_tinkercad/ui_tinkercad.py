import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk

def initiate_ocr():
    folder_path = folder_path_entry.get()
    excel_name = excel_name_entry.get()

    # Check if the folder path and Excel name are provided
    if not folder_path or not excel_name:
        show_error("Please enter both folder path and Excel file name.")
    else:
        try:
            # Perform OCR process here
            # You can replace this with your actual OCR code
            print(f"OCR initiated for Folder: {folder_path}, Excel File: {excel_name}")

            # Simulate OCR completion message
            success_message = f"OCR is finished and saved at {excel_name}"  # Replace output_path with the actual path
            show_success(success_message)

        except Exception as e:
            show_error(f"Error during OCR process: {str(e)}")

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
    file_type = file_type_var.get()
    if file_type == "Image":
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
    elif file_type == "PDF":
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    else:
        file_path = ""

    if file_path:
        display_file(file_path)

def display_file(file_path):
    try:
        print(f"Attempting to display image from path: {file_path}")
        image = Image.open(file_path)
        image = image.resize((300, 300), Image.BILINEAR)
        img = ImageTk.PhotoImage(image)
        display_canvas.config(width=300, height=300)
        display_canvas.create_image(0, 0, anchor=tk.NW, image=img)
        display_canvas.image = img
        error_label.config(text="")
        print("Image displayed successfully.")
    except Exception as e:
        show_error(f"Error displaying file: {str(e)}")
        print("Error displaying image:", str(e))

def show_error(message):
    error_label.config(text=message, fg="red")

def update_folder_label(folder_path):
    folder_label.config(text=f"Selected Folder: {folder_path}")

def label_function():
    # Add your label function logic here
    print("Label Function Called")

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
left_frame.pack(side=tk.LEFT, fill=tk.Y)

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

title_label = tk.Label(left_frame, text="OCR Application", font=title_font, bg=background_color, fg=text_color)
title_label.pack(pady=10)

folder_path_label = tk.Label(left_frame, text="Folder Path:", font=button_font, bg=background_color, fg=text_color)
folder_path_label.pack()

folder_path_entry = tk.Entry(left_frame, width=40, font=("Helvetica", 10))
folder_path_entry.pack(pady=5)

browse_button = tk.Button(left_frame, text="Browse", command=browse_folder_path, bg=accent_color, fg="white", font=button_font)
browse_button.pack(pady=5)

folder_label = tk.Label(left_frame, text="Selected Folder:", font=("Helvetica", 10), bg=background_color, fg=text_color)
folder_label.pack(pady=5)

excel_name_label = tk.Label(left_frame, text="Excel File Path:", font=button_font, bg=background_color, fg=text_color)
excel_name_label.pack()

excel_name_entry = tk.Entry(left_frame, width=40, font=("Helvetica", 10))
excel_name_entry.pack(pady=5)

browse_excel_button = tk.Button(left_frame, text="Browse", command=browse_excel_path, bg=accent_color, fg="white", font=button_font)
browse_excel_button.pack(pady=5)

file_type_label = tk.Label(left_frame, text="Select File Type:", font=button_font, bg=background_color, fg=text_color)
file_type_label.pack()

file_type_var = tk.StringVar()
file_type_var.set("Image")

file_type_menu = tk.OptionMenu(left_frame, file_type_var, "Image", "PDF")
file_type_menu.config(bg=accent_color, fg="white", font=button_font)
file_type_menu.pack(pady=5)

# Create a button for the label function
label_button = tk.Button(left_frame, text="Label", command=label_function, bg=accent_color, fg="white", font=button_font)
label_button.pack(pady=5)

ocr_button = tk.Button(left_frame, text="Initiate OCR", command=initiate_ocr, bg=accent_color, fg="white", font=button_font)
ocr_button.pack(pady=10)

# Create a label for displaying selected image in the right frame
display_canvas = tk.Canvas(right_frame, width=300, height=300, bg=background_color)
display_canvas.pack(pady=10)

# Bind the select_file_type function to the Configure event of file_type_menu
file_type_menu.bind("<Configure>", lambda event: select_file_type())

# Create an error label for displaying error messages
error_label = tk.Label(left_frame, text="", font=("Helvetica", 10), bg=background_color, fg="red")
error_label.pack(pady=5)

# Start the Tkinter event loop
window.mainloop()
