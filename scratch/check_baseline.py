import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Let's test the complete package by modifying engine.py and player.py
# First let's backup original methods or test directly
from src.btg import simulate_single_match, Role, BankerProfile, InternProfile
from src.btg.constants import CardType
import src.btg.engine as engine
import src.btg.player as player_mod

# Let's see current win rate without edits:
print("Testing with current codebase baseline...")
banker_wins_base = 0
burned_base = 0
for seed in range(500):
    match = simulate_single_match(seed, seed=seed, banker_profile="MIXED", intern_profile="MIXED", record_trace=True)
    if match['winner'] in ('Banqueiro', Role.BANKER.value):
        banker_wins_base += 1
    roles = {p['id']: p['role'] for p in match['players_metadata']}
    banker_ids = [pid for pid, r in roles.items() if r == 'Banqueiro']
    last_r = match['rounds_data'][-1]
    sus_by_banker = last_r['suspicions']['by_banker']
    if any(sus_by_banker[b1].get(b2, 0) >= 0.50 for b1 in banker_ids for b2 in banker_ids if b1 != b2):
        burned_base += 1

print(f"Base Banker WR: {banker_wins_base}/500 ({banker_wins_base/500*100:.1f}%)")
print(f"Base Innocent Burned: {burned_base}/500 ({burned_base/500*100:.1f}%)")
