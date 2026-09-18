import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match

print("=== ENCONTRANDO QUEM MARCOU BANQUEIRO COM SUSPEITA ALTA ===")

# Vamos rodar o Jogo 0 que deu Chair 2 achando Banqueiro 3 com sus 1.00
res = simulate_single_match(0, seed=300000, record_trace=True)

for p in res['players_metadata']:
    print(f"Player {p['id']}: Role={p['role']}, Profile={p['profile']}")

for r_idx, r in enumerate(res['rounds_data']):
    print(f"\n--- RODADA {r_idx+1} ---")
    print(f"  Contrato: {r['contract']['name']}, Req: {r['contract']['req_commodity']}")
    print(f"  Chair: {r['chair_id']}, Comm: {r['committee']}, Supplier: {r['promised_supplier']}")
    print(f"  Sucesso: {r['is_success']}")
    print(f"  Submitted:")
    for s in r['submitted']:
        print(f"     Player {s['player_id']}: {[c['type'] for c in s['cards']]} (req_resp={s.get('is_req_responsible')})")
    print(f"  Suspeitas pós-rodada do Chair 2:")
    if 'suspicions' in r and 'by_banker' in r['suspicions']:
        for b_id, sus_map in r['suspicions']['by_banker'].items():
            print(f"     Banker {b_id}: {sus_map}")
