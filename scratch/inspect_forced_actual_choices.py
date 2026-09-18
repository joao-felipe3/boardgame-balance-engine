import sys, os
sys.path.insert(0, os.path.abspath('.'))
from src.btg import simulate_single_match, Role, BankerProfile, InternProfile
import src.btg.engine as engine_module
import itertools

# Let's intercept forced committee in engine.py
forced_details = []

# Let's inspect 50 matches
for seed in range(50):
    res = simulate_single_match(seed, seed=550000 + seed, record_trace=True)
    if res['forced_committees'] > 0:
        meta = res['players_metadata']
        roles = {p['id']: p['role'] for p in meta}
        for r in res['rounds_data']:
            if r['round_num'] in [1, 2, 3, 4, 5, 6, 7]:
                # Check if this round was forced
                # Let's check votes
                pass

print("Done")
