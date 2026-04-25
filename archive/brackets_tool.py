import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from PIL.ExifTags import TAGS
import os
from copiador_de_arquivo import copia_arquivo
import time
import shutil

[lower_limit, upper_limit] = [-0.7, 0.3]

source_dir = r"E:\Selecionar\2024_09_18_Islandia\A74\JPGs\101MSDCF JPG"
# source_dir = 'D:\\128_sorter'
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

        if exif_table["ExposureMode"] == 2: # is bracketed
            return float(exif_table["ExposureBiasValue"])
        elif exif_table["ExposureMode"] == 0: # is not bracketed
            return float(exif_table["ExposureBiasValue"])
        else:
            print(f"{filename} got faulty EXIF info")
            return None  # Faulty data
    except AttributeError:
        print(f"Error: Failed to extract exif tags from file {filename}")


print(f"Processing {len(files)} files")
count = [0, 0, 0]

for file in files:
    # print("")
    # print("file:", file)
    # print("is_bracketed(file):", is_bracketed(file))
    # print("ExposureBiasValue(file):", ExposureBiasValue(file))
    # print("ExposureBiasValue(file) type:", type(ExposureBiasValue(file)))
    # print("upper_limit:", upper_limit)
    # print("ExposureBiasValue(file) <= upper_limit:", ExposureBiasValue(file) <= upper_limit)
    # print("float(ExposureBiasValue(file)) <= upper_limit:", float(ExposureBiasValue(file)) <= upper_limit)
    if not is_bracketed(file):
        # print(f"move {file} to Unbracketeds")
        copia_arquivo(source_dir, file, Unbracketeds_dir)
        count[0] += 1
    elif is_bracketed(file):
        # print("lower_limit", lower_limit)
        # print("ExposureBiasValue(file)", ExposureBiasValue(file))
        # print("upper_limit", upper_limit)
        # print("lower_limit <= ExposureBiasValue(file) <= upper_limit", lower_limit <= ExposureBiasValue(file) <= upper_limit)
        if lower_limit <= ExposureBiasValue(file) <= upper_limit:
            # print(f"move {file} to Braketed_Medians")
            copia_arquivo(source_dir, file, Braketed_Medians_dir)
            count[1] += 1
        else:
            # print(f"move {file} to Braketed_Outliers")
            copia_arquivo(source_dir, file, Braketed_Outliers_dir)
            count[2] += 1
    print(f"Progress: {(1+files.index(file))/len(files)*100} %")
print(count, "unbracketed, medians and outliers")

# location = os.path.join(source_dir, files[0])
# from exif import Image
# with open(location, 'rb') as image_file:
#    my_image = Image(image_file)
# my_image.list_all()
# print(my_image)

print("fim :)")
# TODO "press any key to close"???
