import os
import re
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

def parse_result_file(file_path):
    """
    Extrae información importante del archivo de resultados
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Datos básicos
    dataset_match = re.search(r'Dataset: (\S+)', content)
    tiempo_total_match = re.search(r'Tiempo total ejecución: ([\d.]+) segundos', content)
    soluciones_encontradas_match = re.search(r'Soluciones encontradas: (\d+)', content)
    status_match = re.search(r'Status: (.+)', content)
    
    # Buscar tiempo de primera solución
    primera_sol_match = re.search(r'Tiempo hasta primera solución: ([\d.]+) segundos', content)
    
    # Buscar en las estadísticas MiniZinc el tiempo de solve
    solve_time_match = re.search(r'%%%mzn-stat: solveTime=([\d.]+)', content)
    
    # Buscar número de soluciones en estadísticas
    solutions_stat_match = re.search(r'%%%mzn-stat: nSolutions=(\d+)', content)
    
    # Si no encontramos tiempo de primera solución pero hay solveTime, usamos ese
    tiempo_primera_sol = None
    if primera_sol_match:
        tiempo_primera_sol = float(primera_sol_match.group(1))
    elif solve_time_match:
        tiempo_primera_sol = float(solve_time_match.group(1))
    
    # Número de soluciones
    if solutions_stat_match:
        soluciones_encontradas = int(solutions_stat_match.group(1))
    elif soluciones_encontradas_match:
        soluciones_encontradas = int(soluciones_encontradas_match.group(1))
    else:
        soluciones_encontradas = 0
    
    return {
        'dataset': dataset_match.group(1) if dataset_match else os.path.basename(file_path),
        'tiempo_total': float(tiempo_total_match.group(1)) if tiempo_total_match else None,
        'tiempo_primera_sol': tiempo_primera_sol,
        'soluciones_encontradas': soluciones_encontradas,
        'status': status_match.group(1) if status_match else 'DESCONOCIDO',
        'timeout': 'LÍMITE DE TIEMPO EXCEDIDO' in content
    }

def generar_grafico_tipo(tipo_archivo, tipo_display, datos, output_dir):
    """
    Genera gráfico de barras para un tipo específico
    """
    # Filtrar datos válidos
    datos_validos = [d for d in datos if d['tiempo_primera_sol'] is not None]
    
    if not datos_validos:
        print(f"  ⚠️  No hay datos válidos para {tipo_display}")
        return
    
    # Ordenar por número de dataset
    datos_validos.sort(key=lambda x: int(re.search(r'(\d+)', x['dataset']).group(1)))
    
    # Preparar datos para el gráfico
    datasets = [d['dataset'].replace('.dzn', '') for d in datos_validos]
    tiempos = [d['tiempo_primera_sol'] for d in datos_validos]
    soluciones = [d['soluciones_encontradas'] for d in datos_validos]
    
    # Crear gráfico
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Barras de tiempo
    bars = ax1.bar(datasets, tiempos, color='skyblue', alpha=0.7, label='Tiempo primera solución (s)')
    ax1.set_xlabel('Dataset')
    ax1.set_ylabel('Tiempo (segundos)', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.set_title(f'Tiempo de Ejecución vs Dataset - {tipo_display.capitalize()}')
    plt.xticks(rotation=45)
    
    # Añadir etiquetas con el tiempo en las barras
    for bar, tiempo in zip(bars, tiempos):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + max(tiempos)*0.01,
                f'{tiempo:.1f}s', ha='center', va='bottom', fontsize=9)
    
    # Añadir número de soluciones como texto arriba de las barras
    for i, (bar, sol) in enumerate(zip(bars, soluciones)):
        ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + max(tiempos)*0.05,
                f'{sol} sol', ha='center', va='bottom', fontsize=8, color='red', weight='bold')
    
    plt.tight_layout()
    
    # Guardar gráfico
    output_path = output_dir / f"grafico_tiempos_{tipo_archivo}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"  📊 Gráfico guardado: {output_path}")

def crear_archivo_analisis(tipo_archivo, tipo_display, datos, output_dir):
    """
    Crea archivo de análisis conciso para cada tipo
    """
    # Ordenar por número de dataset
    datos_ordenados = sorted(datos, key=lambda x: int(re.search(r'(\d+)', x['dataset']).group(1)))
    
    # Preparar contenido
    contenido = f"ANÁLISIS DE DATOS - {tipo_display.upper()}\n"
    contenido += "=" * 50 + "\n\n"
    
    for dato in datos_ordenados:
        contenido += f"Dataset: {dato['dataset']}\n"
        contenido += f"Status: {dato['status']}\n"
        contenido += f"Soluciones encontradas: {dato['soluciones_encontradas']}\n"
        
        if dato['tiempo_primera_sol'] is not None:
            contenido += f"Tiempo primera solución: {dato['tiempo_primera_sol']:.2f} segundos\n"
        else:
            contenido += "Tiempo primera solución: NO ENCONTRADO\n"
        
        if dato['tiempo_total'] is not None:
            contenido += f"Tiempo total ejecución: {dato['tiempo_total']:.2f} segundos\n"
        
        contenido += f"Timeout: {'SÍ' if dato['timeout'] else 'NO'}\n"
        contenido += "-" * 30 + "\n"
    
    # Añadir resumen estadístico
    tiempos_validos = [d['tiempo_primera_sol'] for d in datos_ordenados if d['tiempo_primera_sol'] is not None]
    soluciones_totales = sum([d['soluciones_encontradas'] for d in datos_ordenados])
    timeouts = sum([1 for d in datos_ordenados if d['timeout']])
    
    contenido += "\nRESUMEN ESTADÍSTICO:\n"
    contenido += f"Total datasets: {len(datos_ordenados)}\n"
    contenido += f"Total soluciones encontradas: {soluciones_totales}\n"
    contenido += f"Timeouts: {timeouts}\n"
    
    if tiempos_validos:
        contenido += f"Tiempo promedio primera solución: {sum(tiempos_validos)/len(tiempos_validos):.2f} segundos\n"
        contenido += f"Tiempo máximo: {max(tiempos_validos):.2f} segundos\n"
        contenido += f"Tiempo mínimo: {min(tiempos_validos):.2f} segundos\n"
    
    # Guardar archivo
    output_path = output_dir / f"datosAnalisis_{tipo_archivo}.txt"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print(f"  📄 Archivo análisis guardado: {output_path}")

def main():
    # Configuración de rutas
    BASE_DIR = Path(".").resolve()
    RESULTADOS_DIR = BASE_DIR / "Resultadosminizinc"
    ANALISIS_DIR = BASE_DIR / "datosAnalisis"
    
    # Crear directorio de análisis si no existe
    ANALISIS_DIR.mkdir(exist_ok=True)
    
    print("📈 Iniciando análisis de resultados...")
    print(f"📁 Resultados: {RESULTADOS_DIR}")
    print(f"📊 Análisis: {ANALISIS_DIR}")
    print("-" * 50)
    
    # Mapeo de nombres de archivo a nombres de display
    # Basado en los nombres reales que me proporcionaste
    TIPOS_CONFIG = {
        "pequeñao": "pequeñas",
        "medianao": "medianas", 
        "grandes": "grandes"
    }
    
    # Procesar cada tipo
    for tipo_archivo, tipo_display in TIPOS_CONFIG.items():
        print(f"\n🔍 Analizando tipo: {tipo_display} (archivos: {tipo_archivo}_*.txt)")
        
        # Buscar archivos de resultados para este tipo
        pattern = f"Resultado_{tipo_archivo}_*.txt"
        archivos_resultados = list(RESULTADOS_DIR.glob(pattern))
        
        if not archivos_resultados:
            print(f"  ⚠️  No se encontraron archivos para patrón: {pattern}")
            # Listar archivos disponibles para debugging
            todos_archivos = list(RESULTADOS_DIR.glob("Resultado_*.txt"))
            if todos_archivos:
                print(f"  📂 Archivos disponibles: {[f.name for f in todos_archivos]}")
            continue
        
        print(f"  📁 Encontrados {len(archivos_resultados)} archivos")
        
        # Parsear todos los archivos
        datos_tipo = []
        for archivo in archivos_resultados:
            try:
                datos = parse_result_file(archivo)
                datos_tipo.append(datos)
                print(f"    ✅ {archivo.name} - {datos['soluciones_encontradas']} soluciones - {datos['tiempo_primera_sol'] or 'N/A'}s")
            except Exception as e:
                print(f"    ❌ Error parseando {archivo.name}: {e}")
        
        # Generar gráfico
        generar_grafico_tipo(tipo_archivo, tipo_display, datos_tipo, ANALISIS_DIR)
        
        # Crear archivo de análisis
        crear_archivo_analisis(tipo_archivo, tipo_display, datos_tipo, ANALISIS_DIR)
    
    print("\n" + "=" * 50)
    print("🎉 Análisis completado!")
    print(f"📈 Gráficos guardados en: {ANALISIS_DIR}")
    print(f"📄 Archivos de análisis guardados en: {ANALISIS_DIR}")

if __name__ == "__main__":
    main()