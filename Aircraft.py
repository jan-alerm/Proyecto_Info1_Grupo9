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


# ======================================================================================================================
# CARGA DE VUELOS DESDE FICHERO (LOAD_ARRIVALS)
# ======================================================================================================================
def load_arrivals(filename):
    """ INPUT:          -> filename: el nombre del fichero que contiene los vuelos de llegada

        OUTPUT:         -> la lista de objetos Aircraft (información de los vuelos) cargados desde el fichero (arrivals)

        DESCRIPTION:    -> lee el fichero de llegadas y crea un objeto Aircraft para cada línea válida encontrada
                        -> se asegura que el fichero tenga el formato: AIRCRAFT ORIGIN ARRIVAL AIRLINE
                        -> tener en cuenta que las líneas que no tengan exactamente 4 campos sean ignoradas
    """
    f = open(filename, 'r')
    lista_arrivals = []
    f.readline()
    linea = f.readline()

    while linea != "":
        elementos = linea.split()
        # comprobamos que la línea tiene el formato esperado
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


# ======================================================================================================================
# CARGA DE SALIDAS (LOAD_DEPARTURES)
# ======================================================================================================================
def LoadDepartures(filename):
    """ INPUT:          -> filename: el fichero de texto con las salidas programadas

        OUTPUT:         -> lista_departures: una lista de objetos Aircraft
                        -> status: 1 si la carga ha sido correcta
                                  -1 si error durante la carga

        DESCRIPTION:    -> lee el fichero de salidas y crea un objeto Aircraft para cada línea válida encontrada
                        -> los datos de llegada se dejan vacíos y ÚNICAMENTE se inicializan los datos de salida
    """
    # comprobamos que el fichero existe antes de procesarlo
    if not os.path.exists(filename):
        print(f"Error: El archivo {filename} no existe.")
        return [], -1

    lista_departures = []

    try:
        f = open(filename, 'r', encoding='utf-8')
        # lee la cabecera  y salta la línea (AIRCRAFT DESTINATION DEPARTURE AIRLINE)
        f.readline()
        linea = f.readline()

        while linea != "":
            elementos = linea.split()
            # comprobamos si la línea tiene el formato deseado
            if len(elementos) == 4:
                codigo = elementos[0]
                destino = elementos[1]
                hora_salida = elementos[2]
                company = elementos[3]

                # creamos el objeto Aircraft únicamente con los datos de salida
                nuevo_vuelo = Aircraft(codigo, company, origin="", time="")
                nuevo_vuelo.destination = destino
                nuevo_vuelo.departure_time = hora_salida

                lista_departures.append(nuevo_vuelo)

            linea = f.readline()

        f.close()
        return lista_departures, 1                                                                      #1 indica éxito

    except Exception as e:
        print(f"Error procesando el archivo de salidas: {e}")
        return [], -1                                                                                   #-1 indica error


