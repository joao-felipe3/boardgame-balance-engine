# -*- coding: utf-8 -*-
"""
BTG Madagascar - Bateria de Experimentos de Economia Base de Recursos
====================================================================
Testa 6 configurações de economia de cartas:
1. Baseline (Mão 3 + Compra 1 cega por rodada)
2. Opção 1: Mercado de Balcão Aberto (Open Market Draft com rastreamento visual)
3. Opção 2: Recomposição de Mão Fixa a 4 Cartas (Hand Refresh pós-missão)
4. Opção 3: Carteira Inicial Estruturada (Kit [CO, VN, TI + 1 topo])
5. Opção 4: Compra 2, Descarta 1 (Draft Tático)
6. Opção 5 (Combo Ideal): Mercado de Balcão + Recomposição a 4 Cartas + Carteira Inicial
"""

import random
import time
import sys
from enum import Enum
from typing import List, Dict, Tuple, Optional, Set
import itertools
import pandas as pd
import numpy as np


class CardType(Enum):
    CO = 'Cobalto (+1)'
    VN = 'Baunilha (+2)'
    TI = 'Titanio (+3)'
    SF = 'Safira (+4)'
    WILD = 'Ouro Liquido (+4 / Coringa)'
    TOXIC = 'Ativo Toxico (-4)'

CARD_BASE_VALUES = {
    CardType.CO: 1,
    CardType.VN: 2,
    CardType.TI: 3,
    CardType.SF: 4,
    CardType.WILD: 4,
    CardType.TOXIC: -4
}

INITIAL_COMMERCIAL_DECK = (
    [CardType.CO] * 22 +
    [CardType.VN] * 18 +
    [CardType.TI] * 10 +
    [CardType.SF] * 6 +
    [CardType.WILD] * 2 +
    [CardType.TOXIC] * 2
)

class Role(Enum):
    BANKER = 'Banqueiro'
    INTERN = 'Estagiario'

class InternProfile(Enum):
    A_AGGRESSIVE = 'A (Agressivo / Blefe Imediato)'
    B_SLEEPER = 'B (Infiltracao Profunda / Sleeper)'
    C_HEDGE = 'C (Hedge / Retencao Economica)'

class ResourceCard:
    __slots__ = ('card_type',)
    def __init__(self, card_type: CardType):
        self.card_type = card_type
    @property
    def base_value(self) -> int:
        return CARD_BASE_VALUES[self.card_type]

class ContractSpec:
    __slots__ = ('name', 'tier', 'committee_size', 'cost_per_player', 'target_value', 'req_commodity', 'req_commodity_count')
    def __init__(self, name: str, tier: int, committee_size: int, cost_per_player: int, target_value: int, req_commodity: Optional[CardType] = None, req_commodity_count: int = 1):
        self.name = name
        self.tier = tier
        self.committee_size = committee_size
        self.cost_per_player = cost_per_player
        self.target_value = target_value
        self.req_commodity = req_commodity
        self.req_commodity_count = req_commodity_count

