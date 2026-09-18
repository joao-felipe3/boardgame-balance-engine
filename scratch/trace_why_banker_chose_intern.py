import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match, InternProfile, BankerProfile
from src.btg import Role

# Vamos rodar partidas e encontrar a primeira onde o Chairman Banqueiro escolheu um comitê com Estagiário na R3
for seed in range(100):
    match = simulate_single_match(seed, seed=77700 + seed, banker_profile="MIXED", intern_profile="MIXED", record_trace=True)
    roles = {p['id']: p['role'] for p in match['players_metadata']}
    intern_ids = {pid for pid, r in roles.items() if r in ('Estagiario', 'Estagiário')}
    banker_ids = {pid for pid, r in roles.items() if r == 'Banqueiro'}
    
    # Procurar round_num == 3 ou tier == 3
    for r in match['rounds_data']:
        if r['contract']['tier'] in (3, 4):
            chair = r['chair_id']
            comm = r['committee']
            int_in_comm = [p for p in comm if p in intern_ids]
            if roles[chair] == 'Banqueiro' and len(int_in_comm) > 0:
                print(f"ENCONTRADO NO JOGO {seed}, TIER {r['contract']['tier']}:")
                print(f"Chairman: P{chair} (Banqueiro)")
                print(f"Banqueiros reais: {sorted(banker_ids)}")
                print(f"Estagiários reais: {sorted(intern_ids)}")
                print(f"Comitê Escolhido: {comm} (Contém estagiário: {int_in_comm})")
                print(f"Suspeitas do Chairman P{chair}:")
                sus_dict = r['suspicions']['by_banker'].get(chair, {})
                for pid in range(5):
                    print(f"  P{pid} ({roles[pid]}): sus={sus_dict.get(pid, 'N/A')}")
                print(f"Declarações na rodada:")
                for pid, dec in r['declarations'].items():
                    print(f"  P{pid}: claims_req={dec['claims_req']}, val={dec['claimed_val']}, bench={dec['prefers_bench']}")
                sys.exit(0)
