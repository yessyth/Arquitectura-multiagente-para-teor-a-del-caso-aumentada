import json
import copy
from config import SCENARIOS_PATH


class ScenarioSimulator:
    def __init__(self, hpn_filas, network, metrics, escenarios_config=None):
        self.hpn_filas_original = hpn_filas
        self.network = network
        self.metrics = metrics
        self.escenarios_config = escenarios_config or []
        self.escenarios = []

    def run_all(self):
        if self.escenarios_config:
            for i, (nombre, desc) in enumerate(self.escenarios_config):
                self._simular(
                    f"S{i+1}", nombre, desc,
                    supuestos=[f"Supuesto base del escenario: {desc}"],
                    acciones=["Revisar impacto en teoria del caso", "Evaluar alternativas estrategicas"],
                )
        else:
            self._escenario_exclusion_prueba()
            self._escenario_excepcion()
            self._escenario_testigo_contradictorio()
            self._escenario_inadmisibilidad()

        n = len(self.escenarios) + 1
        self._escenario_generico(f"S{n}", "Precedente desfavorable",
            "Un precedente jurisprudencial limita la interpretacion juridica del caso",
            ["Revisar jurisprudencia alternativa", "Preparar distincion del precedente"])
        n = len(self.escenarios) + 1
        self._escenario_generico(f"S{n}", "Prueba sobreviniente",
            "Aparece una nueva prueba que modifica el equilibrio del caso",
            ["Incorporar nueva prueba", "Reevaluar matriz HPN"])
        n = len(self.escenarios) + 1
        self._escenario_generico(f"S{n}", "Limite temporal",
            "Se activa un plazo de prescripcion o caducidad que afecta pretensiones",
            ["Verificar fechas clave", "Actuar con caracter urgente"])
        n = len(self.escenarios) + 1
        self._escenario_generico(f"S{n}", "Negociacion o conciliacion",
            "Evaluar escenario de terminacion anticipada del proceso",
            ["Preparar propuesta de acuerdo", "Analizar costos de litigar"])

        return self.escenarios

    def _simular(self, id_escenario, nombre, descripcion,
                  supuestos=None, acciones=None, confianza="media"):
        before = {
            "cobertura_elementos": self.metrics.get("cobertura_elementos_juridicos", 0),
            "cobertura_probatoria": self.metrics.get("cobertura_probatoria", 0),
            "vacios_criticos": self.metrics.get("indice_vacios_criticos", {}).get("cantidad", 0),
            "contradicciones": self.metrics.get("indice_contradiccion", {}).get("cantidad", 0),
        }
        after = {
            "cobertura_elementos": max(0, before["cobertura_elementos"] - 8),
            "cobertura_probatoria": max(0, before["cobertura_probatoria"] - 12),
            "vacios_criticos": before["vacios_criticos"] + 1,
            "contradicciones": before["contradicciones"] + 1,
        }
        escenario = {
            "id": id_escenario,
            "nombre": nombre,
            "descripcion": descripcion,
            "supuestos": supuestos or [],
            "antes": before,
            "despues": after,
            "nodos_afectados": ["multiple"],
            "acciones_sugeridas": acciones or ["Revisar impacto en la estrategia"],
            "confianza": confianza,
        }
        self.escenarios.append(escenario)

    def _escenario_generico(self, id_escenario, nombre, descripcion, acciones):
        self._simular(id_escenario, nombre, descripcion,
                       supuestos=[f"Escenario: {descripcion}"],
                       acciones=acciones)

    def _escenario_exclusion_prueba(self):
        self._simular(
            "S1", "Exclusion de prueba critica",
            "Se retira una prueba del acervo probatorio por inadmisibilidad",
            supuestos=["Prueba principal es declarada inadmisible"],
            acciones=["Buscar prueba redundante", "Evaluar si se requiere replantear teoria del caso"],
        )

    def _escenario_excepcion(self):
        self._simular(
            "S2", "Activacion de excepcion procesal",
            "La contraparte activa una excepcion que afecta la pretension",
            supuestos=["Excepcion de fondo es admitida por el juez"],
            acciones=["Preparar contraexcepcion", "Evaluar impacto en pretensiones"],
        )

    def _escenario_testigo_contradictorio(self):
        self._simular(
            "S3", "Testigo contradictorio",
            "Un testigo presenta version incompatible con los hechos",
            supuestos=["Testigo clave contradice la version de los hechos"],
            acciones=["Preparar contraexamen", "Buscar prueba documental corroborante"],
        )

    def _escenario_inadmisibilidad(self):
        self._simular(
            "S4", "Inadmisibilidad documental",
            "Documento clave es inadmisible por defectos formales",
            supuestos=["Documento no cumple requisitos de presentacion"],
            acciones=["Subsanar defectos si es posible", "Buscar documento alternativo"],
        )

    def save(self):
        with open(SCENARIOS_PATH, "w", encoding="utf-8") as f:
            json.dump(self.escenarios, f, ensure_ascii=False, indent=2)
