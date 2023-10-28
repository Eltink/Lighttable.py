import tkinter as tk
from PIL import ImageTk, Image
import os
from copiador_de_arquivo import copia_arquivo

class ImageViewer:
    def __init__(self, root):
        self.root = root
        self.image_label = tk.Label(root)
        self.file_info_text = tk.StringVar()
        self.loaded_files = {}
        self.index_atual = 0
        self.source_dir = 'C:\\Users\\glauc\\Desktop\\sel'
        self.destination_dir = 'C:\\Users\\glauc\\Desktop\\sel'
        self.valid_extensions = [".jpg", ".jpeg", ".png", ".gif", ".JPG"]
        self.zoom_factor = 1.0

    def setup_gui(self):
        self.root.title("Eu amo o Bernado")
        self.root.state('zoomed')

        file_info_label = tk.Label(self.root, textvariable=self.file_info_text, font=('Arial', 12))
        file_info_label.place(anchor=tk.NW)

        self.root.bind("6", self.next_image)
        self.root.bind("4", self.previous_image)
        self.root.bind("8", self.copy_image)
        self.root.bind("<MouseWheel>", self.zoom_image)

    def run(self):
        self.load_images()
        self.display_image(self.index_atual)
        self.root.mainloop()

    def load_images(self):
        files = [file for file in os.listdir(self.source_dir) if any(file.endswith(ext) for ext in self.valid_extensions)]
        for file in files:
            try:
                self.loaded_files[file] = self.load_image(file)
            except FileNotFoundError:
                print(f"Error: File {file} not found in {self.source_dir}")
        if not self.loaded_files:
            messagebox.showinfo("No Images Found", "No valid image files found in the source directory.")

    def load_image(self, filename):
        img = Image.open(os.path.join(self.source_dir, filename))
        return ImageTk.PhotoImage(img)

    def display_image(self, index):
        filenames = list(self.loaded_files.keys())
        if index >= 0 and index < len(filenames):
            filename = filenames[index]
            img = self.loaded_files[filename]
            width = int(img.width() * self.zoom_factor)
            height = int(img.height() * self.zoom_factor)
            img = img.resize((width, height))
            self.image_label.config(image=img)
            self.image_label.image = img  # Keep a reference to prevent garbage collection
            metadata = [str(self.get_exif(filename, tag)) for tag in
                        ["FocalLength", "FNumber", "ExposureTime", "ISOSpeedRatings", "ExposureBiasValue",
                         "ExposureProgram", "DateTime", "LensModel"]]
            metadata_labels = ["FocalLength: ", "FNumber: ", "ExposureTime: 1/", "ISO-", "Exposure Bias: ",
                               "Bracketing: ", "DateTime: ", "Lens: "]
            metadata_text = "\n".join(label + data for label, data in zip(metadata_labels, metadata))
            self.file_info_text.set(metadata_text)
            self.root.update()
            self.root.title(f"Eu amo o Bernado - {filename} - {index + 1} of {len(self.loaded_files)}")
        else:
            messagebox.showinfo("Image Not Found", f"The image '{filename}' was not found in the loaded files.")

    def get_exif(self, filename, tag):
        img = Image.open(os.path.join(self.source_dir, filename))
        try:
            exif_table = {}
            for k, v in img._getexif().items():
                exif_tag = ExifTags.TAGS.get(k)
                exif_table[exif_tag] = v
            return exif_table.get(tag)
        except AttributeError:
            print(f"Error: Failed to extract exif tags from file {filename}")
        except KeyError:
            print(f"Info: Key 'Orientation' of {filename} was not found")
        return None

    def copy_image(self, event):
        if self.index_atual >= 0 and self.index_atual < len(self.loaded_files):
            filename = list(self.loaded_files.keys())[self.index_atual]
            copia_arquivo(self.source_dir, filename, self.destination_dir)
            self.next_image(event)
        else:
            messagebox.showinfo("Invalid Image", "No image selected to copy.")

    def next_image(self, event):
        self.index_atual = (self.index_atual + 1) % len(self.loaded_files)
        self.display_image(self.index_atual)

    def previous_image(self, event):
        self.index_atual = (self.index_atual - 1) % len(self.loaded_files)
        self.display_image(self.index_atual)

    def zoom_image(self, event):
        if event.delta > 0:
            self.zoom_factor *= 1.2  # Increase zoom factor by 20%
        else:
            self.zoom_factor /= 1.2  # Decrease zoom factor by 20%
        self.display_image(self.index_atual)

if __name__ == "__main__":
    root = tk.Tk()
    image_viewer = ImageViewer(root)
    image_viewer.setup_gui()
    image_viewer.run()
