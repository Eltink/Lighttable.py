import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from PIL.ExifTags import TAGS
import os

import brackets_sorter
from copiador_de_arquivo import copia_arquivo
from brackets_sorter import *

# Initialize the GUI
root = tk.Tk()
imagem_mostrada = tk.Label(root)
imagem_mostrada.pack()
index_atual = 0

# Set up the window
root.title("Eu amo o Bernado")
root.state('zoomed')
root.configure(background="black")

# Set up the file information display
file_info_visible = True
file_info_text = tk.StringVar()
file_info_text.set("init")
file_info_label = tk.Label(root, textvariable=file_info_text, font=('Arial', 12))
file_info_label.place(anchor=tk.NW)

# Set up the copied image feedback display fixme
feedback_label_text = tk.StringVar()
feedback_label_text.set("init")
feedback_label = tk.Label(root, textvariable=feedback_label_text, font=('Arial', 12))
feedback_label.place(anchor=tk.SW)

# Toggle file information display
def toggle_file_info(event):
    global file_info_visible
    file_info_visible = not file_info_visible
    if file_info_visible:
        file_info_label.place(anchor=tk.NW)
    else:
        file_info_label.place_forget()

# Get the source directory from user input
source_dir = filedialog.askdirectory()
# source_dir = "D:\\2023_02_15_SAm\\128 pt2\\2273"
parent_dir = os.path.dirname(source_dir)    # Get the parent directory of the source directory
subdirectories = os.path.split(source_dir)  # Get the name of the last subdirectory in the source directory
last_subdirectory = subdirectories[-1]
destination_dir = os.path.join(parent_dir, last_subdirectory + ' sel') # Create the destination directory path in the parent directory

# Create the destination directory if it doesn't exist
if not os.path.exists(destination_dir):
    os.makedirs(destination_dir)

# Define valid image file extensions
valid_extensions = [".JPG", ".jpg", ".jpeg", ".png", ".gif"]

def wanted_files(dir):
    files = os.listdir(dir)
    EV = [exif(file, "ExposureBiasValue") for file in files]
    neutral_files = []
    for i in range(1, len(files) - 1):
        if EV[i] == (EV[i - 1] + EV[i + 1]) / 2:
            neutral_files.append(files[i])
    non_bracketed = []
    for file in files:
        if exif(file, "ExposureMode") == 0:
            non_bracketed.append(file)
    return neutral_files


# # Get a list of files with valid extensions in the source directory
# wanted_files = brackets_sorter_v3.process_files(source_dir)[0] + brackets_sorter_v3.process_files(source_dir)[1]
# print("wanted_files", wanted_files)
# # files = [file for file in os.listdir(source_dir) if any(file.endswith(ext) for ext in valid_extensions)]
# # files = [file for file in os.listdir(source_dir) if file in wanted_files and any(file.endswith(ext) for ext in valid_extensions)]
# files = [file for file in os.listdir(source_dir) if os.path.join(source_dir, file) in wanted_files and any(file.endswith(ext) for ext in valid_extensions)]
# print("files", files)
# files = wanted_files #fixme

# As i cant remove outliers yet, i'll keep the working dumb function
files = [file for file in os.listdir(source_dir) if any(file.endswith(ext) for ext in valid_extensions)]

loaded_files = dict.fromkeys(files, None)
copied_files = {}

# Extract Exif metadata from an image file
def exif(filename, gettag):
    img = Image.open(os.path.join(source_dir, filename))
    try:
        exif_table = {}
        for k, v in img._getexif().items():
            tag = TAGS.get(k)
            exif_table[tag] = v
        #print(exif_table)
        return exif_table.get(gettag)
    except (AttributeError, KeyError):
        return None

# Load an image and perform necessary adjustments
def carrega(filename):
    img = Image.open(os.path.join(source_dir, filename))
    try:
        Orientation = exif(filename, "Orientation")
        if Orientation == 8:
            img = img.rotate(90, expand=True)
        elif Orientation == 3:
            img = img.rotate(180, expand=True)
        elif Orientation == 6:
            img = img.rotate(270, expand=True)
    except KeyError:
        pass

    aspect_ratio = img.width / img.height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    screen_aspect_ratio = screen_width / screen_height

    if aspect_ratio < screen_aspect_ratio:
        img = img.resize((int(screen_height * aspect_ratio), screen_height), Image.LANCZOS)
    else:
        img = img.resize((screen_width, int(screen_width / aspect_ratio)), Image.LANCZOS)
    return ImageTk.PhotoImage(img)