# ======================================================================================================================
# FUSIÓN DE MOVIMIENTOS (MERGE_MOVEMENTS)
# ======================================================================================================================
def MergeMovements(arrivals, departures):
    """ INPUT:          -> arrivals: la lista de vuelos de llegada
                        -> departures: la lista de vuelos de salida

        OUTPUT:         -> lista_fusionada: la lista de objetos Aircraft con la información de llegadas y salidas combinadas
                        -> -1: si alguna de las listas de entrada está vacía

        DESCRIPTION:    -> empareja las llegadas y salidas utilizando el identificador del avión (código  ICAO)
                        -> se asegura que una llegada y una salida solo puedan fusionarse si la hora de llegada es anterior a la de salida
                        -> la función también tiene en cuenta: - rotaciones múltiples
                                                               - aviones que SOLO llegan
                                                               - aviones "nocturnos" o que SOLO salen
    """
    # comprobamos que ambas listas tienen datos antes de fusionarlas
    if not arrivals or not departures:
        print("Error: Una de las listas de entrada está vacía.")
        return -1
    # una función auxiliar para convertir una hora hh:mm a minutos totales y facilitar las comparaciones de tiempo
    def a_minutos(hora_str):
        if not hora_str:
            return -1
        try:
            h, m = map(int, hora_str.split(':'))
            return h * 60 + m
        except:
            return -1

    lista_fusionada = []

    # listas de control para evitar emparejar elementos que ya hayan sido emparejados
    salidas_emparejadas = [False] * len(departures)
    llegadas_emparejadas = [False] * len(arrivals)

    # 1. Intentar emparejar cada llegada con su salida correspondiente y compatible
    i = 0
    while i < len(arrivals):
        llegada = arrivals[i]
        minutos_llegada = a_minutos(llegada.time)

        # busca una salida compatible para este mismo avión
        j = 0
        encontrado = False
        while j < len(departures):
            salida = departures[j]

            if llegada.codigo == salida.codigo and not salidas_emparejadas[j]:
                minutos_salida = a_minutos(salida.departure_time)

                # verificamos que la salida ocurre DESPUÉS de la llegada
                if minutos_llegada < minutos_salida:
                    # creamos un nuevo objeto Aircraft con la información fusiona
                    avion_fusionado = Aircraft(llegada.codigo, llegada.company, llegada.origin, llegada.time)
                    avion_fusionado.destination = salida.destination
                    avion_fusionado.departure_time = salida.departure_time

                    lista_fusionada.append(avion_fusionado)
                    salidas_emparejadas[j] = True
                    llegadas_emparejadas[i] = True
                    encontrado = True
                    break                                      #emparejado con la primera salida cronológicamente válida
            j += 1

        # si el avión no tiene ninguna salida compatible, se guarda solamente como llegada
        if not encontrado:
            avion_solo_llegada = Aircraft(llegada.codigo, llegada.company, llegada.origin, llegada.time)
            lista_fusionada.append(avion_solo_llegada)
            llegadas_emparejadas[i] = True

        i += 1

    # 2. Añadir los aviones que no han tenido llegada, solamente salida (aviones nocturnos / de base)
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

# ======================================================================================================================
# DETECCIÓN DE AVIONES NOCTURNOS (NIGHT_AIRCRAFT)
# ======================================================================================================================
def NightAircraft(aircrafts):
    """ INPUT:          -> aircrafts: la lista de objetos Aircraft (normalmente lista ya fusionada)

        OUTPUT:         -> lista_nocturnos: la lista de aviones que han pasado la noche en el aeropuerto
                        -> -1: si la lista de entrada está vacía

        DESCRIPTION:    -> identifica los aviones que no tienen información de llegada (origin o time == "") pero SÍ tienen una hora de salida asignada
                        -> estos aviones se considerarán "aeronaves nocturnas" o de base en el aeropuerto
    """

    # comprobar que la lista contiene aeronaves antes de procesarla
    if not aircrafts:
        print("Error: La lista de aeronaves proporcionada está vacía.")
        return -1

    lista_nocturnos = []
    i = 0

    # recorremos todas las aeronaves de la lista
    while i < len(aircrafts):
        avion = aircrafts[i]

        # un avión es nocturno o pernoctó si SOLO tiene información de salida, por lo tanto NO tiene origen/hora de llegada
        if (avion.time == "" or avion.origin == "") and avion.departure_time != "":
            lista_nocturnos.append(avion)

        i += 1

    return lista_nocturnos


# ======================================================================================================================
# DISTRIBUCIÓN HORARIA DE LLEGADAS (PLOT_ARRIVALS)
# ======================================================================================================================
def plot_arrivals(lista_de_vuelos):
    """ INPUT:          -> lista_de_vuelos: la lista de objetos Aircraft

        OUTPUT:         -> TRUE: si el gráfico se genera correctamente
                        -> FALSE: si la lista está vacía o ocurre un error

        DESCRIPTION:    -> genera un gráfico de barras que representar la distribución horaria de las llegadas
                        -> (solamente se tiene en cuenta la hora de llegada para hacer la distribución horaria)
    """
    # comprobamos que existen vuelos cargados antes de generar el gráfico
    if not lista_de_vuelos:
        print("Error", "No hay datos cargados.")
        return False

    try:
        # extrae únicamente la hora de llegada hh
        horas_formato = []
        for obj in lista_de_vuelos:
            hora_str = obj.time.split(':')[0]
            horas_formato.append(int(hora_str))

        # contabiliza cuántos vuelos llegan en cada hora del día
        cont_hora = [0] * 24
        for hora in horas_formato:
            if 0 <= hora < 24:
                cont_hora[hora] += 1

        # datos para representar el gráfico
        eje_x = list(range(24))
        eje_y = cont_hora

        plt.figure(figsize=(10, 5))
        plt.bar(eje_x, eje_y, color='blue', edgecolor='black')
        plt.title("Vuelos por Hora de Llegada")
        plt.xlabel("Hora del día")
        plt.ylabel("Cantidad de aviones")
        plt.xticks(eje_x)                                                   #mostrar todas las horas del día (de 00:00 a 23:00)
        plt.grid(axis='y', linestyle='--', alpha=0.4)

        plt.show()
        return True

    except AttributeError:
        print("Error", "Los objetos cargados no tienen el atributo '.time'")
        return False


