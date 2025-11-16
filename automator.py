import subprocess
import os
import time
import glob
from pathlib import Path

def run_minizinc_with_solutions(model_file, dataset_file, output_file, timeout_ms, max_solutions=3):
    """
    Ejecuta MiniZinc buscando hasta max_solutions soluciones o hasta timeout
    """
    solutions_found = 0
    output_content = ""
    
    try:
        # Preparar comando base
        cmd = [
            'minizinc', 
            '--solver', 'chuffed',
            '--time-limit', str(timeout_ms),
            '--output-time',
            '--statistics'
        ]
        
        # Si queremos múltiples soluciones, añadir parámetro
        if max_solutions > 1:
            cmd.extend(['-a', '-n', str(max_solutions)])  # -a: todas las soluciones, -n: máximo número
        
        cmd.extend([str(model_file), str(dataset_file)])
        
        # Ejecutar MiniZinc con codificación UTF-8 explícita
        start_time = time.time()
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='replace',  # Reemplazar caracteres problemáticos
            timeout=(timeout_ms/1000)+10
        )
        end_time = time.time()
        actual_time = end_time - start_time
        
        # Analizar salida para contar soluciones
        output_lines = result.stdout.split('\n')
        solutions_found = 0
        solution_times = []
        statistics = []
        
        # Contar soluciones basado en líneas típicas de MiniZinc
        for line in output_lines:
            # Detectar soluciones (formato común de MiniZinc)
            if '----------' in line or 'solution' in line.lower() and '=' in line:
                solutions_found += 1
            # Capturar líneas de estadísticas
            elif any(keyword in line.lower() for keyword in ['%', 'time:', 'solve', 'variables', 'constraints']):
                if line.strip():
                    statistics.append(line.strip())
        
        # Si no detectamos soluciones con el método anterior, usar enfoque alternativo
        if solutions_found == 0 and '==========' in result.stdout:
            solutions_found = result.stdout.count('==========')
        
        # Preparar contenido del resultado
        output_content = f"Dataset: {os.path.basename(dataset_file)}\n"
        output_content += f"Tiempo límite: {timeout_ms/1000/60:.1f} minutos\n"
        output_content += f"Tiempo total ejecución: {actual_time:.2f} segundos\n"
        output_content += f"Soluciones solicitadas: {max_solutions}\n"
        output_content += f"Soluciones encontradas: {solutions_found}\n"
        output_content += f"Status: {'SOLUCIÓN(ES) ENCONTRADA(S)' if solutions_found > 0 else 'SIN SOLUCIONES'}\n"
        output_content += "=" * 60 + "\n"
        
        # Agregar estadísticas
        if statistics:
            output_content += "ESTADÍSTICAS DEL SOLVER:\n"
            for stat in statistics:
                output_content += f"  {stat}\n"
            output_content += "-" * 40 + "\n"
        
        # Agregar salida completa
        output_content += "SALIDA COMPLETA:\n"
        output_content += result.stdout
        
        if result.stderr:
            output_content += "\n[ERRORES]\n" + result.stderr
            
    except subprocess.TimeoutExpired:
        actual_time = timeout_ms / 1000
        output_content = f"Dataset: {os.path.basename(dataset_file)}\n"
        output_content += f"Tiempo límite: {timeout_ms/1000/60:.1f} minutos\n"
        output_content += f"Tiempo ejecución: {actual_time:.2f} segundos\n"
        output_content += f"Soluciones solicitadas: {max_solutions}\n"
        output_content += f"Soluciones encontradas: {solutions_found}\n"
        output_content += "Status: LÍMITE DE TIEMPO EXCEDIDO\n"
        output_content += "=" * 60 + "\n"
        output_content += "El solver no encontró todas las soluciones dentro del tiempo límite\n"
    
    except UnicodeDecodeError as e:
        output_content = f"Dataset: {os.path.basename(dataset_file)}\n"
        output_content += f"Tiempo límite: {timeout_ms/1000/60:.1f} minutos\n"
        output_content += "Status: ERROR DE CODIFICACIÓN\n"
        output_content += f"Soluciones solicitadas: {max_solutions}\n"
        output_content += f"Soluciones encontradas: {solutions_found}\n"
        output_content += f"Error: Problema de codificación - {str(e)}\n"
        output_content += "Sugerencia: El solver puede estar outputendo caracteres no UTF-8\n"
    
    except Exception as e:
        output_content = f"Dataset: {os.path.basename(dataset_file)}\n"
        output_content += f"Tiempo límite: {timeout_ms/1000/60:.1f} minutos\n"
        output_content += "Status: ERROR EN LA EJECUCIÓN\n"
        output_content += f"Soluciones solicitadas: {max_solutions}\n"
        output_content += f"Soluciones encontradas: {solutions_found}\n"
        output_content += f"Error: {str(e)}\n"
        output_content += f"Tipo de error: {type(e).__name__}\n"
    
    # Guardar resultados
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_content)
    except Exception as e:
        print(f"    ❌ Error guardando archivo: {e}")
        # Crear contenido de emergencia
        emergency_content = f"Error guardando resultados para {dataset_file}\nError: {e}"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(emergency_content)
    
    return output_content, solutions_found

