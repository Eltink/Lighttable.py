import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from PIL.ExifTags import TAGS
import os
from copiador_de_arquivo import copia_arquivo

# Initialize the GUI
root = tk.Tk()
imagem_mostrada = tk.Label(root)
imagem_mostrada.pack()
index_atual = 0

# Set up the window
root.title("Eu amo o Bernado")
root.state('zoomed')

# Set up the file information display
file_info_visible = True
file_info_text = tk.StringVar()
file_info_text.set("init\nisso ai")
file_info_label = tk.Label(root, textvariable=file_info_text, font=('Arial', 12))
file_info_label.place(anchor=tk.NW)


# Toggle file information display
def toggle_file_info(event):
    global file_info_visible
    file_info_visible = not file_info_visible
    if file_info_visible:
        file_info_label.place(anchor=tk.NW)
    else:
        file_info_label.place_forget()


# Define source and destination directories
#source_dir = 'C:\\Users\\glauc\\Desktop\\sel'
source_dir = filedialog.askdirectory()
destination_dir = 'C:\\Users\\glauc\\Desktop\\sel'

# Define valid image file extensions
valid_extensions = [".jpg", ".jpeg", ".png", ".gif", ".JPG"]

# Get a list of files with valid extensions in the source directory
files = [file for file in os.listdir(source_dir) if any(file.endswith(ext) for ext in valid_extensions)]
loaded_files = dict.fromkeys(files, None)


# Extract Exif metadata from an image file
def exif(filename, gettag):
    img = Image.open(os.path.join(source_dir, filename))
    try:
        exif_table = {}
        for k, v in img._getexif().items():
            tag = TAGS.get(k)
            exif_table[tag] = v
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
    metadata_tags = ["FocalLength",    "FNumber",     "ExposureTime", "ISOSpeedRatings", "ExposureBiasValue", "ExposureProgram", "DateTime", "LensModel"]
    metadata_labels = ["FocalLength: ", "FNumber: ", "ExposureTime: 1/", "ISO-",         "Exposure Bias: ",   "Bracketing: ", "DateTime: ", "Lens: "]
    metadata = [str(exif(file, tag)) for tag in metadata_tags]
    # Fix for ExposureMode == 2 is bracketed
    metadata[2] = str(1 / float(metadata[2]))
    formatted_metadata = [label + value if value else "" for label, value in zip(metadata_labels, metadata)]
    return '\n'.join(formatted_metadata)


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
        root.title("Eu amo o Bernado - " + str(files[index_atual]) + " - " + str(index_atual + 1) + " of " + str(
            len(files)))
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
        try:
            ExposureMode = exif(file, "ExposureMode")
            if ExposureMode == 0 or ExposureMode == 8:
                root.configure(background="black")
            elif ExposureMode == 2:
                root.configure(background="gray")
        except KeyError:
            pass
    return

# Event handlers
def copiar(event):
    copia_arquivo(source_dir, files[index_atual], destination_dir)
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

root.mainloop()
print("fim")
