import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Vamos testar modificando temporariamente a função ou rodando uma cópia
import copy
from src.btg import simulate_single_match, InternProfile, BankerProfile, Role

# Vamos rodar 500 partidas atuais como baseline
b_wins = 0
for i in range(500):
    res = simulate_single_match(i, seed=20260900 + i, banker_profile="MIXED", intern_profile="MIXED")
    if res['winner'] == 'Banqueiro':
        b_wins += 1
print(f"Baseline Atual (500 partidas): Banqueiros venceram {b_wins}/500 ({b_wins/5:.1f}%)")
