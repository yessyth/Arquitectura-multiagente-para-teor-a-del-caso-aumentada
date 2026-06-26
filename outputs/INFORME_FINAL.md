# INFORME FINAL
## Arquitectura Multiagente para Teoría del Caso Aumentada

**Ciencia de Datos - Ingeniería de Sistemas**
**Universidad de Pamplona - 2026-1**

---

## 1. Resumen Ejecutivo

Se implementó una arquitectura multiagente que recibe un expediente judicial en PDF,
lo procesa y produce una matriz HPN (Hecho-Prueba-Norma), una red compleja multicapa,
métricas de cobertura y fragilidad, simulación de escenarios procesales y un dashboard
interactivo para el abogado. El sistema detecta automáticamente el tipo de caso
(Civil, Penal, Laboral o Familia) y ajusta sus patrones de extracción en consecuencia.

---

## 2. Descripción del Expediente de Entrada

Se utilizaron tres expedientes de prueba:

| Expediente | Tipo | Páginas | Descripción |
|------------|------|---------|-------------|
| `expediente_prueba.pdf` | Civil | 3 | Incumplimiento de contrato de desarrollo de software |
| `expediente_penal_prueba.pdf` | Penal | 3 | Hurto calificado y suministro de sustancia nociva |
| `expediente_laboral_prueba.pdf` | Laboral | 2 | Despido injusto y prestaciones sociales |

Los PDFs son de texto plano (no escaneados), procesados con PyMuPDF.

---

## 3. Arquitectura Multiagente Implementada

### 3.1 Agentes desarrollados (10)

| # | Agente | Archivo | Función |
|---|--------|---------|---------|
| 1 | Ingesta | `pdf_reader.py` | Extrae texto del PDF, segmenta por páginas |
| 2 | Fáctico-cronológico | `agents/factual_agent.py` | Identifica hechos, actores, fechas |
| 3 | Probatorio | `agents/evidence_agent.py` | Detecta pruebas y documentos |
| 4 | Normativo | `agents/normative_agent.py` | Identifica normas y jurisprudencia |
| 5 | HPN | `agents/hpn_agent.py` | Construye matriz Hecho-Prueba-Norma |
| 6 | Red multicapa | `agents/network_agent.py` | Construye grafo multicapa con NetworkX |
| 7 | Métrico | `agents/metrics_agent.py` | Calcula 16 indicadores |
| 8 | Adversarial | `agents/adversarial_agent.py` | Ataca la teoría del caso |
| 9 | Simulador | `agents/simulator_agent.py` | Simula escenarios procesales |
| 10 | Auditor | `agents/auditor_agent.py` | Verifica trazabilidad y coherencia |

### 3.2 Detector de tipo de caso

Módulo `case_detector.py` que analiza el texto completo del expediente y detecta
el tipo mediante puntuación de palabras clave. Soporta 4 tipos:
- **Civil**: contratos, obligaciones, incumplimientos
- **Penal**: delitos, hurtos, lesiones, estupefacientes
- **Laboral**: despidos, prestaciones sociales, salarios
- **Familia**: divorcio, custodia, alimentos

Cada tipo tiene su propio vocabulario de:
- Elementos jurídicos
- Normas base (Código Penal, CST, etc.)
- Keywords para extracción de hechos
- Tipos de prueba esperados
- Acciones sugeridas
- Excepciones típicas
- Escenarios de simulación

### 3.3 Orquestación

El orquestador (`orchestrator.py`) ejecuta los agentes en secuencia:
1. Ingesta de PDF → 2. Detección de tipo de caso → 3. Extracción fáctica
4. Extracción probatoria → 5. Extracción normativa → 6. Construcción de HPN
7. Construcción de red → 8. Cálculo de métricas → 9. Análisis adversarial
10. Simulación de escenarios → 11. Auditoría

Cada agente registra sus acciones en un archivo JSONL con timestamp, entrada,
salida y herramienta utilizada (trazabilidad completa).

