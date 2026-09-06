# -*- coding: utf-8 -*-
"""
BTG Madagascar - Simulador Oficial v14.0 (Comitê de 4 na R5 & Clímax na 7ª Rodada)
==================================================================================
Mecânicas Consolidadas:
1. Carteira Inicial Estruturada: Kit [1 Cobalto (+1) + 1 Baunilha (+2) + 1 Titânio (+3) + 1 Topo].
2. Mercado de Balcão Aberto: 3 cartas sempre visíveis no centro para compra e dedução visual.
3. Recomposição de Mão Fixa: Toda rodada as mãos voltam a 4 cartas.
4. Tokens de Rendimento (+1🪙): Acumuláveis no banco (máx. 3) para combater Ativos Tóxicos.
5. Comitê de 4 Operadores no Tier 5 (R5 - Megaconsórcio): Os Banqueiros acumulam recursos nas R1-R4 e usam na R5.
6. Dupla de Infiltração Sleeper (Agente Ativo + Agente Reserva) & Confiança Progressiva.
"""

import random
import time
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Tuple, Optional, Set
import itertools
import json
import os
import numpy as np
import pandas as pd


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

@dataclass
class ResourceCard:
    card_type: CardType

    @property
    def base_value(self) -> int:
        return CARD_BASE_VALUES[self.card_type]

    def __repr__(self):
        return f"{self.card_type.name}(base={self.base_value})"


class Role(Enum):
    BANKER = 'Banqueiro'
    INTERN = 'Estagiario'

class InternProfile(Enum):
    A_AGGRESSIVE = 'A (Agressivo / Blefe Imediato)'
    B_SLEEPER = 'B (Infiltracao Profunda / Sleeper)'
    C_HEDGE = 'C (Hedge / Retencao Economica)'

@dataclass
class ContractSpec:
    name: str
    tier: int
    committee_size: int
    cost_per_player: int
    target_value: int
    req_commodity: Optional[CardType] = None
    req_commodity_count: int = 1


