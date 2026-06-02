import os

class Airport:
    def __init__(self, code, lat, lon):
        self.code = code
        self.lat = lat
        self.lon = lon
        self.schengen = False


# ======================================================================================================================
# COMPROBACION DE AEROPUERTO SCHENGEN (IS_SCHENGEN_AIRPORT)
# ======================================================================================================================
def is_schengen_airport(code):
    """ INPUT:          -> code: el código ICAO del aeropuerto

        OUTPUT:         -> TRUE: si el aeropuerto pertenece al espacio Schengen
                        -> FALSE: si no pertenece o el codigo esta vacio

        DESCRIPTION:    -> clasifica un aeropuerto utilizando el prefijo ICAO del codigo
                        -> compara el prefijo con la lista de zonas Schengen consideradas en el proyecto
    """
    if not code:
        return False
    prefix = code[:2]
    schengen_prefixes = [
        'LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG', 'EH', 'LH','BI',
        'LI', 'EV', 'EY', 'EL', 'LM', 'EN', 'EP', 'LP', 'LZ', 'LJ', 'LE','ES', 'LS'
    ]

    return prefix in schengen_prefixes


# ======================================================================================================================
# ASIGNACION DEL ATRIBUTO SCHENGEN (SET_SCHENGEN)
# ======================================================================================================================
def set_schengen(airport):
    """ INPUT:          -> airport: objeto Airport

        OUTPUT:         -> no devuelve ningun valor

        DESCRIPTION:    -> actualiza el atributo schengen del objeto aeropuerto
                        -> reutiliza is_schengen_airport para decidir si el codigo ICAO es Schengen
    """
    airport.schengen = is_schengen_airport(airport.code)


# ======================================================================================================================
# MOSTRAR DATOS DE AEROPUERTO (PRINT_AIRPORT)
# ======================================================================================================================
def print_airport(airport):
    """ INPUT:          -> airport: objeto Airport que se quiere mostrar

        OUTPUT:         -> imprime por terminal los datos principales del aeropuerto

        DESCRIPTION:    -> muestra codigo ICAO, coordenadas y estado Schengen
                        -> transforma el booleano schengen en texto comprensible para el usuario
    """
    if airport.schengen:
        status = "Yes"
    else:
        status = "No"
    print("---Airport Data---")
    print("ICAO Code: ",airport.code)
    print("Coordinates: ", airport.lat, airport.lon)
    print("Schengen: ",status)


# ======================================================================================================================
# CARGA DE AEROPUERTOS DESDE FICHERO (LOAD_AIRPORTS)
# ======================================================================================================================
def load_airports(filename):
    """ INPUT:          -> filename: fichero de texto con aeropuertos y coordenadas

        OUTPUT:         -> lista de objetos Airport cargados desde el fichero
                        -> lista vacia si el fichero no existe

        DESCRIPTION:    -> lee un fichero con formato CODE LAT LON
                        -> convierte coordenadas en grados/minutos/segundos a coordenadas decimales
                        -> crea un objeto Airport por cada linea valida encontrada
    """
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
            if lat_str[0] == "S" or lat_str[0] == "W":
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


# ======================================================================================================================
# GUARDAR AEROPUERTOS SCHENGEN (SAVE_SCHENGEN_AIRPORTS)
# ======================================================================================================================
def save_schengen_airports(airports, filename):
    """ INPUT:          -> airports: lista de objetos Airport
                        -> filename: fichero de salida donde guardar los aeropuertos Schengen

        OUTPUT:         -> 1 si se genera el fichero correctamente
                        -> 0 si no hay aeropuertos Schengen para guardar

        DESCRIPTION:    -> recorre la lista de aeropuertos y filtra los que tienen schengen == True
                        -> guarda codigo y coordenadas decimales en un fichero de texto
    """
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


