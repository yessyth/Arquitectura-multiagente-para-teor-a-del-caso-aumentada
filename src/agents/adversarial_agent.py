from agents.base_agent import BaseAgent


class AdversarialAgent(BaseAgent):
    def __init__(self):
        super().__init__("agente_adversarial", "Ataca la teoría del caso desde la contraparte o juez crítico")

    def run(self, hpn_filas: list, network):
        self.log("analizando_ataques", {"filas_hpn": len(hpn_filas)})
        ataques = []

        for fila in hpn_filas:
            # Identificar filas vulnerables
            if fila.estado in ("vacio_critico", "debil"):
                ataques.append({
                    "fila_id": fila.id,
                    "elemento": fila.elemento_juridico,
                    "ataque": f"La contraparte puede cuestionar la falta de soporte probatorio para {fila.elemento_juridico}",
                    "tipo": "vacio_probatorio",
                    "severidad": "alta",
                })

            for p in fila.pruebas:
                if p.relacion == "contradice":
                    ataques.append({
                        "fila_id": fila.id,
                        "elemento": fila.elemento_juridico,
                        "ataque": f"La prueba {p.id} ({p.tipo}) contradice el hecho H{fila.hecho.id}",
                        "tipo": "contradiccion",
                        "severidad": "alta",
                    })

            if fila.riesgo in ("alto", "critico"):
                ataques.append({
                    "fila_id": fila.id,
                    "elemento": fila.elemento_juridico,
                    "ataque": f"Alto riesgo en {fila.elemento_juridico}: recomendable modular o reforzar",
                    "tipo": "riesgo",
                    "severidad": "media",
                })

        if not ataques:
            ataques.append({
                "fila_id": "general",
                "elemento": "teoria del caso",
                "ataque": "Revisar consistencia general de la teoria ante posibles excepciones",
                "tipo": "preventivo",
                "severidad": "baja",
            })

        self.memory["ataques"] = ataques
        self.log("ataques_identificados", {"ataques": len(ataques)})
        return ataques
