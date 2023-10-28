import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from PIL.ExifTags import TAGS
import os
from copiador_de_arquivo import copia_arquivo
import time

# Inicializando as coisas globais chatas
root = tk.Tk()  # Create window
imagem_mostrada = tk.Label(root) #Label is the content of the GUI
imagem_mostrada.pack() #Loads the input set to the Label
index_atual = 0  # Qual o indice da imagem que esta sendo mostrada
# Setting up overall environment
root.title("Eu amo o Bernado")
root.state('zoomed')

#For file metadata. Creating a StringVar class
file_info_visible = True
file_info_text = tk.StringVar()
file_info_text.set("Nothing to display yet :)") # set the text
file_info_Lablel = tk.Label(root, textvariable=file_info_text, font=('Arial', 12))
file_info_Lablel.place(anchor= tk.NW)

def toggle_file_info(event):
    global file_info_visible
    file_info_visible = not file_info_visible
    if file_info_visible:
        file_info_Lablel.place(anchor=tk.NW)
    else:
        file_info_Lablel.place_forget()

# Import of configuration parameters
source_dir = 'C:\\Users\\glauc\\Desktop\\sel'
#source_dir = filedialog.askdirectory()
destination_dir = 'C:\\Users\\glauc\\Desktop\\sel'

valid_extensions = [".jpg", ".jpeg", ".png", ".gif", ".JPG"]  # Add any other image file extensions if necessary
files = [file for file in os.listdir(source_dir) if any(file.endswith(ext) for ext in valid_extensions)] # O nome das imagens
loaded_files = dict.fromkeys(files, None)           #Is this prelocating enought? Or does it need to be the same variable format?

def exif(filename, gettag):
    # global source_dir #Necessary?
    img = Image.open(os.path.join(source_dir, filename))
    try:
        exif_table = {}
        for k, v in img._getexif().items():
            tag = TAGS.get(k)
            exif_table[tag] = v
        #print(exif_table)
        return exif_table[gettag]
    except AttributeError:
        print(f"Error: Failed to extract exif tags from file {filename}")
    except KeyError:
        print(f"Info: Key 'Orientation' of {filename} was not found")
    return None

def carrega(filename):
    img = Image.open(os.path.join(source_dir, filename))

    # Rotate the image if it is in portrait orientation
    try:
        Orientation = exif(filename, "Orientation")
        if   Orientation == 8:
            img = img.rotate(90,  expand=True)
        elif Orientation == 3:
            img = img.rotate(180, expand=True)
        elif Orientation == 6:
            img = img.rotate(270, expand=True)
#    except AttributeError:
#        print(f"Error: Failed to extract exif tags from file {filename}")
    except KeyError:
        print(f"Info: Key 'Orientation' of {filename} was not found")

    # Fixing image aspect ratio to screen aspect ratio
    if True:
        # Get aspect ratio of the image
        aspect_ratio = img.width / img.height

        # Get the screen height and width
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Get the screen aspect ratio
        screen_aspect_ratio = screen_width / screen_height

        # Determine the new size for the image
        if aspect_ratio < screen_aspect_ratio:
            new_width = int(screen_height * aspect_ratio)
            new_height = screen_height
        else:
            new_width = screen_width
            new_height = int(screen_width / aspect_ratio)

        # Resize the image to the new size
        img = img.resize((new_width, new_height))

    return ImageTk.PhotoImage(img)

