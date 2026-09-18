import sys, os
sys.path.insert(0, os.path.abspath('.'))
from src.btg import simulate_single_match

empty_hand_count = 0
total_matches = 500
matches_with_empty_hands = 0
for s in range(total_matches):
    res = simulate_single_match(s, seed=500000 + s, record_trace=True)
    had_empty = False
    for r in res['rounds_data']:
        for cd in r['submitted']:
            if len(cd['cards']) == 0:
                empty_hand_count += 1
                had_empty = True
                if empty_hand_count <= 8:
                    c = r['contract']
                    print(f"Match {s}, R{r['round_num']} (T{c['tier']}, req_cost={c['cost_per_player']}): P{cd['player_id']} ({res['players_metadata'][cd['player_id']]['role']}) submitted {len(cd['cards'])} cards!")
    if had_empty:
        matches_with_empty_hands += 1

print(f"\nTotal zero-card submissions in {total_matches} matches: {empty_hand_count}")
print(f"Matches with at least one empty hand: {matches_with_empty_hands} ({matches_with_empty_hands/total_matches*100:.1f}%)")
