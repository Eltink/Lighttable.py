import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

# TODO fix missing_images as its using the imasges from database to throw an error, not images from selecao
# fix the definition of selecao?
# option to include subdirs or not?
# warning if database is too big?

debugging = 1
root = None
def file_finder(database, dest_dir, wanted_files):
    global root
    global copied_images, copied_files, source_filepaths, missing_images, feedback_text, total_files, progress_var
    for path, subdir, files in os.walk(database):
        for file in files:
            if file in wanted_files:
                source_filepath = os.path.join(path, file)
                file_copier(source_filepath, dest_dir)

    if missing_images:
        feedback_text.set(f"Some images were not found in the base folder.\n"
                          f"Copied images: {copied_files}\n"
                          f"Missing files: {len(missing_images)}\n"
                          f"Failure rate: {100 * len(missing_images) / total_files}%")
    else: feedback_text.set(f"Copied {copied_files} of {total_files} images")

    if debugging: return
    # Show missing images and completion messages in the GUI
    messagebox.showinfo("Copying Complete", "Image copying process completed.\n"
                                            f"Copied {copied_files} of {total_files} images")
    if missing_images: messagebox.showinfo("Missing Images", str(missing_images))


def file_copier(source_filepath, dest_dir):
    global copied_images, copied_files, source_filepaths, missing_images, feedback_text, total_files, progress_var
    try:
        shutil.copy(source_filepath, dest_dir)
        copied_images.append(source_filepath)
        source_filepaths.append(source_filepath)
        copied_files += 1

        progress = int((copied_files / total_files) * 100)
        progress_var.set(progress)

        feedback_text.set(f"Copied {copied_files} of {total_files} images")

    except Exception as e:
        missing_images.append(source_filepath)
        feedback_text += f"File {source_filepath} is wanted but could not be copied from {source_filepath} with error {e}.\n"

def browse_folder(entry):
    folder_path = filedialog.askdirectory()
    entry.delete(0, tk.END)
    entry.insert(0, folder_path)

def main():
    def start_copying():
        global debugging
        global copied_images, copied_files, source_filepaths, missing_images, feedback_text, total_files, progress_var

        base_de_dados = base_de_dados_entry.get()
        selecao = selecao_entry.get()
        formato_quero = formato_quero_entry.get()
        formato_tenho = formato_tenho_entry.get()

        if not formato_quero: formato_quero = ".ARW"
        if not formato_tenho: formato_tenho = ".JPG"
        if debugging:
            if not base_de_dados: base_de_dados = r"E:\Selecionar\2022_01_22_Festas parte 208"
            if not selecao:       selecao =       r"E:\Selecionar\2022_01_22_Festas parte 208\JPG sel"

        destino = os.path.join(selecao, "copiadas")

        if not os.path.exists(destino): os.makedirs(destino)

        progress_var.set(0)
        feedback_text.set("Copying images...")

        wanted_files = [file.replace(formato_tenho, formato_quero) for file in os.listdir(selecao)]

        copied_images = set(os.listdir(destino))
        selection_images = set(wanted_files)
        missing_images = []

        total_files = len(wanted_files)
        copied_files = 0

        file_finder(base_de_dados, destino, wanted_files)

    global root
    root = tk.Tk()
    root.title("Image Copy Tool")
    root.geometry("400x400")
    root.eval('tk::PlaceWindow . center')

    base_de_dados_label = tk.Label(root, text="Base de Dados Folder:")
    base_de_dados_label.pack()
    base_de_dados_entry = tk.Entry(root)
    base_de_dados_entry.pack()
    base_de_dados_button = tk.Button(root, text="Browse", command=lambda: browse_folder(base_de_dados_entry))
    base_de_dados_button.pack()

    selecao_label = tk.Label(root, text="Selecao Folder:")
    selecao_label.pack()
    selecao_entry = tk.Entry(root)
    selecao_entry.pack()
    selecao_button = tk.Button(root, text="Browse", command=lambda: browse_folder(selecao_entry))
    selecao_button.pack()

    formato_quero_label = tk.Label(root, text="Formato Quero (Default: .ARW):")
    formato_quero_label.pack()
    formato_quero_entry = tk.Entry(root)
    formato_quero_entry.pack()

    formato_tenho_label = tk.Label(root, text="Formato Tenho (Default: .JPG):")
    formato_tenho_label.pack()
    formato_tenho_entry = tk.Entry(root)
    formato_tenho_entry.pack()

    start_button = tk.Button(root, text="Start Copying", command=start_copying)
    start_button.pack()

    progress_var_label = tk.Label(root, text="Progress bar")
    progress_var_label.pack()
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
    progress_bar.pack()

    feedback_text = tk.StringVar()
    feedback_label = tk.Label(root, textvariable=feedback_text)
    feedback_label.pack()

    if debugging: start_copying()

    root.mainloop()

if __name__ == "__main__":
    main()

