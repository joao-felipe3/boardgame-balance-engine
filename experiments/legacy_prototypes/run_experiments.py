# -*- coding: utf-8 -*-
"""
BTG Madagascar - Framework de Experimentos de Game Design Econômico
===================================================================
Testa 7 configurações:
1. Individual: Fator 1 (Teto de Juros +2j máx)
2. Individual: Fator 2 (Exigência Rígida de Commodities)
3. Individual: Fator 3 (Metas com Margem Apertada)
4. Par: Fator 1 + Fator 2
5. Par: Fator 1 + Fator 3
6. Par: Fator 2 + Fator 3
7. Triplo: Fator 1 + Fator 2 + Fator 3
"""

import random
import time
import sys
from dataclasses import dataclass
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

@dataclass
class ResourceCard:
    card_type: CardType
    interest_accumulated: int = 0

    @property
    def effective_value(self) -> int:
        if self.card_type == CardType.TOXIC:
            return CARD_BASE_VALUES[CardType.TOXIC]
        return CARD_BASE_VALUES[self.card_type] + self.interest_accumulated

    def __repr__(self):
        j = f"+{self.interest_accumulated}j" if self.interest_accumulated > 0 else ""
        return f"{self.card_type.name}(val={self.effective_value}{j})"


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
    req_commodity_count: int = 1  # Fator 2: Quantidade exigida do insumo


def get_catalog(use_tight_margins: bool, use_rigid_commodities: bool) -> Dict[int, List[ContractSpec]]:
    if use_tight_margins:
        # Metas Apertadas (Fator 3)
        return {
            1: [
                ContractSpec("Arbitragem Simples", 1, 2, 1, 3),
                ContractSpec("Exportacao de Baunilha", 1, 2, 1, 4, req_commodity=CardType.VN, req_commodity_count=1),
            ],
            2: [
                ContractSpec("Mineracao de Cobalto", 2, 2, 1, 5, req_commodity=CardType.CO, req_commodity_count=1),
                ContractSpec("Lote Agricola", 2, 2, 1, 5, req_commodity=CardType.VN, req_commodity_count=1),
            ],
            3: [
                ContractSpec("Sindicato de Titanio", 3, 3, 1, 9, req_commodity=CardType.TI, req_commodity_count=2 if use_rigid_commodities else 1),
                ContractSpec("Logistica Portuaria", 3, 3, 1, 8, req_commodity=CardType.CO, req_commodity_count=2 if use_rigid_commodities else 1),
            ],
            4: [
                ContractSpec("Refino Metalurgico", 4, 3, 1, 11, req_commodity=CardType.TI, req_commodity_count=2 if use_rigid_commodities else 1),
                ContractSpec("Consorcio Agro-Industrial", 4, 3, 1, 11, req_commodity=CardType.VN, req_commodity_count=2 if use_rigid_commodities else 1),
            ],
            5: [
                ContractSpec("Cofre de Gemas", 5, 2, 2, 15, req_commodity=CardType.SF, req_commodity_count=2 if use_rigid_commodities else 1),
                ContractSpec("Fundicao Estrategica", 5, 2, 2, 14, req_commodity=CardType.TI, req_commodity_count=2 if use_rigid_commodities else 1),
            ],
            6: [
                ContractSpec("Consorcio Safira", 6, 3, 2, 20, req_commodity=CardType.SF, req_commodity_count=2 if use_rigid_commodities else 1),
                ContractSpec("Complexo Greenfield", 6, 3, 2, 19, req_commodity=CardType.TI, req_commodity_count=2 if use_rigid_commodities else 1),
            ],
            7: [
                ContractSpec("Holding Global BTG (Climax)", 7, 3, 2, 24, req_commodity=CardType.SF, req_commodity_count=3 if use_rigid_commodities else 1),
            ]
        }
    else:
        # Metas Padrão (Sem Fator 3)
        return {
            1: [
                ContractSpec("Arbitragem Simples", 1, 2, 1, 3),
                ContractSpec("Exportacao de Baunilha", 1, 2, 1, 4, req_commodity=CardType.VN, req_commodity_count=1),
            ],
            2: [
                ContractSpec("Mineracao de Cobalto", 2, 2, 1, 4, req_commodity=CardType.CO, req_commodity_count=1),
                ContractSpec("Lote Agricola", 2, 2, 1, 4, req_commodity=CardType.VN, req_commodity_count=1),
            ],
            3: [
                ContractSpec("Sindicato de Titanio", 3, 3, 1, 8, req_commodity=CardType.TI, req_commodity_count=2 if use_rigid_commodities else 1),
                ContractSpec("Logistica Portuaria", 3, 3, 1, 7, req_commodity=CardType.CO, req_commodity_count=2 if use_rigid_commodities else 1),
            ],
            4: [
                ContractSpec("Refino Metalurgico", 4, 3, 1, 10, req_commodity=CardType.TI, req_commodity_count=2 if use_rigid_commodities else 1),
                ContractSpec("Consorcio Agro-Industrial", 4, 3, 1, 10, req_commodity=CardType.VN, req_commodity_count=2 if use_rigid_commodities else 1),
            ],
            5: [
                ContractSpec("Cofre de Gemas", 5, 2, 2, 13, req_commodity=CardType.SF, req_commodity_count=2 if use_rigid_commodities else 1),
                ContractSpec("Fundicao Estrategica", 5, 2, 2, 12, req_commodity=CardType.TI, req_commodity_count=2 if use_rigid_commodities else 1),
            ],
            6: [
                ContractSpec("Consorcio Safira", 6, 3, 2, 17, req_commodity=CardType.SF, req_commodity_count=2 if use_rigid_commodities else 1),
                ContractSpec("Complexo Greenfield", 6, 3, 2, 16, req_commodity=CardType.TI, req_commodity_count=2 if use_rigid_commodities else 1),
            ],
            7: [
                ContractSpec("Holding Global BTG (Climax)", 7, 3, 2, 21, req_commodity=CardType.SF, req_commodity_count=3 if use_rigid_commodities else 1),
            ]
        }


