import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match, Role

for seed in range(100):
    match = simulate_single_match(seed, seed=seed, banker_profile="MIXED", intern_profile="MIXED", record_trace=True)
    roles = {p['id']: p['role'] for p in match['players_metadata']}
    banker_ids = [pid for pid, r in roles.items() if r in ('Banqueiro', Role.BANKER.value)]
    last_r = match['rounds_data'][-1]
    sus_by_banker = last_r['suspicions']['by_banker']
    
    burned = [(b1, b2, sus_by_banker[b1][b2]) for b1 in banker_ids for b2 in banker_ids if b1 != b2 and sus_by_banker[b1].get(b2, 0) >= 0.99]
    if burned:
        print(f"Seed {seed}: Burned={burned}")
        for r_idx, r in enumerate(match['rounds_data']):
            for b1, b2, _ in burned:
                curr_sus = r['suspicions']['by_banker'][b1].get(b2, 0)
                if curr_sus >= 0.99:
                    prev_r = match['rounds_data'][r_idx - 1] if r_idx > 0 else None
                    print(f"  R{r['round_num']}: B{b1} sets B{b2} to {curr_sus} | Prev Comm: {prev_r['committee'] if prev_r else None} (Chair {prev_r['chair_id'] if prev_r else None}) | Success: {prev_r['is_success'] if prev_r else None} | HasReq: {prev_r['has_req'] if prev_r else None} | Toxic: {any(c['type']=='TOXIC' for d in prev_r['submitted'] for c in d['cards']) if prev_r else None}")
                    break
            if curr_sus >= 0.99:
                break
