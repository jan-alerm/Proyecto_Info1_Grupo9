
from airport import *


airport = Airport ("LEBL", 41.297445, 2.0832941)
set_schengen(airport)
print_airport(airport)


airport2 = Airport ("EGLL", 51.4700, -0.4543)
set_schengen(airport2)
print_airport(airport2)

lista = load_airports("airports.txt")
print("Aeropuertos cargados: ",len(lista))

nuevo = Airport("LEGE", 41.9009, 2.7605)
add_airport(lista, nuevo)
print("Tras añadir LEGE, total:", len(lista))

i = 0
while i < len(lista):
    set_schengen(lista[i])
    i += 1

resultado_save = save_schengen_airports(lista,"solo_schengen.txt")

if resultado_save == 1:
    print("Archivo 'solo_schengen.txt' creado con éxito.")
elif resultado_save == 0:
    print("No se creó el archivo porque no había aeropuertos Schengen.")
else:
    print("Error: La lista estaba vacía.")

codigo_a_borrar = "BIKF"
resultado_borrar = remove_airport(lista, codigo_a_borrar)
if resultado_borrar == 1:
    print("Aeropuerto", codigo_a_borrar, "eliminado correctamente.")
else:
    print("Error: No se pudo eliminar", codigo_a_borrar, "(no encontrado).")

print("\n--- LISTA FINAL DE AEROPUERTOS ---")
i = 0
while i < len(lista):
    print_airport(lista[i])
    i += 1

plot_airports(lista)
map_airports(lista)
