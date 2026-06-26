import re


CASE_TYPES = {
    "civil": {
        "label": "Civil",
        "keywords": [
            "contrato", "incumplimiento contractual", "obligacion", "demandante",
            "demandado", "indemnizacion", "clausula penal", "perjuicio",
            "dano emergente", "lucro cesante", "obligacion de pago",
            "cumplimiento", "restitucion", "resolucion del contrato",
            "responsabilidad contractual", "entrega", "plazo",
        ],
        "elementos": [
            "incumplimiento contractual", "obligacion de pago", "plazo de entrega",
            "calidad del servicio", "responsabilidad contractual", "existencia del contrato",
            "causal de excepcion", "pretension principal", "pretension subsidiaria",
            "dano emergente", "lucro cesante", "perjuicio moral",
            "carga de la prueba", "prescripcion de la accion", "caso fortuito",
            "cumplimiento de obligacion", "obligacion de resultado", "restitucion contractual",
        ],
        "normas_base": ["Codigo Civil", "Codigo de Comercio", "Ley 1564 de 2012 (CGP)"],
        "hechos_keywords": [
            "contrat", "oblig", "incumpli", "entreg", "pag", "firm",
            "acord", "suscribi", "establec", "pact", "venci",
            "certific", "notific", "present",
        ],
        "pruebas_tipos": ["contrato", "correo", "factura", "comunicacion", "testimonio", "peritaje"],
        "acciones": {
            "completo": "preservar prueba y preparar alegato",
            "parcial": "buscar prueba complementaria",
            "controvertido": "preparar contraexamen y buscar prueba redundante",
            "vacio_critico": "solicitar prueba por escrito o pedir termino probatorio",
            "debil": "reforzar con prueba adicional o peritaje",
        },
        "excepciones_tipicas": [
            "prescripcion", "caducidad", "cosa juzgada", "transaccion",
            "pago efectivo", "compensacion", "novacion", "remision",
            "falta de legitimacion", "inexistencia de la obligacion",
        ],
        "escenarios": [
            ("Exclusion de prueba documental", "Se retira un documento contractual clave del acervo probatorio"),
            ("Activacion de excepcion contractual", "La contraparte activa una excepcion basada en incumplimiento reciproco"),
            ("Testigo contradictorio en audiencia", "Un testigo presencial contradice la version cronologica de los hechos"),
            ("Inadmisibilidad de peritaje contable", "El dictamen pericial es rechazado por defectos de forma"),
            ("Precedente jurisprudencial adverso", "Se cita un precedente de la Corte que limita la interpretacion contractual"),
            ("Conciliacion extrajudicial", "Las partes muestran disposicion a negociar antes de la audiencia"),
        ],
    },
    "penal": {
        "label": "Penal",
        "keywords": [
            "delito", "hurto", "robo", "homicidio", "lesiones", "estafa",
            "fraude", "violencia", "amenaza", "secuestro", "dosis personal",
            "sustancia", "narcotico", "estupefaciente", "arma", "municion",
            "victima", "imputado", "acusado", "procesado", "sindicado",
            "fiscalia", "juzgado penal", "carcel", "detencion", "captura",
            "indagacion", "investigacion", "causa penal", "tipo penal",
            "tipicidad", "antijuridicidad", "culpabilidad", "dolo", "culpa",
        ],
        "elementos": [
            "tipicidad de la conducta", "antijuridicidad", "culpabilidad",
            "dolo eventual", "culpa consciente", "participacion criminal",
            "autor material", "determinador", "complicidad", "tentativa",
            "consumacion", "circunstancia de agravacion", "circunstancia de atenuacion",
            "causal de justificacion", "causal de inimputabilidad",
            "medida de aseguramiento", "principio de oportunidad",
            "preacuerdo", "reparacion integral",
        ],
        "normas_base": ["Codigo Penal (Ley 599 de 2000)", "Codigo de Procedimiento Penal (Ley 906 de 2004)"],
        "hechos_keywords": [
            "delit", "hurto", "rob", "homicid", "lesion", "estaf",
            "violen", "amenaz", "captur", "detencion", "victim",
            "imput", "acus", "dosif", "sustanci", "narcot",
        ],
        "pruebas_tipos": ["testimonio", "peritaje", "fotografia", "documento", "acta", "audio"],
        "acciones": {
            "completo": "conservar cadena de custodia y preparar alegatos",
            "parcial": "solicitar pruebas complementarias a la Fiscalia",
            "controvertido": "preparar contraexamen de testigos y peritos",
            "vacio_critico": "solicitar termino probatorio o descubrimiento de evidencia",
            "debil": "reforzar con evidencia forense o documental",
        },
        "excepciones_tipicas": [
            "prescripcion de la accion penal", "cosa juzgada", "inimputabilidad",
            "legitima defensa", "estado de necesidad", "cumplimiento de un deber legal",
            "obediencia debida", "error de tipo", "error de prohibicion",
        ],
        "escenarios": [
            ("Exclusion de prueba por cadena de custodia", "Se excluye una evidencia por ruptura de la cadena de custodia"),
            ("Testigo que se retracta", "Un testigo clave se retracta de su declaracion inicial"),
            ("Nuevo peritaje forense", "Un peritaje tecnico contradice la hipotesis de la investigacion"),
            ("Aplicacion del principio de oportunidad", "La Fiscalia evalua aplicar el principio de oportunidad"),
            ("Medida de aseguramiento", "Se discute la imposicion de medida de aseguramiento intramural"),
            ("Preacuerdo con la Fiscalia", "El procesado evalua celebrar un preacuerdo con la Fiscalia"),
        ],
    },
    "laboral": {
        "label": "Laboral",
        "keywords": [
            "contrato de trabajo", "despido", "salario", "prestaciones sociales",
            "cesantias", "primas", "vacaciones", "indemnizacion", "jornada laboral",
            "horas extras", "trabajador", "empleador", "sindicato", "huelga",
            "seguridad social", "pension", "riesgos laborales", "acoso laboral",
            "fuero sindical", "estabilidad laboral", "contrato a termino indefinido",
            "renuncia", "liquidacion", "dotacion", "subordinacion",
        ],
        "elementos": [
            "existencia del contrato laboral", "despido sin justa causa",
            "pago de salarios", "pago de prestaciones sociales",
            "indemnizacion por despido", "acoso laboral",
            "horas extras y recargos", "seguridad social",
            "estabilidad laboral reforzada", "fuero sindical",
            "licencias y permisos", "vacaciones",
        ],
        "normas_base": ["Codigo Sustantivo del Trabajo", "Ley 789 de 2002", "Ley 1010 de 2006 (Acoso Laboral)"],
        "hechos_keywords": [
            "despid", "salario", "labor", "trabaj", "emplead", "empleador",
            "contrat", "cesant", "prima", "vacacion", "indemniz",
            "renunci", "liquid", "pension",
        ],
        "pruebas_tipos": ["contrato", "testimonio", "documento", "correo", "certificacion"],
        "acciones": {
            "completo": "consolidar prueba documental y preparar demanda",
            "parcial": "solicitar historial laboral y certificaciones",
            "controvertido": "preparar contraexamen de testigos de la empresa",
            "vacio_critico": "requerir documentos laborales mediante apostamiento",
            "debil": "buscar testimonios de companeros o registros de asistencia",
        },
        "excepciones_tipicas": [
            "prescripcion", "caducidad", "inexistencia de la obligacion",
            "pago", "compensacion", "falta de legitimacion",
        ],
        "escenarios": [
            ("Expedicion de certificaciones laborales", "La empresa se niega a expedir certificaciones laborales"),
            ("Testimonio de companero de trabajo", "Un companero de trabajo contradice la version del empleado"),
            ("Inspeccion judicial al lugar de trabajo", "El juez ordena inspeccion judicial al centro de trabajo"),
        ],
    },
    "familia": {
        "label": "Familia",
        "keywords": [
            "divorcio", "custodia", "alimentos", "visitas", "regimen de visitas",
            "patria potestad", "hijo", "conyuge", "matrimonio", "separacion",
            "sociedad conyugal", "liquidacion", "violencia intrafamiliar",
            "medida de proteccion", "comisaria de familia", "bienestar familiar",
            "parentesco", "filiacion", "adopcion", "guarda", "menor",
        ],
        "elementos": [
            "causal de divorcio", "custodia y cuidado personal",
            "regimen de visitas", "fijacion de cuota alimentaria",
            "liquidacion de sociedad conyugal", "patria potestad",
            "violencia intrafamiliar", "medida de proteccion",
            "filiacion", "adopcion",
        ],
        "normas_base": ["Codigo Civil", "Ley 1098 de 2006 (Infancia y Adolescencia)", "Ley 294 de 1996"],
        "hechos_keywords": [
            "divorci", "custodi", "alimento", "visita", "matrimoni",
            "separ", "conyug", "hijo", "menor", "violenci",
        ],
        "pruebas_tipos": ["documento", "testimonio", "peritaje", "certificacion", "comunicacion"],
        "acciones": {
            "completo": "preparar demanda con prueba documental completa",
            "parcial": "solicitar entrevista con trabajo social",
            "controvertido": "preparar contraexamen y evaluacion psicologica",
            "vacio_critico": "solicitar valoracion integral por equipo interdisciplinario",
            "debil": "reforzar con testigos y documentacion adicional",
        },
        "excepciones_tipicas": [
            "falta de legitimacion", "cosa juzgada", "transaccion",
        ],
        "escenarios": [
            ("Valoracion psicologica", "Un peritaje psicologico contradice la idoneidad del custodio"),
            ("Entrevista al menor", "El menor manifiesta su opinion ante el juez"),
            ("Incumplimiento de cuota alimentaria", "El obligado incumple el pago de alimentos"),
        ],
    },
}


