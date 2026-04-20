
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

    def f_plot_arrivals(self):
        if not self.lista_aeropuertos:
            messagebox.showwarning("Error", "No hay datos cargados. Usa el botón 1 primero.")
            return

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
