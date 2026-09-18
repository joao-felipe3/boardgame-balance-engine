import sys, os
sys.path.insert(0, os.path.abspath('.'))
from src.btg import simulate_single_match, Role, BankerProfile, InternProfile

# Case A: Inspect R2 pure banker fails
print("=" * 70)
print("INVESTIGANDO CASE A: R2 COM 2 BANQUEIROS QUE FALHAM")
print("=" * 70)

r2_samples = 0
for s in range(500):
    res = simulate_single_match(s, seed=987650 + s, record_trace=True)
    meta = res['players_metadata']
    roles = {p['id']: p['role'] for p in meta}
    for r in res['rounds_data']:
        if r['round_num'] == 2 and not r['is_success']:
            comm = r['committee']
            if all(roles[pid] == 'Banqueiro' for pid in comm):
                r2_samples += 1
                if r2_samples <= 3:
                    c = r['contract']
                    print(f"\nCaso A.{r2_samples} (Match {s}):")
                    print(f"  Contrato: Tier {c['tier']} ({c['name']}), Meta={c['target']}, Req={c['req_commodity']}")
                    print(f"  Comitê: {comm} (Ambos Banqueiros)")
                    print(f"  Mão antes: {[str(c_card) for c_card in r['hands_before'][comm[0]]]} e {[str(c_card) for c_card in r['hands_before'][comm[1]]]}")
                    print(f"  Submetido: {[(cd['player_id'], [x['name'] for x in cd['cards']], cd['tokens_spent']) for cd in r['submitted']]}")
                    print(f"  Sucesso: {r['is_success']}, Has_req: {r['has_req']}, Total_val: {r['total_value']}")
                    print(f"  Banco de reservas: quem estava no banco? {[pid for pid in range(5) if pid not in comm]}")
                    print(f"  3º Banqueiro: {[pid for pid in range(5) if roles[pid] == 'Banqueiro' and pid not in comm]}")

print("\n" + "=" * 70)
print("INVESTIGANDO CASE B: R3 BANQUEIRO CHAIR CONVIDA ESTAGIÁRIO")
print("=" * 70)

r3_samples = 0
for s in range(500):
    res = simulate_single_match(s, seed=987650 + s, record_trace=True)
    meta = res['players_metadata']
    roles = {p['id']: p['role'] for p in meta}
    for r in res['rounds_data']:
        if r['round_num'] == 3 and not r['is_success']:
            ch = r['chair_id']
            comm = r['committee']
            if roles[ch] == 'Banqueiro' and any(roles[pid] == 'Estagiario' for pid in comm):
                r3_samples += 1
                if r3_samples <= 3:
                    c = r['contract']
                    print(f"\nCaso B.{r3_samples} (Match {s}):")
                    print(f"  Contrato: Tier {c['tier']} ({c['name']}), Meta={c['target']}, Req={c['req_commodity']}, ReqCount={c['req_count']}")
                    print(f"  Chair: P{ch} (Banqueiro)")
                    print(f"  Comitê escolhido: {comm} (Roles: {[roles[pid] for pid in comm]})")
                    print(f"  Suspeitas do Chair P{ch}: {r['suspicions']['by_banker'].get(ch)}")
                    print(f"  Declarações públicas: {r['declarations']}")
