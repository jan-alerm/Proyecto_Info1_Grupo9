import os

class Gate:
    def __init__(self, name):
        self.name = name
        self.occupied = False
        self.aircraft_id = None


class BoardingArea:
    def __init__(self, name, area_type):
        self.name = name
        self.type = area_type                                                           # 'schengen' or 'non-schengen'
        self.gates = []


class Terminal:
    def __init__(self, name):
        self.name = name
        self.boarding_areas = []
        self.airline_icao_codes = []


class BarcelonaAP:
    def __init__(self, code):
        self.code = code
        self.terminals = []


def set_gates(area, init_gate, end_gate, prefix):
    """
    Updates the list of gates of a boarding area.
    Returns -1 if end_gate is not greater than init_gate.
    """
    if end_gate <= init_gate:
        return -1

    area.gates = []

    for i in range(init_gate, end_gate + 1):
        gate_name = prefix + str(i)
        new_gate = Gate(gate_name)
        area.gates.append(new_gate)

    return True

#=========================================== CARGAR AEROLÍNEAS POR TERMINAL ============================================
def load_airlines(terminal, t_name):
#FUNCIÓN: carga las aerolíneas que tocan a una terminal desde los ficheros T1_airlines.txt o T2_airlines.txt
#         si el fichero no existe, se devuelve false

    if t_name == "T1" or t_name == "T2":
        terminal_name = t_name + "_Airlines.txt"
    else:
        print("No hay terminal con ese nombre")
        return False

    #Si no se encuentra el fichero de esa terminal:
    try:
        f = open(terminal_name, "r")
    except FileNotFoundError:
        print("The file is not found")
        return False

    nueva_lista = []                                                           #lee la primera línea
    line = f.readline()                                                        #nueva lista vacía para añadir aerolineas

    while line != "":
        # 1. Primero eliminamos el salto de línea invisible (\n) si existe
        line_limpia = line.replace("\n", "").replace("\r", "")

        # 2. Ahora sí, extraemos estrictamente los 3 últimos caracteres de esa línea limpia
        codigo = line_limpia[-3:]

        if codigo:
            nueva_lista.append(codigo)

        line = f.readline()

    f.close()
    terminal.airline_icao_codes = nueva_lista                               #actualizamos la nueva lista en la terminal
    return True

#=========================================== CARGAR "ESTRUCTURA DEL AEROPUERTO" ========================================
def load_airport_structure(filename):
#FUNCIÓN: crea un "objeto" BarcelonaAP utilizando la información guardada en el fichero LEBL.txt
#         la función transforma los datos del fichero para construir la estructura que se entiende:
#          - terminales
#          - boarding areas
#          - gates
#         además de cargar las aerolíneas correspondientes a cada terminal
#         importante que la estructura del documento "terminals": AREA LETTER SCHENGEN/NON SCHENGEN GATES NUM_GATES

    try:
        f = open(filename, "r")
    except FileNotFoundError:
        print("The file is not found")
        return False

    # LEBL tiene 2 terminals
    first_line = f.readline().split()
    airport_code = first_line[0]
    bcn = BarcelonaAP(airport_code)
    line = f.readline()

    while line != "":
        elementos = line.split()

#       -------------TERMINAL--------------
        if elementos[0] == "Terminal":
            terminal_name = elementos[1]
            nueva_terminal = Terminal(terminal_name)
#           cargar las aerolíneas de cada terminal
            load_airlines(nueva_terminal, terminal_name)
            num_areas = int(elementos[2])
            i = 0

            while i < num_areas:
                area_line = f.readline().split()
                #transformar distribución del documento
                area_name = area_line[1]
                area_type = area_line[2]
                init_gate = int(area_line[4])
                end_gate = int(area_line[6])
                nueva_area = BoardingArea(area_name, area_type)

                #definir el prefijo para ver si schengen / non schengen
                prefix = terminal_name + area_name + "G"
                set_gates(nueva_area, init_gate, end_gate, prefix)
                nueva_terminal.boarding_areas.append(nueva_area)

                i = i + 1

            bcn.terminals.append(nueva_terminal)
        line = f.readline()
    f.close()
    return bcn

