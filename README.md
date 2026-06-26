# Teoría del Caso Aumentada - Arquitectura Multiagente

Proyecto integrador del tercer corte - Ciencia de Datos
**Universidad de Pamplona** | Programa Ingeniería de Sistemas | 2026-1

## Descripción

Sistema de arquitectura multiagente que recibe un expediente judicial en PDF,
extrae y estructura la información para producir:

1. **Matriz HPN** (Hecho-Prueba-Norma)
2. **Red compleja multicapa** con nodos y relaciones
3. **Métricas** de cobertura, fragilidad, contradicción y trazabilidad
4. **Simulación de escenarios** procesales (antes/después)
5. **Dashboard** interactivo para el abogado

## Estructura del Proyecto

```
├── src/
│   ├── orchestrator.py          # Orquestador multiagente (punto de entrada)
│   ├── pdf_reader.py            # Ingesta y extracción de PDF
│   ├── schemas.py               # Esquemas de datos (dataclasses)
│   ├── config.py                # Configuración de rutas
│   ├── hpn_matrix.py            # Matriz HPN
│   ├── multilayer_network.py    # Red multicapa con NetworkX
│   ├── metrics_calculator.py    # Cálculo de métricas
│   ├── scenario_simulator.py    # Simulación de escenarios
│   ├── dashboard_app.py         # Dashboard Streamlit
│   └── agents/
│       ├── base_agent.py        # Agente base
│       ├── factual_agent.py     # Agente fáctico-cronológico
│       ├── evidence_agent.py    # Agente probatorio
│       ├── normative_agent.py   # Agente normativo
│       ├── hpn_agent.py         # Agente constructor HPN
│       ├── network_agent.py     # Agente de red multicapa
│       ├── metrics_agent.py     # Agente métrico
│       ├── adversarial_agent.py # Agente adversarial
│       ├── simulator_agent.py   # Agente simulador
│       └── auditor_agent.py     # Agente auditor
├── data/                        # Datos generados (fragments, HPN, red, métricas, escenarios)
│   └── expediente_prueba.pdf    # Expediente de prueba
├── outputs/                     # Reportes exportables
├── requirements.txt             # Dependencias
└── README.md
```

## Requisitos

- Python 3.10+
- Dependencias en `requirements.txt`

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

### 1. Ejecutar el orquestador multiagente

```bash
python src/orchestrator.py data/expediente_prueba.pdf
```

Esto procesa el PDF y genera:
- `data/fragments.jsonl` - Fragmentos del expediente
- `data/hpn_matrix.csv` y `data/hpn_matrix.json` - Matriz HPN
- `data/multilayer_network.json` - Red multicapa
- `data/metrics.json` - Métricas calculadas
- `data/scenarios.json` - Escenarios simulados
- `data/agent_logs.jsonl` - Trazabilidad de agentes

### 2. Iniciar el dashboard

```bash
streamlit run src/dashboard_app.py
```

## Arquitectura Multiagente

| Agente | Función |
|--------|---------|
| **Agente de ingesta** | Extrae texto del PDF, segmenta por páginas |
| **Agente fáctico** | Identifica hechos, actores, fechas y eventos |
| **Agente probatorio** | Detecta pruebas, documentos, testimonios |
| **Agente normativo** | Identifica normas y requisitos jurídicos |
| **Agente HPN** | Construye matriz Hecho-Prueba-Norma |
| **Agente de red** | Transforma en red multicapa |
| **Agente métrico** | Calcula indicadores |
| **Agente adversarial** | Ataca la teoría del caso |
| **Agente simulador** | Simula escenarios procesales |
| **Agente auditor** | Verifica trazabilidad y coherencia |

## Matriz HPN

Columnas: ID, Elemento Jurídico, Hecho, Prueba, Norma, Fuente, Estado, Riesgo,
Contradicciones, Acción Sugerida, Agente, Revisión Humana.

## Red Multicapa

Capas: Hechos, Pruebas, Normas, Actores.
Relaciones: soporta, contradice, activa, fundamenta.

## Escenarios Simulados

1. Exclusión de prueba crítica
2. Activación de excepción procesal
3. Testigo contradictorio
4. Inadmisibilidad documental
5. Precedente distinguido
6. Incorporación de peritaje
7. Límite temporal
8. Escenario de conciliación

## Nota

Este sistema no reemplaza el criterio del abogado. Todas las conclusiones
requieren revisión humana antes de ser utilizadas en litigio.
