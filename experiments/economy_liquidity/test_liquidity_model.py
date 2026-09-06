# -*- coding: utf-8 -*-
"""
BTG Madagascar - Simulador do Modelo de Poder de Liquidez & Ativos Tóxicos
========================================================================
Mecânica:
- Baralho (60 Cartas):
    * 20 Cobalto (+1)
    * 16 Baunilha (+2)
    * 8 Titânio (+3)
    * 4 Safira (+5)
    * 4 Ouro Líquido (+5 / Coringa)
    * 8 Ativo Tóxico (-2)
- Contratos por Tiers exigem:
    * Valor Financeiro Líquido Mínimo (Soma dos valores das cartas >= Meta)
    * Pelo menos 1 insumo temático obrigatório (ex: 1 Titânio, 1 Safira)
- Sabotagem com Dúvida Plausível:
    * Jogar Ativo Tóxico (-2) ou carta de valor baixo (+1 Cobalto)
    * O traidor pode argumentar: "Gente, eu dei o meu melhor, mas só tinha carta fraca na mão!"
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


class Card(Enum):
    CO = 'Cobalto (+1)'
    VN = 'Baunilha (+2)'
    TI = 'Titanio (+3)'
    SF = 'Safira (+5)'
    WILD = 'Coringa (+5)'
    TOXIC = 'Ativo Toxico (-2)'

CARD_VALUES = {
    Card.CO: 1,
    Card.VN: 2,
    Card.TI: 3,
    Card.SF: 5,
    Card.WILD: 5,
    Card.TOXIC: -2
}

INITIAL_DECK = (
    [Card.CO] * 20 +
    [Card.VN] * 16 +
    [Card.TI] * 8 +
    [Card.SF] * 4 +
    [Card.WILD] * 4 +
    [Card.TOXIC] * 8
)

class Role(Enum):
    BANKER = 'Banqueiro'
    INTERN = 'Estagiario'

class InternProfile(Enum):
    A_AGGRESSIVE = 'A (Agressivo / Fraude Imediata)'
    B_SLEEPER = 'B (Late-Game Sleeper / Camuflado)'
    C_HEDGE = 'C (Hedge / Retencao Estrategica)'

@dataclass
class LiquidityContract:
    name: str
    tier: int
    committee_size: int
    cost_per_player: int
    target_value: int
    req_commodity: Optional[Card] = None  # Insumo obrigatório específico

    @property
    def total_cards(self) -> int:
        return self.committee_size * self.cost_per_player

LIQUIDITY_CATALOG = {
    1: [
        LiquidityContract("Arbitragem Rapida", 1, committee_size=2, cost_per_player=1, target_value=3),
        LiquidityContract("Exportacao de Baunilha", 1, committee_size=2, cost_per_player=1, target_value=3, req_commodity=Card.VN),
        LiquidityContract("Mineracao de Cobalto", 1, committee_size=2, cost_per_player=1, target_value=2, req_commodity=Card.CO),
    ],
    2: [
        LiquidityContract("Sindicato Agricola", 2, committee_size=3, cost_per_player=1, target_value=5, req_commodity=Card.VN),
        LiquidityContract("Fundicao de Titanio", 2, committee_size=3, cost_per_player=1, target_value=6, req_commodity=Card.TI),
        LiquidityContract("Logistica Portuaria", 2, committee_size=3, cost_per_player=1, target_value=5, req_commodity=Card.CO),
    ],
    3: [
        LiquidityContract("Refino Metalurgico", 3, committee_size=2, cost_per_player=2, target_value=8, req_commodity=Card.TI),
        LiquidityContract("Cofre de Gemas", 3, committee_size=2, cost_per_player=2, target_value=9, req_commodity=Card.SF),
        LiquidityContract("Lote Agro-Industrial", 3, committee_size=2, cost_per_player=2, target_value=7, req_commodity=Card.VN),
    ],
    4: [
        LiquidityContract("Consorcio Safira", 4, committee_size=3, cost_per_player=2, target_value=13, req_commodity=Card.SF),
        LiquidityContract("Complexo Greenfield", 4, committee_size=3, cost_per_player=2, target_value=12, req_commodity=Card.TI),
    ],
    5: [
        LiquidityContract("Holding Global BTG", 5, committee_size=3, cost_per_player=2, target_value=15, req_commodity=Card.SF),
    ]
}

class DeckManager:
    __slots__ = ('draw_pile', 'discard_pile', 'rng')

    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.draw_pile = INITIAL_DECK.copy()
        self.rng.shuffle(self.draw_pile)
        self.discard_pile: List[Card] = []

    def draw(self, n: int = 1) -> List[Card]:
        drawn = []
        for _ in range(n):
            if not self.draw_pile:
                if not self.discard_pile:
                    drawn.append(Card.CO)
                    continue
                self.draw_pile = self.discard_pile.copy()
                self.discard_pile = []
                self.rng.shuffle(self.draw_pile)
            drawn.append(self.draw_pile.pop())
        return drawn

    def discard(self, cards: List[Card]):
        self.discard_pile.extend(cards)


class PlayerAI:
    __slots__ = ('id', 'role', 'profile', 'rng', 'hand', 'suspicions', 'known_traitors', 'known_innocents')

    def __init__(self, player_id: int, role: Role, profile: InternProfile, rng: random.Random):
        self.id = player_id
        self.role = role
        self.profile = profile
        self.rng = rng
        self.hand: List[Card] = []
        self.suspicions: Dict[int, float] = {i: 0.4 for i in range(5)}
        self.suspicions[self.id] = 0.0 if role == Role.BANKER else 1.0
        self.known_traitors: Set[int] = set()
        self.known_innocents: Set[int] = {self.id} if role == Role.BANKER else set()

    def apply_hold_yield(self) -> bool:
        """Hold: 2 cartas iguais de commodities válidas viram 1 Coringa (+5)."""
        counts = Counter([c for c in self.hand if c not in (Card.WILD, Card.TOXIC)])
        for card, count in counts.items():
            if count >= 2:
                self.hand.remove(card)
                self.hand.remove(card)
                self.hand.append(Card.WILD)
                return True
        return False

    def vote_on_proposal(self, proposer: int, committee: List[int], contract: LiquidityContract) -> bool:
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
                return (self.id in committee) or (self.rng.random() < 0.40)
            elif self.profile == InternProfile.B_SLEEPER:
                if contract.tier <= 2:
                    return True
                return (self.id in committee) or (self.rng.random() < 0.35)
            elif self.profile == InternProfile.C_HEDGE:
                if self.id in committee:
                    return True
                return self.rng.random() < 0.20
        return True

    def choose_cards_to_submit(
        self,
        contract: LiquidityContract,
        round_num: int,
        must_provide_req: bool = False
    ) -> List[Card]:
        cost = contract.cost_per_player
        should_sabotage = False

        if self.role == Role.INTERN:
            if self.profile == InternProfile.A_AGGRESSIVE:
                should_sabotage = True
            elif self.profile == InternProfile.B_SLEEPER:
                should_sabotage = (round_num >= 3)
            elif self.profile == InternProfile.C_HEDGE:
                should_sabotage = (round_num >= 3 or self.rng.random() < 0.60)

        chosen: List[Card] = []
        temp_hand = self.hand.copy()

        if not should_sabotage:
            # Banqueiro / Estagiário Camuflado: Tenta maximizar o valor e atender insumo
            # 1. Se precisa do insumo obrigatório e tem:
            if must_provide_req and contract.req_commodity is not None:
                req = contract.req_commodity
                if req in temp_hand:
                    temp_hand.remove(req)
                    chosen.append(req)
                elif Card.WILD in temp_hand:
                    temp_hand.remove(Card.WILD)
                    chosen.append(Card.WILD)

            # 2. Escolhe as cartas de MAIOR valor positivo disponível
            pos_cards = [c for c in temp_hand if c != Card.TOXIC]
            pos_cards.sort(key=lambda c: -CARD_VALUES[c])

            while len(chosen) < cost and pos_cards:
                c = pos_cards.pop(0)
                temp_hand.remove(c)
                chosen.append(c)

            # 3. Se a mão só tinha Ativo Tóxico e faltou carta, é obrigado a jogar
            while len(chosen) < cost and temp_hand:
                c = temp_hand.pop(0)
                chosen.append(c)

            return chosen[:cost]
        else:
            # Sabotagem com Dúvida Plausível:
            # Prioriza jogar Ativo Tóxico (-2) ou cartas de baixo valor (+1 Cobalto)
            toxic_cards = [c for c in temp_hand if c == Card.TOXIC]
            low_pos = [c for c in temp_hand if c == Card.CO]

            # Joga o Ativo Tóxico se tiver
            while len(chosen) < cost and toxic_cards:
                c = toxic_cards.pop(0)
                temp_hand.remove(c)
                chosen.append(c)

            # Joga Cobalto fraco
            while len(chosen) < cost and low_pos:
                c = low_pos.pop(0)
                temp_hand.remove(c)
                chosen.append(c)

            # Completa com o que sobrou de menor valor
            temp_hand.sort(key=lambda c: CARD_VALUES[c])
            while len(chosen) < cost and temp_hand:
                c = temp_hand.pop(0)
                chosen.append(c)

            return chosen[:cost]


def evaluate_contract_outcome(submitted_cards: List[Card], contract: LiquidityContract) -> Tuple[bool, int, bool]:
    """
    Retorna:
    - is_success: se atingiu o valor e o insumo obrigatório
    - total_value: valor líquido total entregue
    - has_required_commodity: se o insumo temático estava presente
    """
    total_val = sum(CARD_VALUES[c] for c in submitted_cards)
    has_req = True

    if contract.req_commodity is not None:
        has_direct = (contract.req_commodity in submitted_cards)
        has_wild = (Card.WILD in submitted_cards)
        has_req = (has_direct or has_wild)

    is_success = (total_val >= contract.target_value) and has_req
    return is_success, total_val, has_req


def simulate_single_liquidity_game(
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
    total_vetoes = 0
    ops = [rng.choice(LIQUIDITY_CATALOG[t]) for t in range(1, 6)]

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
                total_vetoes += 1
                curr_chair = (curr_chair + 1) % 5

        if approved_committee is None:
            forced_execution = True
            chair_player = players[curr_chair]
            others = [p.id for p in players if p.id != chair_player.id]
            approved_committee = [chair_player.id] + others[:contract.committee_size - 1]

        # Hold fora do comitê
        for p in players:
            if p.id not in approved_committee:
                p.apply_hold_yield()

        comm_objs = [players[pid] for pid in approved_committee]

        # Envio de cartas
        submitted_all: List[Card] = []
        for idx, p in enumerate(comm_objs):
            # O primeiro membro tenta fornecer o insumo obrigatório se houver
            must_req = (idx == 0) and (contract.req_commodity is not None)
            sub = p.choose_cards_to_submit(contract, round_count, must_provide_req=must_req)
            for c in sub:
                if c in p.hand:
                    p.hand.remove(c)
            submitted_all.extend(sub)

        deck.discard(submitted_all)

        # Auditoria de Liquidez e Conformidade
        is_success, total_val, has_req = evaluate_contract_outcome(submitted_all, contract)

        if is_success:
            banker_score += 1
            for bp in players:
                if bp.role == Role.BANKER:
                    for cid in approved_committee:
                        if cid != bp.id and cid not in bp.known_traitors:
                            bp.suspicions[cid] = max(0.05, bp.suspicions[cid] - 0.20)
        else:
            intern_score += 1
            if forced_execution:
                return {
                    "winner": Role.INTERN.value,
                    "cause": "Insolvencia no 3º Veto",
                    "rounds": round_count,
                    "b_score": banker_score,
                    "i_score": intern_score,
                    "profile": profile.value
                }

            # Atualização de Suspeita com Dúvida Plausível:
            # Se apareceu Ativo Tóxico (-2): a suspeita sobre todos os membros sobe fortemente!
            toxic_count = submitted_all.count(Card.TOXIC)
            if toxic_count > 0:
                delta = 0.50 if len(approved_committee) == 2 else 0.35
            else:
                delta = 0.30 if len(approved_committee) == 2 else 0.20

            for bp in players:
                if bp.role == Role.BANKER:
                    for cid in approved_committee:
                        if cid != bp.id:
                            bp.suspicions[cid] = min(0.95, bp.suspicions[cid] + delta)

        if banker_score >= 3:
            return {
                "winner": Role.BANKER.value,
                "cause": "3 Contratos Concluidos",
                "rounds": round_count,
                "b_score": banker_score,
                "i_score": intern_score,
                "profile": profile.value
            }
        elif intern_score >= 3:
            return {
                "winner": Role.INTERN.value,
                "cause": "3 Contratos Reprovados",
                "rounds": round_count,
                "b_score": banker_score,
                "i_score": intern_score,
                "profile": profile.value
            }

        curr_chair = (curr_chair + 1) % 5

    w = Role.BANKER.value if banker_score > intern_score else Role.INTERN.value
    return {
        "winner": w,
        "cause": "Fim de Rodadas",
        "rounds": 5,
        "b_score": banker_score,
        "i_score": intern_score,
        "profile": profile.value
    }


def run_liquidity_monte_carlo(n=100000):
    print("=" * 80)
    print(" SIMULADOR MONTE CARLO - MODELO DE PODER DE LIQUIDEZ & ATIVOS TÓXICOS ")
    print("=" * 80)
    t0 = time.time()
    results = []
    profiles = [InternProfile.A_AGGRESSIVE, InternProfile.B_SLEEPER, InternProfile.C_HEDGE]

    for i in range(n):
        prof = random.choice(profiles)
        res = simulate_single_liquidity_game(i, prof, seed=900000 + i)
        results.append(res)

        if (i + 1) % 10000 == 0:
            print(f"   [Liquidez & Ativos Toxicos] {i + 1:6,d} / {n:,} ({(i+1)/n*100:5.1f}%) | Tempo: {time.time() - t0:4.1f}s")
            sys.stdout.flush()

    df = pd.DataFrame(results)
    b_wins = (df["winner"] == Role.BANKER.value).sum()
    i_wins = (df["winner"] == Role.INTERN.value).sum()

    print("\n" + "=" * 80)
    print("                RESULTADOS DO MODELO DE PODER DE LIQUIDEZ")
    print("=" * 80)
    print(f"\n1. WIN RATE GLOBAL (Meta: 51% a 54% pró-Banqueiros)")
    print(f"   - Banqueiros : {(b_wins/n)*100:6.2f}% ({b_wins:,} vitórias)")
    print(f"   - Estagiários: {(i_wins/n)*100:6.2f}% ({i_wins:,} vitórias)")
    print(f"   - Duração Média: {df['rounds'].mean():.2f} ± {df['rounds'].std():.2f} rodadas")

    print(f"\n2. MATRIZ DE PLACARES FINAIS")
    print("-" * 60)
    df["score"] = df["b_score"].astype(str) + " x " + df["i_score"].astype(str)
    score_counts = df["score"].value_counts()
    for sc, cnt in score_counts.items():
        print(f"   • {sc:<15}: {cnt:>8,d} ({(cnt/n)*100:5.2f}%)")

    print(f"\n3. PERFORMANCE POR PERFIL DE IA")
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
    run_liquidity_monte_carlo(100000)