if True:  # So that code folding is possible
    def mostra_imagem(file):
        if file in loaded_files:
            imagem_mostrada['image'] = loaded_files[file]  # Mostrar a imagem selecionada na tela
            if file_info_visible:
                file_info_Lablel.place(anchor=tk.NW)
                metadata = [str(exif(file, tags)) for tags in
                            ["FocalLength", "FNumber", "ExposureTime", "ISOSpeedRatings", "ExposureBiasValue",
                             "ExposureProgram", "DateTime", "LensModel"]]
                metadata_label = ["FocalLength: ", "FNumber: ", "ExposureTime: 1/", "ISO-", "Exposure Bias: ",
                                  "Bracketing: ", "DateTime: ", "Lens: "]
                metadata = [x + y for x, y in zip(metadata_label, metadata)]
                file_info_text.set(metadata)  # Set the metadata for fileinfo Label
                file_info_text.set('\n'.join(metadata))
            else:
                file_info_Lablel.place_forget()
            root.update()                                   #Aparently this is not ideal performance, but is already an improvement
            root.title("Eu amo o Bernado - "+str(files[index_atual])+" - "+str(index_atual+1)+" of "+str(len(files)))

        else: #Debug info
            print("This didnt work. Info for debbug follows:")
            print(f"index_atual: {index_atual}")
            print(f"files[index_atual]: {files[index_atual]}")
            print(f"loaded_files[files[index_atual]] was not found")
            print("This are the available dictionary keys: ", loaded_files.keys())

        # Changing bg color when bracketing
        if True:
            try:
                img = Image.open(os.path.join(source_dir, file))
            except FileNotFoundError:
                print(f"Error: {file} not found")
                return
            except OSError as e:
                print(f"Error opening file: {e}")
                return
            try:
                ExposureMode = exif(file, "ExposureMode")
                if   ExposureMode == 0: root.configure(background="black")
                elif ExposureMode == 2: root.configure(background="gray")
            except KeyError:
                # Handle cases where the ExposureMode is not present in the exif data
                pass
        return


    def copiar(event):
        copia_arquivo(source_dir, files[index_atual], destination_dir)
        proxima(event)
        if loaded_files.get(files[(index_atual + 1)%len(files)] ) is None:
            loaded_files[files[index_atual+1]] = carrega(files[index_atual+1])
        return

    def proxima(event):
        global index_atual
        # Incrementa o index e mostra a proxima
        index_atual = (index_atual + 1) % len(files)  # Depois da ultima, volta pro começo
        mostra_imagem(files[index_atual])
        return

    def anterior(event):
        global index_atual
        index_atual = (index_atual - 1) % len(files)  # Depois da ultima, volta pro começo
        mostra_imagem(files[index_atual])
        return

    def right(event):
        proxima(event)
        if loaded_files.get(files[(index_atual + 1)%len(files)] ) is None:
            loaded_files[files[index_atual+1]] = carrega(files[index_atual+1])
        return

    def left(event):
        anterior(event)
        if loaded_files.get(files[(index_atual - 1) % len(files)]) is None:
            loaded_files[files[index_atual-1]] = carrega(files[index_atual-1])
        return

#Old
root.bind("<Up>",       copiar)
root.bind("<Right>",    right)
root.bind("<Left>",     left)

#New
root.bind("6",          right)
root.bind("4",          left)
root.bind("8",          copiar)
root.bind("i", toggle_file_info)

try:
    for file in files[0:2]:  # Carrega so as 2 primeiras imagens, pra ir mais rapido
        loaded_files[file] = carrega(file)
        try:
            loaded_files[file] = carrega(file)
        except:
            print(f"Error: File {file} not found in {source_dir}")
except:
    print(f"Error: Source {files} might have problematic structure")
    #loaded_files[file] = carrega(file)  # O indice do dicio (key) é o nome do arquivo (file) e a "definicao do dicio" é a saída de carrega(file)
    #comentei a linha acima e nao deu erro, acho q pode deletar

#location = os.path.join(source_dir, files[0])
#from exif import Image
#with open(location, 'rb') as image_file:
#    my_image = Image(image_file)
#my_image.list_all()
#print(my_image)

mostra_imagem(files[0])  # Inicializando a janela, com a primeira imagem
imagem_mostrada.pack() #Loads the input set to the Label
root.mainloop() # Fica escutando se algum evento aconteceu
# Qualquer coisa depois disso só roda dps q fechar a janela
print("fim")

#TODO
#Alt menu to change source dir
# files_to_load as an extract of files
#not crash when there is a folder
#Deal with ARW files
#raise a warning when dest dir doesnt exist
#cleanup warnings and timings
#overlay camera settings
#Implement option to hide bracketing
# Sort based on exposure?