SEVEN_TIERS_CATALOG = {
    1: [
        ContractSpec("Arbitragem Simples", 1, 2, 1, 3),
        ContractSpec("Exportacao de Baunilha", 1, 2, 1, 4, req_commodity=CardType.VN, req_commodity_count=1),
    ],
    2: [
        ContractSpec("Mineracao de Cobalto", 2, 2, 1, 4, req_commodity=CardType.CO, req_commodity_count=1),
        ContractSpec("Lote Agricola", 2, 2, 1, 4, req_commodity=CardType.VN, req_commodity_count=1),
    ],
    3: [
        ContractSpec("Sindicato de Titanio", 3, 3, 1, 8, req_commodity=CardType.TI, req_commodity_count=2),
        ContractSpec("Logistica Portuaria", 3, 3, 1, 7, req_commodity=CardType.CO, req_commodity_count=2),
    ],
    4: [
        ContractSpec("Refino Metalurgico", 4, 4, 1, 11, req_commodity=CardType.TI, req_commodity_count=2),
        ContractSpec("Consorcio Agro-Industrial", 4, 4, 1, 11, req_commodity=CardType.VN, req_commodity_count=2),
    ],
    5: [
        ContractSpec("Fundicao Estrategica", 5, 2, 2, 12, req_commodity=CardType.TI, req_commodity_count=2),
        ContractSpec("Cofre de Gemas", 5, 2, 2, 13, req_commodity=CardType.SF, req_commodity_count=2),
    ],
    6: [
        ContractSpec("Complexo Greenfield", 6, 3, 2, 16, req_commodity=CardType.TI, req_commodity_count=2),
        ContractSpec("Consorcio Safira", 6, 3, 2, 17, req_commodity=CardType.SF, req_commodity_count=2),
    ],
    7: [
        ContractSpec("Holding Global BTG (Climax)", 7, 3, 2, 21, req_commodity=CardType.SF, req_commodity_count=3),
    ]
}

class DeckManager:
    __slots__ = ('draw_pile', 'discard_pile', 'open_market', 'rng')

    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.draw_pile = INITIAL_COMMERCIAL_DECK.copy()
        self.rng.shuffle(self.draw_pile)
        self.discard_pile: List[CardType] = []
        self.open_market: List[CardType] = []

    def refill_open_market(self, target_size=3):
        while len(self.open_market) < target_size:
            drawn = self.draw_blind(1)
            if drawn:
                self.open_market.append(drawn[0].card_type)
            else:
                break

    def draw_blind(self, n: int = 1) -> List[ResourceCard]:
        drawn = []
        for _ in range(n):
            if not self.draw_pile:
                if not self.discard_pile:
                    drawn.append(ResourceCard(CardType.CO))
                    continue
                self.draw_pile = self.discard_pile.copy()
                self.discard_pile = []
                self.rng.shuffle(self.draw_pile)
            card_t = self.draw_pile.pop()
            drawn.append(ResourceCard(card_t))
        return drawn

    def draw_from_market(self, card_type: CardType) -> ResourceCard:
        if card_type in self.open_market:
            self.open_market.remove(card_type)
            self.refill_open_market()
            return ResourceCard(card_type)
        return self.draw_blind(1)[0]

    def discard(self, cards: List[ResourceCard]):
        self.discard_pile.extend([c.card_type for c in cards])


