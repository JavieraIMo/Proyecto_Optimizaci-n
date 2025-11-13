import json
import matplotlib.pyplot as plt
import numpy as np
import os

def cargar_solucion_json(ruta_json):
    with open(ruta_json, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    return datos

def graficar_calendario(datos, asignacion=None):
    trabajadores = list(datos['trabajadores'].values())
    dias = datos['metadata']['horizonte_dias']
    turnos = datos['metadata']['turnos']
    n_trabajadores = datos['metadata']['num_trabajadores']
    fig, ax = plt.subplots(figsize=(dias+2, n_trabajadores/2+2))
    tabla = []
    encabezado = ['Día'] + trabajadores
    for d in range(1, dias+1):
        fila = [f"{d}"]
        for p in range(1, n_trabajadores+1):
            celda = ""
            if asignacion:
                for t_idx, t in enumerate(turnos):
                    clave = f"x_{p}_{d}_{t}"
                    if asignacion.get(clave, 0) == 1:
                        celda += t.upper()[0] + " "
            fila.append(celda.strip())
        tabla.append(fila)
    # Mostrar tabla
    ax.axis('off')
    tabla_plot = ax.table(cellText=tabla, colLabels=encabezado, loc='center', cellLoc='center')
    tabla_plot.auto_set_font_size(False)
    tabla_plot.set_fontsize(10)
    tabla_plot.scale(1.2, 1.2)
    plt.title('Asignación de turnos (calendario)')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Graficar todas las instancias generadas en 'instancias/'
    directorio = 'instancias'
    archivos = [f for f in os.listdir(directorio) if f.endswith('.json')]
    if not archivos:
        print(f"No se encontraron archivos .json en {directorio}")
    for archivo in archivos:
        ruta_json = os.path.join(directorio, archivo)
        print(f"Mostrando calendario para: {archivo}")
        datos = cargar_solucion_json(ruta_json)
        graficar_calendario(datos)
