import time
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from PIL.ExifTags import TAGS
import os
import rawpy # Necessary to read .arw files
import imageio # Necessary to read .arw files
import threading
import subprocess

import brackets_sorter
from copiador_de_arquivo import copia_arquivo
from tools import *

filepath = r"E:\Selecionar\2024_01_08_Southern Africa\A73\JPG\17631216\GE_00877.JPG"
exif = []
img = Image.open(filepath)
try:
    exif_data = img._getexif()
    if exif_data is not None:
        for k, v in exif_data.items():
            tag = ExifTags.TAGS.get(k)
            print(tag,"%",v)

            exif += [tag,v]
except (AttributeError, KeyError):
    pass

EM = get_exif(filepath, "ExposureMode")
print(f"EM {EM}")
print(f"exif {exif}")



