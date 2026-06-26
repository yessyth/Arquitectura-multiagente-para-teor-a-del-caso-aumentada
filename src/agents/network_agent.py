from agents.base_agent import BaseAgent
from schemas import Arista, CapaRed, TipoRelacion
from multilayer_network import MultilayerNetwork


class NetworkAgent(BaseAgent):
    def __init__(self):
        super().__init__("agente_red", "Transforma matriz y expediente en red multicapa")

    def run(self, hpn_filas: list, actores: list, pruebas_raw: list, normas_raw: list):
        self.log("construyendo_red_multicapa", {"filas_hpn": len(hpn_filas)})
        net = MultilayerNetwork()

        for fila in hpn_filas:
            net.add_node(fila.hecho.id, capa=CapaRed.HECHOS.value,
                         label=fila.hecho.texto[:50], estado=fila.estado, riesgo=fila.riesgo)
            for p in fila.pruebas:
                net.add_node(p.id, capa=CapaRed.PRUEBAS.value,
                             label=f"{p.tipo}: {p.id}", tipo=p.tipo, fuerza=p.fuerza)
                net.add_edge(Arista(
                    source=p.id, target=fila.hecho.id,
                    type=p.relacion, layer_source=CapaRed.PRUEBAS.value,
                    layer_target=CapaRed.HECHOS.value, weight=p.fuerza,
                ))
            for n in fila.normas:
                net.add_node(n.id, capa=CapaRed.NORMAS.value,
                             label=n.texto[:50], fuente=n.fuente)
                net.add_edge(Arista(
                    source=n.id, target=fila.hecho.id,
                    type=TipoRelacion.ACTIVA.value, layer_source=CapaRed.NORMAS.value,
                    layer_target=CapaRed.HECHOS.value, weight=0.7,
                ))

        for actor in actores:
            net.add_node(f"ACT-{hash(actor) % 1000}", capa=CapaRed.ACTORES.value, label=actor)

        for p in pruebas_raw:
            node_id = p["id"]
            if node_id not in {n_id for n_id, _ in net.graph.nodes(data="capa") if _}:
                net.add_node(node_id, capa=CapaRed.PRUEBAS.value,
                             label=f"{p['tipo']}: {p.get('texto', '')[:50]}",
                             tipo=p["tipo"], fuerza=p.get("fuerza", 0.5))

        for n in normas_raw:
            node_id = n["id"]
            if node_id not in {n_id for n_id, _ in net.graph.nodes(data="capa") if _}:
                net.add_node(node_id, capa=CapaRed.NORMAS.value,
                             label=n["texto"][:50], tipo=n.get("tipo", ""), fuente=n["fuente"])

        net.save()
        self.memory["red"] = net
        self.log("red_multicapa_creada", {
            "nodos": net.graph.number_of_nodes(),
            "aristas": net.graph.number_of_edges(),
        })
        return net
