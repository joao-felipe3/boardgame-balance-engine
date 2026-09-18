import sys, os
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match, Role

depleted_fails = 0
total_r2_pure_fails = 0

for i in range(500):
    res = simulate_single_match(i, seed=111000 + i, record_trace=True)
    r2 = res['rounds_data'][1]
    if not r2['is_success']:
        comm = r2['committee']
        interns = [pid for pid in comm if res['players_metadata'][pid]['role'] in ('Estagiario', 'Estagiário', 'INTERN')]
        if not interns:
            total_r2_pure_fails += 1
            r1_comm = res['rounds_data'][0]['committee']
            both_in_r1 = all(pid in r1_comm for pid in comm)
            tokens_total = sum(sub['tokens_spent'] for sub in r2['submitted'])
            val = r2['total_value']
            target = r2['contract']['target']
            print(f"R2 Falha Pura (Jogo {i}): Comm={comm}, R1_Comm={r1_comm}, Val={val}/{target}, Toks={tokens_total}, BothInR1={both_in_r1}")
            if both_in_r1:
                depleted_fails += 1
            if total_r2_pure_fails >= 10:
                break

print(f"\nTotal falhas puras em R2: {total_r2_pure_fails}")
