import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
FRAGMENTS_PATH = os.path.join(DATA_DIR, "fragments.jsonl")
HPN_CSV_PATH = os.path.join(DATA_DIR, "hpn_matrix.csv")
HPN_JSON_PATH = os.path.join(DATA_DIR, "hpn_matrix.json")
NETWORK_PATH = os.path.join(DATA_DIR, "multilayer_network.json")
METRICS_PATH = os.path.join(DATA_DIR, "metrics.json")
SCENARIOS_PATH = os.path.join(DATA_DIR, "scenarios.json")
LOG_PATH = os.path.join(DATA_DIR, "agent_logs.jsonl")

for d in [DATA_DIR, OUTPUTS_DIR]:
    os.makedirs(d, exist_ok=True)
