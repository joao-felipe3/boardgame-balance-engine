import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match
from collections import Counter

print("=== INSPECIONANDO OS MOTIVOS DE VETO DOS BANQUEIROS ===")

# Vamos rodar 50 jogos e logar as propostas rejeitadas na R1, R2 e R3
for g in range(30):
    res = simulate_single_match(g, seed=500000 + g, record_trace=True)
    # Procurar jogos com comitês forçados
    if res['forced_committees'] > 0:
        print(f"\n--- JOGO {g} (Total vetos: {res['total_vetoes']}, Forçados: {res['forced_committees']}) ---")
        for r_idx, r in enumerate(res['rounds_data']):
            print(f"  Rodada {r_idx+1} (Tier {r['contract']['tier']}): Chair={r['chair_id']}, Comm={r['committee']}, Succ={r['is_success']}")
            print(f"     Votos: {r['votes']}")
        break
