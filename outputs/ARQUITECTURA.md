# Documento de Arquitectura
## Sistema Multiagente para Teoría del Caso Aumentada

**Versión:** 1.0
**Fecha:** 26 de junio de 2026
**Asignatura:** Ciencia de Datos - Ingeniería de Sistemas
**Universidad de Pamplona**

---

## 1. Diagrama de Arquitectura

```
                    ┌─────────────────┐
                    │   PDF Entrada   │
                    │  (expediente)   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Agente Ingesta │
                    │  (pdf_reader.py)│
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐     ┌──────────────────┐
                    │ Case Detector   │────▶│ Tipo: Civil/Penal│
                    │ (case_detector) │     │      /Laboral    │
                    └────────┬────────┘     └──────────────────┘
                             │
             ┌───────────────┼───────────────────┐
             │               │                   │
    ┌────────▼──────┐ ┌─────▼───────┐ ┌─────────▼──────┐
    │Agente Fáctico │ │Agente Prob. │ │Agente Normativo│
    │  (hechos,     │ │  (pruebas,  │ │  (normas,      │
    │   actores,    │ │   docum.)   │ │   artículos)   │
    │   fechas)     │ │             │ │                │
    └────────┬──────┘ └─────┬───────┘ └────────┬───────┘
             │              │                  │
             └──────────────┼──────────────────┘
                            │
                    ┌───────▼────────┐
                    │  Agente HPN   │
                    │ (Matriz HPN)  │
                    └───────┬────────┘
                            │
                    ┌───────▼────────┐
                    │  Agente Red   │
                    │ (Red Multicapa)│
                    └───────┬────────┘
                            │
              ┌─────────────┼──────────────┐
              │             │              │
     ┌────────▼─────┐ ┌────▼─────┐ ┌──────▼───────┐
     │Agente Métrico│ │Agente    │ │Agente Simul. │
     │ (16 métricas)│ │Adversarial│ │(8 escenarios)│
     └────────┬─────┘ └────┬─────┘ └──────┬───────┘
              │             │              │
              └─────────────┼──────────────┘
                            │
                    ┌───────▼────────┐
                    │ Agente Auditor │
                    │ (trazabilidad) │
                    └───────┬────────┘
                            │
                    ┌───────▼────────┐
                    │   Dashboard   │
                    │  (Streamlit)   │
                    │  6 pestañas   │
                    └────────────────┘

                            ▲
                            │
                    ┌───────┴────────┐
                    │ Revisión Humana│
                    │  (Abogado)     │
                    └────────────────┘
```

---

## 2. Flujo de Datos

```
PDF ──▶ Fragmentos (JSONL) ──▶ Hechos + Actores + Fechas
                                    │
                          ┌─────────▼─────────┐
                          │  Memoria Compartida │
                          │  (archivos en data/) │
                          └─────────┬─────────┘
                                    │
        ◄── HPN Matrix ── HPN Agent ── Pruebas + Normas
        ◄── Red Multicapa ── Network Agent
        ◄── Métricas ── Metrics Agent
        ◄── Ataques ── Adversarial Agent
        ◄── Escenarios ── Simulator Agent
        ◄── Alertas ── Auditor Agent
```

---

## 3. Agentes - Especificación Detallada

### 3.1 Agente de Ingesta
| Atributo | Descripción |
|----------|-------------|
| **Objetivo** | Extraer texto del PDF, segmentar por páginas |
| **Entrada** | Ruta al archivo PDF |
| **Salida** | `data/fragments.jsonl` (JSONL con página, texto, hash, sección) |
| **Herramientas** | PyMuPDF (fitz) |
| **Memoria** | No persistente |
| **Límites** | Solo PDFs de texto; no procesa imágenes |
| **Criterios de calidad** | Hash SHA-256 por fragmento |

### 3.2 Agente Fáctico-Cronológico
| Atributo | Descripción |
|----------|-------------|
| **Objetivo** | Identificar hechos, actores, fechas y eventos |
| **Entrada** | Fragmentos del expediente + case_config |
| **Salida** | Lista de objetos Hecho + actores + fechas |
| **Herramientas** | Expresiones regulares con vocabulario por tipo de caso |
| **Memoria** | Almacena hechos, actores, fechas |
| **Límites** | Solo detecta hechos con palabras clave del dominio |
| **Criterios de calidad** | Cada hecho debe tener fragmento fuente (página) |

### 3.3 Agente Probatorio
| Atributo | Descripción |
|----------|-------------|
| **Objetivo** | Detectar pruebas, documentos, testimonios |
| **Entrada** | Fragmentos + hechos + case_config |
| **Salida** | Lista de pruebas con tipo, texto, página |
| **Herramientas** | Patrones regex según tipo de caso |
| **Memoria** | Almacena pruebas detectadas |
| **Límites** | No distingue prueba disponible de prueba faltante |
| **Criterios de calidad** | Desduplicación por similitud de texto |

