import sys, os
sys.path.insert(0, os.path.abspath('.'))
from src.btg import simulate_single_match, Role, BankerProfile, InternProfile

r2_pure_banker_fail_count = 0
total_matches = 500

for s in range(total_matches):
    res = simulate_single_match(s, seed=660000 + s, record_trace=True)
    meta = res['players_metadata']
    roles = {p['id']: p['role'] for p in meta}
    for r in res['rounds_data']:
        if r['round_num'] == 2 and not r['is_success']:
            comm = r['committee']
            if all(roles[pid] == 'Banqueiro' for pid in comm):
                r2_pure_banker_fail_count += 1

print(f"In {total_matches} matches, R2 failed with TWO BANQUEIROS: {r2_pure_banker_fail_count} times ({r2_pure_banker_fail_count/total_matches*100:.1f}%)")
