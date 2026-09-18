import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match
from collections import Counter

print("=== POR QUE O CHAIRMAN BANQUEIRO ESCOLHE ESTAGIÁRIO NA R3? ===")

chosen_reasons = Counter()

for g in range(300):
    res = simulate_single_match(g, seed=800000 + g, record_trace=True)
    if len(res['rounds_data']) >= 3:
        r3 = res['rounds_data'][2]
        chair_id = r3['chair_id']
        comm = r3['committee']
        players = res['players_metadata']
        banker_ids = [p['id'] for p in players if p['role'] == 'Banqueiro']
        intern_ids = [p['id'] for p in players if p['role'] == 'Estagiario']
        
        if chair_id in banker_ids and chair_id in comm:
            interns_in_comm = [pid for pid in comm if pid in intern_ids]
            if interns_in_comm:
                # O Chairman Banqueiro incluiu pelo menos 1 Estagiário. Por quê?
                # Quem eram os outros 2 banqueiros?
                other_bankers = [b for b in banker_ids if b != chair_id]
                decls = r3['declarations']
                # Ver as suspeitas do chair sobre os banqueiros vs estagiários escolhidos
                chair_sus = r3['suspicions']['by_banker'][chair_id]
                chosen_intern = interns_in_comm[0]
                
                # Motivo 1: Insumo. O estagiário declarou insumo e algum outro banqueiro não?
                intern_claimed_req = decls[chosen_intern]['claims_req']
                bankers_claimed_req = sum(1 for b in other_bankers if decls[b]['claims_req'])
                req_needed = r3['contract']['req_count']
                
                if intern_claimed_req and bankers_claimed_req < req_needed:
                    chosen_reasons["intern_had_req_banker_did_not"] += 1
                elif any(decls[b]['prefers_bench'] for b in other_bankers):
                    chosen_reasons["a_banker_preferred_bench"] += 1
                elif any(chair_sus[b] > chair_sus[chosen_intern] for b in other_bankers):
                    chosen_reasons["a_banker_had_higher_sus_than_intern"] += 1
                else:
                    chosen_reasons["other"] += 1

print("Distribuição de motivos:")
for k, v in chosen_reasons.items():
    print(f"  {k}: {v}")
