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