# ======================================================================================================================
# GUARDAR VUELOS EN FICHERO (SAVE_FLIGHTS)
# ======================================================================================================================
def save_flights(aircrafts, filename):
    """ INPUT:          -> aircrafts: lista de objetos Aircraft
                        -> filename: nombre del fichero de salida

        OUTPUT:         -> TRUE: si el fichero se genera correctamente
                        -> FALSE: si la lista está vacía

        DESCRIPTION:    -> guarda la información de los vuelos en un fichero de texto utilizando el mismo formato que el fichero original de entrada
                        -> los campos vacíos se representan símbolo "-"
    """
    # comprobamos que existen vuelos para guardar
    if not aircrafts:
        return False
    f = open(filename, 'w')
    f.write("AIRCRAFT ORIGIN ARRIVAL AIRLINE\n")
    # sustituimos los campos vacíos por "-"
    for aircraft in aircrafts:
        aid = aircraft.codigo if aircraft.codigo else "-"
        origin = aircraft.origin if aircraft.origin else "-"
        time = aircraft.time if aircraft.time else "-"
        company = aircraft.company if aircraft.company else "-"

        f.write(f"{aid} {origin} {time} {company}\n")
    f.close()
    return True


# ======================================================================================================================
# ESTADÍSTICAS DE COMPAÑÍAS AEREAS (PLOT_AIRLINES)
# ======================================================================================================================
def plot_airlines(lista_vols, airlines_selected=None):
    """ INPUT:          -> lista_vol: la lista de objetos Aircraft

        OUTPUT:         -> TRUE: si el gráfico se genera correctamente
                        -> FALSE: si la lista está vacía

        DESCRIPTION:    -> genera un gráfico de barras que representa el número de vuelos operados por cada compañía
                        -> cada barra corresponde a una compañía, su altura indica la cantidad de vuelos
    """
    # comprobamos que existen vuelos cargados antes de generar el gráfico
    if len(lista_vols) == 0:
        print("Error: No hay vuelos cargados.")
        return False

    nombres_agencias = []
    conteos = []

    # recorremos todos los vuelos de la lista
    v = 0
    while v < len(lista_vols):
        avion = lista_vols[v]
        agencia_actual = avion.company

        # --- NUEVO FILTRO ---
        # si el usuario ha seleccionado aerolíneas específicas y la actual no está en la lista, la ignoramos
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

        # comprobamos si la agencia ya está registrada en nuestras listas del gráfico
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

    # si después del filtro no queda ninguna aerolínea para pintar
    if len(nombres_agencias) == 0:
        print("Error: Ninguna de las aerolíneas seleccionadas tiene vuelos cargados.")
        return False

    # generamos del gráfico
    plt.figure(figsize=(12, 5))                                                         # reducido un poco el ancho para que quede más estético si son pocas
    plt.bar(nombres_agencias, conteos, color='orange', edgecolor='black')

    plt.title("Airlines Statistics (Filtered)")
    plt.xlabel("Agencies")
    plt.ylabel("Number of Aircraft")
    plt.xticks(rotation=45)
    plt.xticks(fontsize=8)
    plt.grid(axis='y', linestyle='--', alpha=0.3)

    plt.show()
    return True


