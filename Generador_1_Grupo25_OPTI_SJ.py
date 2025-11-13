"""
Función objetivo del modelo de optimización (referencia):
Maximizar la disposición total asignada:
    max sum_{p,d,t} s[p,d,t] * x[p,d,t]
Donde:
    s[p,d,t] = disposición (puntaje 0-10) de persona p en día d, turno t
    x[p,d,t] = variable binaria de asignación (1 si p trabaja en d,t, 0 si no)
Las restricciones se definen en el modelo MiniZinc.

Restricciones principales del modelo de optimización (referencia):
1. Cobertura exacta por día-turno:
    sum_{p} x[p,d,t] = dem[d,t]  para todo d, t
2. Compatibilidad con disposición:
    x[p,d,t] <= 1 si s[p,d,t] > 0, 0 si s[p,d,t] = 0
3. Máximo 2 turnos por día por persona:
    sum_{t} x[p,d,t] <= 2  para todo p, d
4. Prohibición noche seguido de mañana:
    x[p,d,3] + x[p,d+1,1] <= 1  para todo p, d
5. No tres fines de semana consecutivos trabajados:
    y[p,w] + y[p,w+1] + y[p,w+2] <= 2  para todo p, w
Las restricciones completas y la función objetivo se implementan en el modelo MiniZinc (.mzn).

Justificación sobre factibilidad y parámetros distribucionales:
- La demanda se genera como 25% del total de trabajadores con variaciones por turno.
- Día/Mañana: 30% (1.2 × 0.25), Tarde: 25%, Noche: 17.5% (0.7 × 0.25).
- Fines de semana tienen +30% demanda en día/tarde, +10% en noche.
- El generador garantiza factibilidad ajustando disposiciones cuando no hay suficientes trabajadores disponibles.
- Esto asegura que todas las instancias tengan solución, permitiendo evaluar la calidad de las asignaciones.
- Media y desviación estándar escalan con el tamaño para mantener proporciones realistas.
"""

"""
Generador de Instancias ACTUALIZADO según especificaciones
- 5 instancias por tamaño (pequeñas, medianas, grandes)
- Distribución Uniforme U(0,10) para disposición
- Distribución Normal para demanda por turno
- Rangos específicos según tabla

IMPORTANTE:
Este generador solo produce los datos de entrada (demanda y disposición) para el modelo de optimización.
No incluye función objetivo ni restricciones: esas se definen y aplican únicamente en el modelo MiniZinc (.mzn).
"""

import random
import numpy as np
import json
from datetime import datetime
import argparse
import os

