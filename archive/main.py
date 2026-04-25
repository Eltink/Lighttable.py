import os
import shutil

# Path to the directory containing the *.arw files
arw_dir = "path/to/arw/files"

# Path to the directory containing the wanted *.jpg files
jpg_dir = "path/to/jpg/files"

# Create a new directory called "copied"
copied_dir = "copied"
os.makedirs(copied_dir, exist_ok=True)

# List to store the names of the *.jpg files that do not have an associated *.arw file
not_found = []

# Iterate over the files in the *.arw directory
for arw_file in os.listdir(arw_dir):
    # Check if the file is an *.arw file
    if arw_file.endswith(".arw"):
        # Get the corresponding *.jpg file by replacing the file extension
        jpg_file = arw_file.replace(".arw", ".jpg")

        # Check if the corresponding *.jpg file exists in the jpg_dir directory
        if os.path.exists(os.path.join(jpg_dir, jpg_file)):
            # Copy the *.arw file to the "copied" directory
            shutil.copy(os.path.join(arw_dir, arw_file), copied_dir)
            # Copy the corresponding *.jpg file to the "copied" directory
            shutil.copy(os.path.join(jpg_dir, jpg_file), copied_dir)
        else:
    # If the corresponding *.jpg file does not exist, add its name to the
