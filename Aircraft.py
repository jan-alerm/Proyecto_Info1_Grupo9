import math
import os
import matplotlib.pyplot as plt

class Aircraft:
# se representan los vuelos mediante: - código de avión
#                                     - compañía aerea
#                                     - aeropuerto de origen
#                                     - hora de llegada
    def __init__(self, codigo, company, origin, time):
        self.codigo = codigo
        self.company = company
        self.origin = origin
        self.time = time

        self.destination = ""  # Código ICAO de destino
        self.departure_time = ""  # Hora de salida (formato hh:mm)
#============================================= CARGA DE VUELOS DESDE FICHERO ===========================================
def load_arrivals(filename):
#FUNCIÓN: carga los vuelos almacenados en en un fichero (.txt) y genera una lista de objetos Aircraft
#         el fichero (.txt) debe seguir el formato: AIRCRAFT ORIGIN ARRIVAL AIRLINE
#         convierte las coordenadas desde el formato sexagesimal a decimal
#         si el fichero no existe o una línea no tiene el formato correcto, la línea se IGNORA

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


# ======================================================================================
# CARGA DE SALIDAS (DEPARTURES)
# ======================================================================================
def LoadDepartures(filename):
    """
    Abre el fichero de salidas y devuelve una lista de objetos Aircraft
    inicializados ÚNICAMENTE con los datos de salida.
    Si el fichero no existe, devuelve una lista vacía y un código de error (-1).
    """
    if not os.path.exists(filename):
        print(f"Error: El archivo {filename} no existe.")
        return [], -1

    lista_departures = []

    try:
        f = open(filename, 'r', encoding='utf-8')
        f.readline()  # Leer la cabecera (AIRCRAFT DESTINATION DEPARTURE AIRLINE)
        linea = f.readline()

        while linea != "":
            elementos = linea.split()

            if len(elementos) == 4:
                codigo = elementos[0]
                destino = elementos[1]
                hora_salida = elementos[2]
                company = elementos[3]

                # Creamos el objeto indicando la salida. Los campos de llegada quedan vacíos de momento.
                nuevo_vuelo = Aircraft(codigo, company, origin="", time="")
                nuevo_vuelo.destination = destino
                nuevo_vuelo.departure_time = hora_salida

                lista_departures.append(nuevo_vuelo)

            linea = f.readline()

        f.close()
        return lista_departures, 1  # 1 indica éxito

    except Exception as e:
        print(f"Error procesando el archivo de salidas: {e}")
        return [], -1


# ======================================================================================
# FUSIÓN DE MOVIMIENTOS (MERGE MOVEMENTS)
# ======================================================================================
def MergeMovements(arrivals, departures):
    """
    Recibe la lista de llegadas y salidas. Devuelve una lista unificada de objetos Aircraft.
    Cruza los datos por ID de avión (codigo) siempre que la hora de llegada sea anterior
    a la de salida. Soporta rotaciones múltiples y aviones pernoctando.
    """
    if not arrivals or not departures:
        print("Error: Una de las listas de entrada está vacía.")
        return -1

    # Función auxiliar interna para convertir hh:mm a minutos totales y comparar fácil
    def a_minutos(hora_str):
        if not hora_str:
            return -1
        try:
            h, m = map(int, hora_str.split(':'))
            return h * 60 + m
        except:
            return -1

    lista_fusionada = []

    # Listas auxiliares para controlar qué elementos ya han sido emparejados
    salidas_emparejadas = [False] * len(departures)
    llegadas_emparejadas = [False] * len(arrivals)

    # 1. Intentar emparejar cada llegada con su salida correspondiente y compatible
    i = 0
    while i < len(arrivals):
        llegada = arrivals[i]
        minutos_llegada = a_minutos(llegada.time)

        # Buscar una salida compatible para este mismo avión
        j = 0
        encontrado = False
        while j < len(departures):
            salida = departures[j]

            # Si coincide el código y la salida no ha sido asignada todavía
            if llegada.codigo == salida.codigo and not salidas_emparejadas[j]:
                minutos_salida = a_minutos(salida.departure_time)

                # El avión debe salir DESPUÉS de haber llegado
                if minutos_llegada < minutos_salida:
                    # Creamos el clon fusionado
                    avion_fusionado = Aircraft(llegada.codigo, llegada.company, llegada.origin, llegada.time)
                    avion_fusionado.destination = salida.destination
                    avion_fusionado.departure_time = salida.departure_time

                    lista_fusionada.append(avion_fusionado)
                    salidas_emparejadas[j] = True
                    llegadas_emparejadas[i] = True
                    encontrado = True
                    break  # Emparejado con la primera salida cronológicamente válida
            j += 1

        # Si no encontró ninguna salida compatible para este aterrizaje, se añade solo como llegada
        if not encontrado:
            avion_solo_llegada = Aircraft(llegada.codigo, llegada.company, llegada.origin, llegada.time)
            lista_fusionada.append(avion_solo_llegada)
            llegadas_emparejadas[i] = True

        i += 1

    # 2. Agregar los aviones remanentes que no tuvieron llegada (aviones nocturnos / de base)
    k = 0
    while k < len(departures):
        if not salidas_emparejadas[k]:
            salida = departures[k]
            avion_nocturno = Aircraft(salida.codigo, salida.company, origin="", time="")
            avion_nocturno.destination = salida.destination
            avion_nocturno.departure_time = salida.departure_time

            lista_fusionada.append(avion_nocturno)
            salidas_emparejadas[k] = True
        k += 1

    return lista_fusionada


