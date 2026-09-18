import sys, os
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match, Role, BankerProfile, InternProfile
from src.btg.player import PlayerAI
from collections import Counter

# Let's intercept PlayerAI.vote_on_proposal to record every single reason a Banker votes False!
original_vote = PlayerAI.vote_on_proposal

banker_veto_reasons = Counter()

def debug_vote(self, proposer, committee, contract, round_num, conflict_pairs=None, consecutive_vetoes=0, declarations=None):
    res = original_vote(self, proposer, committee, contract, round_num, conflict_pairs, consecutive_vetoes, declarations)
    if self.role == Role.BANKER and not res:
        # Why did it return False?
        # Let's check each condition
        if proposer in self.known_traitors or self.suspicions[proposer] >= 0.85:
            banker_veto_reasons["proposer_known_traitor_or_>=0.85"] += 1
        elif any(p in self.known_traitors or self.suspicions[p] >= 0.85 for p in committee):
            banker_veto_reasons["member_known_traitor_or_>=0.85"] += 1
        elif conflict_pairs and any(sum(1 for pid in committee if pid in cp) > 1 for cp in conflict_pairs):
            banker_veto_reasons["two_conflict_members_together"] += 1
        elif consecutive_vetoes >= 2:
            banker_veto_reasons["emergency_veto_failed_somehow"] += 1
        elif contract.req_commodity is not None and declarations and len([pid for pid in committee if declarations[pid].claims_req]) < contract.req_commodity_count:
            banker_veto_reasons["req_commodity_missing_claims"] += 1
        elif declarations and sum(declarations[pid].claimed_value for pid in committee) < contract.target_value - 3:
            banker_veto_reasons["liquidity_deficit_>3"] += 1
        elif any(self.suspicions[p] >= 0.75 for p in committee):
            banker_veto_reasons["member_sus_>=0.75"] += 1
        elif proposer != self.id and self.suspicions[proposer] >= 0.50 and sum(1 for p in committee if self.suspicions[p] >= 0.50) >= 2:
            banker_veto_reasons["suspect_proposer_brought_another_suspect"] += 1
        elif self.id in committee:
            others = [p for p in committee if p != self.id]
            avg_sus = sum(self.suspicions[p] for p in others) / len(others) if others else 0.0
            banker_veto_reasons[f"with_self_avg_sus({avg_sus:.2f})>limit"] += 1
        else:
            avg_sus = sum(self.suspicions[p] for p in committee) / len(committee)
            banker_veto_reasons[f"without_self_avg_sus({avg_sus:.2f})>limit"] += 1
            
    return res

PlayerAI.vote_on_proposal = debug_vote

print("Rodando 100 partidas para capturar os motivos exatos de voto NÃO dos Banqueiros...")
for i in range(100):
    simulate_single_match(i, seed=900000 + i, record_trace=False)

print("\nTop Motivos de Voto NÃO dos Banqueiros:")
for r, c in banker_veto_reasons.most_common(20):
    print(f"  {r:50s}: {c:5d}")
