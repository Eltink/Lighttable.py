

def troca_cor (carro_cor,nova_cor):
    carro_cor = nova_cor
    return carro_cor

def troca_cor2 (nova_cor):
    return nova_cor

def main():
    global carro1
    global carro2
    global carro1_cor
    global carro2_cor
    carro1_cor = 1
    carro2_cor = 2
    carro1_cor= troca_cor2(3)

    carro1_cor = 3
    print(carro1_cor)


main()



