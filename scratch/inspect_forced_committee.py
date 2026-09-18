import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Vamos rodar uma simulação manual de uma rodada com vetos
import numpy as np
from src.btg.constants import Role, CardType, BankerProfile, InternProfile, SEVEN_TIERS_CATALOG
from src.btg.deck import DeckManager, ResourceCard
from src.btg.player import PlayerAI
from src.btg.engine import choose_optimal_committee

rng = np.random.default_rng(123)

# Roster de teste
deck = DeckManager(seed=123)
players = [
    PlayerAI(0, Role.BANKER, BankerProfile.BALANCED, rng),
    PlayerAI(1, Role.BANKER, BankerProfile.BALANCED, rng),
    PlayerAI(2, Role.BANKER, BankerProfile.BALANCED, rng),
    PlayerAI(3, Role.INTERN, InternProfile.B_SLEEPER, rng),
    PlayerAI(4, Role.INTERN, InternProfile.A_AGGRESSIVE, rng),
]
for p in players:
    p.hand = [ResourceCard(CardType.CO), ResourceCard(CardType.TI)] + deck.draw_blind(2)

contract = SEVEN_TIERS_CATALOG[3][0] # Tier 3 (Sindicato de Titanio: 3 membros, 2x TI)
print(f"Contrato: {contract.name}, req={contract.req_commodity}, count={contract.req_commodity_count}, target={contract.target_value}")

for p in players:
    print(f"Player {p.id} ({p.role.name}): Hand={[c.card_type.name for c in p.hand]}")

declarations = {p.id: p.make_public_declaration(contract, 3) for p in players}
for pid, d in declarations.items():
    print(f"  Decl P{pid}: claims_req={d.claims_req}, val={d.claimed_value}, bench={d.prefers_bench}")

for attempt in range(3):
    chair = players[attempt]
    chosen_comm, assigned_sup = choose_optimal_committee(chair, players, contract, declarations)
    print(f"\nTentativa {attempt+1} (Chair P{chair.id}): Comm={chosen_comm}, Sup={assigned_sup}")
    votes = {}
    for p in players:
        votes[p.id] = p.vote_on_proposal(chair.id, chosen_comm, contract, 3, consecutive_vetoes=attempt, declarations=declarations)
    print(f"  Votos: {votes} -> Aprovado? {sum(1 for v in votes.values() if v) >= 3}")
