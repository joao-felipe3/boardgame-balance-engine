import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match, InternProfile, BankerProfile
from collections import Counter, defaultdict

print("=" * 80)
print("INVESTIGAÇÃO CIRÚRGICA: POR QUE OS ESTAGIÁRIOS VENCEM 60% DAS VEZES?")
print("=" * 80)

n_matches = 500
intern_wins = 0
banker_wins = 0

# Contadores de falhas
fail_by_tier = Counter() # tier -> contagem de falhas
fail_reasons_by_tier = defaultdict(Counter) # tier -> reason -> contagem
interns_in_failed_comm = defaultdict(Counter) # tier -> num_interns -> count
who_proposed_failed_comm = defaultdict(Counter) # tier -> proposer_role -> count
was_forced_when_failed = defaultdict(Counter) # tier -> was_forced -> count

# Por que o Chairman Banqueiro escolhe Estagiários?
banker_chose_intern_reasons = Counter()
banker_chose_intern_tiers = Counter()

# Exame de partidas
for seed in range(n_matches):
    match = simulate_single_match(seed, seed=50000 + seed, banker_profile="MIXED", intern_profile="MIXED", record_trace=True)
    winner = match['winner']
    if winner in ('Estagiario', 'Estagiário'):
        intern_wins += 1
    else:
        banker_wins += 1

    roles = {p['id']: p['role'] for p in match['players_metadata']}
    intern_ids = {pid for pid, r in roles.items() if r in ('Estagiario', 'Estagiário')}
    banker_ids = {pid for pid, r in roles.items() if r in ('Banqueiro',)}

    for r in match['rounds_data']:
        tier = r['contract']['tier']
        comm = r['committee']
        proposer = r['chair_id']
        proposer_role = roles[proposer]
        passed = r['is_success']
        
        has_toxic = any(c.get('type') == 'TOXIC' for d in r.get('submitted', []) for c in d.get('cards', []))
        missing_req = not r['has_req']
        missing_pts = r['total_value'] < r['contract']['target']
        
        if not passed:
            if has_toxic:
                reason = "sabotado (ativo toxico)"
            elif missing_req and missing_pts:
                reason = "sem insumo e sem pontos"
            elif missing_req:
                reason = "sem insumo (req faltou)"
            elif missing_pts:
                reason = f"sem pontos ({r['total_value']}/{r['contract']['target']})"
            else:
                reason = "outro"
        else:
            reason = "sucesso"
            
        interns_count = sum(1 for p in comm if p in intern_ids)

        if proposer_role == 'Banqueiro' and interns_count > 0:
            banker_chose_intern_tiers[tier] += 1

        if not passed:
            fail_by_tier[tier] += 1
            fail_reasons_by_tier[tier][reason] += 1
            interns_in_failed_comm[tier][interns_count] += 1
            who_proposed_failed_comm[tier][proposer_role] += 1

print(f"Total Partidas: {n_matches}")
print(f"Banqueiros venceram: {banker_wins} ({banker_wins/n_matches*100:.1f}%)")
print(f"Estagiários venceram: {intern_wins} ({intern_wins/n_matches*100:.1f}%)\n")

print("-" * 80)
print("ANÁLISE DE TODAS AS FALHAS POR TIER:")
print("-" * 80)
for tier in range(1, 8):
    total_f = fail_by_tier[tier]
    if total_f == 0:
        continue
    print(f"\n>> TIER {tier} (Total de Falhas: {total_f}):")
    print(f"   Motivos de Falha:")
    for reason, c in fail_reasons_by_tier[tier].most_common():
        print(f"     - {reason:25s}: {c:3d} ({c/total_f*100:5.1f}%)")
    print(f"   Estagiários no Comitê que Falhou:")
    for n_int, c in sorted(interns_in_failed_comm[tier].items()):
        print(f"     - {n_int} Estagiários : {c:3d} ({c/total_f*100:5.1f}%)")
    print(f"   Propositor do Comitê que Falhou:")
    for p_role, c in who_proposed_failed_comm[tier].most_common():
        print(f"     - Proposto por {p_role:12s}: {c:3d} ({c/total_f*100:5.1f}%)")

print("\n" + "-" * 80)
print("QUANTAS VEZES O PRÓPRIO CHAIRMAN BANQUEIRO CONVIDOU VOLUNTARIAMENTE UM ESTAGIÁRIO?")
print("-" * 80)
for tier in range(1, 8):
    print(f"  Tier {tier}: {banker_chose_intern_tiers[tier]} vezes")
