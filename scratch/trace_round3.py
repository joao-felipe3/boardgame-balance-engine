import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import Role, simulate_single_match
from collections import Counter

print("=== TRACE DETALHADO DA SELEÇÃO DA RODADA 3 ===")

r3_reasons = Counter()
r3_counts = 0
r3_intern_in_comm = 0

for g in range(1000):
    res = simulate_single_match(
        g,
        seed=200000 + g,
        record_trace=True
    )
    
    if len(res['rounds_data']) >= 3:
        r3_counts += 1
        r3 = res['rounds_data'][2] # R3
        comm = r3['committee']
        chair_id = r3['chair_id']
        players = res['players_metadata']
        intern_ids = [p['id'] for p in players if p['role'] == 'Estagiario']
        banker_ids = [p['id'] for p in players if p['role'] == 'Banqueiro']
        
        interns_in_c = [pid for pid in comm if pid in intern_ids]
        if interns_in_c:
            r3_intern_in_comm += 1
            if chair_id in intern_ids:
                r3_reasons["intern_is_chair"] += 1
            else:
                decls = r3['declarations']
                bankers_req = sum(1 for pid in banker_ids if decls[pid]['claims_req'])
                req_needed = r3['contract']['req_count']
                req_comm = r3['contract']['req_commodity']
                
                if req_comm is not None and bankers_req < req_needed:
                    r3_reasons["bankers_lack_req_claims"] += 1
                
                # Suspeitas do chair
                chair_sus = r3['suspicions']['by_banker'].get(chair_id, {})
                min_intern_sus = min([chair_sus[i_id] for i_id in intern_ids], default=1.0)
                max_banker_sus = max([chair_sus[b_id] for b_id in banker_ids if b_id != chair_id], default=0.0)
                if min_intern_sus < max_banker_sus:
                    r3_reasons["intern_has_lower_sus_than_a_banker"] += 1
                
                if any(decls[b_id]['prefers_bench'] for b_id in banker_ids):
                    r3_reasons["some_banker_prefers_bench"] += 1

print(f"Total R3 avaliadas: {r3_counts}")
print(f"R3 com Estagiário no comitê: {r3_intern_in_comm} ({r3_intern_in_comm/r3_counts*100:.1f}%)")
print("Causas identificadas quando Chairman é Banqueiro e escolhe Estagiário:")
for k, v in r3_reasons.items():
    print(f"  {k}: {v} ({v/r3_counts*100:.1f}%)")
