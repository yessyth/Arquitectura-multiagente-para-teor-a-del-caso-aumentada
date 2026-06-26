from dataclasses import dataclass, field, asdict
from typing import Optional
from enum import Enum
import json


class EstadoEpistemico(str, Enum):
    COMPLETO = "completo"
    PARCIAL = "parcial"
    CONTROVERTIDO = "controvertido"
    DEBIL = "debil"
    VACIO_CRITICO = "vacio_critico"
    RIESGO_ADVERSARIAL = "riesgo_adversarial"
    BLOQUEADO = "bloqueado"
    PENDIENTE = "pendiente"


class NivelRiesgo(str, Enum):
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"
    CRITICO = "critico"


class TipoRelacion(str, Enum):
    SOPORTA = "soporta"
    CONTRADICE = "contradice"
    ACTIVA = "activa"
    FUNDAMENTA = "fundamenta"
    DERROTA = "derrota"
    PRECEDE = "precede"
    DISTINGUE = "distingue"
    RIESGO = "riesgo"


class CapaRed(str, Enum):
    HECHOS = "hecho"
    PRUEBAS = "prueba"
    NORMAS = "norma"
    PRECEDENTES = "precedente"
    ARGUMENTOS = "argumento"
    RIESGOS = "riesgo"
    TIEMPO = "tiempo"
    ACTORES = "actor"
    PRETENSIONES = "pretension"


@dataclass
class Fuente:
    pagina: int
    fragmento_id: str
    texto: str = ""


@dataclass
class Hecho:
    id: str
    texto: str
    fuente: Fuente


@dataclass
class Prueba:
    id: str
    tipo: str
    relacion: str
    fuerza: float


@dataclass
class Norma:
    id: str
    texto: str
    fuente: str = ""


@dataclass
class FilaHPN:
    id: str
    elemento_juridico: str
    hecho: Hecho
    pruebas: list
    normas: list
    estado: str
    riesgo: str
    accion_sugerida: str
    agente: str = ""
    revision_humana: str = "pendiente"
    contradicciones: str = ""
    fuente_expediente: str = ""

    def to_dict(self):
        return {
            "id": self.id,
            "elemento_juridico": self.elemento_juridico,
            "hecho": {
                "id": self.hecho.id,
                "texto": self.hecho.texto,
                "fuente": {
                    "pagina": self.hecho.fuente.pagina,
                    "fragmento_id": self.hecho.fuente.fragmento_id,
                },
            },
            "pruebas": [
                {"id": p.id, "tipo": p.tipo, "relacion": p.relacion, "fuerza": p.fuerza}
                for p in self.pruebas
            ],
            "normas": [{"id": n.id, "texto": n.texto, "fuente": n.fuente} for n in self.normas],
            "estado": self.estado,
            "riesgo": self.riesgo,
            "accion_sugerida": self.accion_sugerida,
            "agente": self.agente,
            "revision_humana": self.revision_humana,
            "contradicciones": self.contradicciones,
            "fuente_expediente": self.fuente_expediente,
        }


@dataclass
class Arista:
    source: str
    target: str
    type: str
    layer_source: str
    layer_target: str
    weight: float
    evidence: Optional[dict] = None
    status: str = "validada_por_agente"
    human_review: str = "pendiente"

    def to_dict(self):
        d = {
            "source": self.source,
            "target": self.target,
            "type": self.type,
            "layer_source": self.layer_source,
            "layer_target": self.layer_target,
            "weight": self.weight,
            "status": self.status,
            "human_review": self.human_review,
        }
        if self.evidence:
            d["evidence"] = self.evidence
        return d
