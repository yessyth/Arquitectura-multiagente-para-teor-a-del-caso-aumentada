import re
from agents.base_agent import BaseAgent


class NormativeAgent(BaseAgent):
    def __init__(self):
        super().__init__("agente_normativo", "Identifica normas, reglas y requisitos jurídicos")

    def run(self, fragments: list):
        self.log("extrayendo_normas", {"num_fragments": len(fragments)})
        normas = []
        n_id = 0

        norm_patterns = [
            (r"(?:art[íi]culo|art\.)\s+\d+", "articulo"),
            (r"(?:c[óo]digo|ley|decreto|resoluci[óo]n|ordenanza|acuerdo)\s+\d+", "norma"),
            (r"(?:constituci[óo]n|constituci[óo]n\s+pol[íi]tica)", "constitucion"),
            (r"(?:sentencia|fallo|jurisprudencia|precedente)", "precedente"),
            (r"cl[áa]usula\s+\d+", "clausula"),
            (r"(?:contrato|convenio|pacto)\s+(?:social|de\s+.*?)\b", "contractual"),
        ]

        for frag in fragments:
            text = frag["texto"]
            for pattern, tipo in norm_patterns:
                for m in re.finditer(pattern, text, re.IGNORECASE):
                    n_id += 1
                    context = self._get_context(text, m.start(), m.end())
                    normas.append({
                        "id": f"N{n_id}",
                        "texto": context,
                        "tipo": tipo,
                        "fuente": f"expediente, página {frag['pagina']}",
                        "pagina": frag["pagina"],
                        "fragmento_id": frag["fragment_id"],
                    })

        if not normas:
            normas.append({
                "id": "N1",
                "texto": "Normas generales aplicables al caso (Código Civil / Comercial según corresponda)",
                "tipo": "norma_general",
                "fuente": "inferida del contexto del expediente",
                "pagina": 0,
                "fragmento_id": "rag",
            })

        self.memory["normas"] = normas
        self.log("normas_extraidas", {"normas": len(normas)})
        return normas

    def _get_context(self, text: str, start: int, end: int, window: int = 100) -> str:
        ctx_start = max(0, start - window)
        ctx_end = min(len(text), end + window)
        return text[ctx_start:ctx_end].strip()
