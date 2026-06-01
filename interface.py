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

        # --- Estados de visibilidad para los menús colapsables (Acordeón) ---
        self.airports_visible = False  # False = Menú de Aeropuertos cerrado al arrancar
        self.flights_visible = False  # False = Menú de Operaciones cerrado al arrancar
        self.gates_visible = False  # False = Menú del Administrator de Puertas cerrado al arrancar
        self.fase4_visible = False  # False = Menú de Fase 4 cerrado al arrancar

        # --- Configuración del motor de estilos tipográficos y visuales (TTK) ---
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Segoe UI", 10), padding=4)  # Diseño por defecto para botones generales
        self.style.configure("Header.TLabel",font=("Segoe UI", 16, "bold"),background="#f4f6f7",foreground="#355C8A")
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

        self.scroll_canvas.bind_all("<MouseWheel>", on_mouse_wheel)

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
            f"Estado: OK | Aeropuertos: {len(self.lista_aeropuertos)} | Vuelos (Arr): {len(self.lista_vuelos)} | Salidas (Dep): {len(self.lista_salidas)} | Estructura LEBL: {lebl_status}")

    # =====================================================================================
    # SECCIÓN 3: CONSTRUCCIÓN DEL MENÚ INTERACTIVO (CONTRACCIONES Y DESPLEGABLES)
    # =====================================================================================
    def setup_collapsible_menus(self):
        """Crea los botones principales y los subpaneles ocultos para simular un menú de pestañas colapsables."""

        # ----------------- SUBMENÚ 1: GEOMETRÍA Y AEROPUERTOS -----------------
        self.btn_toggle_airports = tk.Button(self.button_frame,
            text="▲ GEOMETRÍA Y AEROPUERTOS",
            width=35,
            bg="#8FB6E8",
            activebackground="#76A7E2",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.toggle_airports_panel)
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

        # ----------------- SUBMENÚ 2: OPERACIONES Y TRÁFICO -----------------
        self.btn_toggle_flights = tk.Button(
            self.button_frame,
            text="▲ OPERACIONES Y TRÁFICO",
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

        ttk.Button(self.flights_content, text="Cargar Archivo de Llegadas...", width=33,
                   command=self.f_load_arrivals).pack(pady=2, padx=5)
        ttk.Button(self.flights_content, text="Gráfico: Frecuencia Horaria", width=33,
                   command=self.f_plot_arrivals_embedded).pack(pady=2, padx=5)
        ttk.Button(self.flights_content, text="Gráfico: Vuelos por Aerolínea", width=33,
                   command=self.f_ui_plot_airlines_selected).pack(pady=2, padx=5)
        ttk.Button(self.flights_content, text="Gráfico: Vuelos por Origen", width=33,
                   command=self.f_plot_type_embedded).pack(pady=2, padx=5)
        ttk.Button(self.flights_content, text="Guardar Vuelos a Fichero...", width=33,
                   command=self.f_save_flights).pack(pady=2, padx=5)
        ttk.Button(self.flights_content, text="Ver Trayectorias en Google Earth", width=33,
                   command=self.f_map_flights).pack(pady=2, padx=5)
        ttk.Button(self.flights_content, text="Filtrar Larga Distancia (>2000km)", width=33,
                   command=self.f_long_flights).pack(pady=2, padx=5)

        # ----------------- SUBMENÚ 3: ADMINISTRADOR DE PUERTAS -----------------
        self.btn_toggle_gates = tk.Button(self.button_frame,
            text="▲ ADMINISTRADOR DE PUERTAS",
            width=35,
            bg="#8FB6E8",
            activebackground="#76A7E2",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.toggle_gates_panel)
        self.btn_toggle_gates.pack(fill="x", pady=(5, 0))

        self.gates_content = tk.Frame(self.button_frame, bg="#f4f6f7", bd=1, relief="groove")

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
        ttk.Button(self.gates_content, text="Asignar Puerta Automática", width=33, command=self.f_ui_assign_gate).pack(
            pady=2, padx=5)

        # ----------------- SUBMENÚ 4: SALIDAS Y FUSIÓN (NUEVA FASE 4) -----------------
        self.btn_toggle_fase4 = tk.Button(self.button_frame,
                                          text="▲ SALIDAS Y FUSIÓN (FASE 4)",
                                          width=35,
                                          bg="#8FB6E8",
                                          activebackground="#76A7E2",
                                          font=("Segoe UI", 10, "bold"),
                                          relief="flat",
                                          cursor="hand2",
                                          command=self.toggle_fase4_panel)
        self.btn_toggle_fase4.pack(fill="x", pady=(5, 0))

        self.fase4_content = tk.Frame(self.button_frame, bg="#f4f6f7", bd=1, relief="groove")

        ttk.Button(self.fase4_content, text="Cargar Archivo Salidas...", width=33,
                   command=self.f_ui_load_departures).pack(pady=2, padx=5)
        ttk.Button(self.fase4_content, text="Fusionar Movimientos (Merge)", width=33,
                   command=self.f_ui_merge_movements).pack(pady=2, padx=5)
        ttk.Button(self.fase4_content, text="Ver Aviones Nocturnos (Pernoctas)", width=33,
                   command=self.f_ui_night_aircraft).pack(pady=2, padx=5)
        ttk.Button(self.fase4_content, text="Asignación Dinámica por Hora", width=33,
                   command=self.f_ui_assign_gates_at_time).pack(pady=2, padx=5)
        ttk.Button(self.fase4_content, text="Gráfico: Ocupación Diaria 24h", width=33,
                   command=self.f_ui_plot_day_occupancy_embedded).pack(pady=2, padx=5)
        ttk.Button(self.fase4_content, text="📡 Radar de Alerta (Slots)", width=33,
                   command=self.f_ui_radar_saturacion).pack(pady=2, padx=5)

        # NUEVO BOTÓN: Auditoría de Conectividad Hub
        ttk.Button(self.fase4_content, text="📊 Auditoría Hub Analysis", width=33,
                   command=self.f_ui_hub_analysis).pack(pady=2, padx=5)

        # Cierre Seguro de Aplicación
        tk.Button(self.exit_frame, text="SALIR DE LA APLICACIÓN", width=35, bg="#C0392B", fg="white",
                  activebackground="#A93226", activeforeground="white", font=("Segoe UI", 10, "bold"), relief="flat",
                  cursor="hand2", command=self.f_ui_exit_with_feedback).pack(fill="x")

    # --- MÉTODOS DE ANIMACIÓN DE LOS MENÚS (PACK / PACK_FORGET) ---
        # =====================================================================================
        # NOU MÈTODE FASE 1: FILTRATGE DINÀMIC D'AEROLÍNIES SELECCIONADES
        # =====================================================================================
    def f_ui_plot_airlines_selected(self):
            """Función secundaria de interfaz: Pide las aerolíneas al usuario y lanza el gráfico filtrado."""
            if not self.lista_vuelos:
                messagebox.showerror("Error", "Primero debes cargar los datos de los vuelos (Pestaña Operaciones).")
                return

            # Ventana emergente para pedir los códigos de las aerolíneas
            dialog = tk.Toplevel(self.root)
            dialog.title("Filtrar Aerolíneas")
            dialog.geometry("350x150")
            dialog.configure(bg="#f4f6f7")
            dialog.resizable(False, False)

            tk.Label(dialog, text="Introduce los códigos ICAO separados por comas:\n(Ejemplo: VLG, IBE, RYR)",
                     bg="#f4f6f7", font=("Segoe UI", 10)).pack(pady=10)

            entry_airlines = ttk.Entry(dialog, width=25, font=("Segoe UI", 10), justify="center")
            entry_airlines.pack(pady=2)
            entry_airlines.insert(0, "VLG, IBE")  # Ejemplo por defecto para guiar al usuario

            def ejecutar_filtro():
                texto = entry_airlines.get().upper()
                if not texto:
                    messagebox.showwarning("Campo vacío", "Introduce al menos un código.", parent=dialog)
                    return

                # Limpiamos espacios y creamos la lista de seleccionadas de manera limpia con un bucle while
                lista_sucia = texto.split(',')
                aerolineas_elegidas = []

                idx = 0
                while idx < len(lista_sucia):
                    codigo_limpio = lista_sucia[idx].strip()
                    if codigo_limpio != "":
                        aerolineas_elegidas.append(codigo_limpio)
                    idx += 1

                dialog.destroy()

                # Llamamos a la función modificada que está en tu motor Aircraft.py
                # Le pasamos tu lista de vuelos cargada y el filtro creado
                plot_airlines(self.lista_vuelos, airlines_selected=aerolineas_elegidas)

            ttk.Button(dialog, text="Generar Gráfico", command=ejecutar_filtro, width=18).pack(pady=12)
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
        Analiza de forma predictiva la carga de movimientos y dibuja un radar
        altamente visual en el panel derecho con barras de carga, semáforos de nivel
        y una guía explicativa para el usuario.
        """
        # 1. Comprobación de seguridad de carga de datos
        movimientos_activos = []
        if hasattr(self, 'lista_unificada') and self.lista_unificada:
            movimientos_activos = self.lista_unificada
        elif hasattr(self, 'lista_vuelos') and self.lista_vuelos:
            movimientos_activos = self.lista_vuelos
        else:
            messagebox.showerror("Radar de Alerta",
                                 "No hay operaciones cargadas. Carga vuelos o realiza la fusión de movimientos primero.")
            return

        # 2. Limpiar el panel derecho completamente
        self.clear_plot_frame()

        # Configurar un estilo personalizado para que las barras de progreso tengan colores vivos
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Verde.Horizontal.TProgressbar", foreground='#2ecc71', background='#2ecc71', thickness=12)
        style.configure("Amarillo.Horizontal.TProgressbar", foreground='#f1c40f', background='#f1c40f', thickness=12)
        style.configure("Rojo.Horizontal.TProgressbar", foreground='#e74c3c', background='#e74c3c', thickness=12)

        # 3. Contenedor principal oscuro estilo Pantalla de Radar
        radar_frame = tk.Frame(self.plot_frame, bg="#111111", bd=2, relief="flat")
        radar_frame.pack(expand=True, fill="both", padx=15, pady=15)

        # Título principal del Radar con estética neón
        tk.Label(
            radar_frame,
            text="📡 RADAR DE SATURACIÓN TEMPORAL (SLOTS EN TIEMPO REAL)",
            font=("Consolas", 15, "bold"),
            bg="#111111",
            fg="#00ff66"
        ).pack(pady=(15, 5))

        # =====================================================================
        # NUEVO: PANEL EXPLICATIVO (GUÍA DE USUARIO INTEGRADA)
        # =====================================================================
        info_frame = tk.LabelFrame(
            radar_frame,
            text=" 📖 ¿CÓMO ENTENDER ESTE RADAR? ",
            font=("Segoe UI", 10, "bold"),
            bg="#1c1c1c",
            fg="#ffffff",
            relief="solid",
            bd=1
        )
        info_frame.pack(fill="x", padx=20, pady=(5, 10))

        texto_explicativo = (
            "• ¿Qué es un Slot?: Es la franja horaria asignada para que un avión pueda despegar o aterrizar en el aeropuerto.\n"
            "• ¿Qué mide este gráfico?: Analiza las 24 horas del día. Cada recuadro representa una hora y monitoriza su nivel de estrés.\n"
            "• Barras de carga: Indican visualmente el porcentaje de ocupación de la pista según el volumen máximo de vuelos del día.\n"
            "• Código de colores (Semáforo):\n"
            "   [ ✓ ESTABLE (Verde) ]: Menos de 4 operaciones por hora. Pista despejada y flujos de tráfico seguros.\n"
            "   [ ⚡ ADVERTENCIA (Amarillo) ]: Entre 4 y 7 operaciones. Tráfico moderado, requiere atención por posibles colas.\n"
            "   [ ⚠️ CRÍTICO (Rojo) ]: 8 o más operaciones. Saturación de slots. Riesgo inminente de retrasos y demoras en tierra."
        )

        tk.Label(
            info_frame,
            text=texto_explicativo,
            font=("Segoe UI", 9),
            bg="#1c1c1c",
            fg="#e0e0e0",
            justify="left",
            anchor="w"
        ).pack(fill="x", padx=15, pady=10)
        # =====================================================================

        # 4. Inicializar y contar frecuencias por hora (00:00 a 23:00)
        conteo_horas = [0] * 24
        for m in movimientos_activos:
            t_str = m.time if hasattr(m, 'time') and m.time else getattr(m, 'departure_time', "00:00")
            try:
                h = int(t_str.split(":")[0])
                if 0 <= h < 24:
                    conteo_horas[h] += 1
            except:
                pass

        # 5. Crear la cuadrícula/matriz de visualización (4 filas x 6 columnas)
        grid_frame = tk.Frame(radar_frame, bg="#111111")
        grid_frame.pack(expand=True, pady=5)

        horas_criticas = 0
        max_vuelos_esperados = max(max(conteo_horas), 1)

        for i in range(24):
            fila = i // 6
            columna = i % 6
            vuelos = conteo_horas[i]

            # Definición del Umbral de Estrés e Identidad Gráfica
            if vuelos >= 8:  # CRÍTICO (Rojo)
                color_casilla = "#f2dede"
                color_texto = "black"
                estilo_barra = "Rojo.Horizontal.TProgressbar"
                estado = "⚠️ CRÍTICO"
                horas_criticas += 1
            elif vuelos >= 4:  # TRÁFICO MEDIO (Amarillo)
                color_casilla = "#fcf8e3"
                color_texto = "black"
                estilo_barra = "Amarillo.Horizontal.TProgressbar"
                estado = "⚡ ADVERTENCIA"
            else:  # ESTABLE (Verde)
                color_casilla = "#dff0d8"
                color_texto = "black"
                estilo_barra = "Verde.Horizontal.TProgressbar"
                estado = "✓ ESTABLE"

            # Crear el recuadro GIGANTE con BORDE NEGRO ESTRICTO de 2 píxeles
            casilla = tk.Frame(
                grid_frame,
                bg=color_casilla,
                highlightbackground="black",
                highlightthickness=2,
                width=140,
                height=90
            )
            casilla.grid(row=fila, column=columna, padx=8, pady=5)
            casilla.grid_propagate(False)

            # Elemento 1: Identificador de Hora (Texto Negro)
            tk.Label(casilla, text=f"🕒 {str(i).zfill(2)}:00 h", font=("Segoe UI", 10, "bold"), bg=color_casilla,
                     fg=color_texto).pack(pady=(4, 2))

            # Elemento 2: Barra de Progreso Visual
            progreso = ttk.Progressbar(casilla, orient="horizontal", length=110, mode="determinate", style=estilo_barra)
            progreso.pack(pady=2)
            porcentaje_llenado = (vuelos / max_vuelos_esperados) * 100
            progreso['value'] = porcentaje_llenado

            # Elemento 3: Métrica Numérica (Texto Negro destacado)
            tk.Label(casilla, text=f"{vuelos} Operaciones", font=("Segoe UI", 10, "bold"), bg=color_casilla,
                     fg=color_texto).pack()

            # Elemento 4: Estado textual descriptivo
            tk.Label(casilla, text=estado, font=("Segoe UI", 8, "bold"), bg=color_casilla, fg=color_texto).pack(
                pady=(2, 2))

        # 6. Barra inferior de Diagnóstico Automatizado
        if horas_criticas > 0:
            diagnostico_txt = f"🚨 ALERTA DEL SISTEMA: Se detectan {horas_criticas} franjas horarias saturadas con riesgo inminente de retrasos."
            color_diag = "#ff3333"
        else:
            diagnostico_txt = "🟢 DIAGNÓSTICO: Todos los slots horarios operan con flujos de tráfico seguros y estables."
            color_diag = "#00ff66"

        tk.Label(
            radar_frame,
            text=diagnostico_txt,
            font=("Segoe UI", 12, "bold"),
            bg="#111111",
            fg=color_diag
        ).pack(pady=(10, 15))

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
            "• Propósito: Evalúa si el aeropuerto funciona eficientemente como centro de interconexión logística (Hub), "
            "analizando la coordinación temporal entre los vuelos que aterrizan y los que despegan.\n\n"
            "• Método de Análisis: El sistema escanea en tiempo real las listas de Llegadas (Fase 1) y Salidas (Fase 4). "
            "Busca automáticamente parejas de vuelos operados por la misma aerolínea o alianza táctica.\n\n"
            "• Ventanas de Conexión Evaluadas:\n"
            "  - 🟢 Conexiones Viables (Entre 35 min y 4 horas): Intervalo óptimo que permite a los pasajeros bajarse de su "
            "primer avión, cruzar la terminal y embarcar en el segundo vuelo de forma cómoda.\n"
            "  - 🔴 Riesgo Pérdida de Maletas (Menos de 35 min): Ventana excesivamente ajustada. Alerta al operador de la torre "
            "porque el personal de tierra (Handling) no dispondrá de tiempo suficiente para trasladar el equipaje facturado "
            "de una bodega a otra, generando retrasos o pérdidas."
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
            self.btn_toggle_airports.configure(text="▲ GEOMETRÍA Y AEROPUERTOS")
            self.airports_visible = False
        else:
            self.airports_content.pack(fill="x", padx=2, pady=(0, 10), after=self.btn_toggle_airports)
            self.btn_toggle_airports.configure(text="▼ GEOMETRÍA Y AEROPUERTOS")
            self.airports_visible = True

    def toggle_flights_panel(self):
        if self.flights_visible:
            self.flights_content.pack_forget()
            self.btn_toggle_flights.configure(text="▲ OPERACIONES Y TRÁFICO")
            self.flights_visible = False
        else:
            self.flights_content.pack(fill="x", padx=2, pady=(0, 10), after=self.btn_toggle_flights)
            self.btn_toggle_flights.configure(text="▼ OPERACIONES Y TRÁFICO")
            self.flights_visible = True

    def toggle_gates_panel(self):
        if self.gates_visible:
            self.gates_content.pack_forget()
            self.btn_toggle_gates.configure(text="▲ ADMINISTRADOR DE PUERTAS")
            self.gates_visible = False
        else:
            self.gates_content.pack(fill="x", padx=2, pady=(0, 10), after=self.btn_toggle_gates)
            self.btn_toggle_gates.configure(text="▼ ADMINISTRADOR DE PUERTAS")
            self.gates_visible = True

    def toggle_fase4_panel(self):
        if self.fase4_visible:
            self.fase4_content.pack_forget()
            self.btn_toggle_fase4.configure(text="▲ SALIDAS Y FUSIÓN (FASE 4)")
            self.fase4_visible = False
        else:
            self.fase4_content.pack(fill="x", padx=2, pady=(0, 10), after=self.btn_toggle_fase4)
            self.btn_toggle_fase4.configure(text="▼ SALIDAS Y FUSIÓN (FASE 4)")
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
        map_airports(self.lista_aeropuertos)
        messagebox.showinfo("KML Generado", "Se ha creado 'airports_map.kml' en el directorio de trabajo.")

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

        fig, ax = plt.subplots(figsize=(5, 4))
        ax.bar(["Schengen", "No Schengen"], [schengen, not_schengen], color=["#3498db", "#e74c3c"])
        ax.set_title("Proporción de Espacio Schengen")
        ax.set_ylabel("Cantidad")

        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

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
        ax.bar(range(24), horas, color="#2ecc71")
        ax.set_title("Frecuencia Horaria de Operaciones")
        ax.set_xlabel("Hora del Día")
        ax.set_ylabel("Vuelos")
        ax.set_xticks(range(24))

        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def f_plot_airlines_embedded(self):
        if not self.lista_vuelos:
            messagebox.showerror("Error", "Carga datos de vuelos primero.")
            return
        self.clear_plot_frame()
        airlines_dict = {}
        i = 0
        while i < len(self.lista_vuelos):
            comp = self.lista_vuelos[i].company
            airlines_dict[comp] = airlines_dict.get(comp, 0) + 1
            i += 1

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(airlines_dict.keys(), airlines_dict.values(), color="#9b59b6")
        ax.set_title("Operaciones Agrupadas por Aerolínea")
        plt.setp(ax.get_xticklabels(), rotation=45, horizontalalignment='right')

        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def f_plot_type_embedded(self):
        if not self.lista_vuelos or not self.lista_aeropuertos:
            messagebox.showerror("Error", "Se requieren listas de vuelos y aeropuertos cruzadas.")
            return
        self.clear_plot_frame()
        origenes = {}
        i = 0
        while i < len(self.lista_vuelos):
            orig = self.lista_vuelos[i].origin
            origenes[orig] = origenes.get(orig, 0) + 1
            i += 1

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(origenes.keys(), origenes.values(), color="#f1c40f")
        ax.set_title("Distribución por Aeropuerto de Origen")
        plt.setp(ax.get_xticklabels(), rotation=45, horizontalalignment='right')

        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

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
        map_flights(self.lista_vuelos, self.lista_aeropuertos)
        messagebox.showinfo("Rutas de Vuelo", "Se generó 'flights_map.kml' con las trazas de arco geodésico.")

    def f_long_flights(self):
        if not self.lista_vuelos or not self.lista_aeropuertos:
            messagebox.showerror("Error", "Faltan datos operacionales esenciales para el cálculo.")
            return
        largos = long_distance_arrivals(self.lista_vuelos, self.lista_aeropuertos)
        if largos:
            messagebox.showinfo("Filtro Geo",
                                f"Detectados {len(largos)} vuelos de larga distancia (>2000 km) hacia LEBL.")
            self.clear_plot_frame()
            text_widget = tk.Text(self.plot_frame, font=("Consolas", 10), wrap="none", bg="#1e1e1e", fg="#ffffff")
            text_widget.pack(fill="both", expand=True, padx=5, pady=5)
            text_widget.insert(tk.END, "=== AVIONES DE LARGO RECORRIDO INSPECCIONADOS ===\n\n")
            i = 0
            while i < len(largos):
                v = largos[i]
                text_widget.insert(tk.END, f"Avión: {v.codigo} | Procedencia: {v.origin} | Cía: {v.company}\n")
                i += 1
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
                    self.clear_plot_frame()
                    self.show_welcome_message()
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

        tk.Label(work_panel, text="Asignación Individual de Puerta (AssignGate)", font=("Segoe UI", 11, "bold"),
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
            elif puerta_obtenida == False:
                messagebox.showwarning("Saturación", "No quedan puertas libres en la zona adecuada para este vuelo.")
            else:
                messagebox.showinfo("Éxito",
                                    f"Vuelo {vuelo_seleccionado.codigo} asignado con éxito a la puerta: {puerta_obtenida}")

        ttk.Button(work_panel, text="Asignar Puerta Automática", command=ejecutar_asignacion).grid(row=2, column=0,
                                                                                                   columnspan=2,
                                                                                                   pady=15)

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
            self.clear_plot_frame()

            text_widget = tk.Text(self.plot_frame, font=("Consolas", 10), wrap="none", bg="#1e1e1e", fg="#ffffff")
            text_widget.pack(fill="both", expand=True, padx=5, pady=5)
            text_widget.insert(tk.END, f"=== REGISTRO DE SALIDAS OPERATIVAS (Fichero: {path.split('/')[-1]}) ===\n\n")
            text_widget.insert(tk.END, f"{'AIRCRAFT':<15}{'DESTINATION':<15}{'DEPARTURE TIME':<18}{'AIRLINE':<10}\n")
            text_widget.insert(tk.END, "-" * 60 + "\n")

            i = 0
            while i < len(self.lista_salidas):
                dep = self.lista_salidas[i]
                text_widget.insert(tk.END,
                                   f"{dep.codigo:<15}{dep.destination:<15}{dep.departure_time:<18}{dep.company:<10}\n")
                i += 1
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

    def f_ui_plot_day_occupancy_embedded(self):
        """Función secundaria de interfaz"""
        if not self.bcn_airport:
            messagebox.showerror("Error", "Primero debes cargar la estructura del aeropuerto (Función 3).")
            return
        if not self.lista_unificada:
            messagebox.showerror("Error",
                                 "Se requiere la lista unificada (Merge Movements) para simular el día completo.")
            return

        # Executem el motor de simulació de 24 hores que hem programat a LEBL
        horas, ocupados, rechazados = LEBL.PlotDayOccupancy(self.bcn_airport, self.lista_unificada)

        # Netejem el panell d'ajust de la dreta
        self.clear_plot_frame()

        # Creem el gràfic de Matplotlib amb dos subplots o línies combinades
        fig, ax = plt.subplots(figsize=(7, 4.5))

        # Línia 1: Portes ocupades en total
        ax.plot(horas, ocupados, marker='o', color='#2980b9', linewidth=2, label='Puertas Ocupadas')
        # Línia 2: Avions rebutjats (sense porta)
        ax.plot(horas, rechazados, marker='x', color='#e74c3c', linewidth=2, linestyle='--', label='Aviones sin Puerta')

        ax.set_title("Puertas Ocupadas VS Aviones sin Puertas", fontsize=12, fontweight='bold', pad=10)
        ax.set_xlabel("Hora del Día (00:00 - 23:00)", fontsize=10)
        ax.set_ylabel("Cantidad de Aeronaves por puertas", fontsize=10)
        ax.set_xticks(range(24))
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.legend(loc='upper left')

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
