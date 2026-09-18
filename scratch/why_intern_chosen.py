import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match, Role, BankerProfile, InternProfile
from src.btg.player import PlayerAI
import src.btg.engine as engine
from collections import Counter

original_choose = engine.choose_optimal_committee

intern_picked_reasons = Counter()

def instrumented_choose(chair, players, contract, declarations, conflict_pairs=None, quarantined_pid=None, public_accused=None, passed_members=None):
    comm, sups = original_choose(chair, players, contract, declarations, conflict_pairs, quarantined_pid, public_accused, passed_members)
    
    # If chair is Banker, did chair pick any Intern?
    if chair.role == Role.BANKER:
        interns_in_comm = [pid for pid in comm if players[pid].role == Role.INTERN]
        if interns_in_comm:
            # Why did chair pick this intern?
            # Could chair have picked a pure banker committee?
            banker_pids = [p.id for p in players if p.role == Role.BANKER]
            if len(banker_pids) >= contract.committee_size:
                pure_banker_comm = banker_pids[:contract.committee_size]
                # Check why pure_banker_comm wasn't chosen
                # evaluate pure_banker_comm
                pb_sups = [pid for pid in pure_banker_comm if declarations[pid].claims_req] if contract.req_commodity else []
                pb_has_req = (contract.req_commodity is None or len(pb_sups) >= contract.req_commodity_count)
                pb_total = sum(declarations[pid].claimed_value for pid in pure_banker_comm)
                pb_viable = (pb_total >= contract.target_value)
                
                chosen_total = sum(declarations[pid].claimed_value for pid in comm)
                
                if not pb_has_req:
                    intern_picked_reasons["pure_banker_missing_req_coverage"] += 1
                elif not pb_viable:
                    intern_picked_reasons["pure_banker_failed_liquidity_viability"] += 1
                else:
                    intern_picked_reasons["other_reason"] += 1

    return comm, sups

engine.choose_optimal_committee = instrumented_choose

print("Rodando 1000 partidas para investigar escolhas dos Banqueiros...")
for i in range(1000):
    simulate_single_match(i, seed=888000 + i, record_trace=False)

print("\nRazões pelas quais um Chairman Banqueiro escolheu um Estagiário em vez de um Comitê 100% Banqueiro:")
for r, c in intern_picked_reasons.most_common():
    print(f"  {r:45s}: {c:5d}")
