import os
from PIL import Image
from PIL.ExifTags import TAGS

# Currently working, defines functions to be called by other programs

def exif(filename, gettag):
    img = Image.open(filename)
    try:
        exif_table = {}
        for k, v in img._getexif().items():
            tag = TAGS.get(k)
            exif_table[tag] = v
        return exif_table.get(gettag)
    except (AttributeError, KeyError):
        return None

def process_files(source_dir, lower_limit=-0.7, upper_limit=0.3):
    valid_extensions = [".jpg", ".jpeg", ".png", ".gif", ".JPG"]
    files = []
    for root, dirs, files_list in os.walk(source_dir):
        for file_name in files_list:
            if any(file_name.endswith(ext) for ext in valid_extensions):
                file_path = os.path.join(root, file_name)
                files.append(file_path)

    unbracketeds = []
    medians = []
    outliers = []

    for file in files:
        if not is_bracketed(file):
            unbracketeds.append(file)
        elif is_bracketed(file):
            exposure_bias = ExposureBiasValue(file)
            if exposure_bias is not None and lower_limit <= exposure_bias <= upper_limit:
                medians.append(file)
            else:
                outliers.append(file)
    return unbracketeds, medians, outliers

def is_bracketed(filename):
    img = Image.open(filename)
    exposure_mode = exif(filename, "ExposureMode")
    if exposure_mode == 0:
        return False
    elif exposure_mode == 2:
        return True
    else:
        return False

def ExposureBiasValue(filename):
    img = Image.open(filename)
    return float(exif(filename, "ExposureBiasValue"))
