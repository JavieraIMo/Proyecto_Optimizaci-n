# Entrega 2 - Proyecto de Optimización
**Grupo 25 | INF-292 | Noviembre 2025**

---

## 📁 Estructura del Proyecto
```
Entrega_2_GrupoN°25_OPTI/
├── README.md                           # (ACTUALIZADO) Este archivo
├── supuestos_generador.md              # (ACTUALIZADO)Supuestos y observaciones complementarias
├── Modelo_1_Grupo25_OPTI_SJ.pdf        # (ACTUALIZADO)Formulación matemática completa
├── Generador_1_Grupo25_OPTI_SJ.py      # (ACTUALIZADO)Generador de instancias
├── instancia_ejemplo.json              # Instancia de ejemplo (JSON)
├── instancia_ejemplo.dzn               # Instancia de ejemplo (MiniZinc)
├── modelo.mzn                          # modelo para minizinc
└── instancias/                         # Directorio generado al ejecutar
    ├── pequeñas_01.json/.dzn
    ├── pequeñas_02.json/.dzn
    ├── ...
    └── resumen_instancias.md

```

---

## 📋 Item 1: Formulación Matemática

**Archivo:** `Entrega_2_proyecto_Grupo25_OPTI_SJ.pdf`

### Contenido del Modelo

#### Componentes Básicos
- **Conjuntos**: Trabajadores (P), Días (D), Turnos (T), Semanas (W)
- **Parámetros**: 
  - `demanda[d,t]`: Demanda de personal por día-turno
  - `puntajes[p,d,t]`: Disposición del trabajador (puntaje 0-10)
- **Variables**: 
  - `x[p,d,t]`: Asignación binaria (1 si trabaja, 0 si no)
  - `y[p,w]`: Trabajo en fin de semana (1 si trabajó, 0 si no)

#### Función Objetivo
```
Maximizar: Σ puntajes[p,d,t] × x[p,d,t]
           p,d,t
```
**Objetivo:** Maximizar la disposición total del personal asignado

#### Restricciones Principales

|   ID   |          Restricción       |               Descripción                  |
|--------|----------------------------|--------------------------------------------|
| **R1** | Cobertura exacta           | `Σ x[p,d,t] = demanda[d,t]` para todo (d,t)|
| **R2** | Compatibilidad             | `x[p,d,t] = 0` si `puntajes[p,d,t] = 0`    |
| **R3** | Máximo 2 turnos/día        | `Σ x[p,d,t] ≤ 2` para todo (p,d)           |
| **R4** | No noche→mañana            | Prohíbe turno noche seguido de mañana      |
| **R5** | Definición fin de semana   | `y[p,w] = 1` si trabaja sábado o domingo   |
| **R6** | Máx 2 de 3 fines de semana | `y[p,w] + y[p,w+1] + y[p,w+2] ≤ 2`         |

---

## 🔧 Item 2: Generador de Instancias

**Archivo:** `Generador_1_Grupo25_OPTI_SJ.py`

### Cambios para Entrega 2

- El generador **no asegura factibilidad**: la disposición se genera con U(0,10) completamente aleatoria, sin corrección.
- Puede haber días/turnos con menos trabajadores dispuestos que la demanda (instancias infactibles).
- Esto permite analizar el desempeño y robustez del modelo ante casos factibles e infactibles.
- La demanda sigue siendo generada con distribución Normal escalada según el tamaño.
- Se prioriza la diversidad y realismo de los datos generados.

**El resto de la estructura y formatos se mantiene igual.**

### Especificaciones por Tamaño

|    Tamaño    | Días  | Trabajadores |         Turnos       |   Cantidad   |
|--------------|-------|--------------|----------------------|--------------|
| **Pequeñas** | 5-7   | 5-15         | Día, Noche           | 5 instancias |
| **Medianas** | 7-14  | 15-45        | Mañana, Tarde, Noche | 5 instancias |
| **Grandes**  | 14-28 | 45-90        | Mañana, Tarde, Noche | 5 instancias |

### Decisiones de Diseño

#### 1. Distribución Normal para Demanda
```python
Base factor: 25% de trabajadores por turno

Variaciones por turno:
- Día/Mañana: 30% (1.2 × 0.25)
- Tarde:      25% (1.0 × 0.25)
- Noche:      17.5% (0.7 × 0.25)

Fines de semana:
- Día/Tarde: +30% de demanda
- Noche:     +10% de demanda
```

**Justificación:** Refleja patrones reales de operación clínica con mayor demanda diurna y en fines de semana.

#### 2. Distribución Uniforme para Disposición
```python
Puntajes: U(0, 10) completamente aleatoria
- 0:    No puede trabajar
- 1-3:  Baja disposición
- 4-7:  Disposición moderada
- 8-10: Alta disposición
```

