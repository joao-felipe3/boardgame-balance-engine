import sys, os
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match, Role
import numpy as np

# Let's inspect 5 games where in R3, Chair was Banker, comm had Intern, and it passed by vote
cases = []
for i in range(100):
    res = simulate_single_match(i, seed=666000 + i, record_trace=True)
    r = res['rounds_data'][2] # Round 3
    chair_role = res['players_metadata'][r['chair_id']]['role']
    interns = [pid for pid in r['committee'] if res['players_metadata'][pid]['role'] in ('Estagiario', 'Estagiário', 'INTERN')]
    v_for = sum(1 for v in r['votes'].values() if v)
    if chair_role == 'Banqueiro' and interns and v_for >= 3:
        cases.append((i, r, res['players_metadata'], res['rounds_data']))
        if len(cases) >= 5:
            break

print(f"Casos encontrados em R3 com Chair Banqueiro convidando Estagiário: {len(cases)}\n")
for idx, (g, r, p_meta, r_data) in enumerate(cases):
    print(f"================ CASO {idx+1} (Jogo {g}) ================")
    print(f"Contrato: {r['contract']['name']}, Req: {r['contract']['req_commodity']} x {r['contract']['req_count']}, Target: {r['contract']['target']}")
    print(f"Chair: P{r['chair_id']} (Banqueiro)")
    print(f"Comitê Escolhido: {r['committee']}")
    print(f"Fornecedor: {r['promised_supplier']}")
    print(f"Votos: {r['votes']}")
    print(f"Papéis dos jogadores:")
    for pm in p_meta:
        print(f"  P{pm['id']}: {pm['role']}")
    print("Histórico Rodada 1:")
    r1 = r_data[0]
    print(f"  R1: Comm={r1['committee']}, Succ={r1['is_success']}")
    print("Histórico Rodada 2:")
    r2 = r_data[1]
    print(f"  R2: Comm={r2['committee']}, Succ={r2['is_success']}")
    print(f"Declarações na R3:")
    for pid, d in r['declarations'].items():
        print(f"  P{pid}: claims_req={d['claims_req']}, val={d['claimed_val']}, bench={d['prefers_bench']}, desc={d['offered_desc']}")
    print(f"Suspeitas no início da R3 (conforme visão do Chair):")
    # chair suspicions
    chair_sus = r['suspicions']['by_banker'][r['chair_id']]
    print(f"  Chair suspicions: {chair_sus}")
