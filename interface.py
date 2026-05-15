import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Importamos tus funciones originales
from airport import *
from Aircraft import *


class AirportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EETAC - Advanced Dynamic Dashboard v3.1")
        self.root.geometry("1300x900")
        self.root.configure(bg="#f4f6f7")

        # Variables de datos de tus archivos originales
        self.lista_aeropuertos = []
        self.lista_vuelos = []

        # CAMBIO: Ahora los apartados inician cerrados (False)
        self.airports_visible = False
        self.flights_visible = False

        # --- ESTILOS ---
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Segoe UI", 10), padding=4)
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), background="#f4f6f7", foreground="#2c3e50")
        self.style.configure("Toggle.TButton", font=("Segoe UI", 10, "bold"), foreground="#2c3e50")

        # --- LAYOUT PRINCIPAL ---
        header = ttk.Label(self.root, text="SISTEMA DE GESTIÓN AEROPORTUARIA", style="Header.TLabel")
        header.pack(pady=15)

        # Contenedor central
        self.main_container = tk.Frame(self.root, bg="#f4f6f7")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=5)

        # Panel Izquierdo (Controles y Botones)
        self.button_frame = tk.Frame(self.main_container, bg="#f4f6f7")
        self.button_frame.pack(side="left", fill="y", padx=10)

        # Panel Derecho (Contenedor de Gráficos Integrados)
        self.plot_frame = tk.LabelFrame(self.main_container, text="Panel de Visualización Integrado", bg="white",
                                        font=("Segoe UI", 11, "bold"), fg="#34495e")
        self.plot_frame.pack(side="right", fill="both", expand=True, padx=10, pady=5)

        # Mensaje por defecto en el panel de gráficos
        self.show_welcome_message()

        # Construir menús desplegables
        self.setup_collapsible_menus()

        # Barra de estado inferior
        self.status_var = tk.StringVar(value="Listo | Aeropuertos cargados: 0 | Vuelos cargados: 0")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief="sunken", anchor="w",
                                   font=("Consolas", 10), bg="#bdc3c7")
        self.status_bar.pack(side="bottom", fill="x")

    def show_welcome_message(self):
        """Muestra el mensaje inicial neutro en el panel derecho"""
        self.no_plot_label = tk.Label(
            self.plot_frame,
            text="Panel libre.\n\nCarga los ficheros correspondientes y haz clic en\ncualquier botón de gráfico estadístico para visualizarlo aquí.",
            font=("Segoe UI", 11, "italic"),
            bg="white",
            fg="#7f8c8d"
        )
        self.no_plot_label.pack(expand=True)

    def setup_collapsible_menus(self):
        """Configura las secciones colapsables (Inician contraídas)"""

        # ================= SECCIÓN 1: AEROPUERTOS =================
        # CAMBIO: El texto inicial ahora tiene '▲' indicando que está cerrado
        self.btn_toggle_airports = ttk.Button(self.button_frame, text="▲ GEOMETRÍA Y AEROPUERTOS",
                                              style="Toggle.TButton", width=35, command=self.toggle_airports_panel)
        self.btn_toggle_airports.pack(fill="x", pady=(5, 0))

        # Contenedor interno de los botones de aeropuertos
        self.airports_content = tk.Frame(self.button_frame, bg="#f4f6f7", bd=1, relief="groove")
        # CAMBIO: No le hacemos .pack() aquí para que inicie oculto

        ttk.Button(self.airports_content, text="Cargar Archivo Aeropuertos...", width=33, command=self.f_load).pack(
            pady=2, padx=5)
        ttk.Button(self.airports_content, text="Calcular Atributo Schengen", width=33, command=self.f_schengen).pack(
            pady=2, padx=5)
        ttk.Button(self.airports_content, text="Mostrar Datos (Terminal)", width=33, command=self.f_show).pack(pady=2,
                                                                                                               padx=5)
        ttk.Button(self.airports_content, text="Guardar Schengen a Fichero...", width=33, command=self.f_save).pack(
            pady=2, padx=5)
        ttk.Button(self.airports_content, text="Ver Aeropuertos en Google Earth (KML)", width=33,
                   command=self.f_map).pack(pady=2, padx=5)
        ttk.Button(self.airports_content, text="Gráfico: Schengen vs No Schengen", width=33,
                   command=self.f_plot_airports_embedded).pack(pady=2, padx=5)

        # Sub-zona para borrar dentro del mismo bloque
        delete_zone = tk.LabelFrame(self.airports_content, text="Eliminar Aeropuerto por Código", bg="#f4f6f7",
                                    font=("Segoe UI", 9, "bold"))
        delete_zone.pack(fill="x", pady=5, padx=5)
        tk.Label(delete_zone, text="ICAO:", bg="#f4f6f7", font=("Segoe UI", 9)).pack(side="left", padx=2, pady=2)
        self.delete_entry = ttk.Entry(delete_zone, width=8, font=("Segoe UI", 10, "bold"))
        self.delete_entry.pack(side="left", padx=2, pady=2)
        ttk.Button(delete_zone, text="Eliminar", width=8, command=self.f_delete_dynamic).pack(side="right", padx=2,
                                                                                              pady=2)

        # ================= SECCIÓN 2: OPERACIONES (ARRIVALS) =================
        # CAMBIO: El texto inicial ahora tiene '▲' indicando que está cerrado
        self.btn_toggle_flights = ttk.Button(self.button_frame, text="▲ OPERACIONES Y TRÁFICO", style="Toggle.TButton",
                                             width=35, command=self.toggle_flights_panel)
        self.btn_toggle_flights.pack(fill="x", pady=(5, 0))

        # Contenedor interno de los botones de operaciones
        self.flights_content = tk.Frame(self.button_frame, bg="#f4f6f7", bd=1, relief="groove")
        # CAMBIO: Tampoco hacemos .pack() aquí para que empiece oculto

        ttk.Button(self.flights_content, text="Cargar Archivo Operaciones...", width=33,
                   command=self.f_load_arrivals).pack(pady=2, padx=5)
        ttk.Button(self.flights_content, text="Gráfico: Frecuencia Horaria", width=33,
                   command=self.f_plot_arrivals_embedded).pack(pady=2, padx=5)
        ttk.Button(self.flights_content, text="Gráfico: Vuelos por Aerolínea", width=33,
                   command=self.f_plot_airlines_embedded).pack(pady=2, padx=5)
        ttk.Button(self.flights_content, text="Gráfico: Vuelos por Origen (Schengen)", width=33,
                   command=self.f_plot_type_embedded).pack(pady=2, padx=5)
        ttk.Button(self.flights_content, text="Guardar Vuelos a Fichero...", width=33,
                   command=self.f_save_flights).pack(pady=2, padx=5)
        ttk.Button(self.flights_content, text="Ver Trayectorias en Google Earth", width=33,
                   command=self.f_map_flights).pack(pady=2, padx=5)
        ttk.Button(self.flights_content, text="Filtrar Larga Distancia (>2000km)", width=33,
                   command=self.f_long_flights).pack(pady=2, padx=5)

        # Botón de salida global fijado abajo del frame
        ttk.Button(self.button_frame, text="SALIR DE LA APLICACIÓN", width=35, command=self.root.quit).pack(
            side="bottom", pady=15)

    # --- CONTROLADORES DE LOS DESPLEGABLES ---
    def toggle_airports_panel(self):
        """Muestra u oculta la sección de aeropuertos"""
        if self.airports_visible:
            self.airports_content.pack_forget()
            self.btn_toggle_airports.configure(text="▲ GEOMETRÍA Y AEROPUERTOS")
            self.airports_visible = False
        else:
            self.airports_content.pack(fill="x", padx=2, pady=(0, 10), after=self.btn_toggle_airports)
            self.btn_toggle_airports.configure(text="▼ GEOMETRÍA Y AEROPUERTOS")
            self.airports_visible = True

    def toggle_flights_panel(self):
        """Muestra u oculta la sección de vuelos"""
        if self.flights_visible:
            self.flights_content.pack_forget()
            self.btn_toggle_flights.configure(text="▲ OPERACIONES Y TRÁFICO")
            self.flights_visible = False
        else:
            self.flights_content.pack(fill="x", padx=2, pady=(0, 10), after=self.btn_toggle_flights)
            self.btn_toggle_flights.configure(text="▼ OPERACIONES Y TRÁFICO")
            self.flights_visible = True

    # --- LÓGICA DE ACTUALIZACIÓN Y LIMPIEZA ---
    def update_status(self):
        self.status_var.set(
            f"Estado: Base de datos sincronizada | Aeropuertos: {len(self.lista_aeropuertos)} | Vuelos: {len(self.lista_vuelos)}")

    def clear_plot_frame(self):
        if self.no_plot_label.winfo_exists():
            self.no_plot_label.pack_forget()
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

    # --- MÉTODOS DE DATOS Y EVENTOS ---
    def f_load(self):
        path = filedialog.askopenfilename(title="Abrir base de datos de aeropuertos",
                                          filetypes=[("Text files", "*.txt")])
        if path:
            self.lista_aeropuertos = load_airports(path)
            messagebox.showinfo("Éxito", f"Cargados {len(self.lista_aeropuertos)} aeropuertos.")
            self.update_status()
            self.clear_plot_frame()
            self.show_welcome_message()

    def f_load_arrivals(self):
        path = filedialog.askopenfilename(title="Abrir registro de llegadas (Arrivals)",
                                          filetypes=[("Text files", "*.txt")])
        if path:
            self.lista_vuelos = load_arrivals(path)
            messagebox.showinfo("Éxito", f"Cargados {len(self.lista_vuelos)} vuelos.")
            self.update_status()
            self.clear_plot_frame()
            self.show_welcome_message()

    def f_delete_dynamic(self):
        codigo_a_borrar = self.delete_entry.get().strip().upper()
        if not codigo_a_borrar:
            messagebox.showwarning("Campo vacío", "Introduce un código ICAO.")
            return

        res = remove_airport(self.lista_aeropuertos, codigo_a_borrar)
        if res == 1:
            messagebox.showinfo("Éxito", f"El aeropuerto {codigo_a_borrar} eliminado.")
            self.delete_entry.delete(0, tk.END)
            self.update_status()
            self.clear_plot_frame()
            self.show_welcome_message()
        else:
            messagebox.showerror("Error", f"El aeropuerto {codigo_a_borrar} no se encuentra.")

    def f_schengen(self):
        if not self.lista_aeropuertos:
            messagebox.showwarning("Atención", "No hay aeropuertos cargados.")
            return
        for a in self.lista_aeropuertos:
            set_schengen(a)
        messagebox.showinfo("Éxito", "Atributos Schengen mapeados.")

    def f_save(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="solo_schengen.txt",
                                            filetypes=[("Text files", "*.txt")])
        if path:
            res = save_schengen_airports(self.lista_aeropuertos, path)
            if res == 1:
                messagebox.showinfo("Éxito", "Fichero Schengen guardado.")
            else:
                messagebox.showwarning("Error", "No hay datos para guardar.")

    def f_save_flights(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="saved_arrivals.txt",
                                            filetypes=[("Text files", "*.txt")])
        if path:
            if save_flights(self.lista_vuelos, path):
                messagebox.showinfo("Éxito", "Registro de vuelos guardado.")
            else:
                messagebox.showerror("Error", "La lista de vuelos está vacía.")

    # ================= MÉTODOS DE GRÁFICOS INTEGRADOS =================
    def f_plot_airports_embedded(self):
        if not self.lista_aeropuertos:
            messagebox.showerror("Error", "No hay aeropuertos cargados.")
            return
        self.clear_plot_frame()
        schengen = sum(1 for a in self.lista_aeropuertos if a.schengen)
        not_schengen = len(self.lista_aeropuertos) - schengen

        fig, ax = plt.subplots(figsize=(5, 5))
        labels = ["Aeropuertos"]
        ax.bar(labels, [schengen], label="Schengen", color="#2980b9", width=0.4)
        ax.bar(labels, [not_schengen], bottom=[schengen], label="Not Schengen", color="#e74c3c", width=0.4)
        ax.set_ylabel("Cantidad")
        ax.set_title("Estadística de Espacio Schengen")
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.5)

        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        plt.close(fig)

    def f_plot_arrivals_embedded(self):
        if not self.lista_vuelos:
            messagebox.showerror("Error", "No hay registros de vuelos cargados.")
            return
        self.clear_plot_frame()
        horas_formato = [int(obj.time.split(':')[0]) for obj in self.lista_vuelos]
        cont_hora = [0] * 24
        for hora in horas_formato:
            if 0 <= hora < 24:
                cont_hora[hora] += 1

        fig, ax = plt.subplots(figsize=(6, 4))
        eje_x = list(range(24))
        ax.bar(eje_x, cont_hora, color='#8e44ad', edgecolor='black')
        ax.set_title("Frecuencia de Vuelos por Hora de Llegada")
        ax.set_xlabel("Hora del día")
        ax.set_ylabel("Aviones")
        ax.set_xticks(eje_x)
        ax.grid(axis='y', linestyle='--', alpha=0.4)

        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        plt.close(fig)

    def f_plot_airlines_embedded(self):
        if not self.lista_vuelos:
            messagebox.showerror("Error", "No hay vuelos cargados.")
            return
        self.clear_plot_frame()
        nombres_agencias = []
        conteos = []
        for avion in self.lista_vuelos:
            agencia_actual = avion.company
            if agencia_actual in nombres_agencias:
                idx = nombres_agencias.index(agencia_actual)
                conteos[idx] += 1
            else:
                nombres_agencias.append(agencia_actual)
                conteos.append(1)

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(nombres_agencias, conteos, color='orange', edgecolor='black')
        ax.set_title("Estadísticas de Tráfico por Aerolíneas")
        ax.set_xlabel("Compañías")
        ax.set_ylabel("Número de Aeronaves")
        ax.set_xticklabels(nombres_agencias, rotation=35, ha="right", fontsize=8)
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        plt.close(fig)

    def f_plot_type_embedded(self):
        if not self.lista_vuelos:
            messagebox.showerror("Error", "No hay datos de operaciones cargados.")
            return
        self.clear_plot_frame()
        schengen_prefixes = [
            'LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG', 'EH', 'LH', 'BI',
            'LI', 'EV', 'EY', 'EL', 'LM', 'EN', 'EP', 'LP', 'LZ', 'LJ', 'LE', 'ES', 'LS'
        ]
        total_schengen = 0
        total_no_schengen = 0
        for avion in self.lista_vuelos:
            if avion.origin[:2] in schengen_prefixes:
                total_schengen += 1
            else:
                total_no_schengen += 1

        fig, ax = plt.subplots(figsize=(5, 4))
        ejes_x = ['Schengen', 'Non-Schengen']
        ejes_y = [total_schengen, total_no_schengen]
        bars = ax.bar(ejes_x, ejes_y, color=['#2ecc71', '#e74c3c'], edgecolor='black', width=0.5)
        ax.set_title("Total de Vuelos según Tipo de Origen")
        ax.set_ylabel("Número de Aeronaves")
        ax.grid(axis='y', linestyle='--', alpha=0.3)

        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, yval + 0.2, str(yval), ha='center', va='bottom',
                    fontweight='bold')

        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        plt.close(fig)

    # --- MÉTODOS DE MAPAS ORIGINALES ---
    def f_show(self):
        print("\n--- Estado Actual en Memoria Volátil ---")
        for a in self.lista_aeropuertos:
            print_airport(a)
        messagebox.showinfo("Terminal", "Mapeo volcado en la consola de tu IDE.")

    def f_map(self):
        if self.lista_aeropuertos:
            map_airports(self.lista_aeropuertos)
            messagebox.showinfo("KML", "Archivo 'airports_map.kml' generado.")
        else:
            messagebox.showwarning("Error", "Carga aeropuertos primero.")

    def f_map_flights(self):
        if self.lista_vuelos and self.lista_aeropuertos:
            map_flights(self.lista_vuelos, self.lista_aeropuertos)
            messagebox.showinfo("KML", "Archivo 'flights_map.kml' generado y lanzado.")
        else:
            messagebox.showerror("Error", "Carga aeropuertos y operaciones simultáneamente.")

    def f_long_flights(self):
        if self.lista_vuelos and self.lista_aeropuertos:
            largos = long_distance_arrivals(self.lista_vuelos, self.lista_aeropuertos)
            if largos:
                map_flights(largos, self.lista_aeropuertos)
                messagebox.showinfo("Filtro Geo",
                                    f"Detectados {len(largos)} vuelos de larga distancia (>2000 km) hacia LEBL.")
            else:
                messagebox.showinfo("Info", "Ninguna operación supera el umbral de los 2000 km.")
        else:
            messagebox.showerror("Error", "Falta cargar datos de aeropuertos o vuelos.")


if __name__ == "__main__":
    ventana = tk.Tk()
    app = AirportApp(ventana)
    ventana.mainloop()
