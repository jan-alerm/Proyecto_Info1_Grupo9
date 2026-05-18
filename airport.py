import os
import matplotlib.pyplot as plt

class Airport:
# se representan los aeropuertos mediante: - código ICAO
#                                          - coordenadas geográficas (lat, lon)
    def __init__(self, code, lat, lon):
        self.code = code
        self.lat = lat                                                                                  #formato decimal
        self.lon = lon                                                                                  #formato decimal
        self.schengen = False

#============================================== AEROPUERTO SCHENGEN O NO ===============================================
def is_schengen_airport(code):
#FUNCIÓN: comprueba si un aeropuerto pertenece al espacio Schengen utilizando las 2 primeras letras de los códigos ICAO
# TRUE --> aeropuerto schengen
# FALSE --> aeropuerto NO schengen
#si el código está vacío, la función devuelve FALSE

    if not code:
        return False
    prefix = code[:2]
    schengen_prefixes = [
        'LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG', 'EH', 'LH','BI',
        'LI', 'EV', 'EY', 'EL', 'LM', 'EN', 'EP', 'LP', 'LZ', 'LJ', 'LE','ES', 'LS'
    ]
    return prefix in schengen_prefixes

#=======================================================================================================================
def set_schengen(airport):
#FUNCIÓN: actualiza la caracterísitca schengen de un aeropuerto utilizando la función anterior
    airport.schengen = is_schengen_airport(airport.code)

#================================================= MOSTRAR INFORMACIÓN =================================================
def print_airport(airport):
#FUNCIÓN: muestra la información principal de un aeropuerto, visualizando: - ICAO
#                                                                          - coordenadas geográficas
#                                                                          - estado schengen

    if airport.schengen:
        status = "Yes"
    else:
        status = "No"
    print("---Airport Data---")
    print("ICAO Code: ",airport.code)
    print("Coordinates: ", airport.lat, airport.lon)
    print("Schengen: ",status)

#============================================ CARGAR AEROPUERTOS DESDE FICHERO =========================================
def load_airports(filename):
#FUNCIÓN: carga los aeropuertos almacenados en un fichero (.txt) y genera una lista de objetos Airport
#         el fichero (.txt) debe seguir el formato: CODE LATITUDE LONGITUDE
#         convierte las coordenadas desde el formato sexagesimal a decimal
#         si el fichero no existe, devuelve una lista vacía

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

            # -------- LATITUD --------
            grados = float(lat_str[1:3])
            minutos = float(lat_str[3:5])
            segundos = float(lat_str[5:7])
            # conversión a grados decimales
            lat_decimal = grados + (minutos / 60) + (segundos / 3600)
            if lat_str[0] == "S" or lat_str[0] == "W":
                lat_decimal = -lat_decimal

            # -------- LONGITUDE --------
            grados_lon = float(lon_str[1:4])
            minutos_lon = float(lon_str[4:6])
            segundos_lon = float(lon_str[6:8])
            # conversión a grados decimales
            lon_decimal = grados_lon + (minutos_lon / 60) + (segundos_lon / 3600)
            if lon_str[0] == 'S' or lon_str[0] == 'W':
                lon_decimal = -lon_decimal
            nuevo_aeropuerto = Airport(codigo, lat_decimal, lon_decimal)
            lista_aeropuertos.append(nuevo_aeropuerto)
        linea = f.readline()
    f.close()
    return lista_aeropuertos

#============================================== GUARDAR AEROPUERTOS SCHENGEN ===========================================
def save_schengen_airports(airports, filename):
#FUNCIÓN: guardar en un fichero ÚNICAMENTE los aeropuertos que pertenecen al espacio schengen
#         importante tener en cuenta que primero comprueba si existe al menos 1 aeropuerto schengen antes de generar
#         el fichero, si no existe ni 1 ya no genera el fichero
# 1 --> guardado/realizado correcto
# 0 --> no existe aeropuerto schengen

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
            f.write(a.code + " " + str(a.lat) + " " + str(a.lon) + "\n")
        i += 1
    f.close()
    return 1

#================================================ AÑADIR AEROPUERTOS A LISTA ===========================================
def add_airport(airports,airport):
#FUNCIÓN: añadir un aeropuerto a la lista pero comprobando que no haya duplicados códigos ICAO

    encontrado = False
    i = 0
    while i < len(airports):
        if airports[i].code == airport.code:
            encontrado = True
        i += 1
    if not encontrado:
        airports.append(airport)

#============================================== ELIMINAR AEROPUERTOS DE LISTA ==========================================
def remove_airport(airports,code):
#FUNCIÓN: eliminar un aeropuerto de la lista utilizando el código ICAO
# 1 --> aeropuerto eliminado correctamente
# 0 --> no realizado

    i = 0
    while i < len(airports):
        if airports[i].code == code:
            airports.pop(i)
            return 1
        i += 1
    return 0

#===================================== GRÁFICO DE BARRAS AEROPUERTOS (SCHENGEN/NO SCHENGEN) ============================
def plot_airports(airports):
#FUNCIÓN: generar un gráfico de barras apiladas con la distribución de aeropuertos schengen/no schengen

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
    plt.ylabel("Number of airports.txt")
    plt.title("Schengen vs Not schengen")
    plt.legend()
    plt.show()

#======================================= GENERA FICHERO .KML + CARGAR EN GOOGLE EARTH ==================================
def map_airports(airports):
# FUNCIÓN:generar un fichero .kml para cargar los aeropuertos en Google Earth diferenciando los aeropuertos
#         schengen/ no schengen por colores

    f = open("airports_map.kml", "w")
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    f.write('<Document>\n')

    i = 0
    while i < len(airports):
        a = airports[i]
        #diferenciación por colores
        if a.schengen:
            color = "ffff0000"
        else:
            color = "ff0000ff"  #rojo

        f.write('<Placemark>\n')

        # configuración del marcador
        f.write('<Style>\n')
        f.write('<IconStyle>\n')
        f.write('<color>' + color + '</color>\n')
        f.write('</IconStyle>\n')
        f.write('</Style>\n')
        f.write('<name>' + a.code + '</name>\n')
        f.write('<Point>\n')
        f.write('<coordinates>' + str(a.lon) + "," + str(a.lat) + '</coordinates>\n')
        f.write('</Point>\n')
        f.write('</Placemark>\n')

        i += 1

    f.write('</Document>\n')
    f.write('</kml>\n')

    f.close()

    print("Archivo 'airports_map.kml' creado. Ábrelo con Google Earth.")

    #abrir el Google Earth de manera directa
    os.startfile("airports_map.kml")
