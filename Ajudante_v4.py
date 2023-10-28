import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

# TODO improve closing message
# How many succesfull vs error
#

root = None
def copy_images(source_folder, destination_folder, base_de_dados, formato_quero, formato_tenho, progress_var, feedback_text):
    global root
    imagens_copiadas = set(os.listdir(destination_folder))

    nao_encontradas = []

    total_files = 0
    copied_files = 0

    for rootdir, _, files in os.walk(source_folder):
        total_files += len(files)

    for rootdir, _, files in os.walk(source_folder):
        for file in files:
            if formato_tenho in file:
                imagem_quero = file[:-len(formato_tenho)] + formato_quero
                caminho_imagem_base_de_dados = os.path.join(base_de_dados, imagem_quero)
                if imagem_quero not in imagens_copiadas:
                    if os.path.exists(caminho_imagem_base_de_dados):
                        shutil.copy(caminho_imagem_base_de_dados, destination_folder)
                        imagens_copiadas.add(imagem_quero)
                        copied_files += 1
                        progress = int((copied_files / total_files) * 100)
                        progress_var.set(progress)
                        feedback_text.set(f"Copied {copied_files} of {total_files} images")
                        root.update()
                    else:
                        nao_encontradas.append(imagem_quero)

    if nao_encontradas:
        text = "Some images were not found in the base de dados.\n"
        text += f"Copied images: {(copied_files)}\n"
        text += f"Missing files: {len(nao_encontradas)}\n"
        text += f"Fail rate: {100*len(nao_encontradas)/(total_files)}%\n"
        feedback_text.set(text)

    messagebox.showinfo("nao_encontradas", str(nao_encontradas))

    messagebox.showinfo("Copying Complete", "Image copying process completed.")

def browse_folder(entry):
    folder_path = filedialog.askdirectory()
    entry.delete(0, tk.END)
    entry.insert(0, folder_path)

def main():
    def start_copying():
        base_de_dados = base_de_dados_entry.get()
        selecao = selecao_entry.get()
        formato_quero = formato_quero_entry.get()
        formato_tenho = formato_tenho_entry.get()

        if not formato_quero:
            formato_quero = ".ARW"
        if not formato_tenho:
            formato_tenho = ".JPG"

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

    root.mainloop()

if __name__ == "__main__":
    main()