SEVEN_TIERS_CATALOG = {
    1: [
        ContractSpec("Arbitragem Simples", 1, committee_size=2, cost_per_player=1, target_value=3),
        ContractSpec("Exportacao de Baunilha", 1, committee_size=2, cost_per_player=1, target_value=4, req_commodity=CardType.VN, req_commodity_count=1),
    ],
    2: [
        ContractSpec("Mineracao de Cobalto", 2, committee_size=2, cost_per_player=1, target_value=4, req_commodity=CardType.CO, req_commodity_count=1),
        ContractSpec("Lote Agricola", 2, committee_size=2, cost_per_player=1, target_value=4, req_commodity=CardType.VN, req_commodity_count=1),
    ],
    3: [
        ContractSpec("Sindicato de Titanio", 3, committee_size=3, cost_per_player=1, target_value=8, req_commodity=CardType.TI, req_commodity_count=2),
        ContractSpec("Logistica Portuaria", 3, committee_size=3, cost_per_player=1, target_value=7, req_commodity=CardType.CO, req_commodity_count=2),
    ],
    4: [
        ContractSpec("Refino Metalurgico", 4, committee_size=3, cost_per_player=1, target_value=10, req_commodity=CardType.TI, req_commodity_count=2),
        ContractSpec("Consorcio Agro-Industrial", 4, committee_size=3, cost_per_player=1, target_value=10, req_commodity=CardType.VN, req_commodity_count=2),
    ],
    5: [
        ContractSpec("Megaconsorcio Industrial", 5, committee_size=4, cost_per_player=1, target_value=14, req_commodity=CardType.TI, req_commodity_count=2),
        ContractSpec("Cofre de Commodities", 5, committee_size=4, cost_per_player=1, target_value=14, req_commodity=CardType.VN, req_commodity_count=2),
    ],
    6: [
        ContractSpec("Complexo Greenfield", 6, committee_size=3, cost_per_player=2, target_value=16, req_commodity=CardType.TI, req_commodity_count=2),
        ContractSpec("Consorcio Safira", 6, committee_size=3, cost_per_player=2, target_value=17, req_commodity=CardType.SF, req_commodity_count=2),
    ],
    7: [
        ContractSpec("Holding Global BTG (Climax)", 7, committee_size=3, cost_per_player=2, target_value=20, req_commodity=CardType.SF, req_commodity_count=2),
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


@dataclass
class PlayerDeclaration:
    player_id: int
    claims_req: bool
    claimed_value: int
    req_commodity_value: int
    tokens_offered: int
    prefers_bench: bool
    offered_desc: str


class PlayerAI:
    __slots__ = ('id', 'role', 'profile', 'is_active_saboteur', 'rng', 'hand', 'interest_tokens', 'suspicions', 'known_traitors', 'credits_accumulated', 'public_known_cards')

    def __init__(self, player_id: int, role: Role, profile: InternProfile, rng: random.Random, is_active_saboteur: bool = False):
        self.id = player_id
        self.role = role
        self.profile = profile
        self.is_active_saboteur = is_active_saboteur
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

    def make_public_declaration(self, contract: ContractSpec, round_num: int) -> PlayerDeclaration:
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
            return PlayerDeclaration(self.id, has_req_real, best_total_val, req_val, tokens_to_offer, prefers_bench=is_dry, offered_desc=offered_str)
        else:
            if self.profile == InternProfile.A_AGGRESSIVE:
                claims = True if contract.req_commodity is not None else False
                req_v = req_val if has_req_real else max(3, int(expected_quota))
                offered_str = f"{contract.req_commodity.name.split(' ')[0]}(~{req_v}pts)" if contract.req_commodity else f"Liquidez Alta(~{int(expected_quota)}pts)"
                return PlayerDeclaration(self.id, claims, max(best_total_val, int(expected_quota)), req_v, self.interest_tokens, prefers_bench=False, offered_desc=offered_str)
            elif self.profile == InternProfile.B_SLEEPER:
                if round_num <= 2 or not self.is_active_saboteur:
                    top_card_names = [f"{c.card_type.name.split(' ')[0]}({c.base_value}pts)" for c in eligible_cards[:cost]]
                    offered_str = " + ".join(top_card_names) if top_card_names else "Liquidez Baixa"
                    return PlayerDeclaration(self.id, has_req_real, best_total_val, req_val, tokens_to_offer, prefers_bench=is_dry, offered_desc=offered_str)
                else:
                    claims = True if contract.req_commodity is not None else False
                    req_v = req_val if has_req_real else max(3, int(expected_quota))
                    offered_str = f"{contract.req_commodity.name.split(' ')[0]}(~{req_v}pts)" if contract.req_commodity else f"Liquidez Forte(~{int(expected_quota)}pts)"
                    if self.interest_tokens > 0:
                        offered_str += f" [+{self.interest_tokens}🪙]"
                    return PlayerDeclaration(self.id, claims, max(best_total_val, int(expected_quota)), req_v, self.interest_tokens, prefers_bench=False, offered_desc=offered_str)
            elif self.profile == InternProfile.C_HEDGE:
                claims = True if contract.req_commodity is not None else False
                req_v = req_val if has_req_real else max(3, int(expected_quota))
                offered_str = f"{contract.req_commodity.name.split(' ')[0]}(~{req_v}pts)" if contract.req_commodity else f"Liquidez Média(~{int(expected_quota)}pts)"
                return PlayerDeclaration(self.id, claims, max(best_total_val, int(expected_quota)), req_v, tokens_to_offer, prefers_bench=False, offered_desc=offered_str)

    def vote_on_proposal(self, proposer: int, committee: List[int], contract: ContractSpec, round_num: int) -> bool:
        if self.role == Role.BANKER:
            for p in committee:
                if p in self.known_traitors or self.suspicions[p] >= 0.70:
                    return False
            if self.id in committee:
                others = [p for p in committee if p != self.id]
                max_sus = max([self.suspicions[p] for p in others], default=0.0)
                return max_sus < 0.60
            else:
                avg_sus = sum(self.suspicions[p] for p in committee) / len(committee)
                return avg_sus < 0.50
        else:
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

        if is_match_point or contract.tier >= 6 or contract.committee_size >= 4:
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
    contract: ContractSpec,
    is_pure_banker_committee: bool = False
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
    declarations: Dict[int, PlayerDeclaration]
) -> Tuple[List[int], Optional[int]]:
    c_size = contract.committee_size
    clean_pids = [p.id for p in players if p.id not in chair.known_traitors and chair.suspicions[p.id] < 0.60]
    if len(clean_pids) < c_size:
        clean_pids = [p.id for p in players if p.id not in chair.known_traitors]
    if len(clean_pids) < c_size:
        clean_pids = [p.id for p in players]

    candidate_comms = list(itertools.combinations(clean_pids, c_size))
    evaluated_comms = []

    for comm in candidate_comms:
        supplier_id = None
        if contract.req_commodity is not None:
            suppliers = [pid for pid in comm if declarations[pid].claims_req]
            if len(suppliers) >= contract.req_commodity_count:
                suppliers.sort(key=lambda pid: (chair.suspicions[pid], -declarations[pid].req_commodity_value))
                supplier_id = suppliers[0]

        total_declared = sum(declarations[pid].claimed_value for pid in comm)
        is_viable = (total_declared >= contract.target_value)
        avg_sus = sum(chair.suspicions[pid] for pid in comm if pid != chair.id) / len(comm)
        has_chair = (chair.id in comm)
        bench_count = sum(1 for pid in comm if declarations[pid].prefers_bench)

        evaluated_comms.append({
            'comm': list(comm),
            'supplier_id': supplier_id,
            'is_viable': is_viable,
            'avg_sus': avg_sus,
            'has_chair': has_chair,
            'bench_count': bench_count,
            'total_declared': total_declared
        })

    evaluated_comms.sort(key=lambda x: (
        round(x['avg_sus'], 2),
        not x['is_viable'],
        x['bench_count'],
        not x['has_chair'],
        -x['total_declared']
    ))

    best = evaluated_comms[0]
    return best['comm'], best['supplier_id']


def coordinate_committee_contributions(
    comm_objs: List[PlayerAI],
    contract: ContractSpec,
    round_num: int,
    promised_supplier_id: Optional[int],
    declarations: Dict[int, PlayerDeclaration],
    banker_score: int
) -> Tuple[List[ResourceCard], int, List[Dict], Dict[int, int]]:
    planning_order = []
    if promised_supplier_id is not None:
        sup_obj = next((p for p in comm_objs if p.id == promised_supplier_id), None)
        if sup_obj:
            planning_order.append(sup_obj)
    for p in comm_objs:
        if p not in planning_order:
            planning_order.append(p)

    submitted_all_cards: List[ResourceCard] = []
    total_tokens_spent = 0
    submitted_cards_data = []
    cumulative_committed_val = 0
    is_match_point = (banker_score == 3)
    promised_values = {}

    for idx, p in enumerate(planning_order):
        is_req_responsible = (p.id == promised_supplier_id)
        remaining_members = len(planning_order) - idx
        remaining_target = max(0, contract.target_value - cumulative_committed_val)
        quota_for_p = remaining_target / remaining_members

        declared_p_val = declarations[p.id].claimed_value if p.id in declarations else 0
        if p.role == Role.BANKER and round_num >= 3 and contract.target_value >= 8:
            quota_for_p = max(quota_for_p, min(declared_p_val, contract.target_value / contract.committee_size))

        should_sabotage = False
        if p.role == Role.INTERN:
            if p.profile == InternProfile.A_AGGRESSIVE:
                should_sabotage = True
            elif p.profile == InternProfile.B_SLEEPER:
                if p.is_active_saboteur:
                    should_sabotage = (round_num >= 3)
                else:
                    should_sabotage = (round_num >= 4)
            elif p.profile == InternProfile.C_HEDGE:
                has_toxic = any(c.card_type == CardType.TOXIC for c in p.hand)
                should_sabotage = (has_toxic and round_num >= 3) or (round_num >= 4)

        honest_cards, honest_tokens, honest_val = p.plan_honest_contribution(contract, round_num, is_req_responsible, quota_for_p, is_match_point=is_match_point)
        cumulative_committed_val += honest_val
        promised_values[p.id] = honest_val

        if not should_sabotage:
            actual_cards = honest_cards
            actual_tokens = honest_tokens
        else:
            actual_cards, actual_tokens = p.plan_sabotage_contribution(contract, round_num, is_req_responsible)

        p.interest_tokens -= actual_tokens
        total_tokens_spent += actual_tokens

        for c in actual_cards:
            if c in p.hand:
                p.hand.remove(c)
            if c.card_type in p.public_known_cards:
                p.public_known_cards.remove(c.card_type)

        submitted_all_cards.extend(actual_cards)
        submitted_cards_data.append({
            'player_id': p.id,
            'is_req_responsible': is_req_responsible,
            'tokens_spent': actual_tokens,
            'cards': [{
                'type': c.card_type.name,
                'name': c.card_type.value,
                'base': c.base_value
            } for c in actual_cards]
        })

    return submitted_all_cards, total_tokens_spent, submitted_cards_data, promised_values


def simulate_game(
    game_idx: int,
    profile: InternProfile,
    seed: Optional[int] = None,
    record_trace: bool = False
) -> Dict:
    rng = random.Random(seed if seed is not None else (int(time.time() * 1000) ^ game_idx))
    
    roles = [Role.BANKER] * 3 + [Role.INTERN] * 2
    rng.shuffle(roles)

    intern_count = 0
    players = []
    for i in range(5):
        is_active = False
        if roles[i] == Role.INTERN:
            is_active = (intern_count == 0)
            intern_count += 1
        players.append(PlayerAI(i, roles[i], profile, rng, is_active_saboteur=is_active))

    players_metadata = [{'id': p.id, 'role': p.role.value} for p in players]

    deck = DeckManager(seed=rng.randint(0, 10**9))
    deck.refill_open_market(3)

    for p in players:
        p.hand = [ResourceCard(CardType.CO), ResourceCard(CardType.VN), ResourceCard(CardType.TI)] + deck.draw_blind(1)

    banker_score = 0
    intern_score = 0
    curr_chair = 0
    round_count = 0
    ops = [rng.choice(SEVEN_TIERS_CATALOG[t]) for t in range(1, 8)]
    suspicion_history = []
    rounds_data = []

    for r_idx, contract in enumerate(ops):
        round_count += 1

        for p in players:
            needed = max(0, 4 - len(p.hand))
            for _ in range(needed):
                if p.role == Role.BANKER and contract.req_commodity in deck.open_market:
                    c = deck.draw_from_market(contract.req_commodity)
                    p.public_known_cards.append(contract.req_commodity)
                elif p.role == Role.BANKER and any(card in deck.open_market for card in [CardType.SF, CardType.WILD, CardType.TI]):
                    noble = next(card for card in [CardType.WILD, CardType.SF, CardType.TI] if card in deck.open_market)
                    c = deck.draw_from_market(noble)
                    p.public_known_cards.append(noble)
                else:
                    c = deck.draw_blind(1)[0]
                p.hand.append(c)

        hands_before = {
            p.id: {
                'cards': [{'type': c.card_type.name, 'name': c.card_type.value, 'base': c.base_value} for c in p.hand],
                'tokens': p.interest_tokens
            } for p in players
        }

        bankers = [p for p in players if p.role == Role.BANKER]
        
        sus_avg = {}
        sus_by_banker = {}
        for target_id in range(5):
            sus_vals = [b.suspicions[target_id] for b in bankers if b.id != target_id]
            sus_avg[target_id] = round(float(np.mean(sus_vals)), 2) if sus_vals else 0.0
        
        for b in bankers:
            sus_by_banker[b.id] = {target_id: round(b.suspicions[target_id], 2) for target_id in range(5)}

        suspicion_history.append(sus_avg)

        consecutive_vetoes = 0
        approved_committee = None
        promised_supplier = None
        all_declarations = {}

        while consecutive_vetoes < 3 and approved_committee is None:
            chair = players[curr_chair]
            declarations = {p.id: p.make_public_declaration(contract, round_count) for p in players}
            all_declarations = declarations

            chosen_comm, assigned_req_player = choose_optimal_committee(chair, players, contract, declarations)

            votes = {p.id: p.vote_on_proposal(curr_chair, chosen_comm, contract, round_count) for p in players}
            if sum(votes.values()) >= 3:
                approved_committee = chosen_comm
                promised_supplier = assigned_req_player
            else:
                consecutive_vetoes += 1
                curr_chair = (curr_chair + 1) % 5

        if approved_committee is None:
            all_comms = list(itertools.combinations(range(5), contract.committee_size))
            best_comm = min(all_comms, key=lambda cm: sum(sum(p.suspicions[cid] for p in players if p.role == Role.BANKER) for cid in cm))
            approved_committee = list(best_comm)
            promised_supplier = None

        for p in players:
            if p.id not in approved_committee:
                p.accumulate_holding_interest()

        comm_objs = [players[pid] for pid in approved_committee]

        submitted_cards, total_tokens_spent, submitted_cards_data, promised_values = coordinate_committee_contributions(
            comm_objs, contract, round_count, promised_supplier, all_declarations, banker_score
        )

        deck.discard(submitted_cards)
        is_pure_bankers = all(p.role == Role.BANKER for p in comm_objs)
        is_success, total_val, has_req = evaluate_contract_outcome(submitted_cards, total_tokens_spent, contract, is_pure_banker_committee=is_pure_bankers)

        credits_awarded = []
        if is_success:
            banker_score += 1
            for p in comm_objs:
                p.claim_success_credit()
                credits_awarded.append(p.id)

            decay = 0.05 if contract.tier <= 2 else (0.15 if contract.tier <= 4 else 0.30)
            for bp in players:
                if bp.role == Role.BANKER:
                    for cid in approved_committee:
                        if cid != bp.id and cid not in bp.known_traitors:
                            bp.suspicions[cid] = max(0.05, bp.suspicions[cid] - decay)
        else:
            intern_score += 1
            has_toxic = any(c.card_type == CardType.TOXIC for c in submitted_cards)

            for bp in players:
                if bp.role == Role.BANKER:
                    if len(approved_committee) == 2 and bp.id in approved_committee:
                        partner_id = next(cid for cid in approved_committee if cid != bp.id)
                        bp.suspicions[partner_id] = 1.00
                        bp.known_traitors.add(partner_id)
                    elif len(approved_committee) == 2 and bp.id not in approved_committee:
                        for cid in approved_committee:
                            bp.suspicions[cid] = min(0.60, bp.suspicions[cid] + 0.20)
                    else:
                        penalty = 0.15 if len(approved_committee) >= 4 else 0.25
                        for cid in approved_committee:
                            if cid != bp.id:
                                bp.suspicions[cid] = min(0.85, bp.suspicions[cid] + penalty)

        if record_trace:
            rounds_data.append({
                'round_num': round_count,
                'contract': {
                    'name': contract.name,
                    'tier': contract.tier,
                    'target': contract.target_value,
                    'req_commodity': contract.req_commodity.value if contract.req_commodity else None,
                    'req_count': contract.req_commodity_count,
                    'committee_size': contract.committee_size,
                    'cost_per_player': contract.cost_per_player
                },
                'chair_id': curr_chair,
                'committee': approved_committee,
                'promised_supplier': promised_supplier,
                'declarations': {pid: {'claims_req': d.claims_req, 'claimed_val': d.claimed_value, 'tokens_offered': d.tokens_offered, 'prefers_bench': d.prefers_bench, 'offered_desc': d.offered_desc} for pid, d in all_declarations.items()},
                'votes': votes,
                'submitted': submitted_cards_data,
                'total_tokens_spent': total_tokens_spent,
                'total_value': total_val,
                'has_req': has_req,
                'is_success': is_success,
                'banker_score': banker_score,
                'intern_score': intern_score,
                'credits_awarded': credits_awarded,
                'hands_before': hands_before,
                'suspicions': {
                    'avg': sus_avg,
                    'by_banker': sus_by_banker,
                    'known_traitors': {b.id: list(b.known_traitors) for b in bankers}
                }
            })

        if banker_score >= 4:
            res_dict = {
                "winner": Role.BANKER.value,
                "cause": "4 Contratos Concluidos",
                "rounds": round_count,
                "b_score": banker_score,
                "i_score": intern_score,
                "profile": profile.value,
                "sus_history": suspicion_history,
                "players_metadata": players_metadata
            }
            if record_trace:
                res_dict['rounds_data'] = rounds_data
            return res_dict
        elif intern_score >= 4:
            res_dict = {
                "winner": Role.INTERN.value,
                "cause": "4 Contratos Reprovados",
                "rounds": round_count,
                "b_score": banker_score,
                "i_score": intern_score,
                "profile": profile.value,
                "sus_history": suspicion_history,
                "players_metadata": players_metadata
            }
            if record_trace:
                res_dict['rounds_data'] = rounds_data
            return res_dict

        curr_chair = (curr_chair + 1) % 5

    w = Role.BANKER.value if banker_score > intern_score else Role.INTERN.value
    res_dict = {
        "winner": w,
        "cause": "Fim das 7 Rodadas",
        "rounds": 7,
        "b_score": banker_score,
        "i_score": intern_score,
        "profile": profile.value,
        "sus_history": suspicion_history,
        "players_metadata": players_metadata
    }
    if record_trace:
        res_dict['rounds_data'] = rounds_data
    return res_dict


def run_full_100k_simulation(n=100000):
    print("=" * 80)
    print(" SIMULADOR MONTE CARLO - MOTOR OFICIAL v14.0 (COMITÊ DE 4 NA R5) (100k) ")
    print("=" * 80)
    t0 = time.time()
    results = []
    profiles = [InternProfile.A_AGGRESSIVE, InternProfile.B_SLEEPER, InternProfile.C_HEDGE]

    for i in range(n):
        prof = random.choice(profiles)
        res = simulate_game(i, prof, seed=999000 + i)
        results.append(res)

        if (i + 1) % 10000 == 0:
            print(f"   [Simulação v14.0] {i + 1:6,d} / {n:,} ({(i+1)/n*100:5.1f}%) | Tempo: {time.time() - t0:4.1f}s")
            sys.stdout.flush()

    df = pd.DataFrame(results)
    b_wins = (df["winner"] == Role.BANKER.value).sum()
    i_wins = (df["winner"] == Role.INTERN.value).sum()

    print("\n" + "=" * 80)
    print("             RELATÓRIO FINAL DE BALANCEAMENTO (100.000 PARTIDAS)")
    print("=" * 80)
    print(f"\n1. WIN RATE GLOBAL")
    print(f"   - Banqueiros : {(b_wins/n)*100:6.2f}% ({b_wins:,} vitórias)")
    print(f"   - Estagiários: {(i_wins/n)*100:6.2f}% ({i_wins:,} vitórias)")
    print(f"   - Duração Média: {df['rounds'].mean():.2f} ± {df['rounds'].std():.2f} rodadas")

    print(f"\n2. MATRIZ DE PLACARES FINAIS (Primeiro a 4 Pontos)")
    print("-" * 60)
    df["score"] = df["b_score"].astype(str) + " x " + df["i_score"].astype(str)
    score_counts = df["score"].value_counts()
    for sc, cnt in score_counts.head(7).items():
        tag = "[Clímax 7ª Rodada]" if "4 x 3" in sc or "3 x 4" in sc else ""
        print(f"   * {sc:<15}: {cnt:>8,d} ({(cnt/n)*100:5.2f}%) {tag}")

    print(f"\n3. PERFORMANCE COMPARATIVA POR PERFIL DE IA")
    print("-" * 80)
    print(f"{'Perfil':<35} | {'WR Estagiários':<16} | {'WR Banqueiros':<15} | {'Duração':<10}")
    print("-" * 80)
    for prof in profiles:
        sub = df[df["profile"] == prof.value]
        sub_iw = (sub["winner"] == Role.INTERN.value).sum()
        sub_bw = (sub["winner"] == Role.BANKER.value).sum()
        sub_len = len(sub)
        print(f"{prof.value:<35} | {(sub_iw/sub_len)*100:>14.2f}% | {(sub_bw/sub_len)*100:>13.2f}% | {sub['rounds'].mean():>6.2f} ops")
    print("=" * 80)


def generate_traces_and_save():
    g1 = simulate_game(101, InternProfile.B_SLEEPER, seed=112233, record_trace=True)
    g2 = simulate_game(202, InternProfile.A_AGGRESSIVE, seed=445566, record_trace=True)
    g3 = simulate_game(303, InternProfile.C_HEDGE, seed=778899, record_trace=True)

    def format_trace(g, prof, seed):
        players_meta = g['players_metadata']
        banker_ids = [p['id'] for p in players_meta if p['role'] == Role.BANKER.value]
        intern_ids = [p['id'] for p in players_meta if p['role'] == Role.INTERN.value]
        return {
            'seed': seed,
            'profile': prof.value,
            'players': players_meta,
            'banker_ids': banker_ids,
            'intern_ids': intern_ids,
            'final_winner': g['winner'],
            'final_score': f"{g['b_score']} x {g['i_score']}",
            'total_rounds': g['rounds'],
            'rounds': g['rounds_data']
        }

    all_traces = {
        'sleeper_game': format_trace(g1, InternProfile.B_SLEEPER, 112233),
        'aggressive_game': format_trace(g2, InternProfile.A_AGGRESSIVE, 445566),
        'hedge_game': format_trace(g3, InternProfile.C_HEDGE, 778899)
    }

    with open('game_traces.json', 'w', encoding='utf-8') as f:
        json.dump(all_traces, f, indent=2, ensure_ascii=False)
    print("Traces v14.0 gerados com sucesso!")


if __name__ == '__main__':
    generate_traces_and_save()
