import json
import networkx as nx
from config import METRICS_PATH


class MetricsCalculator:
    def __init__(self, hpn_filas, network, full_text: str = ""):
        self.hpn_filas = hpn_filas
        self.network = network
        self.full_text = full_text
        self.metrics = {}

    def calculate_all(self):
        self.metrics["cobertura_elementos_juridicos"] = self._cobertura_elementos()
        self.metrics["cobertura_probatoria"] = self._cobertura_probatoria()
        self.metrics["cobertura_normativa"] = self._cobertura_normativa()
        self.metrics["indice_vacios_criticos"] = self._vacios_criticos()
        self.metrics["indice_contradiccion"] = self._contradiccion()
        self.metrics["debilidad_argumentativa"] = self._debilidad()
        self.metrics["acciones_pendientes"] = self._acciones_pendientes()
        self.metrics["trazabilidad"] = self._trazabilidad()

        if self.network and self.network.graph.number_of_nodes() > 0:
            g = self.network.graph
            self.metrics["total_nodos"] = g.number_of_nodes()
            self.metrics["total_aristas"] = g.number_of_edges()

            if g.number_of_nodes() > 1:
                try:
                    self.metrics["densidad_red"] = round(
                        nx.density(g), 4
                    )
                except Exception:
                    self.metrics["densidad_red"] = 0
            else:
                self.metrics["densidad_red"] = 0

            degrees = [d for _, d in g.degree()]
            self.metrics["grado_promedio"] = round(sum(degrees) / len(degrees), 2) if degrees else 0
            self.metrics["grado_maximo"] = max(degrees) if degrees else 0
            self.metrics["grado_minimo"] = min(degrees) if degrees else 0

            capas = {}
            for _, d in g.nodes(data=True):
                capa = d.get("capa", "desconocida")
                capas[capa] = capas.get(capa, 0) + 1
            self.metrics["distribucion_capas"] = capas

        return self.metrics

    def _cobertura_elementos(self):
        if not self.hpn_filas:
            return 0
        completas = sum(1 for f in self.hpn_filas if f.estado == "completo")
        return round(completas / len(self.hpn_filas) * 100, 1)

    def _cobertura_probatoria(self):
        if not self.hpn_filas:
            return 0
        con_prueba = sum(1 for f in self.hpn_filas if len(f.pruebas) > 0)
        return round(con_prueba / len(self.hpn_filas) * 100, 1)

    def _cobertura_normativa(self):
        if not self.hpn_filas:
            return 0
        con_norma = sum(1 for f in self.hpn_filas if len(f.normas) > 0)
        return round(con_norma / len(self.hpn_filas) * 100, 1)

    def _vacios_criticos(self):
        if not self.hpn_filas:
            return 0
        vacios = sum(1 for f in self.hpn_filas if f.estado == "vacio_critico")
        return {"cantidad": vacios, "porcentaje": round(vacios / len(self.hpn_filas) * 100, 1)}

    def _contradiccion(self):
        if not self.hpn_filas:
            return 0
        contradictorias = sum(1 for f in self.hpn_filas if f.estado == "controvertido")
        return {"cantidad": contradictorias, "porcentaje": round(contradictorias / len(self.hpn_filas) * 100, 1)}

    def _debilidad(self):
        if not self.hpn_filas:
            return 0
        debiles = sum(1 for f in self.hpn_filas if f.estado in ("debil", "parcial", "vacio_critico"))
        return {"cantidad": debiles, "porcentaje": round(debiles / len(self.hpn_filas) * 100, 1)}

    def _acciones_pendientes(self):
        if not self.hpn_filas:
            return 0
        pendientes = sum(1 for f in self.hpn_filas if f.revision_humana == "pendiente")
        return {"cantidad": pendientes, "porcentaje": round(pendientes / len(self.hpn_filas) * 100, 1)}

    def _trazabilidad(self):
        if not self.hpn_filas:
            return 0
        con_fuente = sum(1 for f in self.hpn_filas if f.fuente_expediente)
        con_agente = sum(1 for f in self.hpn_filas if f.agente)
        return {
            "con_fuente": round(con_fuente / len(self.hpn_filas) * 100, 1),
            "con_agente": round(con_agente / len(self.hpn_filas) * 100, 1),
        }

    def save(self):
        with open(METRICS_PATH, "w", encoding="utf-8") as f:
            json.dump(self.metrics, f, ensure_ascii=False, indent=2)
