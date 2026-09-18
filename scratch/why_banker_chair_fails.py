import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match, Role, BankerProfile, InternProfile
from src.btg.player import PlayerAI
import src.btg.engine as engine
from collections import Counter

original_vote = PlayerAI.vote_on_proposal

cases = []

def instrumented_vote(self, proposer, committee, contract, round_num, conflict_pairs=None, consecutive_vetoes=0, declarations=None):
    # Call original
    v = original_vote(self, proposer, committee, contract, round_num, conflict_pairs, consecutive_vetoes, declarations)
    return v

# We can intercept inside choose_optimal_committee and vote_on_proposal
# Let's inspect 50 games and log every time a Banker chair's proposal is rejected (votes_for < 3)
failed_banker_proposals = []

class Interceptor:
    current_players = []

def run_test():
    for g in range(100):
        # We can record the round attempts by patching PlayerAI
        pass

# Let's write a small script that runs the match loop directly for 20 matches and prints every rejected Banker proposal:
from src.btg.constants import SEVEN_TIERS_CATALOG, CardType
from src.btg.deck import DeckManager, ResourceCard
import numpy as np

for seed in range(50):
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

    curr_chair = 0
    passed_members = set()
    conflict_pairs = []
    public_accused = set()

    for rnd in range(1, 7):
        contract = SEVEN_TIERS_CATALOG[rnd][0]
        consecutive_vetoes = 0
        approved = None
        while consecutive_vetoes < 3 and approved is None:
            chair = players[curr_chair]
            declarations = {p.id: p.make_public_declaration(contract, rnd) for p in players}
            chosen_comm, assigned_req = engine.choose_optimal_committee(
                chair, players, contract, declarations,
                conflict_pairs=conflict_pairs,
                public_accused=public_accused,
                passed_members=passed_members
            )
            votes = {}
            for p in players:
                votes[p.id] = p.vote_on_proposal(chair.id, chosen_comm, contract, rnd, conflict_pairs=conflict_pairs, consecutive_vetoes=consecutive_vetoes, declarations=declarations)
            
            v_for = sum(1 for v in votes.values() if v)
            if chair.role == Role.BANKER and v_for < 3:
                # A BANKER CHAIR'S PROPOSAL WAS REJECTED!
                failed_banker_proposals.append({
                    'seed': seed,
                    'rnd': rnd,
                    'consecutive_vetoes': consecutive_vetoes,
                    'chair': chair.id,
                    'chosen_comm': chosen_comm,
                    'chosen_roles': [players[cid].role.name for cid in chosen_comm],
                    'votes': votes,
                    'banker_no_voters': [p.id for p in players if p.role == Role.BANKER and not votes[p.id]],
                    'passed_members': list(passed_members),
                    'conflict_pairs': [list(cp) for cp in conflict_pairs],
                    'public_accused': list(public_accused)
                })

            if v_for >= 3:
                approved = chosen_comm
            else:
                consecutive_vetoes += 1
                curr_chair = (curr_chair + 1) % 5

        # Simular avanço da rodada
        if approved:
            comm_objs = [players[pid] for pid in approved]
            interns = [p.id for p in comm_objs if p.role == Role.INTERN]
            if not interns:
                passed_members.update(approved)
                for bp in players:
                    if bp.role == Role.BANKER:
                        for cid in approved:
                            bp.suspicions[cid] = min(0.08, bp.suspicions[cid])
            else:
                # Missão falha
                if len(approved) == 2:
                    conflict_pairs.append(set(approved))
                    public_accused.update(approved)
                    for bp in players:
                        if bp.role == Role.BANKER:
                            for cid in approved:
                                bp.suspicions[cid] = max(bp.suspicions[cid], 0.65)

print(f"Total de propostas de Chairman Banqueiro rejeitadas em 50 partidas: {len(failed_banker_proposals)}")
print("\nPrimeiras 8 propostas de Banqueiro rejeitadas:")
for idx, fbp in enumerate(failed_banker_proposals[:8]):
    print(f"\n--- Caso {idx+1} (Seed {fbp['seed']}, Rodada {fbp['rnd']}, Tentativa {fbp['consecutive_vetoes']+1}) ---")
    print(f"  Chair: P{fbp['chair']} (BANKER)")
    print(f"  Comitê proposto: {fbp['chosen_comm']} ({fbp['chosen_roles']})")
    print(f"  Votos: {fbp['votes']} -> Banqueiros que votaram NÃO: {fbp['banker_no_voters']}")
    print(f"  Passed members: {fbp['passed_members']}, Conflitos: {fbp['conflict_pairs']}, Acusados: {fbp['public_accused']}")