---

## 4. Esquemas de Datos

### 4.1 Fragmentos del expediente (JSONL)
```json
{"fragment_id": "frag-001", "pagina": 1, "texto": "...", "hash": "abc123", "seccion": "hechos"}
```

### 4.2 Matriz HPN (JSON)
```json
{"id": "HPN-001", "elemento_juridico": "incumplimiento contractual",
 "hecho": {"id": "H1", "texto": "...", "fuente": {"pagina": 1, "fragmento_id": "frag-001"}},
 "pruebas": [{"id": "P1", "tipo": "contrato", "relacion": "soporta", "fuerza": 0.7}],
 "normas": [{"id": "N1", "texto": "...", "fuente": "expediente"}],
 "estado": "completo", "riesgo": "bajo",
 "accion_sugerida": "preservar prueba y preparar alegato",
 "agente": "agente_hpn", "revision_humana": "pendiente"}
```

### 4.3 Red multicapa (GraphML + JSON)
Nodos con capa (hecho, prueba, norma, actor) y aristas con tipo (soporta, contradice, activa).

### 4.4 Logs de agentes (JSONL)
```json
{"timestamp": "...", "agente": "agente_factico", "accion": "extrayendo_hechos",
 "entrada": "...", "salida": "...", "herramienta": ""}
```

---

## 5. Matriz HPN Generada

### 5.1 Resultados por tipo de caso

| Métrica | Civil | Penal | Laboral |
|---------|-------|-------|---------|
| Filas generadas | 15 | 14 | 19 |
| Cobertura elementos | 100% | 92.9% | 100% |
| Cobertura probatoria | 100% | 100% | 100% |
| Cobertura normativa | 100% | 100% | 100% |
| Estados completo | 15 | 13 | 19 |
| Estados parcial | 0 | 1 | 0 |
| Riesgo bajo | 15 | 13 | 19 |
| Riesgo medio | 0 | 1 | 0 |

### 5.2 Análisis de calidad
- Cada fila HPN tiene fuente del expediente (página y fragmento)
- Las pruebas se asignan por co-ocurrencia de página y palabras clave
- Los elementos jurídicos se asignan dinámicamente según el contenido
- Las acciones sugeridas varían según el estado epistémico
- Todas las filas requieren revisión humana (revision_humana: "pendiente")

---

## 6. Red Multicapa Generada

### 6.1 Resultados

| Métrica | Civil | Penal | Laboral |
|---------|-------|-------|---------|
| Nodos | 34 | 41 | 50 |
| Aristas | 132 | 163 | 328 |
| Capas | 4 | 4 | 4 |
| Grado promedio | 7.76 | 7.95 | 13.12 |
| Densidad | 0.118 | 0.099 | 0.134 |

### 6.2 Distribución por capas
- **Hechos**: nodos que representan afirmaciones fácticas
- **Pruebas**: documentos, testimonios, peritajes
- **Normas**: artículos, leyes, jurisprudencia
- **Actores**: partes procesales y terceros

### 6.3 Métricas de red calculadas
- Grado del nodo (máximo, mínimo, promedio)
- Densidad de la red
- Distribución por capas
- Rutas de soporte entre nodos

---

## 7. Escenarios Simulados

Se implementaron 8 escenarios procesales:

| ID | Escenario | Qué perturba |
|----|-----------|-------------|
| S1 | Exclusión de prueba crítica | Retira prueba del acervo probatorio |
| S2 | Activación de excepción procesal | Actúa excepción de la contraparte |
| S3 | Testigo contradictorio | Versión incompatible con los hechos |
| S4 | Inadmisibilidad documental | Documento clave rechazado |
| S5 | Precedente desfavorable | Límite jurisprudencial |
| S6 | Prueba sobreviniente | Nueva prueba disponible |
| S7 | Límite temporal | Prescripción o caducidad |
| S8 | Negociación o conciliación | Terminación anticipada |

