import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match, Role

for seed in range(10):
    match = simulate_single_match(seed, seed=seed, banker_profile="MIXED", intern_profile="MIXED", record_trace=True)
    roles = {p['id']: p['role'] for p in match['players_metadata']}
    banker_ids = [pid for pid, r in roles.items() if r in ('Banqueiro', Role.BANKER.value)]
    
    # check if any round caused a jump to >= 0.50
    for r_idx, r in enumerate(match['rounds_data']):
        sus = r['suspicions']['by_banker']
        for b1 in banker_ids:
            for b2 in banker_ids:
                if b1 != b2 and sus[b1].get(b2, 0) >= 0.50:
                    prev_sus = match['rounds_data'][r_idx - 1]['suspicions']['by_banker'][b1].get(b2, 0) if r_idx > 0 else 0.40
                    if prev_sus < 0.50:
                        prev_r = match['rounds_data'][r_idx - 1]
                        print(f"Match {seed} | R{prev_r['round_num']} -> R{r['round_num']}: B{b1} jumped sus on B{b2} from {prev_sus} to {sus[b1][b2]}")
                        print(f"   Prev round was: Comm={prev_r['committee']}, Success={prev_r['is_success']}, HasReq={prev_r['has_req']}, Toxic={any(c['type']=='TOXIC' for d in prev_r['submitted'] for c in d['cards'])}")
                        print(f"   Submitted was: {[d['player_id'] for d in prev_r['submitted']]}")
