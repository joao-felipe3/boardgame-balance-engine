import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match, Role, BankerProfile, InternProfile
from src.btg.constants import CardType

fail_reasons = {'insumo': 0, 'toxico': 0, 'valor': 0}
committees_composition = {'0_interns': 0, '1_intern': 0, '2_interns': 0, '3_interns': 0}
games_analyzed = 100

for seed in range(games_analyzed):
    match = simulate_single_match(seed, seed=seed, banker_profile="MIXED", intern_profile="MIXED", record_trace=True)
    roles = {p['id']: p['role'] for p in match['players_metadata']}
    for r in match['rounds_data']:
        comm = r['committee']
        interns_count = sum(1 for pid in comm if roles[pid] in ('Estagiário', Role.INTERN.value))
        key = f"{interns_count}_interns" if interns_count <= 2 else "3_interns"
        committees_composition[key] = committees_composition.get(key, 0) + 1
        
        telemetry = r.get('tier_telemetry', {})
        # Check fail cause from telemetry or outcome
        if not r.get('success', False):
            # check fail cause
            t_data = r.get('telemetry', {})
            cause = r.get('fail_cause', 'valor')
            fail_reasons[cause] = fail_reasons.get(cause, 0) + 1

print("Committees composition:", committees_composition)
print("Fail reasons:", fail_reasons)
