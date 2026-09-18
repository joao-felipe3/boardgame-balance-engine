import sys, os
sys.path.insert(0, os.path.abspath('.'))
from src.btg import simulate_single_match, Role, BankerProfile, InternProfile
from src.btg.player import PlayerAI

original_vote = PlayerAI.vote_on_proposal

def instrumented_vote(self, proposer, committee, contract, round_num, conflict_pairs=None, consecutive_vetoes=0, declarations=None):
    res = original_vote(self, proposer, committee, contract, round_num, conflict_pairs, consecutive_vetoes, declarations)
    if self.role == Role.BANKER and not res:
        print(f"\n[VETO] P{self.id} (Banker) voted FALSE to {committee} (Chair P{proposer}) in R{round_num} (Tentativa {consecutive_vetoes+1})")
        print(f"  Declarations: {[(pid, d.claims_req, d.claimed_value) for pid, d in declarations.items()]}")
        print(f"  Contract: Tier={contract.tier}, Target={contract.target_value}, Req={contract.req_commodity}, ReqCount={contract.req_commodity_count}")
        print(f"  Known traitors of P{self.id}: {self.known_traitors}")
        print(f"  Suspicions of P{self.id}: {dict(self.suspicions)}")
        print(f"  Conflict pairs: {conflict_pairs}")
        
        # Test which line caused it:
        if contract.req_commodity is not None and declarations and consecutive_vetoes < 2:
            suppliers = [pid for pid in committee if declarations[pid].claims_req]
            if len(suppliers) < contract.req_commodity_count:
                print(f"  -> MOTIVO: contract.req_commodity ({contract.req_commodity.name}) sem declarantes suficientes ({len(suppliers)} < {contract.req_commodity_count})")
        if declarations and consecutive_vetoes < 2:
            total_declared = sum(declarations[pid].claimed_value for pid in committee)
            if total_declared < contract.target_value - 2:
                print(f"  -> MOTIVO: liquidez total ({total_declared}) < {contract.target_value - 2}")
        if proposer in self.known_traitors:
            print(f"  -> MOTIVO: proposer P{proposer} in known_traitors!")
        if any(p in self.known_traitors for p in committee):
            print(f"  -> MOTIVO: member in known_traitors!")
        if conflict_pairs and any(sum(1 for pid in committee if pid in cp) > 1 for cp in conflict_pairs):
            print(f"  -> MOTIVO: two members of same conflict pair!")
        if any(self.suspicions[p] >= 0.75 for p in committee):
            print(f"  -> MOTIVO: member with suspicion >= 0.75!")
        if self.id in committee:
            others = [p for p in committee if p != self.id]
            avg_sus = sum(self.suspicions[p] for p in others) / len(others) if others else 0.0
            print(f"  -> MOTIVO: avg_sus with self = {avg_sus:.2f}")
        else:
            avg_sus = sum(self.suspicions[p] for p in committee) / len(committee)
            print(f"  -> MOTIVO: avg_sus without self = {avg_sus:.2f}")
            
    return res

PlayerAI.vote_on_proposal = instrumented_vote

simulate_single_match(3, seed=123453, record_trace=True)
