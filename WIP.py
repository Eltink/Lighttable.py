import os
from PIL import Image, ImageTk, ExifTags
import rawpy # Necessary to read .arw files
import time
from PIL import Image, ImageTk
from PIL.ExifTags import TAGS
import tools
import copiador_de_arquivo

bad_dir = r"C:\Users\glauc\Desktop\bom ou bad\Bad\copiadas"
bad = os.listdir(bad_dir)

all_dir = r"C:\Users\glauc\Desktop\bom ou bad\All HDRs"
all = os.listdir(all_dir)

i = 0
bons, bads = 0, 0

dest_dir = r"C:\Users\glauc\Desktop\bom ou bad\out"

# This assumes that all bad brackets are complete!
for i in range(len(all)):
    if all[i] in bad:
        copiador_de_arquivo.copia_arquivo(all_dir, all[i + 1], dest_dir)
        i += 3
        bads += 1
    else:
        copiador_de_arquivo.copia_arquivo(all_dir, all[i], dest_dir)
        i += 1
        bons += 1

print(f"all {len(all)}")
print(f"bads {bads}")
print(f"bons {bons}")
print(f"3x bads + bons = {3*bads+bons}")