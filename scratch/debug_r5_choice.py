import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import Role, BankerProfile, InternProfile
from src.btg.constants import SEVEN_TIERS_CATALOG, CardType
from src.btg.deck import DeckManager, ResourceCard
from src.btg.player import PlayerAI
from src.btg.engine import choose_optimal_committee
import numpy as np

rng = np.random.default_rng(42)
roles = [Role.BANKER, Role.BANKER, Role.BANKER, Role.INTERN, Role.INTERN]
players = [
    PlayerAI(i, roles[i], BankerProfile.BALANCED if roles[i]==Role.BANKER else InternProfile.B_SLEEPER, rng)
    for i in range(5)
]
deck = DeckManager(seed=42)
for p in players:
    p.hand = [ResourceCard(CardType.CO), ResourceCard(CardType.TI)] + deck.draw_blind(2)

# Simular que P0, P1, P2 passaram missões anteriores
passed_members = {0, 1, 2}
for bp in players[:3]:
    for cid in [0, 1, 2]:
        if cid != bp.id:
            bp.suspicions[cid] = 0.08
    bp.suspicions[3] = 0.40
    bp.suspicions[4] = 0.40

# Agora rodada 5
contract = SEVEN_TIERS_CATALOG[5][0] # Megaconsórcio Industrial, target=10, req=TIx2
declarations = {p.id: p.make_public_declaration(contract, 5) for p in players}

for pid, d in declarations.items():
    print(f"P{pid} ({players[pid].role.name}): claims_req={d.claims_req}, val={d.claimed_value}, req_val={d.req_commodity_value}, bench={d.prefers_bench}")

all_comms = list(__import__('itertools').combinations(range(5), 3))
evals = []
chair = players[0]
for comm in all_comms:
    supplier_ids = []
    if contract.req_commodity is not None:
        suppliers = [pid for pid in comm if declarations[pid].claims_req]
        if len(suppliers) >= contract.req_commodity_count:
            suppliers.sort(key=lambda pid: (chair.suspicions[pid], -declarations[pid].req_commodity_value))
            supplier_ids = suppliers[:contract.req_commodity_count]

    has_req_coverage = (len(supplier_ids) >= contract.req_commodity_count)
    total_declared = sum(declarations[pid].claimed_value for pid in comm)
    is_viable = (total_declared >= contract.target_value)
    avg_sus = sum(chair.suspicions[pid] for pid in comm if pid != chair.id) / len(comm)
    has_chair = (chair.id in comm)
    bench_count = sum(1 for pid in comm if declarations[pid].prefers_bench)
    untested_count = sum(1 for pid in comm if pid != chair.id and pid not in passed_members and chair.suspicions[pid] >= 0.25)

    evals.append({
        'comm': list(comm),
        'has_req': has_req_coverage,
        'viable': is_viable,
        'untested': untested_count,
        'avg_sus': round(avg_sus, 2),
        'bench': bench_count,
        'chair': has_chair,
        'total_dec': total_declared
    })

evals.sort(key=lambda x: (
    not x['has_req'],
    not x['viable'],
    0, # conflict
    x['untested'],
    x['avg_sus'],
    x['bench'],
    not x['chair'],
    -x['total_dec']
))

print("\nTop 5 comitês avaliados:")
for e in evals[:5]:
    print(" ", e)
