"""
Generador de Instancias para el Problema de Asignación de Personal por Turnos
Proyecto INF292 - Entrega 1
Autores: Javiera Ibaca, Sebastían Guzmán, Jorge Ríos
Fecha: Octubre 2025

Este script genera instancias del problema de asignación de personal considerando:
- Trabajadores con diferentes niveles de disposición
- Demanda variable por día y turno
- Horizonte de planificación configurable
"""

import random
import numpy as np
import json
from datetime import datetime, timedelta
import argparse

class GeneradorInstancias:
    def __init__(self, num_trabajadores=10, horizonte_dias=14, semilla=42):
        """
        Inicializa el generador de instancias.
        
        Args:
            num_trabajadores (int): Número de trabajadores disponibles
            horizonte_dias (int): Número de días en el horizonte de planificación
            semilla (int): Semilla para reproducibilidad
        """
        self.P = num_trabajadores  # Conjunto de trabajadores
        self.H = horizonte_dias    # Horizonte en días
        self.W = (horizonte_dias + 6) // 7  # Número de semanas
        self.turnos = ['m', 't', 'n']  # mañana, tarde, noche
        
        # Configurar semilla para reproducibilidad
        random.seed(semilla)
        np.random.seed(semilla)
        
        # Nombres de trabajadores para hacer más realista la instancia
        self.nombres_trabajadores = [
            f"Trabajador_{i+1}" for i in range(num_trabajadores)
        ]
    
    def generar_demanda(self):
        """
        Genera la demanda de personal por día y turno.
        
        Supuestos:
        - Los fines de semana tienen mayor demanda
        - Los turnos de noche tienen menor demanda
        - La demanda varía entre 2 y 6 trabajadores por turno
        """
        demanda = {}
        
        for d in range(1, self.H + 1):
            # Determinar si es fin de semana (sábado=6, domingo=0 en módulo 7)
            dia_semana = d % 7
            es_fin_semana = (dia_semana == 6 or dia_semana == 0)
            
            for t in self.turnos:
                # Demanda base
                if t == 'n':  # noche
                    demanda_base = 2
                elif t == 'm':  # mañana
                    demanda_base = 4
                else:  # tarde
                    demanda_base = 3
                
                # Incrementar demanda en fin de semana
                if es_fin_semana:
                    factor_fin_semana = 1.5 if t != 'n' else 1.2
                    demanda_base = int(demanda_base * factor_fin_semana)
                
                # Añadir variablidad aleatoria
                variacion = random.randint(-1, 1)
                demanda_final = max(1, demanda_base + variacion)
                
                demanda[(d, t)] = demanda_final
        
        return demanda
    
    def generar_puntajes_disposicion(self):
        """
        Genera los puntajes de disposición de cada trabajador para cada día-turno.
        
        Supuestos:
        - Cada trabajador tiene preferencias por ciertos turnos
        - Los puntajes van de 0 a 10
        - Algunos trabajadores prefieren mañanas, otros tardes o noches
        - La disposición puede variar por día (cansancio, compromisos)
        """
        puntajes = {}
        
        # Asignar preferencias básicas a cada trabajador
        preferencias_trabajadores = {}
        for p in range(1, self.P + 1):
            # Cada trabajador tiene un turno preferido y uno menos preferido
            turno_preferido = random.choice(self.turnos)
            turno_menos_preferido = random.choice([t for t in self.turnos if t != turno_preferido])
            
            preferencias_trabajadores[p] = {
                'preferido': turno_preferido,
                'menos_preferido': turno_menos_preferido,
                'nivel_base': random.randint(5, 8)  # Nivel base de disposición
            }
        
        # Generar puntajes para cada combinación trabajador-día-turno
        for p in range(1, self.P + 1):
            pref = preferencias_trabajadores[p]
            
            for d in range(1, self.H + 1):
                # Factor de cansancio (reduce disposición en días consecutivos)
                factor_cansancio = 1.0 - (d % 7) * 0.05
                
                for t in self.turnos:
                    puntaje_base = pref['nivel_base']
                    
                    # Ajustar según preferencias de turno
                    if t == pref['preferido']:
                        puntaje_base += 2
                    elif t == pref['menos_preferido']:
                        puntaje_base -= 2
                    
                    # Aplicar factor de cansancio
                    puntaje_base = int(puntaje_base * factor_cansancio)
                    
                    # Añadir variabilidad aleatoria diaria
                    variacion = random.randint(-1, 2)
                    puntaje_final = max(0, min(10, puntaje_base + variacion))
                    
                    puntajes[(p, d, t)] = puntaje_final
        
        return puntajes
    
    def generar_instancia(self, nombre_archivo=None):
        """
        Genera una instancia completa del problema.
        
        Returns:
            dict: Diccionario con todos los datos de la instancia
        """
        print(f"Generando instancia con {self.P} trabajadores y {self.H} días...")
        
        # Generar todos los componentes
        demanda = self.generar_demanda()
        puntajes = self.generar_puntajes_disposicion()
        
        # Crear estructura de datos completa
        instancia = {
            'metadata': {
                'num_trabajadores': self.P,
                'horizonte_dias': self.H,
                'num_semanas': self.W,
                'turnos': self.turnos,
                'fecha_generacion': datetime.now().isoformat(),
                'descripcion': 'Instancia generada para problema de asignación de personal por turnos'
            },
            'trabajadores': {
                i+1: self.nombres_trabajadores[i] for i in range(self.P)
            },
            'demanda': {
                f"dia_{d}_turno_{t}": demanda[(d, t)]
                for d in range(1, self.H + 1)
                for t in self.turnos
            },
            'puntajes_disposicion': {
                f"trabajador_{p}_dia_{d}_turno_{t}": puntajes[(p, d, t)]
                for p in range(1, self.P + 1)
                for d in range(1, self.H + 1)
                for t in self.turnos
            }
        }
        
        # Guardar archivo si se especifica nombre
        if nombre_archivo:
            with open(nombre_archivo, 'w', encoding='utf-8') as f:
                json.dump(instancia, f, indent=2, ensure_ascii=False)
            print(f"Instancia guardada en: {nombre_archivo}")
        
        return instancia
    
    def generar_archivo_minizinc(self, instancia, nombre_archivo):
        """
        Genera un archivo de datos compatible con MiniZinc.
        
        Args:
            instancia (dict): Instancia generada
            nombre_archivo (str): Nombre del archivo .dzn a crear
        """
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            # Parámetros básicos
            f.write(f"% Archivo de datos para MiniZinc\n")
            f.write(f"% Generado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"num_trabajadores = {self.P};\n")
            f.write(f"horizonte_dias = {self.H};\n")
            f.write(f"num_semanas = {self.W};\n\n")
            
            # Demanda por día y turno
            f.write("% Demanda por día y turno [día, turno]\n")
            f.write("demanda = array2d(1..horizonte_dias, 1..3, [\n")
            for d in range(1, self.H + 1):
                valores = [str(instancia['demanda'][f"dia_{d}_turno_{t}"]) for t in self.turnos]
                f.write(f"  {', '.join(valores)}")
                if d < self.H:
                    f.write(",")
                f.write("\n")
            f.write("]);\n\n")
            
            # Puntajes de disposición
            f.write("% Puntajes de disposición [trabajador, día, turno]\n")
            f.write("puntajes = array3d(1..num_trabajadores, 1..horizonte_dias, 1..3, [\n")
            for p in range(1, self.P + 1):
                for d in range(1, self.H + 1):
                    valores = [str(instancia['puntajes_disposicion'][f"trabajador_{p}_dia_{d}_turno_{t}"]) for t in self.turnos]
                    f.write(f"  {', '.join(valores)}")
                    if p < self.P or d < self.H:
                        f.write(",")
                    f.write("\n")
            f.write("]);\n")
        
        print(f"Archivo MiniZinc guardado en: {nombre_archivo}")
    
    def mostrar_resumen(self, instancia):
        """
        Muestra un resumen estadístico de la instancia generada.
        """
        print("\n" + "="*60)
        print("RESUMEN DE LA INSTANCIA GENERADA")
        print("="*60)
        
        print(f"Trabajadores: {self.P}")
        print(f"Días: {self.H}")
        print(f"Semanas: {self.W}")
        print(f"Turnos por día: {len(self.turnos)} (mañana, tarde, noche)")
        
        # Estadísticas de demanda
        demandas = [v for k, v in instancia['demanda'].items()]
        print(f"\nDemanda total: {sum(demandas)} turnos")
        print(f"Demanda promedio por turno: {np.mean(demandas):.1f}")
        print(f"Demanda mínima: {min(demandas)}")
        print(f"Demanda máxima: {max(demandas)}")
        
        # Estadísticas de puntajes
        puntajes = [v for k, v in instancia['puntajes_disposicion'].items()]
        print(f"\nPuntaje promedio de disposición: {np.mean(puntajes):.1f}")
        print(f"Puntaje mínimo: {min(puntajes)}")
        print(f"Puntaje máximo: {max(puntajes)}")
        
        print("="*60)

def main():
    """Función principal para ejecutar el generador desde línea de comandos."""
    parser = argparse.ArgumentParser(description='Generador de instancias para asignación de personal')
    parser.add_argument('--trabajadores', type=int, default=10, help='Número de trabajadores')
    parser.add_argument('--dias', type=int, default=14, help='Horizonte en días')
    parser.add_argument('--semilla', type=int, default=42, help='Semilla para reproducibilidad')
    parser.add_argument('--archivo', type=str, default='instancia.json', help='Nombre del archivo de salida')
    
    args = parser.parse_args()
    
    # Crear generador
    generador = GeneradorInstancias(
        num_trabajadores=args.trabajadores,
        horizonte_dias=args.dias,
        semilla=args.semilla
    )
    
    # Generar instancia
    instancia = generador.generar_instancia(args.archivo)
    
    # Generar archivo para MiniZinc
    nombre_dzn = args.archivo.replace('.json', '.dzn')
    generador.generar_archivo_minizinc(instancia, nombre_dzn)
    
    # Mostrar resumen
    generador.mostrar_resumen(instancia)

if __name__ == "__main__":
    main()