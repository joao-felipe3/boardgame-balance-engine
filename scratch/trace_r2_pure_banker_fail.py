import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match, Role

print("Inspecionando 5 casos onde comitê puro de Banqueiros falhou na R2:")

count = 0
for seed in range(500):
    match = simulate_single_match(seed, seed=90000 + seed, banker_profile="MIXED", intern_profile="MIXED", record_trace=True)
    roles = {p['id']: p['role'] for p in match['players_metadata']}
    intern_ids = set([pid for pid, r in roles.items() if r in ('Estagiario', 'Estagiário')])
    
    r2 = match['rounds_data'][1]
    comm = r2['committee']
    is_pure = not any(p in intern_ids for p in comm)
    if is_pure and not r2['is_success']:
        count += 1
        print(f"\n--- CASO {count} (Jogo seed {seed}) ---")
        print(f"Comitê R2: {comm} (Todos Banqueiros)")
        print(f"Contract: {r2['contract']['name']}, Target: {r2['contract']['target']}, Req: {r2['contract']['req_commodity']}")
        print(f"Total Value: {r2['total_value']}, Has Req: {r2['has_req']}")
        print(f"Mãos ANTES da R2:")
        for pid in comm:
            h = r2['hands_before'][pid]
            h_str = [f"{c['type']}({c['val']})" for c in h]
            print(f"  P{pid}: hand={h_str}")
        print(f"Cartas SUBMETIDAS na R2:")
        for d in r2['submitted']:
            pid = d['player_id']
            c_str = [f"{c['type']}({c['val']})" for c in d['cards']]
            print(f"  P{pid} submeteu: {c_str}, tokens={d.get('tokens_spent', 0)}")
        if count >= 5:
            break
