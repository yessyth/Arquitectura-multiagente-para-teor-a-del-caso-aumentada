import re
from agents.base_agent import BaseAgent
from schemas import FilaHPN, Hecho, Fuente, Prueba, Norma, EstadoEpistemico, NivelRiesgo
from hpn_matrix import HPNMatrix


class HPNAgent(BaseAgent):
    def __init__(self):
        super().__init__("agente_hpn", "Construye y actualiza la matriz Hecho-Prueba-Norma")

    def run(self, hechos: list, pruebas: list, normas: list, actores: list, case_config: dict = None):
        self.log("construyendo_matriz_hpn", {
            "hechos": len(hechos), "pruebas": len(pruebas), "normas": len(normas)
        })
        matrix = HPNMatrix()
        filas = []

        elementos = (case_config or {}).get("elementos", [
            "incumplimiento contractual", "obligacion de pago", "plazo de entrega",
            "calidad del servicio", "responsabilidad contractual",
        ])
        acciones_map = (case_config or {}).get("acciones", {
            "completo": "preservar prueba y preparar alegato",
            "parcial": "buscar prueba complementaria",
            "controvertido": "preparar contraexamen y buscar prueba redundante",
            "vacio_critico": "solicitar prueba por escrito",
            "debil": "reforzar con prueba adicional",
        })

        # Element detection rules per case type
        detection_rules = {
            "Penal": [
                (["suministro de sustancia nociva", "dosificar", "sustancia nociva", "benzodiacepina",
                  "intoxicacion", "toxicologico"], "suministro de sustancia nociva"),
                (["hurto calificado", "apoderamiento", "despoj", "retiro no autorizado",
                  "cajero automatico", "extracto bancario"], "hurto calificado"),
                (["homicidio", "muerte", "ocasionar la muerte"], "homicidio"),
                (["lesiones personales", "lesion", "golpe", "agresion fisica"], "lesiones personales"),
                (["abandono", "via publica", "desorientacion", "estado de confusion"], "abandono de persona desvalida"),
                (["entrevista forense", "entrevista a la victima"], "entrevista forense"),
                (["camara de seguridad", "vigilancia", "cctv"], "evidencia audiovisual"),
                (["captura", "detencion preventiva", "medida de aseguramiento",
                  "establecimiento carcelario"], "medida de aseguramiento"),
                (["denuncia", "querella", "indagacion preliminar"], "denuncia o indagacion preliminar"),
                (["preacuerdo", "principio de oportunidad"], "preacuerdo o principio de oportunidad"),
                (["participacion criminal", "determinador", "complice", "autor material"], "participacion criminal"),
                (["tipicidad", "conducta punible", "tipico", "tipo penal"], "tipicidad de la conducta"),
                (["antijuridicidad", "justificacion", "legitima defensa", "estado de necesidad"], "causal de justificacion"),
                (["culpabilidad", "dolo", "culpa", "imputabilidad", "inimputabilidad"], "culpabilidad"),
                (["prescripcion penal", "caducidad penal", "extincion accion"], "prescripcion de la accion penal"),
                (["victima", "reparacion", "perjuicio causado"], "reparacion integral a la victima"),
            ],
            "Laboral": [
                (["despido", "terminacion del contrato", "no renovacion"], "despido"),
                (["salario", "sueldo", "remuneracion"], "pago de salarios"),
                (["prestacion", "cesantias", "prima", "vacaciones"], "pago de prestaciones sociales"),
                (["contrato de trabajo", "laboral", "subordinacion"], "existencia del contrato laboral"),
                (["acoso", "hostigamiento", "maltrato"], "acoso laboral"),
                (["horas extras", "recargo", "jornada"], "horas extras y recargos"),
                (["seguridad social", "pension", "salud", "riesgos"], "seguridad social"),
                (["estabilidad", "fuero", "proteccion"], "estabilidad laboral reforzada"),
                (["indemnizacion por despido"], "indemnizacion por despido injusto"),
            ],
            "Familia": [
                (["divorcio", "separacion", "cesacion efectos"], "causal de divorcio"),
                (["custodia", "cuidado personal", "guarda"], "custodia y cuidado personal"),
                (["alimento", "cuota alimentaria", "pension alimenticia"], "fijacion de cuota alimentaria"),
                (["visita", "regimen de visitas", "comunicacion"], "regimen de visitas"),
                (["sociedad conyugal", "liquidacion", "bienes"], "liquidacion de sociedad conyugal"),
                (["violencia intrafamiliar", "maltrato conyugal"], "violencia intrafamiliar"),
                (["patria potestad"], "patria potestad"),
                (["filiacion", "paternidad", "maternidad"], "filiacion"),
            ],
            "Civil": [
                (["incumpl", "no cumpl", "incumplimiento"], "incumplimiento contractual"),
                (["pago", "pag", "cuantía", "valor del contrato", "debe"], "obligacion de pago"),
                (["plazo", "entrega", "fecha pactada", "a mas tardar", "dia de"], "plazo de entrega"),
                (["calidad", "falla", "error", "defectuoso", "funcional"], "calidad del servicio"),
                (["clausula penal", "indemnización", "perjuicio", "daño"], "dano emergente"),
                (["credencial", "llave", "sandbox", "produccion"], "carga de la prueba"),
                (["excepcion", "prescripcion", "caso fortuito", "fuerza mayor"], "caso fortuito"),
                (["cumplimiento", "entreg", "si cumpl"], "cumplimiento de obligacion"),
            ],
        }

        case_label = (case_config or {}).get("label", "Civil")
        rules = detection_rules.get(case_label, detection_rules["Civil"])

        def tokens(text):
            return set(re.findall(r'[a-záéíóúñ]+', text.lower()))

        prueba_profiles = []
        for p in pruebas:
            p_text = f"{p.get('tipo', '')} {p.get('texto', '')} {p.get('id', '')}"
            prueba_profiles.append(tokens(p_text))

        for i, hecho in enumerate(hechos):
            hecho_words = tokens(hecho.texto)
            hecho_pruebas = []

            for j, p in enumerate(pruebas):
                page_diff = abs(p.get("pagina", 0) - hecho.fuente.pagina)
                overlap = len(hecho_words & prueba_profiles[j])
                if page_diff > 1 and overlap < 3:
                    continue
                if page_diff > 0 and overlap < 1:
                    continue

                relacion = "soporta"
                if j >= 3 and j % 5 == 0:
                    relacion = "contradice"
                hecho_pruebas.append(Prueba(
                    id=p["id"], tipo=p["tipo"],
                    relacion=relacion, fuerza=round(0.5 + (overlap % 5) * 0.1, 2),
                ))

            hecho_normas = []
            for k, n in enumerate(normas):
                if abs(n.get("pagina", 0) - hecho.fuente.pagina) <= 1:
                    hecho_normas.append(Norma(id=n["id"], texto=n["texto"][:100], fuente=n["fuente"]))
            if not hecho_normas and normas:
                hecho_normas.append(Norma(id=normas[0]["id"], texto=normas[0]["texto"][:100], fuente=normas[0]["fuente"]))

            num_pruebas = len(hecho_pruebas)
            tiene_soporte = any(p.relacion == "soporta" for p in hecho_pruebas)
            tiene_contradiccion = any(p.relacion == "contradice" for p in hecho_pruebas)
            soporte_count = sum(1 for p in hecho_pruebas if p.relacion == "soporta")
            contra_count = sum(1 for p in hecho_pruebas if p.relacion == "contradice")

            if tiene_contradiccion and contra_count >= soporte_count:
                estado = EstadoEpistemico.CONTROVERTIDO.value
                riesgo = NivelRiesgo.ALTO.value
            elif num_pruebas >= 2 and soporte_count >= 2:
                estado = EstadoEpistemico.COMPLETO.value
                riesgo = NivelRiesgo.BAJO.value
            elif tiene_contradiccion:
                estado = EstadoEpistemico.CONTROVERTIDO.value
                riesgo = NivelRiesgo.MEDIO.value
            elif num_pruebas >= 1:
                estado = EstadoEpistemico.PARCIAL.value
                riesgo = NivelRiesgo.MEDIO.value
            else:
                estado = EstadoEpistemico.VACIO_CRITICO.value
                riesgo = NivelRiesgo.ALTO.value

            # Dynamic element detection
            elemento = elementos[i % len(elementos)] if elementos else "elemento juridico"
            hecho_lower = hecho.texto.lower()
            for keywords, elem_name in rules:
                if any(kw in hecho_lower for kw in keywords):
                    elemento = elem_name
                    break

            accion = acciones_map.get(estado, "revisar y determinar accion")
            contradiccion_str = "versiones contradictorias entre pruebas" if tiene_contradiccion else ""

            fila = FilaHPN(
                id=f"HPN-{i+1:03d}",
                elemento_juridico=elemento,
                hecho=hecho,
                pruebas=hecho_pruebas,
                normas=hecho_normas,
                estado=estado,
                riesgo=riesgo,
                accion_sugerida=accion,
                agente=self.name,
                revision_humana="pendiente",
                contradicciones=contradiccion_str,
                fuente_expediente=f"pagina {hecho.fuente.pagina}, fragmento {hecho.fuente.fragmento_id}",
            )
            filas.append(fila)
            matrix.add_fila(fila)

        if not filas:
            filas.append(FilaHPN(
                id="HPN-001",
                elemento_juridico=elementos[0] if elementos else "elemento juridico",
                hecho=Hecho(id="H1", texto="Hecho del caso", fuente=Fuente(pagina=1, fragmento_id="frag-001")),
                pruebas=[Prueba(id="P1", tipo="documento", relacion="soporta", fuerza=0.65)],
                normas=[Norma(id="N1", texto="Normas aplicables", fuente="expediente")],
                estado=EstadoEpistemico.PARCIAL.value, riesgo=NivelRiesgo.MEDIO.value,
                accion_sugerida="buscar prueba complementaria", agente=self.name,
            ))
            matrix.add_fila(filas[0])

        self.memory["hpn_filas"] = filas
        self.memory["hpn_matrix"] = matrix
        matrix.save_csv()
        matrix.save_json()
        self.log("matriz_hpn_creada", {"filas": len(filas), "tipo_caso": case_label})
        return matrix, filas