def check_dependencies():
    """Verificar que MiniZinc esté disponible"""
    try:
        result = subprocess.run(['minizinc', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ MiniZinc encontrado")
            return True
        else:
            print("❌ MiniZinc no responde correctamente")
            return False
    except FileNotFoundError:
        print("❌ MiniZinc no encontrado. Asegúrate de que esté instalado y en el PATH")
        return False
    except Exception as e:
        print(f"❌ Error verificando MiniZinc: {e}")
        return False

def main():
    # Configuración de rutas
    BASE_DIR = Path(".").resolve()
    INSTANCIAS_DIR = BASE_DIR / "instancias"
    RESULTADOS_DIR = BASE_DIR / "Resultadosminizinc"
    MODEL_FILE = BASE_DIR / "modelo.mzn"
    
    print("🔍 Verificando dependencias...")
    if not check_dependencies():
        return
    
    # Verificar que existen los directorios y archivos necesarios
    if not INSTANCIAS_DIR.exists():
        print(f"❌ No se encuentra el directorio de instancias: {INSTANCIAS_DIR}")
        return
    
    if not MODEL_FILE.exists():
        print(f"❌ No se encuentra el modelo: {MODEL_FILE}")
        return
    
    # Crear directorio de resultados si no existe
    RESULTADOS_DIR.mkdir(exist_ok=True)
    
    # Configuración de tiempos por tipo (en milisegundos)
    TIMEOUT_CONFIG = {
        "pequeñas": 5 * 60 * 1000,    # 5 minutos
        "medianas": 10 * 60 * 1000,   # 10 minutos  
        "grandes": 25 * 60 * 1000     # 25 minutos
    }
    
    # Configuración de número de soluciones por tipo
    SOLUTIONS_CONFIG = {
        "pequeñas": 3,   # Buscar hasta 3 soluciones para pequeñas
        "medianas": 3,    # Buscar hasta 3 soluciones para medianas  
        "grandes": 1      # Buscar solo 1 solución para grandes (por tiempo)
    }
    
    # Tipos de datasets
    TIPOS = ["pequeñas", "medianas", "grandes"]
    
    print("\n🚀 Iniciando ejecución automática de MiniZinc")
    print(f"📁 Instancias: {INSTANCIAS_DIR}")
    print(f"📊 Resultados: {RESULTADOS_DIR}")
    print(f"🔧 Modelo: {MODEL_FILE}")
    print("-" * 60)
    
    # Estadísticas
    stats = {
        "total": 0,
        "completados": 0,
        "timeouts": 0,
        "errores": 0,
        "soluciones_totales": 0
    }
    
    # Procesar cada tipo de dataset
    for tipo in TIPOS:
        print(f"\n📂 Procesando datasets {tipo}...")
        timeout_ms = TIMEOUT_CONFIG[tipo]
        max_solutions = SOLUTIONS_CONFIG[tipo]
        
        for n in range(1, 6):  # n del 1 al 5
            # Formato del archivo: pequeñas_01.dzn, pequeñas_02.dzn, etc.
            dataset_pattern = f"{tipo}_{n:02d}.dzn"
            dataset_files = list(INSTANCIAS_DIR.glob(dataset_pattern))
            
            if not dataset_files:
                print(f"  ⚠️  No se encontró: {dataset_pattern}")
                continue
                
            dataset_file = dataset_files[0]
            stats["total"] += 1
            
            # Nombre del archivo de resultado: Resultado_pequeño_01.txt (con 01)
            tipo_singular = tipo[:-1] + 'o' if tipo.endswith('as') else tipo
            output_filename = f"Resultado_{tipo_singular}_{n:02d}.txt"
            output_file = RESULTADOS_DIR / output_filename
            
            print(f"  🔄 Ejecutando: {dataset_file.name}")
            print(f"    ⏰ Timeout: {timeout_ms/60000:.0f}min, Soluciones: {max_solutions}")
            
            try:
                # Ejecutar MiniZinc
                result, solutions_found = run_minizinc_with_solutions(
                    MODEL_FILE, 
                    dataset_file, 
                    output_file, 
                    timeout_ms,
                    max_solutions
                )
                
                stats["soluciones_totales"] += solutions_found
                
                # Analizar resultado
                if "LÍMITE DE TIEMPO EXCEDIDO" in result:
                    stats["timeouts"] += 1
                    print(f"    ⏰ Timeout - Soluciones encontradas: {solutions_found}")
                elif "ERROR" in result:
                    stats["errores"] += 1
                    print(f"    ❌ Error en ejecución - Soluciones: {solutions_found}")
                else:
                    stats["completados"] += 1
                    print(f"    ✅ Completado - Soluciones: {solutions_found}")
                    
            except Exception as e:
                stats["errores"] += 1
                print(f"    💥 Error crítico: {e}")
                # Crear archivo de error
                error_content = f"Error crítico procesando {dataset_file.name}\nError: {e}"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(error_content)
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN EJECUCIÓN")
    print(f"   Total datasets procesados: {stats['total']}")
    print(f"   Ejecuciones completadas: {stats['completados']}")
    print(f"   Timeouts: {stats['timeouts']}")
    print(f"   Errores: {stats['errores']}")
    print(f"   Total soluciones encontradas: {stats['soluciones_totales']}")
    print(f"   Resultados guardados en: {RESULTADOS_DIR}")

if __name__ == "__main__":
    main()