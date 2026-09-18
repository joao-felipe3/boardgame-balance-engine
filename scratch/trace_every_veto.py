import sys, os
sys.path.insert(0, os.path.abspath('.'))
from src.btg import simulate_single_match, Role, BankerProfile, InternProfile
from src.btg.player import PlayerAI
from collections import Counter

original_vote = PlayerAI.vote_on_proposal

vetoed_proposals = []

def tracking_vote(self, proposer, committee, contract, round_num, conflict_pairs=None, consecutive_vetoes=0, declarations=None):
    v = original_vote(self, proposer, committee, contract, round_num, conflict_pairs, consecutive_vetoes, declarations)
    return v

# Let's inspect where consecutive_vetoes increment in engine.py
# Let's run a script that prints traces of 10 matches
res_list = []
for s in range(20):
    res = simulate_single_match(s, seed=123450 + s, record_trace=True)
    if res['total_vetoes'] >= 3:
        res_list.append(res)
        if len(res_list) >= 3:
            break

for idx, res in enumerate(res_list):
    meta = res['players_metadata']
    roles = {p['id']: p['role'] for p in meta}
    print(f"\n{'='*75}\nPARTIDA {idx+1} (Winner: {res['winner']}, Vetoes: {res['total_vetoes']}, Forced: {res['forced_committees']})")
    print(f"Papeis: {roles}")
    for r in res['rounds_data']:
        c = r['contract']
        v_dict = r['votes']
        v_yes = [pid for pid, v in v_dict.items() if v]
        v_no = [pid for pid, v in v_dict.items() if not v]
        print(f"  R{r['round_num']} (Tier {c['tier']}, Meta {c['target']}): Chair P{r['chair_id']} ({roles[r['chair_id']]}) -> Comite {r['committee']}")
        print(f"    Votos: SIM={v_yes}, NAO={v_no} | Sucesso={r['is_success']}")
