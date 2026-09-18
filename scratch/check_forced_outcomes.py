import sys, os
sys.path.insert(0, os.path.abspath('.'))
from src.btg import simulate_single_match, Role, BankerProfile, InternProfile
from collections import Counter
import src.btg.engine as engine_module

# Monkey-patch _forced_score or trace forced committee selection
original_sim = engine_module.simulate_single_match

forced_rounds_data = []

# Let's run 200 matches
for seed in range(200):
    res = simulate_single_match(seed, seed=330000 + seed, record_trace=True)
    if res['forced_committees'] > 0:
        meta = res['players_metadata']
        roles = {p['id']: p['role'] for p in meta}
        # In this match, res['winner']
        forced_rounds_data.append((res['winner'], roles, res['forced_committees']))

print(f"Total matches with forced committees: {len(forced_rounds_data)} / 200")
winners_in_forced = Counter(x[0] for x in forced_rounds_data)
print(f"Winners in matches with forced committees: {winners_in_forced}")
