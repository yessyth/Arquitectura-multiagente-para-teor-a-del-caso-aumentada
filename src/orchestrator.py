import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
from datetime import datetime
from config import DATA_DIR
from pdf_reader import PDFReader
from case_detector import CaseTypeDetector, CASE_TYPES
from agents.factual_agent import FactualAgent
from agents.evidence_agent import EvidenceAgent
from agents.normative_agent import NormativeAgent
from agents.hpn_agent import HPNAgent
from agents.network_agent import NetworkAgent
from agents.metrics_agent import MetricsAgent
from agents.adversarial_agent import AdversarialAgent
from agents.simulator_agent import SimulatorAgent
from agents.auditor_agent import AuditorAgent


class Orchestrator:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.fragments = []
        self.full_text = ""
        self.case_type = "civil"
        self.case_config = CASE_TYPES["civil"]
        self.hechos = []
        self.actores = []
        self.fechas = []
        self.pruebas = []
        self.vacios = []
        self.normas = []
        self.hpn_matrix = None
        self.hpn_filas = []
        self.network = None
        self.metrics = {}
        self.ataques = []
        self.escenarios = []
        self.alertas_auditoria = []
        self.logs_agentes = []

        self.factual_agent = FactualAgent()
        self.evidence_agent = EvidenceAgent()
        self.normative_agent = NormativeAgent()
        self.hpn_agent = HPNAgent()
        self.network_agent = NetworkAgent()
        self.metrics_agent = MetricsAgent()
        self.adversarial_agent = AdversarialAgent()
        self.simulator_agent = SimulatorAgent()
        self.auditor_agent = AuditorAgent()

    def run(self):
        print("=" * 60)
        print(f"SISTEMA DE TEORIA DEL CASO AUMENTADA")
        print(f"Inicio: {datetime.now().isoformat()}")
        print("=" * 60)

        # Paso 1: Ingesta de PDF
        print("\n[1/9] Ingestando PDF...")
        reader = PDFReader(self.pdf_path)
        self.fragments = reader.extract()
        reader.save_fragments()
        self.full_text = reader.get_full_text()
        print(f"  -> {len(self.fragments)} fragmentos extraidos")

        # Detección de tipo de caso
        print("\n[Detector] Analizando tipo de caso...")
        detector = CaseTypeDetector(self.full_text)
        self.case_type = detector.detect()
        self.case_config = detector.get_config(self.case_type)
        print(f"  -> Tipo detectado: {self.case_config['label']}")

        # Paso 2: Extracción fáctica y cronológica
        print("\n[2/9] Extrayendo hechos, actores y fechas...")
        self.hechos, self.actores, self.fechas = self.factual_agent.run(
            self.fragments, self.full_text, self.case_config
        )
        print(f"  -> {len(self.hechos)} hechos, {len(self.actores)} actores, {len(self.fechas)} fechas")

        # Paso 3: Extracción probatoria
        print("\n[3/9] Extrayendo pruebas...")
        self.pruebas, self.vacios = self.evidence_agent.run(self.fragments, self.hechos, self.case_config)
        print(f"  -> {len(self.pruebas)} pruebas, {len(self.vacios)} vacios detectados")

        # Paso 4: Extracción normativa
        print("\n[4/9] Extrayendo normas...")
        self.normas = self.normative_agent.run(self.fragments, self.case_config)
        print(f"  -> {len(self.normas)} normas identificadas")

        # Paso 5: Construcción de matriz HPN
        print("\n[5/9] Construyendo matriz HPN...")
        self.hpn_matrix, self.hpn_filas = self.hpn_agent.run(
            self.hechos, self.pruebas, self.normas, self.actores, self.case_config
        )
        summary = self.hpn_matrix.get_summary()
        print(f"  -> {summary['total_filas']} filas HPN generadas")
        print(f"  -> Estados: {summary['estados']}")
        print(f"  -> Riesgos: {summary['riesgos']}")

        # Paso 6: Construcción de red multicapa
        print("\n[6/9] Construyendo red multicapa...")
        self.network = self.network_agent.run(
            self.hpn_filas, self.actores, self.pruebas, self.normas
        )
        net_summary = self.network.get_summary()
        print(f"  -> {net_summary['total_nodos']} nodos, {net_summary['total_aristas']} aristas")
        print(f"  -> Capas: {net_summary['capas']}")

        # Paso 7: Cálculo de métricas
        print("\n[7/9] Calculando métricas...")
        self.metrics = self.metrics_agent.run(
            self.hpn_filas, self.network, self.full_text
        )
        self.metrics["tipo_caso"] = self.case_config["label"]
        for k, v in self.metrics.items():
            if isinstance(v, (int, float)):
                print(f"  -> {k}: {v}")
        print(f"  -> {len(self.metrics)} metricas calculadas")

        # Paso 8: Análisis adversarial
        print("\n[8/9] Analisis adversarial...")
        self.ataques = self.adversarial_agent.run(self.hpn_filas, self.network, self.case_config)
        print(f"  -> {len(self.ataques)} ataques/riesgos identificados")

        # Paso 9: Simulación de escenarios
        print("\n[9/9] Simulando escenarios procesales...")
        self.escenarios = self.simulator_agent.run(
            self.hpn_filas, self.network, self.metrics, self.case_config
        )
        print(f"  -> {len(self.escenarios)} escenarios simulados")

        # Auditoría final
        print("\n[Auditoria] Verificando trazabilidad y coherencia...")
        self.alertas_auditoria = self.auditor_agent.run(self.hpn_filas, self.fragments)
        print(f"  -> {len(self.alertas_auditoria)} alertas de auditoria")

        print("\n" + "=" * 60)
        print("PROCESO COMPLETADO EXITOSAMENTE")
        print(f"Tipo de caso: {self.case_config['label']}")
        print("=" * 60)

        return {
            "fragments": self.fragments,
            "hechos": self.hechos,
            "actores": self.actores,
            "fechas": self.fechas,
            "pruebas": self.pruebas,
            "vacios": self.vacios,
            "normas": self.normas,
            "hpn_matrix": self.hpn_matrix,
            "hpn_filas": self.hpn_filas,
            "network": self.network,
            "metrics": self.metrics,
            "ataques": self.ataques,
            "escenarios": self.escenarios,
            "alertas_auditoria": self.alertas_auditoria,
            "case_type": self.case_type,
            "case_config": self.case_config,
        }


def main():
    if len(sys.argv) < 2:
        print("Uso: python orchestrator.py <ruta_del_pdf>")
        sys.exit(1)
    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"Error: No se encuentra el archivo {pdf_path}")
        sys.exit(1)
    orch = Orchestrator(pdf_path)
    orch.run()


if __name__ == "__main__":
    main()
