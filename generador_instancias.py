"""
Generador de Instancias ACTUALIZADO según especificaciones del profesor
- 5 instancias por tamaño (pequeñas, medianas, grandes)
- Distribución Uniforme U(0,10) para disposición
- Distribución Normal para demanda por turno
- Rangos específicos según tabla del profesor
"""

import random
import numpy as np
import json
from datetime import datetime
import argparse
import os

class GeneradorInstanciasProfesor:
    def __init__(self, semilla=42):
        """
        Generador según especificaciones 
        """
        self.semilla = semilla
        random.seed(semilla)
        np.random.seed(semilla)
        self.turnos = ['m', 't', 'n']  # mañana, tarde, noche
        
        # Rangos según tabla 
        self.tamaños = {
            'pequeñas': {
                'dias': (5, 7),
                'trabajadores': (5, 15),
                'nombre': 'Pequeñas'
            },
            'medianas': {
                'dias': (7, 14),
                'trabajadores': (15, 45),
                'nombre': 'Medianas'
            },
            'grandes': {
                'dias': (14, 28),
                'trabajadores': (45, 90),
                'nombre': 'Grandes'
            }
        }
    
    def generar_demanda_normal(self, num_dias):
        """
        Genera demanda usando distribución Normal.
        
        Parámetros distribucionales justificados:
        - Media: Basada en operaciones típicas por turno
        - Desviación: 20% de la media para variabilidad realista
        """
        demanda = {}
        
        # Parámetros de distribución Normal por turno
        parametros_turnos = {
            'm': {'media': 4.0, 'std': 0.8},  # Mañana: mayor actividad
            't': {'media': 3.0, 'std': 0.6},  # Tarde: actividad media
            'n': {'media': 2.0, 'std': 0.4}   # Noche: menor actividad
        }
        
        for d in range(1, num_dias + 1):
            # Determinar si es fin de semana
            dia_semana = d % 7
            es_fin_semana = (dia_semana == 6 or dia_semana == 0)
            
            for t in self.turnos:
                params = parametros_turnos[t]
                
                # Generar demanda base con distribución Normal
                demanda_base = np.random.normal(params['media'], params['std'])
                
                # Incrementar en fin de semana
                if es_fin_semana:
                    factor = 1.3 if t != 'n' else 1.1
                    demanda_base *= factor
                
                # Asegurar que sea entero positivo ≥ 1
                demanda_final = max(1, int(round(demanda_base)))
                
                demanda[(d, t)] = demanda_final
        
        return demanda
    
    def generar_disposicion_uniforme(self, num_trabajadores, num_dias):
        """
        Genera puntajes de disposición con distribución Uniforme U(0,10).
        
        Justificación: Distribución uniforme asegura que todos los
        niveles de disposición (0 a 10) tengan igual probabilidad.
        """
        puntajes = {}
        
        for p in range(1, num_trabajadores + 1):
            for d in range(1, num_dias + 1):
                for t in self.turnos:
                    # Distribución Uniforme U(0,10)
                    puntaje = random.randint(0, 10)
                    puntajes[(p, d, t)] = puntaje
        
        return puntajes
    
    def generar_instancia_tamaño(self, tamaño, numero_instancia):
        """
        Genera una instancia específica para un tamaño dado.
        """
        config = self.tamaños[tamaño]
        
        # Generar parámetros aleatorios dentro del rango
        num_dias = random.randint(*config['dias'])
        num_trabajadores = random.randint(*config['trabajadores'])
        num_semanas = (num_dias + 6) // 7
        
        print(f"Generando instancia {numero_instancia} - {config['nombre']}: "
              f"{num_trabajadores} trabajadores, {num_dias} días")\
        
        # Generar datos
        demanda = self.generar_demanda_normal(num_dias)
        puntajes = self.generar_disposicion_uniforme(num_trabajadores, num_dias)
        
        # Crear estructura de datos
        instancia = {
            'metadata': {
                'tamaño': config['nombre'],
                'numero_instancia': numero_instancia,
                'num_trabajadores': num_trabajadores,
                'horizonte_dias': num_dias,
                'num_semanas': num_semanas,
                'turnos': self.turnos,
                'semilla_base': self.semilla,
                'fecha_generacion': datetime.now().isoformat(),
                'distribucion_demanda': 'Normal con parámetros por turno',
                'distribucion_disposicion': 'Uniforme U(0,10)'
            },
            'trabajadores': {
                i+1: f"Trabajador_{i+1}" for i in range(num_trabajadores)
            },
            'demanda': {
                f"dia_{d}_turno_{t}": demanda[(d, t)]
                for d in range(1, num_dias + 1)
                for t in self.turnos
            },
            'puntajes_disposicion': {
                f"trabajador_{p}_dia_{d}_turno_{t}": puntajes[(p, d, t)]
                for p in range(1, num_trabajadores + 1)
                for d in range(1, num_dias + 1)
                for t in self.turnos
            }
        }
        
        return instancia
    
    def generar_archivo_minizinc(self, instancia, nombre_archivo):
        """Genera archivo DZN para MiniZinc."""
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            f.write(f"% Instancia {instancia['metadata']['tamaño']} #{instancia['metadata']['numero_instancia']}\n")
            f.write(f"% Generada el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"num_trabajadores = {instancia['metadata']['num_trabajadores']};\n")
            f.write(f"horizonte_dias = {instancia['metadata']['horizonte_dias']};\n")
            f.write(f"num_semanas = {instancia['metadata']['num_semanas']};\n\n")
            
            # Demanda
            f.write("demanda = array2d(1..horizonte_dias, 1..3, [\n")
            for d in range(1, instancia['metadata']['horizonte_dias'] + 1):
                valores = [str(instancia['demanda'][f"dia_{d}_turno_{t}"]) for t in self.turnos]
                f.write(f"  {', '.join(valores)}")
                if d < instancia['metadata']['horizonte_dias']:
                    f.write(",")
                f.write("\n")
            f.write("]);\n\n")
            
            # Puntajes
            f.write("puntajes = array3d(1..num_trabajadores, 1..horizonte_dias, 1..3, [\n")
            for p in range(1, instancia['metadata']['num_trabajadores'] + 1):
                for d in range(1, instancia['metadata']['horizonte_dias'] + 1):
                    valores = [str(instancia['puntajes_disposicion'][f"trabajador_{p}_dia_{d}_turno_{t}"]) for t in self.turnos]
                    f.write(f"  {', '.join(valores)}")
                    if p < instancia['metadata']['num_trabajadores'] or d < instancia['metadata']['horizonte_dias']:
                        f.write(",")
                    f.write("\n")
            f.write("]);\n")
    
    def generar_todas_las_instancias(self, directorio_salida="instancias"):
        """
        Genera las 15 instancias requeridas (5 por cada tamaño).
        """
        if not os.path.exists(directorio_salida):
            os.makedirs(directorio_salida)
        
        resumen = []
        
        for tamaño in ['pequeñas', 'medianas', 'grandes']:
            print(f"\n=== Generando instancias {tamaño.upper()} ===")
            
            for i in range(1, 6):  # 5 instancias por tamaño
                # Usar semilla diferente para cada instancia
                semilla_instancia = self.semilla + (len(resumen))
                random.seed(semilla_instancia)
                np.random.seed(semilla_instancia)
                
                instancia = self.generar_instancia_tamaño(tamaño, i)
                
                # Nombres de archivos
                nombre_base = f"{tamaño}_{i:02d}"
                archivo_json = f"{directorio_salida}/{nombre_base}.json"
                archivo_dzn = f"{directorio_salida}/{nombre_base}.dzn"
                
                # Guardar archivos
                with open(archivo_json, 'w', encoding='utf-8') as f:
                    json.dump(instancia, f, indent=2, ensure_ascii=False)
                
                self.generar_archivo_minizinc(instancia, archivo_dzn)
                
                # Estadísticas para resumen
                stats = {
                    'archivo': nombre_base,
                    'tamaño': tamaño,
                    'trabajadores': instancia['metadata']['num_trabajadores'],
                    'dias': instancia['metadata']['horizonte_dias'],
                    'demanda_total': sum(instancia['demanda'].values()),
                    'disposicion_promedio': np.mean(list(instancia['puntajes_disposicion'].values()))
                }
                resumen.append(stats)
        
        self.generar_resumen(resumen, directorio_salida)
        return resumen
    
    def generar_resumen(self, estadisticas, directorio):
        """Genera un resumen de todas las instancias."""
        with open(f"{directorio}/resumen_instancias.md", 'w', encoding='utf-8') as f:
            f.write("# Resumen de Instancias Generadas\n\n")
            f.write("Generadas según especificaciones del profesor:\n")
            f.write("- 5 instancias por tamaño\n")
            f.write("- Distribución Uniforme U(0,10) para disposición\n")
            f.write("- Distribución Normal para demanda\n\n")
            
            f.write("| Archivo | Tamaño | Trabajadores | Días | Demanda Total | Disposición Promedio |\n")
            f.write("|---------|--------|--------------|------|---------------|---------------------|\n")
            
            for stats in estadisticas:
                f.write(f"| {stats['archivo']} | {stats['tamaño']} | {stats['trabajadores']} | "
                       f"{stats['dias']} | {stats['demanda_total']} | {stats['disposicion_promedio']:.1f} |\n")

def main():
    parser = argparse.ArgumentParser(description='Generador según especificaciones del profesor')
    parser.add_argument('--semilla', type=int, default=42, help='Semilla base')
    parser.add_argument('--directorio', type=str, default='instancias', help='Directorio de salida')
    
    args = parser.parse_args()
    
    generador = GeneradorInstanciasProfesor(semilla=args.semilla)
    estadisticas = generador.generar_todas_las_instancias(args.directorio)
    
    print(f"\n Generadas 15 instancias en directorio: {args.directorio}")
    print(f" Ver resumen en: {args.directorio}/resumen_instancias.md")

if __name__ == "__main__":
    main()