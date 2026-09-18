import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match, Role

# Inspecionar o primeiro jogo onde um banqueiro desconfia de outro
for seed in range(100):
    match = simulate_single_match(seed, seed=12345 + seed, banker_profile="MIXED", intern_profile="MIXED", record_trace=True)
    roles = {p['id']: p['role'] for p in match['players_metadata']}
    banker_ids = sorted([pid for pid, r in roles.items() if r == 'Banqueiro'])
    
    last_r = match['rounds_data'][-1]
    sus_by_banker = last_r['suspicions']['by_banker']
    
    found = False
    for b1 in banker_ids:
        for b2 in banker_ids:
            if b1 != b2 and sus_by_banker[b1].get(b2, 0) >= 0.50:
                print(f"JOGO {seed}: P{b1} (Banqueiro) desconfia de P{b2} (Banqueiro) com sus={sus_by_banker[b1][b2]}")
                print(f"Banqueiros: {banker_ids}")
                print(f"Estagiários: {[pid for pid, r in roles.items() if r != 'Banqueiro']}")
                print("\nHISTÓRICO DAS RODADAS:")
                for r in match['rounds_data']:
                    r_num = r['round_num']
                    tier = r['contract']['tier']
                    chair = r['chair_id']
                    comm = r['committee']
                    succ = r['is_success']
                    sus_b1_b2 = r['suspicions']['by_banker'][b1].get(b2, 0)
                    print(f"  R{r_num} (Tier {tier}): Chair P{chair}, Comm {comm}, Success={succ} -> P{b1} suspeita de P{b2}: {sus_b1_b2:.2f}")
                found = True
                break
        if found:
            break
    if found:
        break