# ======================================================================================================================
# DISTRIBUCIÓN DE VUELOS SCHENGEN / NO SCHENGEN (PLOT_FLIGHTS_TYPE)
# ======================================================================================================================
def plot_flights_type(aircrafts):
    """ INPUT:          -> aircrafts: la lista de objetos Aircraft

        OUTPUT:         -> TRUE: si el gráfico se genera correctamente
                        -> FALSE: si la lista está vacía

        DESCRIPTION:    -> genera un gráfico de barras que representa ela cantidad de vuelos procedentes de países Schengen o Non-Schengen
                        -> la clasificación se hace con el prefijo del código ICAO
    """
    # comprobamos que existen vuelos cargados antes de generar el gráfico
    if len(aircrafts) == 0:
        print("Error: No hay vuelos cargados.")
        return False

    schengen_prefixes = [
        'LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG', 'EH', 'LH', 'BI',
        'LI', 'EV', 'EY', 'EL', 'LM', 'EN', 'EP', 'LP', 'LZ', 'LJ', 'LE', 'ES', 'LS'
    ]

    total_schengen = 0
    total_no_schengen = 0

    # contabiliza los vuelos según el tipo de origen de los vuelos
    for avion in aircrafts:
        prefijo = avion.origin[:2]
        if prefijo in schengen_prefixes:
            total_schengen += 1
        else:
            total_no_schengen += 1

    # prepara los datos para representar el gráfico
    ejes_x = ['Schengen', 'Non-Schengen']
    ejes_y = [total_schengen, total_no_schengen]
    # genera el gráfico de barras
    plt.figure(figsize=(8, 6))
    colores = ['green', 'red']
    plt.bar(ejes_x, ejes_y, color=colores, edgecolor='black')
    plt.title("Total Flights by Origin Type")
    plt.xlabel("Type of Origin")
    plt.ylabel("Number of Aircraft")

    # muestra el valor númerico sobre cada barra
    for i in range(len(ejes_y)):
        plt.text(i, ejes_y[i] + 0.1, str(ejes_y[i]), ha='center', va='bottom', fontsize=12)

    plt.grid(axis='y', linestyle='--', alpha=0.3)
    plt.show()

    return True


# ======================================================================================================================
# TRAYECTORIAS EN GOOGLE EARTH
# ======================================================================================================================
def map_flights(aircrafts, airports):
    """ INPUT:          -> aircrafts: la lista de objetos Aircraft
                        -> airports: la lista de objetos Airport

        OUTPUT:         -> genera un fichero "flights_map.kml" y lo abre automáticamente en Google Earth

        DESCRIPTION:    -> representa las trayectorias de llegada hacia LEBL con lineas KML
                        -> las trayectorias se califican según el tipo (Schengen, Non-Schengen) utilizando colores
    """
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
        # búsqueda del aeropuerto de origen asociado al vuelo
        j = 0
        encontrado = False
        while j < len(airports):
            if airports[j].code == avion.origin:
                origen = airports[j]
                encontrado = True
            j += 1
        # ignoramos el vuelo si no se encuentra un aeropuerto de origen
        if not encontrado:
            i += 1
            continue

        # determina el tipo de origen con el prefijo para asignar el color de la trayectoria
        prefix = avion.origin[:2]
        schengen_prefixes = [
            'LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG', 'EH', 'LH', 'BI',
            'LI', 'EV', 'EY', 'EL', 'LM', 'EN', 'EP', 'LP', 'LZ', 'LJ', 'LE', 'ES', 'LS'
        ]
        if prefix in schengen_prefixes:
            color = "ffff0000"  # azul
        else:
            color = "ff00ff00"  # verde

        f.write('<Placemark>\n')
        f.write('<Style><LineStyle><color>' + color + '</color><width>3</width></LineStyle></Style>\n')                 #hace que las lineas sean bien visibles
        f.write('<LineString>\n')
        f.write('<tessellate>1</tessellate>\n')                                                                         #mejora la curvatura de las líneas
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


# ======================================================================================================================
# HAVERSINE DISTANCE (HAVERSINE)
# ======================================================================================================================
def Haversine(lat1, lon1, lat2, lon2):
    """ INPUT:          -> lat1, lon1: coordenadas del origen
                        ->lat2, lon2 -> coordenadas del destino

        OUTPUT:         -> la distancia entre ambos puntos (que son los aeropuertos) en kilómetros

        DESCRIPTION:    -> utilizamos la fórmula de Haversine para calcular distancias sobre la Tierra
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


# ======================================================================================================================
# VUELOS DE LARGA DISTANCIA (+2000KM)
# ======================================================================================================================
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