# ======================================================================================================================
# ANADIR AEROPUERTO A LA LISTA (ADD_AIRPORT)
# ======================================================================================================================
def add_airport(airports,airport):
    """ INPUT:          -> airports: lista de objetos Airport
                        -> airport: nuevo objeto Airport que se quiere insertar

        OUTPUT:         -> no devuelve ningun valor

        DESCRIPTION:    -> comprueba si el codigo ICAO ya existe en la lista
                        -> anade el aeropuerto solamente si no esta duplicado
    """
    encontrado = False
    i = 0
    while i < len(airports):
        if airports[i].code == airport.code:
            encontrado = True
        i += 1

    if not encontrado:
        airports.append(airport)


# ======================================================================================================================
# ELIMINAR AEROPUERTO DE LA LISTA (REMOVE_AIRPORT)
# ======================================================================================================================
def remove_airport(airports,code):
    """ INPUT:          -> airports: lista de objetos Airport
                        -> code: codigo ICAO del aeropuerto que se quiere eliminar

        OUTPUT:         -> 1 si el aeropuerto se elimina correctamente
                        -> -1 si no se encuentra el codigo indicado

        DESCRIPTION:    -> busca un aeropuerto por codigo ICAO dentro de la lista
                        -> elimina el primer objeto que coincida con el codigo proporcionado
    """
    i = 0
    while i < len(airports):
        if airports[i].code == code:
            airports.pop(i)
            return 1
        i += 1
    return -1

import matplotlib.pyplot as plt


# ======================================================================================================================
# ESTADISTICAS DE AEROPUERTOS SCHENGEN (PLOT_AIRPORTS)
# ======================================================================================================================
def plot_airports(airports):
    """ INPUT:          -> airports: lista de objetos Airport

        OUTPUT:         -> genera un grafico de barras apiladas

        DESCRIPTION:    -> contabiliza cuantos aeropuertos son Schengen y cuantos no lo son
                        -> representa visualmente ambos grupos mediante Matplotlib
    """
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


# ======================================================================================================================
# MAPA DE AEROPUERTOS EN GOOGLE EARTH (MAP_AIRPORTS)
# ======================================================================================================================
def map_airports(airports):
    """ INPUT:          -> airports: lista de objetos Airport

        OUTPUT:         -> genera el fichero airports_map.kml
                        -> abre el fichero automaticamente en Google Earth

        DESCRIPTION:    -> recorre todos los aeropuertos de la lista y crea un marcador KML para cada uno
                        -> usa color azul para aeropuertos Schengen y rojo para aeropuertos no Schengen
    """
    f = open("airports_map.kml", "w")
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    f.write('<Document>\n')
    f.write('<name>Airport Map</name>\n')

    i = 0
    while i < len(airports):
        a = airports[i]

        # Recalculamos (usando el ICAO) el atributo Schengen para los aeropuertos antes de generar el mapa.
        # De esta forma nos aseguramos de que los datos estén "actualizados" incluso si no han ejecutado previamente
        # la opción de: "Calcular Atributo Schengen" en la interfaz
        if is_schengen_airport(a.code):
            color = "ffff0000"      # azul
        else:
            color = "ff0000ff"      # rojo

        # generación del marcador KML del aeropuerto
        f.write('<Placemark>\n')
        f.write('<Style>\n')
        f.write('<IconStyle>\n')
        f.write('<color>' + color + '</color>\n')
        f.write('</IconStyle>\n')
        f.write('</Style>\n')
        # solo mostrar el ICAO como nombre del marcador
        f.write('<name>' + a.code + '</name>\n')
        f.write('<Point>\n')
        f.write('<coordinates>' + str(a.lon) + ',' + str(a.lat) + '</coordinates>\n')
        f.write('</Point>\n')
        f.write('</Placemark>\n')
        i += 1

    f.write('</Document>\n')
    f.write('</kml>\n')
    f.close()

    print("Archivo 'airports_map.kml' creado.")

    import os
    os.startfile("airports_map.kml")
