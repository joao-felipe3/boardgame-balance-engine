import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match, Role

# Let's inspect baseline innocent burned and win rate on seeds 0..499
base_wins = 0
base_burned = 0
for seed in range(500):
    match = simulate_single_match(seed, seed=seed, banker_profile="MIXED", intern_profile="MIXED", record_trace=False)
    if match['winner'] in ('Banqueiro', Role.BANKER.value):
        base_wins += 1
    roles = {p['id']: p['role'] for p in match['players_metadata']}
    banker_ids = [pid for pid, r in roles.items() if r in ('Banqueiro', Role.BANKER.value)]
    # check if any banker suspected another banker >= 0.50
    # we can check suspicions by banker in rounds_data or by simulating
print(f"Current Win Rate: {base_wins}/500 ({base_wins/500*100:.1f}%)")
