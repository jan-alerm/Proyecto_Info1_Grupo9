

class Airport:
    def __init__(self,code,lat,lon):
        self.code = code
        self.coordinates =(lat,lon)
        self.schengen = False

def is_schengen_airport(code):
    if not code:
        return False
    prefix = code[:2]
    schengen_prefixes = [
        'LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG', 'EH', 'LH','BI',
        'LI', 'EV', 'EY', 'EL', 'LM', 'EN', 'EP', 'LP', 'LZ', 'LJ', 'LE','ES', 'LS'
    ]

    return prefix in schengen_prefixes

def set_schengen(airport):
    airport.schengen = is_schengen_airport(airport.code)

def print_airport(airport):
    if airport.schengen:
        status = "Yes"
    else:
        status = "No"
    print("---Airport Data---")
    print("ICAO Code: ",airport.code)
    print("Coordinates: ",airport.coordinates[0],airport.coordinates[1])
    print("Schengen: ",status)

import os

def load_airports(filename):
    if not os.path.exists(filename):
        return []

    lista_aeropuertos=[]
    f = open(filename,'r')
    f.readline()
    linea = f.readline()
    while linea != "":
        elementos = linea.split()
        if len(elementos) == 3:
            codigo = elementos[0]
            lat_str = elementos[1]
            lon_str = elementos[2]

            grados = float(lat_str[1:3])
            minutos = float(lat_str[3:5])
            segundos = float(lat_str[5:7])
            lat_decimal = grados + (minutos / 60) + (segundos / 3600)
            if lat_str[0] == "S" or lat_str == "W":
                lat_decimal = -lat_decimal

            grados_lon = float(lon_str[1:4])
            minutos_lon = float(lon_str[4:6])
            segundos_lon = float(lon_str[6:8])
            lon_decimal = grados_lon + (minutos_lon / 60) + (segundos_lon / 3600)
            if lon_str[0] == 'S' or lon_str[0] == 'W':
                lon_decimal = -lon_decimal
            nuevo_aeropuerto = Airport(codigo, lat_decimal, lon_decimal)
            lista_aeropuertos.append(nuevo_aeropuerto)
        linea = f.readline()
    f.close()
    return lista_aeropuertos

def save_schengen_airports(airports, filename):
    hay_schengen = False
    i = 0
    while i < len(airports):
        if airports[i].schengen == True:
            hay_schengen = True
        i += 1

    if not hay_schengen:
        return 0

    f = open(filename,'w')
    f.write("CODE LAT LON\n")

    i=0
    while i < len(airports):
        a = airports[i]
        if a.schengen == True:
            f.write(a.code + " " + str(a.coordinates[0]) + " " + str(a.coordinates[1]) + "\n")
        i += 1
    f.close()
    return 1

def add_airport(airports,airport):
    encontrado = False
    i = 0
    while i < len(airports):
        if airports[i].code == airport.code:
            encontrado = True
        i += 1

    if not encontrado:
        airports.append(airport)

def remove_airport(airports,code):
    i = 0
    while i < len(airports):
        if airports[i].code == code:
            airports.pop(i)
            return 1
        i += 1
    return -1

import matplotlib.pyplot as plt

def plot_airports(airports):
    schengen = 0
    not_schengen = 0
    i = 0
    while i < len(airports):
        if airports[i].schengen:
            schengen += 1
        else:
            not_schengen += 1
        i += 1
    labels = ["Airports"]
    plt.bar(labels,[schengen],label="Schengen",color="blue")
    plt.bar(labels,[not_schengen],bottom=[schengen],label="Not schengen",color="red")
    plt.ylabel("Number of airports")
    plt.title("Schengen vs Not schengen")
    plt.legend()
    plt.show()

def map_airports(airports):
    f = open("airports_map.kml","w")
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<kml xmlns="https://www.opengis.net/kml/2.2">\n')
    f.write('<Document>\n')
    i = 0
    while i < len(airports):
        a = airports[i]
        color = "ff0000ff"  # Rojo
        if a.schengen:
            color = "ffff0000"  # Azul
        f.write('<Placemark>\n')
        f.write('  <name>' + a.code + '</name>\n')
        f.write('  <Point>\n')
        f.write('    <coordinates>' + str(a.coordinates[1]) + ',' + str(a.coordinates[0]) + '</coordinates>\n')
        f.write('  </Point>\n')
        f.write('</Placemark>\n')
        i =+ 1

    f.write('</Document>\n')
    f.write('</kml>\n')
    f.close()
    print("Archivo 'airports_map.kml' creado. Ábrelo con Google Earth.")


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

