# -*- coding: utf-8 -*-
"""
BTG Madagascar - Simulador de 7 Rodadas com Triangularidade & Bônus do Sleeper
=============================================================================
Novas Mecânicas:
1. Estrutura de 7 Rodadas (Primeiro a 4 Vitórias):
   - Dá espaço para a construção de confiança, blefes de longo prazo e reviravoltas.
2. Bônus de Performance / Reputação (Incentivo ao Sleeper):
   - Membros de comitês bem-sucedidos ganham 1 Token de Reputação (+2 para Banqueiros /
     capacidade de Alavancagem Oculta para Estagiários).
3. Triangularidade (Risco vs Recompensa):
   - Rush: Rápido, mas sem bônus e gera isolamento.
   - Sleeper: Alto risco no início (dá pontos aos Banqueiros), mas ganha letalidade crítica
     no late-game com alavancagem de reputação!
"""

import random
import time
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Tuple, Optional, Set
import numpy as np
import pandas as pd


class CardType(Enum):
    CO = 'Cobalto (+1 base)'
    VN = 'Baunilha (+2 base)'
    TI = 'Titanio (+3 base)'
    SF = 'Safira (+4 base)'
    WILD = 'Ouro Liquido (+4 base)'
    TOXIC = 'Ativo Toxico (-2)'

CARD_BASE_VALUES = {
    CardType.CO: 1,
    CardType.VN: 2,
    CardType.TI: 3,
    CardType.SF: 4,
    CardType.WILD: 4,
    CardType.TOXIC: -2
}

