# Entrega 1 - Proyecto INF292
## Octubre 2025

## 📁 Estructura del Proyecto

```
Proyecto_Optimizaci-n/
├── README.md                    # Resumen general de la entrega
├── main.tex                     # Pregunta 1: Formulación matemática
├── generador_instancias.py      # Pregunta 2: Generador en Python  
├── supuestos_generador.md       # Pregunta 2: Explicación de supuestos
├── instancia_ejemplo.json       # Ejemplo de instancia generada
├── instancia_ejemplo.dzn        # Datos para MiniZinc
└── Entrega_1_Proyecto_INF292.pdf # PDF compilado del modelo
```

### Pregunta 1: Formulación del Modelo Matemático ✓

La formulación matemática completa está documentada en `main.tex` e incluye:

- **Conjuntos e índices**: Trabajadores (P), días (D), turnos (T), semanas (W)
- **Parámetros**: Demanda por día-turno, puntajes de disposición
- **Variables**: Asignaciones binarias x_{p,d,t} y variables de fin de semana y_{p,w}
- **Función objetivo**: Maximizar disposición total del personal asignado
- **Restricciones**: 
  - R1: Cobertura de demanda
  - R2: Máximo 2 turnos por día por trabajador
  - R3: Prohibición noche→mañana consecutiva
  - R4: Definición de trabajo en fin de semana
  - R5: No más de 2 fines de semana de cada 3 consecutivos

### Pregunta 2: Generador de Instancias ✓

**Archivos entregados:**
1. `generador_instancias.py` - Script principal en Python
2. `supuestos_generador.md` - Documentación detallada de supuestos
3. `instancia_ejemplo.json` - Instancia de ejemplo generada (original)
4. `instancia_ejemplo.dzn` - Datos para MiniZinc (original)

**Al ejecutar el generador se crean:**
- `instancias/` - Directorio con 15 instancias (5 pequeñas, 5 medianas, 5 grandes)
- Archivos JSON y DZN para cada instancia
- Resumen estadístico en markdown

**Características del generador:**
- Cumple especificaciones exactas del profesor
- Genera 5 instancias por cada tamaño (pequeñas, medianas, grandes)
- Distribución Uniforme U(0,10) para puntajes de disposición
- Distribución Normal para demanda de personal por turno
- Rangos específicos según tabla del profesor
- Semillas reproducibles para cada instancia
- Produce archivos JSON y DZN compatibles con MiniZinc
- Incluye resumen estadístico de todas las instancias

**Supuestos principales:**
- Demanda mayor en fines de semana
- Trabajadores con preferencias de turno individuales
- Factor de cansancio semanal
- Variabilidad aleatoria controlada
- Puntajes en escala 0-10

**Uso del generador:**
```bash
# Generar todas las 15 instancias según especificaciones del profesor
python generador_instancias.py --semilla 42

# Generar en directorio personalizado
python generador_instancias.py --semilla 42 --directorio mis_instancias

# Genera automáticamente:
# - 5 instancias pequeñas (5-15 trabajadores, 5-7 días)
# - 5 instancias medianas (15-45 trabajadores, 7-14 días)  
# - 5 instancias grandes (45-90 trabajadores, 14-28 días)
# - Archivos JSON y DZN para cada instancia
# - Resumen estadístico en markdown
```

**📋 Nota para el profesor:**
> Las instancias NO están pre-generadas. Ejecute el comando anterior para crear las 15 instancias según sus especificaciones. Esto garantiza que puede verificar la generación desde cero.

**Especificaciones técnicas:**
- **Distribuciones**: Uniforme U(0,10) para disposición, Normal para demanda
- **Tamaños**: Según tabla del profesor (pequeñas, medianas, grandes)
- **Replicabilidad**: Semilla base + offset para cada instancia
- **Formatos**: JSON (legible) + DZN (MiniZinc)

**Instancias que se generan al ejecutar:**
- **15 instancias totales** según especificaciones del profesor
- **5 pequeñas**: 5-15 trabajadores, 5-7 días
- **5 medianas**: 15-45 trabajadores, 7-14 días  
- **5 grandes**: 45-90 trabajadores, 14-28 días
- **Distribuciones correctas**: U(0,10) para disposición, Normal para demanda
- **Reproducibles**: Cada instancia tiene semilla específica
- **Documentadas**: Resumen estadístico incluido automáticamente

**Instancia de ejemplo original:**
- 8 trabajadores, 14 días (2 semanas)
- 136 turnos de demanda total
- Demanda promedio: 3.2 trabajadores por turno
- Puntajes de disposición balanceados (promedio 5.0)
- **Generada con semilla 42**: Los datos específicos en `instancia_ejemplo.json` corresponden exactamente a esta semilla

**Importante sobre los archivos de datos:**
- **JSON**: Contiene datos **ya calculados** (resultados finales de la generación)
- **DZN**: Mismos datos en formato MiniZinc (para resolver el problema)
- **Regeneración**: Con la misma semilla obtienes exactamente los mismos números
- **Flexibilidad**: Puedes generar solo en memoria (sin archivos) o guardar para análisis

## 📋 Checklist de Entrega

### ✅ Pregunta 1: Formulación Matemática
- **Archivo**: `main.tex`
- **Contenido**: Modelo completo con conjuntos, parámetros, variables, función objetivo y restricciones
- **Estado**: Completado

### ✅ Pregunta 2: Generador de Instancias  
- **Archivo principal**: `generador_instancias.py`
- **Documentación**: `supuestos_generador.md`
- **Ejemplo funcional**: `instancia_ejemplo.json` + `instancia_ejemplo.dzn`
- **Replicabilidad**: Semillas implementadas y documentadas
- **Estado**: Completado

### Próximos pasos:
- Implementar el modelo en MiniZinc
- Resolver instancias generadas
- Analizar resultados y sensibilidad