#=========================================== OCUPACIÓN DE LAS "GATES" TERMINALES =======================================
def gate_occupancy(bcn):
#FUNCIÓN: devuelve una lista del estado de ocupación de todas las puertas ("gates") del aeropuerto (T1 y T2)

    lista_ocupacion = []
    i = 0

    while i < len(bcn.terminals):
        terminal = bcn.terminals[i]
        j = 0
        while j < len(terminal.boarding_areas):
            area = terminal.boarding_areas[j]
            a = 0
            while a < len(area.gates):
                gate = area.gates[a]

                if gate.occupied:
                    estado = "Ocupado"
                    aircraft = gate.aircraft_id
                else:
                    estado = "Free"
                    aircraft = "-"

                info_gate = [gate.name, estado, aircraft]
                lista_ocupacion.append(info_gate)

                a = a + 1

            j = j + 1

        i = i + 1

    return lista_ocupacion

#======================================== COMPROBAR AEROLÍNEA A TERMINAL CORRECTA ======================================
def is_airline_in_terminal(terminal, name):
#FUNCIÓN: comprueba si una aerolínea está operando en la terminal correcto ("asignada")
    if name == "":
        return False
    if len(terminal.airline_icao_codes) == 0:
        return False

    i = 0
    while i < len(terminal.airline_icao_codes):
        if terminal.airline_icao_codes[i] == name:
            return True
        i = i + 1
    return False

#-----------------------------------------------------------------------------------------------------------------------
def SearchTerminal(bcn, name):

    # Iniciamos la i en 0 para recorrer las terminales del aeropuerto
    i = 0

    # Recorremos la lista de terminales de bcn usando un while
    while i < len(bcn.terminals):
        terminal_actual = bcn.terminals[i]

        # Comprobamos si la aerolínea opera en la terminal actual
        if is_airline_in_terminal(terminal_actual, name):
            return terminal_actual.name  # Si la encuentra, devuelve el nombre de la terminal ("T1", "T2")

        i = i + 1

    # Si termina el bucle y no se ha encontrado en ninguna terminal, devolvemos un string vacío
    return ""


def AssignGate(bcn, aircraft):
    """
    Given bcn of class BarcelonaAP and an aircraft of class Aircraft, this
    function looks for the first gate that is not occupied in the correct boarding
    area for this specific flight.
    """
    # 1. Encontrar la terminal de la aerolínea (T1 o T2)
    terminal_name = SearchTerminal(bcn, aircraft.company)

    if terminal_name == "Error" or not terminal_name:
        return -1  # Error: Aerolínea no registrada

    # 2. Determinar zona (schengen / non-schengen)
    from airport import is_schengen_airport
    if is_schengen_airport(aircraft.origin):
        flight_type = "schengen"
    else:
        flight_type = "non-schengen"

    # 3. Buscar la primera puerta libre en la zona correspondiente
    i = 0
    while i < len(bcn.terminals):
        terminal_actual = bcn.terminals[i]

        if terminal_actual.name == terminal_name:
            j = 0
            while j < len(terminal_actual.boarding_areas):
                area_actual = terminal_actual.boarding_areas[j]

                if area_actual.type.lower() == flight_type:
                    g = 0
                    while g < len(area_actual.gates):
                        gate_actual = area_actual.gates[g]

                        if not gate_actual.occupied:
                            # Asignación segura en el objeto
                            gate_actual.occupied = True
                            gate_actual.aircraft_id = aircraft.codigo
                            return gate_actual.name  # Retornamos el nombre de la puerta (ej: 'B14')
                        g += 1
                j += 1
        i += 1

    return -2  # Error: No quedan puertas libres en esta zona

#-----------------------------------------------------------------------------------------------------------------------
def FreeGate(bcn, gate_name):
    i = 0
    while i < len(bcn.terminals):

        terminal = bcn.terminals[i]
        j = 0
        while j < len(terminal.boarding_areas):

            area = terminal.boarding_areas[j]
            k = 0
            while k < len(area.gates):
                gate = area.gates[k]

                if gate.name == gate_name:
                    gate.occupied = False
                    gate.aircraft_id = None
                    return True

                k += 1

            j += 1

        i += 1

    return False

#----------------------------------------------------------------------------------------------------------------------
def AssignNightGates(bcn, aircrafts):
    if not aircrafts:
        return -1
    asignados = []
    i = 0
    while i < len(aircrafts):
        avion = aircrafts[i]

        if (avion.time == "" or avion.origin == "") and avion.departure_time != "":
            puerta = AssignGate(bcn, avion)

            if puerta != -1 and puerta != -2:
                asignados.append([avion.codigo, puerta])

        i += 1

    return asignados


