from agents.base_agent import BaseAgent


class AdversarialAgent(BaseAgent):
    def __init__(self):
        super().__init__("agente_adversarial", "Ataca la teoría del caso desde la contraparte o juez crítico")

    def run(self, hpn_filas: list, network, case_config: dict = None):
        self.log("analizando_ataques", {"filas_hpn": len(hpn_filas)})
        ataques = []
        excepciones = (case_config or {}).get("excepciones_tipicas", [])

        for fila in hpn_filas:
            if fila.estado in ("vacio_critico", "debil"):
                ex = excepciones[hash(fila.id) % len(excepciones)] if excepciones else "excepcion aplicable"
                ataques.append({
                    "fila_id": fila.id,
                    "elemento": fila.elemento_juridico,
                    "ataque": f"La contraparte puede cuestionar {fila.elemento_juridico} invocando {ex}. No hay soporte probatorio suficiente.",
                    "tipo": "vacio_probatorio",
                    "severidad": "alta",
                })

            for p in fila.pruebas:
                if p.relacion == "contradice":
                    ataques.append({
                        "fila_id": fila.id,
                        "elemento": fila.elemento_juridico,
                        "ataque": f"La prueba {p.id} ({p.tipo}) contradice la afirmacion sobre {fila.elemento_juridico}",
                        "tipo": "contradiccion",
                        "severidad": "alta",
                    })

            if fila.riesgo in ("alto", "critico"):
                ataques.append({
                    "fila_id": fila.id,
                    "elemento": fila.elemento_juridico,
                    "ataque": f"Alto riesgo en {fila.elemento_juridico}: modular o reforzar antes de audiencia",
                    "tipo": "riesgo",
                    "severidad": "media",
                })

        if not ataques:
            ex = excepciones[0] if excepciones else "excepcion"
            ataques.append({
                "fila_id": "general",
                "elemento": "teoria del caso",
                "ataque": f"Revisar consistencia general. Evaluar si la contraparte puede invocar {ex} como defensa.",
                "tipo": "preventivo",
                "severidad": "baja",
            })

        self.memory["ataques"] = ataques
        self.log("ataques_identificados", {"ataques": len(ataques)})
        return ataques
