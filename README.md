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
3. `instancia_ejemplo.json` - Instancia de ejemplo generada
4. `instancia_ejemplo.dzn` - Datos para MiniZinc

**Características del generador:**
- Configurable en número de trabajadores, días y semilla
- Genera demanda realista con variaciones por tipo de día
- Crea puntajes de disposición con preferencias individuales
- Produce archivos compatibles con MiniZinc
- Incluye validación y estadísticas

**Supuestos principales:**
- Demanda mayor en fines de semana
- Trabajadores con preferencias de turno individuales
- Factor de cansancio semanal
- Variabilidad aleatoria controlada
- Puntajes en escala 0-10

**Uso del generador:**
```bash
# Instancia estándar (8 trabajadores, 14 días, semilla por defecto)
python generador_instancias.py --trabajadores 8 --dias 14 --archivo mi_instancia.json

# Con semilla personalizada para replicabilidad
python generador_instancias.py --trabajadores 8 --dias 14 --semilla 42 --archivo mi_instancia.json

# Diferentes semillas generan diferentes instancias
python generador_instancias.py --trabajadores 8 --dias 14 --semilla 123 --archivo instancia_var1.json
python generador_instancias.py --trabajadores 8 --dias 14 --semilla 456 --archivo instancia_var2.json

# Genera automáticamente:
# - mi_instancia.json (datos completos)
# - mi_instancia.dzn (formato MiniZinc)
```

**Replicabilidad con semillas:**
- **Misma semilla = Misma instancia**: Garantiza reproducibilidad exacta de experimentos
- **Semilla por defecto**: 42 (para consistencia en todas las pruebas)
- **Comparación justa**: Permite probar diferentes algoritmos con datos idénticos
- **Debugging**: Reproduce exactamente la misma situación si hay errores

**Instancia de ejemplo generada:**
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