Cada escenario muestra: supuestos, métricas antes/después, nodos afectados y
acciones sugeridas para el abogado.

---

## 8. Dashboard

### 8.1 Componentes implementados
1. **Vista General**: gráficos de estado/riesgo, métricas clave, fragmentos
2. **Matriz HPN**: tabla filtrable por estado y riesgo
3. **Red Multicapa**: visualización interactiva con Plotly
4. **Métricas**: 16 indicadores organizados por categoría
5. **Simulación**: 8 escenarios con comparación antes/después
6. **Alertas**: vacíos críticos, contradicciones, preguntas sugeridas

### 8.2 Decisiones que permite preparar
- Identificar hechos que pueden afirmarse con fuerza
- Detectar hechos débiles o controvertidos
- Proteger pruebas críticas
- Anticipar excepciones de la contraparte
- Simular escenarios antes de decidir

### 8.3 Declaración de incertidumbre
El dashboard incluye la advertencia explícita:
> "Este sistema no reemplaza el criterio del abogado. Todas las conclusiones
> requieren revisión humana antes de ser utilizadas en litigio."

---

## 9. Limitaciones, Errores e Incertidumbre

### 9.1 Limitaciones conocidas
1. **Sistema basado en reglas**: No usa LLM, por lo que la extracción depende
   de patrones predefinidos. No "entiende" el texto semánticamente.
2. **PDF de texto solamente**: No soporta PDFs escaneados sin OCR.
3. **Idioma específico**: Los patrones están optimizados para español jurídico
   colombiano.
4. **Tipos de caso limitados**: Soporta Civil, Penal, Laboral y Familia.
   Otros tipos (administrativo, constitucional) pueden no detectarse correctamente.

### 9.2 Fuentes de error
- Falsos positivos en extracción de hechos (encabezados detectados como hechos)
- Asignación de pruebas por proximidad de página (no por relación semántica)
- Elementos jurídicos asignados por palabras clave (pueden ser incorrectos si
  el texto usa lenguaje ambiguo)
- Normas detectadas parcialmente (solo las explícitamente mencionadas)

### 9.3 Incertidumbre declarada
- El sistema no predice resultados judiciales
- No sustituye la valoración probatoria profesional
- No presenta sus conclusiones como asesoría jurídica definitiva
- Todas las métricas requieren interpretación humana
- La simulación de escenarios muestra efectos estructurales, no predicciones

### 9.4 Revisión humana requerida
- Toda fila HPN tiene estado de revisión "pendiente"
- El dashboard alerta sobre la necesidad de revisión
- El sistema declara explícitamente que la decisión final es humana

---

## 10. Conclusiones

### 10.1 Utilidad para litigio aumentado
El sistema demuestra que es posible transformar un expediente textual en datos
jurídicamente significativos. La matriz HPN, la red multicapa y las métricas
proporcionan una visión estructurada del caso que permite al abogado:
- Identificar vacíos probatorios antes de la audiencia
- Anticipar ataques de la contraparte
- Simular escenarios para preparar estrategias
- Priorizar acciones de preparación

### 10.2 Cumplimiento de objetivos
- ✅ Arquitectura multiagente con 10 agentes especializados
- ✅ Detección automática de tipo de caso
- ✅ Matriz HPN exportable con trazabilidad
- ✅ Red multicapa con métricas estructurales
- ✅ 8 escenarios procesales simulados
- ✅ Dashboard interactivo con alertas
- ✅ Código reproducible con README y dependencias

### 10.3 Trabajo futuro
- Integrar un LLM local para extracción semántica
- Agregar OCR (Tesseract) para PDFs escaneados
- Exportar informe en PDF desde el dashboard
- Agregar más tipos de caso (administrativo, constitucional)
- Implementar RAG para recuperación de normas no mencionadas

---

*Documento generado el 26 de junio de 2026*
*Ciencia de Datos - Ingeniería de Sistemas*
*Universidad de Pamplona*
