import sys, os
sys.path.insert(0, os.path.abspath('.'))
from src.btg import simulate_single_match, Role, BankerProfile, InternProfile
from src.btg.player import PlayerAI, PlayerDeclaration
from src.btg.constants import CardType, ContractSpec
from src.btg.deck import ResourceCard
import src.btg.engine as engine_module
import itertools
import numpy as np

# 1. Preservação de Titânio e Poupança Econômica em plan_honest_contribution:
original_plan_honest = PlayerAI.plan_honest_contribution

def smart_plan_honest(
    self,
    contract: ContractSpec,
    round_num: int,
    is_responsible_for_req: bool,
    quota_needed: float,
    is_match_point: bool = False
):
    cost = contract.cost_per_player
    pos_cards = [c for c in self.hand if c.card_type != CardType.TOXIC]
    if not pos_cards:
        return self.hand[:cost], 0, sum(c.base_value for c in self.hand[:cost])

    valid_combos = list(itertools.combinations(pos_cards, cost))
    if not valid_combos:
        valid_combos = list(itertools.combinations(self.hand, cost))
    if not valid_combos:
        return self.hand[:cost], 0, sum(c.base_value for c in self.hand[:cost])

    if is_responsible_for_req and contract.req_commodity is not None:
        req_combos = [cb for cb in valid_combos if any(c.card_type in (contract.req_commodity, CardType.WILD) for c in cb)]
        if req_combos:
            valid_combos = req_combos

    # Em Tiers 6 e 7, joga o melhor combo com tokens necessários
    if contract.tier >= 6:
        best_combo = max(valid_combos, key=lambda cb: sum(c.base_value for c in cb))
        needed_tok = max(0, int(np.ceil(quota_needed - sum(c.base_value for c in best_combo))))
        best_tokens = min(self.interest_tokens, needed_tok if not is_match_point else self.interest_tokens)
        best_val = sum(c.base_value for c in best_combo) + best_tokens
        return list(best_combo), best_tokens, best_val

    # Tiers 1 a 5: Poupança Ativa de Titânio e Safira
    best_combo = None
    best_tokens = 0
    best_val = -999
    best_score = (9999, 9999, 9999, 9999)

    safety_margin = 2 if is_match_point else (1 if round_num >= 3 else 0)
    target_for_p = max(cost, quota_needed + safety_margin)

    for cb in valid_combos:
        base_v = sum(c.base_value for c in cb)
        needed_tokens = max(0, int(np.ceil(target_for_p - base_v)))
        tokens_to_use = min(self.interest_tokens, needed_tokens)

        total_v = base_v + tokens_to_use

        # Preservar Safiras e Wilds
        has_safira = any(c.card_type in (CardType.SF, CardType.WILD) for c in cb)
        safira_penalty = 30 if (has_safira and contract.req_commodity != CardType.SF and contract.tier < 6) else 0

        # Preservar Titânio estritamente nas R1 e R2 a menos que seja o insumo exigido
        has_titanio = any(c.card_type == CardType.TI for c in cb)
        if has_titanio and contract.req_commodity != CardType.TI:
            if round_num <= 2:
                titanio_penalty = 25  # Poupado para a R3 (Sindicato de Titânio)
            elif contract.tier < 5:
                titanio_penalty = 12
            else:
                titanio_penalty = 0
        else:
            titanio_penalty = 0

        token_penalty = tokens_to_use * 2

        if total_v >= quota_needed:
            overkill = total_v - quota_needed
            score = (0, safira_penalty + titanio_penalty, token_penalty, overkill)
        else:
            deficit = quota_needed - total_v
            score = (1, deficit, safira_penalty + titanio_penalty, -total_v)

        if best_combo is None or score < best_score:
            best_combo = cb
            best_tokens = tokens_to_use
            best_val = total_v
            best_score = score

    return list(best_combo), best_tokens, best_val

PlayerAI.plan_honest_contribution = smart_plan_honest