class DeckManager:
    __slots__ = ('draw_pile', 'discard_pile', 'rng')

    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.draw_pile = INITIAL_COMMERCIAL_DECK.copy()
        self.rng.shuffle(self.draw_pile)
        self.discard_pile: List[CardType] = []

    def draw(self, n: int = 1) -> List[ResourceCard]:
        drawn = []
        for _ in range(n):
            if not self.draw_pile:
                if not self.discard_pile:
                    drawn.append(ResourceCard(CardType.CO, 0))
                    continue
                self.draw_pile = self.discard_pile.copy()
                self.discard_pile = []
                self.rng.shuffle(self.draw_pile)
            card_t = self.draw_pile.pop()
            drawn.append(ResourceCard(card_t, 0))
        return drawn

    def discard(self, cards: List[ResourceCard]):
        self.discard_pile.extend([c.card_type for c in cards])


@dataclass
class PlayerDeclaration:
    player_id: int
    claims_req: bool
    claimed_value: int
    req_commodity_value: int
    prefers_bench: bool
    offered_desc: str


class PlayerAI:
    __slots__ = ('id', 'role', 'profile', 'rng', 'hand', 'suspicions', 'known_traitors', 'credits_accumulated', 'max_interest_cap')

    def __init__(self, player_id: int, role: Role, profile: InternProfile, rng: random.Random, max_interest_cap: int = 99):
        self.id = player_id
        self.role = role
        self.profile = profile
        self.rng = rng
        self.hand: List[ResourceCard] = []
        self.suspicions: Dict[int, float] = {i: 0.40 for i in range(5)}
        self.suspicions[self.id] = 0.0 if role == Role.BANKER else 1.0
        self.known_traitors: Set[int] = set()
        self.credits_accumulated = 0
        self.max_interest_cap = max_interest_cap

    def accumulate_holding_interest(self):
        for card in self.hand:
            if card.card_type != CardType.TOXIC:
                if card.interest_accumulated < self.max_interest_cap:
                    card.interest_accumulated += 1

    def claim_success_credit(self):
        self.credits_accumulated += 1
        if self.credits_accumulated >= 1:
            self.credits_accumulated -= 1
            if self.role == Role.BANKER:
                self.hand.append(ResourceCard(CardType.WILD, 0))
            else:
                self.hand.append(ResourceCard(CardType.TOXIC, 0))

    def make_public_declaration(self, contract: ContractSpec, round_num: int) -> PlayerDeclaration:
        has_req_real = False
        req_val = 0
        if contract.req_commodity is not None:
            req_cards = [c for c in self.hand if c.card_type in (contract.req_commodity, CardType.WILD)]
            if req_cards:
                has_req_real = True
                req_val = max(c.effective_value for c in req_cards)

        cost = contract.cost_per_player
        expected_quota = contract.target_value / contract.committee_size

        eligible_cards = [c for c in self.hand if c.card_type != CardType.TOXIC]
        if round_num <= 3 and contract.req_commodity != CardType.SF:
            non_nobles = [c for c in eligible_cards if c.card_type not in (CardType.SF, CardType.WILD)]
            if len(non_nobles) >= cost:
                eligible_cards = non_nobles

        eligible_cards.sort(key=lambda c: -c.effective_value)
        best_val = sum(c.effective_value for c in eligible_cards[:cost]) if eligible_cards else 0
        is_dry = (best_val < expected_quota) and (round_num >= 2) and (not has_req_real)

        if self.role == Role.BANKER:
            top_card_names = [f"{c.card_type.name.split(' ')[0]}({c.effective_value}pts)" for c in eligible_cards[:cost]]
            offered_str = " + ".join(top_card_names) if top_card_names else "Liquidez Baixa"
            return PlayerDeclaration(self.id, has_req_real, best_val, req_val, prefers_bench=is_dry, offered_desc=offered_str)
        else:
            if self.profile == InternProfile.A_AGGRESSIVE:
                claims = True if contract.req_commodity is not None else False
                req_v = req_val if has_req_real else max(3, int(expected_quota))
                offered_str = f"{contract.req_commodity.name.split(' ')[0]}(~{req_v}pts)" if contract.req_commodity else f"Liquidez Alta(~{int(expected_quota)}pts)"
                return PlayerDeclaration(self.id, claims, max(best_val, int(expected_quota)), req_v, prefers_bench=False, offered_desc=offered_str)
            elif self.profile == InternProfile.B_SLEEPER:
                if round_num <= 2:
                    top_card_names = [f"{c.card_type.name.split(' ')[0]}({c.effective_value}pts)" for c in eligible_cards[:cost]]
                    offered_str = " + ".join(top_card_names) if top_card_names else "Liquidez Baixa"
                    return PlayerDeclaration(self.id, has_req_real, best_val, req_val, prefers_bench=is_dry, offered_desc=offered_str)
                else:
                    has_toxic = any(c.card_type == CardType.TOXIC for c in self.hand)
                    claims = True if (contract.req_commodity is not None and has_toxic) else has_req_real
                    req_v = req_val if has_req_real else max(4, int(expected_quota))
                    offered_str = f"{contract.req_commodity.name.split(' ')[0]}(~{req_v}pts)" if (claims and contract.req_commodity) else f"Liquidez Forte(~{int(expected_quota)}pts)"
                    return PlayerDeclaration(self.id, claims, max(best_val, int(expected_quota)), req_v, prefers_bench=False, offered_desc=offered_str)
            elif self.profile == InternProfile.C_HEDGE:
                top_card_names = [f"{c.card_type.name.split(' ')[0]}({c.effective_value}pts)" for c in eligible_cards[:cost]]
                offered_str = " + ".join(top_card_names) if top_card_names else "Liquidez Baixa"
                return PlayerDeclaration(self.id, has_req_real, best_val, req_val, prefers_bench=False, offered_desc=offered_str)

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
    ) -> Tuple[List[ResourceCard], int]:
        cost = contract.cost_per_player
        pos_cards = [c for c in self.hand if c.card_type != CardType.TOXIC]
        if not pos_cards:
            return self.hand[:cost], sum(c.effective_value for c in self.hand[:cost])

        valid_combos = list(itertools.combinations(pos_cards, cost))
        if not valid_combos:
            valid_combos = list(itertools.combinations(self.hand, cost))
        if not valid_combos:
            return self.hand[:cost], sum(c.effective_value for c in self.hand[:cost])

        if is_responsible_for_req and contract.req_commodity is not None:
            req = contract.req_commodity
            req_combos = [cb for cb in valid_combos if any(c.card_type in (req, CardType.WILD) for c in cb)]
            if req_combos:
                valid_combos = req_combos

        if is_match_point or contract.tier >= 7:
            best_combo = max(valid_combos, key=lambda cb: sum(c.effective_value for c in cb))
            return list(best_combo), sum(c.effective_value for c in best_combo)

        if contract.tier >= 5:
            safe_combos = [cb for cb in valid_combos if sum(c.effective_value for c in cb) >= quota_needed]
            if safe_combos:
                best_combo = min(safe_combos, key=lambda cb: (sum(c.effective_value for c in cb) if sum(c.effective_value for c in cb) >= quota_needed + 2 else sum(c.effective_value for c in cb) + 20))
            else:
                best_combo = max(valid_combos, key=lambda cb: sum(c.effective_value for c in cb))
            return list(best_combo), sum(c.effective_value for c in best_combo)

        non_noble_combos = [cb for cb in valid_combos if not any(c.card_type in (CardType.SF, CardType.WILD) for c in cb)]
        winning_non_nobles = [cb for cb in non_noble_combos if sum(c.effective_value for c in cb) >= quota_needed]

        if winning_non_nobles and round_num <= 3 and contract.req_commodity != CardType.SF:
            best_combo = min(winning_non_nobles, key=lambda cb: sum(c.effective_value for c in cb))
        else:
            def combo_score(cb):
                val = sum(c.effective_value for c in cb)
                diff = val - quota_needed
                has_safira = any(c.card_type in (CardType.SF, CardType.WILD) for c in cb)
                if diff >= 0:
                    return (0, 10 if (has_safira and round_num <= 3 and contract.req_commodity != CardType.SF) else 0, diff)
                else:
                    return (1, 0, -diff)

            best_combo = min(valid_combos, key=combo_score)

        val = sum(c.effective_value for c in best_combo)
        return list(best_combo), val

    def plan_sabotage_contribution(self, contract: ContractSpec) -> List[ResourceCard]:
        cost = contract.cost_per_player
        toxic_cards = [c for c in self.hand if c.card_type == CardType.TOXIC]
        low_pos = sorted([c for c in self.hand if c.card_type != CardType.TOXIC], key=lambda c: c.effective_value)

        chosen: List[ResourceCard] = []
        while len(chosen) < cost and toxic_cards:
            chosen.append(toxic_cards.pop(0))
        while len(chosen) < cost and low_pos:
            chosen.append(low_pos.pop(0))
        while len(chosen) < cost and self.hand:
            chosen.append(self.hand[0])

        return chosen[:cost]


