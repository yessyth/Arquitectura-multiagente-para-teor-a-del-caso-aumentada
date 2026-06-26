from agents.base_agent import BaseAgent
from metrics_calculator import MetricsCalculator


class MetricsAgent(BaseAgent):
    def __init__(self):
        super().__init__("agente_metrico", "Calcula métricas de matriz HPN y red multicapa")

    def run(self, hpn_filas: list, network, full_text: str):
        self.log("calculando_metricas", {"filas_hpn": len(hpn_filas)})
        calculator = MetricsCalculator(hpn_filas, network, full_text)
        metrics = calculator.calculate_all()
        calculator.save()
        self.memory["metrics"] = metrics
        self.log("metricas_calculadas", {"num_metricas": len(metrics)})
        return metrics
