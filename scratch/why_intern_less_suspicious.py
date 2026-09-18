import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import Role, simulate_single_match

print("=== INVESTIGAÇÃO: POR QUE ESTAGIÁRIO TEM MENOR SUSPEITA QUE BANQUEIRO NA R3? ===")

samples = 0
for g in range(500):
    res = simulate_single_match(g, seed=300000 + g, record_trace=True)
    if len(res['rounds_data']) >= 3:
        r3 = res['rounds_data'][2]
        chair_id = r3['chair_id']
        players = res['players_metadata']
        intern_ids = [p['id'] for p in players if p['role'] == 'Estagiario']
        banker_ids = [p['id'] for p in players if p['role'] == 'Banqueiro']
        
        if chair_id in banker_ids:
            chair_sus = r3['suspicions']['by_banker'].get(chair_id, {})
            # Achar se algum estagiário tem menor suspeita que algum banqueiro
            for i_id in intern_ids:
                for b_id in banker_ids:
                    if b_id != chair_id and chair_sus.get(i_id, 0) < chair_sus.get(b_id, 0):
                        print(f"Jogo {g} | Chair {chair_id} (Banqueiro): Estag {i_id} (sus={chair_sus[i_id]:.2f}) < Banqueiro {b_id} (sus={chair_sus[b_id]:.2f})")
                        print(f"   R1 comm: {res['rounds_data'][0]['committee']} | Succ: {res['rounds_data'][0]['is_success']}")
                        print(f"   R2 comm: {res['rounds_data'][1]['committee']} | Succ: {res['rounds_data'][1]['is_success']}")
                        print(f"   R1 decls: {res['rounds_data'][0]['declarations']}")
                        samples += 1
                        break
                if samples >= 5:
                    break
        if samples >= 5:
            break
