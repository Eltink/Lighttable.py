import tkinter as tk
from PIL import Image, ImageTk
import os

# Import of configuration parameters
source_dir = 'C:\\Users\\glauc\\Desktop\\TL raios takaoka\\LR_out'
files = os.listdir(source_dir)

# Setting up overall environment
root = tk.Tk() #Create window
label = tk.Label(root)
first_file = os.path.join(source_dir,files[0])
img = Image.open(first_file)
img_resized = img.resize((1920,1080))
label.img = ImageTk.PhotoImage(img)
label['image'] = label.img
label.pack()

def pressionou1(event):
    img = Image.open(os.path.join(source_dir,files[1]))
    label.img = ImageTk.PhotoImage(img)
    label['image'] = label.img

root.bind("1", pressionou1)

root.mainloop()