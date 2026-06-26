import re
from agents.base_agent import BaseAgent
from schemas import Hecho, Fuente


class FactualAgent(BaseAgent):
    def __init__(self):
        super().__init__("agente_factico", "Identifica hechos, actores, fechas y eventos del expediente")

    def run(self, fragments: list, full_text: str, case_config: dict = None):
        self.log("extrayendo_hechos", {"num_fragments": len(fragments)})
        hechos = []
        actores = set()
        fechas = []

        date_pattern = re.compile(
            r"\b(\d{1,2}\s+de\s+[a-zñ]+\s+de\s+\d{4}|\d{4}/\d{2}/\d{2}|\d{2}-\d{2}-\d{4})\b",
            re.IGNORECASE,
        )
        actor_keywords = [
            "demandante", "demandado", "actor", "parte demandante", "parte demandada",
            "testigo", "perito", "juez", "tribunal", "tercero",
            "victima", "imputado", "acusado", "procesado", "sindicado",
            "fiscal", "trabajador", "empleador", "conyuge", "menor",
        ]

        hecho_keywords = case_config.get("hechos_keywords", [
            "contrat", "oblig", "incumpli", "entreg", "pag", "firm",
            "acord", "suscribi", "establec", "pact", "venci",
        ]) if case_config else [
            "hecho", "ocurri", "sucedi", "aconteci",
        ]

        skip_patterns = [
            r"^INFORME\s+(DE|TÉCNICO|FINAL|PREVIO)",
            r"^EVIDENCIA\s+E-\d+",
            r"^PRUEBA\s+\d+",
            r"^P\d+\s*[:.].*",
            r"^REF-",
            r"^Cas[oó]:",
            r"^Fecha\s+de\s+(suscripción|los\s+hechos)",
            r"^Lugar:",
            r"^Cuant[íi]a",
            r"^Relación\s+de\s+Hechos",
            r"^ANEXO",
            r"^\d+\.\s*$",
            r"^[A-Z\s]{10,}$",
            r"^El contrato se rige",
        ]

        # Actor extraction by role contexts
        role_extractors = [
            (["demandante", "demandado", "parte", "actor", "senor", "senora",
              "empresa", "representante", "jefe", "ingeniero", "director",
              "doctor", "abogado", "licenciado"], "civil"),
            (["victima", "imputado", "acusado", "procesado", "sindicado",
              "fiscal", "testigo", "perito", "ofendido"], "penal"),
            (["trabajador", "empleador", "empleado", "jefe", "supervisor",
              "companero"], "laboral"),
            (["conyuge", "esposo", "esposa", "padre", "madre", "hijo",
              "menor", "custodio"], "familia"),
        ]
        all_roles = list(set(r for roles, _ in role_extractors for r in roles))

        hecho_id = 0
        for frag in fragments:
            text = frag["texto"]
            page = frag["pagina"]
            frag_id = frag["fragment_id"]

            for match in date_pattern.finditer(text):
                fechas.append({"fecha": match.group(), "pagina": page, "fragmento": frag_id})

            for kw in all_roles:
                for m in re.finditer(
                    rf"(?:el|la|los|las|senor|senora|empresa|senorita|la)\s+{kw}\s*[,;:.]?\s*([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*)",
                    text, re.IGNORECASE,
                ):
                    actores.add(m.group(0).strip())

            name_pattern = re.compile(
                r"([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+\s*(?:[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)?)",
            )
            for m in name_pattern.finditer(text):
                name = m.group(1).strip()
                if len(name) > 8 and not any(kw in name.lower() for kw in
                    ["clausula", "articulo", "codigo", "expediente", "juzgado", "corte", "sala",
                     "evidencia", "anexo", "informe"]):
                    context_before = text[max(0, m.start()-40):m.start()].lower()
                    if any(rw in context_before for rw in all_roles):
                        actores.add(f"{name}")

            lines = text.split("\n")
            for line in lines:
                sent = line.strip()
                if len(sent) < 30:
                    continue
                skip = False
                for sp in skip_patterns:
                    if re.match(sp, sent, re.IGNORECASE):
                        skip = True
                        break
                if skip:
                    continue
                if any(kw in sent.lower() for kw in hecho_keywords):
                    hecho_id += 1
                    hechos.append(Hecho(
                        id=f"H{hecho_id}",
                        texto=sent[:250],
                        fuente=Fuente(pagina=page, fragmento_id=frag_id, texto=sent[:250]),
                    ))

            for m in re.finditer(
                r"(PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO|SEXTO)[:.]\s*([A-ZÁÉÍÓÚÑ].*?)(?=(?:PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO|SEXTO|$))",
                text, re.DOTALL,
            ):
                paragraph_text = m.group(2).strip()[:250]
                if len(paragraph_text) > 40:
                    hecho_id += 1
                    hechos.append(Hecho(
                        id=f"H{hecho_id}",
                        texto=paragraph_text[:250],
                        fuente=Fuente(pagina=page, fragmento_id=frag_id, texto=paragraph_text[:250]),
                    ))

        self.memory["hechos"] = hechos
        self.memory["actores"] = list(actores)
        self.memory["fechas"] = fechas
        self.log("hechos_extraidos", {"hechos": len(hechos), "actores": len(actores), "fechas": len(fechas)})
        return hechos, list(actores), fechas