# 2. Votação com Tolerância de Bancada Leal
def smart_vote(
    self,
    proposer: int,
    committee: list,
    contract: ContractSpec,
    round_num: int,
    conflict_pairs=None,
    consecutive_vetoes: int = 0,
    declarations=None
) -> bool:
    if self.role == Role.BANKER:
        # Rejeição imediata se proponente ou membro é traidor comprovado
        if proposer in self.known_traitors or self.suspicions[proposer] >= 0.85:
            return False
        for p in committee:
            if p in self.known_traitors or self.suspicions[p] >= 0.85:
                return False

        # Nunca aprovar dois membros do mesmo par de conflito juntos
        if conflict_pairs:
            for cp in conflict_pairs:
                if sum(1 for pid in committee if pid in cp) > 1:
                    return False

        # Emergência: na 3ª tentativa (consecutive_vetoes >= 2), aprova qualquer comitê limpo
        if consecutive_vetoes >= 2:
            return True

        if self.id in committee:
            others = [p for p in committee if p != self.id]
            avg_sus = sum(self.suspicions[p] for p in others) / len(others) if others else 0.0
        else:
            avg_sus = sum(self.suspicions[p] for p in committee) / len(committee)

        # Núcleo de confiança: banqueiros leais com suspeita controlada
        is_trusted_core = (avg_sus <= 0.40 and self.suspicions[proposer] <= 0.48)

        # Se for o núcleo de confiança, NÃO VETA por insumo nem por liquidez declarada!
        if not is_trusted_core:
            if contract.req_commodity is not None and declarations and consecutive_vetoes == 0:
                suppliers_in_comm = [pid for pid in committee if declarations[pid].claims_req]
                if len(suppliers_in_comm) < contract.req_commodity_count:
                    return False

            if declarations and consecutive_vetoes == 0:
                total_declared = sum(declarations[pid].claimed_value for pid in committee)
                if total_declared < contract.target_value - 3:
                    return False

        # Limiares de governança
        prop_limit = 0.60
        comm_with_self_limit = 0.52
        avg_comm_limit = 0.48

        if proposer != self.id and self.suspicions[proposer] >= prop_limit:
            return False

        for p in committee:
            if self.suspicions[p] >= 0.75:
                return False

        if proposer != self.id and self.suspicions[proposer] >= 0.50:
            suspect_in_comm = sum(1 for p in committee if self.suspicions[p] >= 0.50)
            if suspect_in_comm >= 2:
                return False

        if self.id in committee:
            return avg_sus <= comm_with_self_limit
        else:
            return avg_sus <= avg_comm_limit
    else:
        # Estagiário
        if self.profile == InternProfile.A_AGGRESSIVE:
            return (self.id in committee) or (self.rng.random() < 0.30)
        elif self.profile == InternProfile.B_SLEEPER:
            if contract.tier <= 2:
                return True
            if self.id in committee:
                return True
            return self.rng.random() < 0.20
        elif self.profile == InternProfile.C_HEDGE:
            if self.id in committee:
                return True
            return self.rng.random() < 0.25
        elif self.profile == InternProfile.D_OPPORTUNIST:
            if self.id in committee:
                return True
            if contract.tier <= 2:
                return True
            return self.rng.random() < 0.35
        elif self.profile == InternProfile.E_TECHNICIAN:
            if self.id in committee:
                return True
            return self.rng.random() < (0.45 if round_num <= 2 else 0.20)
    return True

PlayerAI.vote_on_proposal = smart_vote

print("Rodando teste com Preservação de Titânio e Votação de Bancada Leal...")
b_wins = 0
i_wins = 0
vetoes_total = 0
forced_total = 0
lockouts = 0

n_games = 1000
for i in range(n_games):
    res = simulate_single_match(i, seed=20260900 + i, banker_profile="MIXED", intern_profile="MIXED")
    if res['winner'] == 'Banqueiro':
        b_wins += 1
    else:
        i_wins += 1
    vetoes_total += res['total_vetoes']
    forced_total += res['forced_committees']
    if res['intern_lockout']:
        lockouts += 1

print(f"\n[Resultado]")
print(f"  Vitórias Banqueiros : {b_wins:4d} ({b_wins/n_games*100:5.1f}%)")
print(f"  Vitórias Estagiários: {i_wins:4d} ({i_wins/n_games*100:5.1f}%)")
print(f"  Média de Vetos/Jogo : {vetoes_total/n_games:4.2f}")
print(f"  Comitês Forçados    : {forced_total:4d} ({forced_total/n_games*100:5.1f}% das partidas)")
print(f"  Taxa de Lockout     : {lockouts:4d} ({lockouts/n_games*100:5.1f}%)")
