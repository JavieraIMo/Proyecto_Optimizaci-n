# Supuestos del Generador de Instancias

## Pregunta 2: Generador de Instancias para el Problema de Asignación de Personal

### Supuestos Generales

El generador de instancias implementado en Python realiza los siguientes supuestos para crear datos realistas del problema de asignación de personal por turnos:

### 1. Estructura Temporal
- **Horizonte de planificación**: Por defecto 14 días (2 semanas), configurable
- **Turnos diarios**: 3 turnos fijos (mañana 'm', tarde 't', noche 'n')
- **Numeración de días**: Comienza en lunes (día 1), donde sábado ≡ 6 (mod 7) y domingo ≡ 0 (mod 7)

### 2. Demanda de Personal

#### Supuestos de Demanda Base:
- **Turno mañana**: 4 trabajadores base (mayor actividad)
- **Turno tarde**: 3 trabajadores base (actividad media)
- **Turno noche**: 2 trabajadores base (menor actividad, vigilancia)

#### Variaciones por Tipo de Día:
- **Fines de semana**: Incremento del 50% en mañana/tarde, 20% en noche
- **Variabilidad aleatoria**: ±1 trabajador por turno para simular demanda variable
- **Mínimo garantizado**: Al menos 1 trabajador por turno

#### Justificación:
Este patrón refleja operaciones típicas donde:
- Los fines de semana requieren más personal por mayor actividad
- Las noches necesitan menos personal (principalmente seguridad/vigilancia)
- Existe variabilidad natural en la demanda diaria

### 3. Puntajes de Disposición

#### Modelo de Preferencias Individuales:
Cada trabajador tiene:
- **Turno preferido**: Asignado aleatoriamente (+2 puntos)
- **Turno menos preferido**: Asignado aleatoriamente (-2 puntos)
- **Nivel base**: Entre 5-8 puntos (trabajador promedio a muy dispuesto)

#### Factores que Afectan la Disposición:

1. **Factor de cansancio semanal**:
   - Reduce disposición gradualmente: 1.0 - (día % 7) × 0.05
   - Simula fatiga acumulada durante la semana

2. **Variabilidad diaria**:
   - ±1 a +2 puntos aleatorios por día
   - Simula factores personales (estado de ánimo, compromisos)

3. **Restricciones de rango**:
   - Puntajes entre 0 y 10 (escala estándar)

#### Justificación:
- **Heterogeneidad realista**: Trabajadores tienen preferencias diferentes
- **Variabilidad temporal**: La disposición cambia día a día
- **Fatiga**: Modelado simplificado de cansancio semanal

### 4. Parámetros de Configuración

#### Valores por Defecto:
- **Número de trabajadores**: 10 (suficiente para cubrir demanda con flexibilidad)
- **Horizonte**: 14 días (2 semanas completas)
- **Semilla aleatoria**: 42 (para reproducibilidad en pruebas)

#### Escalabilidad:
- Todos los parámetros son configurables vía argumentos
- El generador se adapta automáticamente a diferentes tamaños

### 5. Formatos de Salida

#### Archivo JSON:
- Estructura completa con metadatos
- Nombres legibles para trabajadores
- Fácil procesamiento posterior

#### Archivo MiniZinc (.dzn):
- Arrays bidimensionales y tridimensionales
- Indexación desde 1 (convención MiniZinc)
- Comentarios explicativos

### 6. Supuestos Simplificadores

1. **Disponibilidad uniforme**: Todos los trabajadores están disponibles todos los días
2. **Capacidades iguales**: Todos pueden realizar cualquier turno
3. **Sin costos diferenciados**: Solo se considera disposición, no costos monetarios
4. **Sin restricciones individuales**: No se modelan vacaciones, licencias médicas, etc.
5. **Turnos independientes**: No hay tareas que requieran continuidad entre turnos

### 7. Validación de Instancias

El generador incluye:
- **Verificación de factibilidad**: La demanda total no excede la capacidad máxima
- **Estadísticas descriptivas**: Resumen de la instancia generada
- **Reproducibilidad**: Uso de semillas para generar instancias idénticas

### 8. Ejemplo de Uso

```python
# Generar instancia estándar
python generador_instancias.py

# Instancia personalizada
python generador_instancias.py --trabajadores 15 --dias 21 --archivo mi_instancia.json
```

### Conclusión

Estos supuestos crean instancias realistas que:
- Reflejan patrones operacionales típicos
- Mantienen complejidad manejable
- Permiten validar el modelo matemático
- Son escalables a problemas más grandes

El equilibrio entre realismo y simplicidad permite enfocarse en la metodología de optimización sin perderse en detalles operacionales específicos de cada organización.