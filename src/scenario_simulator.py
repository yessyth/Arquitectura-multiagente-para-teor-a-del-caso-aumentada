import json
import copy
from config import SCENARIOS_PATH


class ScenarioSimulator:
    def __init__(self, hpn_filas, network, metrics):
        self.hpn_filas_original = hpn_filas
        self.network = network
        self.metrics = metrics
        self.escenarios = []

    def run_all(self):
        self._escenario_exclusion_prueba()
        self._escenario_excepcion()
        self._escenario_testigo_contradictorio()
        self._escenario_inadmisibilidad()
        self._escenario_precedente_distinguido()
        self._escenario_peritaje_agregado()
        self._escenario_limite_temporal()
        self._escenario_conciliacion()
        return self.escenarios

    def _simular(self, id_escenario: str, nombre: str, descripcion: str,
                  supuestos: list, modificaciones: list, acciones: list, confianza: str):
        before = {
            "cobertura_elementos": self.metrics.get("cobertura_elementos_juridicos", 0),
            "cobertura_probatoria": self.metrics.get("cobertura_probatoria", 0),
            "vacios_criticos": self.metrics.get("indice_vacios_criticos", {}).get("cantidad", 0),
            "contradicciones": self.metrics.get("indice_contradiccion", {}).get("cantidad", 0),
        }

        efectos = []
        for mod in modificaciones:
            efectos.append(mod)

        after = dict(before)
        for ef in efectos:
            if "disminuye cobertura" in ef.lower():
                after["cobertura_elementos"] = max(0, after["cobertura_elementos"] - 10)
                after["cobertura_probatoria"] = max(0, after["cobertura_probatoria"] - 15)
                after["vacios_criticos"] += 1
            elif "aumenta cobertura" in ef.lower() or "mejora" in ef.lower():
                after["cobertura_elementos"] = min(100, after["cobertura_elementos"] + 8)
                after["cobertura_probatoria"] = min(100, after["cobertura_probatoria"] + 12)
            elif "contradiccion" in ef.lower() or "testigo" in ef.lower():
                after["contradicciones"] += 1
                after["cobertura_elementos"] = max(0, after["cobertura_elementos"] - 5)

        escenario = {
            "id": id_escenario,
            "nombre": nombre,
            "descripcion": descripcion,
            "supuestos": supuestos,
            "antes": before,
            "despues": after,
            "nodos_afectados": self._nodos_afectados(modificaciones),
            "acciones_sugeridas": acciones,
            "confianza": confianza,
        }
        self.escenarios.append(escenario)
        return escenario

    def _nodos_afectados(self, modificaciones):
        afectados = set()
        for m in modificaciones:
            for f in self.hpn_filas_original:
                for p in f.pruebas:
                    if p.id.lower() in m.lower():
                        afectados.add(p.id)
                        afectados.add(f.hecho.id)
        return list(afectados) if afectados else ["multiple"]

    def _escenario_exclusion_prueba(self):
        self._simular(
            "S1", "Exclusión de prueba crítica",
            "Se retira una prueba crítica del acervo probatorio por inadmisibilidad o falta de cadena de custodia",
            supuestos=[
                "Prueba P1 es declarada inadmisible",
                "El juez excluye la prueba por falta de cadena de custodia",
                "No existe prueba redundante para los hechos H1-H3",
            ],
            modificaciones=[
                "disminuye cobertura probatoria en hechos principales",
                "aumentan vacios criticos",
                "rutas de soporte colapsan",
            ],
            acciones=[
                "Buscar prueba redundante antes de audiencia",
                "Modular afirmaciones sobre hechos que perdieron soporte",
                "Preparar argumento de apelacion si la exclusion es recurrible",
                "Evaluar si la teoria del caso requiere replantearse",
            ],
            confianza="media"
        )

    def _escenario_excepcion(self):
        self._simular(
            "S2", "Activación de excepción procesal",
            "La contraparte activa una excepción de prescripción, caducidad o fuerza mayor",
            supuestos=[
                "Excepcion de prescripcion extintiva es admitida",
                "El plazo para accionar judicialmente habria vencido",
                "Nexo causal entre hechos y pretension se debilita",
            ],
            modificaciones=[
                "disminuye cobertura de elementos juridicos",
                "algunas pretensiones pueden resultar afectadas",
                "rutas argumentativas se debilitan",
            ],
            acciones=[
                "Preparar contraexcepcion basada en actos de interrupcion de prescripcion",
                "Revisar fechas de notificacion y requerimientos",
                "Plantear pretension subsidiaria no afectada por prescripcion",
                "Evaluar viabilidad de conciliacion",
            ],
            confianza="media-baja"
        )

    def _escenario_testigo_contradictorio(self):
        self._simular(
            "S3", "Testigo contradictorio",
            "Un testigo clave de la contraparte contradice la version de los hechos presentada",
            supuestos=[
                "Testigo T1 presenta version incompatible con H2",
                "Documentacion existente no permite corroborar completamente",
                "La contradiccion afecta credibilidad de la teoria",
            ],
            modificaciones=[
                "aumenta indice de contradiccion",
                "disminuye cobertura de elementos en estado completo",
                "hechos controvertidos se incrementan",
            ],
            acciones=[
                "Preparar contraexamen detallado del testigo",
                "Buscar prueba documental que respalde la version propia",
                "Identificar inconsistencias en el testimonio de la contraparte",
                "Evaluar impacto en credibilidad general",
            ],
            confianza="media"
        )

    def _escenario_inadmisibilidad(self):
        self._simular(
            "S4", "Inadmisibilidad documental",
            "Documento clave es marcado como inadmisible por defectos formales",
            supuestos=[
                "Documento D3 no cumple requisitos de presentacion",
                "No se admitio por extemporaneo",
                "Afecta soporte de pretension principal",
            ],
            modificaciones=[
                "disminuye cobertura probatoria",
                "pierde soporte el elemento juridico principal",
                "rutas de soporte colapsan parcialmente",
            ],
            acciones=[
                "Subsanar defectos formales si es posible",
                "Reemplazar con documento alternativo",
                "Replantear estrategia de litigio",
            ],
            confianza="media"
        )

    def _escenario_precedente_distinguido(self):
        self._simular(
            "S5", "Precedente distinguido",
            "El juez distingue el precedente jurisprudencial citado como fundamento",
            supuestos=[
                "Precedente J1 es distinguido por diferencias facticas",
                "Argumento principal pierde soporte jurisprudencial",
                "Necesidad de buscar nueva linea jurisprudencial",
            ],
            modificaciones=[
                "disminuye cobertura normativa",
                "argumentos principales requieren nuevo fundamento",
                "rutas argumentativas se afectan",
            ],
            acciones=[
                "Buscar nueva linea jurisprudencial aplicable",
                "Reforzar argumentacion con doctrina",
                "Diferenciar el caso del precedente distinguido",
                "Preparar argumento alternativo",
            ],
            confianza="media-baja"
        )

    def _escenario_peritaje_agregado(self):
        self._simular(
            "S6", "Incorporacion de peritaje tecnico",
            "Se incorpora una prueba pericial tecnica que favorece la teoria del caso",
            supuestos=[
                "Peritaje tecnico P5 cuantifica el dano reclamado",
                "Prueba pericial es admitida sin objeciones",
                "Refuerza nexo causal y cuantificacion",
            ],
            modificaciones=[
                "mejora cobertura probatoria",
                "aumenta cobertura de elementos juridicos",
                "fortalece rutas de soporte de pretension",
            ],
            acciones=[
                "Incorporar peritaje en alegatos",
                "Preparar contrainterrogatorio a perito de contraparte",
                "Usar peritaje como base de cuantificacion en audiencia",
            ],
            confianza="alta"
        )

    def _escenario_limite_temporal(self):
        self._simular(
            "S7", "Limite temporal - Prescripcion o caducidad",
            "Se activa un limite temporal que afecta la viabilidad de ciertas pretensiones",
            supuestos=[
                "Plazo de prescripcion de accion principal esta por vencer",
                "Actos de interrupcion no estan claramente acreditados",
                "Urgencia de actuacion judicial",
            ],
            modificaciones=[
                "bloquea pretensiones afectadas por prescripcion",
                "aumenta riesgo de perdida de accion",
                "requiere actuacion inmediata",
            ],
            acciones=[
                "Presentar demanda o medida cautelar con caracter urgente",
                "Acreditar actos de interrupcion de prescripcion",
                "Evaluar pretensiones no prescritas como alternativa",
            ],
            confianza="alta"
        )

    def _escenario_conciliacion(self):
        self._simular(
            "S8", "Escenario de conciliacion",
            "Se evaluan costos y riesgos de una posible conciliacion frente al litigio",
            supuestos=[
                "Contraparte muestra disposicion a negociar",
                "Costos procesales pueden superar beneficio esperado",
                "Riesgo de perder en juicio es significativo",
            ],
            modificaciones=[
                "mejora perfil de riesgo general",
                "reduce exposicion a contingencias procesales",
                "acelera resolucion del conflicto",
            ],
            acciones=[
                "Preparar propuesta de conciliacion con rangos negociables",
                "Evaluar costo-beneficio de litigar vs conciliar",
                "Revisar pretensiones minimas aceptables",
                "Presentar alternativa al cliente con escenarios comparativos",
            ],
            confianza="media"
        )

    def save(self):
        with open(SCENARIOS_PATH, "w", encoding="utf-8") as f:
            json.dump(self.escenarios, f, ensure_ascii=False, indent=2)
