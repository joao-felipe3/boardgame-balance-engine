import sys, os
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match, Role, BankerProfile, InternProfile
from collections import Counter

# Let's find 5 games where Round 3 had 0 interns in committee, but failed QUEBRA_INSUMO
cases = []
for i in range(100):
    res = simulate_single_match(i, seed=333000 + i, record_trace=True)
    for r_idx, r in enumerate(res['rounds_data']):
        rnd = r_idx + 1
        if rnd == 3 and not r['is_success'] and not r['has_req']:
            comm = r['committee']
            interns = [pid for pid in comm if res['players_metadata'][pid]['role'] == 'INTERN']
            if not interns:
                cases.append((i, r))
                if len(cases) >= 5:
                    break
    if len(cases) >= 5:
        break

print(f"Casos encontrados de R3 falhando por QUEBRA_INSUMO com 100% Banqueiros: {len(cases)}")
for idx, (g, r) in enumerate(cases):
    print(f"\n--- Caso {idx+1} (Jogo {g}) ---")
    print(f"Contrato: {r['contract']['name']}, Req: {r['contract']['req_commodity']} x {r['contract']['req_count']}")
    print(f"Comitê: {r['committee']}")
    print(f"Fornecedor prometido: {r['promised_supplier']}")
    print(f"Declarações: {r['declarations']}")
    print(f"Cartas submetidas:")
    for sub in r['submitted']:
        print(f"  P{sub['player_id']} (RespReq={sub['is_req_responsible']}, Tok={sub['tokens_spent']}): {[c['type'] for c in sub['cards']]}")
