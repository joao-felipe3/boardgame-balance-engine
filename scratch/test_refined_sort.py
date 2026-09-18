import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Vamos testar o impacto com a nova lógica
from src.btg import simulate_single_match

print("Testando 1000 partidas com o modelo atual:")
b_wins = 0
forced_total = 0
vetoes_total = 0

for i in range(1000):
    res = simulate_single_match(i, seed=303000 + i, banker_profile="MIXED", intern_profile="MIXED")
    if res['winner'] == 'Banqueiro':
        b_wins += 1
    forced_total += res['forced_committees']
    vetoes_total += res['total_vetoes']

print(f"Vitórias Banqueiros: {b_wins}/1000 ({b_wins/10:.1f}%)")
print(f"Comitês Forçados: {forced_total} ({forced_total/10:.1f}%)")
print(f"Média Vetos: {vetoes_total/1000:.2f}")