### 3.4 Agente Normativo
| Atributo | Descripción |
|----------|-------------|
| **Objetivo** | Identificar normas, reglas y requisitos jurídicos |
| **Entrada** | Fragmentos + case_config |
| **Salida** | Lista de normas con tipo, texto, fuente |
| **Herramientas** | Patrones regex + normas base por tipo de caso |
| **Memoria** | Almacena normas detectadas |
| **Límites** | No inventa normas; marca si viene del expediente o de RAG |
| **Criterios de calidad** | Desduplicación por contenido |

### 3.5 Agente HPN
| Atributo | Descripción |
|----------|-------------|
| **Objetivo** | Construir matriz Hecho-Prueba-Norma |
| **Entrada** | Hechos, pruebas, normas, actores, case_config |
| **Salida** | `data/hpn_matrix.csv` + `data/hpn_matrix.json` |
| **Herramientas** | pandas, reglas de asignación dinámica |
| **Memoria** | Almacena filas HPN |
| **Límites** | Asignación por página + palabras clave |
| **Criterios de calidad** | Validar cobertura y consistencia de filas |

### 3.6 Agente de Red Multicapa
| Atributo | Descripción |
|----------|-------------|
| **Objetivo** | Transformar matriz y expediente en red multicapa |
| **Entrada** | Filas HPN + actores + pruebas + normas |
| **Salida** | `data/multilayer_network.json` + `data/multilayer_network.graphml` |
| **Herramientas** | NetworkX (MultiDiGraph) |
| **Memoria** | Almacena el grafo |
| **Límites** | Aristas con tipo, dirección, fuente y peso |
| **Criterios de calidad** | Exportación en múltiples formatos |

### 3.7 Agente Métrico
| Atributo | Descripción |
|----------|-------------|
| **Objetivo** | Calcular métricas de matriz y red |
| **Entrada** | Filas HPN + red + texto completo |
| **Salida** | `data/metrics.json` (16 indicadores) |
| **Herramientas** | Cálculos directos sobre datos estructurados |
| **Memoria** | Almacena métricas calculadas |
| **Límites** | Fórmulas transparentes y reproducibles |
| **Criterios de calidad** | Fórmulas documentadas |

### 3.8 Agente Adversarial
| Atributo | Descripción |
|----------|-------------|
| **Objetivo** | Atacar teoría del caso desde la contraparte |
| **Entrada** | Filas HPN + red + case_config |
| **Salida** | Lista de ataques con severidad |
| **Herramientas** | Reglas sobre estados y riesgos de filas HPN |
| **Memoria** | Almacena ataques identificados |
| **Límites** | No inventar ataques sin soporte |
| **Criterios de calidad** | Marcar ataques como hipótesis |

### 3.9 Agente Simulador
| Atributo | Descripción |
|----------|-------------|
| **Objetivo** | Ejecutar escenarios de perturbación |
| **Entrada** | Filas HPN + red + métricas + case_config |
| **Salida** | `data/scenarios.json` |
| **Herramientas** | Reglas de perturbación sobre métricas |
| **Memoria** | Almacena escenarios generados |
| **Límites** | No predecir sentencia; simular efectos estructurales |
| **Criterios de calidad** | Escenarios con supuestos, efectos y acciones |

### 3.10 Agente Auditor
| Atributo | Descripción |
|----------|-------------|
| **Objetivo** | Verificar fuentes, trazabilidad y coherencia |
| **Entrada** | Filas HPN + fragmentos |
| **Salida** | Lista de alertas de auditoría |
| **Herramientas** | Validaciones sobre metadatos de filas |
| **Memoria** | Almacena alertas |
| **Límites** | Debe operar separado del generador |
| **Criterios de calidad** | Detectar duplicados, estado inválido, falta de fuente |

---

## 4. Formatos de Datos

| Artefacto | Formato | Archivo |
|-----------|---------|---------|
| Fragmentos del expediente | JSONL | `data/fragments.jsonl` |
| Matriz HPN | CSV + JSON | `data/hpn_matrix.{csv,json}` |
| Red multicapa | JSON + GraphML | `data/multilayer_network.{json,graphml}` |
| Métricas | JSON | `data/metrics.json` |
| Escenarios | JSON | `data/scenarios.json` |
| Logs de agentes | JSONL | `data/agent_logs.jsonl` |

---

## 5. Criterios de Parada

Cada agente tiene una condición de parada implícita:
- **Inicio**: Cuando el agente recibe su entrada del agente predecesor
- **Fin**: Cuando completa su procesamiento y entrega su salida
- **Error**: Si la entrada está vacía, el agente genera una salida mínima por defecto

---

## 6. Gobernanza

- Todos los agentes registran acciones en `data/agent_logs.jsonl`
- El agente auditor verifica la trazabilidad de forma independiente
- El dashboard muestra alertas y requiere revisión humana
- No hay decisiones automáticas vinculantes

---

## 7. Escalamiento Humano

El sistema está diseñado para aumentar (no reemplazar) al abogado:
- Dashboard con interpretación de métricas
- Preguntas sugeridas para preparación de litigio
- Alertas sobre vacíos y contradicciones
- Declaración explícita de incertidumbre
- Estado de revisión humana en cada fila HPN

---

*Documento generado el 26 de junio de 2026*
*Ciencia de Datos - Ingeniería de Sistemas*
*Universidad de Pamplona*