class PlayerAI:
    __slots__ = ('id', 'role', 'profile', 'rng', 'hand', 'interest_tokens', 'suspicions', 'known_traitors', 'credits_accumulated', 'public_known_cards')

    def __init__(self, player_id: int, role: Role, profile: InternProfile, rng: random.Random):
        self.id = player_id
        self.role = role
        self.profile = profile
        self.rng = rng
        self.hand: List[ResourceCard] = []
        self.interest_tokens: int = 0
        self.suspicions: Dict[int, float] = {i: 0.40 for i in range(5)}
        self.suspicions[self.id] = 0.0 if role == Role.BANKER else 1.0
        self.known_traitors: Set[int] = set()
        self.credits_accumulated = 0
        self.public_known_cards: List[CardType] = []

    def accumulate_holding_interest(self):
        if self.interest_tokens < 3:
            self.interest_tokens += 1

    def claim_success_credit(self):
        self.credits_accumulated += 1
        if self.credits_accumulated >= 1:
            self.credits_accumulated -= 1
            if self.role == Role.BANKER:
                self.hand.append(ResourceCard(CardType.WILD))
            else:
                self.hand.append(ResourceCard(CardType.TOXIC))

    def make_public_declaration(self, contract: ContractSpec, round_num: int) -> Tuple[bool, int, int, int, bool, str]:
        has_req_real = False
        req_val = 0
        if contract.req_commodity is not None:
            req_cards = [c for c in self.hand if c.card_type in (contract.req_commodity, CardType.WILD)]
            if req_cards:
                has_req_real = True
                req_val = max(c.base_value for c in req_cards) + min(self.interest_tokens, 2)

        cost = contract.cost_per_player
        expected_quota = contract.target_value / contract.committee_size

        eligible_cards = [c for c in self.hand if c.card_type != CardType.TOXIC]
        if round_num <= 3 and contract.req_commodity != CardType.SF:
            non_nobles = [c for c in eligible_cards if c.card_type not in (CardType.SF, CardType.WILD)]
            if len(non_nobles) >= cost:
                eligible_cards = non_nobles

        eligible_cards.sort(key=lambda c: -c.base_value)
        best_base_val = sum(c.base_value for c in eligible_cards[:cost]) if eligible_cards else 0
        tokens_to_offer = self.interest_tokens if round_num >= 3 else min(self.interest_tokens, 1)
        best_total_val = best_base_val + tokens_to_offer

        is_dry = (best_total_val < expected_quota) and (round_num >= 2) and (not has_req_real)

        if self.role == Role.BANKER:
            top_card_names = [f"{c.card_type.name.split(' ')[0]}({c.base_value}pts)" for c in eligible_cards[:cost]]
            offered_str = " + ".join(top_card_names) if top_card_names else "Liquidez Baixa"
            if tokens_to_offer > 0:
                offered_str += f" [+{tokens_to_offer}🪙]"
            return has_req_real, best_total_val, req_val, tokens_to_offer, is_dry, offered_str
        else:
            if self.profile == InternProfile.A_AGGRESSIVE:
                claims = True if contract.req_commodity is not None else False
                req_v = req_val if has_req_real else max(3, int(expected_quota))
                offered_str = f"{contract.req_commodity.name.split(' ')[0]}(~{req_v}pts)" if contract.req_commodity else f"Liquidez Alta(~{int(expected_quota)}pts)"
                return claims, max(best_total_val, int(expected_quota)), req_v, self.interest_tokens, False, offered_str
            elif self.profile == InternProfile.B_SLEEPER:
                if round_num <= 2:
                    top_card_names = [f"{c.card_type.name.split(' ')[0]}({c.base_value}pts)" for c in eligible_cards[:cost]]
                    offered_str = " + ".join(top_card_names) if top_card_names else "Liquidez Baixa"
                    return has_req_real, best_total_val, req_val, tokens_to_offer, is_dry, offered_str
                else:
                    claims = True if contract.req_commodity is not None else False
                    req_v = req_val if has_req_real else max(3, int(expected_quota))
                    offered_str = f"{contract.req_commodity.name.split(' ')[0]}(~{req_v}pts)" if contract.req_commodity else f"Liquidez Forte(~{int(expected_quota)}pts)"
                    if self.interest_tokens > 0:
                        offered_str += f" [+{self.interest_tokens}🪙]"
                    return claims, max(best_total_val, int(expected_quota)), req_v, self.interest_tokens, False, offered_str
            elif self.profile == InternProfile.C_HEDGE:
                claims = True if contract.req_commodity is not None else False
                req_v = req_val if has_req_real else max(3, int(expected_quota))
                offered_str = f"{contract.req_commodity.name.split(' ')[0]}(~{req_v}pts)" if contract.req_commodity else f"Liquidez Média(~{int(expected_quota)}pts)"
                return claims, max(best_total_val, int(expected_quota)), req_v, tokens_to_offer, False, offered_str

    def vote_on_proposal(self, proposer: int, committee: List[int], contract: ContractSpec, round_num: int) -> bool:
        if self.role == Role.BANKER:
            for p in committee:
                if p in self.known_traitors or self.suspicions[p] >= 0.85:
                    return False
            if self.id in committee:
                others = [p for p in committee if p != self.id]
                max_sus = max([self.suspicions[p] for p in others], default=0.0)
                return max_sus < 0.65
            else:
                avg_sus = sum(self.suspicions[p] for p in committee) / len(committee)
                return avg_sus < 0.55
        else:
            if self.profile == InternProfile.A_AGGRESSIVE:
                return (self.id in committee) or (self.rng.random() < 0.35)
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
        return True

    def plan_honest_contribution(
        self,
        contract: ContractSpec,
        round_num: int,
        is_responsible_for_req: bool,
        quota_needed: float,
        is_match_point: bool = False
    ) -> Tuple[List[ResourceCard], int, int]:
        cost = contract.cost_per_player
        pos_cards = [c for c in self.hand if c.card_type != CardType.TOXIC]
        if not pos_cards:
            return self.hand[:cost], 0, sum(c.base_value for c in self.hand[:cost])

        valid_combos = list(itertools.combinations(pos_cards, cost))
        if not valid_combos:
            valid_combos = list(itertools.combinations(self.hand, cost))
        if not valid_combos:
            return self.hand[:cost], 0, sum(c.base_value for c in self.hand[:cost])

        if contract.req_commodity is not None:
            req_combos = [cb for cb in valid_combos if any(c.card_type in (contract.req_commodity, CardType.WILD) for c in cb)]
            if req_combos:
                valid_combos = req_combos

        if is_match_point or contract.tier >= 6:
            best_combo = max(valid_combos, key=lambda cb: sum(c.base_value for c in cb))
            best_tokens = self.interest_tokens
            best_val = sum(c.base_value for c in best_combo) + best_tokens
            return list(best_combo), best_tokens, best_val

        best_combo = None
        best_tokens = 0
        best_val = -999
        best_score = (999, 999, 999, 999)

        for cb in valid_combos:
            base_v = sum(c.base_value for c in cb)
            needed_tokens = max(0, int(np.ceil(quota_needed - base_v)))
            tokens_to_use = min(self.interest_tokens, needed_tokens)
            total_v = base_v + tokens_to_use

            has_safira = any(c.card_type in (CardType.SF, CardType.WILD) for c in cb)
            penalty = 10 if (has_safira and round_num <= 3 and contract.req_commodity != CardType.SF) else 0

            if total_v >= quota_needed:
                score = (0, penalty, tokens_to_use, total_v - quota_needed)
            else:
                score = (1, penalty, -tokens_to_use, -(total_v - quota_needed))

            if best_combo is None or score < best_score:
                best_combo = cb
                best_tokens = tokens_to_use
                best_val = total_v
                best_score = score

        return list(best_combo), best_tokens, best_val

    def plan_sabotage_contribution(
        self,
        contract: ContractSpec,
        round_num: int,
        is_responsible_for_req: bool
    ) -> Tuple[List[ResourceCard], int]:
        cost = contract.cost_per_player
        toxic_cards = [c for c in self.hand if c.card_type == CardType.TOXIC]
        pos_cards = [c for c in self.hand if c.card_type != CardType.TOXIC]
        low_pos = sorted(pos_cards, key=lambda c: c.base_value)

        chosen: List[ResourceCard] = []

        if toxic_cards and (contract.committee_size >= 4 or round_num >= 4):
            chosen.append(toxic_cards.pop(0))
            while len(chosen) < cost and low_pos:
                chosen.append(low_pos.pop(0))
            while len(chosen) < cost and self.hand:
                chosen.append(self.hand[0])
            return chosen[:cost], 0

        if is_responsible_for_req and contract.req_commodity is not None:
            non_req_cards = [c for c in low_pos if c.card_type not in (contract.req_commodity, CardType.WILD)]
            if non_req_cards:
                chosen.append(non_req_cards[0])
                while len(chosen) < cost and low_pos:
                    chosen.append(low_pos.pop(0))
                return chosen[:cost], 0

        while len(chosen) < cost and low_pos:
            chosen.append(low_pos.pop(0))
        while len(chosen) < cost and self.hand:
            chosen.append(self.hand[0])

        return chosen[:cost], 0


