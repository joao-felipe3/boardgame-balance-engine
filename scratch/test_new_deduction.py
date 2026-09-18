import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Let's inspect the sort order and simulate with the refined logic
import src.btg.engine as engine
from src.btg import Role, BankerProfile, simulate_single_match

# Let's see what happens if we patch choose_optimal_committee to put has_chair at the top
orig_choose = engine.choose_optimal_committee

from src.btg.constants import CardType

def patched_choose_optimal_committee(chair, players, contract, declarations, conflict_pairs=None, quarantined_pid=None, public_accused=None, passed_members=None):
    c_size = contract.committee_size
    valid_players = [p for p in players if p.id != quarantined_pid]
    if len(valid_players) < c_size:
        valid_players = players

    accused_set = public_accused or set()

    if chair.role == Role.BANKER and accused_set:
        unaccused_clean = [
            p.id for p in valid_players
            if p.id not in chair.known_traitors and p.id not in accused_set and chair.suspicions[p.id] < 0.60
        ]
        if len(unaccused_clean) >= c_size:
            clean_pids = unaccused_clean
        else:
            clean_pids = [
                p.id for p in valid_players
                if p.id not in chair.known_traitors and chair.suspicions[p.id] < 0.60
            ]
    else:
        clean_pids = [
            p.id for p in valid_players
            if p.id not in chair.known_traitors and chair.suspicions[p.id] < 0.60
        ]

    if len(clean_pids) < c_size:
        clean_pids = [p.id for p in valid_players if p.id not in chair.known_traitors]
    if len(clean_pids) < c_size:
        clean_pids = [p.id for p in valid_players]

    import itertools
    all_comms = list(itertools.combinations(clean_pids, c_size))
    candidate_comms = [
        cm for cm in all_comms
        if not (conflict_pairs and any(sum(1 for pid in cm if pid in cp) > 1 for cp in conflict_pairs))
    ]
    if not candidate_comms:
        candidate_comms = all_comms

    evaluated_comms = []
    for comm in candidate_comms:
        supplier_ids = []
        if contract.req_commodity is not None:
            suppliers = [pid for pid in comm if declarations[pid].claims_req]
            if len(suppliers) >= contract.req_commodity_count:
                suppliers.sort(key=lambda pid: (chair.suspicions[pid], -declarations[pid].req_commodity_value))
                supplier_ids = suppliers[:contract.req_commodity_count]

        has_req_coverage = (
            contract.req_commodity is None or
            len(supplier_ids) >= contract.req_commodity_count
        )

        total_declared = sum(declarations[pid].claimed_value for pid in comm)
        is_viable = (total_declared >= contract.target_value)
        partners = [pid for pid in comm if pid != chair.id]
        avg_sus = sum(chair.suspicions[pid] for pid in partners) / len(partners) if partners else 0.0
        has_chair = (chair.id in comm)
        bench_count = sum(1 for pid in comm if declarations[pid].prefers_bench)
        untested_count = sum(1 for pid in comm if pid != chair.id and pid not in passed_members)
        intruders_count = sum(1 for pid in comm if pid != chair.id and chair.suspicions[pid] >= 0.38)

        conflict_penalty = 0
        if conflict_pairs:
            for cp in conflict_pairs:
                cp_count = sum(1 for pid in comm if pid in cp)
                if cp_count > 1:
                    conflict_penalty += 10
                elif cp_count == 1:
                    conflict_penalty += 1
        if accused_set:
            conflict_penalty += sum(1 for pid in comm if pid in accused_set)

        traitor_count = sum(1 for pid in comm if pid in chair.known_traitors or chair.suspicions[pid] >= 0.80)
        total_tokens = sum(declarations[pid].tokens_offered for pid in comm)
        fatigue_count = sum(1 for pid in comm if players[pid].consecutive_rounds >= 2)
        public_req_count = sum(
            1 for pid in comm
            if contract.req_commodity is not None and (
                contract.req_commodity in players[pid].public_known_cards or
                CardType.WILD in players[pid].public_known_cards
            )
        )

        evaluated_comms.append({
            'comm': list(comm),
            'supplier_ids': supplier_ids,
            'supplier_id': supplier_ids[0] if supplier_ids else None,
            'has_req_coverage': has_req_coverage,
            'is_viable': is_viable,
            'avg_sus': avg_sus,
            'has_chair': has_chair,
            'bench_count': bench_count,
            'untested_count': untested_count,
            'intruders_count': intruders_count,
            'conflict_penalty': conflict_penalty,
            'traitor_count': traitor_count,
            'total_declared': total_declared,
            'total_tokens': total_tokens,
            'fatigue_count': fatigue_count,
            'public_req_count': public_req_count
        })

    # NOVO CRITÉRIO: O Chairman leal SEMPRE se inclui e prioriza isolamento de teste!
    evaluated_comms.sort(key=lambda x: (
        x['traitor_count'],         # 1º: zero traidores conhecidos
        not x['has_chair'],         # 2º: Chairman leal SEMPRE se inclui (controle de variável)
        x['conflict_penalty'],      # 3º: evitar conflitos
        not x['has_req_coverage'],  # 4º: cobertura de insumos garantida
        not x['is_viable'],         # 5º: meta garantida na conversa pré-comitê
        x['intruders_count'],       # 6º: isolamento de suspeito (mínimo de intrusos: 0 ou 1)
        round(x['avg_sus'], 3),     # 7º: menor suspeita média
        x['untested_count'],        # 8º: operadores já comprovados
        -x['total_tokens'],         # 9º: tokens reais
        x['fatigue_count'],         # 10º: rotação
        -x['public_req_count'],
        x['bench_count'],
        -x['total_declared']
    ))

    best = evaluated_comms[0]
    return best['comm'], best['supplier_ids']

engine.choose_optimal_committee = patched_choose_optimal_committee

# Test 500 games
banker_wins = 0
num_games = 500
innocent_burned_count = 0

for seed in range(num_games):
    match = simulate_single_match(seed, seed=seed, banker_profile="MIXED", intern_profile="MIXED", record_trace=True)
    if match['winner'] in ('Banqueiro', Role.BANKER.value):
        banker_wins += 1
    roles = {p['id']: p['role'] for p in match['players_metadata']}
    banker_ids = [pid for pid, r in roles.items() if r == 'Banqueiro']
    last_r = match['rounds_data'][-1]
    sus_by_banker = last_r['suspicions']['by_banker']
    match_burned = any(
        sus_by_banker[b1].get(b2, 0) >= 0.50
        for b1 in banker_ids for b2 in banker_ids if b1 != b2
    )
    if match_burned:
        innocent_burned_count += 1

print(f"Patched Committee Sorting:")
print(f"Banker Win Rate: {banker_wins}/{num_games} ({banker_wins/num_games*100:.1f}%)")
print(f"Matches with Innocent Banker Suspected (sus >= 0.50): {innocent_burned_count}/{num_games} ({innocent_burned_count/num_games*100:.1f}%)")
