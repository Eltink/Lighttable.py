import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk


class Ajudante:
    def __init__(self, debugging = False, enable_gui = True):
        self.copied_images      = []
        self.copied_files       = 0
        self.source_filepaths   = []
        self.total_files        = 0
        self.selection_images   = []

        self.database           = ""
        self.wanted_files       = []
        self.missing_images     = []

        self.debugging          = debugging
        self.attempts           = 0

        if enable_gui:
            self.root = tk.Tk()
            self.root.title("Image Copy Tool")
            # self.root.geometry("400x400")
            self.root.eval('tk::PlaceWindow . center')

            self.selecao_label = tk.Label(self.root, text="Selecao Folder:")
            self.selecao_label.pack()
            self.selecao_entry = tk.Entry(self.root)
            self.selecao_entry.pack()
            self.selecao_button = tk.Button(self.root, text="Browse", command=lambda: browse_folder(self.selecao_entry))
            self.selecao_button.pack()

            self.base_de_dados_label = tk.Label(self.root, text="Base de Dados Folder:")
            self.base_de_dados_label.pack()
            self.base_de_dados_entry = tk.Entry(self.root)
            self.base_de_dados_entry.pack()
            self.base_de_dados_button = tk.Button(self.root, text="Browse", command=lambda: browse_folder(self.base_de_dados_entry))
            self.base_de_dados_button.pack()

            self.formato_quero_label = tk.Label(self.root, text="Formato Quero (Default: .ARW):")
            self.formato_quero_label.pack()
            self.formato_quero_entry = tk.Entry(self.root)
            self.formato_quero_entry.pack()

            self.formato_tenho_label = tk.Label(self.root, text="Formato Tenho (Default: .JPG):")
            self.formato_tenho_label.pack()
            self.formato_tenho_entry = tk.Entry(self.root)
            self.formato_tenho_entry.pack()

            self.start_button = tk.Button(self.root, text="Start Copying", command=self.excecuter)
            self.start_button.pack()

            self.progress_var_label = tk.Label(self.root, text="Progress bar")
            self.progress_var_label.pack()
            self.progress_var = tk.DoubleVar()
            self.progress_var.set(0)
            self.progress_bar = ttk.Progressbar(self.root, variable=self.progress_var, maximum=100)
            self.progress_bar.pack()

            self.feedback_text = tk.StringVar()
            self.feedback_label = tk.Label(self.root, textvariable=self.feedback_text)
            self.feedback_label.pack()

            # Bind the Enter key (Return key) to the start_copying function
            self.root.bind('<Return>', self.excecuter)

        if debugging: self.excecuter()

        # start GUI
        if enable_gui: self.root.mainloop()

    def excecuter(self, event=None):
        self.get_user_input()

        self.copied_images = set(os.listdir(self.dest_dir))
        self.selection_images = set(self.wanted_files)
        self.total_files = len(self.wanted_files)

        self.file_finder()

        self.attempts += 1

        if self.copied_files == 0 and self.attempts < 2:
            self.database = os.path.dirname(self.database)  # If nothing is found, try with parent dir
            self.excecuter()  # Im kinda proud of this recursiveness
            self.attempts += 1

        self.closer()

    def get_user_input(self):
        if self.debugging:
            formato_quero = ".ARW"
            formato_tenho = ".JPG"
            selecao       = r"C:\Users\andre\Desktop\git\Glauco\Test_images\sel"
            self.database = r"C:\Users\andre\Desktop\git\Glauco\Test_images"
            if not self.database: self.database = self.base_de_dados_entry.get() # First try: inherit, then user input, then parent dir
            if not self.database: self.database = os.path.dirname(selecao) # If database entry is empty, try with selecao parent dir
        else:
            selecao = self.selecao_entry.get()
            if not self.database: self.database = self.base_de_dados_entry.get() # First try: inherit, then user input, then parent dir
            if not self.database: self.database = os.path.dirname(selecao) # If database entry is empty, try with selecao parent dir
            formato_quero = self.formato_quero_entry.get()
            formato_tenho = self.formato_tenho_entry.get()
            if not formato_quero: formato_quero = ".ARW" # Isnt this broken because of the start of the function?
            if not formato_tenho: formato_tenho = ".JPG"

        self.dest_dir = os.path.join(os.path.dirname(selecao), str(os.path.split(selecao)[-1]) + " copiadas")

        if not os.path.exists(self.dest_dir): os.makedirs(self.dest_dir)
        self.wanted_files = [file.replace(formato_tenho, formato_quero) for path, subdir, files in os.walk(selecao) for file in files]

    def file_finder(self):
        for path, subdir, files in os.walk(self.database):
            folder_name = os.path.split(path)[1]
            if "sel" in folder_name or "JPG" in folder_name : break #ignoring any /JPG and *sel folder
            for file in files:
                if file in self.wanted_files:
                    if path == os.path.join(self.database, "1010 sel copiadas"): return
                    self.file_copier(path, file)
                    self.root.update_idletasks()  # Updates only stuff like progress bar, not entire UI

        if len(self.copied_images)!= len(self.wanted_files): # This line checks if all images from sel were copied
            for wanted_file in self.wanted_files:
                if wanted_file not in self.copied_images and wanted_file not in self.missing_images: self.missing_images.append(wanted_file)
        if self.missing_images:
            self.feedback_text.set(f"Some images were not found in the base folder.\n"
                              f"Copied images: {self.copied_files}\n"
                              f"Missing files: {len(self.missing_images)}\n"
                              f"Failure rate: {100 * len(self.missing_images) / self.total_files}%")
        else:
            self.feedback_text.set(f"Copied {self.copied_files} of {self.total_files} images")

    def file_copier(self, path, file_name):
        source_filepath = os.path.join(path, file_name)
        if source_filepath == self.dest_dir: return

        try:
            shutil.copy(source_filepath, self.dest_dir)
            self.copied_images.add(file_name)
            self.source_filepaths.append(source_filepath)
            self.copied_files += 1

            progress = int((self.copied_files / self.total_files) * 100)
            self.progress_var.set(progress)

            self.feedback_text.set(f"Copied {self.copied_files} of {self.total_files} images")
            # self.root.update()
            self.root.update_idletasks()  # Updates only stuff like progress bar, not entire UI. Is this working here too?

        except Exception as e:
            # # self.feedback_text.set(self.feedback_text.get() + f"File {source_filepath} is wanted but could not be copied from {source_filepath} with error {e}.\n")
            print("Hey! Got this error:", e)

    def closer(self):
        # if self.debugging: return

        # Show missing images and completion messages in the GUI
        tk.messagebox.showinfo("Copying Complete", "Image copying process completed.\n"
                                                    f"Found {self.copied_files} of {self.total_files} images")

        # if self.missing_images: tk.messagebox.showinfo("Missing Images", str(self.missing_images))
        print(f"self.missing_images: {self.missing_images}")
        if self.missing_images: tk.messagebox.showinfo("Missing Images", '\n'.join(self.missing_images))

        # if self.missing_images:
        #     text = "Some images were not found in the base de dados.\n"
        #     text += f"Copied images: {self.copied_files}\n"
        #     text += f"Missing files: {len(self.missing_images)}\n"
        #     text += f"Fail rate: {100 * len(self.missing_images) / self.total_files}%\n"
        #     self.feedback_text.set(text)
        #
        # tk.messagebox.showinfo("nao_encontradas", str(self.missing_images))

        if not os.listdir(self.dest_dir): os.rmdir(self.dest_dir)

        # feedback_text for current status update, messagebox.showinfo to show images not found

def browse_folder(entry):
   folder_path = filedialog.askdirectory()
   entry.delete(0, tk.END)
   entry.insert(0, folder_path)

if __name__ == "__main__":
    debugging = True
    enable_gui = True
    ajudante = Ajudante(debugging, enable_gui)

# TODO fix wrong feedback info: number of missing images, filenames