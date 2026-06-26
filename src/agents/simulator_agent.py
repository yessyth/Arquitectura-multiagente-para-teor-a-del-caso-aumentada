from agents.base_agent import BaseAgent
from scenario_simulator import ScenarioSimulator


class SimulatorAgent(BaseAgent):
    def __init__(self):
        super().__init__("agente_simulador", "Ejecuta escenarios de perturbación sobre matriz y red")

    def run(self, hpn_filas, network, metrics):
        self.log("ejecutando_simulaciones", {"filas_hpn": len(hpn_filas)})
        simulator = ScenarioSimulator(hpn_filas, network, metrics)
        escenarios = simulator.run_all()
        simulator.save()
        self.memory["escenarios"] = escenarios
        self.log("simulaciones_completadas", {"escenarios": len(escenarios)})
        return escenarios
