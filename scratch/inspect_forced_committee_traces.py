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

def debug_match(seed=42):
    rng = np.random.default_rng(seed)
    roles = [Role.BANKER, Role.BANKER, Role.BANKER, Role.INTERN, Role.INTERN]
    players = [
        PlayerAI(i, roles[i], BankerProfile.BALANCED if roles[i]==Role.BANKER else InternProfile.B_SLEEPER, rng)
        for i in range(5)
    ]
    deck = DeckManager(seed=seed)
    for p in players:
        p.hand = [ResourceCard(CardType.CO), ResourceCard(CardType.TI)] + deck.draw_blind(2)

    curr_chair = 0
    passed_members = set()
    conflict_pairs = []
    public_accused = set()

    for rnd in range(1, 7):
        contract = SEVEN_TIERS_CATALOG[rnd][0]
        print(f"\n--- RODADA {rnd} (Tier {contract.tier}: {contract.name}, Tam={contract.committee_size}, Meta={contract.target_value}, Req={contract.req_commodity}x{contract.req_commodity_count}) ---")
        consecutive_vetoes = 0
        approved = None

        while consecutive_vetoes < 3 and approved is None:
            chair = players[curr_chair]
            declarations = {p.id: p.make_public_declaration(contract, rnd) for p in players}
            chosen_comm, assigned_req = choose_optimal_committee(
                chair, players, contract, declarations,
                conflict_pairs=conflict_pairs,
                public_accused=public_accused,
                passed_members=passed_members
            )
            print(f"  Tentativa {consecutive_vetoes+1}: Chair P{chair.id} ({chair.role.name}) propõe {chosen_comm} (Fornecedor={assigned_req})")
            
            votes = {}
            for p in players:
                v = p.vote_on_proposal(chair.id, chosen_comm, contract, rnd, conflict_pairs=conflict_pairs, consecutive_vetoes=consecutive_vetoes, declarations=declarations)
                votes[p.id] = v
            
            v_for = sum(1 for v in votes.values() if v)
            print(f"    Votos: {votes} ({v_for} SIM, {5-v_for} NÃO) -> {'APROVADO' if v_for >= 3 else 'REJEITADO'}")
            
            if v_for >= 3:
                approved = chosen_comm
            else:
                consecutive_vetoes += 1
                curr_chair = (curr_chair + 1) % 5

        if approved is None:
            print("  *** COMITÊ FORÇADO PELO BANCO CENTRAL! ***")
            all_comms = list(__import__('itertools').combinations(range(5), contract.committee_size))
            def _forced_score(cm):
                accused_count = sum(1 for cid in cm if cid in public_accused or (conflict_pairs and any(cid in cp for cp in conflict_pairs)))
                total_sus = sum(sum(p.suspicions[cid] for p in players if p.role == Role.BANKER) for cid in cm)
                supplier_count = sum(1 for pid in cm if declarations[pid].claims_req) if contract.req_commodity else 0
                has_cov = (contract.req_commodity is None or supplier_count >= contract.req_commodity_count)
                bench_in_comm = sum(1 for pid in cm if declarations[pid].prefers_bench)
                return (not has_cov, accused_count, total_sus, bench_in_comm)
            best_comm = min(all_comms, key=_forced_score)
            approved = list(best_comm)
            print(f"  Banco Central impôs: {approved}")

        # Simulate outcome
        comm_objs = [players[pid] for pid in approved]
        interns = [p.id for p in comm_objs if p.role == Role.INTERN]
        print(f"  Membros finais: {approved} (Estagiários: {interns})")
        if not interns:
            print("  -> Missão SUCESSO (Banqueiros)")
            passed_members.update(approved)
            for bp in players:
                if bp.role == Role.BANKER:
                    for cid in approved:
                        bp.suspicions[cid] = min(0.08, bp.suspicions[cid])
        else:
            print("  -> Missão SABOTADA (Estagiário presente)")
            veterans = [cid for cid in approved if cid in passed_members]
            newcomers = [cid for cid in approved if cid not in passed_members]
            if len(newcomers) == 1 and len(veterans) >= 1:
                culprit = newcomers[0]
                print(f"    Flagrante! {culprit} é o único novato entre veteranos!")
                public_accused.add(culprit)
                for bp in players:
                    if bp.role == Role.BANKER:
                        bp.known_traitors.add(culprit)
                        bp.suspicions[culprit] = 1.0
            elif len(approved) == 2:
                conflict_pairs.append(set(approved))
                public_accused.update(approved)
                for bp in players:
                    if bp.role == Role.BANKER:
                        for cid in approved:
                            bp.suspicions[cid] = max(bp.suspicions[cid], 0.65)

debug_match(42)
debug_match(123)
