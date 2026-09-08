# -*- coding: utf-8 -*-
"""
BTG Madagascar - Modelo de Jogador, Carteira, Tokens e Tomada de Decisão
"""

import random
import itertools
import numpy as np
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass

from .constants import CardType, Role, InternProfile, BankerProfile, ContractSpec
from .deck import ResourceCard


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
    __slots__ = (
        'id', 'role', 'profile', 'is_active_saboteur', 'rng',
        'hand', 'interest_tokens', 'suspicions', 'known_traitors',
        'credits_accumulated', 'public_known_cards', 'consecutive_rounds'
    )

    def __init__(
        self,
        player_id: int,
        role: Role,
        profile: object,
        rng: random.Random,
        is_active_saboteur: bool = False
    ):
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
        self.credits_accumulated: int = 0
        self.public_known_cards: List[CardType] = []
        self.consecutive_rounds: int = 0

    def accumulate_holding_interest(self):
        """Ficar no banco rende +1 Token de Juros (máx 3)."""
        if self.interest_tokens < 3:
            self.interest_tokens += 1

    def claim_success_credit(self):
        """Créditos de sucesso institucionais.
        A cada 2 créditos acumulados (2 missões bem-sucedidas como membro do comitê),
        o operador pode adquirir 1 ativo especial:
          - Banqueiro: Ouro Líquido (Wild +4) — recurso premium para missões tardias
          - Estagiário: Ativo Tóxico (-4) — arma de sabotagem disfarcçada como bônus de desempenho
        Isso incentiva o cumprimento de missões para disfarce (Estagiário acumula Tóxicos
        participando 'honestamente') e recompensa coord. leal dos Banqueiros com Wild cards.
        """
        self.credits_accumulated += 1
        if self.credits_accumulated >= 2:  # 2 créditos = 1 ativo especial
            self.credits_accumulated -= 2
            if self.role == Role.BANKER:
                self.hand.append(ResourceCard(CardType.WILD))
            else:
                self.hand.append(ResourceCard(CardType.TOXIC))

    def make_public_declaration(self, contract: ContractSpec, round_num: int) -> PlayerDeclaration:
        """Declaração pública de aptidão, insumo e oferta de tokens para o comitê."""
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
            if self.profile == BankerProfile.CONSERVATIVE:
                # Conservador: se liquidez estiver no limite, prefere banco para acumular rendimento
                is_dry = (best_total_val <= expected_quota) and (round_num >= 2) and (not has_req_real)
            elif self.profile == BankerProfile.PRAGMATIC:
                # Pragmático: topa ir para o comitê mesmo com liquidez justa
                is_dry = (best_total_val < expected_quota - 1) and (round_num >= 2) and (not has_req_real)
            elif self.profile == BankerProfile.STRATEGIST:
                # Estrategista: se já jogou 2 rodadas seguidas, prefere banco para girar a carteira
                is_dry = is_dry or (self.consecutive_rounds >= 2 and round_num <= 4)

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
            elif self.profile == InternProfile.D_OPPORTUNIST:
                claims = has_req_real or (contract.req_commodity is not None and round_num >= 3 and self.rng.random() < 0.50)
                req_v = req_val if has_req_real else max(3, int(expected_quota))
                offered_str = f"{contract.req_commodity.name.split(' ')[0]}(~{req_v}pts)" if contract.req_commodity else f"Liquidez Adaptável(~{int(expected_quota)}pts)"
                return PlayerDeclaration(self.id, claims, max(best_total_val, int(expected_quota)), req_v, tokens_to_offer, prefers_bench=False, offered_desc=offered_str)
            elif self.profile == InternProfile.E_TECHNICIAN:
                claims = has_req_real or (contract.req_commodity is not None and round_num >= 3 and self.rng.random() < 0.50)
                req_v = req_val if has_req_real else (max(3, int(expected_quota)) if claims else 0)
                offered_str = f"{contract.req_commodity.name.split(' ')[0]}({req_v}pts)" if claims else f"Liquidez Calculada(~{int(expected_quota)}pts)"
                should_bench = is_dry and round_num <= 2
                return PlayerDeclaration(self.id, claims, max(best_total_val, int(expected_quota)), req_v, tokens_to_offer, prefers_bench=should_bench, offered_desc=offered_str)

    def vote_on_proposal(self, proposer: int, committee: List[int], contract: ContractSpec, round_num: int) -> bool:
        """Votação de governança corporativa diferenciada por perfil."""
        if self.role == Role.BANKER:
            # 1. Rejeição imediata se o propositor é um traidor já comprovado
            if proposer in self.known_traitors:
                return False

            if self.profile == BankerProfile.CONSERVATIVE:
                prop_threshold = 0.45
                mem_threshold = 0.60
                comm_with_self_limit = 0.52
                avg_comm_limit = 0.45
            elif self.profile == BankerProfile.PRAGMATIC:
                prop_threshold = 0.55
                mem_threshold = 0.75
                comm_with_self_limit = 0.68
                avg_comm_limit = 0.55
            elif self.profile == BankerProfile.STRATEGIST:
                prop_threshold = 0.50
                mem_threshold = 0.68
                comm_with_self_limit = 0.58
                avg_comm_limit = 0.48
            else:  # BALANCED ou fallback
                prop_threshold = 0.50
                mem_threshold = 0.70
                comm_with_self_limit = 0.60
                avg_comm_limit = 0.50

            if proposer != self.id and self.suspicions[proposer] >= prop_threshold:
                return False

            for p in committee:
                if p in self.known_traitors or self.suspicions[p] >= mem_threshold:
                    return False
            if self.id in committee:
                others = [p for p in committee if p != self.id]
                max_sus = max([self.suspicions[p] for p in others], default=0.0)
                return max_sus < comm_with_self_limit
            else:
                avg_sus = sum(self.suspicions[p] for p in committee) / len(committee)
                return avg_sus < avg_comm_limit
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

    def plan_honest_contribution(
        self,
        contract: ContractSpec,
        round_num: int,
        is_responsible_for_req: bool,
        quota_needed: float,
        is_match_point: bool = False
    ) -> Tuple[List[ResourceCard], int, int]:
        """Aporte leal e otimizado de recursos."""
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

            # Estrategista poupa tokens em rodadas iniciais se cartas cobrirem ou ficarem próximas
            if self.role == Role.BANKER and self.profile == BankerProfile.STRATEGIST and round_num <= 3 and not is_match_point and contract.tier < 6:
                if base_v >= quota_needed - 1 and tokens_to_use > 1:
                    tokens_to_use = 1

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
        """Aporte de sabotagem tática (Ativo Tóxico ou Troca de Insumo na Cota)."""
        cost = contract.cost_per_player
        toxic_cards = [c for c in self.hand if c.card_type == CardType.TOXIC]
        pos_cards = [c for c in self.hand if c.card_type != CardType.TOXIC]
        low_pos = sorted(pos_cards, key=lambda c: c.base_value)

        chosen: List[ResourceCard] = []


        if toxic_cards and (contract.committee_size >= 3 or round_num >= 3):
            chosen.append(toxic_cards.pop(0))
            while len(chosen) < cost and low_pos:
                chosen.append(low_pos.pop(0))
            remaining_hand = [c for c in self.hand if c not in chosen]
            while len(chosen) < cost and remaining_hand:
                chosen.append(remaining_hand.pop(0))
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
        remaining_hand = [c for c in self.hand if c not in chosen]
        while len(chosen) < cost and remaining_hand:
            chosen.append(remaining_hand.pop(0))

        return chosen[:cost], 0
