import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match, Role, BankerProfile, InternProfile
from src.btg.player import PlayerAI
from collections import Counter, defaultdict

# Let's wrap vote_on_proposal to log reasons for voting False
original_vote = PlayerAI.vote_on_proposal

veto_reasons = Counter()
rejections_by_round = Counter()
proposer_role_rejection = Counter()
comm_composition_rejection = Counter()

def instrumented_vote(self, proposer, committee, contract, round_num, conflict_pairs=None, consecutive_vetoes=0, declarations=None):
    # We trace why Banker votes False
    if self.role == Role.BANKER:
        # Rejeição técnica
        if contract.req_commodity is not None and declarations and consecutive_vetoes < 2:
            suppliers_in_comm = [pid for pid in committee if declarations[pid].claims_req]
            if len(suppliers_in_comm) < contract.req_commodity_count:
                veto_reasons["req_coverage_missing"] += 1
                return False

        if declarations and consecutive_vetoes < 2:
            total_declared = sum(declarations[pid].claimed_value for pid in committee)
            if total_declared < contract.target_value - 2:
                veto_reasons["liquidity_deficit"] += 1
                return False

        if proposer in self.known_traitors:
            veto_reasons["proposer_known_traitor"] += 1
            return False

        for p in committee:
            if p in self.known_traitors:
                veto_reasons["member_known_traitor"] += 1
                return False

        if conflict_pairs:
            for cp in conflict_pairs:
                if sum(1 for pid in committee if pid in cp) > 1:
                    veto_reasons["conflict_pair_together"] += 1
                    return False

        if consecutive_vetoes >= 2:
            has_high_sus = any(self.suspicions[p] >= 0.58 for p in committee)
            proposer_is_bad = (proposer != self.id and self.suspicions[proposer] >= 0.60)
            if not has_high_sus and not proposer_is_bad:
                return True
            else:
                veto_reasons[f"emergency_veto_failed(high_sus={has_high_sus},bad_prop={proposer_is_bad})"] += 1
                return False

        # Thresholds
        if self.profile == BankerProfile.CONSERVATIVE:
            prop_threshold = 0.45; mem_threshold = 0.56; comm_with_self_limit = 0.50; avg_comm_limit = 0.45
        elif self.profile == BankerProfile.PRAGMATIC:
            prop_threshold = 0.52; mem_threshold = 0.64; comm_with_self_limit = 0.60; avg_comm_limit = 0.52
        elif self.profile == BankerProfile.STRATEGIST:
            prop_threshold = 0.48; mem_threshold = 0.60; comm_with_self_limit = 0.55; avg_comm_limit = 0.48
        else:
            prop_threshold = 0.48; mem_threshold = 0.58; comm_with_self_limit = 0.54; avg_comm_limit = 0.48

        if proposer != self.id and self.suspicions[proposer] >= 0.50:
            unproven = sum(1 for p in committee if self.suspicions[p] >= 0.50)
            if unproven >= 2:
                veto_reasons["unproven_with_suspect_proposer"] += 1
                return False

        if proposer != self.id and self.suspicions[proposer] >= prop_threshold:
            veto_reasons[f"proposer_sus_above_threshold({self.suspicions[proposer]:.2f}>={prop_threshold})"] += 1
            return False

        for p in committee:
            if self.suspicions[p] >= mem_threshold:
                veto_reasons[f"member_sus_above_threshold({self.suspicions[p]:.2f}>={mem_threshold})"] += 1
                return False

        if self.id in committee:
            others = [p for p in committee if p != self.id]
            max_sus = max([self.suspicions[p] for p in others], default=0.0)
            if len(others) >= 2:
                untrusted = sum(1 for p in others if self.suspicions[p] >= 0.50)
                if untrusted >= 2:
                    veto_reasons["two_untrusted_with_self"] += 1
                    return False
            if max_sus >= comm_with_self_limit:
                veto_reasons[f"max_sus_with_self({max_sus:.2f}>={comm_with_self_limit})"] += 1
                return False
            return True
        else:
            avg_sus = sum(self.suspicions[p] for p in committee) / len(committee)
            if avg_sus >= avg_comm_limit:
                veto_reasons[f"avg_sus_without_self({avg_sus:.2f}>={avg_comm_limit})"] += 1
                return False
            return True

    return original_vote(self, proposer, committee, contract, round_num, conflict_pairs, consecutive_vetoes, declarations)

PlayerAI.vote_on_proposal = instrumented_vote

print("Rodando 300 partidas com diagnóstico detalhado...")
forced_count = 0
for i in range(300):
    res = simulate_single_match(i, seed=123000 + i, record_trace=False)
    if res['forced_committees'] > 0:
        forced_count += res['forced_committees']

print(f"Total de Comitês Forçados em 300 partidas: {forced_count} ({forced_count/300*100:.1f}%)")
print("\nTop Motivos de Veto dos Banqueiros:")
for reason, count in veto_reasons.most_common(20):
    print(f"  {reason:50s}: {count:5d}")
