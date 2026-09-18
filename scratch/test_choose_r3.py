import sys, os
sys.path.insert(0, os.path.abspath('.'))
from src.btg import Role, BankerProfile, InternProfile
from src.btg.player import PlayerAI, PlayerDeclaration
from src.btg.constants import SEVEN_TIERS_CATALOG, CardType
import numpy as np

contract = SEVEN_TIERS_CATALOG[3][0]

p2 = PlayerAI(2, Role.BANKER, BankerProfile.BALANCED, np.random.default_rng(42))
players = [
    PlayerAI(0, Role.INTERN, InternProfile.B_SLEEPER, np.random.default_rng(42)),
    PlayerAI(1, Role.BANKER, BankerProfile.BALANCED, np.random.default_rng(42)),
    p2,
    PlayerAI(3, Role.INTERN, InternProfile.B_SLEEPER, np.random.default_rng(42)),
    PlayerAI(4, Role.BANKER, BankerProfile.BALANCED, np.random.default_rng(42)),
]

# Set tokens: P4 was on the bench for 2 rounds, so P4 has 2 tokens!
players[4].interest_tokens = 2
# P0 and P1 have 0 tokens
players[0].interest_tokens = 0
players[1].interest_tokens = 0

declarations = {
    0: PlayerDeclaration(0, claims_req=True, claimed_value=5, req_commodity_value=3, tokens_offered=0, prefers_bench=False, offered_desc=''),
    1: PlayerDeclaration(1, claims_req=True, claimed_value=3, req_commodity_value=3, tokens_offered=0, prefers_bench=False, offered_desc=''),
    2: PlayerDeclaration(2, claims_req=False, claimed_value=1, req_commodity_value=0, tokens_offered=0, prefers_bench=False, offered_desc=''),
    3: PlayerDeclaration(3, claims_req=True, claimed_value=5, req_commodity_value=3, tokens_offered=0, prefers_bench=False, offered_desc=''),
    4: PlayerDeclaration(4, claims_req=True, claimed_value=5, req_commodity_value=3, tokens_offered=2, prefers_bench=False, offered_desc=''),
}

# Now compare score of [0, 1, 2] vs [1, 2, 4]:
# If we favor total_tokens offered:
# [0, 1, 2] has tokens_offered = 0
# [1, 2, 4] has tokens_offered = 2
print("Tokens [0, 1, 2]:", sum(declarations[pid].tokens_offered for pid in [0, 1, 2]))
print("Tokens [1, 2, 4]:", sum(declarations[pid].tokens_offered for pid in [1, 2, 4]))