def evaluate_contract_outcome(
    submitted_cards: List[ResourceCard],
    contract: ContractSpec
) -> Tuple[bool, int, bool]:
    total_val = sum(c.effective_value for c in submitted_cards)
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
    all_pids = [p.id for p in players if p.id not in chair.known_traitors and chair.suspicions[p.id] < 0.85]
    if len(all_pids) < c_size:
        all_pids = [p.id for p in players]

    candidate_comms = list(itertools.combinations(all_pids, c_size))
    evaluated_comms = []

    for comm in candidate_comms:
        supplier_id = None
        if contract.req_commodity is not None:
            suppliers = [pid for pid in comm if declarations[pid].claims_req]
            if len(suppliers) < contract.req_commodity_count:
                continue
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

    if not evaluated_comms:
        chosen = [chair.id] + [p for p in all_pids if p != chair.id][:c_size - 1]
        return chosen, (chair.id if declarations[chair.id].claims_req else None)

    evaluated_comms.sort(key=lambda x: (
        not x['is_viable'],
        x['bench_count'],
        x['avg_sus'],
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
) -> Tuple[List[ResourceCard], List[Dict], Dict[int, int]]:
    planning_order = []
    if promised_supplier_id is not None:
        sup_obj = next((p for p in comm_objs if p.id == promised_supplier_id), None)
        if sup_obj:
            planning_order.append(sup_obj)
    for p in comm_objs:
        if p not in planning_order:
            planning_order.append(p)

    submitted_all: List[ResourceCard] = []
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
                has_toxic = any(c.card_type == CardType.TOXIC for c in p.hand)
                should_sabotage = (round_num >= 3 and has_toxic) or (round_num >= 4)
            elif p.profile == InternProfile.C_HEDGE:
                has_toxic = any(c.card_type == CardType.TOXIC for c in p.hand)
                should_sabotage = (has_toxic and round_num >= 3) or (round_num >= 4)

        honest_cards, honest_val = p.plan_honest_contribution(contract, round_num, is_req_responsible, quota_for_p, is_match_point=is_match_point)
        cumulative_committed_val += honest_val
        promised_values[p.id] = honest_val

        if not should_sabotage:
            actual_cards = honest_cards
        else:
            actual_cards = p.plan_sabotage_contribution(contract)

        for c in actual_cards:
            if c in p.hand:
                p.hand.remove(c)

        submitted_all.extend(actual_cards)
        submitted_cards_data.append({
            'player_id': p.id,
            'is_req_responsible': is_req_responsible,
            'cards': [{
                'type': c.card_type.name,
                'name': c.card_type.value,
                'base': CARD_BASE_VALUES[c.card_type],
                'interest': c.interest_accumulated,
                'effective': c.effective_value
            } for c in actual_cards]
        })

    return submitted_all, submitted_cards_data, promised_values


def simulate_game(
    game_idx: int,
    profile: InternProfile,
    seed: Optional[int] = None,
    max_interest_cap: int = 99,
    use_tight_margins: bool = False,
    use_rigid_commodities: bool = False
) -> Dict:
    rng = random.Random(seed if seed is not None else (int(time.time() * 1000) ^ game_idx))
    catalog = get_catalog(use_tight_margins, use_rigid_commodities)

    roles = [Role.BANKER] * 3 + [Role.INTERN] * 2
    rng.shuffle(roles)
    players = [PlayerAI(i, roles[i], profile, rng, max_interest_cap=max_interest_cap) for i in range(5)]

    deck = DeckManager(seed=rng.randint(0, 10**9))
    for p in players:
        p.hand = deck.draw(3)

    banker_score = 0
    intern_score = 0
    curr_chair = 0
    round_count = 0
    ops = [rng.choice(catalog[t]) for t in range(1, 8)]

    for r_idx, contract in enumerate(ops):
        round_count += 1

        for p in players:
            p.hand.extend(deck.draw(1))

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
            chair = players[curr_chair]
            others = [p.id for p in players if p.id != chair.id]
            approved_committee = [chair.id] + others[:contract.committee_size - 1]
            promised_supplier = None

        for p in players:
            if p.id not in approved_committee:
                p.accumulate_holding_interest()

        comm_objs = [players[pid] for pid in approved_committee]

        submitted_all, submitted_cards_data, promised_values = coordinate_committee_contributions(
            comm_objs, contract, round_count, promised_supplier, all_declarations, banker_score
        )

        deck.discard(submitted_all)
        is_success, total_val, has_req = evaluate_contract_outcome(submitted_all, contract)

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
            has_toxic = any(c.card_type == CardType.TOXIC for c in submitted_all)
            broken_req_promise = (contract.req_commodity is not None and not has_req and promised_supplier is not None)
            penalty = 0.35 if contract.tier <= 2 else 0.55

            for bp in players:
                if bp.role == Role.BANKER:
                    if broken_req_promise and promised_supplier != bp.id:
                        bp.suspicions[promised_supplier] = 0.95
                        bp.known_traitors.add(promised_supplier)

                    if bp.id in approved_committee and len(approved_committee) == 2:
                        partner_id = next(cid for cid in approved_committee if cid != bp.id)
                        partner_sub_val = sum(c['effective'] for s in submitted_cards_data if s['player_id'] == partner_id for c in s['cards'])
                        partner_promised = promised_values.get(partner_id, 0)

                        if partner_sub_val < partner_promised or has_toxic:
                            bp.suspicions[partner_id] = 1.00
                            bp.known_traitors.add(partner_id)
                        else:
                            bp.suspicions[partner_id] = min(0.95, bp.suspicions[partner_id] + penalty)
                    else:
                        delta = 0.55 if has_toxic else penalty
                        if len(approved_committee) >= 3:
                            delta *= 0.70
                        for cid in approved_committee:
                            if cid != bp.id and cid != promised_supplier:
                                bp.suspicions[cid] = min(0.95, bp.suspicions[cid] + delta)

        if banker_score >= 4:
            return {"winner": Role.BANKER.value, "rounds": round_count, "b_score": banker_score, "i_score": intern_score, "profile": profile.value}
        elif intern_score >= 4:
            return {"winner": Role.INTERN.value, "rounds": round_count, "b_score": banker_score, "i_score": intern_score, "profile": profile.value}

        curr_chair = (curr_chair + 1) % 5

    w = Role.BANKER.value if banker_score > intern_score else Role.INTERN.value
    return {"winner": w, "rounds": 7, "b_score": banker_score, "i_score": intern_score, "profile": profile.value}


def run_experiment_suite(n_per_config=20000):
    configs = [
        ("1. [Individual] Teto de Juros (+2j max)", {"max_interest_cap": 2, "use_tight_margins": False, "use_rigid_commodities": False}),
        ("2. [Individual] Exigência Rígida de Insumos", {"max_interest_cap": 99, "use_tight_margins": False, "use_rigid_commodities": True}),
        ("3. [Individual] Metas de Margem Apertada", {"max_interest_cap": 99, "use_tight_margins": True, "use_rigid_commodities": False}),
        ("4. [Par] Teto + Insumos Rígidos", {"max_interest_cap": 2, "use_tight_margins": False, "use_rigid_commodities": True}),
        ("5. [Par] Teto + Metas Apertadas", {"max_interest_cap": 2, "use_tight_margins": True, "use_rigid_commodities": False}),
        ("6. [Par] Insumos Rígidos + Metas Apertadas", {"max_interest_cap": 99, "use_tight_margins": True, "use_rigid_commodities": True}),
        ("7. [Triplo] Teto + Insumos + Metas Apertadas", {"max_interest_cap": 2, "use_tight_margins": True, "use_rigid_commodities": True}),
    ]

    profiles = [InternProfile.A_AGGRESSIVE, InternProfile.B_SLEEPER, InternProfile.C_HEDGE]
    summary_rows = []

    print("=" * 90)
    print(" INICIANDO BATERIA DE EXPERIMENTOS DE GAME DESIGN (7 CONFIGURAÇÕES x 20.000 PARTIDAS) ")
    print("=" * 90)

    for idx, (name, params) in enumerate(configs, 1):
        t0 = time.time()
        results = []
        for i in range(n_per_config):
            prof = random.choice(profiles)
            res = simulate_game(i, prof, seed=100000 * idx + i, **params)
            results.append(res)

        df = pd.DataFrame(results)
        b_wins = (df["winner"] == Role.BANKER.value).sum()
        i_wins = (df["winner"] == Role.INTERN.value).sum()
        b_wr = (b_wins / n_per_config) * 100
        i_wr = (i_wins / n_per_config) * 100
        avg_r = df["rounds"].mean()

        # WR por perfil
        sub_a = df[df["profile"] == InternProfile.A_AGGRESSIVE.value]
        sub_b = df[df["profile"] == InternProfile.B_SLEEPER.value]
        sub_c = df[df["profile"] == InternProfile.C_HEDGE.value]

        wr_a = ((sub_a["winner"] == Role.INTERN.value).sum() / len(sub_a)) * 100
        wr_b = ((sub_b["winner"] == Role.INTERN.value).sum() / len(sub_b)) * 100
        wr_c = ((sub_c["winner"] == Role.INTERN.value).sum() / len(sub_c)) * 100

        # Placares
        df["score"] = df["b_score"].astype(str) + " x " + df["i_score"].astype(str)
        climax_pct = ((df["score"].isin(["4 x 3", "3 x 4"])).sum() / n_per_config) * 100

        print(f"[{idx}/7] {name:<45} | WR Banq: {b_wr:5.1f}% | WR Estag: {i_wr:5.1f}% | Clímax: {climax_pct:4.1f}% | Tempo: {time.time()-t0:4.1f}s")
        sys.stdout.flush()

        summary_rows.append({
            "Configuração": name,
            "WR Banqueiros": f"{b_wr:.1f}%",
            "WR Estagiários": f"{i_wr:.1f}%",
            "WR Agressivo": f"{wr_a:.1f}%",
            "WR Sleeper": f"{wr_b:.1f}%",
            "WR Hedge": f"{wr_c:.1f}%",
            "Duração Média": f"{avg_r:.2f}",
            "Clímax (7ª R)": f"{climax_pct:.1f}%"
        })

    summary_df = pd.DataFrame(summary_rows)
    print("\n" + "=" * 100)
    print("                      MATRIZ COMPARATIVA FINAL DE GAME DESIGN")
    print("=" * 100)
    print(summary_df.to_string(index=False))
    print("=" * 100)


if __name__ == '__main__':
    run_experiment_suite(20000)