INITIAL_DECK = (
    [CardType.CO] * 20 +
    [CardType.VN] * 16 +
    [CardType.TI] * 8 +
    [CardType.SF] * 4 +
    [CardType.WILD] * 4 +
    [CardType.TOXIC] * 8
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


class Role(Enum):
    BANKER = 'Banqueiro'
    INTERN = 'Estagiario'

class InternProfile(Enum):
    A_AGGRESSIVE = 'A (Agressivo / Sabotagem Cedo)'
    B_SLEEPER = 'B (Infiltração Profunda / Sleeper)'
    C_HEDGE = 'C (Hedge / Retenção Econômica)'

@dataclass
class YieldContract:
    name: str
    tier: int
    committee_size: int
    cost_per_player: int
    target_value: int
    req_commodity: Optional[CardType] = None
    points_reward: int = 1  # Pontos que o contrato concede (1 ou 2 se for alavancado)

# Catálogo de 7 Tiers de Contratos
SEVEN_ROUND_CATALOG = {
    1: [
        YieldContract("Arbitragem Simples", 1, committee_size=2, cost_per_player=1, target_value=3),
        YieldContract("Exportacao de Baunilha", 1, committee_size=2, cost_per_player=1, target_value=3, req_commodity=CardType.VN),
    ],
    2: [
        YieldContract("Mineracao de Cobalto", 2, committee_size=2, cost_per_player=1, target_value=4, req_commodity=CardType.CO),
        YieldContract("Lote Agricola", 2, committee_size=2, cost_per_player=1, target_value=4, req_commodity=CardType.VN),
    ],
    3: [
        YieldContract("Sindicato de Titanio", 3, committee_size=3, cost_per_player=1, target_value=7, req_commodity=CardType.TI),
        YieldContract("Logistica Portuaria", 3, committee_size=3, cost_per_player=1, target_value=7, req_commodity=CardType.CO),
    ],
    4: [
        YieldContract("Refino Metalurgico", 4, committee_size=3, cost_per_player=1, target_value=8, req_commodity=CardType.TI),
        YieldContract("Consorcio Agro-Industrial", 4, committee_size=3, cost_per_player=1, target_value=8, req_commodity=CardType.VN),
    ],
    5: [
        YieldContract("Cofre de Gemas (Alavancado)", 5, committee_size=2, cost_per_player=2, target_value=12, req_commodity=CardType.SF, points_reward=1),
        YieldContract("Fundicao Estrategica", 5, committee_size=2, cost_per_player=2, target_value=11, req_commodity=CardType.TI, points_reward=1),
    ],
    6: [
        YieldContract("Consorcio Safira", 6, committee_size=3, cost_per_player=2, target_value=16, req_commodity=CardType.SF, points_reward=1),
        YieldContract("Complexo Greenfield", 6, committee_size=3, cost_per_player=2, target_value=15, req_commodity=CardType.TI, points_reward=1),
    ],
    7: [
        YieldContract("Holding Global BTG (Climax)", 7, committee_size=4, cost_per_player=2, target_value=24, req_commodity=CardType.SF, points_reward=1),
    ]
}

class DeckManager:
    __slots__ = ('draw_pile', 'discard_pile', 'rng')

    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.draw_pile = INITIAL_DECK.copy()
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


class PlayerAI:
    __slots__ = ('id', 'role', 'profile', 'rng', 'hand', 'suspicions', 'known_traitors', 'performance_tokens')

    def __init__(self, player_id: int, role: Role, profile: InternProfile, rng: random.Random):
        self.id = player_id
        self.role = role
        self.profile = profile
        self.rng = rng
        self.hand: List[ResourceCard] = []
        self.suspicions: Dict[int, float] = {i: 0.4 for i in range(5)}
        self.suspicions[self.id] = 0.0 if role == Role.BANKER else 1.0
        self.known_traitors: Set[int] = set()
        self.performance_tokens = 0

    def accumulate_holding_interest(self):
        """Quem fica fora acumula +1 de juro por carta positiva."""
        for card in self.hand:
            if card.card_type != CardType.TOXIC:
                card.interest_accumulated += 1

    def vote_on_proposal(self, proposer: int, committee: List[int], contract: YieldContract) -> bool:
        if self.role == Role.BANKER:
            for p in committee:
                if p in self.known_traitors or self.suspicions[p] >= 0.95:
                    return False
            if self.id in committee:
                others = [p for p in committee if p != self.id]
                max_sus = max([self.suspicions[p] for p in others], default=0.0)
                return max_sus < 0.65
            else:
                avg_sus = sum(self.suspicions[p] for p in committee) / len(committee)
                return avg_sus < 0.50
        else:
            if self.profile == InternProfile.A_AGGRESSIVE:
                return (self.id in committee) or (self.rng.random() < 0.35)
            elif self.profile == InternProfile.B_SLEEPER:
                # Sleeper aprova comitês para construir confiança e avançar o jogo
                if contract.tier <= 3:
                    return True
                return (self.id in committee) or (self.rng.random() < 0.40)
            elif self.profile == InternProfile.C_HEDGE:
                if self.id in committee:
                    return True
                return self.rng.random() < 0.20
        return True

    def choose_cards_to_submit(
        self,
        contract: YieldContract,
        round_num: int,
        must_provide_req: bool = False
    ) -> Tuple[List[ResourceCard], int]:
        cost = contract.cost_per_player
        should_sabotage = False

        if self.role == Role.INTERN:
            if self.profile == InternProfile.A_AGGRESSIVE:
                should_sabotage = True
            elif self.profile == InternProfile.B_SLEEPER:
                # Sleeper sabota no momento crítico (Tier 4 em diante ou quando tem tokens acumulados)
                should_sabotage = (round_num >= 4 or self.performance_tokens >= 2)
            elif self.profile == InternProfile.C_HEDGE:
                should_sabotage = (round_num >= 3 or self.rng.random() < 0.50)

        chosen: List[ResourceCard] = []
        temp_hand = self.hand.copy()
        extra_token_impact = 0

        if not should_sabotage:
            # Entrega Honesta: Banqueiro ou Sleeper camuflado
            if must_provide_req and contract.req_commodity is not None:
                req = contract.req_commodity
                matching = [c for c in temp_hand if c.card_type in (req, CardType.WILD)]
                if matching:
                    best_match = max(matching, key=lambda c: c.effective_value)
                    temp_hand.remove(best_match)
                    chosen.append(best_match)

            pos_cards = [c for c in temp_hand if c.card_type != CardType.TOXIC]
            pos_cards.sort(key=lambda c: -c.effective_value)

            while len(chosen) < cost and pos_cards:
                c = pos_cards.pop(0)
                temp_hand.remove(c)
                chosen.append(c)

            while len(chosen) < cost and temp_hand:
                c = temp_hand.pop(0)
                chosen.append(c)

            # Banqueiro gasta Tokens de Reputação (+2 cada) se necessário para garantir
            if self.role == Role.BANKER and self.performance_tokens > 0:
                # Gasta até 1 token para reforçar
                extra_token_impact = 2
                self.performance_tokens -= 1

            return chosen[:cost], extra_token_impact
        else:
            # Sabotagem:
            toxic_cards = [c for c in temp_hand if c.card_type == CardType.TOXIC]
            low_pos = [c for c in temp_hand if c.card_type != CardType.TOXIC]
            low_pos.sort(key=lambda c: c.effective_value)

            while len(chosen) < cost and toxic_cards:
                c = toxic_cards.pop(0)
                temp_hand.remove(c)
                chosen.append(c)

            while len(chosen) < cost and low_pos:
                c = low_pos.pop(0)
                temp_hand.remove(c)
                chosen.append(c)

            while len(chosen) < cost and temp_hand:
                c = temp_hand.pop(0)
                chosen.append(c)

            # Alavancagem Oculta do Sleeper:
            # Se o Estagiário tem Tokens de Performance acumulados da cooperação, ele pode gastá-los
            # para DOBRAR o dano do Ativo Tóxico (de -2 para -4 ou -6!)
            if self.performance_tokens > 0:
                spent_tokens = self.performance_tokens
                self.performance_tokens = 0
                extra_token_impact = -(spent_tokens * 2)  # Dano extra oculto!

            return chosen[:cost], extra_token_impact


def evaluate_7_round_contract(
    submitted_cards: List[ResourceCard],
    extra_impact: int,
    contract: YieldContract
) -> Tuple[bool, int, bool]:
    total_val = sum(c.effective_value for c in submitted_cards) + extra_impact
    has_req = True

    if contract.req_commodity is not None:
        has_direct = any(c.card_type == contract.req_commodity for c in submitted_cards)
        has_wild = any(c.card_type == CardType.WILD for c in submitted_cards)
        has_req = (has_direct or has_wild)

    is_success = (total_val >= contract.target_value) and has_req
    return is_success, total_val, has_req


def simulate_7_round_game(
    game_idx: int,
    profile: InternProfile,
    seed: Optional[int] = None
) -> Dict:
    rng = random.Random(seed if seed is not None else (int(time.time() * 1000) ^ game_idx))
    deck = DeckManager(seed=rng.randint(0, 10**9))

    roles = [Role.BANKER] * 3 + [Role.INTERN] * 2
    rng.shuffle(roles)
    players = [PlayerAI(i, roles[i], profile, rng) for i in range(5)]

    for p in players:
        p.hand = deck.draw(3)

    banker_score = 0
    intern_score = 0
    curr_chair = 0
    round_count = 0
    ops = [rng.choice(SEVEN_ROUND_CATALOG[t]) for t in range(1, 8)]

    for r_idx, contract in enumerate(ops):
        round_count += 1

        for p in players:
            p.hand.extend(deck.draw(1))

        consecutive_vetoes = 0
        approved_committee = None
        forced_execution = False

        while consecutive_vetoes < 3 and approved_committee is None:
            chair_player = players[curr_chair]
            if chair_player.role == Role.BANKER:
                cands = [p.id for p in players if p.id != chair_player.id and p.id not in chair_player.known_traitors]
                cands.sort(key=lambda pid: chair_player.suspicions[pid])
                if len(cands) < contract.committee_size - 1:
                    cands = [p.id for p in players if p.id != chair_player.id]
                    cands.sort(key=lambda pid: chair_player.suspicions[pid])
                comm = [chair_player.id] + cands[:contract.committee_size - 1]
            else:
                others = [p.id for p in players if p.id != chair_player.id]
                rng.shuffle(others)
                comm = [chair_player.id] + others[:contract.committee_size - 1]

            votes = [p.vote_on_proposal(curr_chair, comm, contract) for p in players]
            if sum(votes) >= 3:
                approved_committee = comm
            else:
                consecutive_vetoes += 1
                curr_chair = (curr_chair + 1) % 5

        if approved_committee is None:
            forced_execution = True
            chair_player = players[curr_chair]
            others = [p.id for p in players if p.id != chair_player.id]
            approved_committee = [chair_player.id] + others[:contract.committee_size - 1]

        # Juros para quem ficou fora
        for p in players:
            if p.id not in approved_committee:
                p.accumulate_holding_interest()

        comm_objs = [players[pid] for pid in approved_committee]

        submitted_all: List[ResourceCard] = []
        total_token_impact = 0

        for idx, p in enumerate(comm_objs):
            must_req = (idx == 0) and (contract.req_commodity is not None)
            sub, impact = p.choose_cards_to_submit(contract, round_count, must_provide_req=must_req)
            for c in sub:
                if c in p.hand:
                    p.hand.remove(c)
            submitted_all.extend(sub)
            total_token_impact += impact

        deck.discard(submitted_all)
        is_success, total_val, has_req = evaluate_7_round_contract(submitted_all, total_token_impact, contract)

        if is_success:
            banker_score += contract.points_reward
            # BÔNUS DE PERFORMANCE: Cada membro do comitê ganha +1 Token de Reputação!
            for p in comm_objs:
                p.performance_tokens += 1

            for bp in players:
                if bp.role == Role.BANKER:
                    for cid in approved_committee:
                        if cid != bp.id and cid not in bp.known_traitors:
                            bp.suspicions[cid] = max(0.05, bp.suspicions[cid] - 0.20)
        else:
            intern_score += contract.points_reward
            if forced_execution:
                return {
                    "winner": Role.INTERN.value,
                    "cause": "Insolvencia no 3º Veto",
                    "rounds": round_count,
                    "b_score": banker_score,
                    "i_score": intern_score,
                    "profile": profile.value
                }

            has_toxic = any(c.card_type == CardType.TOXIC for c in submitted_all)
            delta = 0.45 if has_toxic else 0.25
            if len(approved_committee) >= 3:
                delta *= 0.70

            for bp in players:
                if bp.role == Role.BANKER:
                    for cid in approved_committee:
                        if cid != bp.id:
                            bp.suspicions[cid] = min(0.95, bp.suspicions[cid] + delta)

        # Primeiro a 4 Vitórias vence!
        if banker_score >= 4:
            return {
                "winner": Role.BANKER.value,
                "cause": "4 Contratos Concluidos",
                "rounds": round_count,
                "b_score": banker_score,
                "i_score": intern_score,
                "profile": profile.value
            }
        elif intern_score >= 4:
            return {
                "winner": Role.INTERN.value,
                "cause": "4 Contratos Reprovados",
                "rounds": round_count,
                "b_score": banker_score,
                "i_score": intern_score,
                "profile": profile.value
            }

        curr_chair = (curr_chair + 1) % 5

    w = Role.BANKER.value if banker_score > intern_score else Role.INTERN.value
    return {
        "winner": w,
        "cause": "Fim das 7 Rodadas",
        "rounds": 7,
        "b_score": banker_score,
        "i_score": intern_score,
        "profile": profile.value
    }


def run_7_rounds_benchmark(n=100000):
    print("=" * 80)
    print(" SIMULADOR MONTE CARLO: ESTRUTURA DE 7 RODADAS & TRIANGULARIDADE (100.000 JOGOS) ")
    print("=" * 80)
    t0 = time.time()
    results = []
    profiles = [InternProfile.A_AGGRESSIVE, InternProfile.B_SLEEPER, InternProfile.C_HEDGE]

    for i in range(n):
        prof = random.choice(profiles)
        res = simulate_7_round_game(i, prof, seed=990000 + i)
        results.append(res)

        if (i + 1) % 10000 == 0:
            print(f"   [7 Rodadas & Triangularidade] {i + 1:6,d} / {n:,} ({(i+1)/n*100:5.1f}%) | Tempo: {time.time() - t0:4.1f}s")
            sys.stdout.flush()

    df = pd.DataFrame(results)
    b_wins = (df["winner"] == Role.BANKER.value).sum()
    i_wins = (df["winner"] == Role.INTERN.value).sum()

    print("\n" + "=" * 80)
    print("             RESULTADOS DO MODELO DE 7 RODADAS COM TRIANGULARIDADE")
    print("=" * 80)
    print(f"\n1. WIN RATE GLOBAL (Meta de Game Design: 51% a 54% pró-Banqueiros)")
    print(f"   - Banqueiros : {(b_wins/n)*100:6.2f}% ({b_wins:,} vitórias)")
    print(f"   - Estagiários: {(i_wins/n)*100:6.2f}% ({i_wins:,} vitórias)")
    print(f"   - Duração Média: {df['rounds'].mean():.2f} ± {df['rounds'].std():.2f} rodadas")

    print(f"\n2. MATRIZ DE PLACARES FINAIS (Primeiro a 4 Pontos)")
    print("-" * 60)
    df["score"] = df["b_score"].astype(str) + " x " + df["i_score"].astype(str)
    score_counts = df["score"].value_counts()
    for sc, cnt in score_counts.items():
        tag = "[Clímax da 7ª Rodada]" if "4 x 3" in sc or "3 x 4" in sc else ""
        print(f"   • {sc:<15}: {cnt:>8,d} ({(cnt/n)*100:5.2f}%) {tag}")

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

if __name__ == '__main__':
    run_7_rounds_benchmark(100000)
