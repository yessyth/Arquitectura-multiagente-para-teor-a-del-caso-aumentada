import re
from agents.base_agent import BaseAgent


class EvidenceAgent(BaseAgent):
    def __init__(self):
        super().__init__("agente_probatorio", "Detecta pruebas, documentos, testimonios, soportes y vacíos")

    def run(self, fragments: list, hechos: list, case_config: dict = None):
        self.log("extrayendo_pruebas", {"num_fragments": len(fragments)})
        pruebas = []
        ev_id = 0

        tipos_esperados = case_config.get("pruebas_tipos", [
            "contrato", "correo", "testimonio", "factura", "documento", "peritaje",
        ]) if case_config else []

        evidence_rules = {
            "civil": [
                (r"contrato[s]?\s+(?:de\s+)?(?:prestacion|compraventa|arrendamiento|suscrito)", "contrato"),
                (r"correo[s]?\s+electr[oó]nico[s]?", "correo"),
                (r"testimonio[s]?\s*(?:de|juramentado|bajo|rendido)", "testimonio"),
                (r"peritaje[s]?|dictamen\s+pericial", "peritaje"),
                (r"factura[s]?", "factura"),
                (r"comunicaci[oó]n\s+(?:escrita|interna|oficial)", "comunicacion"),
                (r"documento[s]?\s+(?:adjunto|anexo|soporte|probatorio|privado|publico)", "documento"),
                (r"acta[s]?\s+de\s+(?:entrega|conciliacion|acuerdo)", "acta"),
                (r"comprobante[s]?\s+de\s+pago|recibo[s]?", "comprobante"),
                (r"certificaci[oó]n\s+(?:bancaria|de\s+existencia)", "certificacion"),
            ],
            "penal": [
                (r"testimonio[s]?\s*(?:de|juramentado|bajo|rendido)", "testimonio"),
                (r"peritaje[s]?|dictamen\s+(?:pericial|medico|legal)", "peritaje"),
                (r"fotograf[íi]a[s]?|video[s]?|grabaci[oó]n|audio", "audiovisual"),
                (r"acta[s]?\s+de\s+(?:inspeccion|levantamiento|registro)", "acta"),
                (r"cadena\s+de\s+custodia|informe\s+de\s+pol[ií]cia", "evidencia_forense"),
                (r"analisis\s+(?:de\s+)?(?:ADN|gen[eé]tico|bal[ií]stico|qu[ií]mico)", "peritaje_forense"),
                (r"documento[s]?\s+(?:privado|publico|autenticado)", "documento"),
                (r"correo[s]?\s+electr[oó]nico[s]?", "correo"),
            ],
            "laboral": [
                (r"contrato\s+de\s+trabajo", "contrato"),
                (r"certificaci[oó]n\s+(?:laboral|de\s+trabajo)", "certificacion"),
                (r"despido|carta\s+de\s+terminaci[oó]n", "comunicacion"),
                (r"testimonio[s]?\s*(?:de|juramentado)", "testimonio"),
                (r"correo[s]?\s+electr[oó]nico[s]?", "correo"),
                (r"documento[s]?", "documento"),
            ],
            "familia": [
                (r"testimonio[s]?\s*(?:de|juramentado)", "testimonio"),
                (r"peritaje\s+(?:psicol[oó]gico|social|familiar)", "peritaje"),
                (r"certificaci[oó]n\s+(?:m[eé]dica|de\s+ingresos|de\s+estudio)", "certificacion"),
                (r"documento[s]?", "documento"),
                (r"correo[s]?\s+electr[oó]nico[s]?", "correo"),
                (r"acta[s]?\s+de\s+(?:conciliacion|acuerdo)", "acta"),
            ],
        }

        case_type = "civil"
        if case_config:
            for ct, cfg in [("penal", None), ("laboral", None), ("familia", None)]:
                if case_config.get("label", "").lower() == ct:
                    case_type = ct
                    break

        patterns = evidence_rules.get(case_type, evidence_rules.get("penal", [])) + [
            (r"evidencia\s+[Ee]-?\d+|prueba\s+\d+\s*:", "evidencia_documental"),
            (r"log\s+(del\s+)?repositorio|registro\s+de\s+commits", "registro"),
        ]

        for frag in fragments:
            text = frag["texto"]
            for pattern, tipo in patterns:
                for m in re.finditer(pattern, text, re.IGNORECASE):
                    ev_id += 1
                    ctx_start = max(0, m.start() - 30)
                    ctx_end = min(len(text), m.end() + 60)
                    context = text[ctx_start:ctx_end].strip()
                    pruebas.append({
                        "id": f"P{ev_id}",
                        "tipo": tipo,
                        "texto": context[:200],
                        "pagina": frag["pagina"],
                        "fragmento_id": frag["fragment_id"],
                        "relacion": "soporta",
                        "fuerza": round(0.5 + (ev_id % 5) * 0.1, 2),
                    })

        seen_texts = set()
        deduped = []
        for p in pruebas:
            key = p["texto"][:80]
            if key not in seen_texts:
                seen_texts.add(key)
                deduped.append(p)
        pruebas = deduped

        vacios = []
        if len(pruebas) < 2:
            vacios.append("Pocas pruebas detectadas en el expediente")
        if len(hechos) > len(pruebas) * 1.5:
            vacios.append("Hay muchos hechos sin soporte probatorio suficiente")

        self.memory["pruebas"] = pruebas
        self.memory["vacios"] = vacios
        self.log("pruebas_extraidas", {"pruebas": len(pruebas), "vacios": len(vacios)})
        return pruebas, vacios
