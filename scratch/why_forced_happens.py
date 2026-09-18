import sys, os
sys.path.insert(0, os.path.abspath('.'))
from src.btg import simulate_single_match, Role, BankerProfile, InternProfile
from src.btg.player import PlayerAI
from collections import Counter

# Let's inspect what happens specifically on attempt 3 (when consecutive_vetoes == 2)
attempt3_rejections = Counter()
attempt3_chairs = Counter()
attempt3_voters_who_said_no = Counter()

original_vote = PlayerAI.vote_on_proposal

def debug_vote(self, proposer, committee, contract, round_num, conflict_pairs=None, consecutive_vetoes=0, declarations=None):
    res = original_vote(self, proposer, committee, contract, round_num, conflict_pairs, consecutive_vetoes, declarations)
    if consecutive_vetoes >= 2 and not res:
        # Player voted NO on 3rd attempt!
        role_str = self.role.name
        attempt3_voters_who_said_no[f"P{self.id}_{role_str}"] += 1
        
        # Why did this player vote NO?
        if self.role == Role.BANKER:
            if contract.req_commodity is not None and declarations and len([pid for pid in committee if declarations[pid].claims_req]) < contract.req_commodity_count:
                # Wait, line 169 says: `if contract.req_commodity is not None and declarations and consecutive_vetoes < 2:`
                # So this shouldn't trigger if consecutive_vetoes >= 2!
                pass
            if proposer in self.known_traitors:
                attempt3_rejections["proposer_known_traitor"] += 1
            elif any(p in self.known_traitors for p in committee):
                attempt3_rejections["member_known_traitor"] += 1
            elif conflict_pairs and any(sum(1 for pid in committee if pid in cp) > 1 for cp in conflict_pairs):
                attempt3_rejections["two_conflict_members"] += 1
            elif any(self.suspicions[p] >= 0.80 for p in committee):
                attempt3_rejections["member_sus_>=0.80"] += 1
            elif proposer != self.id and (proposer in self.known_traitors or self.suspicions[proposer] >= 0.80):
                attempt3_rejections["proposer_sus_>=0.80"] += 1
            else:
                attempt3_rejections["other_banker_reason"] += 1
        else:
            attempt3_rejections[f"intern_{self.profile.name}"] += 1
    return res

PlayerAI.vote_on_proposal = debug_vote

print("Rodando 200 partidas para investigar o que causa a rejeição da 3ª tentativa...")
for s in range(200):
    simulate_single_match(s, seed=880000 + s)

print("\n--- Motivos de Voto NÃO na 3ª Tentativa (Gera Comitê Forçado) ---")
for k, v in attempt3_rejections.most_common(20):
    print(f"  {k:35s}: {v:5d}")

print("\n--- Quem votou NÃO na 3ª Tentativa ---")
for k, v in attempt3_voters_who_said_no.most_common(10):
    print(f"  {k:35s}: {v:5d}")
