class Gate:
    def __init__(self, name):
        self.name = name
        self.occupied = False
        self.aircraft_id = None


class BoardingArea:
    def __init__(self, name, area_type):
        self.name = name
        self.type = area_type  # 'Schengen' or 'non-Schengen'
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


def SetGates(area, init_gate, end_gate, prefix):
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

def LoadAirlines(terminal, t_name):
    # Si el nombre de la terminal no concuerda con el de los ficheros:
    if t_name == "T1" or t_name == "T2":
        terminal_name = t_name+"_Airlines.txt"
    else:
        print("No terminal with that name")
        return False

    #Si no se encuentra el fichero de esa terminal:
    try:
        f = open(terminal_name, "r")
    except FileNotFoundError:
        print("The file is not found")
        return False


    line = f.readline() # Lee la primera línea
    nueva_lista = [] # Crea una nueva lista vacía para añadirle las nuevas aerolíneas

    while line != "":
        codigo = line[-3:] # Solo nos interesa el ICAO code de la aerolínea que son los últimos tres carácteres
        nueva_lista.append(codigo)
        line = f.readline()

    f.close()
    terminal.airline_icao_codes = nueva_lista # Actualizamos la nueva lista en la terminal
    return True