def evaluate_contract_outcome(
    submitted_cards: List[ResourceCard],
    total_tokens_used: int,
    contract: ContractSpec
) -> Tuple[bool, int, bool]:
    total_val = sum(c.base_value for c in submitted_cards) + total_tokens_used
    has_req = True

    if contract.req_commodity is not None:
        matching_count = sum(1 for c in submitted_cards if c.card_type in (contract.req_commodity, CardType.WILD))
        has_req = (matching_count >= contract.req_commodity_count)

    is_success = (total_val >= contract.target_value) and has_req
    return is_success, total_val, has_req


def choose_optimal_committee(
    chair: PlayerAI,
    players: List[PlayerAI],
    contract: ContractSpec,
    declarations: Dict[int, Tuple]
) -> Tuple[List[int], Optional[int]]:
    c_size = contract.committee_size
    all_pids = [p.id for p in players if p.id not in chair.known_traitors and chair.suspicions[p.id] < 0.85]
    if len(all_pids) < c_size:
        all_pids = [p.id for p in players]

    candidate_comms = list(itertools.combinations(all_pids, c_size))
    evaluated_comms = []

    for comm in candidate_comms:
        supplier_id = None
        if contract.req_commodity is not None:
            suppliers = [pid for pid in comm if declarations[pid][0]]
            if len(suppliers) < contract.req_commodity_count:
                continue
            suppliers.sort(key=lambda pid: (chair.suspicions[pid], -declarations[pid][2]))
            supplier_id = suppliers[0]

        total_declared = sum(declarations[pid][1] for pid in comm)
        is_viable = (total_declared >= contract.target_value)
        avg_sus = sum(chair.suspicions[pid] for pid in comm if pid != chair.id) / len(comm)
        has_chair = (chair.id in comm)
        bench_count = sum(1 for pid in comm if declarations[pid][4])

        evaluated_comms.append({
            'comm': list(comm),
            'supplier_id': supplier_id,
            'is_viable': is_viable,
            'avg_sus': avg_sus,
            'has_chair': has_chair,
            'bench_count': bench_count,
            'total_declared': total_declared
        })

    if not evaluated_comms:
        chosen = [chair.id] + [p for p in all_pids if p != chair.id][:c_size - 1]
        return chosen, (chair.id if declarations[chair.id][0] else None)

    evaluated_comms.sort(key=lambda x: (
        not x['is_viable'],
        x['bench_count'],
        x['avg_sus'],
        not x['has_chair'],
        -x['total_declared']
    ))

    best = evaluated_comms[0]
    return best['comm'], best['supplier_id']


