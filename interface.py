from Aircraft import *


class AirportApp:
    def __init__(self, root):
        self.lista_vuelos = []
        self.root = root
        self.root.title("Airport Manager v1.0")
        self.root.geometry("400x500")
        self.lista_aeropuertos = []


        tk.Label(root, text="AIRPORT MANAGEMENT SYSTEM", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Button(root, text="1. Load Airports from File", width=30, command=self.f_load).pack(pady=5)

        tk.Button(root, text="2. Set Schengen Attribute", width=30, command=self.f_schengen).pack(pady=5)

        tk.Button(root, text="3. Show Data (Console)", width=30, command=self.f_show).pack(pady=5)

        tk.Button(root, text="4. Save Schengen to File", width=30, command=self.f_save).pack(pady=5)

        tk.Button(root, text="5. Plot Schengen Stats", width=30, command=self.f_plot).pack(pady=5)

        tk.Button(root, text="6. Show in Google Earth", width=30, command=self.f_map).pack(pady=5)

        tk.Button(root, text="7. Delete Airport (BIKF)", width=30, command=self.f_delete).pack(pady=5)

        tk.Button(root, text="EXIT", width=30, bg="red", fg="white", command=root.quit).pack(pady=20)

        tk.Label(root, text="LEBL ARRIVALS (V2)", font=("Arial", 12, "bold"), fg="blue").pack(pady=10)

        tk.Button(root, text="8. Load Arrivals (LEBL)", width=30, command=self.f_load_arrivals).pack(pady=5)
        tk.Button(root, text="9. Plot Arrivals Frequency", width=30, command=self.f_plot_arrivals).pack(pady=5)
        tk.Button(root, text="10. Save Flights to File", width=30, command=self.f_save_flights).pack(pady=5)

        tk.Button(root, text="11. Plot Flights per Airline", width=35, command=self.f_plot_airlines).pack(pady=2)
        tk.Button(root, text="12. Plot Flights by Type", width=35, command=self.f_plot_type).pack(pady=2)

        tk.Button(root, text="EXIT", width=30, bg="red", fg="white", command=root.quit).pack(pady=20)

    def f_load(self):
        self.lista_aeropuertos = load_airports("airports.txt")
        messagebox.showinfo("Success", "Loaded " + str(len(self.lista_aeropuertos)) + " airports.")

    def f_schengen(self):
        i = 0
        while i < len(self.lista_aeropuertos):
            set_schengen(self.lista_aeropuertos[i])
            i += 1
        messagebox.showinfo("Success", "Schengen attribute updated for all.")

    def f_show(self):
        print("\n--- Current Airports in List ---")
        i = 0
        while i < len(self.lista_aeropuertos):
            print_airport(self.lista_aeropuertos[i])
            i += 1
        messagebox.showinfo("Info", "Check your PyCharm console to see the data.")

    def f_save(self):
        res = save_schengen_airports(self.lista_aeropuertos, "solo_schengen.txt")
        if res == 1:
            messagebox.showinfo("Success", "File 'solo_schengen.txt' created.")
        else:
            messagebox.showwarning("Error", "Could not save (list empty or no Schengen).")

    def f_plot(self):
        plot_airports(self.lista_aeropuertos)

    def f_map(self):
        map_airports(self.lista_aeropuertos)
        messagebox.showinfo("KML", "KML file generated. Open it in Google Earth.")

    def f_delete(self):
        # Ejemplo borrando BIKF como pedía el Step 4
        res = remove_airport(self.lista_aeropuertos, "BIKF")
        if res == 1:
            messagebox.showinfo("Success", "BIKF removed from memory.")
        else:
            messagebox.showerror("Error", "BIKF not found.")

    def f_load_arrivals(self):
        self.lista_vuelos = load_arrivals("arrivals.txt")
        if self.lista_vuelos:
            messagebox.showinfo("Success", f"Loaded {len(self.lista_vuelos)} aircraft arrivals.")
        else:
            messagebox.showwarning("Warning", "No arrivals loaded. Check 'arrivals.txt'.")

    def f_plot_arrivals(self):
        if self.lista_vuelos:
            plot_arrivals(self.lista_vuelos)
        else:
            messagebox.showerror("Error", "No flight data to plot.")

    def f_save_flights(self):
        res = save_flights(self.lista_vuelos, "saved_arrivals.txt")
        if res == 1:
            messagebox.showinfo("Success", "Flights saved to 'saved_arrivals.txt'.")
        else:
            messagebox.showerror("Error", "List is empty, file not created.")

    def f_plot_airlines(self):
        if self.lista_vuelos:
            plot_airlines(self.lista_vuelos)
        else:
            messagebox.showerror("Error", "No flights loaded for Airline plot.")

    def f_plot_type(self):
        if self.lista_vuelos:
            PlotFlightsType(self.lista_vuelos)
        else:
            messagebox.showerror("Error", "No flights loaded for Type plot.")

    # --- INICIO DE LA APLICACIÓN ---


if __name__ == "__main__":
    ventana = tk.Tk()
    app = AirportApp(ventana)
    ventana.mainloop()
