import re
from agents.base_agent import BaseAgent


class NormativeAgent(BaseAgent):
    def __init__(self):
        super().__init__("agente_normativo", "Identifica normas, reglas y requisitos jurídicos")

    def run(self, fragments: list, case_config: dict = None):
        self.log("extrayendo_normas", {"num_fragments": len(fragments)})
        normas = []
        n_id = 0

        if case_config:
            normas_base = case_config.get("normas_base", [])
            for nb in normas_base:
                n_id += 1
                normas.append({
                    "id": f"N{n_id}",
                    "texto": nb,
                    "tipo": "norma_base",
                    "fuente": "normatividad aplicable segun tipo de caso",
                    "pagina": 0,
                    "fragmento_id": "rag",
                })

        norm_patterns = [
            (r"(?:art[íi]cul[oa]s?|art\.)\s+[\d\s,]+", "articulo"),
            (r"(?:c[óo]digo|ley|decreto|resoluci[óo]n|ordenanza|acuerdo)\s+[\wÁÉÍÓÚÑáéíóúñ]+", "norma"),
            (r"(?:constituci[óo]n|constituci[óo]n\s+pol[íi]tica)", "constitucion"),
            (r"(?:sentencia|fallo|jurisprudencia|precedente)\s*(?:SC-|C-|T-|SU-)?[\w-]*", "precedente"),
            (r"cl[áa]usula\s+\d+", "clausula"),
            (r"r[ée]gimen\s+(?:jur[íi]dico|legal|contractual|de\s+obligaciones|pensional)", "regimen"),
        ]

        seen_norms = set()
        for frag in fragments:
            text = frag["texto"]
            for pattern, tipo in norm_patterns:
                for m in re.finditer(pattern, text, re.IGNORECASE):
                    ctx_start = max(0, m.start() - 80)
                    ctx_end = min(len(text), m.end() + 150)
                    context = text[ctx_start:ctx_end].strip()

                    dedup_key = context[:100].lower()
                    if dedup_key in seen_norms:
                        continue
                    seen_norms.add(dedup_key)

                    n_id += 1
                    normas.append({
                        "id": f"N{n_id}",
                        "texto": context[:200],
                        "tipo": tipo,
                        "fuente": f"expediente, página {frag['pagina']}",
                        "pagina": frag["pagina"],
                        "fragmento_id": frag["fragment_id"],
                    })

        if not normas:
            n_id += 1
            normas.append({
                "id": f"N{n_id}",
                "texto": "Normas generales aplicables al caso segun la legislacion colombiana",
                "tipo": "norma_general",
                "fuente": "inferida del contexto del expediente",
                "pagina": 0,
                "fragmento_id": "rag",
            })

        self.memory["normas"] = normas
        self.log("normas_extraidas", {"normas": len(normas)})
        return normas
