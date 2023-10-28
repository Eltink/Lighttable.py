import time
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from PIL.ExifTags import TAGS
import os
import rawpy  # Necessary to read .arw files
import imageio  # Necessary to read .arw files
import threading

import brackets_sorter
from copiador_de_arquivo import copia_arquivo
from tools import *

debugging = 0
timing = 0

# Initialize the GUI
root = tk.Tk()
imagem_mostrada = tk.Label(root)
imagem_mostrada.pack()
index_atual = 0

# Set up the window
root.title("Eu amo o Bernado")
root.state('zoomed')
root.configure(background="black")

# Set up the file information display
file_info_visible = True
file_info_text = tk.StringVar()
file_info_text.set("init")
file_info_label = tk.Label(root, textvariable=file_info_text, font=('Arial', 12))
# file_info_label.place(anchor=tk.NW) # seem to be already handled by toggle_file_info

# Set up the copied image feedback display fixme
feedback_label_text = tk.StringVar()
feedback_label_text.set("init")
feedback_label = tk.Label(root, textvariable=feedback_label_text, font=('Arial', 12))
feedback_label.place(anchor=tk.SW)


# Toggle file information display
def toggle_file_info(event):
    global file_info_visible
    file_info_visible = not file_info_visible
    if file_info_visible:
        file_info_label.place(anchor=tk.NW)
    else:
        file_info_label.place_forget()


# Get the source directory from user input
if debugging:
    source_dir = r"C:\Users\glauc\Desktop\kjaf"
# if debugging: source_dir = filedialog.askdirectory()
else:
    source_dir = filedialog.askdirectory()
destination_dir = get_destination_dir(source_dir)

# Define valid image file extensions
valid_extensions = [".JPG", ".jpg", ".jpeg", ".png", ".gif", ".ARW"]
t0 = time.time()
# Original list of files with valid extensions
files = [file for file in os.listdir(source_dir) if any(file.endswith(ext) for ext in valid_extensions)]

# Refining files
filepaths = [os.path.join(source_dir, file) for file in files]
t1 = time.time()
showable = is_it_showable(filepaths)  # Example: [1, 1, 0, 1]
if timing: print("Time to calculate showable: ", time.time() - t1)
files = [file for file, is_showable in zip(files, showable) if is_showable]
if timing: print("Time to calculate files: ", time.time() - t0)

loaded_files = dict.fromkeys(files, None)
copied_files = {}


# Load an image and perform necessary adjustments
def carrega(filename):
    file_path = os.path.join(source_dir, filename)

    if filename.endswith('.ARW'):
        # For .ARW files, use rawpy to read the raw data and imageio to convert to RGB
        raw = rawpy.imread(file_path)
        rgb = raw.postprocess()  # This is a slow function
        img = Image.fromarray(rgb)
    else:
        img = Image.open(file_path)

    try:
        Orientation = get_exif(file_path, "Orientation")
        if Orientation == 8:
            img = img.rotate(90, expand=True)
        elif Orientation == 3:
            img = img.rotate(180, expand=True)
        elif Orientation == 6:
            img = img.rotate(270, expand=True)
    except Exception as e:
        print(f"An error occurred on loading file {filename}: {e}")

    aspect_ratio = img.width / img.height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    screen_aspect_ratio = screen_width / screen_height

    if aspect_ratio < screen_aspect_ratio:
        img = img.resize((int(screen_height * aspect_ratio), screen_height),
                         Image.LANCZOS)  # Image.ANTIALIAS is an alternative. Better?
    else:
        img = img.resize((screen_width, int(screen_width / aspect_ratio)), Image.LANCZOS)

    loaded_files[filename] = ImageTk.PhotoImage(img)  # Converting the image from PIL to TK format
    # return ImageTk.PhotoImage(img)
    # Legacy version


