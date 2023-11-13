import os
import copiador_de_arquivo

# Programm to sort between good and bar HDRs, previously sorted

bad_dir = r"C:\Users\glauc\Desktop\bom ou bad\bad"
bad = os.listdir(bad_dir)

all_dir = r"C:\Users\glauc\Desktop\bom ou bad\all"
all = os.listdir(all_dir)

i = 0
bons, bads = 0, 0

dest_dir = r"C:\Users\glauc\Desktop\bom ou bad\out"

# This assumes that all bad brackets are complete!
while i < len(all):
    if i == len(all)-1:
        if all[i-1] not in bad:  # This assumes that the last good is complete
            copiador_de_arquivo.copia_arquivo(all_dir, all[i], r"C:\Users\glauc\Desktop\bom ou bad\out\bom")
            i += 1
            bons += 1
    elif all[i+1] in bad:
        copiador_de_arquivo.copia_arquivo(all_dir, all[i+1], r"C:\Users\glauc\Desktop\bom ou bad\out\bad")
        i += 3
        bads += 1
    else:
        copiador_de_arquivo.copia_arquivo(all_dir, all[i], r"C:\Users\glauc\Desktop\bom ou bad\out\bom")
        i += 1
        bons += 1

print(f"all {len(all)}")
print(f"bads {bads}")
print(f"bons {bons}")
print(f"3x bads + bons = {3*bads+bons}")
