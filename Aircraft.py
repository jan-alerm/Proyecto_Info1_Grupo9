import matplotlib.pyplot as plt


class Aircraft:
    def __init__(self, codigo, company, origin, time):
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
            nueva_llegada = Aircraft(codigo,company,origen,tiempo)
            lista_arrivals.append(nueva_llegada)
            linea = f.readline()

    f.close()
    return lista_arrivals


def plot_arrivals(lista_de_vuelos):
    if not lista_de_vuelos:
        print("Error", "No hay datos cargados.")
        return False

    try:

        horas_formato = []
        for obj in lista_de_vuelos:
            hora_str = obj.time.split(':')[0]
            horas_formato.append(int(hora_str))

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


def save_flights(aircrafts, filename):
    if not aircrafts:
        return False
    f = open(filename, 'w')
    f.write("AIRCRAFT ORIGIN ARRIVALS AIRLINE\n")
    for aircraft in aircrafts:
        if aircraft.codigo:
            aid = aircraft.codigo
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
    plt.xticks(fontsize=5)
    plt.title("Airlines Statistics")
    plt.xlabel("Agencies")
    plt.ylabel("Number of Aircraft")
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.2)

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



def map_flights (aircrafts, airports):
    f = open('airports_map.kml', 'w')
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    f.write('<Document>\n')                                     

    lat_lebl = 41.297445
    lon_lebl = 2.0832941

    i = 0
    while i < len(aircrafts):
        avion = aircrafts[i]
        
        j = 0
        encontrado = False
        while j < len(airports):
            if airports[j].code == avion.origin:                
                origen = airports[j]
                encontrado = True
            j += 1
        if not encontrado:
            i += 1
            continue

        prefix = avion.origin[:2]                                                   # esto es lo mismo que al principip
        schengen_prefixes = [
            'LO','EB','LK','LC','EK','EE','EF','LF','ED','LG','EH','LH','BI',
            'LI','EV','EY','EL','LM','EN','EP','LP','LZ','LJ','LE','ES','LS'
        ]
        if prefix in schengen_prefixes:
            color = "ff0000ff"   # azul
        else:
            color = "ff00ff00"   # verde  

        f.write('<Placemark>\n')
        f.write('<Style><LineStyle><color>' + color + '</color></LineStyle></Style>\n')
        f.write('<LineString>\n')
        f.write('<coordinates>\n')

        f.write(str(origen.lon) + "," + str(origen.lat) + "\n")
        f.write(str(lon_lebl) + "," + str(lat_lebl) + "\n")

        f.write('</coordinates>\n')
        f.write('</LineString>\n')
        f.write('</Placemark>\n')

        i += 1 

write('</Document>\n')
    f.write('</kml>\n')

    f.close()

    print("Archivo flights_map.kml creado")

#--------------------------------------------------- HAVERSINE DISTANCE ------------------------------------------------
import math
def Haversine (lat1, lon1, lat2, lon2):
    R = 6371                                        # radio tierra
    lat1 = math.radians(lat1)                       # es importante que los angulos RADIANES
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dif_lat = lat2 - lat1                          #calcular la distancia angular entre puntos
    dif_lon = lon2 - lon1

    #fórmula
    a = math.sin(dif_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dif_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

#------------------------------------------------ LONG DISTANCE ARRIVALS -----------------------------------------------
def long_distance_arrivals (aircrafts, airports):
# teniendo en cuenta la lista de aeropuertos y de aviones
# devuelve una lista de flights que llegan a LEBL desde un aeropuerto +2000km (special inspection)
    lista_long_flights  =[]
    i = 0
    #coordenadas base de LEBL (BARCELONA)
    lat_lebl = 41.297445
    lon_lebl = 2.0832941

    while i < len(aircrafts):               # primero miraremos los vuelos uno a uno
        avion = aircrafts[i]                # "primer" avión a mirar

        j = 0                               # esto hará que busque el aeropuerto de origen
        encontrado = False
        while j < len(airports):            # recorrido de los aeropuertos
            if airports[j].code == avion.origin:            # este aeropuerte = origen avión?
                origen = airports[j]                        # si --> true, guarda el aeropuerto (+ coordenadas)
                encontrado = True
            j += 1

        if not encontrado:
            i += 1
            continue

        distancia = Haversine(origen.lat, origen.lon, lat_lebl, lon_lebl)
        # aquí ya se entiende que si no hay aeropuerto = origen no guarda la lon o lat

        if distancia > 2000:
            lista_long_flights.append(avion)

        i += 1

    return lista_long_flights
