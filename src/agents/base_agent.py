import json
from datetime import datetime
from config import LOG_PATH


class BaseAgent:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.memory = {}
        self.logs = []

    def log(self, action: str, input_data=None, output_data=None, tool: str = ""):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agente": self.name,
            "rol": self.role,
            "accion": action,
            "entrada": str(input_data)[:500] if input_data else None,
            "salida": str(output_data)[:500] if output_data else None,
            "herramienta": tool,
        }
        self.logs.append(entry)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def get_summary(self) -> dict:
        return {
            "name": self.name,
            "role": self.role,
            "logs_count": len(self.logs),
        }
