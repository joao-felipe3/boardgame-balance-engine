import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match, Role, BankerProfile, InternProfile
from src.btg.player import PlayerAI
import src.btg.engine as engine
from collections import Counter

original_choose = engine.choose_optimal_committee

def inspect_other_reason():
    examples = []
    
    def instrumented_choose(chair, players, contract, declarations, conflict_pairs=None, quarantined_pid=None, public_accused=None, passed_members=None):
        comm, sups = original_choose(chair, players, contract, declarations, conflict_pairs, quarantined_pid, public_accused, passed_members)
        if chair.role == Role.BANKER and len(examples) < 10:
            interns_in_comm = [pid for pid in comm if players[pid].role == Role.INTERN]
            if interns_in_comm:
                banker_pids = [p.id for p in players if p.role == Role.BANKER]
                if len(banker_pids) >= contract.committee_size:
                    # Check if there is ANY pure banker combination
                    import itertools
                    pure_banker_comms = list(itertools.combinations(banker_pids, contract.committee_size))
                    for pb_comm in pure_banker_comms:
                        pb_sups = [pid for pid in pb_comm if declarations[pid].claims_req] if contract.req_commodity else []
                        pb_has_req = (contract.req_commodity is None or len(pb_sups) >= contract.req_commodity_count)
                        pb_total = sum(declarations[pid].claimed_value for pid in pb_comm)
                        pb_viable = (pb_total >= contract.target_value)
                        if pb_has_req and pb_viable:
                            # Both chosen comm and pb_comm are viable and have req
                            # Why was chosen_comm ranked higher than pb_comm?
                            examples.append({
                                'contract': contract.name,
                                'tier': contract.tier,
                                'c_size': contract.committee_size,
                                'chair': chair.id,
                                'chair_suspicions': dict(chair.suspicions),
                                'chosen_comm': comm,
                                'pb_comm': list(pb_comm),
                                'chosen_total': sum(declarations[pid].claimed_value for pid in comm),
                                'pb_total': pb_total,
                                'chosen_bench': sum(1 for pid in comm if declarations[pid].prefers_bench),
                                'pb_bench': sum(1 for pid in pb_comm if declarations[pid].prefers_bench),
                                'passed_members': list(passed_members or []),
                                'conflict_pairs': [list(cp) for cp in (conflict_pairs or [])],
                                'public_accused': list(public_accused or [])
                            })
                            break
        return comm, sups

    engine.choose_optimal_committee = instrumented_choose

    for i in range(100):
        simulate_single_match(i, seed=999000 + i, record_trace=False)
        if len(examples) >= 5:
            break

    print(f"Exemplos de 'other_reason' encontrados: {len(examples)}\n")
    for idx, ex in enumerate(examples):
        print(f"--- EXEMPLO {idx+1} ---")
        print(f"Contrato: Tier {ex['tier']} ({ex['contract']}), Tam: {ex['c_size']}")
        print(f"Chair: P{ex['chair']} (BANKER)")
        print(f"Suspeitas do Chair: {ex['chair_suspicions']}")
        print(f"Passed members: {ex['passed_members']}, Conflitos: {ex['conflict_pairs']}, Acusados: {ex['public_accused']}")
        print(f"Comitê Escolhido (com Estagiário): {ex['chosen_comm']} (Total decl: {ex['chosen_total']}, Bench: {ex['chosen_bench']})")
        print(f"Comitê 100% Banqueiro Disponível: {ex['pb_comm']} (Total decl: {ex['pb_total']}, Bench: {ex['pb_bench']})")

inspect_other_reason()
