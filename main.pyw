import time
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk, ImageOps # ImageOps to handle rotation from EXIF
from PIL.ExifTags import TAGS
from pillow_heif import register_heif_opener
import os
import ctypes
# import rawpy # Necessary to read .arw files
import imageio # Necessary to read .arw files
import threading
import subprocess
import Ajudante

import brackets_sorter
from copiador_de_arquivo import copia_arquivo
from tools import *

debugging = 0
timing = 1
show_all = 0
include_sub_dirs = 1
slideshow_delay = 3.0

# Initialize the GUI
root = tk.Tk()
imagem_mostrada = tk.Label(root)
imagem_mostrada.pack()
index_atual = 0
register_heif_opener() # Register the HEIF opener with Pillow so Image.open() knows how to handle .HEIC

# Grab the initial source_dir
clipboard_getter = tk.Tk()
try: clipboard = clipboard_getter.clipboard_get()
except: clipboard = ""
clipboard_getter.update_idletasks()
clipboard_getter.destroy()

if os.path.exists(clipboard):   source_dir = clipboard
elif debugging:                 source_dir = r"C:\Users\glauc\Desktop\BK limpando 128 JPG\2025_06_17_España\21650622"
else:                           source_dir = filedialog.askdirectory()

# Set up the window
root.title("Eu amo o Bernado")
root.state('zoomed')
root.configure(background="black")

# root.after(1, lambda: root.attributes("-topmost", True))
# root.after(1, lambda: root.focus_force())

# root.lift()
# root.attributes("-topmost", True)
# root.after(1000, lambda: root.attributes("-topmost", False))
# ctypes.windll.user32.SetForegroundWindow(root.winfo_id())

# Set up the file information display
file_info_visible = True
file_info_text = tk.StringVar()
file_info_text.set("init")
file_info_label = tk.Label(root, textvariable=file_info_text, font=('Arial', 12))

feedback_label_text = tk.StringVar()
feedback_label_text.set(" ")
feedback_label = tk.Label(root, textvariable=feedback_label_text, font=('Arial', 12))
feedback_label.place(y=200, anchor=tk.NW)

bracketed_info_text = tk.StringVar()
bracketed_info_text.set(" ")
bracketed_info_label = tk.Label(root, textvariable=bracketed_info_text, font=('Arial', 12))
bracketed_info_label.place(y=400, anchor=tk.NW)

# Toggle file information display
def toggle_file_info(event):
    global file_info_visible
    file_info_visible = not file_info_visible
    if file_info_visible:   file_info_label.place(anchor=tk.NW)
    else:                   file_info_label.place_forget()

destination_dir = get_destination_dir(source_dir)
valid_extensions = [".JPG", ".jpg", ".jpeg", ".png", ".HEIC"]  # ".ARW" can be tested if needed
loaded_files = {}
copied_files = {}

def carrega(filepath):
    if loaded_files.get(filepath) is not None: return  # Already loaded
    if filepath.endswith('.ARW'): pass  # placeholder for rawpy logic
    else:
        try: img = Image.open(filepath)
        except Exception as e:
            print(f"Could not open file {filepath}: {e}")
            return
    # Handle EXIF orientation
    # try:
    #     orientation = get_exif(filepath, "Orientation")
    #     if orientation == 8:    img = img.rotate(90, expand=True)
    #     elif orientation == 3:  img = img.rotate(180, expand=True)
    #     elif orientation == 6:  img = img.rotate(270, expand=True)
    # except Exception as e:      print(f"An error occurred on loading file {filepath}: {e}")
    img = ImageOps.exif_transpose(img) # Handle EXIF orientation

    aspect_ratio = img.width / img.height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    screen_aspect_ratio = screen_width / screen_height

    if aspect_ratio < screen_aspect_ratio:
        img =   img.resize((int(screen_height * aspect_ratio), screen_height), Image.HAMMING) # https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-filters
    else: img = img.resize((screen_width, int(screen_width / aspect_ratio)), Image.HAMMING)

    loaded_files[filepath] = ImageTk.PhotoImage(img)  # Converting the image from PIL to TK format

