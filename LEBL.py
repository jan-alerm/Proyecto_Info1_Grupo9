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
