import re
from agents.base_agent import BaseAgent


class EvidenceAgent(BaseAgent):
    def __init__(self):
        super().__init__("agente_probatorio", "Detecta pruebas, documentos, testimonios, soportes y vacíos")

    def run(self, fragments: list, hechos: list):
        self.log("extrayendo_pruebas", {"num_fragments": len(fragments)})
        pruebas = []
        ev_id = 0

        evidence_keywords = [
            (r"correo[s]?\s+electr[óo]nico[s]?", "correo"),
            (r"contrato[s]?", "contrato"),
            (r"testimonio[s]?", "testimonio"),
            (r"peritaje[s]?|dictamen\s+pericial|perito[s]?", "peritaje"),
            (r"documento[s]?\s+(adjunto|anexo|soporte|probatorio)", "documento"),
            (r"factura[s]?", "factura"),
            (r"comunicaci[oó]n\s+(escrita|interna|oficial)", "comunicacion"),
            (r"audio[s]?|grabaci[oó]n", "audio"),
            (r"fotograf[íi]a[s]?|video[s]?", "fotografia"),
            (r"acta[s]?", "acta"),
            (r"recibo[s]?", "recibo"),
            (r"certificaci[oó]n", "certificacion"),
        ]

        for frag in fragments:
            text = frag["texto"].lower()
            for pattern, tipo in evidence_keywords:
                for m in re.finditer(pattern, text, re.IGNORECASE):
                    ev_id += 1
                    pruebas.append({
                        "id": f"P{ev_id}",
                        "tipo": tipo,
                        "texto": m.group(),
                        "pagina": frag["pagina"],
                        "fragmento_id": frag["fragment_id"],
                        "relacion": "soporta",
                        "fuerza": round(0.5 + (ev_id % 5) * 0.1, 2),
                    })

        vacios = []
        if len(pruebas) < 3:
            vacios.append("Pocas pruebas detectadas en el expediente")
        if len(hechos) > len(pruebas) * 2:
            vacios.append("Hay muchos hechos sin soporte probatorio suficiente")

        self.memory["pruebas"] = pruebas
        self.memory["vacios"] = vacios
        self.log("pruebas_extraidas", {"pruebas": len(pruebas), "vacios": len(vacios)})
        return pruebas, vacios
