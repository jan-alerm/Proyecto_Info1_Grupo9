import matplotlib.pyplot as plt
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

def plot_arrivals(self):
        
    if not self.lista_aeropuertos:
        print("Error", "No hay datos cargados.")
        return False

    try:

        horas_formato = [int(obj.time[:2]) for obj in self.lista_aeropuertos]

        cont_hora = [0] * 24
        for hora in horas_formato:
            if 0 <= hora < 24:
                cont_hora[hora] += 1

        eje_x = list(range(24))
        eje_y = cont_hora

        plt.figure(figsize=(10, 5))
        plt.bar(eje_x, eje_y, color='blue', edgecolor='black')
        plt.title("Vuelos por Hora de Llegada")
        plt.xlabel("Hora del día")
        plt.ylabel("Cantidad de aviones")
        plt.xticks(eje_x)  # Para que salgan todos los números del 0 al 23
        plt.grid(axis='y', linestyle='--', alpha=0.4)

        plt.show()
        return True
        
    except AttributeError:
        print("Error", "Los objetos cargados no tienen el atributo '.time'")


def save_flights(aircrafts,filename):
    if not aircrafts:
        return False
    f = open(filename, 'w')
    f.write("AIRCRAFT ORIGIN ARRIVALS AIRLINE\n")
    for aircraft in aircrafts:
        if aircraft.code:
            aid = aircraft.code
        else:
            aid = "-"
        if aircraft.origin:
            origin = aircraft.origin
        else:
            origin = "-"
        if aircraft.time:
            time = aircraft.time
        else:
            time = "-"
        if aircraft.company:
            company = aircraft.company
        else:
            company = "-"

        f.write(f"{aid} {origin} {time} {company}\n")
    f.close()
    return True

def plot_airlines(lista_vols):
    if len(lista_vols) == 0:
        print("Error: The vector is empty.")
        return False

    nombres_agencias = []
    conteos = []

    for avion in lista_vols:
        agencia_actual = avion.company

        encontrado = False
        i = 0
        while i < len(nombres_agencias):
            if nombres_agencias[i] == agencia_actual:
                conteos[i] += 1
                encontrado = True
            i += 1

        if not encontrado:
            nombres_agencias.append(agencia_actual)
            conteos.append(1)

    plt.figure(figsize=(10, 5))
    plt.bar(nombres_agencias, conteos, color='orange', edgecolor='black')

    plt.title("Airlines Statistics")
    plt.xlabel("Agencies")
    plt.ylabel("Number of Aircraft")
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.3)

    plt.show()
    return True

def PlotFlightsType(aircrafts):
    if len(aircrafts) == 0:
        print("Error: The aircraft list is empty.")
        return False

    schengen_prefixes = [
        'LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG', 'EH', 'LH', 'BI',
        'LI', 'EV', 'EY', 'EL', 'LM', 'EN', 'EP', 'LP', 'LZ', 'LJ', 'LE', 'ES', 'LS'
    ]

    total_schengen = 0
    total_no_schengen = 0

    for avion in aircrafts:
        prefijo = avion.origin[:2]

        if prefijo in schengen_prefixes:
            total_schengen += 1
        else:
            total_no_schengen += 1

    ejes_x = ['Schengen', 'Non-Schengen']
    ejes_y = [total_schengen, total_no_schengen]

    plt.figure(figsize=(8, 6))
    colores = ['green', 'red']

    plt.bar(ejes_x, ejes_y, color=colores, edgecolor='black')

    plt.title("Total Flights by Origin Type")
    plt.xlabel("Type of Origin")
    plt.ylabel("Number of Aircraft")

    for i in range(len(ejes_y)):
        plt.text(i, ejes_y[i] + 0.1, str(ejes_y[i]), ha='center', va='bottom', fontsize=12)

    plt.grid(axis='y', linestyle='--', alpha=0.3)
    plt.show()

    return True