def get_image_metadata(filepath):
    metadata_tags =   ["FocalLengthIn35mmFilm",   "FNumber",   "ExposureTime",   "ISOSpeedRatings", "ExposureBiasValue", "ExposureMode",    "DateTime",   "LensModel"]
    metadata_labels = ["FocalLength: ",         "FNumber: ", "ExposureTime: ", "ISO-",            "Exposure Bias: ",   "Exposure Mode: ", "DateTime: ", "Lens: "]
    try:
        metadata_values = [str(get_exif(filepath, tag)) for tag in metadata_tags]
        # Format exposure time
        if metadata_values[2] and metadata_values[2] != "None":
            try:
                float_val = float(metadata_values[2])
                if float_val < 1:
                    metadata_values[2] = str(round(1 / float_val)) + "s"
                    metadata_labels[2] += " 1/"
                else: metadata_values[2] = str(round(float_val)) + "s"
            except: pass

        # Format exposure mode
        if metadata_values[5] == "0":   metadata_values[5] = "Single"
        elif metadata_values[5] == "2": metadata_values[5] = "Bracketing"
        else:                           metadata_values[5] = str(metadata_values[5]) + " (unknown case)"

        formatted_metadata = []
        for label, value in zip(metadata_labels, metadata_values):
            if value and value != "None":
                formatted_metadata.append(label + value)
        return '\n'.join(formatted_metadata)
    except Exception as e:
        print(f"An error occurred getting metadata from file {filepath}: {e}")
        return None

def mostra_imagem(filepath):
    global index_atual, bracketed_info_text
    if filepath in loaded_files:
        imagem_mostrada['image'] = loaded_files[filepath]
        if file_info_visible:
            file_info_label.place(anchor=tk.NW)
            metadata = get_image_metadata(filepath)
            if metadata:    file_info_text.set(metadata)
            else:           file_info_text.set("No EXIF")
        else:               file_info_label.place_forget()
        # temp = get_exif(filepath, "ExposureMode")
        bracketed_info_text.set("Bracketed" if get_exif(filepath, "ExposureMode") == 2 else "")
        root.update()
        root.title(f"Eu amo o Bernado - {filepath} - {index_atual + 1} of {len(filepaths)}")
    else:   print(f"File {filepath} not found in loaded_files.")

# We'll define a function to rebuild the file list based on show_all/include_sub_dirs
filepaths = []

def reload_filepaths(event=None):
    global filepaths, loaded_files, index_atual, show_all, include_sub_dirs
    # Clear old loaded files
    loaded_files.clear()

    # Recalculate filepaths based on include_sub_dirs
    if include_sub_dirs == 0:
        # no subdirectories
        filepaths = [os.path.join(source_dir, file) for file in os.listdir(source_dir) if any(file.endswith(ext) for ext in valid_extensions)]
    else:
        # with subdirectories
        temp_list = []
        for path, subdir, files_in_dir in os.walk(source_dir):
            for file in files_in_dir:
                if any(file.endswith(ext) for ext in valid_extensions): temp_list.append(os.path.join(path, file))
        filepaths = temp_list

    # If no images found, show message
    if len(filepaths) == 0: messagebox.showinfo("Folder error", "No valid images were found")

    # If show_all == 0, use bracket logic, else we show them all
    if show_all == 0:
        showable = is_it_showable(filepaths)
        filepaths[:] = [fp for fp, is_sh in zip(filepaths, showable) if is_sh]

    # Reinitialize loaded_files for the updated file list
    loaded_files = dict.fromkeys(filepaths, None)

    # Reset index
    index_atual = 0
    if filepaths:
        carrega(filepaths[0])
        mostra_imagem(filepaths[0])
        if len(filepaths) > 1:
            carrega(filepaths[1])
clipboard_getter = None

t1 = time.time()
reload_filepaths()  # Build the initial list of filepaths
files = filepaths.copy()  # For reference, though we actually use filepaths all over

if timing:  print("Time to calculate showable: ", time.time() - t1)

# Event handlers

