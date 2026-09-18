import sys, os
sys.path.insert(0, os.path.abspath('.'))
from src.btg import simulate_single_match, Role, BankerProfile, InternProfile

print("Inspecionando por que Banqueiro Chairman chama Estagiário na R4...")
count = 0
for s in range(500):
    res = simulate_single_match(s, seed=123400 + s, record_trace=True)
    meta = res['players_metadata']
    roles = {p['id']: p['role'] for p in meta}
    for r in res['rounds_data']:
        if r['round_num'] == 4 and not r['is_success']:
            ch = r['chair_id']
            comm = r['committee']
            if roles[ch] == 'Banqueiro' and any(roles[pid] == 'Estagiario' for pid in comm):
                count += 1
                if count <= 4:
                    c = r['contract']
                    print(f"\nCaso {count} (Match {s}):")
                    print(f"  Contrato: Tier {c['tier']} ({c['name']}), Meta={c['target']}, Req={c['req_commodity']}")
                    print(f"  Papeis: {roles}")
                    print(f"  Chair: P{ch} (Banqueiro)")
                    print(f"  Comite escolhido: {comm} (Roles: {[roles[pid] for pid in comm]})")
                    print(f"  Suspeitas de P{ch}: {r['suspicions']['by_banker'].get(ch)}")
                    print(f"  Known traitors de P{ch}: {r['suspicions']['known_traitors'].get(ch)}")
                    print(f"  Declaracoes: {[(pid, d['claims_req'], d['claimed_val']) for pid, d in r['declarations'].items()]}")
