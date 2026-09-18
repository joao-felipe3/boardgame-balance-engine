import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match
from collections import Counter

print("=== TESTE COM HEURÍSTICA DE VOTAÇÃO HUMANA ===")

# Vamos simular partidas e medir vitórias
banker_wins = 0
intern_wins = 0
for i in range(1000):
    res = simulate_single_match(i, seed=600000 + i)
    if res['winner'] == 'Banqueiro':
        banker_wins += 1
    else:
        intern_wins += 1

print(f"Resultado Atual (1000 jogos):")
print(f"  WR Banqueiros : {banker_wins/10:.1f}%")
print(f"  WR Estagiários: {intern_wins/10:.1f}%")
