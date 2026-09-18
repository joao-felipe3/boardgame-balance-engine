import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match
from collections import Counter

print("=== EM QUAIS RODADAS OCORREM OS COMITÊS FORÇADOS? ===")

forced_by_round = Counter()
total_games = 500

for g in range(total_games):
    res = simulate_single_match(g, seed=333000 + g, record_trace=True)
    for r_idx, r in enumerate(res['rounds_data']):
        # Se os votos registraram rejeição nas tentativas
        # Como saber se essa rodada foi forçada?
        # Se r['committee'] foi escolhido após 3 vetos
        pass

# Vamos olhar diretamente no engine onde forced_committees é incrementado
