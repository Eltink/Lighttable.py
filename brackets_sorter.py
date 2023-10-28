import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from PIL.ExifTags import TAGS
import os
from copiador_de_arquivo import copia_arquivo

# Current working, created a standalone GUI

[lower_limit, upper_limit] = [-0.7, 0.3]

# Function to update the progress label
def update_progress(progress):
    progress_label.config(text=f"Progress: {progress:.2f}%")

# Function to update the status label
def update_status(status):
    status_label.config(text=f"Status: {status}")
    window.update()

# Function to update the statistics label
def update_statistics(count):
    statistics_label.config(text=f"Unbracketed: {count[0]}, Medians: {count[1]}, Outliers: {count[2]}")

# Extract Exif metadata from an image file
def exif(file_path, gettag):
    img = Image.open(file_path)
    try:
        exif_table = {}
        for k, v in img._getexif().items():
            tag = TAGS.get(k)
            exif_table[tag] = v
        return exif_table.get(gettag)
    except (AttributeError, KeyError):
        return None

def is_bracketed(file_path):
    try:
        ExposureMode = exif(file_path, "ExposureMode")
        if ExposureMode == 0:
            return False  # is not bracketed
        elif ExposureMode == 2:
            return True  # is bracketed
        else:
            print("file_path", file_path, "ExposureMode", ExposureMode)
            return None
    except:
        print(f"Error: Failed to extract exif tags from file {file_path}")

# Function to handle the processing of files
def process_files():
    source_dir = filedialog.askdirectory()
    dest_dir = source_dir

    try:
        os.makedirs(os.path.join(dest_dir, "Unbracketeds"))
        os.makedirs(os.path.join(dest_dir, "Braketed_Medians"))
        os.makedirs(os.path.join(dest_dir, "Braketed_Outliers"))
    except:
        pass

    Unbracketeds_dir = os.path.join(dest_dir, "Unbracketeds")
    Braketed_Medians_dir = os.path.join(dest_dir, "Braketed_Medians")
    Braketed_Outliers_dir = os.path.join(dest_dir, "Braketed_Outliers")

    valid_extensions = [".jpg", ".jpeg", ".png", ".gif", ".JPG"]  # Add any other image file extensions if necessary
    files = []
    for root, dirs, files_list in os.walk(source_dir):
        for file_name in files_list:
            if any(file_name.endswith(ext) for ext in valid_extensions):
                file_path = os.path.join(root, file_name)
                files.append(file_path)
    # Now 'files' contains the full paths of all image files in the 'source_dir' and its subdirectories

    count = [0, 0, 0]
    total_files = len(files)
    update_progress(0.0)
    update_status("Processing files...")
    update_statistics(count)

    for i, file_path in enumerate(files):
        update_progress((i + 1) / total_files * 100)
        update_status(f"Processing file {i + 1}/{total_files}")
        if not is_bracketed(file_path):
            copia_arquivo(source_dir, file_path, Unbracketeds_dir)
            count[0] += 1
        elif is_bracketed(file_path):
            if lower_limit <= float(exif(file_path, "ExposureBiasValue")) <= upper_limit:
                copia_arquivo(source_dir, file_path, Braketed_Medians_dir)
                count[1] += 1
            else:
                copia_arquivo(source_dir, file_path, Braketed_Outliers_dir)
                count[2] += 1

        update_statistics(count)

    update_status("Processing complete!")
    update_progress(100.0)

# Create the main window
window = tk.Tk()
window.title("Image Processing")
window.geometry("400x200")

# Create labels for progress, status, and statistics
progress_label = tk.Label(window, text="Progress: 0.00%")
status_label = tk.Label(window, text="Status: Not started")
statistics_label = tk.Label(window, text="Unbracketed: 0, Medians: 0, Outliers: 0")

# Create a button to start processing files
start_button = tk.Button(window, text="Start", command=process_files)

# Place the widgets in the window
progress_label.pack()
status_label.pack()
statistics_label.pack()
start_button.pack()

# Start the GUI event loop
window.mainloop()
