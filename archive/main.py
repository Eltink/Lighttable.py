import os
import shutil

base_de_dados = r"C:\Users\glauc\Desktop\BKs\unwetter\10710621"
selecao = r"C:\Users\glauc\Desktop\Munchen_SEL\Unwetter\temp"
# destino = os.makedirs(selecao+"\\copiadas")

imagens_selecionadas = os.listdir(selecao)

if "copiadas" not in imagens_selecionadas:
    destino = os.makedirs(selecao + "\\copiadas")
else:
    destino = os.path.join(selecao, "copiadas")
imagens_copiadas = os.listdir(destino)
formato_quero = '.JPG'
formato_tenho = '.ARW'
for nome_imagem_selecionada in imagens_selecionadas:
    if formato_tenho in nome_imagem_selecionada:
        imagem_quero = nome_imagem_selecionada[:-len(formato_tenho)] + formato_quero
        caminho_imagem_base_de_dados = os.path.join(base_de_dados, imagem_quero)
        if imagem_quero not in imagens_copiadas:

            if os.path.exists(caminho_imagem_base_de_dados):
                shutil.copy(caminho_imagem_base_de_dados, destino)
                print("copy " + imagem_quero)
            else:
                print("não encontrado: " + imagem_quero)