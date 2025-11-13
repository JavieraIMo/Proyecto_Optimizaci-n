# Entrega 1 - Proyecto de Optimización
**Grupo 25 | INF-292 | Octubre 2025**

---

## 📁 Estructura del Proyecto
```
Proyecto_Optimizacion/
├── README.md                           # Este archivo
├── Modelo_1_Grupo25_OPTI_SJ.pdf        # Formulación matemática completa
├── Generador_1_Grupo25_OPTI_SJ.py      # Generador de instancias
├── instancia_ejemplo.json              # Instancia de ejemplo (JSON)
├── instancia_ejemplo.dzn               # Instancia de ejemplo (MiniZinc)
└── instancias/                         # Directorio generado al ejecutar
    ├── pequeñas_01.json/.dzn
    ├── pequeñas_02.json/.dzn
    ├── ...
    └── resumen_instancias.md
```

---

## 📋 Item 1: Formulación Matemática

**Archivo:** `Modelo_1_Grupo25_OPTI_SJ.pdf`

### Contenido del Modelo

#### Componentes Básicos
- **Conjuntos**: Trabajadores (P), Días (D), Turnos (T), Semanas (W)
- **Parámetros**: 
  - `dem[d,t]`: Demanda de personal por día-turno
  - `s[p,d,t]`: Disposición del trabajador (puntaje 0-10)
- **Variables**: 
  - `x[p,d,t]`: Asignación binaria (1 si trabaja, 0 si no)
  - `y[p,w]`: Trabajo en fin de semana (1 si trabajó, 0 si no)

#### Función Objetivo
```
Maximizar: Σ s[p,d,t] × x[p,d,t]
           p,d,t
```
**Objetivo:** Maximizar la disposición total del personal asignado

#### Restricciones Principales

|   ID   |          Restricción       |               Descripción                |
|--------|----------------------------|------------------------------------------|
| **R1** | Cobertura exacta           | `Σ x[p,d,t] = dem[d,t]` para todo (d,t)  |
| **R2** | Compatibilidad             | `x[p,d,t] = 0` si `s[p,d,t] = 0`         |
| **R3** | Máximo 2 turnos/día        | `Σ x[p,d,t] ≤ 2` para todo (p,d)         |
| **R4** | No noche→mañana            | Prohíbe turno noche seguido de mañana    |
| **R5** | Definición fin de semana   | `y[p,w] = 1` si trabaja sábado o domingo |
| **R6** | Máx 2 de 3 fines de semana | `y[p,w] + y[p,w+1] + y[p,w+2] ≤ 2`       |

### Garantía de Factibilidad

El modelo garantiza factibilidad mediante:
- Ajuste automático de disposiciones cuando `disponibles < demanda`
- Demanda nunca excede el total de trabajadores
- Todas las instancias generadas son factibles por construcción

---

## 🔧 Item 2: Generador de Instancias

**Archivo:** `Generador_1_Grupo25_OPTI_SJ.py`

### Características del Generador

✅ **5 instancias por tamaño** (15 totales)  
✅ **Distribución Uniforme U(0,10)** para disposición  
✅ **Distribución Normal** para demanda  
✅ **Rangos según especificaciones** del profesor  
✅ **Reproducible** con semillas  
✅ **Formatos JSON + DZN** (MiniZinc)

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
Puntajes: U(0, 10)
- 0:    No puede trabajar
- 1-3:  Baja disposición
- 4-7:  Disposición moderada
- 8-10: Alta disposición
```

**Justificación:** Todos los niveles de disposición tienen igual probabilidad, garantizando diversidad en las preferencias.

#### 3. Escalabilidad de Parámetros
```python
Media de demanda ∝ num_trabajadores
Desviación estándar ∝ num_trabajadores

Esto mantiene proporciones realistas:
- Instancia pequeña (10 trabajadores): ~3 por turno
- Instancia grande (90 trabajadores): ~23 por turno
```

#### 4. Garantía de Factibilidad
```python
Si trabajadores_disponibles < demanda[d,t]:
    # Ajustar disposiciones de 0 → valores positivos
    for trabajador in candidatos_con_cero:
        disposicion[trabajador] = random(1, 10)
```

**Justificación:** Permite evaluar calidad de soluciones sin infactibilidades estructurales.

### Cambios para Entrega 2

A partir de la segunda entrega, el generador **ya no garantiza factibilidad**. Ahora:
- Las disposiciones se generan con distribución Uniforme U(0,10) sin corrección.
- Puede haber días/turnos con menos trabajadores dispuestos que la demanda (instancias infactibles).
- Esto permite analizar el desempeño y robustez del modelo ante casos factibles e infactibles.
- La demanda sigue siendo generada con distribución Normal escalada según el tamaño.

**El resto de la estructura y formatos se mantiene igual.**

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

## ✅ Checklist de Cumplimiento

### Especificaciones del Profesor
- [x] 5 instancias por tamaño (15 totales)
- [x] Distribución Uniforme U(0,10) para disposición
- [x] Distribución Normal para demanda
- [x] Rangos según Tabla 1 del enunciado
- [x] Turnos correctos por tamaño
- [x] Parámetros distribucionales justificados
- [x] Garantía de factibilidad explicada

### Requisitos de Entrega
- [x] Modelo matemático completo (PDF)
- [x] Generador en Python con comentarios
- [x] Archivos .json y .dzn por instancia
- [x] Documentación de supuestos
- [x] Instancias reproducibles (semillas)

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

## 🔍 Mejora Opcional Identificada

En el ajuste de factibilidad, actualmente se generan puntajes altos para trabajadores originalmente no disponibles:
```python
# Actual (válido pero optimista)
puntajes[(p, d, t)] = random.randint(1, 10)

# Alternativa más realista (opcional)
puntajes[(p, d, t)] = random.randint(1, 3)  # Baja disposición forzada
```

**Decisión:** Se mantiene la versión actual (1-10) por ser más neutral y permitir mayor flexibilidad al optimizador.