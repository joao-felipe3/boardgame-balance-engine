import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match

print("=== INSPECIONANDO HISTÓRICO R1/R2 ONDE BANQUEIRO FICOU COM MAIOR SUSPEITA QUE ESTAGIÁRIO ===")

samples = 0
for g in range(300):
    res = simulate_single_match(g, seed=900000 + g, record_trace=True)
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
                other_bankers = [b for b in banker_ids if b != chair_id]
                chair_sus = r3['suspicions']['by_banker'][chair_id]
                chosen_intern = interns_in_comm[0]
                
                bad_bankers = [b for b in other_bankers if chair_sus[b] > chair_sus[chosen_intern]]
                if bad_bankers:
                    bb = bad_bankers[0]
                    print(f"\n--- CASO {samples+1} (Jogo {g}) ---")
                    print(f"Chair {chair_id} (Banqueiro): Escolheu Estagiário {chosen_intern} (sus={chair_sus[chosen_intern]:.2f}) em vez de Banqueiro {bb} (sus={chair_sus[bb]:.2f})")
                    print(f"Banqueiros reais: {banker_ids}, Estagiários reais: {intern_ids}")
                    r1 = res['rounds_data'][0]
                    r2 = res['rounds_data'][1]
                    print(f"  R1: Chair={r1['chair_id']}, Comm={r1['committee']}, Succ={r1['is_success']}, Submissions={[ (s['player_id'], [c['type'] for c in s['cards']]) for s in r1['submitted'] ]}")
                    print(f"  R2: Chair={r2['chair_id']}, Comm={r2['committee']}, Succ={r2['is_success']}, Submissions={[ (s['player_id'], [c['type'] for c in s['cards']]) for s in r2['submitted'] ]}")
                    samples += 1
                    if samples >= 5:
                        break

