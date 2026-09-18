import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match, InternProfile, BankerProfile, Role

discarded_pure_banker_for_fake_req = 0
total_r3_r5_with_banker_chair = 0

for seed in range(500):
    match = simulate_single_match(seed, seed=80000 + seed, banker_profile="MIXED", intern_profile="MIXED", record_trace=True)
    roles = {p['id']: p['role'] for p in match['players_metadata']}
    banker_ids = tuple(sorted([pid for pid, r in roles.items() if r == 'Banqueiro']))
    intern_ids = set([pid for pid, r in roles.items() if r in ('Estagiario', 'Estagiário')])
    
    for r in match['rounds_data']:
        r_num = r['round_num']
        c_size = r['contract']['committee_size']
        chair = r['chair_id']
        comm = r['committee']
        req_count = r['contract']['req_count']
        
        if c_size == 3 and roles[chair] == 'Banqueiro' and req_count >= 2:
            total_r3_r5_with_banker_chair += 1
            # Vamos ver se os 3 banqueiros poderiam ter sido chamados
            # Se o comitê escolhido tinha estagiário:
            if any(p in intern_ids for p in comm):
                # Por que não chamou banker_ids?
                # Vamos checar quantos banqueiros declararam claims_req
                banker_claims = sum(1 for b in banker_ids if r['declarations'][b]['claims_req'])
                if banker_claims < req_count:
                    discarded_pure_banker_for_fake_req += 1

print(f"Total de rodadas com c_size=3 e req_count>=2 presididas por Banqueiro: {total_r3_r5_with_banker_chair}")
print(f"Vezes que comitê puro de banqueiros foi descartado porque banqueiros tinham < {req_count} insumos declarados e estagiário mentiu: {discarded_pure_banker_for_fake_req} ({discarded_pure_banker_for_fake_req/total_r3_r5_with_banker_chair*100:.1f}%)")
