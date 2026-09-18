import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match, Role, BankerProfile, InternProfile
from collections import Counter, defaultdict

n_games = 500
intern_wins = 0
banker_wins = 0

fail_cause_by_round = defaultdict(Counter)
intern_presence_in_fails = defaultdict(Counter)
forced_by_round = Counter()
final_scores = Counter()
rounds_interns_scored = Counter()

for i in range(n_games):
    res = simulate_single_match(i, seed=555000 + i, record_trace=True)
    winner = res['winner']
    if winner == 'Banqueiro':
        banker_wins += 1
    else:
        intern_wins += 1
    
    b_score = res['b_score']
    i_score = res['i_score']
    final_scores[f"{b_score}x{i_score}"] += 1

    for r_idx, r in enumerate(res['rounds_data']):
        rnd = r_idx + 1
        if not r['is_success']:
            rounds_interns_scored[rnd] += 1
            has_toxic = any(c.get('card_type') == 'TOXIC' for c in r.get('submitted', []))
            has_req = r.get('has_req', True)
            tot_val = r.get('total_value', 0)
            target = r['contract']['target']
            
            comm = r['committee']
            interns_in_comm = [pid for pid in comm if res['players_metadata'][pid]['role'] in ('Estagiario', 'Estagiário', 'INTERN')]
            
            if not has_req:
                cause = "QUEBRA_INSUMO"
            elif has_toxic:
                cause = "ATIVO_TOXICO"
            elif tot_val < target:
                cause = "DEFICIT_VALOR"
            else:
                cause = "OUTRO"
            
            fail_cause_by_round[rnd][cause] += 1
            intern_presence_in_fails[rnd][len(interns_in_comm)] += 1

print(f"Total Partidas: {n_games}")
print(f"Vitórias Banqueiros: {banker_wins} ({banker_wins/n_games*100:.1f}%)")
print(f"Vitórias Estagiários: {intern_wins} ({intern_wins/n_games*100:.1f}%)")

print("\nPlacares Finais mais comuns:")
for sc, count in final_scores.most_common(10):
    print(f"  {sc:10s}: {count:4d} ({count/n_games*100:5.1f}%)")

print("\nRodadas onde os Estagiários pontuaram (Falhas de Contrato):")
for rnd in sorted(rounds_interns_scored.keys()):
    cnt = rounds_interns_scored[rnd]
    print(f"\n--- RODADA {rnd} (Total falhas: {cnt} em {n_games} jogos = {cnt/n_games*100:.1f}%) ---")
    print(f"  Presença de Estagiários no comitê:")
    for num_interns, c in intern_presence_in_fails[rnd].items():
        print(f"    {num_interns} Estagiários: {c:4d} vezes ({c/cnt*100:5.1f}%)")
    print(f"  Causas da falha:")
    for cause, c in fail_cause_by_round[rnd].items():
        print(f"    {cause:18s}: {c:4d} vezes ({c/cnt*100:5.1f}%)")