def simulate_game_modular(
    game_idx: int,
    profile: InternProfile,
    seed: Optional[int] = None,
    mode_market: bool = False,
    mode_hand_refresh: bool = False,
    mode_starting_kit: bool = False,
    mode_draft_2_keep_1: bool = False
) -> Dict:
    rng = random.Random(seed if seed is not None else (int(time.time() * 1000) ^ game_idx))
    catalog = SEVEN_TIERS_CATALOG

    roles = [Role.BANKER] * 3 + [Role.INTERN] * 2
    rng.shuffle(roles)
    players = [PlayerAI(i, roles[i], profile, rng) for i in range(5)]

    deck = DeckManager(seed=rng.randint(0, 10**9))
    if mode_market:
        deck.refill_open_market(3)

    for p in players:
        if mode_starting_kit:
            p.hand = [ResourceCard(CardType.CO), ResourceCard(CardType.VN), ResourceCard(CardType.TI)] + deck.draw_blind(1)
        else:
            p.hand = deck.draw_blind(3)

    banker_score = 0
    intern_score = 0
    curr_chair = 0
    round_count = 0
    ops = [rng.choice(catalog[t]) for t in range(1, 8)]

    for r_idx, contract in enumerate(ops):
        round_count += 1

        for p in players:
            if mode_hand_refresh:
                needed = max(0, 4 - len(p.hand))
                if needed > 0:
                    if mode_market:
                        for _ in range(needed):
                            if p.role == Role.BANKER and contract.req_commodity in deck.open_market:
                                c = deck.draw_from_market(contract.req_commodity)
                                p.public_known_cards.append(contract.req_commodity)
                            else:
                                c = deck.draw_blind(1)[0]
                            p.hand.append(c)
                    elif mode_draft_2_keep_1:
                        for _ in range(needed):
                            options = deck.draw_blind(2)
                            if p.role == Role.BANKER:
                                chosen = max(options, key=lambda x: x.base_value)
                                discarded = min(options, key=lambda x: x.base_value)
                            else:
                                toxic = [o for o in options if o.card_type == CardType.TOXIC]
                                if toxic:
                                    chosen = toxic[0]
                                    discarded = options[1] if options[0] == chosen else options[0]
                                else:
                                    chosen = min(options, key=lambda x: x.base_value)
                                    discarded = max(options, key=lambda x: x.base_value)
                            deck.discard([discarded])
                            p.hand.append(chosen)
                    else:
                        p.hand.extend(deck.draw_blind(needed))
            else:
                if mode_market:
                    if p.role == Role.BANKER and contract.req_commodity in deck.open_market:
                        c = deck.draw_from_market(contract.req_commodity)
                        p.public_known_cards.append(contract.req_commodity)
                    else:
                        c = deck.draw_blind(1)[0]
                    p.hand.append(c)
                elif mode_draft_2_keep_1:
                    options = deck.draw_blind(2)
                    if p.role == Role.BANKER:
                        chosen = max(options, key=lambda x: x.base_value)
                        discarded = min(options, key=lambda x: x.base_value)
                    else:
                        toxic = [o for o in options if o.card_type == CardType.TOXIC]
                        if toxic:
                            chosen = toxic[0]
                            discarded = options[1] if options[0] == chosen else options[0]
                        else:
                            chosen = min(options, key=lambda x: x.base_value)
                            discarded = max(options, key=lambda x: x.base_value)
                    deck.discard([discarded])
                    p.hand.append(chosen)
                else:
                    p.hand.extend(deck.draw_blind(1))

        consecutive_vetoes = 0
        approved_committee = None
        promised_supplier = None
        all_declarations = {}

        while consecutive_vetoes < 3 and approved_committee is None:
            chair = players[curr_chair]
            declarations = {p.id: p.make_public_declaration(contract, round_count) for p in players}
            all_declarations = declarations

            if mode_market:
                for b in players:
                    if b.role == Role.BANKER:
                        for target_p in players:
                            if contract.req_commodity in target_p.public_known_cards and not declarations[target_p.id][0]:
                                b.suspicions[target_p.id] = 0.90
                                b.known_traitors.add(target_p.id)

            chosen_comm, assigned_req_player = choose_optimal_committee(chair, players, contract, declarations)

            votes = {p.id: p.vote_on_proposal(curr_chair, chosen_comm, contract, round_count) for p in players}
            if sum(votes.values()) >= 3:
                approved_committee = chosen_comm
                promised_supplier = assigned_req_player
            else:
                consecutive_vetoes += 1
                curr_chair = (curr_chair + 1) % 5

        if approved_committee is None:
            chair = players[curr_chair]
            others = [p.id for p in players if p.id != chair.id]
            approved_committee = [chair.id] + others[:contract.committee_size - 1]
            promised_supplier = None

        for p in players:
            if p.id not in approved_committee:
                p.accumulate_holding_interest()

        comm_objs = [players[pid] for pid in approved_committee]

        planning_order = []
        if promised_supplier is not None:
            sup_obj = next((p for p in comm_objs if p.id == promised_supplier), None)
            if sup_obj:
                planning_order.append(sup_obj)
        for p in comm_objs:
            if p not in planning_order:
                planning_order.append(p)

        submitted_all_cards = []
        total_tokens_spent = 0
        cumulative_committed_val = 0
        is_match_point = (banker_score == 3)

        for idx, p in enumerate(planning_order):
            is_req_responsible = (p.id == promised_supplier)
            remaining_members = len(planning_order) - idx
            remaining_target = max(0, contract.target_value - cumulative_committed_val)
            quota_for_p = remaining_target / remaining_members

            declared_p_val = all_declarations[p.id][1] if p.id in all_declarations else 0
            if p.role == Role.BANKER and round_count >= 3 and contract.target_value >= 8:
                quota_for_p = max(quota_for_p, min(declared_p_val, contract.target_value / contract.committee_size))

            should_sabotage = False
            if p.role == Role.INTERN:
                if p.profile == InternProfile.A_AGGRESSIVE:
                    should_sabotage = True
                elif p.profile == InternProfile.B_SLEEPER:
                    has_toxic = any(c.card_type == CardType.TOXIC for c in p.hand)
                    should_sabotage = (round_count >= 3 and has_toxic) or (round_count >= 4)
                elif p.profile == InternProfile.C_HEDGE:
                    has_toxic = any(c.card_type == CardType.TOXIC for c in p.hand)
                    should_sabotage = (has_toxic and round_count >= 3) or (round_count >= 4)

            honest_cards, honest_tokens, honest_val = p.plan_honest_contribution(contract, round_count, is_req_responsible, quota_for_p, is_match_point=is_match_point)
            cumulative_committed_val += honest_val

            if not should_sabotage:
                actual_cards = honest_cards
                actual_tokens = honest_tokens
            else:
                actual_cards, actual_tokens = p.plan_sabotage_contribution(contract, round_count, is_req_responsible)

            p.interest_tokens -= actual_tokens
            total_tokens_spent += actual_tokens

            for c in actual_cards:
                if c in p.hand:
                    p.hand.remove(c)
                if c.card_type in p.public_known_cards:
                    p.public_known_cards.remove(c.card_type)

            submitted_all_cards.extend(actual_cards)

        deck.discard(submitted_all_cards)
        is_success, total_val, has_req = evaluate_contract_outcome(submitted_all_cards, total_tokens_spent, contract)

        if is_success:
            banker_score += 1
            for p in comm_objs:
                p.claim_success_credit()

            decay = 0.06 if contract.tier <= 2 else (0.12 if contract.tier <= 4 else 0.20)
            for bp in players:
                if bp.role == Role.BANKER:
                    for cid in approved_committee:
                        if cid != bp.id and cid not in bp.known_traitors:
                            bp.suspicions[cid] = max(0.05, bp.suspicions[cid] - decay)
        else:
            intern_score += 1
            has_toxic = any(c.card_type == CardType.TOXIC for c in submitted_all_cards)
            penalty = 0.25 if len(approved_committee) >= 4 else (0.35 if len(approved_committee) == 3 else 0.50)

            for bp in players:
                if bp.role == Role.BANKER:
                    for cid in approved_committee:
                        if cid != bp.id:
                            if has_toxic and len(approved_committee) == 2:
                                bp.suspicions[cid] = 1.00
                                bp.known_traitors.add(cid)
                            else:
                                bp.suspicions[cid] = min(0.95, bp.suspicions[cid] + penalty)

        if banker_score >= 4:
            return {"winner": Role.BANKER.value, "rounds": round_count, "b_score": banker_score, "i_score": intern_score, "profile": profile.value}
        elif intern_score >= 4:
            return {"winner": Role.INTERN.value, "rounds": round_count, "b_score": banker_score, "i_score": intern_score, "profile": profile.value}

        curr_chair = (curr_chair + 1) % 5

    w = Role.BANKER.value if banker_score > intern_score else Role.INTERN.value
    return {"winner": w, "rounds": 7, "b_score": banker_score, "i_score": intern_score, "profile": profile.value}


