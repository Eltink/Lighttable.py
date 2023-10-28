# Tava zoando com o chat GPT e testando as saidas. Não ta funcional

import tkinter as tk
import threading
import time
from PIL import Image, ImageTk
import os
from copiador_de_arquivo import copia_arquivo

# Inicializando as coisas globais chatas
root = tk.Tk()  # Create window
imagem_mostrada = tk.Label(root)
index_atual = 0  # Qual o indice da imagem que esta sendo mostrada

# Import of configuration parameters
source_dir = 'C:\\Users\\glauc\\Desktop\\dest'
# source_dir = 'C:\\Users\\glauc\\Desktop\\TL raios takaoka\\LR_out'
# source_dir = 'C:\\Users\\glauc\\Desktop\\Selecionar\\H2\\14421013'
destination_dir = 'C:\\Users\\glauc\\Desktop\\dest'
loaded_files = {}  # Dicionario dizendo quais imagens estão guardadas


def carrega(filename):
    img = Image.open(os.path.join(source_dir, filename))  # Arquivo de origem(src+filename)
    img = img.resize((root.winfo_screenwidth(), root.winfo_screenheight()))
    loaded_files[filename] = ImageTk.PhotoImage(img)  # Mostrar a imagem selecionada na tela


def carrega_threaded(filename):
    thread = threading.Thread(target=carrega, args=(filename,))
    thread.start()


# Função para mostrar
def mostra_imagem():
    while files[index_atual] not in loaded_files:
        time.sleep(0.1)
    imagem_mostrada['image'] = loaded_files[files[index_atual]]  # Mostrar a imagem selecionada na tela
    return


def copiar(event):
    copia_arquivo(source_dir, files[index_atual], destination_dir)
    proxima(event)
    return


def proxima(event):
    global index_atual

    # Se tiver perto da margem, carrega mais e deleta antigas
    if files[index_atual] not in loaded_files:
        for file in files[index_atual:(index_atual+5) % len(files)]:
            carrega_threaded(file)

    # Incrementa o index e mostra a anterior
    index_atual = index_atual + 1
    index_atual = index_atual % len(files)  # Depois da ultima, volta pro começo
    mostra_imagem()
    return


def anterior(event):
    global index_atual
    index_atual = index_atual - 1
    index_atual = index_atual % len(files)  # Depois da ultima, volta pro começo
    mostra_imagem()
    return


# Setting up overall environment
root.title("Eu amo o Bernado")
root.state('zoomed')

files = os.listdir(source_dir)  # O nome das imagens

for file in files:
    carrega_threaded(file)

mostra_imagem()  # Inicializando a janela, com a primeira imagem
imagem_mostrada.pack()

root.bind("1", copiar)
root.bind("<Right>", proxima)
root.bind("<Left>", anterior)

root.mainloop()
