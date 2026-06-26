import re
from agents.base_agent import BaseAgent
from schemas import Hecho, Fuente


class FactualAgent(BaseAgent):
    def __init__(self):
        super().__init__("agente_factico", "Identifica hechos, actores, fechas y eventos del expediente")

    def run(self, fragments: list, full_text: str):
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
        ]
        hecho_keywords = [
            "hecho", "ocurri", "sucedi", "aconteci", "realiz", "entreg",
            "firm", "acord", "notific", "present", "recibi", "contrat",
            "pag", "incumpli", "suscribi", "oblig", "establec", "pact",
            "venci", "configur", "recibi", "manifest",
        ]

        hecho_id = 0
        for frag in fragments:
            text = frag["texto"]
            page = frag["pagina"]
            frag_id = frag["fragment_id"]

            for match in date_pattern.finditer(text):
                fechas.append({"fecha": match.group(), "pagina": page, "fragmento": frag_id})

            for kw in actor_keywords:
                for m in re.finditer(
                    rf"(?:el|la|los|las|senor|senora|empresa|senorita)\s+{kw}\s*[,;:.]?\s*([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*)",
                    text, re.IGNORECASE,
                ):
                    actores.add(m.group(0).strip())

            name_pattern = re.compile(
                r"([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+\s+(?:[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)?)",
            )
            for m in name_pattern.finditer(text):
                name = m.group(1).strip()
                if len(name) > 8 and not any(kw in name.lower() for kw in
                    ["clausula", "articulo", "codigo", "expediente", "juzgado", "corte", "sala"]):
                    context_before = text[max(0, m.start()-40):m.start()].lower()
                    role_words = ["demandante", "demandado", "testigo", "perito", "senor", "senora",
                                  "parte", "actor", "empresa", "representante", "jefe", "ingeniero"]
                    if any(rw in context_before for rw in role_words):
                        actores.add(f"{name} ({context_before.split()[-1] if context_before.split() else 'desconocido'})")

            sentences = re.split(r'(?<=[.!?])\s+', text)
            for sent in sentences:
                sent = sent.strip()
                if len(sent) > 30 and any(kw in sent.lower() for kw in hecho_keywords):
                    hecho_id += 1
                    hechos.append(Hecho(
                        id=f"H{hecho_id}",
                        texto=sent[:200],
                        fuente=Fuente(pagina=page, fragmento_id=frag_id, texto=sent[:200]),
                    ))

            # Also extract numbered paragraphs as facts
            for m in re.finditer(
                r"(PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO|SEXTO)[:.]\s*([A-ZÁÉÍÓÚÑ].*?)(?=(?:PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO|SEXTO|$))",
                text, re.DOTALL,
            ):
                paragraph_text = m.group(2).strip()[:200]
                if len(paragraph_text) > 30:
                    hecho_id += 1
                    hechos.append(Hecho(
                        id=f"H{hecho_id}",
                        texto=paragraph_text[:200],
                        fuente=Fuente(pagina=page, fragmento_id=frag_id, texto=paragraph_text[:200]),
                    ))

        self.memory["hechos"] = hechos
        self.memory["actores"] = list(actores)
        self.memory["fechas"] = fechas
        self.log("hechos_extraidos", {"hechos": len(hechos), "actores": len(actores), "fechas": len(fechas)})
        return hechos, list(actores), fechas
