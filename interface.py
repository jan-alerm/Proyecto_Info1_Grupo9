# ======================================================================================================================
# IMPORTACIONES DE LIBRERÍAS Y MÓDULOS DEL PROYECTO
# ======================================================================================================================
# Librería base para la interfaz gráfica (ventanas, botones, frames)
import math
import os
import struct
import tempfile
import wave
import winsound
import tkinter as tk  # Librería base para la interfaz gráfica (ventanas, botones, frames)
from tkinter import messagebox, filedialog, ttk

# Librería para generar gráficos de barras y frecuencias
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Módulos desarrollados para el proyecto
from airport import *                                                                                                   # Carga de aeropuertos, kml, cálculos geográficos y de espacio Schengen
from aircraft import *                                                                                                  # Control de aeronaves, operaciones y trazas de vuelos de llegada
import LEBL                                                                                                             # Módulo independiente que administra los terminales y asignaciones de puertas de Barcelona


# ======================================================================================================================
# CLASE PRINCIPAL DE LA INTERFAZ GRÁFICA
# ======================================================================================================================
class AirportApp:
    def __init__(self, root):
        """Constructor de la aplicación: Inicializa la ventana y todos sus componentes."""
        self.root = root  # Guarda la ventana raíz de la aplicación
        self.root.title("Proyecto de Informática I - Grupo 9")  # Asigna el título en la barra superior de la ventana
        self.root.state("zoomed")  # Define el tamaño inicial de la pantalla en píxeles (Ancho x Alto)
        self.root.resizable(True, True)
        self.root.configure(bg="#f4f6f7")  # Establece un color de fondo gris claro para una apariencia moderna

        # --- Variables de control de Datos ---
        self.lista_aeropuertos = []  # Lista dinámica en memoria que guardará los objetos tipo Airport cargados
        self.lista_vuelos = []  # Lista dinámica en memoria que guardará los vuelos (Aircraft) leídos del log
        self.bcn_airport = None  # Espacio reservado para almacenar el objeto estructural BarcelonaAP de LEBL

        # --- NUEVAS VARIABLES DE LA FASE 4 ---
        self.lista_salidas = []  # Guardará los datos leídos de las salidas (Departures)
        self.lista_unificada = []  # Guardará el merge de movimientos (arrivals + departures)
        self.airlines_loaded_terminals = set()  # Controla que se hayan cargado T1 y T2 antes de marcar el botón
        self.selected_airport_code = None
        self.music_enabled = True
        self.music_file = None

        # --- Estados de visibilidad para los menús colapsables (Acordeón) ---
        self.airports_visible = False  # False = Menú de Aeropuertos cerrado al arrancar
        self.flights_visible = False  # False = Menú de Operaciones cerrado al arrancar
        self.gates_visible = False  # False = Menú del Administrator de Puertas cerrado al arrancar
        self.fase4_visible = False  # False = Menú de Fase 4 cerrado al arrancar

        # --- Configuración del motor de estilos tipográficos y visuales (TTK) ---
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass
        self.style.configure("TButton", font=("Segoe UI", 10), padding=4)  # Diseño por defecto para botones generales
        self.style.configure("Loaded.TButton", font=("Segoe UI", 10), padding=4,
                             background="#D7E8F7", foreground="#1f3f5b")  # Botón de fichero ya cargado
        self.style.map("Loaded.TButton", background=[("active", "#C9DFF0")])
        self.style.configure("Header.TLabel",font=("Segoe UI", 16, "bold"),background="#f4f6f7",foreground="#355C8A")
        self.style.configure("Toggle.TButton", font=("Segoe UI", 10, "bold"),
                             foreground="#2c3e50")  # Estilo de botones cabecera de menú

        # --- Layout Estructural y Paneles Principales (Distribución en Pantalla) ---
        # Etiqueta del título superior con control de sonido
        header_frame = tk.Frame(self.root, bg="#f4f6f7")
        header_frame.pack(fill="x", pady=15, padx=20)
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(2, weight=1)
        header = ttk.Label(header_frame, text="SISTEMA DE GESTIÓN AEROPORTUARIA", style="Header.TLabel")
        header.grid(row=0, column=1)
        self.music_button = ttk.Button(header_frame, text="🔊", width=4, command=self.toggle_music)
        self.music_button.grid(row=0, column=2, sticky="e")
        self.start_background_music()
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

        # Contenedor maestro que agrupa el panel izquierdo (botones) y el derecho (gráficos)
        self.main_container = tk.Frame(self.root, bg="#f4f6f7")
        self.main_container.pack(fill="both", expand=True, padx=20,
                                 pady=5)  # Se expande por completo respetando márgenes horizontales

        # =====================================================================
        # PANEL IZQUIERDO CORREGIDO: SCROLL DINÁMICO E INTELIGENTE + BOTÓN FIJO
        # =====================================================================

        # 1. Contenedor principal de la barra lateral izquierda (Ancho fijo de 280)
        self.sidebar_container = tk.Frame(self.main_container, bg="#f4f6f7", width=280)
        self.sidebar_container.pack(side="left", fill="y", padx=10)
        self.sidebar_container.pack_propagate(False)  # Evita que el contenedor cambie de tamaño

        # 2. Sub-contenedor para los botones con Scroll (Ocupa todo el alto menos el botón salir)
        self.menu_scroll_frame = tk.Frame(self.sidebar_container, bg="#f4f6f7")
        self.menu_scroll_frame.pack(side="top", fill="both", expand=True)

        # 3. La barra de scroll vertical (Alineada a la derecha del sub-contenedor)
        self.scrollbar_lateral = ttk.Scrollbar(self.menu_scroll_frame, orient="vertical")

        # 4. El Canvas (Alineado a la izquierda, ocupando todo el alto disponible)
        self.scroll_canvas = tk.Canvas(self.menu_scroll_frame, bg="#f4f6f7", bd=0, highlightthickness=0)
        self.scroll_canvas.pack(side="left", fill="both", expand=True)

        # Vincular barra y canvas recíprocamente
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar_lateral.set)
        self.scrollbar_lateral.configure(command=self.scroll_canvas.yview)

        # 5. El Frame interno real donde se guardan tus botones organizados
        self.button_frame = tk.Frame(self.scroll_canvas, bg="#f4f6f7")
        self.canvas_window = self.scroll_canvas.create_window((0, 0), window=self.button_frame, anchor="nw")

        # FUNCIÓN INTELIGENTE: Muestra la barra al 100% de altura SÓLO si hace falta
        def controlar_visibilidad_scroll(event=None):
            self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

            altura_contenido = self.button_frame.winfo_reqheight()
            altura_disponible = self.scroll_canvas.winfo_height()

            if altura_contenido > altura_disponible and altura_disponible > 1:
                if not self.scrollbar_lateral.winfo_manager():
                    # Al empaquetarlo en el sub-contenedor con side="right" y fill="y", toma el 100% del alto
                    self.scrollbar_lateral.pack(side="right", fill="y")
            else:
                if self.scrollbar_lateral.winfo_manager():
                    self.scrollbar_lateral.pack_forget()

        # Enlaces de eventos para actualizar tamaños dinámicamente al abrir menús
        self.button_frame.bind("<Configure>", controlar_visibilidad_scroll)
        self.scroll_canvas.bind("<Configure>",
                                lambda e: (self.scroll_canvas.itemconfig(self.canvas_window, width=e.width),
                                           controlar_visibilidad_scroll()))

        # Control de la rueda del ratón
        def on_mouse_wheel(event):
            if self.scrollbar_lateral.winfo_manager():
                self.scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.scroll_canvas.bind("<Enter>", lambda event: self.scroll_canvas.bind_all("<MouseWheel>", on_mouse_wheel))
        self.scroll_canvas.bind("<Leave>", lambda event: self.scroll_canvas.unbind_all("<MouseWheel>"))

        # 6. CONTENEDOR FIJO INFERIOR PARA EL BOTÓN SALIR (Pegado abajo, sin huecos)
        self.exit_frame = tk.Frame(self.sidebar_container, bg="#f4f6f7")
        self.exit_frame.pack(side="bottom", fill="x", pady=(5, 5))
        # =====================================================================

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
            value="Estado: OK | Aeropuertos: 0 | Vuelos (Arr): 0 | Salidas (Dep): 0 | Estructura LEBL: No cargada")  # Variable de texto interactiva de Tkinter
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
        if hasattr(self, "status_bar"):
            self.status_bar.pack(side="bottom", fill="x")
            self.status_bar.lift()

    def build_music_file(self):
        """Crea un pequeño bucle musical local para el hilo musical de la interfaz."""
        if self.music_file and os.path.exists(self.music_file):
            return self.music_file

        ruta = os.path.join(tempfile.gettempdir(), "airport_background_loop_soft.wav")
        sample_rate = 22050
        duration = 8
        notas = [261.63, 293.66, 329.63, 392.00, 329.63, 293.66, 246.94, 261.63]

        with wave.open(ruta, "w") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)

            total_samples = sample_rate * duration
            samples_por_nota = sample_rate
            for i in range(total_samples):
                nota = notas[(i // samples_por_nota) % len(notas)]
                posicion = (i % samples_por_nota) / samples_por_nota
                envelope = 0.18
                if posicion < 0.08:
                    envelope *= posicion / 0.08
                elif posicion > 0.82:
                    envelope *= max(0.0, (1.0 - posicion) / 0.18)
                valor = int(8000 * envelope * math.sin(2 * math.pi * nota * i / sample_rate))
                wav_file.writeframes(struct.pack("<h", valor))

        self.music_file = ruta
        return ruta

    def start_background_music(self):
        """Activa el hilo musical en bucle si el sonido está habilitado."""
        try:
            winsound.PlaySound(self.build_music_file(), winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
        except Exception:
            self.music_enabled = False

    def stop_background_music(self):
        """Detiene cualquier sonido asíncrono activo."""
        try:
            winsound.PlaySound(None, winsound.SND_PURGE)
        except Exception:
            pass

    def toggle_music(self):
        """Alterna el hilo musical entre sonido y silencio."""
        if self.music_enabled:
            self.stop_background_music()
            self.music_enabled = False
            self.music_button.configure(text="🔇")
        else:
            self.music_enabled = True
            self.music_button.configure(text="🔊")
            self.start_background_music()

    def close_app(self):
        """Cierra la aplicación deteniendo antes el sonido de fondo."""
        self.stop_background_music()
        self.root.destroy()

    def center_window(self, window, width, height):
        """Centra una ventana secundaria respecto a la ventana principal."""
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (width // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{max(x, 0)}+{max(y, 0)}")

    def update_status(self):
        """Lee el tamaño actual de las listas y actualiza la barra informativa del pie de página en tiempo real."""
        lebl_status = f"Cargada ({self.bcn_airport.code})" if self.bcn_airport else "No cargada"
        if not self.status_bar.winfo_ismapped():
            self.status_bar.pack(side="bottom", fill="x")
        self.status_bar.lift()
        self.status_var.set(
            f"Estado: OK | Aeropuertos: {len(self.lista_aeropuertos)} | Vuelos (Arr): {len(self.lista_vuelos)} | Salidas (Dep): {len(self.lista_salidas)} | Estructura LEBL: {lebl_status}")

    def mark_file_button_loaded(self, button):
        """Marca visualmente en azul suave un botón cuyo fichero ya se ha cargado."""
        if button:
            button.configure(style="Loaded.TButton")

    def show_loaded_table(self, title, columns, rows):
        """Muestra cualquier fichero cargado con el mismo formato de tabla en el panel derecho."""
        self.clear_plot_frame()

        container = tk.Frame(self.plot_frame, bg="white")
        container.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(
            container,
            text=title,
            font=("Segoe UI", 12, "bold"),
            bg="white",
            fg="#355C8A"
        ).pack(anchor="w", pady=(0, 8))

        table_frame = tk.Frame(container, bg="white")
        table_frame.pack(fill="both", expand=True)

        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical")
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal")
        scrollbar_x.pack(side="bottom", fill="x")

        tabla = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )
        tabla.pack(fill="both", expand=True)
        scrollbar_y.config(command=tabla.yview)
        scrollbar_x.config(command=tabla.xview)

        for col in columns:
            tabla.heading(col, text=col)
            tabla.column(col, anchor="center", width=140, minwidth=90)

        i = 0
        while i < len(rows):
            tabla.insert("", "end", values=rows[i])
            i += 1

        if "Código" in columns and "Schengen" in columns:
            def seleccionar_aeropuerto(event):
                item = tabla.focus()
                if item:
                    valores = tabla.item(item, "values")
                    if valores:
                        self.selected_airport_code = valores[0]
                        self.delete_entry.delete(0, tk.END)
                        self.delete_entry.insert(0, self.selected_airport_code)

            tabla.bind("<Double-1>", seleccionar_aeropuerto)

        self.update_status()

    def open_kml_in_google_earth(self, filename):
        """Abre el KML con la aplicación asociada del sistema, normalmente Google Earth."""
        try:
            os.startfile(os.path.abspath(filename))
            return True
        except Exception as e:
            messagebox.showerror("Google Earth", f"No se pudo abrir el KML automáticamente:\n{e}")
            return False

    # =====================================================================================
    # SECCIÓN 3: CONSTRUCCIÓN DEL MENÚ INTERACTIVO (CONTRACCIONES Y DESPLEGABLES)
    # =====================================================================================
    def setup_collapsible_menus(self):
        """Crea los botones principales y los subpaneles ocultos para simular un menú de pestañas colapsables."""

        # ----------------- SUBMENÚ 1: AEROPUERTOS -----------------
        self.btn_toggle_airports = tk.Button(self.button_frame,
            text="▲ AEROPUERTOS",
            width=35,
            bg="#8FB6E8",
            activebackground="#76A7E2",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.toggle_airports_panel)
        self.btn_toggle_airports.pack(fill="x", pady=(5, 0))

        self.airports_content = tk.Frame(self.button_frame, bg="#f4f6f7", bd=1, relief="groove")

        self.btn_load_airports_file = ttk.Button(self.airports_content, text="Cargar fichero de Aeropuertos", width=33,
                                                 command=self.f_load)
        self.btn_load_airports_file.pack(pady=2, padx=5)
        ttk.Button(self.airports_content, text="Calcular atributo Schengen (automatic)", width=33,
                   command=self.f_schengen).pack(pady=2, padx=5)
        ttk.Button(self.airports_content, text="Schengen (manual)", width=33, command=self.f_manual_schengen).pack(
            pady=2, padx=5)
        ttk.Button(self.airports_content, text="Mostrar tabla de aeropuertos", width=33, command=self.f_show).pack(
            pady=2, padx=5)
        ttk.Button(self.airports_content, text="Gráfico: Schengen / No Schengen", width=33,
                   command=self.f_plot_airports_embedded).pack(pady=2, padx=5)
        ttk.Button(self.airports_content, text="Exportar Schengen a fichero", width=33, command=self.f_save).pack(
            pady=2, padx=5)
        ttk.Button(self.airports_content, text="Abrir aeropuertos en Google Earth", width=33, command=self.f_map).pack(
            pady=2, padx=5)

        airport_edit_zone = tk.LabelFrame(self.airports_content, text="Gestionar aeropuerto por ICAO", bg="#f4f6f7",
                                          font=("Segoe UI", 9, "bold"))
        airport_edit_zone.pack(fill="x", pady=5, padx=(2, 5))

        tk.Label(airport_edit_zone, text="Eliminar ICAO:", bg="#f4f6f7").grid(row=0, column=0, sticky="w", padx=(2, 2), pady=2)
        self.delete_entry = ttk.Entry(airport_edit_zone, width=8, font=("Segoe UI", 10, "bold"))
        self.delete_entry.grid(row=0, column=1, padx=2, pady=2)
        ttk.Button(airport_edit_zone, text="Eliminar", width=7, command=self.f_delete_dynamic).grid(row=0, column=2, padx=2, pady=2)
        tk.Label(airport_edit_zone, text="Para eliminar solo hace falta el código ICAO.", bg="#f4f6f7", fg="#5d6d7e",
                 font=("Segoe UI", 8, "italic")).grid(row=1, column=0, columnspan=4, sticky="w", padx=2, pady=(0, 4))

        tk.Label(airport_edit_zone, text="Añadir ICAO:", bg="#f4f6f7").grid(row=2, column=0, sticky="w", padx=(2, 2), pady=2)
        self.add_code_entry = ttk.Entry(airport_edit_zone, width=8, font=("Segoe UI", 10, "bold"))
        self.add_code_entry.grid(row=2, column=1, padx=2, pady=2)
        ttk.Button(airport_edit_zone, text="Añadir", width=7, command=self.f_add_dynamic).grid(row=2, column=2, padx=2, pady=2)
        tk.Label(airport_edit_zone, text="Para añadir hacen falta código ICAO, latitud y longitud.", bg="#f4f6f7", fg="#5d6d7e",
                 font=("Segoe UI", 8, "italic")).grid(row=3, column=0, columnspan=4, sticky="w", padx=2, pady=(0, 4))

        coords_frame = tk.Frame(airport_edit_zone, bg="#f4f6f7")
        coords_frame.grid(row=4, column=0, columnspan=4, sticky="w", padx=(2, 0), pady=(4, 0))
        tk.Label(coords_frame, text="Latitud:", bg="#f4f6f7").pack(side="left", padx=(0, 2))
        self.add_lat_entry = ttk.Entry(coords_frame, width=10, justify="center")
        self.add_lat_entry.pack(side="left", padx=(0, 4))
        tk.Label(coords_frame, text="Longitud:", bg="#f4f6f7").pack(side="left", padx=(0, 2))
        self.add_lon_entry = ttk.Entry(coords_frame, width=10, justify="center")
        self.add_lon_entry.pack(side="left", padx=(0, 2))
        tk.Label(
            airport_edit_zone,
            text="Sistema: grados decimales.\nEjemplo LEBL: 41.2974 / 2.0833",
            bg="#f4f6f7",
            fg="#5d6d7e",
            font=("Segoe UI", 8, "italic"),
            justify="center"
        ).grid(row=5, column=0, columnspan=4, sticky="ew", padx=3, pady=(2, 4))

        # ----------------- SUBMENÚ 2: ARRIVALS DE VUELOS -----------------
        self.btn_toggle_flights = tk.Button(
            self.button_frame,
            text="▲ ARRIVALS DE VUELOS",
            width=35,
            bg="#8FB6E8",
            activebackground="#76A7E2",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.toggle_flights_panel
        )
        self.btn_toggle_flights.pack(fill="x", pady=(5, 0))

        self.flights_content = tk.Frame(self.button_frame, bg="#f4f6f7", bd=1, relief="groove")

        self.btn_load_arrivals_file = ttk.Button(self.flights_content, text="Cargar archivo de arrivals", width=33,
                                                 command=self.f_load_arrivals)
        self.btn_load_arrivals_file.pack(pady=2, padx=5)
        ttk.Button(self.flights_content, text="Gráfico: frecuencia horaria", width=33,
                   command=self.f_plot_arrivals_embedded).pack(pady=2, padx=5)
        ttk.Button(self.flights_content, text="Gráfico: arrivals por aerolínea", width=33,
                   command=self.f_ui_plot_airlines_selected).pack(pady=2, padx=5)
        ttk.Button(self.flights_content, text="Gráfico: arrivals por origen", width=33,
                   command=self.f_plot_type_embedded).pack(pady=2, padx=5)
        ttk.Button(self.flights_content, text="Guardar arrivals a fichero", width=33,
                   command=self.f_save_flights).pack(pady=2, padx=5)
        ttk.Button(self.flights_content, text="Abrir trayectorias en Google Earth", width=33,
                   command=self.f_map_flights).pack(pady=2, padx=5)
        ttk.Button(self.flights_content, text="Filtrar larga distancia (>2000 km)", width=33,
                   command=self.f_long_flights).pack(pady=2, padx=5)

        # ----------------- SUBMENÚ 3: ADMINISTRADOR DE GATES LEBL -----------------
        self.btn_toggle_gates = tk.Button(self.button_frame,
            text="▲ ADMINISTRADOR DE GATES (LEBL)",
            width=35,
            bg="#8FB6E8",
            activebackground="#76A7E2",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.toggle_gates_panel)
        self.btn_toggle_gates.pack(fill="x", pady=(5, 0))

        self.gates_content = tk.Frame(self.button_frame, bg="#f4f6f7", bd=1, relief="groove")

        self.btn_load_structure_file = ttk.Button(self.gates_content, text="Cargar estructura LEBL", width=33,
                                                  command=self.f_ui_load_airport_structure)
        self.btn_load_structure_file.pack(pady=2, padx=5)
        ttk.Button(self.gates_content, text="Tabla de ocupación de gates", width=33,
                   command=self.f_ui_gate_occupancy).pack(pady=2, padx=5)
        ttk.Button(self.gates_content, text="Mapa de gates utilizadas", width=33,
                   command=self.f_ui_gate_usage_diagram).pack(pady=2, padx=5)
        ttk.Button(self.gates_content, text="Configurar gates por área", width=33,
                   command=self.f_ui_set_gates).pack(pady=2, padx=5)
        self.btn_load_airlines_file = ttk.Button(self.gates_content, text="Cargar aerolíneas T1/T2", width=33,
                                                 command=self.f_ui_load_airlines)
        self.btn_load_airlines_file.pack(pady=2, padx=5)
        ttk.Button(self.gates_content, text="Verificar aerolínea en terminal", width=33,
                   command=self.f_ui_is_airline_in_terminal).pack(pady=2, padx=5)
        ttk.Button(self.gates_content, text="Buscar terminal de aerolínea", width=33,
                   command=self.f_ui_search_terminal).pack(pady=2, padx=5)
        ttk.Button(self.gates_content, text="Asignar gate a vuelo", width=33,
                   command=self.f_ui_assign_gate).pack(pady=2, padx=5)
        ttk.Button(self.gates_content, text="Localizar gate por vuelo", width=33,
                   command=self.f_ui_locate_flight_gate).pack(pady=2, padx=5)

        # ----------------- SUBMENÚ 4: SALIDAS -----------------
        self.btn_toggle_fase4 = tk.Button(self.button_frame,
                                          text="▲ SALIDAS",
                                          width=35,
                                          bg="#8FB6E8",
                                          activebackground="#76A7E2",
                                          font=("Segoe UI", 10, "bold"),
                                          relief="flat",
                                          cursor="hand2",
                                          command=self.toggle_fase4_panel)
        self.btn_toggle_fase4.pack(fill="x", pady=(5, 0))

        self.fase4_content = tk.Frame(self.button_frame, bg="#f4f6f7", bd=1, relief="groove")

        self.btn_load_departures_file = ttk.Button(self.fase4_content, text="Cargar fichero departures", width=33,
                                                   command=self.f_ui_load_departures)
        self.btn_load_departures_file.pack(pady=2, padx=5)
        ttk.Button(self.fase4_content, text="Fusionar arrivals/departures", width=33,
                   command=self.f_ui_merge_movements).pack(pady=2, padx=5)
        ttk.Button(self.fase4_content, text="Asignar Pernoctas", width=33,
                   command=self.f_ui_night_aircraft).pack(pady=2, padx=5)
        ttk.Button(self.fase4_content, text="Asignación dinámica por hora", width=33,
                   command=self.f_ui_assign_gates_at_time).pack(pady=2, padx=5)
        ttk.Button(self.fase4_content, text="Gráfico: ocupación diaria 24h", width=33,
                   command=self.f_ui_plot_day_occupancy_embedded).pack(pady=2, padx=5)
        ttk.Button(self.fase4_content, text="Mapa de gates por hora", width=33,
                   command=self.f_ui_plot_movements_by_hour).pack(pady=2, padx=5)
        ttk.Button(self.fase4_content, text="Saturación del aeropuerto", width=33,
                   command=self.f_ui_radar_saturacion).pack(pady=2, padx=5)

        # NUEVO BOTÓN: Auditoría de Conectividad Hub
        ttk.Button(self.fase4_content, text="Auditoría Hub Analysis", width=33,
                   command=self.f_ui_hub_analysis).pack(pady=2, padx=5)
        ttk.Button(self.fase4_content, text="Análisis METAR", width=33,
                   command=self.f_ui_metar_analysis).pack(pady=2, padx=5)

        # Cierre Seguro de Aplicación
        tk.Button(self.exit_frame, text="SALIR DE LA APLICACIÓN", width=35, bg="#C0392B", fg="white",
                  activebackground="#A93226", activeforeground="white", font=("Segoe UI", 10, "bold"), relief="flat",
                  cursor="hand2", command=self.f_ui_exit_with_feedback).pack(fill="x")

    # --- MÉTODOS DE ANIMACIÓN DE LOS MENÚS (PACK / PACK_FORGET) ---
        # =====================================================================================
        # NOU MÈTODE FASE 1: FILTRATGE DINÀMIC D'AEROLÍNIES SELECCIONADES
        # =====================================================================================


    def f_ui_exit_with_feedback(self):
        """
        Muestra una pantalla de encuesta de satisfacción integrada directamente
        en el panel derecho de visualización (self.plot_frame).
        Configuración: Casillas MAXIMIZADAS, textos/bordes negros y mensaje
        personalizado de disculpa si se selecciona la opción "Mal".
        """
        # 1. Limpiamos por completo el panel derecho de gráficos usando tu método existente
        self.clear_plot_frame()

        # 2. Creamos un contenedor principal grande centrado dentro del panel derecho
        encuesta_container = tk.Frame(self.plot_frame, bg="white")
        encuesta_container.pack(expand=True, fill="both", padx=40, pady=40)

        # 3. Etiqueta con la pregunta solicitada (Texto grande en color negro)
        tk.Label(
            encuesta_container,
            text="¿Qué te ha parecido el programa?",
            font=("Segoe UI", 22, "bold"),  # Tamaño de la pregunta grande
            bg="white",
            fg="black"
        ).pack(pady=(60, 50))

        # 4. Contenedor horizontal para situar los tres botones gigantes de opción
        btn_frame = tk.Frame(encuesta_container, bg="white")
        btn_frame.pack(pady=20)

        # 5. Función interna encargada de capturar la opinión, evaluar la respuesta y cerrar
        def registrar_y_salir(opinion):
            print(f"Feedback registrado directamente en interfaz: {opinion}")

            # Limpiamos los botones y la pregunta para dar una transición limpia de despedida
            for widget in encuesta_container.winfo_children():
                widget.destroy()

            # NUEVO: Evaluamos si la opinión ha sido "Mal" para cambiar el mensaje en pantalla
            if opinion == "Mal":
                texto_despedida = "Lamentamos escuchar eso. ¡Trabajaremos duro para mejorar!\nCerrando el sistema..."
                color_texto = "#c0392b"  # Color rojo oscuro para enfatizar la disculpa
            else:
                texto_despedida = "¡Muchas gracias por tu colaboración!\nCerrando el sistema..."
                color_texto = "black"  # Texto negro estándar para Bien/Normal

            # Mostramos el mensaje correspondiente en el contenedor
            tk.Label(
                encuesta_container,
                text=texto_despedida,
                font=("Segoe UI", 18, "bold"),
                bg="white",
                fg=color_texto
            ).pack(expand=True)

            # Pausa de 1.5 segundos para que el usuario pueda leer el mensaje antes de salir
            self.root.after(1500, self.root.quit)

        # 6. DEFINICIÓN DE LOS TRES BOTONES MAXIMIZADOS (FONDO DE COLOR, TEXTO NEGRO Y BORDE NEGRO)

        # Botón "Bien" (Fondo Verde, Letras Negras, Borde Negro - GIGANTE)
        tk.Button(
            btn_frame,
            text="😊 Bien",
            font=("Segoe UI", 18, "bold"),  # Letra tamaño 18
            bg="#2ECC71",  # Fondo verde
            fg="black",  # Caras y texto en NEGRO
            activebackground="#27AE60",
            activeforeground="black",
            width=16,  # Ancho maximizado
            height=3,  # Alto de triple fila
            relief="flat",
            highlightbackground="black",  # Color del borde: NEGRO
            highlightthickness=1,  # Grosor del borde: 1 píxel
            cursor="hand2",
            command=lambda: registrar_y_salir("Bien")
        ).pack(side="left", padx=20)  # Separación lateral

        # Botón "Normal" (Fondo Amarillo, Letras Negras, Borde Negro - GIGANTE)
        tk.Button(
            btn_frame,
            text="😐 Normal",
            font=("Segoe UI", 18, "bold"),
            bg="#F1C40F",  # Fondo amarillo
            fg="black",
            activebackground="#D4AC0D",
            activeforeground="black",
            width=16,
            height=3,
            relief="flat",
            highlightbackground="black",
            highlightthickness=1,
            cursor="hand2",
            command=lambda: registrar_y_salir("Normal")
        ).pack(side="left", padx=20)

        # Botón "Mal" (Fondo Rojo, Letras Negras, Borde Negro - GIGANTE)
        tk.Button(
            btn_frame,
            text="🙁 Mal",
            font=("Segoe UI", 18, "bold"),
            bg="#E74C3C",  # Fondo rojo
            fg="black",
            activebackground="#C0392B",
            activeforeground="black",
            width=16,
            height=3,
            relief="flat",
            highlightbackground="black",
            highlightthickness=1,
            cursor="hand2",
            command=lambda: registrar_y_salir("Mal")
        ).pack(side="left", padx=20)

    def f_ui_radar_saturacion(self):
        """
        Analiza la carga horaria de vuelos y muestra las 24 horas con un estilo claro y coherente con la interfaz.
        """
        movimientos_activos = []
        if hasattr(self, 'lista_unificada') and self.lista_unificada:
            movimientos_activos = self.lista_unificada
        elif hasattr(self, 'lista_vuelos') and self.lista_vuelos:
            movimientos_activos = self.lista_vuelos
        else:
            messagebox.showerror("Saturación del Aeropuerto",
                                 "No hay operaciones cargadas. Carga vuelos o realiza la fusión de movimientos primero.")
            return

        self.clear_plot_frame()

        style = ttk.Style()
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass
        style.configure("SaturacionVerde.Horizontal.TProgressbar", foreground='#7fbf7b', background='#7fbf7b', thickness=10)
        style.configure("SaturacionAmarillo.Horizontal.TProgressbar", foreground='#f0c86a', background='#f0c86a', thickness=10)
        style.configure("SaturacionRojo.Horizontal.TProgressbar", foreground='#df6b6b', background='#df6b6b', thickness=10)

        main_frame = tk.Frame(self.plot_frame, bg="white")
        main_frame.pack(fill="both", expand=True, padx=18, pady=14)

        tk.Label(
            main_frame,
            text="Saturación del aeropuerto",
            font=("Segoe UI", 15, "bold"),
            bg="white",
            fg="#355C8A"
        ).pack(anchor="w", pady=(0, 8))

        legend_frame = tk.Frame(main_frame, bg="white")
        legend_frame.pack(fill="x", pady=(0, 10))

        leyenda = [
            ("Estable", "hasta el 40% del pico horario", "#dff0d8"),
            ("Atención", "hasta el 75% del pico horario", "#fcf3cf"),
            ("Crítico", "por encima del 75%", "#f5c6c6"),
        ]
        i = 0
        while i < len(leyenda):
            nombre, descripcion, color = leyenda[i]
            bloque = tk.Frame(legend_frame, bg=color, highlightbackground="#bfc9d4", highlightthickness=1)
            bloque.pack(side="left", padx=(0, 8), ipadx=8, ipady=4)
            tk.Label(bloque, text=nombre, bg=color, fg="#2c3e50", font=("Segoe UI", 9, "bold")).pack(side="left")
            tk.Label(bloque, text=" - " + descripcion, bg=color, fg="#566573", font=("Segoe UI", 9)).pack(side="left")
            i += 1

        conteo_horas = [0] * 24
        for m in movimientos_activos:
            t_str = m.time if hasattr(m, 'time') and m.time else getattr(m, 'departure_time', "00:00")
            try:
                h = int(str(t_str).split(":")[0])
                if 0 <= h < 24:
                    conteo_horas[h] += 1
            except:
                pass

        grid_frame = tk.Frame(main_frame, bg="white")
        grid_frame.pack(fill="both", expand=True)

        horas_criticas = 0
        max_vuelos_esperados = max(max(conteo_horas), 1)
        limite_verde = max(3, int(max_vuelos_esperados * 0.40))
        limite_amarillo = max(limite_verde + 1, int(max_vuelos_esperados * 0.75))

        for i in range(24):
            fila = i // 6
            columna = i % 6
            vuelos = conteo_horas[i]

            if vuelos > limite_amarillo:
                color_casilla = "#f5c6c6"
                estilo_barra = "SaturacionRojo.Horizontal.TProgressbar"
                estado = "Crítico"
                horas_criticas += 1
            elif vuelos > limite_verde:
                color_casilla = "#fcf3cf"
                estilo_barra = "SaturacionAmarillo.Horizontal.TProgressbar"
                estado = "Atención"
            else:
                color_casilla = "#dff0d8"
                estilo_barra = "SaturacionVerde.Horizontal.TProgressbar"
                estado = "Estable"

            casilla = tk.Frame(
                grid_frame,
                bg=color_casilla,
                highlightbackground="#aeb6bf",
                highlightthickness=1,
                width=165,
                height=88
            )
            casilla.grid(row=fila, column=columna, padx=6, pady=5, sticky="nsew")
            casilla.grid_propagate(False)
            grid_frame.grid_columnconfigure(columna, weight=1)
            grid_frame.grid_rowconfigure(fila, weight=1)

            tk.Label(casilla, text=f"{str(i).zfill(2)}:00", font=("Segoe UI", 10, "bold"), bg=color_casilla,
                     fg="#2c3e50").pack(pady=(5, 1))

            progreso = ttk.Progressbar(casilla, orient="horizontal", length=120, mode="determinate", style=estilo_barra)
            progreso.pack(pady=3)
            progreso['value'] = (vuelos / max_vuelos_esperados) * 100

            tk.Label(casilla, text=f"{vuelos} operaciones", font=("Segoe UI", 9), bg=color_casilla,
                     fg="#2c3e50").pack()
            tk.Label(casilla, text=estado, font=("Segoe UI", 8, "bold"), bg=color_casilla,
                     fg="#2c3e50").pack()

        if horas_criticas > 0:
            diagnostico_txt = f"Se detectan {horas_criticas} franjas horarias críticas."
            color_diag = "#c0392b"
        else:
            diagnostico_txt = "No se detectan franjas críticas con los datos cargados."
            color_diag = "#1e8449"

        tk.Label(
            main_frame,
            text=diagnostico_txt,
            font=("Segoe UI", 11, "bold"),
            bg="white",
            fg=color_diag
        ).pack(anchor="w", pady=(10, 0))

    def f_ui_hub_analysis(self):
        """
        Analiza las ventanas de tiempo entre vuelos de llegada y salida para el Hub.
        Incluye un panel de KPIs interactivos, el ranking de operadores y un bloque
        de documentación explicativa integrada de la lógica de negocio.
        """
        # 1. Escaneo de memoria automatizado
        vuelos_llegada = []
        for attr in ['lista_vuelos', 'vuelos', 'lista_llegadas', 'vuelos_llegada']:
            if hasattr(self, attr) and getattr(self, attr):
                vuelos_llegada = getattr(self, attr)
                break

        vuelos_salida = []
        for attr in ['lista_salidas', 'salidas', 'vuelos_salida', 'lista_unificada']:
            if hasattr(self, attr) and getattr(self, attr):
                vuelos_salida = getattr(self, attr)
                break

        if not vuelos_llegada or not vuelos_salida:
            messagebox.showerror(
                "Auditoría de Conectividad",
                f"Error de datos.\nLlegadas en memoria: {len(vuelos_llegada)}\nSalidas en memoria: {len(vuelos_salida)}"
            )
            return

        # 2. Limpiar el panel derecho antes de dibujar
        self.clear_plot_frame()

        # Contenedor principal
        hub_frame = tk.Frame(self.plot_frame, bg="white")
        hub_frame.pack(expand=True, fill="both", padx=20, pady=15)

        # Encabezado principal corporativo
        tk.Label(
            hub_frame,
            text="📊 AUDITORÍA DE CONECTIVIDAD: HUB ANALYSIS",
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(pady=(5, 10))

        # 3. LÓGICA DE EXTRACCIÓN Y PROCESAMIENTO DE DATOS
        conexiones_viables = 0
        conexiones_criticas_maletas = 0
        conexiones_por_aerolinea = {}

        def a_minutos(hora_str):
            if not hora_str: return -1
            hora_str = str(hora_str).strip()
            if " " in hora_str: hora_str = hora_str.split(" ")[1]
            if ":" not in hora_str: return -1
            try:
                partes = hora_str.split(':')
                return int(partes[0]) * 60 + int(partes[1])
            except:
                return -1

        def extraer_datos_vuelo(vuelo):
            linea = "UNKNOWN"
            hora = ""
            if vuelo is None: return linea, hora

            if isinstance(vuelo, dict):
                for k in vuelo.keys():
                    if k.lower() in ['airline', 'compania', 'operator', 'carrier', 'company', 'aerolinea']:
                        linea = vuelo[k]
                    if k.lower() in ['time', 'departure_time', 'arrival_time', 'hora', 'std', 'etd']:
                        hora = vuelo[k]
            else:
                for attr in ['airline', 'compania', 'operator', 'carrier', 'company', 'aerolinea', 'Airline']:
                    if hasattr(vuelo, attr) and getattr(vuelo, attr):
                        linea = getattr(vuelo, attr)
                        break
                for attr in ['std', 'etd', 'time', 'departure_time', 'arrival_time', 'hora', 'Time', 'schedule_time']:
                    if hasattr(vuelo, attr) and getattr(vuelo, attr):
                        hora = getattr(vuelo, attr)
                        break
            return str(linea).upper().strip(), str(hora).strip()

        # Bucle de cruce de datos
        for arr in vuelos_llegada:
            arr_airline, arr_time_str = extraer_datos_vuelo(arr)
            arr_min = a_minutos(arr_time_str)
            if arr_min == -1 or arr_airline == "UNKNOWN" or len(arr_airline) < 2:
                continue

            for dep in vuelos_salida:
                dep_airline, dep_time_str = extraer_datos_vuelo(dep)
                dep_min = a_minutos(dep_time_str)
                if dep_min == -1 or dep_airline == "UNKNOWN":
                    continue

                es_misma_aerolinea = (arr_airline in dep_airline) or (dep_airline in arr_airline) or (arr_airline[:3] == dep_airline[:3])

                if es_misma_aerolinea:
                    dif = dep_min - arr_min
                    if dif < 0: dif += 1440

                    if 0 <= dif < 35:
                        conexiones_criticas_maletas += 1
                    elif 35 <= dif <= 240:
                        conexiones_viables += 1
                        conexiones_por_aerolinea[arr_airline[:12]] = conexiones_por_aerolinea.get(arr_airline[:12], 0) + 1

        # 4. RENDERIZADO VISUAL: SECCIÓN KPIs (Bordes negros estrictos)
        metrics_frame = tk.LabelFrame(hub_frame, text=" Indicadores Clave de Rendimiento (KPIs) ", font=("Segoe UI", 10, "bold"), bg="#f8f9fa", fg="#34495e", bd=1, relief="solid")
        metrics_frame.pack(fill="x", padx=10, pady=5)

        kpi1 = tk.Frame(metrics_frame, bg="#dff0d8", highlightbackground="black", highlightthickness=1, width=220, height=75)
        kpi1.pack(side="left", expand=True, padx=10, pady=8)
        kpi1.pack_propagate(False)
        tk.Label(kpi1, text="Conexiones Viables", font=("Segoe UI", 10, "bold"), bg="#dff0d8", fg="#1e8449").pack(pady=(8,0))
        tk.Label(kpi1, text=str(conexiones_viables), font=("Segoe UI", 15, "bold"), bg="#dff0d8", fg="black").pack()

        kpi2 = tk.Frame(metrics_frame, bg="#f2dede", highlightbackground="black", highlightthickness=1, width=220, height=75)
        kpi2.pack(side="left", expand=True, padx=10, pady=8)
        kpi2.pack_propagate(False)
        tk.Label(kpi2, text="Riesgo Pérdida de Maletas", font=("Segoe UI", 10, "bold"), bg="#f2dede", fg="#c0392b").pack(pady=(8,0))
        tk.Label(kpi2, text=str(conexiones_criticas_maletas), font=("Segoe UI", 15, "bold"), bg="#f2dede", fg="black").pack()

        # Ranking de aerolíneas
        ranking_frame = tk.LabelFrame(hub_frame, text=" Eficiencia por Operador (Top Conexiones Activas) ", font=("Segoe UI", 10, "bold"), bg="white", fg="#34495e", bd=1, relief="solid")
        ranking_frame.pack(fill="x", padx=10, pady=5)

        if conexiones_por_aerolinea:
            sorted_airlines = sorted(conexiones_por_aerolinea.items(), key=lambda x: x[1], reverse=True)
            tk.Label(ranking_frame, text=f"  {'AEROLÍNEA':<22}{'CONEXIONES CONTROLADAS':<25}", font=("Consolas", 10, "bold"), bg="#eef2f5", fg="black", anchor="w", padx=10).pack(fill="x", pady=(2,2))
            for air, total in sorted_airlines[:3]: # Mostramos las 3 principales para dejar espacio al panel explicativo
                tk.Label(ranking_frame, text=f"  ✈️ {air:<20}{total:<25}", font=("Consolas", 10), bg="white", fg="black", anchor="w", padx=15).pack(fill="x", pady=1)
        else:
            tk.Label(ranking_frame, text="No se detectaron conexiones directas con este set de datos.", font=("Segoe UI", 10, "italic"), bg="white", fg="gray").pack(pady=10)

        # 5. NUEVO PANEL: DOCUMENTACIÓN Y EXPLICACIÓN DE LA FUNCIÓN
        help_frame = tk.LabelFrame(hub_frame, text=" 📑 ¿Qué hace esta herramienta? (Guía de Operación Hub) ", font=("Segoe UI", 10, "bold"), bg="#e8f4f8", fg="#2980b9", bd=1, relief="solid")
        help_frame.pack(fill="both", expand=True, padx=10, pady=(8, 5))

        texto_explicativo = (
            "• Evalúa la eficiencia del aeropuerto como Hub analizando la coordinación temporal entre llegadas y salidas.\n\n"
            "• 🟢 Conexión Viable (35 min — 4 h): tiempo suficiente para que el pasajero cruce la terminal y embarque.\n\n"
            "• 🔴 Riesgo de Maletas (< 35 min): ventana demasiado corta, el handling no puede trasladar el equipaje a tiempo."
        )

        txt_label = tk.Label(
            help_frame,
            text=texto_explicativo,
            font=("Segoe UI", 9),
            bg="#e8f4f8",
            fg="#2c3e50",
            justify="left",
            anchor="nw",
            wraplength=520,
            padx=10,
            pady=10
        )
        txt_label.pack(fill="both", expand=True)

        # 6. Conclusión diagnóstica breve al pie
        if conexiones_criticas_maletas > 0 or conexiones_viables > 0:
            if conexiones_criticas_maletas > (conexiones_viables * 0.2):
                conclusion_txt = "⚠️ ALERTA: Ratio de conexiones críticas elevado. Riesgo de pérdida de equipaje."
                color_txt = "#c0392b"
            else:
                conclusion_txt = "🟢 AUDITORÍA SATISFACTORIA: Tiempos de escala equilibrados en la terminal."
                color_txt = "#1e8449"
        else:
            conclusion_txt = "ℹ️ ANÁLISIS COMPLETADO: Sin datos suficientes para generar un diagnóstico definitivo."
            color_txt = "#7f8c8d"

        tk.Label(hub_frame, text=conclusion_txt, font=("Segoe UI", 10, "bold"), bg="white", fg=color_txt, wraplength=500).pack(pady=(5, 0))

    def toggle_airports_panel(self):
        if self.airports_visible:
            self.airports_content.pack_forget()
            self.btn_toggle_airports.configure(text="▲ AEROPUERTOS")
            self.airports_visible = False
        else:
            self.airports_content.pack(fill="x", padx=2, pady=(0, 10), after=self.btn_toggle_airports)
            self.btn_toggle_airports.configure(text="▼ AEROPUERTOS")
            self.airports_visible = True

    def toggle_flights_panel(self):
        if self.flights_visible:
            self.flights_content.pack_forget()
            self.btn_toggle_flights.configure(text="▲ ARRIVALS DE VUELOS")
            self.flights_visible = False
        else:
            self.flights_content.pack(fill="x", padx=2, pady=(0, 10), after=self.btn_toggle_flights)
            self.btn_toggle_flights.configure(text="▼ ARRIVALS DE VUELOS")
            self.flights_visible = True

    def toggle_gates_panel(self):
        if self.gates_visible:
            self.gates_content.pack_forget()
            self.btn_toggle_gates.configure(text="▲ ADMINISTRADOR DE GATES LEBL")
            self.gates_visible = False
        else:
            self.gates_content.pack(fill="x", padx=2, pady=(0, 10), after=self.btn_toggle_gates)
            self.btn_toggle_gates.configure(text="▼ ADMINISTRADOR DE GATES LEBL")
            self.gates_visible = True

    def toggle_fase4_panel(self):
        if self.fase4_visible:
            self.fase4_content.pack_forget()
            self.btn_toggle_fase4.configure(text="▲ SALIDAS")
            self.fase4_visible = False
        else:
            self.fase4_content.pack(fill="x", padx=2, pady=(0, 10), after=self.btn_toggle_fase4)
            self.btn_toggle_fase4.configure(text="▼ SALIDAS")
            self.fase4_visible = True

    # =====================================================================================
    # SECCIÓN 4: CAPA DE INTERFAZ PARA CONTROLADORES ORIGINALES Y LEBL (CON VALIDACIONES)
    # =====================================================================================
    def f_load(self):
        """Cargar Archivo Aeropuertos con validación estricta de cabecera."""
        path = filedialog.askopenfilename(title="Seleccionar aeropuertos", filetypes=[("Text files", "*.txt")])
        if path:
            try:
                # VALIDACIÓN DE CABECERA
                with open(path, "r", encoding="utf-8", errors="ignore") as f_check:
                    cabecera = f_check.readline().strip().upper()
                if "CODE" not in cabecera or "LAT" not in cabecera or "LON" not in cabecera:
                    messagebox.showerror("Error de Fichero",
                                         "El archivo seleccionado no es un fichero válido de Aeropuertos.\nCabecera esperada: CODE LAT LON")
                    return

                self.lista_aeropuertos = load_airports(path)
                messagebox.showinfo("Carga exitosa",
                                    f"Se han cargado {len(self.lista_aeropuertos)} aeropuertos mundiales.")
                self.update_status()
                self.mark_file_button_loaded(self.btn_load_airports_file)
                self.show_loaded_table(
                    "Aeropuertos cargados",
                    ("Código", "Latitud", "Longitud", "Schengen"),
                    [(a.code, round(a.lat, 6), round(a.lon, 6), "Sí" if a.schengen else "No") for a in self.lista_aeropuertos]
                )
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer el archivo: {e}")

    def f_schengen(self):
        if not self.lista_aeropuertos:
            messagebox.showerror("Error", "No hay aeropuertos cargados.")
            return
        i = 0
        while i < len(self.lista_aeropuertos):
            set_schengen(self.lista_aeropuertos[i])
            i += 1
        self.show_loaded_table(
            "Aeropuertos actualizados con atributo Schengen",
            ("Código", "Latitud", "Longitud", "Schengen"),
            [(a.code, round(a.lat, 6), round(a.lon, 6), "Sí" if a.schengen else "No") for a in self.lista_aeropuertos]
        )
        messagebox.showinfo("Proceso Completado", "Atributo Schengen calculado para toda la base.")

    def f_show(self):
        if not self.lista_aeropuertos:
            messagebox.showerror("Error", "No hay aeropuertos cargados.")
            return
        self.clear_plot_frame()
        text_widget = tk.Text(self.plot_frame, font=("Consolas", 10), wrap="none", bg="white")
        text_widget.pack(fill="both", expand=True, padx=5, pady=5)

        i = 0
        while i < len(self.lista_aeropuertos):
            a = self.lista_aeropuertos[i]
            sch_str = "Schengen" if a.schengen else "No Schengen"
            text_widget.insert(tk.END, f"Código: {a.code} | Coordenadas: {a.lat}, {a.lon} | Tipo: {sch_str}\n")
            i += 1

    def f_save(self):
        if not self.lista_aeropuertos:
            messagebox.showerror("Error", "No hay aeropuertos para guardar.")
            return
        path = filedialog.asksaveasfilename(title="Guardar como...", defaultextension=".txt",
                                            filetypes=[("Text files", "*.txt")])
        if path:
            try:
                f = open(path, "w", encoding="utf-8")
                f.write("CODE LAT LON SCHENGEN\n")
                i = 0
                while i < len(self.lista_aeropuertos):
                    a = self.lista_aeropuertos[i]
                    f.write(f"{a.code} {a.lat} {a.lon} {a.schengen}\n")
                    i += 1
                f.close()
                messagebox.showinfo("Éxito", "Archivo guardado correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar: {e}")

    def f_map(self):
        if not self.lista_aeropuertos:
            messagebox.showerror("Error", "No hay aeropuertos cargados.")
            return
        self.write_airports_kml("airports_map.kml")
        if self.open_kml_in_google_earth("airports_map.kml"):
            self.show_loaded_table(
                "KML generado para Google Earth",
                ("Archivo", "Contenido", "Estado"),
                [("airports_map.kml", "Aeropuertos cargados", "Abierto con la aplicación asociada")]
            )

    def write_airports_kml(self, filename):
        """Genera el KML de aeropuertos sin abrir una ventana externa."""
        f = open(filename, "w", encoding="utf-8")
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        f.write('<Document>\n')
        f.write('<name>Airport Map</name>\n')

        i = 0
        while i < len(self.lista_aeropuertos):
            a = self.lista_aeropuertos[i]
            color = "ffff0000" if is_schengen_airport(a.code) else "ff0000ff"
            f.write('<Placemark>\n')
            f.write('<Style><IconStyle><color>' + color + '</color></IconStyle></Style>\n')
            f.write('<name>' + a.code + '</name>\n')
            f.write('<Point><coordinates>' + str(a.lon) + ',' + str(a.lat) + '</coordinates></Point>\n')
            f.write('</Placemark>\n')
            i += 1

        f.write('</Document>\n')
        f.write('</kml>\n')
        f.close()

    def write_flights_kml(self, filename, flights=None):
        """Genera el KML de trayectorias sin abrir una ventana externa."""
        if flights is None:
            flights = self.lista_vuelos

        f = open(filename, "w", encoding="utf-8")
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        f.write('<Document>\n')

        lat_lebl = 41.297445
        lon_lebl = 2.0832941

        i = 0
        while i < len(flights):
            avion = flights[i]
            origen = None
            j = 0
            while j < len(self.lista_aeropuertos):
                if self.lista_aeropuertos[j].code == avion.origin:
                    origen = self.lista_aeropuertos[j]
                    break
                j += 1

            if origen is not None:
                color = "ffff0000" if is_schengen_airport(avion.origin) else "ff00ff00"
                f.write('<Placemark>\n')
                f.write('<Style><LineStyle><color>' + color + '</color><width>3</width></LineStyle></Style>\n')
                f.write('<LineString><tessellate>1</tessellate><coordinates>\n')
                f.write(str(origen.lon) + "," + str(origen.lat) + "\n")
                f.write(str(lon_lebl) + "," + str(lat_lebl) + "\n")
                f.write('</coordinates></LineString>\n')
                f.write('</Placemark>\n')
            i += 1

        f.write('</Document>\n')
        f.write('</kml>\n')
        f.close()

    def show_map_preview(self, airports, flights=None):
        """Muestra un mapa simple dentro del panel integrado con arrastre y zoom de ratón."""
        self.clear_plot_frame()

        map_frame = tk.Frame(self.plot_frame, bg="white")
        map_frame.pack(fill="both", expand=True)

        info = tk.Label(
            map_frame,
            text="Mapa integrado: arrastra con el ratón para mover y usa la rueda para zoom.",
            bg="white",
            fg="#34495e",
            font=("Segoe UI", 10, "italic")
        )
        info.pack(anchor="w", padx=10, pady=(8, 2))

        canvas = tk.Canvas(map_frame, bg="#eef6fb", highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=10, pady=8)

        puntos = []
        i = 0
        while i < len(airports):
            a = airports[i]
            puntos.append((a.code, a.lat, a.lon, is_schengen_airport(a.code)))
            i += 1

        if not puntos:
            canvas.create_text(30, 30, anchor="nw", text="No hay puntos para mostrar.", fill="#34495e")
            return

        min_lat = min(p[1] for p in puntos)
        max_lat = max(p[1] for p in puntos)
        min_lon = min(p[2] for p in puntos)
        max_lon = max(p[2] for p in puntos)
        if min_lat == max_lat:
            min_lat -= 1
            max_lat += 1
        if min_lon == max_lon:
            min_lon -= 1
            max_lon += 1

        width = 900
        height = 560
        margin = 35

        def project(lat, lon):
            x = margin + (lon - min_lon) / (max_lon - min_lon) * (width - 2 * margin)
            y = height - margin - (lat - min_lat) / (max_lat - min_lat) * (height - 2 * margin)
            return x, y

        canvas.configure(scrollregion=(0, 0, width, height))

        if flights:
            lat_lebl = 41.297445
            lon_lebl = 2.0832941
            lebl_x, lebl_y = project(lat_lebl, lon_lebl)
            i = 0
            while i < len(flights):
                vuelo = flights[i]
                origen = None
                j = 0
                while j < len(airports):
                    if airports[j].code == vuelo.origin:
                        origen = airports[j]
                        break
                    j += 1
                if origen is not None:
                    x, y = project(origen.lat, origen.lon)
                    color = "#2f6fb0" if is_schengen_airport(vuelo.origin) else "#2ca25f"
                    canvas.create_line(x, y, lebl_x, lebl_y, fill=color, width=1)
                i += 1

        i = 0
        while i < len(puntos):
            code, lat, lon, schengen = puntos[i]
            x, y = project(lat, lon)
            color = "#2f6fb0" if schengen else "#d64545"
            canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill=color, outline="white")
            canvas.create_text(x + 6, y - 6, anchor="w", text=code, fill="#1f2d3d", font=("Segoe UI", 8, "bold"))
            i += 1

        canvas.bind("<ButtonPress-1>", lambda event: canvas.scan_mark(event.x, event.y))
        canvas.bind("<B1-Motion>", lambda event: canvas.scan_dragto(event.x, event.y, gain=1))

        def zoom(event):
            factor = 1.1 if event.delta > 0 else 0.9
            canvas.scale("all", event.x, event.y, factor, factor)
            canvas.configure(scrollregion=canvas.bbox("all"))

        canvas.bind("<MouseWheel>", zoom)

    def f_plot_airports_embedded(self):
        if not self.lista_aeropuertos:
            messagebox.showerror("Error", "Carga aeropuertos primero.")
            return
        self.clear_plot_frame()
        schengen = 0
        not_schengen = 0
        i = 0
        while i < len(self.lista_aeropuertos):
            if self.lista_aeropuertos[i].schengen:
                schengen += 1
            else:
                not_schengen += 1
            i += 1

        fig, ax = plt.subplots(figsize=(6, 4.5), dpi=100)
        ax.bar(["Aeropuertos"], [schengen], color="blue", label="Schengen", width=0.55)
        ax.bar(["Aeropuertos"], [not_schengen], bottom=[schengen], color="red", label="No Schengen", width=0.55)
        ax.set_title("Schengen Airports", fontsize=12)
        ax.set_ylabel("Count")
        ax.legend(loc="upper right")
        ax.grid(True, axis="y", linestyle=":", alpha=0.35)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        plt.close(fig)

    def f_manual_schengen(self):
        """Marca manualmente como Schengen el aeropuerto seleccionado o escrito."""
        if not self.lista_aeropuertos:
            messagebox.showerror("Error", "Carga aeropuertos primero.")
            return

        code = self.delete_entry.get().strip().upper() or self.selected_airport_code
        if not code:
            messagebox.showwarning("Selecciona un aeropuerto",
                                   "Haz doble clic en un aeropuerto de la tabla o escribe su ICAO en el campo de eliminar.")
            return

        for aeropuerto in self.lista_aeropuertos:
            if aeropuerto.code == code:
                aeropuerto.schengen = True
                self.selected_airport_code = code
                self.show_loaded_table(
                    "Aeropuertos cargados",
                    ("Código", "Latitud", "Longitud", "Schengen"),
                    [(a.code, round(a.lat, 6), round(a.lon, 6), "Sí" if a.schengen else "No") for a in self.lista_aeropuertos]
                )
                messagebox.showinfo("Schengen manual", f"{code} marcado manualmente como Schengen.")
                return

        messagebox.showerror("No encontrado", f"No se encontró el aeropuerto {code}.")

    def f_delete_dynamic(self):
        code_to_del = self.delete_entry.get().strip().upper()
        if not code_to_del:
            messagebox.showwarning("Campo Vacío", "Introduce un código ICAO.")
            return
        res = remove_airport(self.lista_aeropuertos, code_to_del)
        if res == 1:
            messagebox.showinfo("Borrado", f"Aeropuerto {code_to_del} eliminado de la memoria.")
            self.delete_entry.delete(0, tk.END)
            self.update_status()
        else:
            messagebox.showerror("Error", f"No se encontró el aeropuerto {code_to_del}.")

    def f_add_dynamic(self):
        code = self.add_code_entry.get().strip().upper()
        lat_text = self.add_lat_entry.get().strip()
        lon_text = self.add_lon_entry.get().strip()

        if len(code) != 4:
            messagebox.showwarning("Código no válido", "Introduce un código ICAO de 4 letras.")
            return

        try:
            lat = float(lat_text)
            lon = float(lon_text)
        except ValueError:
            messagebox.showwarning("Coordenadas no válidas", "Introduce latitud y longitud en formato decimal.")
            return

        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            messagebox.showwarning("Coordenadas fuera de rango", "Latitud debe estar entre -90 y 90; longitud entre -180 y 180.")
            return

        i = 0
        while i < len(self.lista_aeropuertos):
            if self.lista_aeropuertos[i].code == code:
                messagebox.showerror("Duplicado", f"El aeropuerto {code} ya existe en la memoria.")
                return
            i += 1

        nuevo = Airport(code, lat, lon)
        set_schengen(nuevo)
        add_airport(self.lista_aeropuertos, nuevo)

        self.add_code_entry.delete(0, tk.END)
        self.add_lat_entry.delete(0, tk.END)
        self.add_lon_entry.delete(0, tk.END)
        self.update_status()
        messagebox.showinfo("Añadido", f"Aeropuerto {code} añadido correctamente.")

    def f_load_arrivals(self):
        """Cargar Archivo Operaciones/Llegadas con validación estricta."""
        path = filedialog.askopenfilename(title="Seleccionar llegadas", filetypes=[("Text files", "*.txt")])
        if path:
            try:
                # VALIDACIÓN DE CABECERA
                with open(path, "r", encoding="utf-8", errors="ignore") as f_check:
                    cabecera = f_check.readline().strip().upper()
                if "ARRIVAL" not in cabecera or "ORIGIN" not in cabecera or "AIRCRAFT" not in cabecera:
                    messagebox.showerror("Error de Fichero",
                                         "El archivo seleccionado no es un fichero de Llegadas/Operaciones válido.\nCabecera esperada: AIRCRAFT ORIGIN ARRIVAL AIRLINE")
                    return

                self.lista_vuelos = load_arrivals(path)
                messagebox.showinfo("Carga exitosa", f"Se han cargado {len(self.lista_vuelos)} llegadas de aeronaves.")
                self.update_status()
                self.mark_file_button_loaded(self.btn_load_arrivals_file)
                self.show_loaded_table(
                    "Llegadas cargadas",
                    ("Aircraft", "Origen", "Llegada", "Aerolínea"),
                    [(v.codigo, v.origin, v.time, v.company) for v in self.lista_vuelos]
                )
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer el archivo: {e}")

    def f_plot_arrivals_embedded(self):
        if not self.lista_vuelos:
            messagebox.showerror("Error", "No hay operaciones cargadas.")
            return
        self.clear_plot_frame()
        horas = [0] * 24
        i = 0
        while i < len(self.lista_vuelos):
            try:
                h = int(self.lista_vuelos[i].time.split(":")[0])
                if 0 <= h < 24: horas[h] += 1
            except:
                pass
            i += 1

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(range(24), horas, color="#3498db", edgecolor="#2980b9")
        ax.set_title("Frecuencia Horaria de Operaciones")
        ax.set_xlabel("Hora del Día")
        ax.set_ylabel("Vuelos")
        ax.set_xticks(range(24))

        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)



    def f_ui_plot_airlines_selected(self):
        """
        [ORGANIZACIÓN]: Gráfico estadístico de volumen de operación por operador.
        [AMIGABLE]: Integra un gráfico de BARRAS VERTICALES en el panel derecho sin ventanas.
        Permite escoger entre Top 10 o todas las aerolíneas cargadas.
        """
        # [ROBUSTEZ]: Validación previa para evitar fallos si no hay datos cargados
        if not hasattr(self, 'lista_vuelos') or not self.lista_vuelos:
            messagebox.showwarning("Análisis Estadístico",
                                   "No hay vuelos cargados en memoria. Por favor, cargue un fichero de llegadas primero.")
            return

        modo_grafico = self.ask_airline_chart_mode()
        if modo_grafico is None:
            return
        ver_top10 = modo_grafico == "top10"

        # 1. Limpiar por completo el panel derecho antes de dibujar
        self.clear_plot_frame()

        # 2. Conteo del total de vuelos por cada aerolínea
        conteo_aerolineas = {}
        for avion in self.lista_vuelos:
            # Soporta tanto objetos Aircraft como diccionarios unidos
            if isinstance(avion, dict):
                cia = avion.get('company', avion.get('airline', 'UNKNOWN'))
            else:
                cia = getattr(avion, 'company', 'UNKNOWN')
            cia = str(cia).upper().strip()
            conteo_aerolineas[cia] = conteo_aerolineas.get(cia, 0) + 1

        # Ordenar de mayor a menor volumen operativo para que la barra más alta quede a la izquierda
        aerolineas_ordenadas = sorted(conteo_aerolineas.items(), key=lambda x: x[1], reverse=True)
        if ver_top10:
            top_10 = aerolineas_ordenadas[:10]
            otras = aerolineas_ordenadas[10:]
            suma_otras = sum(item[1] for item in otras)
            aerolineas_ordenadas = top_10
            if suma_otras > 0:
                aerolineas_ordenadas.append(("OTROS", suma_otras))

        labels = [item[0] for item in aerolineas_ordenadas]
        sizes = [item[1] for item in aerolineas_ordenadas]

        if not ver_top10:
            self.show_airlines_fullscreen(labels, sizes)
            return

        # 4. GENERACIÓN DEL GRÁFICO DE BARRAS VERTICALES (Matplotlib incrustado)
        fig_width = 7 if ver_top10 else max(9, len(labels) * 0.35)
        fig, ax = plt.subplots(figsize=(fig_width, 5), dpi=100)

        # Dibujamos las columnas verticales con los ejes intercambiados
        barras = ax.bar(labels, sizes, color="#3498db", edgecolor="#2980b9", width=0.6)

        # Añadir el número exacto de vuelos encima de cada barra vertical
        for barra in barras:
            alto_barra = barra.get_height()
            ax.text(barra.get_x() + barra.get_width() / 2, alto_barra + 1,
                    f'{int(alto_barra)}',
                    va='bottom', ha='center', fontsize=9, fontweight='bold', color="#2c3e50")

        # Configuración estética de los nuevos ejes
        titulo = "TOP 10 AEROLÍNEAS" if ver_top10 else "TODAS LAS AEROLÍNEAS"
        ax.set_title(titulo, fontsize=11, fontweight='bold', pad=15)
        ax.set_xlabel("Aerolíneas", fontsize=10, fontweight='bold')
        ax.set_ylabel("Cantidad de Vuelos", fontsize=10, fontweight='bold')

        # Rotamos las etiquetas del eje X para evitar solapamientos cuando se muestran todas
        plt.xticks(rotation=35 if not ver_top10 else 15, ha='right')

        # Ajustar los márgenes para que no se corte ningún texto
        plt.tight_layout()
        ax.grid(True, axis='y', linestyle=':', alpha=0.6)

        # 5. INCRUSTACIÓN DIRECTA EN EL ENTORNO GRÁFICO TKINTER
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Cierre explícito de la figura para proteger la memoria del sistema
        plt.close(fig)


    def ask_airline_chart_mode(self):
        """Muestra una ventana con botones propios para escoger el tipo de gráfico."""
        seleccion = {"modo": None}
        dialog = tk.Toplevel(self.root)
        dialog.title("Gráfico de aerolíneas")
        dialog.configure(bg="#f4f6f7")
        self.center_window(dialog, 360, 170)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="Selecciona cómo quieres ver las aerolíneas",
            bg="#f4f6f7",
            fg="#2c3e50",
            font=("Segoe UI", 11, "bold")
        ).pack(pady=(18, 12))

        botones = tk.Frame(dialog, bg="#f4f6f7")
        botones.pack(pady=8)

        def elegir(modo):
            seleccion["modo"] = modo
            dialog.destroy()

        ttk.Button(botones, text="Top 10 + OTROS", width=18, command=lambda: elegir("top10")).pack(side="left", padx=6)
        ttk.Button(botones, text="Todas", width=14, command=lambda: elegir("todas")).pack(side="left", padx=6)
        ttk.Button(dialog, text="Cancelar", width=12, command=dialog.destroy).pack(pady=(8, 0))

        dialog.wait_window()
        return seleccion["modo"]


    def show_airlines_fullscreen(self, labels, sizes):
        """Muestra todas las aerolíneas con barras verticales y desplazamiento horizontal."""
        ventana = tk.Toplevel(self.root)
        ventana.title("Todas las aerolíneas")
        ventana.configure(bg="white")
        try:
            ventana.state("zoomed")
        except tk.TclError:
            ventana.geometry("1200x750")

        top_bar = tk.Frame(ventana, bg="white")
        top_bar.pack(fill="x", padx=12, pady=(10, 0))
        tk.Label(
            top_bar,
            text="TODAS LAS AEROLÍNEAS",
            font=("Segoe UI", 13, "bold"),
            bg="white",
            fg="#355C8A"
        ).pack(side="left")
        ttk.Button(top_bar, text="Cerrar", width=10, command=ventana.destroy).pack(side="right")

        grafico_frame = tk.Frame(ventana, bg="white")
        grafico_frame.pack(fill="both", expand=True, padx=12, pady=10)

        scroll_canvas = tk.Canvas(grafico_frame, bg="white", highlightthickness=0)
        scroll_x = ttk.Scrollbar(grafico_frame, orient="horizontal", command=scroll_canvas.xview)
        scroll_canvas.configure(xscrollcommand=scroll_x.set)
        scroll_x.pack(side="bottom", fill="x")
        scroll_canvas.pack(side="left", fill="both", expand=True)

        inner_frame = tk.Frame(scroll_canvas, bg="white")
        window_id = scroll_canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        def ajustar_scroll(event):
            scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))

        inner_frame.bind("<Configure>", ajustar_scroll)

        datos = list(zip(labels, sizes))
        datos.sort(key=lambda x: x[1], reverse=True)
        labels_ordenadas = [item[0] for item in datos]
        sizes_ordenadas = [item[1] for item in datos]

        fig_width = max(14, len(labels_ordenadas) * 0.24)
        fig, ax = plt.subplots(figsize=(fig_width, 6.5), dpi=100)
        barras = ax.bar(labels_ordenadas, sizes_ordenadas, color="#1f77b4", edgecolor="#1f77b4", width=0.72)

        for barra in barras:
            alto = barra.get_height()
            if alto > 0:
                ax.text(barra.get_x() + barra.get_width() / 2, alto + 0.5,
                        f"{int(alto)}", va="bottom", ha="center", fontsize=7, color="#2c3e50")

        ax.set_title("Llegadas por aerolínea (todas)", fontsize=12)
        ax.set_xlabel("Aerolínea", fontsize=10)
        ax.set_ylabel("Número de vuelos", fontsize=10)
        ax.grid(True, axis="y", linestyle="--", alpha=0.35)
        ax.tick_params(axis="x", labelrotation=90, labelsize=8)
        fig.subplots_adjust(left=0.05, right=0.995, top=0.92, bottom=0.22)

        canvas = FigureCanvasTkAgg(fig, master=inner_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)


    def f_plot_type_embedded(self):
        """
        [ORGANIZACIÓN]: Gráfico estadístico de volumen de operaciones por aeropuerto de origen.
        [AMIGABLE]: Integra un gráfico de BARRAS VERTICALES en el panel derecho sin ventanas flotantes.
        Agrupa los aeropuertos con pocos vuelos bajo la categoría 'OTROS' para optimizar el eje X.
        """
        # [ROBUSTEZ]: Validación previa para evitar fallos si no hay datos cargados en memoria
        if not hasattr(self, 'lista_vuelos') or not self.lista_vuelos:
            messagebox.showwarning("Análisis Estadístico",
                                   "No hay vuelos cargados en memoria. Por favor, cargue un fichero de llegadas primero.")
            return

        # 1. Limpiar por completo el panel derecho antes de dibujar para evitar solapamientos
        self.clear_plot_frame()

        # 2. Conteo del total de vuelos provenientes de cada aeropuerto de origen
        conteo_origenes = {}
        for avion in self.lista_vuelos:
            # Soporta tanto si la lista contiene objetos Aircraft como diccionarios
            origen = getattr(avion, 'origin', None) or avion.get('origin', 'UNKNOWN')
            origen = str(origen).upper().strip()
            conteo_origenes[origen] = conteo_origenes.get(origen, 0) + 1

        # 3. LÓGICA DE AGRUPACIÓN INTELIGENTE (Compactación del eje X)
        # Umbral: Aeropuertos de origen con menos de 5 vuelos se agrupan en "OTROS"
        UMBRAL_VUELOS = 5
        origenes_filtrados = {}
        otros_vuelos = 0

        for origen, total in conteo_origenes.items():
            if total < UMBRAL_VUELOS:
                otros_vuelos += total
            else:
                origenes_filtrados[origen] = total

        # Si se acumularon vuelos de aeropuertos minoritarios, añadimos la categoría compactada
        if otros_vuelos > 0:
            origenes_filtrados["OTROS"] = otros_vuelos

        # Ordenar de mayor a menor volumen operativo (la barra más alta a la izquierda)
        origenes_ordenadas = sorted(origenes_filtrados.items(), key=lambda x: x[1], reverse=True)
        labels = [item[0] for item in origenes_ordenadas]
        sizes = [item[1] for item in origenes_ordenadas]

        # 4. GENERACIÓN DEL GRÁFICO DE BARRAS VERTICALES (Matplotlib incrustado)
        fig, ax = plt.subplots(figsize=(6, 5), dpi=100)

        # Dibujamos las columnas verticales (Eje X: Aeropuertos, Eje Y: Cantidad de vuelos)
        barras = ax.bar(labels, sizes, color="#3498db", edgecolor="#2980b9", width=0.6)

        # Añadir el número exacto de vuelos encima de cada columna vertical
        for barra in barras:
            alto_barra = barra.get_height()
            ax.text(barra.get_x() + barra.get_width() / 2, alto_barra + 0.5,
                    f'{int(alto_barra)}',
                    va='bottom', ha='center', fontsize=9, fontweight='bold', color="#2c3e50")

        # Configuración estética y de formato del gráfico
        ax.set_title("VOLUMEN DE VUELOS POR AEROPUERTO DE ORIGEN", fontsize=11, fontweight='bold', pad=15)
        ax.set_xlabel("Aeropuertos de Origen", fontsize=10, fontweight='bold')
        ax.set_ylabel("Cantidad de Vuelos Recibidos", fontsize=10, fontweight='bold')

        # Rotamos las etiquetas del eje X (códigos ICAO) para que se lean perfectamente
        plt.xticks(rotation=30, ha='right')

        # Ajustar los márgenes automáticamente para prevenir recortes de texto
        plt.tight_layout()
        ax.grid(True, axis='y', linestyle=':', alpha=0.6)

        # 5. INCRUSTACIÓN DIRECTA EN EL PANEL BLANCO DE TKINTER
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Cierre de la figura para proteger la memoria RAM
        plt.close(fig)


    def f_save_flights(self):
        if not self.lista_vuelos:
            messagebox.showerror("Error", "No hay registros de vuelos para guardar.")
            return
        path = filedialog.asksaveasfilename(title="Guardar vuelos...", defaultextension=".txt",
                                            filetypes=[("Text files", "*.txt")])
        if path:
            try:
                f = open(path, "w", encoding="utf-8")
                f.write("AIRCRAFT ORIGIN ARRIVAL AIRLINE\n")
                i = 0
                while i < len(self.lista_vuelos):
                    v = self.lista_vuelos[i]
                    f.write(f"{v.codigo} {v.origin} {v.time} {v.company}\n")
                    i += 1
                f.close()
                messagebox.showinfo("Éxito", "Fichero guardado correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo salvar el log: {e}")

    def f_map_flights(self):
        if not self.lista_vuelos or not self.lista_aeropuertos:
            messagebox.showerror("Error", "Carga vuelos y aeropuertos simultáneamente.")
            return
        self.write_flights_kml("flights_map.kml")
        if self.open_kml_in_google_earth("flights_map.kml"):
            self.show_loaded_table(
                "KML generado para Google Earth",
                ("Archivo", "Contenido", "Estado"),
                [("flights_map.kml", "Trayectorias hacia LEBL", "Abierto con la aplicación asociada")]
            )

    def f_long_flights(self):
        if not self.lista_vuelos or not self.lista_aeropuertos:
            messagebox.showerror("Error", "Faltan datos operacionales esenciales para el cálculo.")
            return
        largos = long_distance_arrivals(self.lista_vuelos, self.lista_aeropuertos)
        if largos:
            abrir_google_earth = messagebox.askyesno(
                "Vuelos de larga distancia",
                f"Detectados {len(largos)} vuelos de larga distancia (>2000 km).\n\n"
                "¿Quieres verlos en Google Earth?\n\nSí = Google Earth\nNo = Lista en el panel"
            )

            if abrir_google_earth:
                self.write_flights_kml("long_distance_flights.kml", largos)
                if self.open_kml_in_google_earth("long_distance_flights.kml"):
                    self.show_loaded_table(
                        "KML de larga distancia generado",
                        ("Archivo", "Vuelos", "Estado"),
                        [("long_distance_flights.kml", len(largos), "Abierto con la aplicación asociada")]
                    )
            else:
                self.show_loaded_table(
                    "Vuelos de larga distancia (>2000 km)",
                    ("Aircraft", "Origen", "Llegada", "Aerolínea"),
                    [(v.codigo, v.origin, v.time, v.company) for v in largos]
                )
        else:
            messagebox.showinfo("Info", "Ninguna operación supera el umbral de los 2000 km.")

    def f_ui_load_airport_structure(self):
        """Cargar Estructura Aeropuerto (Terminals) con validación estricta."""
        path = filedialog.askopenfilename(title="Seleccionar estructura LEBL", filetypes=[("Text files", "*.txt")])
        if path:
            try:
                # VALIDACIÓN DE CABECERA
                with open(path, "r", encoding="utf-8", errors="ignore") as f_check:
                    cabecera = f_check.readline().strip().upper()
                if "TERMINALS" not in cabecera and "TERMINAL" not in cabecera:
                    messagebox.showerror("Error de Fichero",
                                         "El archivo no contiene una estructura jerárquica de aeropuerto válida.\nDebe indicar el código del aeropuerto seguido de 'terminals'.")
                    return

                res = LEBL.load_airport_structure(path)
                if res:
                    self.bcn_airport = res
                    messagebox.showinfo("Función 3",
                                        f"Estructura del aeropuerto {self.bcn_airport.code} procesada correctamente.")
                    self.update_status()
                    self.mark_file_button_loaded(self.btn_load_structure_file)
                    rows = []
                    for terminal in self.bcn_airport.terminals:
                        for area in terminal.boarding_areas:
                            rows.append((terminal.name, area.name, area.type, len(area.gates)))
                    self.show_loaded_table(
                        "Estructura LEBL cargada",
                        ("Terminal", "Área", "Tipo", "Puertas"),
                        rows
                    )
                else:
                    messagebox.showerror("Error", "Error al procesar la estructura.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer el archivo: {e}")

    def f_ui_gate_occupancy(self):
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

    def f_ui_gate_usage_diagram(self, highlight_aircraft=None):
        """Dibuja un esquema visual de las puertas utilizadas por terminal y área."""
        if not self.bcn_airport:
            messagebox.showerror("Error", "Carga primero la estructura del aeropuerto.")
            return

        # Construir lista de terminales disponibles
        nombres_terminales = [t.name for t in self.bcn_airport.terminals]

        if len(nombres_terminales) == 0:
            messagebox.showerror("Error", "No hay terminales cargadas.")
            return

        # Preguntar al usuario qué terminal quiere ver
        seleccion = {"terminal": None}

        dialog = tk.Toplevel(self.root)
        dialog.title("Seleccionar Terminal")
        dialog.configure(bg="#f4f6f7")
        self.center_window(dialog, 360, 180)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="¿Qué terminal quieres visualizar?",
            bg="#f4f6f7",
            fg="#2c3e50",
            font=("Segoe UI", 12, "bold")
        ).pack(pady=(20, 15))

        botones_frame = tk.Frame(dialog, bg="#f4f6f7")
        botones_frame.pack(pady=5)

        def elegir(nombre):
            seleccion["terminal"] = nombre
            dialog.destroy()

        for nombre in nombres_terminales:
            tk.Button(
                botones_frame,
                text=f"TERMINAL {nombre}",
                width=16,
                bg="#3498db",
                fg="white",
                activebackground="#2980b9",
                activeforeground="white",
                font=("Segoe UI", 11, "bold"),
                relief="flat",
                cursor="hand2",
                command=lambda n=nombre: elegir(n)
            ).pack(side="left", padx=10)

        ttk.Button(dialog, text="Cancelar", width=12, command=dialog.destroy).pack(pady=(12, 0))

        dialog.wait_window()

        if seleccion["terminal"] is None:
            return

        # Buscar la terminal seleccionada
        terminal_elegida = None
        for t in self.bcn_airport.terminals:
            if t.name == seleccion["terminal"]:
                terminal_elegida = t
                break

        if terminal_elegida is None:
            return

        self.clear_plot_frame()
        self._diagram_stats = {"hay_ocupadas": False, "encontrado_highlight": False}
        self._render_single_terminal(self.plot_frame, terminal_elegida, highlight_aircraft)

        if not self._diagram_stats["hay_ocupadas"]:
            messagebox.showinfo("Gates utilizadas",
                                "No hay gates ocupadas todavía. Asigna puertas para verlas marcadas.")
        if highlight_aircraft and not self._diagram_stats["encontrado_highlight"]:
            messagebox.showwarning("Gate no encontrada",
                                   f"No se ha encontrado ninguna gate ocupada por el vuelo {highlight_aircraft}.")

    def _render_single_terminal(self, master_frame, terminal, highlight_aircraft):
        """Renderiza una única terminal dentro del contenedor de destino indicado."""
        from matplotlib.patches import Rectangle, Patch

        areas = terminal.boarding_areas

        # Calcular altura dinámica según el área con más puertas
        max_gates = max((len(a.gates) for a in areas), default=10)
        cols_max = 2 if max_gates > 11 else 1
        filas_max = math.ceil(max_gates / cols_max)
        top_y = max(12.0, filas_max * 0.50 + 4.0)
        fig_h = max(7.0, filas_max * 0.38 + 4.0)

        fig, ax = plt.subplots(figsize=(15, fig_h), dpi=100)
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")
        ax.axis("off")

        # --- TÍTULO GRANDE CON EL NOMBRE DE LA TERMINAL ---
        ax.text(
            0.5, 0.97,
            f"TERMINAL {terminal.name}",
            transform=ax.transAxes,
            ha="center", va="top",
            fontsize=26, fontweight="bold",
            color="#185a7a"
        )

        # Subtítulo con detalle
        subtitulo = "Gate Occupancy"
        if highlight_aircraft:
            subtitulo += f"  —  Vuelo resaltado: {highlight_aircraft}"
        ax.set_title(subtitulo, loc="left", fontsize=13, color="#555555", pad=8)

        if not areas:
            ax.text(0.5, 0.5, f"No hay áreas cargadas en Terminal {terminal.name}",
                    ha="center", va="center", fontsize=14)
            canvas = FigureCanvasTkAgg(fig, master=master_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            plt.close(fig)
            return

        # --- Parámetros de espaciado ---
        area_width = 5.5
        cell_w = 0.75
        cell_h = 0.42
        col_gap = 0.40
        row_gap = 0.18

        num_areas = len(areas)
        ax.set_xlim(-1, num_areas * area_width + 1)
        ax.set_ylim(0, top_y + 2.5)

        # Viga horizontal superior
        ax.plot(
            [0.2, num_areas * area_width - 1.0],
            [top_y, top_y],
            color="#185a7a", linewidth=16, solid_capstyle="butt", zorder=1
        )

        for area_idx, area in enumerate(areas):
            cx = 1.2 + area_idx * area_width

            num_gates = len(area.gates)
            min_y = 2.5 if num_gates > 12 else 5.0

            # Finger vertical
            ax.plot(
                [cx, cx], [min_y, top_y],
                color="#185a7a", linewidth=16, solid_capstyle="butt", zorder=1
            )

            # Etiqueta del área
            ax.text(cx, min_y - 0.7, f"{terminal.name}{area.name}",
                    ha="center", va="center", fontsize=13, fontweight="bold", color="black")

            cols = 2 if num_gates > 11 else 1
            block_w = cols * cell_w + (cols - 1) * col_gap
            start_x = cx - block_w / 2
            start_y = top_y - 0.8

            for gate_idx, gate in enumerate(area.gates):
                col = gate_idx % cols
                row = gate_idx // cols

                rx = start_x + col * (cell_w + col_gap)
                ry = start_y - row * (cell_h + row_gap)

                if ry < min_y:
                    break

                if highlight_aircraft and gate.aircraft_id == highlight_aircraft:
                    facecolor = "#ffd700"
                    edgecolor = "black"
                    text_color = "black"
                    self._diagram_stats["encontrado_highlight"] = True
                elif gate.occupied:
                    facecolor = "#d62728"
                    edgecolor = "#b21f1f"
                    text_color = "white"
                    self._diagram_stats["hay_ocupadas"] = True
                else:
                    facecolor = "#2ca02c"
                    edgecolor = "#217c21"
                    text_color = "white"

                ax.add_patch(Rectangle(
                    (rx, ry), cell_w, cell_h,
                    facecolor=facecolor, edgecolor=edgecolor,
                    linewidth=1.0, zorder=3
                ))

                ax.text(rx + cell_w / 2, ry + cell_h / 2,
                        f"G{gate_idx + 1}",
                        ha="center", va="center",
                        fontsize=8, fontweight="bold",
                        color=text_color, zorder=4)

                if highlight_aircraft and gate.aircraft_id == highlight_aircraft:
                    ax.text(rx + cell_w / 2, ry + cell_h + 0.15,
                            gate.name,
                            ha="center", va="bottom",
                            fontsize=9, fontweight="bold", color="black")

        # Leyenda
        legend_elements = [
            Patch(facecolor="#2ca02c", edgecolor="#217c21", label="Disponible (Libre)"),
            Patch(facecolor="#d62728", edgecolor="#b21f1f", label="Ocupada"),
        ]
        if highlight_aircraft:
            legend_elements.append(
                Patch(facecolor="#ffd700", edgecolor="black", label=f"Vuelo {highlight_aircraft}")
            )
        ax.legend(handles=legend_elements, loc="upper right", fontsize=11, frameon=True, facecolor="white")

        # Botón para cambiar de terminal integrado debajo del gráfico
        boton_frame = tk.Frame(master_frame, bg="white")
        boton_frame.pack(fill="x", padx=15, pady=(0, 10))

        otras_terminales = [t for t in self.bcn_airport.terminals if t.name != terminal.name]
        for otra in otras_terminales:
            tk.Button(
                boton_frame,
                text=f"Ver Terminal {otra.name}",
                bg="#185a7a",
                fg="white",
                activebackground="#0f3d54",
                activeforeground="white",
                font=("Segoe UI", 10, "bold"),
                relief="flat",
                cursor="hand2",
                command=lambda t=otra: (
                    self.clear_plot_frame(),
                    self.__dict__.update({"_diagram_stats": {"hay_ocupadas": False, "encontrado_highlight": False}}),
                    self._render_single_terminal(self.plot_frame, t, highlight_aircraft)
                )
            ).pack(side="left", padx=6, pady=4)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=master_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=15)
        plt.close(fig)

    def f_ui_locate_flight_gate(self):
        """Permite seleccionar un vuelo y resalta su gate asignada en el mapa de terminales."""
        if not self.bcn_airport:
            messagebox.showerror("Error", "Carga primero la estructura del aeropuerto.")
            return

        vuelos_asignados = []
        for terminal in self.bcn_airport.terminals:
            for area in terminal.boarding_areas:
                for gate in area.gates:
                    if gate.occupied and gate.aircraft_id:
                        vuelos_asignados.append(gate.aircraft_id)

        if not vuelos_asignados:
            messagebox.showwarning("Sin asignaciones", "Todavía no hay vuelos asignados a ninguna gate.")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Localizar gate de vuelo")
        dialog.configure(bg="#f4f6f7")
        self.center_window(dialog, 340, 150)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Selecciona el vuelo que quieres localizar:",
                 bg="#f4f6f7", font=("Segoe UI", 10, "bold")).pack(pady=(18, 8))
        combo = ttk.Combobox(dialog, values=sorted(vuelos_asignados), state="readonly", width=22)
        combo.pack(pady=4)
        combo.current(0)

        def localizar():
            codigo = combo.get()
            dialog.destroy()

            # Buscar automáticamente en qué terminal está el vuelo
            terminal_encontrada = None
            for terminal in self.bcn_airport.terminals:
                for area in terminal.boarding_areas:
                    for gate in area.gates:
                        if gate.aircraft_id == codigo:
                            terminal_encontrada = terminal
                            break
                    if terminal_encontrada:
                        break
                if terminal_encontrada:
                    break

            if not terminal_encontrada:
                messagebox.showwarning("No encontrado", f"No se encontró la gate del vuelo {codigo}.")
                return

            # Ir directamente a la terminal correcta sin preguntar
            self.clear_plot_frame()
            self._diagram_stats = {"hay_ocupadas": False, "encontrado_highlight": False}
            self._render_single_terminal(self.plot_frame, terminal_encontrada, codigo)

            if not self._diagram_stats["encontrado_highlight"]:
                messagebox.showwarning("Gate no encontrada",
                                       f"No se ha encontrado ninguna gate ocupada por el vuelo {codigo}.")

        ttk.Button(dialog, text="Marcar en mapa", command=localizar, width=18).pack(pady=10)
        dialog.wait_window()

        def localizar():
            codigo = combo.get()
            dialog.destroy()
            self.f_ui_gate_usage_diagram(highlight_aircraft=codigo)

        ttk.Button(dialog, text="Marcar en mapa", command=localizar, width=18).pack(pady=10)
        dialog.wait_window()

    def f_ui_load_airlines(self):
        """Cargar Aerolíneas por Terminal con validación estricta."""
        if not self.bcn_airport:
            messagebox.showerror("Error", "Primero carga la estructura con la Función 3.")
            return
        path = filedialog.askopenfilename(title="Seleccionar archivo de aerolíneas (T1_Airlines o T2_Airlines)",
                                          filetypes=[("Text files", "*.txt")])
        if not path: return

        try:
            # VALIDACIÓN DE CONTENIDO / FORMATO INTERNO
            with open(path, "r", encoding="utf-8", errors="ignore") as f_check:
                lineas = f_check.readlines()
            if not lineas or len(lineas[0].split('\t')) < 2 and len(lineas[0].split()) < 2:
                messagebox.showerror("Error de Fichero",
                                     "El archivo de aerolíneas no tiene el formato correcto (Nombre_Aerolínea [TAB/Espacio] Código_ICAO).")
                return

            t_select = None
            if "T1" in path or "t1" in path:
                t_select = "T1"
            elif "T2" in path or "t2" in path:
                t_select = "T2"
            else:
                messagebox.showwarning("Archivo no reconocido",
                                       "El nombre del archivo debe contener explícitamente 'T1' o 'T2' para vincularlo a su terminal.")
                return

            target_terminal = None
            for t in self.bcn_airport.terminals:
                if t.name == t_select: target_terminal = t

            if not target_terminal:
                messagebox.showerror("Error", f"La terminal {t_select} no existe en la estructura.")
                return

            nombre_esperado = f"{t_select}_Airlines.txt"
            with open(path, "r", encoding="utf-8", errors="ignore") as f_origen:
                contenido = f_origen.read()
            with open(nombre_esperado, "w", encoding="utf-8") as f_destino:
                f_destino.write(contenido)

            res = LEBL.load_airlines(target_terminal, t_select)
            if res:
                self.airlines_loaded_terminals.add(t_select)
                if "T1" in self.airlines_loaded_terminals and "T2" in self.airlines_loaded_terminals:
                    self.mark_file_button_loaded(self.btn_load_airlines_file)

                rows = []
                for terminal in self.bcn_airport.terminals:
                    if terminal.name in self.airlines_loaded_terminals:
                        for code in terminal.airline_icao_codes:
                            rows.append((terminal.name, code))

                titulo = "Aerolíneas cargadas"
                if "T1" in self.airlines_loaded_terminals and "T2" in self.airlines_loaded_terminals:
                    titulo = "Aerolíneas cargadas en T1 y T2"
                elif len(self.airlines_loaded_terminals) == 1:
                    titulo = f"Aerolíneas cargadas en {t_select}"

                self.show_loaded_table(
                    titulo,
                    ("Terminal", "Código ICAO"),
                    rows
                )
                messagebox.showinfo("Función 2", f"¡Éxito! Cargada la {t_select}.\nArchivo: {path}")
            else:
                messagebox.showerror("Error", f"El método devolvió False al procesar la {t_select}.")
        except Exception as error:
            messagebox.showerror("Error de Ejecución", f"Detalle:\n{str(error)}")

    def f_ui_set_gates(self):
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
                    if cont == idx_sel: target_area = ar
                    cont += 1

            if target_area:
                resultado = LEBL.set_gates(target_area, ini, fin, pref)
                if resultado == -1:
                    messagebox.showerror("Error", "El rango final debe ser estrictamente mayor que el inicial.")
                else:
                    messagebox.showinfo("Función 1",
                                        f"¡Éxito! El área ahora cuenta con {len(target_area.gates)} nuevas puertas.")
            else:
                messagebox.showerror("Error", "Área no localizada.")

        ttk.Button(work_panel, text="Aplicar set_gates()", command=aplicar_set_gates).grid(row=5, column=0,
                                                                                           columnspan=2, pady=15)

    def f_ui_is_airline_in_terminal(self):
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
                if t.name == t_name: target_terminal = t

            if target_terminal:
                pertenece = LEBL.is_airline_in_terminal(target_terminal, icao)
                if pertenece:
                    messagebox.showinfo("Resultado F5", f"SÍ. La aerolínea {icao} opera en la {t_name}.")
                else:
                    messagebox.showwarning("Resultado F5", f"NO. La aerolínea {icao} NO tiene asignada la {t_name}.")
            else:
                messagebox.showerror("Error", "Terminal no válida.")

        ttk.Button(work_panel, text="Comprobar via is_airline_in_terminal()", command=comprobar).grid(row=3, column=0,
                                                                                                      columnspan=2,
                                                                                                      pady=15)

    def f_ui_search_terminal(self):
        if not self.bcn_airport:
            messagebox.showerror("Error", "Carga primero la estructura con la Función 3.")
            return
        self.clear_plot_frame()
        work_panel = tk.Frame(self.plot_frame, bg="white")
        work_panel.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(work_panel, text="Búsqueda de Terminal por Aerolínea", font=("Segoe UI", 11, "bold"), bg="white").grid(
            row=0, column=0, columnspan=2, pady=10)
        tk.Label(work_panel, text="Código ICAO de la Aerolínea (ej. VLG):", bg="white").grid(row=1, column=0,
                                                                                             sticky="w", pady=5)

        entry_airline = ttk.Entry(work_panel, width=15, font=("Segoe UI", 10, "bold"))
        entry_airline.grid(row=1, column=1, sticky="w", pady=5)
        entry_airline.focus()

        def buscar():
            airline_name = entry_airline.get().strip().upper()
            if not airline_name:
                messagebox.showwarning("Campo Vacío", "Por favor, introduce el código de una aerolínea.")
                return
            terminal_asignada = LEBL.SearchTerminal(self.bcn_airport, airline_name)
            if terminal_asignada != "" and terminal_asignada != "Error":
                messagebox.showinfo("Búsqueda Exitosa",
                                    f"La aerolínea {airline_name} opera en la terminal: {terminal_asignada}")
            else:
                messagebox.showwarning("No Encontrada",
                                       f"La aerolínea {airline_name} no opera en ninguna terminal registrada.")

        ttk.Button(work_panel, text="Buscar Terminal", command=buscar).grid(row=2, column=0, columnspan=2, pady=15)

    def f_ui_assign_gate(self):
        if not self.bcn_airport:
            messagebox.showerror("Error", "Primero debes cargar la estructura del aeropuerto (Cargar Estructura).")
            return
        if not self.lista_vuelos:
            messagebox.showerror("Error", "No hay vuelos cargados. Por favor, carga el archivo de operaciones.")
            return

        self.clear_plot_frame()
        vuelos_id = [v.codigo for v in self.lista_vuelos]

        work_panel = tk.Frame(self.plot_frame, bg="white")
        work_panel.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(work_panel, text="Asignación individual de puerta", font=("Segoe UI", 11, "bold"),
                 bg="white").grid(row=0, column=0, columnspan=2, pady=10)
        tk.Label(work_panel, text="Selecciona Código de Avión:", bg="white").grid(row=1, column=0, sticky="w", pady=5)

        combo_vuelos = ttk.Combobox(work_panel, values=vuelos_id, state="readonly", width=20)
        combo_vuelos.grid(row=1, column=1, sticky="w", pady=5)
        combo_vuelos.current(0)

        def ejecutar_asignacion():
            idx = combo_vuelos.current()
            vuelo_seleccionado = self.lista_vuelos[idx]

            puerta_obtenida = LEBL.AssignGate(self.bcn_airport, vuelo_seleccionado)
            if puerta_obtenida == -1:
                messagebox.showerror("Error", "La aerolínea del vuelo no está registrada en ninguna terminal.")
            elif puerta_obtenida == -2:
                messagebox.showwarning("Saturación", "No quedan puertas libres en la zona adecuada para este vuelo.")
            else:
                messagebox.showinfo("Éxito",
                                    f"Vuelo {vuelo_seleccionado.codigo} asignado con éxito a la puerta: {puerta_obtenida}")
                self.f_ui_gate_occupancy()

        ttk.Button(work_panel, text="Asignar Puerta Automática", command=ejecutar_asignacion).grid(row=2, column=0,
                                                                                                   columnspan=2,
                                                                                                   pady=(15, 8))

        tk.Label(work_panel, text="Puerta manual concreta:", bg="white").grid(row=3, column=0, sticky="w", pady=5)
        entry_gate_manual = ttk.Entry(work_panel, width=20)
        entry_gate_manual.grid(row=3, column=1, sticky="w", pady=5)

        def ejecutar_asignacion_manual():
            idx = combo_vuelos.current()
            vuelo_seleccionado = self.lista_vuelos[idx]
            gate_name = entry_gate_manual.get().strip()
            if not gate_name:
                messagebox.showwarning("Campo vacío", "Introduce el nombre exacto de la puerta.")
                return

            terminal_vuelo = LEBL.SearchTerminal(self.bcn_airport, vuelo_seleccionado.company)
            if not terminal_vuelo:
                messagebox.showerror("Error", "La aerolínea del vuelo no está registrada en ninguna terminal.")
                return

            tipo_vuelo = "schengen" if is_schengen_airport(vuelo_seleccionado.origin) else "non-schengen"
            puerta_encontrada = None
            area_encontrada = None
            terminal_encontrada = None

            for terminal in self.bcn_airport.terminals:
                for area in terminal.boarding_areas:
                    for gate in area.gates:
                        if gate.name.upper() == gate_name.upper():
                            puerta_encontrada = gate
                            area_encontrada = area
                            terminal_encontrada = terminal

            if not puerta_encontrada:
                messagebox.showerror("Puerta no encontrada", f"No existe la puerta {gate_name}.")
                return
            if terminal_encontrada.name != terminal_vuelo:
                messagebox.showerror("Terminal incorrecta", f"La aerolínea opera en {terminal_vuelo}, no en {terminal_encontrada.name}.")
                return
            if area_encontrada.type.lower() != tipo_vuelo:
                messagebox.showerror("Zona incorrecta", f"El vuelo requiere zona {tipo_vuelo}, pero la puerta está en zona {area_encontrada.type}.")
                return
            if puerta_encontrada.occupied:
                messagebox.showwarning("Puerta ocupada", f"La puerta {puerta_encontrada.name} ya está ocupada.")
                return

            puerta_encontrada.occupied = True
            puerta_encontrada.aircraft_id = vuelo_seleccionado.codigo
            messagebox.showinfo("Asignación manual", f"Vuelo {vuelo_seleccionado.codigo} asignado manualmente a {puerta_encontrada.name}.")
            self.f_ui_gate_occupancy()

        ttk.Button(work_panel, text="Asignar Puerta Manual", command=ejecutar_asignacion_manual).grid(row=4, column=0,
                                                                                                      columnspan=2,
                                                                                                      pady=8)

    # =====================================================================================
    # SECCIÓN 5: CAPA DE INTERFAZ PARA LA NUEVA FASE 4 (SALIDAS Y MERGE CON VALIDACIONES)
    # =====================================================================================
    def f_ui_load_departures(self):
        """Cargar Archivo Salidas con validación estricta de cabecera."""
        path = filedialog.askopenfilename(title="Seleccionar fichero de Salidas (Departures)",
                                          filetypes=[("Text files", "*.txt")])
        if not path: return

        try:
            # VALIDACIÓN DE CABECERA
            with open(path, "r", encoding="utf-8", errors="ignore") as f_check:
                cabecera = f_check.readline().strip().upper()
            if "DEPARTURE" not in cabecera or "DESTINATION" not in cabecera or "AIRCRAFT" not in cabecera:
                messagebox.showerror("Error de Fichero",
                                     "El archivo seleccionado no es un fichero de Salidas (Departures) válido.\nCabecera esperada: AIRCRAFT DESTINATION DEPARTURE AIRLINE")
                return

            self.lista_salidas, codigo = LoadDepartures(path)
            if codigo == -1:
                messagebox.showerror("Error Fase 4", "No se pudo procesar el archivo o ruta incorrecta.")
                return

            messagebox.showinfo("Fase 4", f"Se han cargado {len(self.lista_salidas)} salidas programadas con éxito.")
            self.update_status()
            self.mark_file_button_loaded(self.btn_load_departures_file)
            self.show_loaded_table(
                "Salidas cargadas",
                ("Aircraft", "Destino", "Salida", "Aerolínea"),
                [(dep.codigo, dep.destination, dep.departure_time, dep.company) for dep in self.lista_salidas]
            )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo: {e}")

    def f_ui_merge_movements(self):
        if not self.lista_vuelos:
            messagebox.showerror("Error", "Primero debes cargar los vuelos de llegada (Submenú 2).")
            return
        if not self.lista_salidas:
            messagebox.showerror("Error", "Primero debes cargar las salidas del día (Fase 4 - Botón 1).")
            return

        res = MergeMovements(self.lista_vuelos, self.lista_salidas)
        if res == -1:
            messagebox.showerror("Error", "Error crítico durante el cruzado de listas.")
            return

        self.lista_unificada = res
        messagebox.showinfo("Fase 4",
                            f"Fusión concluida. Generados {len(self.lista_unificada)} registros consolidados.")
        self.clear_plot_frame()

        table_frame = tk.Frame(self.plot_frame, bg="white")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")

        columnas = ("Avión", "Compañía", "Llegada", "Salida", "Destino")
        tabla = ttk.Treeview(table_frame, columns=columnas, show="headings", yscrollcommand=scrollbar.set)
        tabla.pack(fill="both", expand=True)
        scrollbar.config(command=tabla.yview)

        tabla.heading("Avión", text="Avión ID")
        tabla.heading("Compañía", text="Aerolínea")
        tabla.heading("Llegada", text="Hora Arr")
        tabla.heading("Salida", text="Hora Dep")
        tabla.heading("Destino", text="Destino")

        tabla.column("Avión", anchor="center", width=100)
        tabla.column("Compañía", anchor="center", width=100)
        tabla.column("Llegada", anchor="center", width=120)
        tabla.column("Salida", anchor="center", width=120)
        tabla.column("Destino", anchor="center", width=100)

        i = 0
        while i < len(self.lista_unificada):
            a = self.lista_unificada[i]
            arr_t = a.time if a.time else "No registra"
            dep_t = a.departure_time if a.departure_time else "No registra"
            dest = a.destination if a.destination else "-"
            tabla.insert("", "end", values=(a.codigo, a.company, arr_t, dep_t, dest))
            i += 1

    def f_ui_night_aircraft(self):
        if not self.lista_unificada:
            messagebox.showerror("Error", "Debes realizar la fusión (Merge) previamente.")
            return

        nocturnos = NightAircraft(self.lista_unificada)
        if nocturnos == -1:
            messagebox.showerror("Error", "La base unificada no cuenta con registros.")
            return

        self.clear_plot_frame()
        text_widget = tk.Text(self.plot_frame, font=("Consolas", 10), wrap="none", bg="#1e1e1e", fg="#e67e22")
        text_widget.pack(fill="both", expand=True, padx=5, pady=5)
        text_widget.insert(tk.END, f"=== REPORTE DE PERNOCTAS AUTOMÁTICAS (NIGHT AIRCRAFT) ===\n")
        text_widget.insert(tk.END, f"Total detectados en base: {len(nocturnos)} aviones.\n\n")
        text_widget.insert(tk.END, f"{'MATRÍCULA / ID':<20}{'COMPAÑÍA':<15}{'SALIDA PROG':<15}{'DESTINO ICAO':<12}\n")
        text_widget.insert(tk.END, "-" * 65 + "\n")

        i = 0
        while i < len(nocturnos):
            n = nocturnos[i]
            text_widget.insert(tk.END, f"{n.codigo:<20}{n.company:<15}{n.departure_time:<15}{n.destination:<12}\n")
            i += 1

        if len(nocturnos) == 0:
            text_widget.insert(tk.END, "\n[INFO] Ningún avión pasó la noche en el aeropuerto según el cruce actual.\n")

    def f_ui_assign_gates_at_time(self):
        """Función secundaria de interfaz: Captura la hora introducida y lanza el motor de LEBL."""
        if not self.bcn_airport:
            messagebox.showerror("Error", "Primero debes cargar la estructura del aeropuerto (Función 3).")
            return
        if not self.lista_unificada:
            messagebox.showerror("Error",
                                 "Se requiere la lista unificada (Merge Movements) para procesar las ventanas horarias.")
            return

        # Crear una pequeña ventana emergente (Pop-up) para pedir el parámetro "time"
        dialog = tk.Toplevel(self.root)
        dialog.title("Simulador Dinámico de Puertas")
        dialog.geometry("340x160")
        dialog.configure(bg="#f4f6f7")
        dialog.resizable(False, False)

        tk.Label(dialog,
                 text="Introduce la hora exacta de corte (Formato hh:00):\nEjemplos: 01:00, 09:00, 14:00, 20:00",
                 bg="#f4f6f7", font=("Segoe UI", 10)).pack(pady=10)

        entry_time = ttk.Entry(dialog, width=12, font=("Segoe UI", 10, "bold"), justify="center")
        entry_time.pack(pady=2)
        entry_time.insert(0, "12:00")  # Hora de muestra predeterminada

        def procesar_simulacion():
            hora_user = entry_time.get().strip()
            if len(hora_user) != 5 or ":" not in hora_user:
                messagebox.showwarning("Formato Incorrecto",
                                       "Usa el formato estricto de 5 caracteres hh:mm (Ej: 08:00).", parent=dialog)
                return

            # Cridem directament la funció de LEBL que hem programat al punt 1
            no_asignados = LEBL.AssignGatesAtTime(self.bcn_airport, self.lista_unificada, hora_user)

            messagebox.showinfo("Proceso Dinámico Completado",
                                f"Simulación completada con éxito para la franja de las {hora_user}.\n\n"
                                f"Aeronaves rechazadas en pista por falta de puertas libres: {no_asignados}",
                                parent=dialog)

            dialog.destroy()
            # Refresca automáticamente la tabla Treeview del panel de visualización derecho
            self.f_ui_gate_occupancy()

        ttk.Button(dialog, text="Ejecutar Algoritmo", command=procesar_simulacion, width=20).pack(pady=12)

    def f_ui_plot_movements_by_hour(self):
        """Pide una hora y muestra el mapa de gates ocupadas en esa franja."""
        if not self.bcn_airport:
            messagebox.showerror("Error", "Carga primero la estructura del aeropuerto.")
            return
        if not self.lista_unificada:
            messagebox.showerror("Error", "Primero fusiona movimientos para simular una hora concreta.")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Mapa de gates por hora")
        dialog.configure(bg="#f4f6f7")
        self.center_window(dialog, 340, 155)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Introduce la hora a simular (hh:00):",
                 bg="#f4f6f7", font=("Segoe UI", 10, "bold")).pack(pady=(18, 8))
        entry_time = ttk.Entry(dialog, width=12, justify="center", font=("Segoe UI", 10, "bold"))
        entry_time.pack(pady=3)
        entry_time.insert(0, "12:00")

        def simular_hora():
            hora_user = entry_time.get().strip()
            if len(hora_user) != 5 or ":" not in hora_user:
                messagebox.showwarning("Formato incorrecto", "Usa formato hh:00, por ejemplo 08:00.", parent=dialog)
                return

            for terminal in self.bcn_airport.terminals:
                for area in terminal.boarding_areas:
                    for gate in area.gates:
                        gate.occupied = False
                        gate.aircraft_id = None

            no_asignados = LEBL.AssignGatesAtTime(self.bcn_airport, self.lista_unificada, hora_user)
            dialog.destroy()
            self.f_ui_gate_usage_diagram()
            messagebox.showinfo("Simulación por hora",
                                f"Mapa de gates generado para {hora_user}.\nArrivals sin puerta: {no_asignados}")

        ttk.Button(dialog, text="Generar mapa", command=simular_hora, width=18).pack(pady=12)
        dialog.wait_window()

    def f_ui_metar_analysis(self):
        """Analiza manualmente un METAR y muestra impacto operativo básico."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Análisis METAR")
        dialog.configure(bg="#f4f6f7")
        self.center_window(dialog, 620, 280)
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Pega un METAR para analizar condiciones operativas:",
                 bg="#f4f6f7", fg="#2c3e50", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=14, pady=(14, 6))
        text_metar = tk.Text(dialog, height=5, wrap="word", font=("Consolas", 10))
        text_metar.pack(fill="both", expand=True, padx=14, pady=6)
        text_metar.insert("1.0", "LEBL 021200Z 22012KT 9999 FEW025 24/16 Q1016")

        def analizar():
            metar = text_metar.get("1.0", tk.END).strip().upper()
            if not metar:
                messagebox.showwarning("METAR vacío", "Introduce un METAR antes de analizar.", parent=dialog)
                return
            dialog.destroy()
            self.show_metar_result(metar)

        ttk.Button(dialog, text="Analizar METAR", command=analizar, width=18).pack(pady=(4, 14))
        dialog.wait_window()

    def show_metar_result(self, metar):
        """Extrae campos sencillos de un METAR y los presenta en el panel."""
        partes = metar.split()
        viento = "No detectado"
        visibilidad = "No detectada"
        nubes = []
        temperatura = "No detectada"
        qnh = "No detectado"
        riesgo = 0
        observaciones = []

        for token in partes:
            if token.endswith("KT") and len(token) >= 5:
                viento = token
                try:
                    velocidad = int(token[3:5])
                    if velocidad >= 20:
                        riesgo += 2
                        observaciones.append("Viento fuerte: revisar asignación y aproximaciones.")
                    elif velocidad >= 12:
                        riesgo += 1
                        observaciones.append("Viento moderado.")
                except Exception:
                    pass
            elif token == "9999" or token.endswith("SM"):
                visibilidad = token
            elif token.startswith(("FEW", "SCT", "BKN", "OVC", "VV")):
                nubes.append(token)
                if token.startswith(("BKN", "OVC", "VV")):
                    riesgo += 1
            elif "/" in token and len(token) <= 7 and token[0].isdigit():
                temperatura = token
            elif token.startswith("Q") and len(token) == 5:
                qnh = token

        if visibilidad not in ("No detectada", "9999"):
            try:
                if int(visibilidad) < 5000:
                    riesgo += 2
                    observaciones.append("Visibilidad reducida.")
            except Exception:
                pass

        if riesgo >= 4:
            estado = "ALTA PRECAUCIÓN"
            color = "#f5c6c6"
        elif riesgo >= 2:
            estado = "PRECAUCIÓN"
            color = "#fcf3cf"
        else:
            estado = "OPERATIVO NORMAL"
            color = "#dff0d8"

        if not observaciones:
            observaciones.append("Condiciones sin impacto operativo relevante según este análisis básico.")

        self.show_loaded_table(
            "Análisis METAR",
            ("Campo", "Valor"),
            [
                ("METAR", metar),
                ("Viento", viento),
                ("Visibilidad", visibilidad),
                ("Nubes", ", ".join(nubes) if nubes else "No detectadas"),
                ("Temperatura/Rocío", temperatura),
                ("QNH", qnh),
                ("Estado operativo", estado),
                ("Observaciones", " ".join(observaciones)),
            ]
        )

        banner = tk.Label(self.plot_frame, text=f"Resultado METAR: {estado}", bg=color, fg="#2c3e50",
                          font=("Segoe UI", 11, "bold"), pady=6)
        banner.pack(fill="x", padx=10, pady=(0, 10))

    def f_ui_plot_day_occupancy_embedded(self):
        """Función secundaria de interfaz"""
        if not self.bcn_airport:
            messagebox.showerror("Error", "Primero debes cargar la estructura del aeropuerto (Función 3).")
            return
        if not self.lista_unificada:
            messagebox.showerror("Error",
                                 "Se requiere la lista unificada (Merge Movements) para simular el día completo.")
            return

        for terminal in self.bcn_airport.terminals:
            for area in terminal.boarding_areas:
                for gate in area.gates:
                    gate.occupied = False
                    gate.aircraft_id = None

        horas = list(range(24))
        t1_asignadas = []
        t2_asignadas = []
        rechazados = []

        for h in horas:
            hora_str = f"{h:02d}:00"
            no_asignados = LEBL.AssignGatesAtTime(self.bcn_airport, self.lista_unificada, hora_str)
            rechazados.append(no_asignados)

            ocupadas_t1 = 0
            ocupadas_t2 = 0
            for terminal in self.bcn_airport.terminals:
                total_terminal = 0
                for area in terminal.boarding_areas:
                    for gate in area.gates:
                        if gate.occupied:
                            total_terminal += 1
                if terminal.name == "T1":
                    ocupadas_t1 = total_terminal
                elif terminal.name == "T2":
                    ocupadas_t2 = total_terminal

            t1_asignadas.append(ocupadas_t1)
            t2_asignadas.append(ocupadas_t2)

        # Netejem el panell d'ajust de la dreta
        self.clear_plot_frame()

        fig, ax = plt.subplots(figsize=(9, 5), dpi=100)

        ax.bar(horas, t1_asignadas, color="#3f8fbd", label="T1 gates assigned", width=0.78)
        ax.bar(horas, t2_asignadas, bottom=t1_asignadas, color="#ff9333", label="T2 gates assigned", width=0.78)
        ax.plot(horas, rechazados, color="black", marker="o", markerfacecolor="yellow",
                markeredgecolor="black", linewidth=2.5, label="Arrivals not assigned")

        ax.set_title("Ocupación de puertas por terminal y arrivals sin puerta (por hora)", fontsize=13, pad=10)
        ax.set_xlabel("Hora del día", fontsize=10)
        ax.set_ylabel("Número de puertas", fontsize=10)
        ax.set_xticks(range(24))
        ax.grid(True, axis="y", linestyle="--", alpha=0.35)
        ax.legend(loc='upper left')
        fig.tight_layout()

        # Incrustem el gràfic a l'entorn de Tkinter del panell de la dreta
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

        # Avisem a l'usuari amb un missatge de confirmació
        messagebox.showinfo("Simulación Diaria",
                            "Gráfico de ocupación de las 24 horas generado correctamente en el panel de visualización.")
# =====================================================================================
# SECCIÓN 6: PUNTO DE ENTRADA AL PROGRAMA (MAIN RUNNER)
# =====================================================================================
if __name__ == "__main__":
    ventana = tk.Tk()  # Instancia la ventana raíz del entorno gráfico de Tkinter
    app = AirportApp(ventana)  # Pasa la ventana raíz como argumento al constructor de nuestra aplicación
    ventana.mainloop()  # Inicia el bucle de eventos
