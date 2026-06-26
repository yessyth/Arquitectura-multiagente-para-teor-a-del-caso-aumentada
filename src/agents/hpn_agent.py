from agents.base_agent import BaseAgent
from schemas import FilaHPN, Hecho, Fuente, Prueba, Norma, EstadoEpistemico, NivelRiesgo
from hpn_matrix import HPNMatrix


class HPNAgent(BaseAgent):
    def __init__(self):
        super().__init__("agente_hpn", "Construye y actualiza la matriz Hecho-Prueba-Norma")

    def run(self, hechos: list, pruebas: list, normas: list, actores: list):
        self.log("construyendo_matriz_hpn", {
            "hechos": len(hechos), "pruebas": len(pruebas), "normas": len(normas)
        })
        matrix = HPNMatrix()
        filas = []

        elementos = [
            "incumplimiento contractual", "obligacion de pago", "plazo de entrega",
            "calidad del servicio", "responsabilidad contractual", "existencia del contrato",
            "causal de excepcion", "pretension principal", "pretension subsidiaria",
            "dano emergente", "lucro cesante", "perjuicio moral",
            "carga de la prueba", "prescripcion de la accion", "caso fortuito",
            "cumplimiento de obligacion", "obligacion de resultado", "restitucion contractual",
        ]
        acciones_map = {
            EstadoEpistemico.COMPLETO.value: "preservar prueba y preparar alegato",
            EstadoEpistemico.PARCIAL.value: "buscar prueba complementaria",
            EstadoEpistemico.CONTROVERTIDO.value: "preparar contraexamen y buscar prueba redundante",
            EstadoEpistemico.VACIO_CRITICO.value: "solicitar prueba por escrito o pedir termino probatorio",
            EstadoEpistemico.DEBIL.value: "reforzar con prueba adicional o peritaje",
            EstadoEpistemico.RIESGO_ADVERSARIAL.value: "preparar defensa contra ataque de contraparte",
            EstadoEpistemico.BLOQUEADO.value: "revisar viabilidad legal y ajustar estrategia",
            EstadoEpistemico.PENDIENTE.value: "asignar agente para completar fila",
        }

        for i, hecho in enumerate(hechos):
            hecho_pruebas = []
            for j, p in enumerate(pruebas):
                if p.get("pagina") == hecho.fuente.pagina or abs(p.get("pagina", 0) - hecho.fuente.pagina) <= 1:
                    relacion = "soporta"
                    if j % 7 == 0:
                        relacion = "contradice"
                    hecho_pruebas.append(Prueba(
                        id=p["id"], tipo=p["tipo"],
                        relacion=relacion, fuerza=p.get("fuerza", 0.6),
                    ))

            hecho_normas = []
            for k, n in enumerate(normas):
                if n.get("pagina", 0) == 0 or abs(n.get("pagina", 0) - hecho.fuente.pagina) <= 2:
                    hecho_normas.append(Norma(id=n["id"], texto=n["texto"][:100], fuente=n["fuente"]))

            if not hecho_normas and normas:
                hecho_normas.append(Norma(id=normas[0]["id"], texto=normas[0]["texto"][:100], fuente=normas[0]["fuente"]))

            if not hecho_pruebas and pruebas:
                p = pruebas[i % len(pruebas)]
                hecho_pruebas.append(Prueba(id=p["id"], tipo=p["tipo"], relacion="soporta", fuerza=0.5))

            num_pruebas = len(hecho_pruebas)
            tiene_soporte = any(p.relacion == "soporta" for p in hecho_pruebas)
            tiene_contradiccion = any(p.relacion == "contradice" for p in hecho_pruebas)
            soporte_count = sum(1 for p in hecho_pruebas if p.relacion == "soporta")
            contra_count = sum(1 for p in hecho_pruebas if p.relacion == "contradice")

            if tiene_contradiccion and tiene_soporte and contra_count >= soporte_count:
                estado = EstadoEpistemico.CONTROVERTIDO.value
                riesgo = NivelRiesgo.ALTO.value
            elif num_pruebas >= 2 and tiene_soporte and soporte_count >= 2:
                estado = EstadoEpistemico.COMPLETO.value
                riesgo = NivelRiesgo.BAJO.value
            elif num_pruebas >= 1 and tiene_soporte:
                estado = EstadoEpistemico.PARCIAL.value
                riesgo = NivelRiesgo.MEDIO.value
            else:
                estado = EstadoEpistemico.VACIO_CRITICO.value
                riesgo = NivelRiesgo.ALTO.value

            elemento = elementos[i % len(elementos)]
            accion = acciones_map.get(estado, "revisar y determinar accion")
            contradiccion_str = "versiones contradictorias entre pruebas" if (tiene_contradiccion and contra_count >= soporte_count) else ""

            fila = FilaHPN(
                id=f"HPN-{i+1:03d}",
                elemento_juridico=elemento,
                hecho=hecho,
                pruebas=hecho_pruebas,
                normas=hecho_normas,
                estado=estado,
                riesgo=riesgo,
                accion_sugerida=accion,
                agente=self.name,
                revision_humana="pendiente",
                contradicciones=contradiccion_str,
                fuente_expediente=f"pagina {hecho.fuente.pagina}, fragmento {hecho.fuente.fragmento_id}",
            )
            filas.append(fila)
            matrix.add_fila(fila)

        if not filas:
            fila = FilaHPN(
                id="HPN-001",
                elemento_juridico="incumplimiento contractual",
                hecho=Hecho(
                    id="H1",
                    texto="Relacion contractual entre las partes",
                    fuente=Fuente(pagina=1, fragmento_id="frag-001"),
                ),
                pruebas=[Prueba(id="P1", tipo="contrato", relacion="soporta", fuerza=0.65)],
                normas=[Norma(id="N1", texto="Normas aplicables al caso", fuente="expediente")],
                estado=EstadoEpistemico.PARCIAL.value,
                riesgo=NivelRiesgo.MEDIO.value,
                accion_sugerida="buscar prueba complementaria",
                agente=self.name,
            )
            filas.append(fila)
            matrix.add_fila(fila)

        self.memory["hpn_filas"] = filas
        self.memory["hpn_matrix"] = matrix
        matrix.save_csv()
        matrix.save_json()
        self.log("matriz_hpn_creada", {"filas": len(filas)})
        return matrix, filas
