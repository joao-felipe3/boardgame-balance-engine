import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match, Role

banker_wins = 0
sus_50_count = 0
sus_75_count = 0
sus_100_count = 0

for seed in range(500):
    match = simulate_single_match(seed, seed=seed, banker_profile="MIXED", intern_profile="MIXED", record_trace=True)
    if match['winner'] in ('Banqueiro', Role.BANKER.value):
        banker_wins += 1
    roles = {p['id']: p['role'] for p in match['players_metadata']}
    banker_ids = [pid for pid, r in roles.items() if r in ('Banqueiro', Role.BANKER.value)]
    last_r = match['rounds_data'][-1]
    sus_by_banker = last_r['suspicions']['by_banker']
    
    max_innocent_sus = max(sus_by_banker[b1].get(b2, 0) for b1 in banker_ids for b2 in banker_ids if b1 != b2)
    if max_innocent_sus >= 0.50:
        sus_50_count += 1
    if max_innocent_sus >= 0.75:
        sus_75_count += 1
    if max_innocent_sus >= 0.99:
        sus_100_count += 1

print(f"Banker Win Rate: {banker_wins}/500 ({banker_wins/500*100:.1f}%)")
print(f"Innocents with sus >= 0.50 (Conflict/Neutral): {sus_50_count}/500 ({sus_50_count/500*100:.1f}%)")
print(f"Innocents with sus >= 0.75 (False Accusations): {sus_75_count}/500 ({sus_75_count/500*100:.1f}%)")
print(f"Innocents with sus == 1.00 (Burned as Traitor): {sus_100_count}/500 ({sus_100_count/500*100:.1f}%)")
