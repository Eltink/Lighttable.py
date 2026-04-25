import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from PIL.ExifTags import TAGS
import os
from copiador_de_arquivo import copia_arquivo
import time
import shutil

# source_dir = 'C:\\Users\\glauc\\Desktop\\kjaf'
source_dir = 'D:\\128_sorter'
dest_dir = source_dir
try:
    os.makedirs(dest_dir + "\\Unbracketeds")
    os.makedirs(dest_dir + "\\Braketed_Medians")
    os.makedirs(dest_dir + "\\Braketed_Outliers")
except:
    pass

Unbracketeds_dir = os.path.join(dest_dir, "Unbracketeds")
Braketed_Medians_dir = os.path.join(dest_dir, "Braketed_Medians")
Braketed_Outliers_dir = os.path.join(dest_dir, "Braketed_Outliers")

# source_dir = filedialog.askdirectory()

valid_extensions = [".jpg", ".jpeg", ".png", ".gif", ".JPG"]  # Add any other image file extensions if necessary
files = [file for file in os.listdir(source_dir) if
         any(file.endswith(ext) for ext in valid_extensions)]  # O nome das imagens

def is_bracketed(filename):
    img = Image.open(os.path.join(source_dir, filename))
    try:
        exif_table = {}
        for k, v in img._getexif().items():
            tag = TAGS.get(k)
            exif_table[tag] = v
        # print(exif_table)

        if exif_table["ExposureMode"] == 0:
            return False  # is not braketed
        elif exif_table["ExposureMode"] == 2:
            return True  # is braketed
        else:
            return None  # Faulty data
    except AttributeError:
        print(f"Error: Failed to extract exif tags from file {filename}")

def ExposureBiasValue(filename):
    img = Image.open(os.path.join(source_dir, filename))
    try:
        exif_table = {}
        for k, v in img._getexif().items():
            tag = TAGS.get(k)
            exif_table[tag] = v
        # print(exif_table)

        if exif_table["ExposureMode"] == 2:
            return exif_table["ExposureBiasValue"]
        else:
            print(f"{filename} got faulty EXIF info")
            return None  # Faulty data
    except AttributeError:
        print(f"Error: Failed to extract exif tags from file {filename}")

def readexif(filename, exifname):
    global source_dir
    img = Image.open(os.path.join(source_dir, filename))
    try:
        exif_table = {}
        for k, v in img._getexif().items():
            tag = TAGS.get(k)
            exif_table[tag] = v
        # print(exif_table)
        return exif_table[exifname]
    except:
        return None

print(f"Processing {len(files)} files")
count = [0, 0, 0]
for file in files:
    print(file, readexif(file, "BrightnessValue"), readexif(file, "ExposureBiasValue"))

# location = os.path.join(source_dir, files[0])
# from exif import Image
# with open(location, 'rb') as image_file:
#    my_image = Image(image_file)
# my_image.list_all()
# print(my_image)

print("fim :)")
# TODO "press any key to close"???
