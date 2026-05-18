import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


from airport import *
from Aircraft import *
import LEBL


class AirportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Proyecto de Informática I - Grupo 9")
        self.root.geometry("1350x950")
        self.root.configure(bg="#f4f6f7")

        # Variables de datos
        self.lista_aeropuertos = []
        self.lista_vuelos = []
        self.bcn_airport = None  # Instancia de BarcelonaAP cuando se cargue

        # Visibilidad paneles colapsables
        self.airports_visible = False
        self.flights_visible = False
        self.gates_visible = False

        # Estilos generales
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Segoe UI", 10), padding=4)
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), background="#f4f6f7", foreground="#2c3e50")
        self.style.configure("Toggle.TButton", font=("Segoe UI", 10, "bold"), foreground="#2c3e50")

        # Layout Estructural
        header = ttk.Label(self.root, text="SISTEMA DE GESTIÓN AEROPORTUARIA", style="Header.TLabel")
        header.pack(pady=15)

        self.main_container = tk.Frame(self.root, bg="#f4f6f7")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=5)

        self.button_frame = tk.Frame(self.main_container, bg="#f4f6f7")
        self.button_frame.pack(side="left", fill="y", padx=10)

        self.plot_frame = tk.LabelFrame(self.main_container, text="Panel de Visualización Integrado", bg="white",
                                        font=("Segoe UI", 11, "bold"), fg="#34495e")
        self.plot_frame.pack(side="right", fill="both", expand=True, padx=10, pady=5)

        self.show_welcome_message()
        self.setup_collapsible_menus()

        # Barra de estado inferior
        self.status_var = tk.StringVar(value="Listo | Estructura LEBL: No cargada")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief="sunken", anchor="w",
                                   font=("Consolas", 10), bg="#bdc3c7")
        self.status_bar.pack(side="bottom", fill="x")

    def show_welcome_message(self):
        self.no_plot_label = tk.Label(
            self.plot_frame,
            text="Panel libre.\n\nSelecciona cualquier operación del menú de control lateral.",
            font=("Segoe UI", 11, "italic"), bg="white", fg="#7f8c8d"
        )
        self.no_plot_label.pack(expand=True)

    def clear_plot_frame(self):
        if hasattr(self, 'no_plot_label') and self.no_plot_label.winfo_exists():
            self.no_plot_label.pack_forget()
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

    def update_status(self):
        lebl_status = f"Cargada ({self.bcn_airport.code})" if self.bcn_airport else "No cargada"
        self.status_var.set(
            f"Estado: OK | Aeropuertos: {len(self.lista_aeropuertos)} | Vuelos: {len(self.lista_vuelos)} | Estructura LEBL: {lebl_status}")

    def setup_collapsible_menus(self):
        # ================= SECCIÓN 1: AEROPUERTOS =================
        self.btn_toggle_airports = ttk.Button(self.button_frame, text="▲ GEOMETRÍA Y AEROPUERTOS",
                                              style="Toggle.TButton", width=35, command=self.toggle_airports_panel)
        self.btn_toggle_airports.pack(fill="x", pady=(5, 0))
        self.airports_content = tk.Frame(self.button_frame, bg="#f4f6f7", bd=1, relief="groove")
        ttk.Button(self.airports_content, text="Cargar Archivo Aeropuertos...", width=33, command=self.f_load).pack(
            pady=2, padx=5)
        ttk.Button(self.airports_content, text="Calcular Atributo Schengen", width=33, command=self.f_schengen).pack(
            pady=2, padx=5)
        ttk.Button(self.airports_content, text="Mostrar Datos (Terminal)", width=33, command=self.f_show).pack(pady=2,
                                                                                                               padx=5)
        ttk.Button(self.airports_content, text="Guardar Schengen a Fichero...", width=33, command=self.f_save).pack(
            pady=2, padx=5)
        ttk.Button(self.airports_content, text="Ver Aeropuertos en Google Earth", width=33, command=self.f_map).pack(
            pady=2, padx=5)
        ttk.Button(self.airports_content, text="Gráfico: Schengen vs No Schengen", width=33,
                   command=self.f_plot_airports_embedded).pack(pady=2, padx=5)

        delete_zone = tk.LabelFrame(self.airports_content, text="Eliminar Aeropuerto por Código", bg="#f4f6f7",
                                    font=("Segoe UI", 9, "bold"))
        delete_zone.pack(fill="x", pady=5, padx=5)
        tk.Label(delete_zone, text="ICAO:", bg="#f4f6f7").pack(side="left", padx=2)
        self.delete_entry = ttk.Entry(delete_zone, width=8, font=("Segoe UI", 10, "bold"))
        self.delete_entry.pack(side="left", padx=2)
        ttk.Button(delete_zone, text="Eliminar", width=8, command=self.f_delete_dynamic).pack(side="right", padx=2)

        # ================= SECCIÓN 2: OPERACIONES =================
        self.btn_toggle_flights = ttk.Button(self.button_frame, text="▲ OPERACIONES Y TRÁFICO", style="Toggle.TButton",
                                             width=35, command=self.toggle_flights_panel)
        self.btn_toggle_flights.pack(fill="x", pady=(5, 0))
        self.flights_content = tk.Frame(self.button_frame, bg="#f4f6f7", bd=1, relief="groove")
        ttk.Button(self.flights_content, text="Cargar Archivo Operaciones...", width=33,
                   command=self.f_load_arrivals).pack(pady=2, padx=5)
        ttk.Button(self.flights_content, text="Gráfico: Frecuencia Horaria", width=33,
                   command=self.f_plot_arrivals_embedded).pack(pady=2, padx=5)
        ttk.Button(self.flights_content, text="Gráfico: Vuelos por Aerolínea", width=33,
                   command=self.f_plot_airlines_embedded).pack(pady=2, padx=5)
        ttk.Button(self.flights_content, text="Gráfico: Vuelos por Origen", width=33,
                   command=self.f_plot_type_embedded).pack(pady=2, padx=5)
        ttk.Button(self.flights_content, text="Guardar Vuelos a Fichero...", width=33,
                   command=self.f_save_flights).pack(pady=2, padx=5)
        ttk.Button(self.flights_content, text="Ver Trayectorias en Google Earth", width=33,
                   command=self.f_map_flights).pack(pady=2, padx=5)
        ttk.Button(self.flights_content, text="Filtrar Larga Distancia (>2000km)", width=33,
                   command=self.f_long_flights).pack(pady=2, padx=5)

        # ================= SECCIÓN 3: ADMINISTRADOR DE PUERTAS (LAS 5 FUNCIONES DE LEBL) =================
        self.btn_toggle_gates = ttk.Button(self.button_frame, text="▲ ADMINISTRADOR DE PUERTAS", style="Toggle.TButton",
                                           width=35, command=self.toggle_gates_panel)
        self.btn_toggle_gates.pack(fill="x", pady=(5, 0))
        self.gates_content = tk.Frame(self.button_frame, bg="#f4f6f7", bd=1, relief="groove")

        # Botones correspondientes a las 5 Funciones del módulo LEBL.py
        ttk.Button(self.gates_content, text="Cargar Estructura", width=33,
                   command=self.f_ui_load_airport_structure).pack(pady=2, padx=5)
        ttk.Button(self.gates_content, text="Ver Ocupación de Puertas", width=33,
                   command=self.f_ui_gate_occupancy).pack(pady=2, padx=5)
        ttk.Button(self.gates_content, text="Cargar Aerolíneas", width=33,
                   command=self.f_ui_load_airlines).pack(pady=2, padx=5)
        ttk.Button(self.gates_content, text="Asignar Puertas", width=33,
                   command=self.f_ui_set_gates).pack(pady=2, padx=5)
        ttk.Button(self.gates_content, text="Verificar Aerolínea", width=33,
                   command=self.f_ui_is_airline_in_terminal).pack(pady=2, padx=5)

        ttk.Button(self.button_frame, text="SALIR DE LA APLICACIÓN", width=35, command=self.root.quit).pack(
            side="bottom", pady=15)

    # --- CONTROLADORES DE LOS DESPLEGABLES ---
    def toggle_airports_panel(self):
        if self.airports_visible:
            self.airports_content.pack_forget(); self.btn_toggle_airports.configure(
                text="▲ GEOMETRÍA Y AEROPUERTOS"); self.airports_visible = False
        else:
            self.airports_content.pack(fill="x", padx=2, pady=(0, 10),
                                       after=self.btn_toggle_airports); self.btn_toggle_airports.configure(
                text="▼ GEOMETRÍA Y AEROPUERTOS"); self.airports_visible = True

    def toggle_flights_panel(self):
        if self.flights_visible:
            self.flights_content.pack_forget(); self.btn_toggle_flights.configure(
                text="▲ OPERACIONES Y TRÁFICO"); self.flights_visible = False
        else:
            self.flights_content.pack(fill="x", padx=2, pady=(0, 10),
                                      after=self.btn_toggle_flights); self.btn_toggle_flights.configure(
                text="▼ OPERACIONES Y TRÁFICO"); self.flights_visible = True

    def toggle_gates_panel(self):
        if self.gates_visible:
            self.gates_content.pack_forget(); self.btn_toggle_gates.configure(
                text="▲ ADMINISTRADOR DE PUERTAS"); self.gates_visible = False
        else:
            self.gates_content.pack(fill="x", padx=2, pady=(0, 10),
                                    after=self.btn_toggle_gates); self.btn_toggle_gates.configure(
                text="▼ ADMINISTRADOR DE PUERTAS"); self.gates_visible = True

    # =====================================================================================
    # CAPA DE INTERFAZ PARA LAS 5 FUNCIONES DE LEBL.py
    # =====================================================================================

    def f_ui_load_airport_structure(self):
        """Llamada a la Función 3: load_airport_structure"""
        path = filedialog.askopenfilename(title="Seleccionar estructura LEBL", filetypes=[("Text files", "*.txt")])
        if path:
            res = LEBL.load_airport_structure(path)
            if res:
                self.bcn_airport = res
                messagebox.showinfo("Función 3",
                                    f"Estructura del aeropuerto {self.bcn_airport.code} procesada correctamente mediante LEBL.load_airport_structure().")
                self.update_status()
                self.clear_plot_frame()
                self.show_welcome_message()
            else:
                messagebox.showerror("Error", "Error al procesar la estructura.")

    def f_ui_gate_occupancy(self):
        """Llamada a la Función 4: gate_occupancy"""
        if not self.bcn_airport:
            messagebox.showerror("Error", "Carga primero la estructura (Función 3).")
            return
        self.clear_plot_frame()
        datos_puertas = LEBL.gate_occupancy(self.bcn_airport)

        table_frame = tk.Frame(self.plot_frame, bg="white")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")

        columnas = ("Puerta", "Estado", "Aeronave Asignada")
        tabla = ttk.Treeview(table_frame, columns=columnas, show="headings", yscrollcommand=scrollbar.set)
        tabla.pack(fill="both", expand=True)
        scrollbar.config(command=tabla.yview)

        tabla.heading("Puerta", text="Puerta (Gate)")
        tabla.heading("Estado", text="Estado")
        tabla.heading("Aeronave Asignada", text="Aeronave")
        tabla.column("Puerta", anchor="center", width=120)
        tabla.column("Estado", anchor="center", width=120)
        tabla.column("Aeronave Asignada", anchor="center", width=150)

        tabla.tag_configure('free', background='#e8f8f5', foreground='#117a65')
        tabla.tag_configure('occupied', background='#fce4d6', foreground='#c0392b')

        for g in datos_puertas:
            tag = 'occupied' if g[1] == "Ocupado" else 'free'
            tabla.insert("", "end", values=(g[0], g[1], g[2]), tags=(tag,))

    def f_ui_load_airlines(self):
        """Llamada a la Función 2: load_airlines"""
        if not self.bcn_airport:
            messagebox.showerror("Error", "Primero carga la estructura con la Función 3.")
            return

        sub_window = tk.Toplevel(self.root)
        sub_window.title("F2: Cargar Aerolíneas")
        sub_window.geometry("350x150")
        sub_window.grab_set()

        tk.Label(sub_window, text="Seleccione Terminal destino:", font=("Segoe UI", 10)).pack(pady=10)
        combo = ttk.Combobox(sub_window, values=["T1", "T2"], state="readonly")
        combo.pack(pady=5)
        combo.current(0)

        def ejecutar():
            t_select = combo.get()
            target_terminal = None
            for t in self.bcn_airport.terminals:
                if t.name == t_select:
                    target_terminal = t

            if target_terminal:
                res = LEBL.load_airlines(target_terminal, t_select)
                if res:
                    messagebox.showinfo("Función 2",
                                        f"Se han cargado {len(target_terminal.airline_icao_codes)} códigos ICAO en la {t_select}.")
                    sub_window.destroy()
                else:
                    messagebox.showerror("Error", "Fichero de aerolíneas ausente.")
            else:
                messagebox.showerror("Error", "La terminal no existe en el objeto cargado.")

        ttk.Button(sub_window, text="Ejecutar load_airlines()", command=ejecutar).pack(pady=10)

    def f_ui_set_gates(self):
        """Llamada a la Función 1: set_gates"""
        if not self.bcn_airport:
            messagebox.showerror("Error", "Carga primero la estructura con la Función 3.")
            return

        self.clear_plot_frame()
        work_panel = tk.Frame(self.plot_frame, bg="white")
        work_panel.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(work_panel, text="F1: Modificar Rango de Puertas Dinámicamente (set_gates)",
                 font=("Segoe UI", 11, "bold"), bg="white").grid(row=0, column=0, columnspan=2, pady=10)

        tk.Label(work_panel, text="Selecciona Área de embarque:", bg="white").grid(row=1, column=0, sticky="w", pady=5)

        areas_disponibles = []
        for term in self.bcn_airport.terminals:
            for ar in term.boarding_areas:
                areas_disponibles.append(f"{term.name} - Area {ar.name}")

        if not areas_disponibles:
            tk.Label(work_panel, text="No hay áreas cargadas.", fg="red", bg="white").grid(row=2, column=0)
            return

        combo_area = ttk.Combobox(work_panel, values=areas_disponibles, state="readonly", width=25)
        combo_area.grid(row=1, column=1, pady=5)
        combo_area.current(0)

        tk.Label(work_panel, text="Puerta Inicial (Int):", bg="white").grid(row=2, column=0, sticky="w", pady=5)
        entry_init = ttk.Entry(work_panel, width=10)
        entry_init.grid(row=2, column=1, sticky="w", pady=5)

        tk.Label(work_panel, text="Puerta Final (Int):", bg="white").grid(row=3, column=0, sticky="w", pady=5)
        entry_end = ttk.Entry(work_panel, width=10)
        entry_end.grid(row=3, column=1, sticky="w", pady=5)

        tk.Label(work_panel, text="Prefijo de Puerta:", bg="white").grid(row=4, column=0, sticky="w", pady=5)
        entry_pref = ttk.Entry(work_panel, width=10)
        entry_pref.grid(row=4, column=1, sticky="w", pady=5)

        def aplicar_set_gates():
            try:
                ini = int(entry_init.get())
                fin = int(entry_end.get())
                pref = entry_pref.get().strip()
                if not pref: raise ValueError
            except ValueError:
                messagebox.showwarning("Campos incorrectos", "Escribe valores numéricos válidos y un prefijo.")
                return

            idx_sel = combo_area.current()
            cont = 0
            target_area = None
            for term in self.bcn_airport.terminals:
                for ar in term.boarding_areas:
                    if cont == idx_sel:
                        target_area = ar
                    cont += 1

            if target_area:
                resultado = LEBL.set_gates(target_area, ini, fin, pref)
                if resultado == -1:
                    messagebox.showerror("Error", "El rango final debe ser estrictamente mayor que el inicial.")
                else:
                    messagebox.showinfo("Función 1",
                                        f"¡Éxito! El área seleccionada ahora cuenta con {len(target_area.gates)} nuevas puertas generadas.")
            else:
                messagebox.showerror("Error", "Área no localizada.")

        ttk.Button(work_panel, text="Aplicar set_gates()", command=aplicar_set_gates).grid(row=5, column=0,
                                                                                           columnspan=2, pady=15)

    def f_ui_is_airline_in_terminal(self):
        """Llamada a la Función 5: is_airline_in_terminal"""
        if not self.bcn_airport:
            messagebox.showerror("Error", "Carga primero la estructura con la Función 3.")
            return

        self.clear_plot_frame()
        work_panel = tk.Frame(self.plot_frame, bg="white")
        work_panel.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(work_panel, text="F5: Validación de Operatividad de Aerolínea", font=("Segoe UI", 11, "bold"),
                 bg="white").grid(row=0, column=0, columnspan=2, pady=10)

        tk.Label(work_panel, text="Código ICAO Compañía (3-4 letras):", bg="white").grid(row=1, column=0, sticky="w",
                                                                                         pady=5)
        entry_icao = ttk.Entry(work_panel, width=12, font=("Segoe UI", 10, "bold"))
        entry_icao.grid(row=1, column=1, sticky="w", pady=5)

        tk.Label(work_panel, text="Consultar en Terminal:", bg="white").grid(row=2, column=0, sticky="w", pady=5)
        combo_term = ttk.Combobox(work_panel, values=[t.name for t in self.bcn_airport.terminals], state="readonly",
                                  width=10)
        combo_term.grid(row=2, column=1, sticky="w", pady=5)
        if self.bcn_airport.terminals: combo_term.current(0)

        def comprobar():
            icao = entry_icao.get().strip().upper()
            t_name = combo_term.get()
            if not icao:
                messagebox.showwarning("Vacío", "Escribe un código de aerolínea.")
                return

            target_terminal = None
            for t in self.bcn_airport.terminals:
                if t.name == t_name:
                    target_terminal = t

            if target_terminal:
                pertenece = LEBL.is_airline_in_terminal(target_terminal, icao)
                if pertenece:
                    messagebox.showinfo("Resultado F5",
                                        f"SÍ. La aerolínea {icao} está autorizada y opera en la {t_name}.")
                else:
                    messagebox.showwarning("Resultado F5",
                                           f"NO. La aerolínea {icao} NO tiene asignada la {t_name} o no se encuentra registrada.")
            else:
                messagebox.showerror("Error", "Terminal no válida.")

        ttk.Button(work_panel, text="Comprobar via is_airline_in_terminal()", command=comprobar).grid(row=3, column=0,
                                                                                                      columnspan=2,
                                                                                                      pady=15)

    # =====================================================================================
    # MÉTODOS DE LOGÍSTICA ORIGINALES (Carga de Aeropuertos, Llegadas, KMLs y Gráficos)
    # =====================================================================================
    def f_load(self):
        path = filedialog.askopenfilename(title="Abrir base de datos de aeropuertos",
                                          filetypes=[("Text files", "*.txt")])
        if path:
            self.lista_aeropuertos = load_airports(path);
            messagebox.showinfo("Éxito", f"Cargados {len(self.lista_aeropuertos)} aeropuertos.");
            self.update_status();
            self.clear_plot_frame();
            self.show_welcome_message()

    def f_load_arrivals(self):
        path = filedialog.askopenfilename(title="Abrir registro de llegadas (Arrivals)",
                                          filetypes=[("Text files", "*.txt")])
        if path:
            self.lista_vuelos = load_arrivals(path);
            messagebox.showinfo("Éxito", f"Cargados {len(self.lista_vuelos)} vuelos.");
            self.update_status();
            self.clear_plot_frame();
            self.show_welcome_message()

    def f_delete_dynamic(self):
        codigo_a_borrar = self.delete_entry.get().strip().upper()
        if not codigo_a_borrar: messagebox.showwarning("Campo vacío", "Introduce un código ICAO."); return
        res = remove_airport(self.lista_aeropuertos, codigo_a_borrar)
        if res == 1:
            messagebox.showinfo("Éxito", f"El aeropuerto {codigo_a_borrar} fue eliminado."); self.delete_entry.delete(0,
                                                                                                                      tk.END); self.update_status(); self.clear_plot_frame(); self.show_welcome_message()
        else:
            messagebox.showerror("Error", f"El aeropuerto {codigo_a_borrar} no se encuentra.")

    def f_schengen(self):
        if not self.lista_aeropuertos: messagebox.showwarning("Atención", "No hay aeropuertos cargados."); return
        for a in self.lista_aeropuertos: set_schengen(a)
        messagebox.showinfo("Éxito", "Atributos Schengen mapeados.")

    def f_save(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="solo_schengen.txt",
                                            filetypes=[("Text files", "*.txt")])
        if path:
            if save_schengen_airports(self.lista_aeropuertos, path) == 1:
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

    def f_plot_airports_embedded(self):
        if not self.lista_aeropuertos: messagebox.showerror("Error", "No hay aeropuertos cargados."); return
        self.clear_plot_frame()
        schengen = sum(1 for a in self.lista_aeropuertos if a.schengen)
        not_schengen = len(self.lista_aeropuertos) - schengen
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.bar(["Aeropuertos"], [schengen], label="Schengen", color="#2980b9", width=0.4)
        ax.bar(["Aeropuertos"], [not_schengen], bottom=[schengen], label="Not Schengen", color="#e74c3c", width=0.4)
        ax.set_ylabel("Cantidad");
        ax.set_title("Estadística de Espacio Schengen");
        ax.legend();
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame);
        canvas.draw();
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10);
        plt.close(fig)

    def f_plot_arrivals_embedded(self):
        if not self.lista_vuelos: messagebox.showerror("Error", "No hay registros de vuelos cargados."); return
        self.clear_plot_frame()
        horas_formato = [int(obj.time.split(':')[0]) for obj in self.lista_vuelos]
        cont_hora = [0] * 24
        for hora in horas_formato:
            if 0 <= hora < 24: cont_hora[hora] += 1
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(list(range(24)), cont_hora, color='#8e44ad', edgecolor='black')
        ax.set_title("Frecuencia de Vuelos por Hora de Llegada");
        ax.set_xlabel("Hora del día");
        ax.set_ylabel("Aviones");
        ax.set_xticks(list(range(24)));
        ax.grid(axis='y', linestyle='--', alpha=0.4)
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame);
        canvas.draw();
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10);
        plt.close(fig)

    def f_plot_airlines_embedded(self):
        if not self.lista_vuelos: messagebox.showerror("Error", "No hay vuelos cargados."); return
        self.clear_plot_frame()
        nombres_agencias, conteos = [], []
        for avion in self.lista_vuelos:
            if avion.company in nombres_agencias:
                conteos[nombres_agencias.index(avion.company)] += 1
            else:
                nombres_agencias.append(avion.company); conteos.append(1)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(nombres_agencias, conteos, color='orange', edgecolor='black')
        ax.set_xticklabels(nombres_agencias, rotation=35, ha="right", fontsize=8);
        ax.grid(axis='y', linestyle='--', alpha=0.3);
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame);
        canvas.draw();
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10);
        plt.close(fig)

    def f_plot_type_embedded(self):
        if not self.lista_vuelos: messagebox.showerror("Error", "No hay datos de operaciones."); return
        self.clear_plot_frame()
        prefixes = ['LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG', 'EH', 'LH', 'BI', 'LI', 'EV', 'EY',
                    'EL', 'LM', 'EN', 'EP', 'LP', 'LZ', 'LJ', 'LE', 'ES', 'LS']
        ts, tns = 0, 0
        for avion in self.lista_vuelos:
            if avion.origin[:2] in prefixes:
                ts += 1
            else:
                tns += 1
        fig, ax = plt.subplots(figsize=(5, 4))
        bars = ax.bar(['Schengen', 'Non-Schengen'], [ts, tns], color=['#2ecc71', '#e74c3c'], edgecolor='black',
                      width=0.5)
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        for bar in bars: ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2, str(bar.get_height()),
                                 ha='center', va='bottom', fontweight='bold')
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame);
        canvas.draw();
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10);
        plt.close(fig)

    def f_show(self):
        print("\n--- Estado en Consola ---")
        for a in self.lista_aeropuertos: print_airport(a)
        messagebox.showinfo("Terminal", "Mapeo volcado en consola.")

    def f_map(self):
        if self.lista_aeropuertos:
            map_airports(self.lista_aeropuertos); messagebox.showinfo("KML", "Archivo 'airports_map.kml' generado.")
        else:
            messagebox.showwarning("Error", "Carga aeropuertos primero.")

    def f_map_flights(self):
        if self.lista_vuelos and self.lista_aeropuertos:
            map_flights(self.lista_vuelos, self.lista_aeropuertos); messagebox.showinfo("KML",
                                                                                        "Archivo 'flights_map.kml' generado.")
        else:
            messagebox.showerror("Error", "Carga aeropuertos y operaciones.")

    def f_long_flights(self):
        if self.lista_vuelos and self.lista_aeropuertos:
            largos = long_distance_arrivals(self.lista_vuelos, self.lista_aeropuertos)
            if largos:
                map_flights(largos, self.lista_aeropuertos); messagebox.showinfo("Filtro Geo",
                                                                                 f"Detectados {len(largos)} vuelos de larga distancia (>2000 km) hacia LEBL.")
            else:
                messagebox.showinfo("Info", "Ninguna operación supera los 2000 km.")
        else:
            messagebox.showerror("Error", "Faltan datos de aeropuertos o vuelos.")


if __name__ == "__main__":
    ventana = tk.Tk()
    app = AirportApp(ventana)
    ventana.mainloop()
