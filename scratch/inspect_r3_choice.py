import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import random, itertools
from src.btg import simulate_single_match, InternProfile, BankerProfile, Role
from src.btg import PlayerAI, DeckManager, ResourceCard, CardType, PlayerDeclaration, ContractSpec
from src.btg.constants import SEVEN_TIERS_CATALOG

# Vamos rodar o jogo 1 manualmente reproduzindo o estado exato da R3
rng = random.Random(77701)
roles = [Role.BANKER, Role.INTERN, Role.BANKER, Role.BANKER, Role.INTERN] # do seed 77701
# Vamos verificar os roles exatos gerados para seed 77701
match = simulate_single_match(1, seed=77701, banker_profile="MIXED", intern_profile="MIXED", record_trace=True)
roles = {p['id']: p['role'] for p in match['players_metadata']}
print("Roles:", roles)
r1 = match['rounds_data'][0]
r2 = match['rounds_data'][1]
r3 = match['rounds_data'][2]

print("R1 committee:", r1['committee'], "passed:", r1['is_success'])
print("R2 committee:", r2['committee'], "passed:", r2['is_success'])
print("R3 chair:", r3['chair_id'], "chosen:", r3['committee'])

# Vamos ver as suspeitas do chair P2 na R3:
chair_sus = r3['suspicions']['by_banker'][2]
print("Suspeitas de P2:", chair_sus)
# Comitê puro de banqueiros: [0, 2, 3]
# Comitê escolhido: [2, 3, 4]

# avg_sus:
# Para [0, 2, 3]:
# members != 2: 0 (0.38) e 3 (0.18).
# avg_sus = (0.38 + 0.18) / 3 = 0.18666... round(x, 2) = 0.19!
# Para [2, 3, 4]:
# members != 2: 3 (0.18) e 4 (0.40).
# avg_sus = (0.18 + 0.40) / 3 = 0.19333... round(x, 2) = 0.19!

print("avg_sus [0, 2, 3]:", round((chair_sus[0] + chair_sus[3]) / 3, 2))
print("avg_sus [2, 3, 4]:", round((chair_sus[3] + chair_sus[4]) / 3, 2))