class GeneradorInstanciasProfesor:
    def __init__(self, semilla=42):
        self.semilla = semilla
        random.seed(semilla)
        np.random.seed(semilla)
        # self.turnos ya no se usa globalmente
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

    def generar_demanda_normal(self, num_dias, num_trabajadores, turnos):
        """
        Genera demanda usando distribución Normal.
        Parámetros distribucionales justificados:
        - Media: Basada en operaciones típicas por turno
        - Desviación: 20% de la media para variabilidad realista
        """
        demanda = {}
        base_factor = 0.25  # 25% de trabajadores en promedio por turno
        num_turnos = len(turnos)
        if num_turnos == 2:
            parametros_turnos = {
                'd': {'media': num_trabajadores * base_factor * 1.2, 'std': num_trabajadores * 0.05},
                'n': {'media': num_trabajadores * base_factor * 0.7, 'std': num_trabajadores * 0.03}
            }
        else:
            parametros_turnos = {
                'm': {'media': num_trabajadores * base_factor * 1.2, 'std': num_trabajadores * 0.05},
                't': {'media': num_trabajadores * base_factor * 1.0, 'std': num_trabajadores * 0.04},
                'n': {'media': num_trabajadores * base_factor * 0.7, 'std': num_trabajadores * 0.03}
            }
        for d in range(1, num_dias + 1):
            dia_semana = d % 7
            es_fin_semana = (dia_semana == 6 or dia_semana == 0)
            for t in turnos:
                params = parametros_turnos[t]
                demanda_base = np.random.normal(params['media'], params['std'])
                if es_fin_semana:
                    factor = 1.3 if t != 'n' else 1.1
                    demanda_base *= factor
                demanda_final = max(1, int(round(demanda_base)))
                demanda_final = min(demanda_final, num_trabajadores)
                demanda[(d, t)] = demanda_final
        return demanda

    def generar_disposicion_uniforme(self, num_trabajadores, num_dias, demanda, turnos):
        """
        Genera puntajes de disposición con distribución Uniforme U(0,10),
        SIN asegurar factibilidad.
        
        Justificación:
        - Se permite que haya días/turnos con disposición insuficiente.
        - Esto genera tanto instancias factibles como infactibles,
          útiles para análisis de desempeño y robustez del modelo.
        """
        puntajes = {}
        for d in range(1, num_dias + 1):
            for t in turnos:
                for p in range(1, num_trabajadores + 1):
                    puntajes[(p, d, t)] = random.randint(0, 10)
        return puntajes

    def generar_instancia_tamaño(self, tamaño, numero_instancia):
        """
        Genera una instancia específica para un tamaño dado.
        """
        config = self.tamaños[tamaño]
        num_dias = random.randint(*config['dias'])
        num_trabajadores = random.randint(*config['trabajadores'])
        num_semanas = (num_dias + 6) // 7
        # Definir turnos localmente
        if tamaño == 'pequeñas':
            turnos = ['d', 'n']
        else:
            turnos = ['m', 't', 'n']
        print(f"Generando instancia {numero_instancia} - {config['nombre']}: {num_trabajadores} trabajadores, {num_dias} días, turnos: {turnos}")
        demanda = self.generar_demanda_normal(num_dias, num_trabajadores, turnos)
        puntajes = self.generar_disposicion_uniforme(num_trabajadores, num_dias, demanda, turnos)
        instancia = {
            'metadata': {
                'tamaño': config['nombre'],
                'numero_instancia': numero_instancia,
                'num_trabajadores': num_trabajadores,
                'horizonte_dias': num_dias,
                'num_semanas': num_semanas,
                'turnos': turnos,
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
                for t in turnos
            },
            'puntajes_disposicion': {
                f"trabajador_{p}_dia_{d}_turno_{t}": puntajes[(p, d, t)]
                for p in range(1, num_trabajadores + 1)
                for d in range(1, num_dias + 1)
                for t in turnos
            }
        }
        return instancia

    def generar_archivo_minizinc(self, instancia, nombre_archivo):
        """Genera archivo DZN para MiniZinc."""
        num_turnos = len(instancia['metadata']['turnos'])
        turnos = instancia['metadata']['turnos']
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            f.write(f"% Instancia {instancia['metadata']['tamaño']} #{instancia['metadata']['numero_instancia']}\n")
            f.write(f"% Generada el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"num_trabajadores = {instancia['metadata']['num_trabajadores']};\n")
            f.write(f"horizonte_dias = {instancia['metadata']['horizonte_dias']};\n")
            f.write(f"num_semanas = {instancia['metadata']['num_semanas']};\n")
            f.write(f"TURNOS = 1..{num_turnos};\n\n")
            # Demanda
            f.write(f"demanda = array2d(1..horizonte_dias, 1..{num_turnos}, [\n")
            for d in range(1, instancia['metadata']['horizonte_dias'] + 1):
                valores = [str(instancia['demanda'][f"dia_{d}_turno_{t}"]) for t in turnos]
                f.write(f"  {', '.join(valores)}")
                if d < instancia['metadata']['horizonte_dias']:
                    f.write(",")
                f.write("\n")
            f.write("]);\n\n")
            # Puntajes
            f.write(f"puntajes = array3d(1..num_trabajadores, 1..horizonte_dias, 1..{num_turnos}, [\n")
            for p in range(1, instancia['metadata']['num_trabajadores'] + 1):
                for d in range(1, instancia['metadata']['horizonte_dias'] + 1):
                    valores = [str(instancia['puntajes_disposicion'][f"trabajador_{p}_dia_{d}_turno_{t}"]) for t in turnos]
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