def copiar(event):
    global index_atual
    if not filepaths:   return
    filepath = filepaths[index_atual]
    if filepath in copied_files:    feedback_label_text.set("Already copied")
    else:
        copia_arquivo(source_dir, filepath, destination_dir)
        copied_files[filepath] = True
        if get_exif(filepath, "ExposureMode") != 2:
            feedback_label_text.set(f"Copied: {index_atual + 1}")
        else:
            feedback_label_text.set(f"Copied: median {filepath}")
            EV = get_exif(filepath, "ExposureBiasValue")
            if not EV:  EV = 0  # fallback
            try:        EV = float(EV)
            except:     EV = 0

            darker = file_navigator(filepath, -1)
            if round(float(get_exif(darker, "ExposureBiasValue") or 0), 1) in [EV - 3, EV - 2, EV - 1]:
                copia_arquivo(source_dir, darker, destination_dir)
                feedback_label_text.set(feedback_label_text.get() + " and darker")
            else:
                feedback_label_text.set(feedback_label_text.get() + " but no darker")

            lighter = file_navigator(filepath, +1)
            if round(float(get_exif(lighter, "ExposureBiasValue") or 0), 1) in [EV + 3, EV + 2, EV + 1]:
                copia_arquivo(source_dir, lighter, destination_dir)
                feedback_label_text.set(feedback_label_text.get() + " and lighter")
            else:
                feedback_label_text.set(feedback_label_text.get() + " but no lighter")

            if feedback_label_text.get().endswith("and darker and lighter"):
                feedback_label_text.set(f"Copied: 3x {index_atual + 1}")

    right(event)

def proxima(event):
    global index_atual
    if not filepaths: return
    index_atual = (index_atual + 1) % len(filepaths)
    mostra_imagem(filepaths[index_atual])

def anterior(event):
    global index_atual
    if not filepaths: return
    index_atual = (index_atual - 1) % len(filepaths)
    mostra_imagem(filepaths[index_atual])

def right(event):
    proxima(event)
    if len(filepaths) > 1:
        next_idx = (index_atual + 1) % len(filepaths)
        if loaded_files.get(filepaths[next_idx]) is None:
            carrega(filepaths[next_idx])

def left(event):
    anterior(event)
    if len(filepaths) > 1:
        prev_idx = (index_atual - 1) % len(filepaths)
        if loaded_files.get(filepaths[prev_idx]) is None:
            carrega(filepaths[prev_idx])

def exit_feedback(event):
    if not copied_files:
        root.destroy()
        return

    def get_total_size(path):
        total_size = 0
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isfile(item_path):
                total_size += os.path.getsize(item_path)
            elif os.path.isdir(item_path):
                total_size += get_total_size(item_path)
        return total_size

    source_size = get_total_size(source_dir) / (1024 ** 3)
    destination_size = get_total_size(destination_dir) / (1024 ** 3)
    messagebox.showinfo("Copying Complete",
                        f"Image copying process completed.\n"\
                        f"Copied files: {len(copied_files)}\n"\
                        f"Keep rate = {100 * len(copied_files) / len(filepaths):.2f}%\n"\
                        f"Total time = {time.time() - t1:.2f} seconds\n"\
                        f"Time per 1k image = {1000 * len(filepaths) / (time.time() - t1):.2f} mHz bzw mFPS\n\n"\
                        f"Original - final = saving\n "\
                        f"{source_size:.0f} - {destination_size:.0f} = {(source_size - destination_size):.0f} GB\n\n"\
                        f"Press Enter to close")
    root.destroy()

# Bind keys to event handlers
root.bind("<Up>", copiar)
root.bind("<Right>", right)
root.bind("<Left>", left)
root.bind("6", right)
root.bind("4", left)
root.bind("8", copiar)
root.bind("i", toggle_file_info)
root.bind("<Control-q>", exit_feedback)
root.bind("<Control-R>", reload_filepaths)


def copy_rejected(event=None):
    if not filepaths:   return
    # join parent dir of source with folder name of source + rejected
    rejected_dir = os.path.join(os.path.dirname(source_dir), os.path.basename(source_dir)+" anti sel")
    print(f"rejected_dir {rejected_dir}")
    if not os.path.exists(rejected_dir): os.makedirs(rejected_dir)

    files_from_destdir = set(os.listdir(destination_dir)) # This includes manual copies, but doesn't deal well with brackets
    for root, _, files in os.walk(source_dir):
        for name in files:
            if name in files_from_destdir: continue             # If this filename is already in the selection folder, skip it
            full_path = os.path.join(root, name)                # Full path of the original file
            copia_arquivo(source_dir, full_path, rejected_dir)  # Copy it to the "anti sel" folder
            feedback_label_text.set(f"Copied: {full_path} to anti sel")
