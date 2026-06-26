from agents.base_agent import BaseAgent


class AuditorAgent(BaseAgent):
    def __init__(self):
        super().__init__("agente_auditor", "Verifica fuentes, trazabilidad, coherencia y duplicados")

    def run(self, hpn_filas: list, fragments: list):
        self.log("auditando_sistema", {"filas_hpn": len(hpn_filas), "fragmentos": len(fragments)})
        alertas = []
        page_set = {f["pagina"] for f in fragments}

        for fila in hpn_filas:
            if fila.fuente_expediente:
                alertas.append({
                    "tipo": "trazabilidad",
                    "fila_id": fila.id,
                    "mensaje": f"Fuente registrada: {fila.fuente_expediente}",
                    "severidad": "info",
                })
            else:
                alertas.append({
                    "tipo": "sin_fuente",
                    "fila_id": fila.id,
                    "mensaje": f"La fila {fila.id} no tiene fuente de expediente",
                    "severidad": "alta",
                })

        ids = [fila.id for fila in hpn_filas]
        if len(ids) != len(set(ids)):
            alertas.append({
                "tipo": "duplicado",
                "fila_id": "general",
                "mensaje": "Se detectaron filas HPN duplicadas",
                "severidad": "alta",
            })

        estados_validos = {"completo", "parcial", "controvertido", "debil",
                           "vacio_critico", "riesgo_adversarial", "bloqueado", "pendiente"}
        for fila in hpn_filas:
            if fila.estado not in estados_validos:
                alertas.append({
                    "tipo": "estado_invalido",
                    "fila_id": fila.id,
                    "mensaje": f"Estado '{fila.estado}' no es válido",
                    "severidad": "media",
                })
            if fila.revision_humana not in ("pendiente", "revisado", "corregido", "aprobado", "rechazado"):
                alertas.append({
                    "tipo": "revision_invalida",
                    "fila_id": fila.id,
                    "mensaje": "Estado de revisión humana no reconocido",
                    "severidad": "media",
                })

        self.memory["alertas"] = alertas
        self.log("auditoria_completada", {"alertas": len(alertas)})
        return alertas
