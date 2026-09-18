import sys, os
sys.path.insert(0, os.path.abspath('.'))
from src.btg import simulate_single_match
for s in range(20):
    seed = 123450 + s
    res = simulate_single_match(s, seed=seed)
    if res['total_vetoes'] >= 3:
        print(f"Match index {s}, seed {seed}, winner={res['winner']}, vetoes={res['total_vetoes']}, forced={res['forced_committees']}")