root.bind("<Control-x>", copy_rejected)

def open_in_explorer(event=None):
    if not filepaths: return
    run_arg = r'explorer /select, "' + filepaths[index_atual] + '"'
    subprocess.run(run_arg)

root.bind("<Control-r>", open_in_explorer)
open_in_explorer_button = tk.Button(root, text="Open in Explorer", command=open_in_explorer)
open_in_explorer_button.pack()

def open_with_photos(_=None):
    if not filepaths:
        return
    file_path = filepaths[index_atual]
    os.system(f'start "" "{file_path}"')

root.bind("<Control-e>", open_with_photos)

slideshow_event = threading.Event()
slideshow_thread = None
slideshow_running = False

def start_slideshow(event=None):
    global index_atual, slideshow_running, slideshow_thread, slideshow_delay
    slideshow_running = not slideshow_running

    def slideshow_thread_func():
        global index_atual
        while slideshow_running and filepaths:
            right(event)
            time.sleep(slideshow_delay)

    if slideshow_running:
        if not (slideshow_thread and slideshow_thread.is_alive()):
            slideshow_thread = threading.Thread(target=slideshow_thread_func)
            slideshow_thread.daemon = True
            slideshow_thread.start()
            # Todo include label "slideshow running: 3s"
    else:
        slideshow_running = False
        if slideshow_thread and slideshow_thread.is_alive():
            slideshow_thread.join()

root.bind("s", start_slideshow)

loading_in_progress = False
loading_thread = None
loaded_count = 0
stop_loading_event = threading.Event() # Event to signal the loading thread to stop

def load_all_images(event=None):
    global index_atual, loading_in_progress, loading_thread, loaded_count

    if loading_thread and loading_thread.is_alive():
        stop_loading_event.set()            # Signal the loading thread to stop
        stop_loading_event.clear()          # Clear the event for the next loading
        loading_thread.join(timeout=0.01)   # Wait a short while for the thread to respond to the stop command
        loading_in_progress = False
        loading_thread = None
    else:
        loaded_count = 0
        loading_in_progress = True

        progress_window = tk.Toplevel(root)
        progress_window.title("Loading Images Progress")
        progress_label = tk.Label(progress_window, text="Loading images... Please wait.")
        progress_label.pack(padx=10, pady=10)

        total_images = len(filepaths)
        start_time = time.time()

        def loading_thread_func():
            global index_atual, loading_in_progress, loading_thread, loaded_count
            for i in range(loaded_count, len(filepaths)):
                if stop_loading_event.is_set() or not loading_in_progress:
                    # If the event is set or loading was manually stopped, interrupt the loading process
                    break

                if loaded_files.get(filepaths[i]) is None:
                    carrega(filepaths[i])
                    loaded_count += 1

                progress = (loaded_count / total_images) * 100
                current_time = time.time()
                elapsed_time = current_time - start_time

                if loaded_count > 0:
                    avg_time_per_image = round(elapsed_time / loaded_count, 2)
                    estimated_remaining_time = avg_time_per_image * (total_images - loaded_count)
                else:
                    avg_time_per_image = 0
                    estimated_remaining_time = 0

                if estimated_remaining_time < 60:
                    ert_text = f"Remaining: {estimated_remaining_time:.0f} seconds"
                else:
                    ert_text = f"Remaining: {estimated_remaining_time / 60:.1f} minutes"

                progress_label.config(
                    text=f"Progress: {progress:.2f}%\n"\
                         f"Time per Image: {avg_time_per_image:.3f} seconds\n"\
                         f"{ert_text}")

                progress_window.update()

            loading_in_progress = False  # Reset the flag when loading is complete
            progress_window.destroy()    # Close the progress window when loading is complete

        loading_thread = threading.Thread(target=loading_thread_func)
        loading_thread.start()

