from threading import Thread

class CARRO():
    def __init__(self,ano,name):
        self.ano = ano
        self.name = name


    def set_name(self,name):
        self.name = name
        print(self.name)

    def get_name(self):
        return(self.name)



def main():
    carro = CARRO(1997,"Onix")
    print(carro.get_name())
    carro.set_name("Corvette")
    print(carro.get_name())
    t = Thread (target=carro.set_name,args=["Novo"])
    t.run()

main()