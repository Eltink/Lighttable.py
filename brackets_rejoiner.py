import os
import shutil
from PIL import Image, ImageTk
from PIL.ExifTags import TAGS

# import the necessary functions or classes from the brackets_sorter module
from copiador_de_arquivo import copia_arquivo

#2023 07 13 This is working as intended, calls itself at the end of the code

def ExposureBiasValue(filepath):
    img = Image.open(filepath)
    try:
        exif_table = {}
        for k, v in img._getexif().items():
            tag = TAGS.get(k)
            exif_table[tag] = v
        # print(exif_table)
        # print("exif_table[ExposureMode]", exif_table.get("ExposureMode"))
        if exif_table.get("ExposureMode") == 2:
            return float(exif_table.get("ExposureBiasValue"))
        else:
            # print(f"{filepath} got faulty EXIF info")
            return None  # Faulty data
    except AttributeError:
        print(f"Error: Failed to extract exif tags from file {filepath}")

def brackets_rejoiner(filename, median_folder, output_folder):
    sequential = int(filename.split('_')[1].split('.')[0])  # Extract the sequential number
    EV = ExposureBiasValue(filename)

    # Searching for target darker file
    target_darker = "GE_" + str(sequential - 1).zfill(5) + ".JPG"  # Create the target darker file name fixme edgecase when goes from 9999 to 0000
    target_darker_path = os.path.join(median_folder, target_darker)
    print("Target Darker File Path:", target_darker_path)
    try:
        target_darker_ev = ExposureBiasValue(target_darker_path)
        print("Target Darker File EV:", target_darker_ev)
        if target_darker_ev in [EV - 1, EV - 2, EV - 3]:
            copia_arquivo(median_folder, target_darker, output_folder)
            print("Copied target darker file:", target_darker)
        else:
            print("Couldn't find the darker file. Sequential:", sequential, "Target:", target_darker)
            # TODO check if it was bracketing, if so, raise a warning
    except Exception as e:
        print("Error:", e)

    # Searching for target lighter file
    target_lighter = "GE_" + str(sequential + 1).zfill(5) + ".JPG"  # Create the target lighter file name
    target_lighter_path = os.path.join(median_folder, target_lighter)
    print("Target Lighter File Path:", target_lighter_path)
    try:
        target_lighter_ev = ExposureBiasValue(target_lighter_path)
        print("Target Lighter File EV:", target_lighter_ev)
        if target_lighter_ev in [EV + 1, EV + 2, EV + 3]:
            copia_arquivo(median_folder, target_lighter, output_folder)
            print("Copied target lighter file:", target_lighter)
        else:
            print("Couldn't find the lighter file. Sequential:", sequential, "Target:", target_lighter)
            # TODO check if it was bracketing, if so, info incomplete bracketing
    except Exception as e:
        print("Error:", e)

def find_associated_bracketed_images(database_folder, median_folder, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Iterate over each file in the database folder
    for filename in os.listdir(median_folder):
        if filename.endswith(".JPG") or filename.endswith(".jpeg") or filename.endswith(".png"):
            # Extract only the filename from the full file path
            file_name = os.path.basename(filename)
            # Call the brackets_rejoiner function for the current file
            file_path = os.path.join(database_folder, filename)
            print("\nProcessing file:", file_path)
            brackets_rejoiner(file_path, database_folder, output_folder)

# Example usage
database_folder = "C:\\Users\\glauc\\Desktop\\database"
median_folder = "C:\\Users\\glauc\\Desktop\\kjaf"
output_folder = os.path.join(median_folder, "brackets_rejoiner")

find_associated_bracketed_images(database_folder, median_folder, output_folder)

