import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from PIL.ExifTags import TAGS
import os
from copiador_de_arquivo import copia_arquivo
import time

# Inicializando as coisas globais chatas
root = tk.Tk()  # Create window
imagem_mostrada = tk.Label(root)
index_atual = 0  # Qual o indice da imagem que esta sendo mostrada

source_dir = filedialog.askdirectory()

# Import of configuration parameters
#source_dir = 'C:\\Users\\glauc\\Desktop\\sel'
destination_dir = 'C:\\Users\\glauc\\Desktop\\sel'

files = os.listdir(source_dir)  # O nome das imagens
loaded_files = dict.fromkeys(files, None)           #Is this prelocating enought? Or does it need to be the same variable format?

# def carrega(filename):
#     img = Image.open(os.path.join(source_dir, filename))                    # Arquivo de origem(src+filename)
#     img = img.resize((root.winfo_screenwidth(), root.winfo_screenheight())) # Faz a imagem preencher a tela, nem mais nem menos
#     return ImageTk.PhotoImage(img)                                          # Mostrar a imagem selecionada na tela

def carrega(filename):
    img = Image.open(os.path.join(source_dir, filename))
    exif_table = {}
    for k, v in img._getexif().items():
        tag = TAGS.get(k)
        exif_table[tag] = v
    #print(exif_table)
    if exif_table["Orientation"] == 8:
        img = img.rotate(90, expand=True)
        # Rotate the image if it is in portrait orientation
    elif exif_table["Orientation"] == 6:
        img = img.rotate(270, expand=True)
        # Rotate the image if it is in portrait orientation
    elif exif_table["Orientation"] == 3:
        img = img.rotate(180, expand=True)
        # Rotate the image if it is in portrait orientation

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


for file in files[0:2]:                 # Carrega so as 2 primeiras imagens, pra ir mais rapido
    loaded_files[file] = carrega(file)  # O indice do dicio (key) é o nome do arquivo (file) e a "definicao do dicio" é a saída de carrega(file)

if True: # So that code folding is possible
    def mostra_imagem(file):
        if file in loaded_files:
            imagem_mostrada['image'] = loaded_files[file]  # Mostrar a imagem selecionada na tela
            root.update()                                   #Aparently this is not ideal performance, but is already an improvement
            root.title("Eu amo o Bernado - " + str(files[index_atual]) + " - " + str(index_atual+1) + " of " + str(len(files)))
        else:
            print("This didnt work. Info for debbug follows:")
            print(f"index_atual: {index_atual}")
            print(f"files[index_atual]: {files[index_atual]}")
            print(f"loaded_files[files[index_atual]] was not found")
            print("This are the available dictionary keys: ", loaded_files.keys())

        if True: #Changing bg color when bracketing
            img = Image.open(os.path.join(source_dir, file))
            exif_table = {}
            for k, v in img._getexif().items():
                tag = TAGS.get(k)
                exif_table[tag] = v
            if exif_table["ExposureMode"] == 0:
                root.configure(background="black")
                #print(file, "is not braketed")
            elif exif_table["ExposureMode"] == 2:
                root.configure(background="gray")
                #print(file, "is braketed")
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
        t = time.time()
        proxima(event)
        #print(time.time()-t, "s para proxima")
        t = time.time()
        if loaded_files.get(files[(index_atual + 1)%len(files)] ) is None:
            loaded_files[files[index_atual+1]] = carrega(files[index_atual+1])
        #print(time.time() - t, "s para load index=", index_atual)
        return

    def left(event):
        anterior(event)
        if loaded_files.get(files[(index_atual - 1) % len(files)]) is None:
            loaded_files[files[index_atual-1]] = carrega(files[index_atual-1])
        return

# Setting up overall environment
root.title("Eu amo o Bernado")
root.state('zoomed')

mostra_imagem(files[0])  # Inicializando a janela, com a primeira imagem
imagem_mostrada.pack()

#Old
root.bind("1",          copiar)
root.bind("<Right>",    right)
root.bind("<Left>",     left)

#New
root.bind("6",          right)
root.bind("4",          left)
root.bind("8",          copiar)

#location = os.path.join(source_dir, files[0])
#from exif import Image
#with open(location, 'rb') as image_file:
#    my_image = Image(image_file)
#my_image.list_all()
#print(my_image)

root.mainloop() # Fica escutando se algum evento aconteceu
# Qualquer coisa depois disso só roda dps q fechar a janela
print("fim")

#TODO
#Alt menu to change source dir
#Deal with ARW files
#not crash when there is a folder
#raise a warning when dest dir doesnt exist
#cleanup warnings and timings
#overlay camera settings
#Implement option to hide bracketing