def run_experiment_suite(n_per_config=20000):
    configs = [
        ("1. [Baseline] Mão 3 + Compra 1 cega", {"mode_market": False, "mode_hand_refresh": False, "mode_starting_kit": False, "mode_draft_2_keep_1": False}),
        ("2. [Opção 1] Mercado de Balcão Aberto", {"mode_market": True, "mode_hand_refresh": False, "mode_starting_kit": False, "mode_draft_2_keep_1": False}),
        ("3. [Opção 2] Recomposição de Mão (4 cartas)", {"mode_market": False, "mode_hand_refresh": True, "mode_starting_kit": False, "mode_draft_2_keep_1": False}),
        ("4. [Opção 3] Carteira Inicial [CO,VN,TI+1]", {"mode_market": False, "mode_hand_refresh": False, "mode_starting_kit": True, "mode_draft_2_keep_1": False}),
        ("5. [Opção 4] Compra 2, Descarta 1", {"mode_market": False, "mode_hand_refresh": False, "mode_starting_kit": False, "mode_draft_2_keep_1": True}),
        ("6. [Combo] Mercado + Recomposição 4 + Kit", {"mode_market": True, "mode_hand_refresh": True, "mode_starting_kit": True, "mode_draft_2_keep_1": False}),
    ]

    profiles = [InternProfile.A_AGGRESSIVE, InternProfile.B_SLEEPER, InternProfile.C_HEDGE]
    summary_rows = []

    print("=" * 105)
    print(" INICIANDO BATERIA DE EXPERIMENTOS DE ECONOMIA BASE (6 CONFIGURAÇÕES x 20.000 PARTIDAS) ")
    print("=" * 105)

    for idx, (name, params) in enumerate(configs, 1):
        t0 = time.time()
        results = []
        for i in range(n_per_config):
            prof = random.choice(profiles)
            res = simulate_game_modular(i, prof, seed=200000 * idx + i, **params)
            results.append(res)

        df = pd.DataFrame(results)
        b_wins = (df["winner"] == Role.BANKER.value).sum()
        i_wins = (df["winner"] == Role.INTERN.value).sum()
        b_wr = (b_wins / n_per_config) * 100
        i_wr = (i_wins / n_per_config) * 100
        avg_r = df["rounds"].mean()

        sub_a = df[df["profile"] == InternProfile.A_AGGRESSIVE.value]
        sub_b = df[df["profile"] == InternProfile.B_SLEEPER.value]
        sub_c = df[df["profile"] == InternProfile.C_HEDGE.value]

        wr_a = ((sub_a["winner"] == Role.INTERN.value).sum() / len(sub_a)) * 100
        wr_b = ((sub_b["winner"] == Role.INTERN.value).sum() / len(sub_b)) * 100
        wr_c = ((sub_c["winner"] == Role.INTERN.value).sum() / len(sub_c)) * 100

        df["score"] = df["b_score"].astype(str) + " x " + df["i_score"].astype(str)
        climax_pct = ((df["score"].isin(["4 x 3", "3 x 4"])).sum() / n_per_config) * 100
        sweep_pct = ((df["score"] == "4 x 0").sum() / n_per_config) * 100

        print(f"[{idx}/6] {name:<42} | WR Banq: {b_wr:5.1f}% | WR Sleeper: {wr_b:5.1f}% | Clímax: {climax_pct:4.1f}% | 4x0: {sweep_pct:4.1f}% | Tempo: {time.time()-t0:4.1f}s")
        sys.stdout.flush()

        summary_rows.append({
            "Configuração": name,
            "WR Banq": f"{b_wr:.1f}%",
            "WR Estag": f"{i_wr:.1f}%",
            "WR Sleeper": f"{wr_b:.1f}%",
            "WR Agressivo": f"{wr_a:.1f}%",
            "Clímax (7ª R)": f"{climax_pct:.1f}%",
            "Taxa 4x0": f"{sweep_pct:.1f}%",
            "Duração": f"{avg_r:.2f}"
        })

    summary_df = pd.DataFrame(summary_rows)
    print("\n" + "=" * 115)
    print("                      MATRIZ COMPARATIVA DE ECONOMIA DE RECURSOS")
    print("=" * 115)
    print(summary_df.to_string(index=False))
    print("=" * 115)


if __name__ == '__main__':
    run_experiment_suite(20000)