def NightAircraft(aircrafts):
    """
    Recibe una lista de objetos Aircraft (generalmente la lista ya unificada)
    y devuelve una nueva lista con las aeronaves que no tienen hora de llegada
    (time == ""), pero sí tienen información de salida configurada.
    Si la lista de entrada está vacía, devuelve un código de error (-1).
    """
    # Validación: Si la lista está vacía o es None, devolvemos el código de error
    if not aircrafts:
        print("Error: La lista de aeronaves proporcionada está vacía.")
        return -1

    lista_nocturnos = []
    i = 0

    # Recorremos la lista usando un bucle while clásico
    while i < len(aircrafts):
        avion = aircrafts[i]

        # Un avión pernoctó si NO tiene origen/hora de llegada, pero SÍ tiene hora de salida
        if (avion.time == "" or avion.origin == "") and avion.departure_time != "":
            lista_nocturnos.append(avion)

        i += 1

    return lista_nocturnos




#============================================ DISTRIBUCIÓN HORARIA DE LLEGADAS =========================================
def plot_arrivals(lista_de_vuelos):
#FUNCIÓN: genera un gráfico de barras con la frecuencia de llegada durante las distintas horas
#         (solamente se tiene en cuenta la hora de llegada para hacer la distribución horaria)
#         si la lista está vacía, muestra "error"
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

#============================================== GUARDAR VUELOS EN FICHERO ==============================================
def save_flights(aircrafts, filename):
#FUNCIÓN: guarda la información de los vuelos en un fichero .txt utilizando el mismo formato que el original
#         las partes vacías se representan símbolo "-"
#         si la lista está vacía no genera ningún fichero
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

#=========================================== ESTADÍSTICAS DE COMPAÑÍAS AEREAS ==========================================
def plot_airlines(lista_vols, airlines_selected=None):
    if len(lista_vols) == 0:
        print("Error: El vector está vacío.")
        return False

    nombres_agencias = []
    conteos = []

    # Recorremos todos los vuelos de la lista
    v = 0
    while v < len(lista_vols):
        avion = lista_vols[v]
        agencia_actual = avion.company

        # --- NUEVO FILTRO ---
        # Si el usuario ha seleccionado aerolíneas específicas y la actual no está en la lista, la ignoramos
        if airlines_selected is not None:
            incluir = False
            a = 0
            while a < len(airlines_selected):
                if airlines_selected[a] == agencia_actual:
                    incluir = True
                    break
                a += 1
            if not incluir:
                v += 1
                continue
        # ---------------------

        # Comprobamos si la agencia ya está registrada en nuestras listas del gráfico
        encontrado = False
        i = 0
        while i < len(nombres_agencias):
            if nombres_agencias[i] == agencia_actual:
                conteos[i] += 1
                encontrado = True
                break
            i += 1

        if not encontrado:
            nombres_agencias.append(agencia_actual)
            conteos.append(1)

        v += 1

    # Si después del filtro no queda ninguna aerolínea para pintar
    if len(nombres_agencias) == 0:
        print("Error: Ninguna de las aerolíneas seleccionadas tiene vuelos cargados.")
        return False

    # Generación del gráfico con Matplotlib
    plt.figure(figsize=(12, 5))  # Reducido un poco el ancho para que quede más estético si son pocas
    plt.bar(nombres_agencias, conteos, color='orange', edgecolor='black')

    plt.title("Airlines Statistics (Filtered)")
    plt.xlabel("Agencies")
    plt.ylabel("Number of Aircraft")
    plt.xticks(rotation=45)
    plt.xticks(fontsize=8)
    plt.grid(axis='y', linestyle='--', alpha=0.3)

    plt.show()
    return True
#============================================= VUELOS SCHENGEN / NO SCHENGEN ===========================================
def plot_flights_type(aircrafts):
#FUNCIÓN: genera un gráfico de barras con la cantidad de vuelos procedentes de países schengen y no schengen
#         la clasificación se hace con el prefijo del código ICAO
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

