import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import Role, BankerProfile, InternProfile
from src.btg.constants import SEVEN_TIERS_CATALOG, CardType
from src.btg.deck import DeckManager, ResourceCard
from src.btg.player import PlayerAI
import src.btg.engine as engine
import numpy as np

seed = 2
rng = np.random.default_rng(seed + 1000)
roles = [Role.BANKER, Role.BANKER, Role.BANKER, Role.INTERN, Role.INTERN]
rng.shuffle(roles)
players = [
    PlayerAI(i, roles[i], BankerProfile.BALANCED if roles[i]==Role.BANKER else InternProfile.B_SLEEPER, rng)
    for i in range(5)
]
deck = DeckManager(seed=seed + 1000)
for p in players:
    p.hand = [ResourceCard(CardType.CO), ResourceCard(CardType.TI)] + deck.draw_blind(2)

# Rodada 1
# P0 e P1 jogam
# R1 falha porque P1 é Intern e sabota
# Rodada 2
# P2 e P3 jogam
# R2 falha porque P3 é Intern e sabota

# Agora Rodada 3
contract = SEVEN_TIERS_CATALOG[3][0] # Sindicato de Titânio, req=TIx2, target=6
declarations = {p.id: p.make_public_declaration(contract, 3) for p in players}

for pid, d in declarations.items():
    print(f"P{pid} ({players[pid].role.name}): claims_req={d.claims_req}, val={d.claimed_value}, hand={[c.card_type.name for c in players[pid].hand]}")

# Conflitos após R1 e R2
conflict_pairs = [{0, 1}, {2, 3}]
public_accused = {0, 1, 2, 3}

# Atualizar suspeitas conforme a engine atualiza após R1 e R2
# P0 estava em [0, 1] que falhou
players[0].suspicions[1] = 1.0; players[0].known_traitors.add(1)
# P2 e P4 viram [0, 1] falhar
players[2].suspicions[0] = 0.65; players[2].suspicions[1] = 0.65
players[4].suspicions[0] = 0.65; players[4].suspicions[1] = 0.65

# P2 estava em [2, 3] que falhou
players[2].suspicions[3] = 1.0; players[2].known_traitors.add(3)
# P0 e P4 viram [2, 3] falhar
players[0].suspicions[2] = 0.65; players[0].suspicions[3] = 0.65
players[4].suspicions[2] = 0.65; players[4].suspicions[3] = 0.65

comm = [0, 2, 4]
print(f"\n--- Testando Votação para a proposta {comm} ---")
for p in players:
    if p.role == Role.BANKER:
        v = p.vote_on_proposal(0, comm, contract, 3, conflict_pairs=conflict_pairs, consecutive_vetoes=0, declarations=declarations)
        print(f"P{p.id} ({p.role.name}) votou: {v}")
        print(f"  suspicions={p.suspicions}")