root.bind("l", load_all_images)

def load_some_images(event=None):
    global index_atual, loaded_files
    allowed_time = 5
    progress_window = tk.Toplevel(root)
    progress_window.title("Loading Images Progress")
    progress_label = tk.Label(progress_window, text="Loading images... Please wait.")
    progress_label.pack(padx=80, pady=20)

    total_images = len(filepaths)
    start_time = time.time()
    loaded_count_local = 0

    while (time.time() - start_time) < allowed_time and loaded_count_local < total_images:
        i = (index_atual + loaded_count_local) % len(filepaths)
        if loaded_files.get(filepaths[i]) is None:
            carrega(filepaths[i])
        loaded_count_local += 1

        current_time = time.time()
        elapsed_time = current_time - start_time
        progress_label.config(text= f"Elapsed Time: {elapsed_time:.2f} seconds\n"
                                    f"Loaded images: {loaded_count_local}\n")
        progress_window.update()

    progress_window.destroy()

root.bind("L", load_some_images)

def callAjudante(_=None):
    ajudante = Ajudante.Ajudante(debugging=False, enable_gui=True)
    ajudante.database = os.path.dirname(os.path.dirname(destination_dir))
    selecao = destination_dir  # selecao for ajudante is where main is putting the files (dest)
    ajudante.selecao_entry.insert(0, "test")
    ajudante.selecao_entry.set(0, "test")
    ajudante.formato_quero = ".ARW"
    ajudante.formato_tenho = ".JPG"
    ajudante.dest_dir = os.path.join(selecao, "copiadas")
    if not os.path.exists(ajudante.dest_dir): os.makedirs(ajudante.dest_dir)
    ajudante.wanted_files = [file.replace(ajudante.formato_tenho, ajudante.formato_quero)
                             for path, subdir, files_ in os.walk(selecao)
                             for file in files_]

    ajudante.copied_images      = set(os.listdir(ajudante.dest_dir))
    ajudante.selection_images   = set(ajudante.wanted_files)
    ajudante.total_files        = len(ajudante.wanted_files)

    ajudante.root.update()

    # ajudante.file_finder()

root.bind("<Control-s>", callAjudante)

###############################################
# Menu / Settings window code for changing show_all, include_sub_dirs, and slideshow_delay
###############################################

settings_window = None

def open_settings_window():
    global settings_window
    if settings_window and tk.Toplevel.winfo_exists(settings_window):
        settings_window.focus()
        return

    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")

    bool_var_show_all   = tk.BooleanVar(value=bool(show_all))
    bool_var_sub_dirs   = tk.BooleanVar(value=bool(include_sub_dirs))
    double_var_delay    = tk.DoubleVar(value=float(slideshow_delay))

    def apply_settings():
        global show_all, include_sub_dirs, slideshow_delay
        show_all = 1 if bool_var_show_all.get() else 0
        include_sub_dirs = 1 if bool_var_sub_dirs.get() else 0
        slideshow_delay = double_var_delay.get()
        reload_filepaths()

    tk.Checkbutton(settings_window, text="Show All", variable=bool_var_show_all).pack(anchor=tk.W, padx=10, pady=5)
    tk.Checkbutton(settings_window, text="Include Subdirectories", variable=bool_var_sub_dirs).pack(anchor=tk.W, padx=10, pady=5)

    tk.Label(settings_window, text="Slideshow delay (seconds)").pack(anchor=tk.W, padx=10)
    spin_delay = tk.Spinbox(settings_window, from_=0.01, to=60.0, increment=0.5, textvariable=double_var_delay)
    spin_delay.pack(anchor=tk.W, padx=10, pady=5)

    btn_apply = tk.Button(settings_window, text="Apply", command=apply_settings)
    btn_apply.pack(pady=10)

    settings_window.resizable(False, False)

menu_bar = tk.Menu(root)

# settings_menu = tk.Menu(menu_bar, tearoff=0)
# settings_menu.add_command(label="Open Settings Window", command=open_settings_window)
# menu_bar.add_cascade(label="Settings", menu=settings_menu)
# root.config(menu=menu_bar)
# Do i need this?