#============================================== TRAYECTORIAS EN GOOGLE EARTH ===========================================
def map_flights(aircrafts, airports):
#FUNCIÓN: genera un fichero .kml para visualizar en Google Earth las trayectorias de llegada de los vuelos hacia LEBL
#         se representan las trayectorias mediante líneas, diferenciando colores dependiendo si schengen o no schengen
#         el ficheroo se abre automáticamente en Google Earth
    f = open('flights_map.kml', 'w')
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    f.write('<Document>\n')

    #coordenadas base LEBL (BARCELONA)
    lat_lebl = 41.297445
    lon_lebl = 2.0832941

    i = 0
    while i < len(aircrafts):
        avion = aircrafts[i]

        j = 0                                                                       #búsqueda del aeropuerto de origen
        encontrado = False                                                          #a cada vuelo
        while j < len(airports):
            if airports[j].code == avion.origin:
                origen = airports[j]
                encontrado = True
            j += 1
        if not encontrado:
            i += 1
            continue

        prefix = avion.origin[:2]  # esto es lo mismo que al principip
        schengen_prefixes = [
            'LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG', 'EH', 'LH', 'BI',
            'LI', 'EV', 'EY', 'EL', 'LM', 'EN', 'EP', 'LP', 'LZ', 'LJ', 'LE', 'ES', 'LS'
        ]
        if prefix in schengen_prefixes:
            color = "ffff0000"  # azul
        else:
            color = "ff00ff00"  # verde

        f.write('<Placemark>\n')
        f.write('<Style><LineStyle><color>' + color + '</color><width>3</width></LineStyle></Style>\n')             #hace que las lineas sean bien visibles
        f.write('<LineString>\n')
        f.write('<tessellate>1</tessellate>\n')                                                                     #mejora la curvatura de las líneas
        f.write('<coordinates>\n')

        f.write(str(origen.lon) + "," + str(origen.lat) + "\n")
        f.write(str(lon_lebl) + "," + str(lat_lebl) + "\n")

        f.write('</coordinates>\n')
        f.write('</LineString>\n')
        f.write('</Placemark>\n')

        i += 1

    f.write('</Document>\n')
    f.write('</kml>\n')

    f.close()

    print("Archivo flights_map.kml creado")


    #abrir el Google Earth de manera directa
    os.startfile("flights_map.kml")

#================================================== HAVERSINE DISTANCE =================================================
def Haversine(lat1, lon1, lat2, lon2):
    """ INPUT:          -> lat1, lon1: coordenadas del origen
                        ->lat2, lon2 -> coordenadas del destino
    OUTPUT:             -> la distancia entre ambos puntos (que son los aeropuertos) en kilómetros
    DESCRIPTION:        -> utilizamos la fórmula de Haversine para calcular distancias sobre la Tierra
    """
    R = 6371                            #radio tierra
    # conversión de grados a radianes
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    # distancia angular entre puntos
    dif_lat = lat2 - lat1
    dif_lon = lon2 - lon1
    # fórmula
    a = math.sin(dif_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dif_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

#=========================================== VUELOS DE LARGA DISTANCIA (2000KM) ========================================
def long_distance_arrivals(aircrafts, airports):
    """ INPUT:          -> aircrafts: lista de vuelos
                        -> airports: lista de aeropuertos
        OUTPUT:         -> genera una lista de vuelos con origen que se encuentra a +2000km de LEBL
        DESCRIPCIÓN:    -> busca el aeropuerto de origen de un vuelo y calcula la distancia mediante "Haversine"
    """
    lista_long_flights = []
    i = 0
    # coordenadas de referencia de LEBL (aeropuerto BARCELONA)
    lat_lebl = 41.297445
    lon_lebl = 2.0832941

    while i < len(aircrafts):
        avion = aircrafts[i]
        # buscar en la lista el aeropuerto de origen del vuelo
        j = 0
        encontrado = False
        while j < len(airports):
            if airports[j].code == avion.origin:
                origen = airports[j]
                # si se encuentra, guarda el aeropuerto (+ coordenadas)
                encontrado = True
            j += 1
        # si no se encuentra el aeropuerto, se pasa al siguiente vuelo
        if not encontrado:
            i += 1
            continue

        # calcula la distancia entre el aeropuerto origen y el aeropuerto BARCELONA
        distancia = Haversine(origen.lat, origen.lon, lat_lebl, lon_lebl)

        #guarda unicamente los vuelos con el aeropuerto de origen a +2000km
        if distancia > 2000:
            lista_long_flights.append(avion)

        i += 1

    return lista_long_flights

load_departures = LoadDepartures
merge_movements = MergeMovements
night_aircraft = NightAircraft
