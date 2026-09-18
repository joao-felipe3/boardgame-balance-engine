import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match, Role

for seed in [2, 4]:
    match = simulate_single_match(seed, seed=seed, banker_profile="MIXED", intern_profile="MIXED", record_trace=True)
    roles = {p['id']: p['role'] for p in match['players_metadata']}
    print(f"\n================ MATCH {seed} (Winner: {match['winner']}) ================")
    print(f"Roles: {roles}")
    for r in match['rounds_data']:
        r_num = r['round_num']
        chair = r['chair_id']
        comm = r['committee']
        success = r['is_success']
        print(f"\n--- R{r_num} (Target {r['contract']['target']}, Req {r['contract']['req_commodity']}, CommSize {r['contract']['committee_size']}) ---")
        print(f"Chair: P{chair}({roles[chair][0]}) | Comm: {[f'P{p}({roles[p][0]})' for p in comm]}")
        print("Declarations:")
        for pid, dec in r['declarations'].items():
            desc_clean = dec['offered_desc'].encode('ascii', 'replace').decode('ascii')
            print(f"  P{pid}({roles[pid][0]}): claims_req={dec['claims_req']}, claimed_val={dec['claimed_val']}, tokens={dec['tokens_offered']}, bench={dec['prefers_bench']}, desc={desc_clean}")
        submitted_summary = {d['player_id']: [f"{c['type']}({c['base']})" for c in d['cards']] for d in r['submitted']}
        print(f"Submitted: {submitted_summary}")
        print(f"Success: {success} (Val: {r.get('total_value')}, Req: {r.get('has_req')})")
