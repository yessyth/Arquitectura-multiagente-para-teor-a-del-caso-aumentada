import csv
import json
from config import HPN_CSV_PATH, HPN_JSON_PATH


class HPNMatrix:
    def __init__(self):
        self.filas = []

    def add_fila(self, fila):
        self.filas.append(fila)

    def to_dataframe(self):
        import pandas as pd
        rows = []
        for f in self.filas:
            rows.append({
                "ID": f.id,
                "Elemento Juridico": f.elemento_juridico,
                "Hecho": f.hecho.texto,
                "Hecho ID": f.hecho.id,
                "Pruebas": "; ".join(f"{p.id} ({p.tipo}, {p.relacion}, {p.fuerza})" for p in f.pruebas),
                "Normas": "; ".join(f"{n.id}: {n.texto[:80]}" for n in f.normas),
                "Estado": f.estado,
                "Riesgo": f.riesgo,
                "Contradicciones": f.contradicciones,
                "Accion Sugerida": f.accion_sugerida,
                "Agente": f.agente,
                "Revision Humana": f.revision_humana,
                "Fuente Expediente": f.fuente_expediente,
            })
        return pd.DataFrame(rows)

    def save_csv(self):
        df = self.to_dataframe()
        df.to_csv(HPN_CSV_PATH, index=False, encoding="utf-8")

    def save_json(self):
        data = [f.to_dict() for f in self.filas]
        with open(HPN_JSON_PATH, "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)

    def get_summary(self):
        estados = {}
        riesgos = {}
        for f in self.filas:
            estados[f.estado] = estados.get(f.estado, 0) + 1
            riesgos[f.riesgo] = riesgos.get(f.riesgo, 0) + 1
        return {
            "total_filas": len(self.filas),
            "estados": estados,
            "riesgos": riesgos,
        }
