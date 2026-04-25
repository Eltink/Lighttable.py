import tkinter as tk
from PIL import Image, ImageTk
import os
from copiador_de_arquivo import copia_arquivo

# Inicializando as coisas globais chatas
root = tk.Tk()  # Create window
imagem_mostrada = tk.Label(root)
index_atual = 0  # Qual o indice da imagem que esta sendo mostrada

# Import of configuration parameters
source_dir = 'C:\\Users\\glauc\\Desktop\\TL raios takaoka\\LR_out'
# source_dir = 'C:\\Users\\glauc\\Desktop\\Selecionar\\H2\\14421013'
destination_dir = 'C:\\Users\\glauc\\Desktop\\dest'

def carrega(filename):
    img = Image.open(os.path.join(source_dir, filename))  # Arquivo de origem(src+filename)
    img = img.resize((root.winfo_screenwidth(), root.winfo_screenheight()))
    return ImageTk.PhotoImage(img)  # Mostrar a imagem selecionada na tela

files = os.listdir(source_dir)      # O nome das imagens
loaded_files = {}                   # Dicionario dizendo quais imagens estão guardadas

for file in files:
    loaded_files[file] = carrega(file)  # O indice do dicio é o nome do arquivo (file) e a "definicao do dicio" é a saída de carrega(file)

# Função para mostrar
def mostra_imagem():
    imagem_mostrada['image'] = loaded_files[files[index_atual]]  # Mostrar a imagem selecionada na tela
    return

def copiar(event):
    copia_arquivo(source_dir, files[index_atual], destination_dir)
    proxima(event)
    return

def proxima(event):
    global index_atual
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

mostra_imagem()  # Inicializando a janela, com a primeira imagem
imagem_mostrada.pack()

root.bind("1", copiar)
root.bind("<Right>", proxima)
root.bind("<Left>", anterior)

root.mainloop()