# Abaixo tem uma versao mais atual do GPT o1
# Chat de 

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
from PIL.ExifTags import TAGS
import os
import pathlib
from datetime import datetime

debugging = False
if debugging: file_paths = [r"E:\Selecionar\2024_09_18_Islandia\A73\JPGs\GE_00349 - A mina q pediu as fotos.JPG"]
else: file_paths = []


# Helper function to clean EXIF data
def clean_exif_data(exif_data):
    clean_data = {}
    exclude_tags = []  # Customize which EXIF tags to exclude

    for tag, value in exif_data.items():
        if tag in exclude_tags:
            continue
        # Skip binary or encoded data
        if isinstance(value, bytes):
            continue
        clean_data[tag] = value

    return clean_data


# Function to convert a timestamp to a readable format
def format_time(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


# Function to format file size to KB, MB, GB
def format_size(size_bytes):
    if size_bytes == 0:
        return "0 bytes"
    size_name = ("bytes", "KB", "MB", "GB", "TB")
    i = int(min(len(size_name) - 1, max(0, size_bytes).bit_length() // 10))
    p = 1 << (i * 10)
    return f"{size_bytes / p:.2f} {size_name[i]}"


# Function to get file metadata using pathlib
def get_file_metadata(filepath):
    file_path = pathlib.Path(filepath)
    stats = file_path.stat()

    # Get file metadata
    metadata = {
        "File Size": format_size(stats.st_size),
        "Creation Time": format_time(stats.st_ctime),
        "Modification Time": format_time(stats.st_mtime),
        "Last Access Time": format_time(stats.st_atime),
        "File Path": str(file_path),
        "File Name": file_path.name,
        "File Extension": file_path.suffix,
    }

    return metadata


# Function to get EXIF data and additional metadata if needed
def get_exif_and_metadata(filepath, basic=False):
    try:
        img = Image.open(filepath)
        exif_data = img._getexif()
        exif_info = {}

        # If EXIF data is found, process it
        if exif_data:
            for tag, value in exif_data.items():
                tag_name = TAGS.get(tag, tag)
                if basic:
                    if tag_name in ('DateTime', 'Make', 'Model', 'GPSInfo'):
                        exif_info[tag_name] = value
                else:
                    exif_info[tag_name] = value

            # Clean the EXIF data
            exif_info = clean_exif_data(exif_info)
        else:
            exif_info = {"EXIF Data": "No EXIF data found"}

        # Add general image metadata (available regardless of EXIF)
        image_metadata = {
            "Format": img.format,
            "Mode": img.mode,
            "Size (width x height)": f"{img.size[0]} x {img.size[1]} pixels",
        }

        # Combine EXIF data, image metadata, and file-level metadata
        return {**image_metadata}, get_file_metadata(filepath), {**exif_info}

    except Exception as e:
        return str(e)


# Function to open files and display EXIF and metadata
def open_files():
    global file_paths
    if not file_paths:  # Only ask for files if not in debugging mode
        # Allow multiple file selection
        file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        if not file_paths:
            return

    basic = var_basic.get()

    result_text.delete(1.0, tk.END)  # Clear existing content

    # Loop through selected files and get EXIF data
    for file_path in file_paths:
        image_metadata, file_metadata, exif_info = get_exif_and_metadata(file_path, basic=basic)
        file_name = os.path.basename(file_path)

        # Add filename as a header
        result_text.insert(tk.END, f"File: {file_name}\n", 'bold')  # Bold header

        # Function to format metadata with alignment
        def format_metadata(metadata):
            if isinstance(metadata, dict):
                # Find the maximum length of keys
                max_key_length = max(len(key) for key in metadata.keys())
                formatted_str = "\n".join(
                    [f"{key}: {' ' * (max_key_length - len(key))} {value}" for key, value in metadata.items()]
                )
            else:
                formatted_str = metadata
            return formatted_str

        # Format each metadata section
        image_str = format_metadata(image_metadata)
        file_str = format_metadata(file_metadata)
        exif_str = format_metadata(exif_info)

        # Display metadata and EXIF data with \n\n separation
        result_text.insert(tk.END, image_str + "\n\n" + file_str + "\n\n" + exif_str + "\n\n")


# GUI Setup
root = tk.Tk()
root.title("EXIF and Metadata Viewer")
root.geometry("500x1500")

# Checkbox for basic or complete EXIF data
var_basic = tk.BooleanVar(value=False)
chk_basic = tk.Checkbutton(root, text="Show only Basic EXIF Data", variable=var_basic)
chk_basic.pack(pady=10)

# Button to select file
btn_open = tk.Button(root, text="Open Image", command=open_files)
btn_open.pack(pady=10)

# Text widget to display EXIF data
result_text = tk.Text(root, wrap=tk.WORD, height=15)
result_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

# Add a tag for bold text
result_text.tag_configure('bold', font=('TkDefaultFont', 10, 'bold'))

if debugging: open_files()

# Start the Tkinter event loop
root.mainloop()


import os
import sys
import time
from PIL import Image, ExifTags

"""
Why do some tags have gibberish like \x01\x00\x00 etc?
----------------------------------------------------
Certain metadata fields are stored as binary data (e.g. an embedded thumbnail, an ICC color profile,
or other unknown chunk), which is not textual. When converted to a Python string, it shows up as
escape sequences like \x01 or other non-readable bytes.

If you want to avoid these fields in your output, you could filter or skip them. Some are still valid info
but not meant for direct reading as text.

Script usage:
--------------
This script will output columns separated by tabs (\t), which Excel can parse when you copy from
the terminal and paste into an Excel sheet. Each line has the format:
  filename    field_name    field_value

To run:
   python compare_metadata.py <directory>

Or simply:
   python compare_metadata.py

and enter the directory path when prompted.
"""

def extract_jpg_metadata(img):
    """
    Extract metadata from a JPG image using ExifTags.
    Returns a dictionary of {tag_name: tag_value}.
    """
    metadata = {}
    exif_data = img._getexif()  # Might be None if there's no EXIF
    if exif_data is not None:
        for tag_id, value in exif_data.items():
            tag_name = ExifTags.TAGS.get(tag_id, tag_id)
            metadata[str(tag_name)] = str(value)
    return metadata

def extract_png_metadata(img):
    """
    Extract metadata from a PNG image using info.
    Returns a dictionary of {tag_name: tag_value}.
    """
    metadata = {}
    for k, v in img.info.items():
        metadata[str(k)] = str(v)
    return metadata

def analyze_directory(dir_path):
    """
    Looks for .jpg and .png files in dir_path.
    Prints tab-separated lines: filename, field_name, field_value.
    Each line can be copy-pasted into Excel.

    For each file:
      1) Extract standard EXIF or PNG info
      2) Print lines for each metadata key
      3) Print lines for creation time, modification time, last access time, and file size.
    """
    valid_extensions = [".jpg", ".jpeg", ".png"]
    all_files = os.listdir(dir_path)
    image_files = [f for f in all_files if any(f.lower().endswith(ext) for ext in valid_extensions)]

    # Print a header row, tab-separated
    print("filename\tfield_name\tfield_value")

    for filename in image_files:
        filepath = os.path.join(dir_path, filename)
        try:
            with Image.open(filepath) as img:
                if filename.lower().endswith((".jpg", ".jpeg")):
                    metadata_dict = extract_jpg_metadata(img)
                else:
                    metadata_dict = extract_png_metadata(img)

                # Print out any extracted image metadata
                if not metadata_dict:
                    print(f"{filename}\tNO_METADATA_FOUND\t")
                else:
                    for key, value in metadata_dict.items():
                        # Replace tabs/newlines with spaces so it doesn't break columns
                        key_escaped = key.replace("\t", " ").replace("\n", " ")
                        value_escaped = value.replace("\t", " ").replace("\n", " ")
                        print(f"{filename}\t{key_escaped}\t{value_escaped}")

            # Now gather OS-level metadata
            ctime = os.path.getctime(filepath)
            mtime = os.path.getmtime(filepath)
            atime = os.path.getatime(filepath)
            size_bytes = os.path.getsize(filepath)
            ctime_human = time.ctime(ctime)
            mtime_human = time.ctime(mtime)
            atime_human = time.ctime(atime)

            # Print them out tab-separated
            print(f"{filename}\tos_path_getctime\t{ctime_human}")
            print(f"{filename}\tos_path_getmtime\t{mtime_human}")
            print(f"{filename}\tos_path_getatime\t{atime_human}")
            print(f"{filename}\tos_path_getsize\t{size_bytes}")

        except Exception as e:
            # If there's an error reading the file, just print an error line.
            err_str = str(e).replace("\t", " ").replace("\n", " ")
            print(f"{filename}\tERROR\t{err_str}")

def main():
    if len(sys.argv) > 1:
        dir_path = sys.argv[1]
    else:
        dir_path = input("Enter the directory path containing your JPG/PNG files: ")

    if not os.path.isdir(dir_path):
        print("Invalid directory.")
        sys.exit(1)

    analyze_directory(dir_path)

if __name__ == "__main__":
    main()