def get_image_metadata(file):
    metadata_tags = ["FocalLength",    "FNumber",     "ExposureTime", "ISOSpeedRatings", "ExposureBiasValue", "ExposureMode", "DateTime", "LensModel"]
    metadata_labels = ["FocalLength: ", "FNumber: ", "ExposureTime: ", "ISO-",         "Exposure Bias: ",   "Exposure Mode: ", "DateTime: ", "Lens: "]
    try:
        metadata = [str(exif(file, tag)) for tag in metadata_tags]
        if float(metadata[2]) < 1:
            metadata[2] = str(round(1 / float(metadata[2]))) + "s"
            metadata_labels[2] += " 1/"
        else:
            metadata[2] = str(round(float(metadata[2]))) + "s"
        if metadata[5] == "0":
            metadata[5] = "Auto exposure"
        elif metadata[5] == "2":
            metadata[5] = "Bracketing"
        else:
            metadata[5] = str(metadata[5]) + " (unknown case, please investigate)"
        formatted_metadata = [label + value if value else "" for label, value in zip(metadata_labels, metadata)]
        return '\n'.join(formatted_metadata)
    except: return None

def mostra_imagem(file):
    if file in loaded_files:
        imagem_mostrada['image'] = loaded_files[file]
        if file_info_visible:
            file_info_label.place(anchor=tk.NW)
            metadata = get_image_metadata(file)
            file_info_text.set(metadata)
        else:
            file_info_label.place_forget()
        root.update()
        root.title("Eu amo o Bernado - " + str(files[index_atual]) + " - " + str(index_atual + 1) + " of " + str(len(files)))
    else:
        print("This didn't work. Info for debugging follows:")
        print(f"index_atual: {index_atual}")
        print(f"files[index_atual]: {files[index_atual]}")
        print(f"loaded_files[files[index_atual]] was not found")
        print("These are the available dictionary keys:", loaded_files.keys())

    if True:
        try:
            img = Image.open(os.path.join(source_dir, file))
        except FileNotFoundError:
            print(f"Error: {file} not found")
            return
        except OSError as e:
            print(f"Error opening file: {e}")
            return
    return

# Event handlers
def copiar(event):
    filename = files[index_atual]
    if filename in copied_files:
        feedback_label_text.set("Already copied")
    else:
        copia_arquivo(source_dir, filename, destination_dir)
        copied_files[filename] = True
        feedback_label_text.set("Copied successfully")
        proxima(event)
        if loaded_files.get(files[(index_atual + 1) % len(files)]) is None:
            loaded_files[files[index_atual + 1]] = carrega(files[index_atual + 1])

def proxima(event):
    global index_atual
    index_atual = (index_atual + 1) % len(files)
    mostra_imagem(files[index_atual])

def anterior(event):
    global index_atual
    index_atual = (index_atual - 1) % len(files)
    mostra_imagem(files[index_atual])

def right(event):
    proxima(event)
    if loaded_files.get(files[(index_atual + 1) % len(files)]) is None:
        loaded_files[files[index_atual + 1]] = carrega(files[index_atual + 1])

def left(event):
    anterior(event)
    if loaded_files.get(files[(index_atual - 1) % len(files)]) is None:
        loaded_files[files[index_atual - 1]] = carrega(files[index_atual - 1])

# Bind keys to event handlers
root.bind("<Up>", copiar)
root.bind("<Right>", right)
root.bind("<Left>", left)
root.bind("6", right)
root.bind("4", left)
root.bind("8", copiar)
root.bind("i", toggle_file_info)

# Preload the first two images
try:
    for file in files[0:2]:
        loaded_files[file] = carrega(file)
except FileNotFoundError as e:
    print(f"Error: {e}")
except OSError as e:
    print(f"Error opening file: {e}")
except Exception as e:
    print(f"Error: {e}")

# Show the first image
mostra_imagem(files[0])

# Add the feedback label to the GUI
# feedback_label.pack()

root.mainloop()
print("fim")
