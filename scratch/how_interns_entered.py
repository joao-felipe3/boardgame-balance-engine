import sys, os
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match, Role
from collections import Counter

# Let's inspect 500 matches and see HOW the interns got into the committee in R3, R4, R5
how_intern_entered = Counter()
banker_chair_intern_count = 0

for i in range(500):
    res = simulate_single_match(i, seed=444000 + i, record_trace=True)
    for r_idx, r in enumerate(res['rounds_data']):
        rnd = r_idx + 1
        comm = r['committee']
        interns = [pid for pid in comm if res['players_metadata'][pid]['role'] in ('Estagiario', 'Estagiário', 'INTERN')]
        if interns:
            chair_id = r['chair_id']
            chair_role = res['players_metadata'][chair_id]['role']
            # Was this committee approved by vote or forced?
            # If r['votes'] has votes, let's see votes
            v_for = sum(1 for v in r['votes'].values() if v)
            if v_for >= 3:
                # approved by vote
                key = f"R{rnd}: Aprovado por Voto (Chair={chair_role})"
            else:
                key = f"R{rnd}: Imposto pelo Banco Central (3 vetos)"
            how_intern_entered[key] += 1

print("Como os Estagiários entraram no comitê nas rodadas disputadas (500 jogos):")
for k, count in sorted(how_intern_entered.items()):
    print(f"  {k:55s}: {count:4d}")
