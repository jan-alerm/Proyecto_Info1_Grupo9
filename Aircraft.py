
class Aircraft:
    def __innit_(self,codigo,company,airport,time):
        self.codigo = codigo
        self.company = company
        self.origin = origin
        self.time = time

def load_arrivals(filename):
    f = open(filename, 'r')
    lista_arrivals = []
    f.readline()
    linea = f.readline()

    while linea != "":
        elementos = linea.split()

        if len(elementos) == 4:
            codigo = elementos[0]
            origen = elementos[1]
            tiempo = elementos[2]
            company = elementos[3]
            nueva_llegada = Aircraft(codigo, company, origen, tiempo)
            lista_arrivals.append(nueva_llegada)
            linea = f.readline()

    f.close()
    return lista_arrivals
