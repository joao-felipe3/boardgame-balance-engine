import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match, InternProfile
from collections import defaultdict

print("=== TESTE DE WIN RATE POR PERFIL DE ESTAGIÁRIO (500 PARTIDAS CADA) ===")

for prof in list(InternProfile) + ['MIXED']:
    prof_name = prof.name if isinstance(prof, InternProfile) else prof
    b_wins = 0
    i_wins = 0
    for i in range(500):
        res = simulate_single_match(i, seed=10000 + i, intern_profile=prof, banker_profile='MIXED')
        if res['winner'] == 'Banqueiro':
            b_wins += 1
        else:
            i_wins += 1
    print(f"Perfil {prof_name:15s} | WR Banco: {b_wins/5:.1f}% | WR Estagiários: {i_wins/5:.1f}%")
