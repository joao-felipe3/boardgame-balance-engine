import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match, Role

for seed in range(50):
    match = simulate_single_match(seed, seed=1000 + seed, banker_profile="MIXED", intern_profile="MIXED", record_trace=True)
    roles = {p['id']: p['role'] for p in match['players_metadata']}
    bankers = [pid for pid, r in roles.items() if r == 'Banqueiro']
    
    # Check each round to see when sus went >= 0.50
    for r in match['rounds_data']:
        r_num = r['round_num']
        comm = r['committee']
        succ = r['is_success']
        fail_cause = r.get('fail_cause')
        sus_map = r['suspicions']['by_banker']
        
        for b1 in bankers:
            for b2 in bankers:
                if b1 != b2 and sus_map[b1].get(b2, 0) >= 0.50:
                    print(f"[Seed {seed} R{r_num}] Banker {b1} suspects Banker {b2} = {sus_map[b1][b2]:.2f}")
                    print(f"   Comm: {comm}, Success: {succ}, Chair: {r['chair_id']}")
                    print(f"   Bankers: {bankers}")
                    print(f"   Submitted cards: {r.get('submitted')}")
                    sys.exit(0)