# ======================================================================================
# FASE 4: ASIGNACIÓN DINÁMICA DE PUERTAS POR FRANJA HORARIA
# ======================================================================================

def a_minutos_lebl(hora_str):
    """Función auxiliar para transformar un formato hh:mm a minutos totales desde las 00:00."""
    if not hora_str or hora_str == "" or hora_str == "-":
        return -1
    try:
        parts = hora_str.split(':')
        h = int(parts[0])
        m = int(parts[1])
        return h * 60 + m
    except:
        return -1


def AssignGatesAtTime(bcn, aircrafts, time_str):

    minutos_inicio = a_minutos_lebl(time_str)
    if minutos_inicio == -1:
        return 0
    minutos_fin = minutos_inicio + 60  # Ventana temporal de 60 minutos

    # Importación local de la función necesaria de airport.py para cruzar datos geográficos
    from airport import is_schengen_airport

    # ----------------------------------------------------------------------------------
    # PASO 1: RECORRER Y LIBERAR LAS GATES CON AVIONES QUE YA HAN DESPEGADO
    # ----------------------------------------------------------------------------------
    t = 0
    while t < len(bcn.terminals):
        terminal = bcn.terminals[t]
        a = 0
        while a < len(terminal.boarding_areas):
            area = terminal.boarding_areas[a]
            g = 0
            while g < len(area.gates):
                puerta = area.gates[g]

                # Si la puerta está ocupada, verificamos si el avión ya ha salido del aeropuerto
                if puerta.occupied and puerta.aircraft_id is not None:
                    matricula_avion = puerta.aircraft_id

                    # Buscamos este avión en el registro general de movimientos
                    v = 0
                    ha_despegado = False
                    while v < len(aircrafts):
                        avion = aircrafts[v]
                        if avion.codigo == matricula_avion and avion.departure_time != "":
                            min_salida = a_minutos_lebl(avion.departure_time)
                            # Si la hora de salida es anterior o igual a la hora actual simulada, queda libre
                            if min_salida != -1 and min_salida <= minutos_inicio:
                                ha_despegado = True
                                break
                        v += 1

                    if ha_despegado:
                        puerta.occupied = False
                        puerta.aircraft_id = None
                g += 1
            a += 1
        t += 1

    # ----------------------------------------------------------------------------------
    # PASO 2: ASIGNAR PUERTAS A LOS AVIONES QUE ATERRIZAN EN ESTA HORA
    # ----------------------------------------------------------------------------------
    aviones_sin_puerta = 0
    i = 0
    while i < len(aircrafts):
        avion = aircrafts[i]

        # Filtramos los aviones que aterrizan exclusivamente dentro de la hora evaluada
        if avion.time != "":
            min_llegada = a_minutos_lebl(avion.time)
            if minutos_inicio <= min_llegada < minutos_fin:

                # 2.1 Encontrar la terminal de la aerolínea (T1 o T2) usando SearchTerminal
                terminal_name = SearchTerminal(bcn, avion.company)

                if not terminal_name:
                    # Si la aerolínea no está registrada, no se puede asignar
                    aviones_sin_puerta += 1
                    i += 1
                    continue

                # 2.2 Determinar la zona requerida (schengen / non-schengen) con el módulo airport
                if is_schengen_airport(avion.origin):
                    flight_type = "schengen"
                else:
                    flight_type = "non-schengen"

                # 2.3 Buscar la primera puerta libre en la terminal y zona adecuadas
                asignado = False
                t_idx = 0
                while t_idx < len(bcn.terminals):
                    terminal_actual = bcn.terminals[t_idx]

                    if terminal_actual.name == terminal_name:
                        b_idx = 0
                        while b_idx < len(terminal_actual.boarding_areas):
                            area_actual = terminal_actual.boarding_areas[b_idx]

                            if area_actual.type.lower() == flight_type:
                                g_idx = 0
                                while g_idx < len(area_actual.gates):
                                    gate_actual = area_actual.gates[g_idx]

                                    if not gate_actual.occupied:
                                        gate_actual.occupied = True
                                        gate_actual.aircraft_id = avion.codigo
                                        asignado = True
                                        break
                                    g_idx += 1
                            if asignado:
                                break
                            b_idx += 1
                    if asignado:
                        break
                    t_idx += 1

                if not asignado:
                    aviones_sin_puerta += 1

        i += 1

    return aviones_sin_puerta


# Asegurar el mapeo de compatibilidad con minúsculas requerido por la interfaz
search_terminal = SearchTerminal
