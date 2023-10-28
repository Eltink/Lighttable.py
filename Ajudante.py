import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

# TODO fix missing_images as its using the imasges from database to throw an error, not images from selecao
# fix the definition of selecao?
# option to include subdirs or not?
# warning if database is too big?

debugging = 0
root = None
def copy_images(selection_folder, destination_folder, base_folder, target_format, source_format, progress_var, feedback_text):
    global root
    copied_images = set(os.listdir(destination_folder))
    selection_images = set(os.listdir(selection_folder))
    print(f"selection_images {selection_images}")
    missing_images = []

    total_files = sum(len(files) for _, _, files in os.walk(selection_folder))
    copied_files = 0

    for path, subdir, files in os.walk(base_folder):
        for file in files:
            if target_format in file:
                file_im_looking_for = file.replace(target_format, source_format)
                target_filepath = os.path.join(path, file)
                print("file_im_looking_for", file_im_looking_for)
                print("target_filepath", target_filepath)
                print(f"path {path}")
                print(f"file {file}")
                # print("file", file)
                print(f"file {file} in selection_images {selection_images} is {file in selection_images}")
                print("\n")
                if file_im_looking_for in selection_images:
                    try:
                        shutil.copy(target_filepath, destination_folder)
                        copied_images.add(file)
                        copied_files += 1

                        progress = int((copied_files / total_files) * 100)
                        progress_var.set(progress)

                        feedback_text.set(f"Copied {copied_files} of {total_files} images")
                    except Exception as e:
                        feedback_text.set(f"Error copying {target_filepath}: {str(e)}")
                        missing_images.append(file)

    print("missing_images", missing_images)
    if missing_images:
        feedback_text.set(
            f"Some images were not found in the base folder.\n"
            f"Copied images: {copied_files}\n"
            f"Missing files: {len(missing_images)}\n"
            f"Failure rate: {100 * len(missing_images) / total_files}%"
        )
    else: feedback_text.set(f"Copied {copied_files} of {total_files} images")

    if debugging: return
    # Show missing images and completion messages in the GUI
    messagebox.showinfo("Copying Complete", "Image copying process completed.\n"
                                            f"Copied {copied_files} of {total_files} images")
    if missing_images: messagebox.showinfo("Missing Images", str(missing_images))

def browse_folder(entry):
    folder_path = filedialog.askdirectory()
    entry.delete(0, tk.END)
    entry.insert(0, folder_path)

def main():
    def start_copying():
        global debugging

        base_de_dados = base_de_dados_entry.get()
        selecao = selecao_entry.get()
        formato_quero = formato_quero_entry.get()
        formato_tenho = formato_tenho_entry.get()

        if not formato_quero:
            formato_quero = ".ARW"
        if not formato_tenho:
            formato_tenho = ".JPG"
        if debugging:
            if not base_de_dados:
                base_de_dados = r"E:\Selecionar\2022_01_22_Festas parte 208"
            if not selecao:
                selecao = r"E:\Selecionar\2022_01_22_Festas parte 208\JPG sel"

        destino = os.path.join(selecao, "copiadas")

        if not os.path.exists(destino):
            os.makedirs(destino)

        progress_var.set(0)
        feedback_text.set("Copying images...")

        copy_images(selecao, destino, base_de_dados, formato_quero, formato_tenho, progress_var, feedback_text)

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