def get_image_metadata(file):
    filepath = os.path.join(source_dir, file)
    metadata_tags = ["FocalLength", "FNumber", "ExposureTime", "ISOSpeedRatings", "ExposureBiasValue", "ExposureMode",
                     "DateTime", "LensModel"]
    metadata_labels = ["FocalLength: ", "FNumber: ", "ExposureTime: ", "ISO-", "Exposure Bias: ", "Exposure Mode: ",
                       "DateTime: ", "Lens: "]
    try:
        metadata = [str(get_exif(filepath, tag)) for tag in metadata_tags]
        if float(metadata[2]) < 1:
            metadata[2] = str(round(1 / float(metadata[2]))) + "s"
            metadata_labels[2] += " 1/"
        else:
            metadata[2] = str(round(float(metadata[2]))) + "s"

        if metadata[5] == "0":
            metadata[5] = "Auto exposure"
        elif metadata[5] == "2":
            metadata[5] = "Bracketing"
        else:
            metadata[5] = str(metadata[5]) + " (unknown case, please investigate)"
        formatted_metadata = [label + value if value else "" for label, value in zip(metadata_labels, metadata)]
        return '\n'.join(formatted_metadata)
    except Exception as e:
        print(f"An error occurred getting metadata from file {file}: {e}")
        return None


def mostra_imagem(file):
    if file in loaded_files:
        imagem_mostrada['image'] = loaded_files[file]
        if file_info_visible:
            file_info_label.place(anchor=tk.NW)
            metadata = get_image_metadata(file)
            file_info_text.set(metadata)
        else:
            file_info_label.place_forget()
        feedback_label.pack()

        root.update()
        root.title(
            "Eu amo o Bernado - " + str(files[index_atual]) + " - " + str(index_atual + 1) + " of " + str(len(files)))
    else:  # Debugging
        print(f"File {file} was not found in loaded_files.Info for debugging follows:")
        print(f"index_atual: {index_atual}")
        print(f"files[index_atual]: {files[index_atual]}")
        print(f"loaded_files[files[index_atual]] was not found")
        print("These are the available dictionary keys:", loaded_files.keys())

    # # What is this doing here? Is it even doing anything?/???
    # try: img = Image.open(os.path.join(source_dir, file))
    # except FileNotFoundError:
    #     print(f"Error: {file} not found")
    #     return
    # except OSError as e:
    #     print(f"Error opening file: {e}")
    #     return
    return


# Event handlers
def copiar(event):
    filename = files[index_atual]
    if filename in copied_files:
        feedback_label_text.set("Already copied")
    else:
        filepath = os.path.join(source_dir, filename)
        copia_arquivo(source_dir, filename, destination_dir)
        copied_files[filename] = True
        if get_exif(filepath, "ExposureMode") != 2:  # Isnt bracketed
            feedback_label_text.set("Copied 1 unbracketed file")
        elif get_exif(filepath, "ExposureMode") == 2:  # Is bracketed
            feedback_label_text.set("Copied median")
            EV = get_exif(filepath, "ExposureBiasValue")
            darker = file_navigator(filepath, -1)
            if get_exif(darker, "ExposureBiasValue") in [EV - 3, EV - 2, EV - 1]:
                copia_arquivo(source_dir, darker,
                              destination_dir)  # How is this working, if source and darker are paths?
                feedback_label_text.set(feedback_label_text.get() + " and darker")
            lighter = file_navigator(filepath, +1)
            if get_exif(lighter, "ExposureBiasValue") in [EV + 3, EV + 2, EV + 1]:
                copia_arquivo(source_dir, lighter, destination_dir)
                feedback_label_text.set(feedback_label_text.get() + " and lighter")

        right(event)


def proxima(event):
    global index_atual
    index_atual = (index_atual + 1) % len(files)
    mostra_imagem(files[index_atual])


def anterior(event):
    global index_atual
    index_atual = (index_atual - 1) % len(files)
    mostra_imagem(files[index_atual])


def right(event):
    proxima(event)
    if loaded_files.get(files[(index_atual + 1) % len(files)]) is None:
        carrega(files[index_atual + 1])


def left(event):
    anterior(event)
    if loaded_files.get(files[(index_atual - 1) % len(files)]) is None:
        carrega(files[index_atual - 1])


# Bind keys to event handlers
root.bind("<Up>", copiar)
root.bind("<Right>", right)
root.bind("<Left>", left)
root.bind("6", right)
root.bind("4", left)
root.bind("8", copiar)
root.bind("i", toggle_file_info)