root.bind_all("<Alt-s>", lambda e: open_settings_window())

def show_histogram(event=None):
    if not filepaths: return
    filepath = filepaths[index_atual]
    img = Image.open(filepath)
    # Get histogram data (all channels concatenated)
    histogram = img.convert("L").histogram()
    import matplotlib.pyplot as plt
    plt.figure("Histogram")
    plt.plot(histogram)
    plt.title("Image Brightness Histogram")
    plt.xlabel("Pixel value")
    plt.ylabel("Frequency")
    plt.show()

root.bind("<Control-h>", show_histogram)

def go_to_image(event=None):
    global index_atual
    if not filepaths: return
    total_images = len(filepaths)
    target_index_str = simpledialog.askstring("Go To Image", f"Enter image number (1-{total_images}):", parent=root)
    if target_index_str:
        try:
            target_index = int(target_index_str) - 1 # User inputs 1-based index
            if 0 <= target_index < total_images:
                index_atual = target_index
                mostra_imagem(filepaths[index_atual])
                # Preload next/previous for smoother navigation
                if len(filepaths) > 1:
                    next_idx = (index_atual + 1) % total_images
                    prev_idx = (index_atual - 1) % total_images
                    if loaded_files.get(filepaths[next_idx]) is None:
                        carrega(filepaths[next_idx])
                    if loaded_files.get(filepaths[prev_idx]) is None:
                        carrega(filepaths[prev_idx])
            else:
                messagebox.showerror("Invalid Input", f"Please enter a number between 1 and {total_images}.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number.")
root.bind("<Control-g>", go_to_image)

menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# --- File Menu ---
file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu, underline=0) # Alt+F
# Add command to change source directory (optional, needs implementation)
# file_menu.add_command(label="Open Folder...", command=lambda: print("TODO: Implement Open Folder"))
file_menu.add_command(label="Open in Explorer", command=open_in_explorer, accelerator="Ctrl+E", underline=7) # Alt+F, E
file_menu.add_command(label="Open with Photos", command=open_with_photos, accelerator="Ctrl+R", underline=10) # Alt+F, P
file_menu.add_separator()
file_menu.add_command(label="Copy File(s)", command=copiar, accelerator="Up / 8", underline=0) # Alt+F, C
file_menu.add_separator()
file_menu.add_command(label="Exit", command=exit_feedback, accelerator="Ctrl+Q", underline=1) # Alt+F, x

# --- View Menu ---
view_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="View", menu=view_menu, underline=0) # Alt+V
view_menu.add_command(label="Next Image", command=right, accelerator="Right / 6", underline=0) # Alt+V, N
view_menu.add_command(label="Previous Image", command=left, accelerator="Left / 4", underline=0) # Alt+V, P
view_menu.add_command(label="Go To...", command=go_to_image, accelerator="Ctrl+G", underline=0) # Alt+V, G
view_menu.add_separator()
view_menu.add_command(label="Toggle File Info", command=toggle_file_info, accelerator="i", underline=7) # Alt+V, I
view_menu.add_command(label="Show Histogram", command=show_histogram, accelerator="Ctrl+H", underline=5) # Alt+V, H
view_menu.add_separator()
view_menu.add_command(label="Start/Stop Slideshow", command=start_slideshow, accelerator="s", underline=0) # Alt+V, S
view_menu.add_separator()
view_menu.add_command(label="Settings...", command=open_settings_window, underline=0) # Alt+V, t

# --- Tools Menu ---
tools_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Tools", menu=tools_menu, underline=0) # Alt+T
tools_menu.add_command(label="Load All Images", command=load_all_images, accelerator="L", underline=5) # Alt+T, A
tools_menu.add_command(label="Load Some Images", command=load_some_images, accelerator="Shift+L", underline=5) # Alt+T, S
tools_menu.add_separator()
tools_menu.add_command(label="Run Helper (Ajudante)", command=callAjudante, accelerator="Ctrl+S", underline=4) # Alt+T, H

if timing:  print("Time to reach mainloop: ", time.time() - t1)

root.mainloop()

print("fim")

if not os.listdir(destination_dir):
    os.rmdir(destination_dir)