class CaseTypeDetector:
    def __init__(self, full_text: str):
        self.full_text = full_text
        self.text_lower = full_text.lower()

    def detect(self) -> str:
        scores = {}
        for case_type, config in CASE_TYPES.items():
            score = 0
            for kw in config["keywords"]:
                matches = re.findall(re.escape(kw.lower()), self.text_lower)
                score += len(matches) * 3
            if case_type == "penal":
                penal_boost = len(re.findall(r'\b(?:delito|hurto|victima|fiscalia|carcel|condena|imputado|penal)\b', self.text_lower))
                score += penal_boost * 5
            if case_type == "civil":
                civil_boost = len(re.findall(r'\b(?:contrato|demandante|demandado|obligacion|clausula)\b', self.text_lower))
                score += civil_boost * 3
            if case_type == "laboral":
                laboral_boost = len(re.findall(r'\b(?:trabajador|empleador|despido|salario|cesantias)\b', self.text_lower))
                score += laboral_boost * 5
            if case_type == "familia":
                familia_boost = len(re.findall(r'\b(?:hijo|conyuge|divorcio|alimentos|custodia|menor)\b', self.text_lower))
                score += familia_boost * 5
            scores[case_type] = score

        if max(scores.values()) == 0:
            return "civil"
        best = max(scores, key=scores.get)
        return best

    def get_config(self, case_type: str = None) -> dict:
        if case_type is None:
            case_type = self.detect()
        return CASE_TYPES.get(case_type, CASE_TYPES["civil"])

    def get_label(self, case_type: str = None) -> str:
        if case_type is None:
            case_type = self.detect()
        return CASE_TYPES.get(case_type, CASE_TYPES["civil"])["label"]