**Justificación:** Todos los niveles de disposición tienen igual probabilidad, permitiendo diversidad y casos infactibles.

#### 3. Escalabilidad de Parámetros
```python
Media de demanda ∝ num_trabajadores
Desviación estándar ∝ num_trabajadores
```

Esto mantiene proporciones realistas y diversidad en las instancias generadas.

### Uso del Generador

#### Instalación de dependencias
```bash
pip install numpy
```

#### Generación de las 15 instancias
```bash
# Usar semilla por defecto (42)
python Generador_1_Grupo25_OPTI_SJ.py

# Usar semilla personalizada
python Generador_1_Grupo25_OPTI_SJ.py --semilla 123

# Directorio personalizado
python Generador_1_Grupo25_OPTI_SJ.py --directorio mis_instancias
```

#### Salida generada
```
instancias/
├── pequeñas_01.json      # Datos en formato legible
├── pequeñas_01.dzn       # Datos para MiniZinc
├── pequeñas_02.json
├── pequeñas_02.dzn
├── ...
├── grandes_05.json
├── grandes_05.dzn
└── resumen_instancias.md # Estadísticas de todas las instancias
```

### Ejemplo de Instancia Generada

**Instancia de ejemplo incluida:** `instancia_ejemplo.json`
- **8 trabajadores**, 14 días (2 semanas)
- **136 turnos** de demanda total
- **Demanda promedio:** 3.2 trabajadores/turno
- **Disposición promedio:** 5.0 (escala 0-10)
- **Semilla:** 42 (reproducible)

---

## 📊 Archivos de Salida

### Formato JSON (legible)
```json
{
  "metadata": {
    "tamaño": "Pequeñas",
    "num_trabajadores": 8,
    "horizonte_dias": 7,
    "turnos": ["d", "n"]
  },
  "demanda": {
    "dia_1_turno_d": 3,
    "dia_1_turno_n": 2
  },
  "puntajes_disposicion": {
    "trabajador_1_dia_1_turno_d": 7,
    "trabajador_1_dia_1_turno_n": 0
  }
}
```

### Formato DZN (MiniZinc)
```dzn
num_trabajadores = 8;
horizonte_dias = 7;
num_semanas = 1;
TURNOS = 1..2;

demanda = array2d(1..7, 1..2, [
  3, 2,
  3, 2,
  ...
]);

puntajes = array3d(1..8, 1..7, 1..2, [
  7, 0,
  5, 8,
  ...
]);
```

---

## 📝 Notas Importantes

### Para el Corrector
> ⚠️ **Las instancias NO están pre-generadas en el repositorio.**  
> Ejecute `python Generador_1_Grupo25_OPTI_SJ.py` para crear las 15 instancias.  
> Esto permite verificar la generación desde cero.

### Reproducibilidad
- **Semilla base:** 42
- **Semilla por instancia:** `base + índice_instancia`
- **Misma semilla → mismos datos exactos**

### Compatibilidad
- **Python:** 3.7+
- **Dependencias:** numpy
- **MiniZinc:** Arrays dinámicos según número de turnos

---

## 📝 Nota sobre la extensión del informe

> ⚠️ Debido a la cantidad y profundidad de información solicitada en el enunciado, **no fue posible reducir el informe PDF a 6 páginas incluyendo la portada**. El documento final tiene 8 páginas para cubrir todos los puntos requeridos (modelo, generador, análisis de factibilidad, ejemplos y supuestos).

---

## 🔍 Mejora Opcional Identificada

En la entrega 2, el generador no ajusta disposiciones para asegurar factibilidad. Todas las disposiciones se generan aleatoriamente en U(0,10), permitiendo instancias infactibles y mayor diversidad para análisis.

---

## 📄 Información complementaria

> Para evitar extender el largo del informe principal, información adicional y observaciones empíricas sobre la infactibilidad, el comportamiento de las instancias y detalles de ejecución se encuentran documentadas en `supuestos_generador.md`. Se recomienda revisar ese archivo para un análisis más profundo y ejemplos prácticos.

---

## 📝 Nota sobre entrega de video y foro de consultas

> No se realizó entrega de video junto con esta entrega, ya que **no estaba especificado en el documento oficial de entrega**. Si bien existe una pauta que menciona el video, el PDF que explica la entrega no lo especifica, por lo que se considera aparte de la entrega dos. Se entregará un link de YouTube cuando esté listo, durante la semana de presentaciones, en caso de optar por la modalidad no presencial.

> Además, en el foro de consultas **no se respondieron las preguntas realizadas**, por lo que no se pudo aclarar información adicional sobre los requisitos de la entrega.

> En caso de cualquier problema con descuento de nota por requisitos no explicitados formalmente, se conversará directamente con el profesor para aclarar la situación.