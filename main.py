# Tendando compartimentalizar as funcoes
import tkinter as tk
from PIL import Image, ImageTk
import os
import funcoes #nao existe mais, era um arquivo vazio
from copiador_de_arquivo import copia_arquivo
import time

# Inicializando as coisas globais chatas
root = tk.Tk()  # Create window
imagem_mostrada = tk.Label(root)
index_atual = 0  # Qual o indice da imagem que esta sendo mostrada

# Import of configuration parameters
source_dir = 'C:\\Users\\glauc\\Desktop\\Selecionar\\Cel pai\\JPG'
# source_dir = 'C:\\Users\\glauc\\Desktop\\TL raios takaoka\\LR_out'
# source_dir = 'C:\\Users\\glauc\\Desktop\\Selecionar\\H2\\14421013'
destination_dir = 'C:\\Users\\glauc\\Desktop\\dest'

files = os.listdir(source_dir)  # O nome das imagens
loaded_files = {}               # Dicionario dizendo quais imagens estão guardadas

def carrega(filename):
    img = Image.open(os.path.join(source_dir, filename))                    # Arquivo de origem(src+filename)
    img = img.resize((root.winfo_screenwidth(), root.winfo_screenheight())) # Faz a imagem preencher a tela, nem mais nem menos
    return ImageTk.PhotoImage(img)                                          # Mostrar a imagem selecionada na tela
#t = time.time()
for file in files[0:5]:                 # Carrega so as 2 primeiras imagens, pra ir mais rapido
    loaded_files[file] = carrega(file)  # O indice do dicio (key) é o nome do arquivo (file) e a "definicao do dicio" é a saída de carrega(file)
#print(time.time() - t)
if True: # So that code folding is possible
    def mostra_imagem(file):
        if file in loaded_files:
            imagem_mostrada['image'] = loaded_files[file]  # Mostrar a imagem selecionada na tela
        else:
            print("This didnt work. Info for debbug follows:")
            print(f"index_atual: {index_atual}")
            print(f"files[index_atual]: {files[index_atual]}")
            print(f"loaded_files[files[index_atual]] was not found")
            print("This are the available dictionary keys: ", loaded_files.keys())
        return

    def copiar(event):
        copia_arquivo(source_dir, files[index_atual], destination_dir)
        proxima(event)
        return

    def proxima(event):
        global index_atual

        # Incrementa o index e mostra a proxima
        mostra_imagem(files[index_atual])

        # Se tiver perto da margem, carrega mais e deleta antigas
        if files[index_atual] not in loaded_files:
            for file in files[index_atual:(index_atual + 5) % len(files)]:
                loaded_files[file] = carrega(file)

        index_atual = index_atual + 1
        index_atual = index_atual % len(files)  # Depois da ultima, volta pro começo
        return

    def anterior(event):
        global index_atual
        index_atual = index_atual - 1
        index_atual = index_atual % len(files)  # Depois da ultima, volta pro começo
        mostra_imagem(files[index_atual])
        return

# Setting up overall environment
root.title("Eu amo o Bernado")
root.state('zoomed')

mostra_imagem(files[0])  # Inicializando a janela, com a primeira imagem
imagem_mostrada.pack()

root.bind("1",          copiar)
root.bind("<Right>",    proxima)
root.bind("<Left>",     anterior)

root.mainloop() # Fica escutando se algum evento aconteceu
# Qualquer coisa depois disso não vai rodar nunca