t0 = time.time()
carrega(files[0])
if timing: print("Time to load first image: ", time.time() - t0)
t1 = time.time()
mostra_imagem(files[0])
if timing: print("Time to show first image: ", time.time() - t1)
t2 = time.time()
carrega(files[1])
if timing: print("Time to load second image: ", time.time() - t2)
if timing: print("Time to boot program: ", time.time() - t0)

slideshow_event = threading.Event()
slideshow_thread = None
slideshow_running = False


def start_slideshow(event=None):  # Add the event parameter with a default value of None
    global index_atual, slideshow_running, slideshow_thread

    # Toggle slideshow state
    slideshow_running = not slideshow_running

    def slideshow_thread_func():
        global index_atual
        while slideshow_running:
            index_atual = (index_atual + 1) % len(files)
            mostra_imagem(files[index_atual])
            root.update()  # Update the GUI
            time.sleep(0.2)  # Delay between images (in seconds)

    if slideshow_running:
        # Start the slideshow thread if it's not already running
        if not hasattr(root, "slideshow_thread") or not slideshow_thread.is_alive():
            slideshow_thread = threading.Thread(target=slideshow_thread_func)
            slideshow_thread.daemon = True  # Allow the thread to be terminated when the program exits
            slideshow_thread.start()
    else:
        # Stop the slideshow thread
        slideshow_running = False
        if hasattr(root, "slideshow_thread") and slideshow_thread.is_alive():
            slideshow_thread.join()  # Wait for the thread to finish


root.bind("s", start_slideshow)


def load_all_images(event=None):
    global index_atual

    # Create a new GUI window for progress display
    progress_window = tk.Toplevel(root)
    progress_window.title("Loading Images Progress")
    progress_label = tk.Label(progress_window, text="Loading images... Please wait.")
    progress_label.pack(padx=10, pady=10)  # Adjust the values as needed

    total_images = len(files)
    start_time = time.time()
    loaded_count = 0

    for i in range(len(files)):
        if loaded_files.get(files[i]) is None:
            carrega(files[i])
            loaded_count += 1

        progress = (loaded_count / total_images) * 100
        current_time = time.time()
        elapsed_time = current_time - start_time

        if loaded_count > 0:
            avg_time_per_image = elapsed_time / loaded_count
            estimated_remaining_time = avg_time_per_image * (total_images - loaded_count)
        else:
            avg_time_per_image = 0
            estimated_remaining_time = 0

        if estimated_remaining_time > 60:
            estimated_remaining_time_text = str(
                f"Estimated Remaining Time: {estimated_remaining_time / 60:.2f} minutes")
        else:
            estimated_remaining_time_text = str(f"Estimated Remaining Time: {estimated_remaining_time:.1f} seconds")

        progress_label.config(text=f"Progress: {progress:.2f}%\n"
                                   f"Elapsed Time: {elapsed_time:.2f} seconds\n"
                                   f"Average Time per Image: {avg_time_per_image:.3f} seconds\n"
                                   f"{estimated_remaining_time_text}")
        progress_window.update()
    progress_window.destroy()  # Close the progress window when loading is complete


root.bind("l", load_all_images)


def load_some_images(event=None):
    global index_atual
    num_images = 20  # Number of images to be loaded
    allowed_time = 5  # Seconds to run the function for
    progress_window = tk.Toplevel(root)
    progress_window.title("Loading Images Progress")

    progress_label = tk.Label(progress_window, text="Loading images... Please wait.")
    progress_label.pack(padx=10, pady=10)  # Adjust the values as needed

    total_images = min(num_images, len(files))  # Limit to available files
    start_time = time.time()
    loaded_count = 0

    while (time.time() - start_time) < allowed_time:
        for i in range(total_images):
            if loaded_files.get(files[i]) is None:
                carrega(files[i])
                loaded_count += 1

            progress = (loaded_count / total_images) * 100
            current_time = time.time()
            elapsed_time = current_time - start_time

            progress_label.config(text=f"Elapsed Time: {elapsed_time:.2f} seconds\n"
                                       f"Loaded images: {loaded_count}\n")

            progress_window.update()
    progress_window.destroy()  # Close the progress window when loading is complete


root.bind("L", load_some_images)

root.mainloop()
print("fim")

# todo if sel is empty delete