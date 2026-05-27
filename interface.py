# =====================================================================================
# SECCIÓN 1: IMPORTACIÓN DE LIBRERÍAS Y MÓDULOS DEL PROYECTO
# =====================================================================================
import tkinter as tk  # Librería base para la interfaz gráfica (ventanas, botones, frames)
from tkinter import messagebox, filedialog, \
    ttk  # Componentes avanzados (cuadros de diálogo, selector de archivos, estilos)
import matplotlib.pyplot as plt  # Librería para generar gráficos de barras y frecuencias
from matplotlib.backends.backend_tkagg import \
    FigureCanvasTkAgg  # Permite incrustar gráficos de Matplotlib directamente dentro de Tkinter

# Importación de funciones lógicas de los archivos externos de tu proyecto corporativo
from airport import *  # Carga de aeropuertos, kml, cálculos geográficos y de espacio Schengen
from Aircraft import *  # Control de aeronaves, operaciones y trazas de vuelos de llegada
import LEBL  # Módulo independiente que administra los terminales y asignaciones de puertas de Barcelona


# =====================================================================================
# SECCIÓN 2: CLASE PRINCIPAL DE LA INTERFAZ GRÁFICA
# =====================================================================================
class AirportApp:
    def __init__(self, root):
        """Constructor de la aplicación: Inicializa la ventana y todos sus componentes."""
        self.root = root  # Guarda la ventana raíz de la aplicación
        self.root.title("Proyecto de Informática I - Grupo 9")  # Asigna el título en la barra superior de la ventana
        self.root.attributes("-fullscreen", True)  # Define el tamaño inicial de la pantalla en píxeles (Ancho x Alto)
        self.root.configure(bg="#f4f6f7")  # Establece un color de fondo gris claro para una apariencia moderna

        # --- Variables de control de Datos ---
        self.lista_aeropuertos = []  # Lista dinámica en memoria que guardará los objetos tipo Airport cargados
        self.lista_vuelos = []  # Lista dinámica en memoria que guardará los vuelos (Aircraft) leídos del log
        self.bcn_airport = None  # Espacio reservado para almacenar el objeto estructural BarcelonaAP de LEBL

        # --- Estados de visibilidad para los menús colapsables (Acordeón) ---
        self.airports_visible = False  # False = Menú de Aeropuertos cerrado al arrancar
        self.flights_visible = False  # False = Menú de Operaciones cerrado al arrancar
        self.gates_visible = False  # False = Menú del Administrador de Puertas cerrado al arrancar

        # --- Configuración del motor de estilos tipográficos y visuales (TTK) ---
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Segoe UI", 10), padding=4)  # Diseño por defecto para botones generales
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), background="#f4f6f7",
                             foreground="#2c3e50")  # Estilo del título
        self.style.configure("Toggle.TButton", font=("Segoe UI", 10, "bold"),
                             foreground="#2c3e50")  # Estilo de botones cabecera de menú

        # --- Layout Estructural y Paneles Principales (Distribución en Pantalla) ---
        # Etiqueta del título superior
        header = ttk.Label(self.root, text="SISTEMA DE GESTIÓN AEROPORTUARIA", style="Header.TLabel")
        header.pack(pady=15)  # Se posiciona arriba dejando un margen vertical de 15 píxeles

        # Contenedor maestro que agrupa el panel izquierdo (botones) y el derecho (gráficos)
        self.main_container = tk.Frame(self.root, bg="#f4f6f7")
        self.main_container.pack(fill="both", expand=True, padx=20,
                                 pady=5)  # Se expande por completo respetando márgenes horizontales

        # Panel izquierdo reservado exclusivamente para los botones de control y menús desplegables
        self.button_frame = tk.Frame(self.main_container, bg="#f4f6f7")
        self.button_frame.pack(side="left", fill="y",
                               padx=10)  # Se alinea a la izquierda y ocupa todo el alto disponible

        # Panel derecho (LabelFrame con borde decorativo) destinado a renderizar gráficos y tablas
        self.plot_frame = tk.LabelFrame(self.main_container, text="Panel de Visualización Integrado", bg="white",
                                        font=("Segoe UI", 11, "bold"), fg="#34495e")
        self.plot_frame.pack(side="right", fill="both", expand=True, padx=10,
                             pady=5)  # Ocupa todo el espacio sobrante de la derecha

        # Inicializa los mensajes en el visor central y construye la arquitectura de botones
        self.show_welcome_message()
        self.setup_collapsible_menus()

        # --- Barra de Estado Inferior ---
        self.status_var = tk.StringVar(
            value="Listo | Estructura LEBL: No cargada")  # Variable de texto interactiva de Tkinter
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief="sunken", anchor="w",
                                   font=("Consolas", 10),
                                   bg="#bdc3c7")  # Control visual estilo "hundido" (sunken) alineado a la izquierda (w)
        self.status_bar.pack(side="bottom",
                             fill="x")  # Se adhiere al fondo absoluto de la ventana expandiéndose horizontalmente

    def show_welcome_message(self):
        """Muestra una etiqueta informativa por defecto en el panel derecho cuando este se encuentra vacío."""
        self.no_plot_label = tk.Label(
            self.plot_frame,
            text="Panel libre.\n\nSelecciona cualquier operación del menú de control lateral.",
            font=("Segoe UI", 11, "italic"), bg="white", fg="#7f8c8d"
        )
        self.no_plot_label.pack(expand=True)  # Se centra automáticamente en el panel de gráficos

    def clear_plot_frame(self):
        """Limpia de forma segura todos los elementos visuales del panel derecho antes de pintar un nuevo gráfico o tabla."""
        if hasattr(self, 'no_plot_label') and self.no_plot_label.winfo_exists():
            self.no_plot_label.pack_forget()  # Oculta la etiqueta de bienvenida si sigue activa
        for widget in self.plot_frame.winfo_children():
            widget.destroy()  # Destruye físicamente cada botón, tabla o gráfico que esté en el panel derecho

    def update_status(self):
        """Lee el tamaño actual de las listas y actualiza la barra informativa del pie de página en tiempo real."""
        lebl_status = f"Cargada ({self.bcn_airport.code})" if self.bcn_airport else "No cargada"
        self.status_var.set(
            f"Estado: OK | Aeropuertos: {len(self.lista_aeropuertos)} | Vuelos: {len(self.lista_vuelos)} | Estructura LEBL: {lebl_status}")

    # =====================================================================================
    # SECCIÓN 3: CONSTRUCCIÓN DEL MENÚ INTERACTIVO (CONTRACCIONES Y DESPLEGABLES)
    # =====================================================================================
    def setup_collapsible_menus(self):
        """Crea los botones principales y los subpaneles ocultos para simular un menú de pestañas colapsables."""

        # ----------------- SUBMENÚ 1: GEOMETRÍA Y AEROPUERTOS -----------------
        # Botón maestro que expande o contrae la Sección 1
        self.btn_toggle_airports = ttk.Button(self.button_frame, text="▲ GEOMETRÍA Y AEROPUERTOS",
                                              style="Toggle.TButton", width=35, command=self.toggle_airports_panel)
        self.btn_toggle_airports.pack(fill="x", pady=(5, 0))

        # Marco oculto (Frame) que almacena la botonera interna de aeropuertos con borde en relieve tipo 'groove'
        self.airports_content = tk.Frame(self.button_frame, bg="#f4f6f7", bd=1, relief="groove")

        # Botones asignados a las funciones lógicas de 'airport.py'
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

        # Zona de borrado dinámico (Subcuadro con campo de texto integrado para eliminar aeropuertos por código ICAO)
        delete_zone = tk.LabelFrame(self.airports_content, text="Eliminar Aeropuerto por Código", bg="#f4f6f7",
                                    font=("Segoe UI", 9, "bold"))
        delete_zone.pack(fill="x", pady=5, padx=5)
        tk.Label(delete_zone, text="ICAO:", bg="#f4f6f7").pack(side="left", padx=2)
        self.delete_entry = ttk.Entry(delete_zone, width=8, font=("Segoe UI", 10, "bold"))  # Caja de entrada de texto
        self.delete_entry.pack(side="left", padx=2)
        ttk.Button(delete_zone, text="Eliminar", width=8, command=self.f_delete_dynamic).pack(side="right", padx=2)

        # ----------------- SUBMENÚ 2: OPERACIONES Y TRÁFICO -----------------
        # Botón maestro que expande o contrae la Sección 2
        self.btn_toggle_flights = ttk.Button(self.button_frame, text="▲ OPERACIONES Y TRÁFICO", style="Toggle.TButton",
                                             width=35, command=self.toggle_flights_panel)
        self.btn_toggle_flights.pack(fill="x", pady=(5, 0))

        # Marco oculto (Frame) para la botonera interna de vuelos
        self.flights_content = tk.Frame(self.button_frame, bg="#f4f6f7", bd=1, relief="groove")

        # Botones asignados a las funciones lógicas de 'Aircraft.py'
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

        # ----------------- SUBMENÚ 3: ADMINISTRADOR DE PUERTAS (LAS 5 FUNCIONES DE LEBL) -----------------
        # Botón maestro que expande o contrae la Sección 3
        self.btn_toggle_gates = ttk.Button(self.button_frame, text="▲ ADMINISTRADOR DE PUERTAS", style="Toggle.TButton",
                                           width=35, command=self.toggle_gates_panel)
        self.btn_toggle_gates.pack(fill="x", pady=(5, 0))

        # Marco oculto (Frame) para las funciones del módulo LEBL
        self.gates_content = tk.Frame(self.button_frame, bg="#f4f6f7", bd=1, relief="groove")

        # Botones mapeados uno a uno con los controladores interactivos de las 5 funciones nativas de LEBL
        ttk.Button(self.gates_content, text="Cargar Estructura", width=33,
                   command=self.f_ui_load_airport_structure).pack(pady=2, padx=5)
        ttk.Button(self.gates_content, text="Ver Ocupación de Puertas", width=33,
                   command=self.f_ui_gate_occupancy).pack(pady=2, padx=5)
        ttk.Button(self.gates_content, text="Cargar Aerolíneas", width=33, command=self.f_ui_load_airlines).pack(pady=2,
                                                                                                                 padx=5)
        ttk.Button(self.gates_content, text="Asignar Puertas", width=33, command=self.f_ui_set_gates).pack(pady=2,
                                                                                                           padx=5)
        ttk.Button(self.gates_content, text="Verificar Aerolínea", width=33,
                   command=self.f_ui_is_airline_in_terminal).pack(pady=2, padx=5)
        ttk.Button(self.gates_content, text="Buscar Terminal de Aerolínea", width=33,
                   command=self.f_ui_search_terminal).pack(pady=2, padx=5)
        ttk.Button(self.gates_content, text="Asignar Puerta Automática", width=33,
                   command=self.f_ui_assign_gate).pack(pady=2, padx=5)
        # Botón de desconexión / cierre seguro de la aplicación (posicionado abajo del todo)
        ttk.Button(self.button_frame, text="SALIR DE LA APLICACIÓN", width=35, command=self.root.quit).pack(
            side="bottom", pady=15)

    # --- MÉTODOS DE ANIMACIÓN DE LOS MENÚS (PACK / PACK_FORGET) ---
    def toggle_airports_panel(self):
        """Muestra u oculta el contenedor de aeropuertos alternando el símbolo indicador (▲ / ▼)."""
        if self.airports_visible:
            self.airports_content.pack_forget()  # Desmonta visualmente el contenedor de la pantalla
            self.btn_toggle_airports.configure(text="▲ GEOMETRÍA Y AEROPUERTOS")
            self.airports_visible = False
        else:
            self.airports_content.pack(fill="x", padx=2, pady=(0, 10),
                                       after=self.btn_toggle_airports)  # Lo monta justo debajo del botón maestro
            self.btn_toggle_airports.configure(text="▼ GEOMETRÍA Y AEROPUERTOS")
            self.airports_visible = True

    def toggle_flights_panel(self):
        """Muestra u oculta el contenedor de operaciones analizando su estado actual de visibilidad."""
        if self.flights_visible:
            self.flights_content.pack_forget()
            self.btn_toggle_flights.configure(text="▲ OPERACIONES Y TRÁFICO")
            self.flights_visible = False
        else:
            self.flights_content.pack(fill="x", padx=2, pady=(0, 10), after=self.btn_toggle_flights)
            self.btn_toggle_flights.configure(text="▼ OPERACIONES Y TRÁFICO")
            self.flights_visible = True

    def toggle_gates_panel(self):
        """Muestra u oculta el panel de administración de las funciones estructurales de LEBL."""
        if self.gates_visible:
            self.gates_content.pack_forget()
            self.btn_toggle_gates.configure(text="▲ ADMINISTRADOR DE PUERTAS")
            self.gates_visible = False
        else:
            self.gates_content.pack(fill="x", padx=2, pady=(0, 10), after=self.btn_toggle_gates)
            self.btn_toggle_gates.configure(text="▼ ADMINISTRADOR DE PUERTAS")
            self.gates_visible = True

    # =====================================================================================
    # SECCIÓN 4: CAPA DE INTERFAZ E INTERACCIÓN PARA LAS 5 FUNCIONES DE LEBL.py
    # =====================================================================================

    def f_ui_load_airport_structure(self):
        """Llamada guiada a la FUNCIÓN 3 (load_airport_structure): Lee el fichero txt de jerarquía aeroportuaria."""
        # Abre una ventana flotante del sistema operativo para buscar y seleccionar ficheros .txt
        path = filedialog.askopenfilename(title="Seleccionar estructura LEBL", filetypes=[("Text files", "*.txt")])
        if path:
            res = LEBL.load_airport_structure(path)  # Llama a la lógica de negocio externa pasando la ruta absoluta
            if res:
                self.bcn_airport = res  # Almacena el objeto estructurado devuelto en la variable global del programa
                messagebox.showinfo("Función 3",
                                    f"Estructura del aeropuerto {self.bcn_airport.code} procesada correctamente mediante LEBL.load_airport_structure().")
                self.update_status()  # Refresca los contadores inferiores de la barra gris
                self.clear_plot_frame()  # Borra el lienzo de dibujo
                self.show_welcome_message()  # Restaura el mensaje inicial de aviso
            else:
                messagebox.showerror("Error", "Error al procesar la estructura.")

    def f_ui_gate_occupancy(self):
        """Llamada guiada a la FUNCIÓN 4 (gate_occupancy): Genera una tabla Treeview interactiva con los estados de las puertas."""
        if not self.bcn_airport:
            messagebox.showerror("Error", "Carga primero la estructura (Función 3).")
            return
        self.clear_plot_frame()  # Limpia el área derecha de la interfaz
        datos_puertas = LEBL.gate_occupancy(
            self.bcn_airport)  # Ejecuta la función del módulo que extrae la matriz de ocupación

        # Construcción de un marco contenedor secundario con scrollbar vertical integrada
        table_frame = tk.Frame(self.plot_frame, bg="white")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")

        # Configuración del widget Treeview de Tkinter para representar datos tabulares organizados por columnas
        columnas = ("Puerta", "Estado", "Aeronave Asignada")
        tabla = ttk.Treeview(table_frame, columns=columnas, show="headings", yscrollcommand=scrollbar.set)
        tabla.pack(fill="both", expand=True)
        scrollbar.config(
            command=tabla.yview)  # Conecta los movimientos del ratón en la barra con el desplazamiento de la tabla

        # Nombres de las cabeceras de la tabla
        tabla.heading("Puerta", text="Puerta (Gate)")
        tabla.heading("Estado", text="Estado")
        tabla.heading("Aeronave Asignada", text="Aeronave")
        # Anchos en píxeles y alineación de los textos en las celdas
        tabla.column("Puerta", anchor="center", width=120)
        tabla.column("Estado", anchor="center", width=120)
        tabla.column("Aeronave Asignada", anchor="center", width=150)

        # Reglas cromáticas estéticas: Verde claro para puertas libres, naranja pastel para puertas ocupadas
        tabla.tag_configure('free', background='#e8f8f5', foreground='#117a65')
        tabla.tag_configure('occupied', background='#fce4d6', foreground='#c0392b')

        # Recorre la lista de listas obtenida de LEBL.py e inserta las filas asignando sus respectivos colores (tags)
        for g in datos_puertas:
            tag = 'occupied' if g[1] == "Ocupado" else 'free'
            tabla.insert("", "end", values=(g[0], g[1], g[2]), tags=(tag,))

    def f_ui_load_airlines(self):
        """Llamada corregida a LEBL.load_airlines sin alterar su comportamiento original."""
        if not self.bcn_airport:
            messagebox.showerror("Error", "Primero carga la estructura con la Función 3.")
            return

        # 1. Abrimos el explorador para buscar el archivo real en la computadora
        path = filedialog.askopenfilename(
            title="Seleccionar archivo de aerolíneas (T1_Airlines o T2_Airlines)",
            filetypes=[("Text files", "*.txt")]
        )

        if not path:
            return  # Si el usuario cancela, salimos de forma segura

        # 2. Identificamos qué terminal es basándonos en el nombre del archivo seleccionado
        t_select = None
        if "T1" in path or "t1" in path:
            t_select = "T1"
        elif "T2" in path or "t2" in path:
            t_select = "T2"
        else:
            messagebox.showwarning("Archivo no reconocido",
                                   "El archivo seleccionado debe contener 'T1' o 'T2' en su nombre para identificar la terminal.")
            return

        # 3. Buscamos el objeto Terminal dentro de nuestro aeropuerto
        target_terminal = None
        for t in self.bcn_airport.terminals:
            if t.name == t_select:
                target_terminal = t

        if not target_terminal:
            messagebox.showerror("Error", f"La terminal {t_select} no existe en la estructura de aeropuerto cargada.")
            return

        # 4. Copiamos temporalmente el archivo seleccionado a la carpeta del proyecto
        #    con el nombre exacto que LEBL.py espera ("T1_Airlines.txt" o "T2_Airlines.txt").
        #    De esta forma, no importa de qué carpeta del PC lo abras, funcionará.
        try:
            nombre_esperado = f"{t_select}_Airlines.txt"

            # Leemos el archivo elegido por el usuario y reescribimos el local
            with open(path, "r", encoding="utf-8", errors="ignore") as f_origen:
                contenido = f_origen.read()
            with open(nombre_esperado, "w", encoding="utf-8") as f_destino:
                f_destino.write(contenido)

            # 5. Ejecutamos tu función tal y como está diseñada en LEBL.py (esperando "T1" o "T2")
            res = LEBL.load_airlines(target_terminal, t_select)

            if res:
                messagebox.showinfo("Función 2",
                                    f"¡Éxito! Se han cargado {len(target_terminal.airline_icao_codes)} códigos ICAO en la {t_select}.\n"
                                    f"Leído desde: {path}")
            else:
                messagebox.showerror("Error", f"Tu función LEBL.load_airlines devolvió False para la {t_select}.")

        except Exception as error:
            # Si algo falla en el proceso, este bloque atrapa el error y evita que la app se cierre sola
            messagebox.showerror("Error de Ejecución",
                                 f"Se evitó un cierre inesperado.\nDetalle del error:\n{str(error)}")

    def f_ui_set_gates(self):
        """Llamada guiada a la FUNCIÓN 1 (set_gates): Inicializa un rango numérico de puertas con prefijo en un área determinada."""
        if not self.bcn_airport:
            messagebox.showerror("Error", "Carga primero la estructura con la Función 3.")
            return

        self.clear_plot_frame()
        # Genera un panel de controles de entrada por cuadrícula (Grid) en la zona derecha de la pantalla
        work_panel = tk.Frame(self.plot_frame, bg="white")
        work_panel.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(work_panel, text="F1: Modificar Rango de Puertas Dinámicamente (set_gates)",
                 font=("Segoe UI", 11, "bold"), bg="white").grid(row=0, column=0, columnspan=2, pady=10)
        tk.Label(work_panel, text="Selecciona Área de embarque:", bg="white").grid(row=1, column=0, sticky="w", pady=5)

        # Mapea todas las áreas disponibles en el aeropuerto para mostrarlas en el Combobox
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

        # Campos de texto (Entry) para capturar los valores numéricos enteros y el string de prefijo
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
            """Valida las entradas de texto del formulario y ejecuta set_gates en la memoria del programa."""
            try:
                ini = int(entry_init.get())
                fin = int(entry_end.get())
                pref = entry_pref.get().strip()
                if not pref: raise ValueError  # Lanza un error manual si el prefijo está vacío
            except ValueError:
                messagebox.showwarning("Campos incorrectos", "Escribe valores numéricos válidos y un prefijo.")
                return

            # Encuentra la referencia del objeto BoardingArea seleccionado basándose en el índice del combo
            idx_sel = combo_area.current()
            cont = 0
            target_area = None
            for term in self.bcn_airport.terminals:
                for ar in term.boarding_areas:
                    if cont == idx_sel:
                        target_area = ar
                    cont += 1

            if target_area:
                resultado = LEBL.set_gates(target_area, ini, fin, pref)  # Llama a la primera función de LEBL.py
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
        """Llamada guiada a la FUNCIÓN 5 (is_airline_in_terminal): Valida la operatividad de una aerolínea mediante su código ICAO."""
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
            """Lee las cajas de texto y ejecuta el algoritmo de búsqueda de coincidencia del módulo LEBL."""
            icao = entry_icao.get().strip().upper()  # Asegura que se compruebe siempre en mayúsculas sin espacios
            t_name = combo_term.get()
            if not icao:
                messagebox.showwarning("Vacío", "Escribe un código de aerolínea.")
                return

            target_terminal = None
            for t in self.bcn_airport.terminals:
                if t.name == t_name:
                    target_terminal = t

            if target_terminal:
                pertenece = LEBL.is_airline_in_terminal(target_terminal, icao)  # Llama a la quinta función de LEBL.py
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

    def f_ui_search_terminal(self):
        #truquem la funcio
        if not self.bcn_airport:
            messagebox.showerror("Error", "Carga primero la estructura con la Función 3.")
            return

        self.clear_plot_frame()
        work_panel = tk.Frame(self.plot_frame, bg="white")
        work_panel.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(work_panel, text="Búsqueda de Terminal por Aerolínea", font=("Segoe UI", 11, "bold"),
                 bg="white").grid(row=0, column=0, columnspan=2, pady=10)
        tk.Label(work_panel, text="Código ICAO de la Aerolínea (ej. VLG):", bg="white").grid(row=1, column=0,
                                                                                             sticky="w", pady=5)

        entry_airline = ttk.Entry(work_panel, width=15, font=("Segoe UI", 10, "bold"))
        entry_airline.grid(row=1, column=1, sticky="w", pady=5)
        entry_airline.focus()

        def buscar():
            airline_name = entry_airline.get().strip().upper()
            if not airline_name:
                messagebox.showwarning("Campo Vacío", "Por favor, introduce el nombre o código de una aerolínea.")
                return

            terminal_asignada = LEBL.SearchTerminal(self.bcn_airport, airline_name)

            if terminal_asignada != "":
                messagebox.showinfo("Búsqueda Exitosa",
                                    f"La aerolínea {airline_name} debe embarcar a sus pasajeros en la terminal: {terminal_asignada}")
            else:
                messagebox.showwarning("No Encontrada",
                                       f"La aerolínea {airline_name} no opera en ninguna terminal registrada de este aeropuerto.")

        ttk.Button(work_panel, text="Buscar Terminal", command=buscar).grid(row=2, column=0, columnspan=2, pady=15)

    def f_ui_assign_gate(self):
        """Pide al usuario que introduzca o seleccione un vuelo y le asigna la puerta de forma individual."""
        from tkinter import simpledialog

        # 1. Validaciones previas de carga de datos
        if not self.bcn_airport:
            messagebox.showerror("Error", "Primero debes cargar la estructura del aeropuerto (Cargar Estructura).")
            return

        if not self.lista_vuelos:
            messagebox.showerror("Error", "No hay vuelos cargados. Por favor, carga el archivo de operaciones primero.")
            return

        # 2. Crear una lista de códigos de vuelos disponibles para mostrársela al usuario
        codigos_disponibles = []
        i = 0
        while i < len(self.lista_vuelos):
            codigos_disponibles.append(self.lista_vuelos[i].codigo)
            i += 1

        # Limitamos la muestra en el mensaje si hay demasiados vuelos
        muestra_codigos = ", ".join(codigos_disponibles[:10]) + ("..." if len(codigos_disponibles) > 10 else "")

        # 3. Lanzar una ventana emergente para introducir el código del avión a gestionar
        codigo_introducido = simpledialog.askstring(
            "Seleccionar Vuelo",
            f"Introduce el código del avión al que deseas asignar puerta:\n\nEjemplos cargados: {muestra_codigos}"
        )

        # Si el usuario cancela la ventana
        if not codigo_introducido:
            return

        # Limpiamos espacios en blanco y pasamos a mayúsculas
        codigo_introducido = codigo_introducido.strip().upper()

        # 4. Buscar el objeto Aircraft correspondiente al código introducido
        vuelo_seleccionado = None
        j = 0
        while j < len(self.lista_vuelos):
            if self.lista_vuelos[j].codigo.upper() == codigo_introducido:
                vuelo_seleccionado = self.lista_vuelos[j]
                break
            j += 1

        if not vuelo_seleccionado:
            messagebox.showerror("Vuelo no encontrado",
                                 f"El código de vuelo '{codigo_introducido}' no existe en las operaciones actuales.")
            return

        # 5. Procesar la asignación unitaria llamando a LEBL
        resultado = LEBL.AssignGate(self.bcn_airport, vuelo_seleccionado)

        # 6. Mostrar el resultado de la asignación en la interfaz
        if resultado == -1:
            messagebox.showerror("Error de Asignación",
                                 f"No se pudo asignar puerta.\nLa aerolínea '{vuelo_seleccionado.company}' no está dada de alta en los ficheros T1/T2.")
        elif resultado == -2:
            messagebox.showwarning("Zona Saturada",
                                   f"Atención: No quedan puertas libres de tipo Schengen/non-Schengen en la terminal asignada para el vuelo {vuelo_seleccionado.codigo}.")
        else:
            # Éxito: 'resultado' contiene el string con el nombre de la puerta (ej: 'C10')
            messagebox.showinfo("Asignación Exitosa",
                                f"¡Puerta Asignada Correctamente!\n\n"
                                f"Vuelo: {vuelo_seleccionado.codigo}\n"
                                f"Compañía: {vuelo_seleccionado.company}\n"
                                f"Origen: {vuelo_seleccionado.origin}\n"
                                f"Puerta Asignada: {resultado}")

            # Refrescar visualmente el estado del aeropuerto si tienes implementada la opción
            if hasattr(self, 'f_ui_show_airport_status'):
                self.f_ui_show_airport_status()
    # =====================================================================================
    # SECCIÓN 5: CONTROLADORES DE LOGÍSTICA ORIGINALES (Carga, KMLs y Gráficos)
    # =====================================================================================

    def f_load(self):
        """Carga y procesa el fichero con la base de datos de aeropuertos mundiales."""
        path = filedialog.askopenfilename(title="Abrir base de datos de aeropuertos",
                                          filetypes=[("Text files", "*.txt")])
        if path:
            self.lista_aeropuertos = load_airports(path)  # Función de airport.py
            messagebox.showinfo("Éxito", f"Cargados {len(self.lista_aeropuertos)} aeropuertos.")
            self.update_status()
            self.clear_plot_frame()
            self.show_welcome_message()

    def f_load_arrivals(self):
        """Carga y procesa el log de operaciones / vuelos de llegada hacia el aeropuerto."""
        path = filedialog.askopenfilename(title="Abrir registro de llegadas (Arrivals)",
                                          filetypes=[("Text files", "*.txt")])
        if path:
            self.lista_vuelos = load_arrivals(path)  # Función de Aircraft.py
            messagebox.showinfo("Éxito", f"Cargados {len(self.lista_vuelos)} vuelos.")
            self.update_status()
            self.clear_plot_frame()
            self.show_welcome_message()

    def f_delete_dynamic(self):
        """Elimina un aeropuerto de la lista en memoria mediante coincidencia de código ICAO."""
        codigo_a_borrar = self.delete_entry.get().strip().upper()
        if not codigo_a_borrar:
            messagebox.showwarning("Campo vacío", "Introduce un código ICAO.")
            return
        res = remove_airport(self.lista_aeropuertos, codigo_a_borrar)  # Función de airport.py
        if res == 1:
            messagebox.showinfo("Éxito", f"El aeropuerto {codigo_a_borrar} fue eliminado.")
            self.delete_entry.delete(0, tk.END)  # Limpia la caja de texto tras la eliminación
            self.update_status()
            self.clear_plot_frame()
            self.show_welcome_message()
        else:
            messagebox.showerror("Error", f"El aeropuerto {codigo_a_borrar} no se encuentra.")

    def f_schengen(self):
        """Calcula el booleano Schengen para cada aeropuerto según su prefijo geográfico ICAO."""
        if not self.lista_aeropuertos:
            messagebox.showwarning("Atención", "No hay aeropuertos cargados.")
            return
        for a in self.lista_aeropuertos:
            set_schengen(a)  # Función de airport.py
        messagebox.showinfo("Éxito", "Atributos Schengen mapeados en memoria.")

    def f_save(self):
        """Guarda en un archivo de texto externo únicamente los aeropuertos pertenecientes a la zona Schengen."""
        path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="solo_schengen.txt",
                                            filetypes=[("Text files", "*.txt")])
        if path:
            if save_schengen_airports(self.lista_aeropuertos, path) == 1:
                messagebox.showinfo("Éxito", "Fichero Schengen guardado.")
            else:
                messagebox.showwarning("Error", "No hay datos para guardar.")

    def f_save_flights(self):
        """Exporta el estado actualizado de la lista de vuelos a un fichero txt persistente."""
        path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="saved_arrivals.txt",
                                            filetypes=[("Text files", "*.txt")])
        if path:
            if save_flights(self.lista_vuelos, path):
                messagebox.showinfo("Éxito", "Registro de vuelos guardado.")
            else:
                messagebox.showerror("Error", "La lista de vuelos está vacía.")

    # --- MÉTODOS DE RENDERIZADO DE GRÁFICOS MATPLOTLIB EN LA INTERFAZ ---

    def f_plot_airports_embedded(self):
        """Dibuja un gráfico de barras apiladas comparando aeropuertos Schengen vs No Schengen."""
        if not self.lista_aeropuertos:
            messagebox.showerror("Error", "No hay aeropuertos cargados.")
            return
        self.clear_plot_frame()
        schengen = sum(1 for a in self.lista_aeropuertos if a.schengen)
        not_schengen = len(self.lista_aeropuertos) - schengen

        fig, ax = plt.subplots(figsize=(5, 5))  # Instancia figura y ejes de Matplotlib
        ax.bar(["Aeropuertos"], [schengen], label="Schengen", color="#2980b9", width=0.4)
        ax.bar(["Aeropuertos"], [not_schengen], bottom=[schengen], label="Not Schengen", color="#e74c3c", width=0.4)
        ax.set_ylabel("Cantidad")
        ax.set_title("Estadística de Espacio Schengen")
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.5)

        # Inserta el gráfico en el panel derecho usando el conector de Tkinter de Matplotlib
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        plt.close(fig)  # Cierra la figura para liberar memoria RAM

    def f_plot_arrivals_embedded(self):
        """Dibuja un histograma de frecuencias horarias basado en las horas de llegada de los vuelos."""
        if not self.lista_vuelos:
            messagebox.showerror("Error", "No hay registros de vuelos cargados.")
            return
        self.clear_plot_frame()
        horas_formato = [int(obj.time.split(':')[0]) for obj in self.lista_vuelos]  # Extrae el entero de la hora (HH)
        cont_hora = [0] * 24
        for hora in horas_formato:
            if 0 <= hora < 24: cont_hora[hora] += 1

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(list(range(24)), cont_hora, color='#8e44ad', edgecolor='black')
        ax.set_title("Frecuencia de Vuelos por Hora de Llegada")
        ax.set_xlabel("Hora del día")
        ax.set_ylabel("Aviones")
        ax.set_xticks(list(range(24)))
        ax.grid(axis='y', linestyle='--', alpha=0.4)

        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        plt.close(fig)

    def f_plot_airlines_embedded(self):
        """Genera un diagrama de barras verticales con el volumen de vuelos operados por cada aerolínea."""
        if not self.lista_vuelos:
            messagebox.showerror("Error", "No hay vuelos cargados.")
            return
        self.clear_plot_frame()
        nombres_agencias, conteos = [], []
        for avion in self.lista_vuelos:
            if avion.company in nombres_agencias:
                conteos[nombres_agencias.index(avion.company)] += 1
            else:
                nombres_agencias.append(avion.company)
                conteos.append(1)

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(nombres_agencias, conteos, color='orange', edgecolor='black')
        ax.set_xticklabels(nombres_agencias, rotation=35, ha="right",
                           fontsize=8)  # Rota etiquetas para evitar solapamientos
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        plt.close(fig)

    def f_plot_type_embedded(self):
        """Clasifica y compara gráficamente los vuelos según su procedencia (Schengen vs Internacionales)."""
        if not self.lista_vuelos:
            messagebox.showerror("Error", "No hay datos de operaciones.")
            return
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
        # Bucle para escribir el valor numérico exacto encima de cada barra del gráfico
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2, str(bar.get_height()), ha='center',
                    va='bottom', fontweight='bold')

        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        plt.close(fig)

    # --- MÉTODOS AUXILIARES: SALIDA POR CONSOLA Y EXPORTACIÓN KML ---

    def f_show(self):
        """Vuelca por la consola estándar de Python los detalles tabulados de los aeropuertos cargados."""
        print("\n--- Estado en Consola ---")
        for a in self.lista_aeropuertos:
            print_airport(a)  # Función de airport.py que ejecuta los prints del objeto
        messagebox.showinfo("Terminal", "Mapeo volcado en la consola del sistema.")

    def f_map(self):
        """Genera el fichero 'airports_map.kml' para proyectar los marcadores de geolocalización en Google Earth."""
        if self.lista_aeropuertos:
            map_airports(self.lista_aeropuertos)  # Función de airport.py
            messagebox.showinfo("KML", "Archivo 'airports_map.kml' generado con éxito en el directorio raíz.")
        else:
            messagebox.showwarning("Error", "Carga aeropuertos primero.")

    def f_map_flights(self):
        """Genera un mapa de trayectorias en formato KML entrelazando los orígenes con el destino (LEBL)."""
        if self.lista_vuelos and self.lista_aeropuertos:
            map_flights(self.lista_vuelos, self.lista_aeropuertos)  # Función de airport.py
            messagebox.showinfo("KML", "Archivo 'flights_map.kml' generado con éxito en el directorio raíz.")
        else:
            messagebox.showerror("Error", "Carga aeropuertos y operaciones simultáneamente.")

    def f_long_flights(self):
        """Filtra y exporta en KML exclusivamente los vuelos de largo alcance cuyo recorrido supere los 2000 km."""
        if self.lista_vuelos and self.lista_aeropuertos:
            largos = long_distance_arrivals(self.lista_vuelos, self.lista_aeropuertos)  # Función de airport.py
            if largos:
                map_flights(largos, self.lista_aeropuertos)
                messagebox.showinfo("Filtro Geo",
                                    f"Detectados {len(largos)} vuelos de larga distancia (>2000 km) hacia LEBL.")
            else:
                messagebox.showinfo("Info", "Ninguna operación en el registro supera el umbral de los 2000 km.")
        else:
            messagebox.showerror("Error", "Faltan datos esenciales de aeropuertos o vuelos para calcular distancias.")


# =====================================================================================
# SECCIÓN 6: PUNTO DE ENTRADA AL PROGRAMA (MAIN RUNNER)
# =====================================================================================
if __name__ == "__main__":
    ventana = tk.Tk()  # Instancia la ventana raíz del entorno gráfico de Tkinter
    app = AirportApp(ventana)  # Pasa la ventana raíz como argumento al constructor de nuestra aplicación
    ventana.mainloop()  # Inicia el bucle infinito de eventos de la interfaz (mantiene la ventana abierta respondiendo a clics)
