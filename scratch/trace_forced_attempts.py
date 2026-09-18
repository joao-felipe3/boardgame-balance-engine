import sys, os
sys.path.insert(0, os.path.abspath('.'))
from src.btg import simulate_single_match, Role, BankerProfile, InternProfile
from src.btg.player import PlayerAI

original_vote = PlayerAI.vote_on_proposal

def tracking_vote(self, proposer, committee, contract, round_num, conflict_pairs=None, consecutive_vetoes=0, declarations=None):
    res = original_vote(self, proposer, committee, contract, round_num, conflict_pairs, consecutive_vetoes, declarations)
    return res

print("Analisando seed=555000 tentativa a tentativa...")
# Let's inspect each round in engine.py by adding print statements or hooking
import src.btg.engine as engine_module

# Hook choose_optimal_committee
orig_choose = engine_module.choose_optimal_committee
def debug_choose(chair, players, contract, declarations, conflict_pairs=None, quarantined_pid=None, public_accused=None, passed_members=None):
    comm, sup = orig_choose(chair, players, contract, declarations, conflict_pairs, quarantined_pid, public_accused, passed_members)
    print(f"    [Tentativa] Chair P{chair.id} ({chair.role.name}) propõe: {comm} (fornecedor={sup})")
    return comm, sup

engine_module.choose_optimal_committee = debug_choose

# Hook vote_on_proposal
def debug_vote(self, proposer, committee, contract, round_num, conflict_pairs=None, consecutive_vetoes=0, declarations=None):
    v = original_vote(self, proposer, committee, contract, round_num, conflict_pairs, consecutive_vetoes, declarations)
    return v

PlayerAI.vote_on_proposal = debug_vote

res = simulate_single_match(0, seed=555000, record_trace=True)
meta = res['players_metadata']
roles = {p['id']: p['role'] for p in meta}
print(f"Papeis: {roles}")
