import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match, Role

innocent_burned_count = 0
total_matches = 500

for seed in range(total_matches):
    match = simulate_single_match(seed, seed=99900 + seed, banker_profile="MIXED", intern_profile="MIXED", record_trace=True)
    roles = {p['id']: p['role'] for p in match['players_metadata']}
    banker_ids = set([pid for pid, r in roles.items() if r == 'Banqueiro'])
    intern_ids = set([pid for pid, r in roles.items() if r in ('Estagiario', 'Estagiário')])
    
    # Vamos ver no final do jogo as suspeitas que cada banqueiro tem dos outros banqueiros
    last_r = match['rounds_data'][-1]
    sus_by_banker = last_r['suspicions']['by_banker']
    
    for b_id in banker_ids:
        b_sus = sus_by_banker.get(b_id, {})
        for other_b in banker_ids:
            if other_b != b_id:
                if b_sus.get(other_b, 0) >= 0.50:
                    innocent_burned_count += 1
                    break

print(f"Total Partidas: {total_matches}")
print(f"Partidas onde Banqueiros terminaram DESCONFIANDO (sus >= 0.50) de outros BANQUEIROS leais: {innocent_burned_count} ({innocent_burned_count/total_matches*100:.1f}%)")
