import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import numpy as np
from src.btg.constants import Role, CardType, BankerProfile, InternProfile, SEVEN_TIERS_CATALOG
from src.btg.deck import DeckManager, ResourceCard
from src.btg.player import PlayerAI

rng = np.random.default_rng(123)
p0 = PlayerAI(0, Role.BANKER, BankerProfile.BALANCED, rng)
contract = SEVEN_TIERS_CATALOG[3][0]

# Vamos ver cada condição em vote_on_proposal para p0
proposer = 0
committee = [0, 1, 2]

# Vamos rodar passo a passo:
print(f"proposer in known_traitors: {proposer in p0.known_traitors}")
print(f"any committee in known_traitors: {any(p in p0.known_traitors for p in committee)}")
print(f"p0 in committee: {0 in committee}")
others = [p for p in committee if p != 0]
print(f"others: {others}")
print(f"suspicions: {p0.suspicions}")
unproven = sum(1 for p in others if p0.suspicions[p] >= 0.35)
print(f"unproven count: {unproven}")
max_sus = max([p0.suspicions[p] for p in others], default=0.0)
print(f"max_sus: {max_sus}")
