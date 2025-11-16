# 1. Introducción y Objetivo del Generador

El generador implementado permite crear **instancias variadas, escalables y realistas** para el problema de asignación de personal por turnos. Estas instancias pueden ser utilizadas para:

- Validar el modelo matemático.
- Analizar rendimiento en casos factibles e infactibles.
- Evaluar robustez bajo alta variabilidad.
- Producir datasets reproducibles para pruebas experimentales.

El generador se diseñó de forma que **no garantiza factibilidad**, permitiendo estudiar escenarios complejos donde la demanda excede la disposición.

---

# 2. Detalles de Implementación del Generador

## Lógica de generación de demanda y disposición
- La demanda se genera con distribución Normal, con media y desviación ajustadas según tipo de turno, tamaño de instancia y día de la semana.
- La disposición se genera con distribución Uniforme U(0,10), sin ajustes para asegurar factibilidad.

### Parámetros ejemplo (instancia mediana de 30 trabajadores)
- **Día/Mañana:** media=9, desviación=1.5  
- **Tarde:** media=7.5, desviación=1.2  
- **Noche:** media=5.25, desviación=0.9  

## Estructura de archivos de salida
- **JSON:** metadatos, trabajadores, demanda y disposición.  
- **DZN:** estructuras MiniZinc indexadas desde 1.

## Uso de semillas
- Semilla base: **42**
- Cada instancia = semilla base + índice → total reproducibilidad.

## Funciones principales del script
- `GeneradorInstanciasProfesor`
- `generar_demanda_normal`
- `generar_disposicion_uniforme`
- `generar_instancia_tamaño`
- `generar_archivo_minizinc`
- `generar_todas_las_instancias`

---

# 3. Supuestos Generales y Simplificadores

## 3.1 Supuestos Generales

### Estructura Temporal
- Horizonte configurable (pequeñas, medianas, grandes)
- 2 o 3 turnos diarios según tamaño
- Días numerados desde lunes (1), sábado = 6, domingo = 0 (mod 7)

### Demanda de Personal
- Distribución Normal proporcional al número de trabajadores
- Variabilidad escalada con tamaño
- Fines de semana con demanda más alta
- Mínimo 1 trabajador por turno; máximo = total de trabajadores

### Puntajes de Disposición
- Uniforme U(0,10)
- Independiente por trabajador/día/turno
- No se garantiza factibilidad

### Parámetros por defecto
- Tamaño define número de trabajadores y horizonte
- Semilla: 42

### Formato de salida
- JSON y DZN con indexación clara

## 3.2 Supuestos Simplificadores
1. Todos los trabajadores están disponibles siempre  
2. Capacidades homogéneas  
3. No existen costos monetarios  
4. No hay vacaciones, licencias u otras restricciones personales  
5. Turnos independientes entre sí  

---

# 4. Formatos de Salida y Reproducibilidad

## JSON
Incluye:
- metadatos  
- trabajadores  
- demanda  
- disposición  

## DZN
- Arrays 2D y 3D  
- Indexación desde 1  
- Comentarios explicativos  

## Reproducibilidad
- Semillas constantes
- Instancias idénticas si se repite el proceso bajo los mismos parámetros

---

# 5. Validación de Instancias y Ejemplo de Uso

## Validación
- No se asegura factibilidad
- Se generan estadísticas descriptivas
- Reproducibilidad mediante semillas

## Ejemplo de uso

```python
# Generar instancia estándar
python Generador_1_Grupo25_OPTI_SJ.py

# Instancia personalizada
python Generador_1_Grupo25_OPTI_SJ.py --semilla 123 --directorio mi_instancias
```

---

# 6. Análisis de Resultados y Tiempos de Resolución

## Función objetivo y comportamiento por tamaño
- En instancias pequeñas, la función objetivo tiende a valores bajos por la menor cantidad de trabajadores y turnos.
- En instancias medianas y grandes, la función objetivo puede crecer, pero la alta variabilidad y la infactibilidad pueden limitar el valor máximo alcanzable.
- El generador permite observar cómo el modelo responde ante diferentes niveles de factibilidad y disponibilidad.

## Nota sobre la probabilidad de infactibilidad
- A medida que aumenta el tamaño de la instancia (más días, trabajadores y turnos), la probabilidad de que se generen instancias infactibles **crece exponencialmente**.
- Esto se debe a la mayor aleatoriedad y variabilidad en la disposición y demanda, haciendo más probable que existan días/turnos donde la demanda supere la cantidad de trabajadores disponibles con disposición positiva.

## Observación empírica
- En la práctica, al ejecutar el modelo con instancias medianas y grandes, no se obtuvo ningún resultado factible incluso tras varias horas de cómputo.
- Esto confirma que, debido a la alta aleatoriedad y la mayor cantidad de restricciones, la probabilidad de infactibilidad en instancias grandes es muy elevada.
- El modelo sirve para ilustrar la dificultad real de cubrir la demanda en escenarios complejos y la importancia de analizar la robustez ante la falta de solución.

## Tiempos de resolución
- Instancias pequeñas (5-7 días, 5-15 trabajadores): se resuelven en pocos segundos usando MiniZinc.
- Instancias medianas (7-14 días, 15-45 trabajadores): el tiempo puede aumentar a decenas de segundos o minutos.
- Instancias grandes (14-28 días, 45-90 trabajadores): pueden requerir varios minutos o más, especialmente si hay alta infactibilidad o muchas combinaciones posibles.
- Se recomienda registrar los tiempos de ejecución para cada instancia y comparar el comportamiento según el tamaño y la factibilidad.

---

# 7. Conclusión

El generador permite crear instancias variadas y robustas para el problema de asignación de personal por turnos, facilitando el análisis de desempeño y factibilidad del modelo matemático. La alta variabilidad y la ausencia de garantía de factibilidad reflejan escenarios realistas y complejos, útiles para pruebas experimentales y estudios de robustez. La documentación y estructura permiten reproducibilidad y fácil integración con MiniZinc.
