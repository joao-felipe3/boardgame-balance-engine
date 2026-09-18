import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match, InternProfile, BankerProfile, Role

untested_invited_count = 0
total_r3_r4 = 0

for seed in range(500):
    match = simulate_single_match(seed, seed=70000 + seed, banker_profile="MIXED", intern_profile="MIXED", record_trace=True)
    roles = {p['id']: p['role'] for p in match['players_metadata']}
    
    played_so_far = set()
    for r in match['rounds_data']:
        r_num = r['round_num']
        chair = r['chair_id']
        comm = r['committee']
        
        if r_num in (2, 3, 4) and roles[chair] == 'Banqueiro':
            total_r3_r4 += 1
            # Jogadores que nunca jogaram antes desta rodada
            untested_in_comm = [p for p in comm if p not in played_so_far and p != chair]
            # Havia veteranos disponíveis no banco que já tinham jogado e passado?
            veterans_on_bench = [p for p in played_so_far if p not in comm and p != chair]
            if untested_in_comm and veterans_on_bench:
                untested_invited_count += 1
                
        played_so_far.update(comm)

print(f"Total R2-R4 com Chairman Banqueiro: {total_r3_r4}")
print(f"Vezes que Chairman Banqueiro chamou alguém que NUNCA JOGOU deixando veterano no banco: {untested_invited_count} ({untested_invited_count/total_r3_r4*100:.1f}%)")
