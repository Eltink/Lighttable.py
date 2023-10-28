import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from PIL.ExifTags import TAGS
import os
from copiador_de_arquivo import copia_arquivo
import time
import shutil

[lower_limit, upper_limit] = [-0.7, 0.3]

source_dir = 'C:\\Users\\glauc\\Desktop\\kjaf'
# source_dir = 'D:\\128_sorter'
source_dir = filedialog.askdirectory()
dest_dir = source_dir
try:
    os.makedirs(dest_dir + "\\Unbracketeds")
    os.makedirs(dest_dir + "\\Braketed_Medians")
    os.makedirs(dest_dir + "\\Braketed_Outliers")
except:
    pass

Unbracketeds_dir        = os.path.join(dest_dir, "Unbracketeds")
Braketed_Medians_dir    = os.path.join(dest_dir, "Braketed_Medians")
Braketed_Outliers_dir   = os.path.join(dest_dir, "Braketed_Outliers")

valid_extensions = [".jpg", ".jpeg", ".png", ".gif", ".JPG"]  # Add any other image file extensions if necessary
files = []
for root, dirs, files_list in os.walk(source_dir):  # Use a different variable name for the loop variable
    for file_name in files_list:  # Use a different variable name for the loop variable
        if any(file_name.endswith(ext) for ext in valid_extensions):
            file_path = os.path.join(root, file_name)  # Full path of the image file
            files.append(file_path)  # Append to the image_files list

# Now 'files' contains the full paths of all image files in the 'source_dir' and its subdirectories

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

def is_bracketed(filename):
    img = Image.open(os.path.join(source_dir, filename))
    try:
        ExposureMode = exif(filename, "ExposureMode")
        if ExposureMode == 0:
            return False  # is not braketed
        elif ExposureMode == 2:
            return True  # is braketed
        else:
            print("filename", filename, "ExposureMode", ExposureMode)
            return None
    except:
        print(f"Error: Failed to extract exif tags from file {filename}")

def ExposureBiasValue(filename):
    img = Image.open(os.path.join(source_dir, filename))
    try:
        exif_table = {}
        for k, v in img._getexif().items():
            tag = TAGS.get(k)
            exif_table[tag] = v
        # print(exif_table)
        print("exif_table[ExposureMode]",exif_table["ExposureMode"])
        if exif_table["ExposureMode"] == 2:
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
    # I commented the lines above and it started working again. No idea why....
    if not is_bracketed(file):
        print(f"move {file} to Unbracketeds")
        copia_arquivo(source_dir, file, Unbracketeds_dir)
        count[0] += 1
    elif is_bracketed(file):
        print("lower_limit", lower_limit)
        print("ExposureBiasValue(file)", ExposureBiasValue(file))
        print("upper_limit", upper_limit)
        print("lower_limit <= ExposureBiasValue(file) <= upper_limit", lower_limit <= ExposureBiasValue(file) <= upper_limit)
        if lower_limit <= ExposureBiasValue(file) <= upper_limit:
            print(f"move {file} to Braketed_Medians")
            copia_arquivo(source_dir, file, Braketed_Medians_dir)
            count[1] += 1
        else:
            print(f"move {file} to Braketed_Outliers")
            copia_arquivo(source_dir, file, Braketed_Outliers_dir)
            count[2] += 1
    print(f"Progress: {((1 + files.index(file)) / len(files) * 100):.1f} % \n")
print(count, "unbracketed, medians and outliers")

print("fim :)")
# TODO "press any key to close"???
