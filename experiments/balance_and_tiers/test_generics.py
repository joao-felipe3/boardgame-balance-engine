# -*- coding: utf-8 -*-
"""
Script de Análise Comparativa: Impacto de Cartas Genéricas / Caixa
Com prints de progresso em tempo real a cada 5.000 iterações.
"""
import random
import time
import sys
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Tuple, Optional
import pandas as pd


class Card(Enum):
    CO = 'Cobalto'
    VN = 'Baunilha'
    TI = 'Titanio'
    SF = 'Safira'
    WILD = 'Coringa'
    CASH = 'Caixa/Generico'

CARD_RARITY = {
    Card.CASH: 1,
    Card.CO: 2,
    Card.VN: 3,
    Card.TI: 4,
    Card.SF: 5,
    Card.WILD: 6
}

class Role(Enum):
    BANKER = 'Banqueiro'
    INTERN = 'Estagiario'

class InternProfile(Enum):
    A_AGGRESSIVE = 'A (Agressivo)'
    B_SLEEPER = 'B (Late-Game Sleeper)'
    C_HEDGE = 'C (Hedge Economico)'
    RANDOM = 'Misto / Aleatorio'

@dataclass
class OperationTemplate:
    name: str
    committee_size: int
    cost_per_player: int
    req_co: int = 0
    req_ti: int = 0
    req_vn: int = 0
    req_sf_or_wild: int = 0
    req_wild: int = 0
    sabotages_to_fail: int = 1

OPERATION_POOL: List[OperationTemplate] = [
    OperationTemplate("Arbitragem Rápida", committee_size=2, cost_per_player=1, sabotages_to_fail=1),
    OperationTemplate("Exportação de Baunilha", committee_size=2, cost_per_player=1, req_vn=1, sabotages_to_fail=1),
    OperationTemplate("Mineração de Cobalto", committee_size=2, cost_per_player=1, req_co=1, sabotages_to_fail=1),
    OperationTemplate("Sindicato Agrícola", committee_size=3, cost_per_player=1, req_vn=1, sabotages_to_fail=1),
    OperationTemplate("Fundição de Titânio", committee_size=3, cost_per_player=1, req_ti=1, sabotages_to_fail=1),
    OperationTemplate("Infraestrutura Portuária", committee_size=3, cost_per_player=1, req_co=1, req_ti=1, sabotages_to_fail=1),
    OperationTemplate("Refino Metalúrgico", committee_size=2, cost_per_player=2, req_co=1, req_ti=1, sabotages_to_fail=1),
    OperationTemplate("Cofre de Gemas", committee_size=2, cost_per_player=2, req_sf_or_wild=1, sabotages_to_fail=1),
    OperationTemplate("Consórcio Safira", committee_size=3, cost_per_player=2, req_sf_or_wild=2, sabotages_to_fail=2),
    OperationTemplate("Holding Global BTG", committee_size=3, cost_per_player=2, req_co=1, req_ti=1, req_vn=1, req_sf_or_wild=1, sabotages_to_fail=1),
]

class DeckManager:
    __slots__ = ('draw_pile', 'discard_pile', 'rng', 'initial_deck')

    def __init__(self, initial_deck: List[Card], seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.initial_deck = initial_deck
        self.draw_pile: List[Card] = []
        self.discard_pile: List[Card] = []
        self.reset()

    def reset(self):
        self.draw_pile = self.initial_deck.copy()
        self.rng.shuffle(self.draw_pile)
        self.discard_pile = []

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
    __slots__ = ('id', 'role', 'profile', 'rng', 'hand', 'suspicions')

    def __init__(self, player_id: int, role: Role, profile: InternProfile, rng: random.Random):
        self.id = player_id
        self.role = role
        self.profile = profile
        self.rng = rng
        self.hand: List[Card] = []
        self.suspicions: Dict[int, float] = {i: 0.4 for i in range(5)}
        self.suspicions[self.id] = 0.0 if role == Role.BANKER else 1.0

    def apply_hold_yield(self):
        counts = Counter(self.hand)
        for card, count in counts.items():
            if card == Card.WILD:
                continue
            if count >= 2:
                if self.rng.random() < 0.30:
                    self.hand.remove(card)
                    self.hand.remove(card)
                    self.hand.append(Card.WILD)
                    break

    def vote_on_proposal(self, proposer: int, committee: List[int], op_spec: OperationTemplate) -> bool:
        if self.role == Role.BANKER:
            if self.id in committee:
                others = [p for p in committee if p != self.id]
                max_sus = max([self.suspicions[p] for p in others], default=0.0)
                return max_sus < 0.65
            else:
                avg_sus = sum(self.suspicions[p] for p in committee) / len(committee)
                return avg_sus < 0.50
        else:
            if self.profile == InternProfile.A_AGGRESSIVE:
                return (self.id in committee) or (self.rng.random() < 0.50)
            elif self.profile == InternProfile.B_SLEEPER:
                return (self.id in committee) or (self.rng.random() < 0.40)
            elif self.profile == InternProfile.C_HEDGE:
                if self.id in committee:
                    return True
                return self.rng.random() < 0.25
        return True

    def decide_sabotage(self, op_spec: OperationTemplate, round_num: int) -> bool:
        if self.role == Role.BANKER:
            return False
        if self.profile == InternProfile.A_AGGRESSIVE:
            return True
        elif self.profile == InternProfile.B_SLEEPER:
            return round_num >= 3
        elif self.profile == InternProfile.C_HEDGE:
            if round_num >= 3:
                return True
            return self.rng.random() < 0.60
        return True

def solve_payment(committee_players: List[PlayerAI], op_spec: OperationTemplate) -> Tuple[bool, Dict[int, List[Card]]]:
    c_per_p = op_spec.cost_per_player
    for p in committee_players:
        if len(p.hand) < c_per_p:
            return False, {}

    available_map: Dict[int, List[Card]] = {}
    for p in committee_players:
        if p.role == Role.BANKER:
            avail = p.hand.copy()
        else:
            if p.profile == InternProfile.C_HEDGE:
                avail = [c for c in p.hand if c not in (Card.SF, Card.WILD)]
                if len(avail) < c_per_p:
                    avail = p.hand.copy()
            else:
                avail = p.hand.copy()
        available_map[p.id] = avail

    from itertools import combinations, product

    def get_combos(p_id: int):
        cards = available_map[p_id]
        combos = list(set(combinations(range(len(cards)), c_per_p)))
        return [[cards[idx] for idx in c] for c in combos]

    player_combos = [get_combos(p.id) for p in committee_players]

    for prod in product(*player_combos):
        combined = [c for c_list in prod for c in c_list]
        counts = Counter(combined)

        if counts[Card.WILD] < op_spec.req_wild:
            continue
        counts[Card.WILD] -= op_spec.req_wild

        req_sf_w = op_spec.req_sf_or_wild
        sf_avail = counts[Card.SF]
        w_avail = counts[Card.WILD]
        if sf_avail + w_avail < req_sf_w:
            continue
        used_sf = min(sf_avail, req_sf_w)
        counts[Card.SF] -= used_sf
        counts[Card.WILD] -= (req_sf_w - used_sf)

        req_ti = op_spec.req_ti
        if counts[Card.TI] + counts[Card.WILD] < req_ti:
            continue
        used_ti = min(counts[Card.TI], req_ti)
        counts[Card.TI] -= used_ti
        counts[Card.WILD] -= (req_ti - used_ti)

        req_co = op_spec.req_co
        if counts[Card.CO] + counts[Card.WILD] < req_co:
            continue
        used_co = min(counts[Card.CO], req_co)
        counts[Card.CO] -= used_co
        counts[Card.WILD] -= (req_co - used_co)

        req_vn = op_spec.req_vn
        if counts[Card.VN] + counts[Card.WILD] < req_vn:
            continue

        paid_map = {p.id: prod[idx] for idx, p in enumerate(committee_players)}
        return True, paid_map

    return False, {}

def deduct_cards(committee_players: List[PlayerAI], paid_map: Dict[int, List[Card]], deck: DeckManager):
    total = []
    for p in committee_players:
        for c in paid_map[p.id]:
            p.hand.remove(c)
        total.extend(paid_map[p.id])
    deck.discard(total)

def run_experiment_with_logs(label: str, initial_deck: List[Card], n=30000) -> Dict[str, float]:
    banker_wins = 0
    intern_wins = 0
    insolvencies = 0
    rounds_list = []
    t_start = time.time()

    print(f"\n[INICIANDO] {label} (Total: {n:,} partidas)...")
    sys.stdout.flush()

    for game_idx in range(n):
        rng = random.Random(300000 + game_idx)
        deck = DeckManager(initial_deck, seed=rng.randint(0, 10**9))
        roles = [Role.BANKER] * 3 + [Role.INTERN] * 2
        rng.shuffle(roles)
        profile = rng.choice([InternProfile.A_AGGRESSIVE, InternProfile.B_SLEEPER, InternProfile.C_HEDGE])
        players = [PlayerAI(i, roles[i], profile, rng) for i in range(5)]

        for p in players:
            p.hand = deck.draw(3)

        b_wins, i_wins = 0, 0
        r_count = 0
        curr_chair = 0
        shuffled_ops = rng.sample(OPERATION_POOL, k=len(OPERATION_POOL))

        for op_spec in shuffled_ops[:5]:
            r_count += 1
            for p in players:
                p.hand.extend(deck.draw(1))

            vetoes = 0
            appr_comm = None
            forced = False

            while vetoes < 3 and appr_comm is None:
                chair = players[curr_chair]
                if chair.role == Role.BANKER:
                    cands = [p.id for p in players if p.id != chair.id]
                    cands.sort(key=lambda pid: chair.suspicions[pid])
                    comm = [chair.id] + cands[:op_spec.committee_size - 1]
                else:
                    others = [p.id for p in players if p.id != chair.id]
                    rng.shuffle(others)
                    comm = [chair.id] + others[:op_spec.committee_size - 1]

                votes = [p.vote_on_proposal(curr_chair, comm, op_spec) for p in players]
                if sum(votes) >= 3:
                    appr_comm = comm
                else:
                    vetoes += 1
                    curr_chair = (curr_chair + 1) % 5

            if appr_comm is None:
                forced = True
                chair = players[curr_chair]
                others = [p.id for p in players if p.id != chair.id]
                appr_comm = [chair.id] + others[:op_spec.committee_size - 1]

            for p in players:
                if p.id not in appr_comm:
                    p.apply_hold_yield()

            comm_objs = [players[pid] for pid in appr_comm]
            can_pay, paid_map = solve_payment(comm_objs, op_spec)

            if forced and not can_pay:
                i_wins += 1
                insolvencies += 1
                break

            if not can_pay:
                i_wins += 1
                for bp in players:
                    if bp.role == Role.BANKER:
                        for cid in appr_comm:
                            if cid != bp.id:
                                bp.suspicions[cid] = min(1.0, bp.suspicions[cid] + 0.20)
            else:
                deduct_cards(comm_objs, paid_map, deck)
                sabs = sum(1 for p in comm_objs if p.role == Role.INTERN and p.decide_sabotage(op_spec, r_count))
                if sabs >= op_spec.sabotages_to_fail:
                    i_wins += 1
                    for bp in players:
                        if bp.role == Role.BANKER:
                            for cid in appr_comm:
                                if cid != bp.id:
                                    bp.suspicions[cid] = min(1.0, bp.suspicions[cid] + 0.35)
                else:
                    b_wins += 1
                    for bp in players:
                        if bp.role == Role.BANKER:
                            for cid in appr_comm:
                                if cid != bp.id:
                                    bp.suspicions[cid] = max(0.05, bp.suspicions[cid] - 0.15)

            if b_wins >= 3 or i_wins >= 3:
                break
            curr_chair = (curr_chair + 1) % 5

        rounds_list.append(r_count)
        if b_wins >= 3:
            banker_wins += 1
        else:
            intern_wins += 1

        if (game_idx + 1) % 5000 == 0 or (game_idx + 1) == n:
            el = time.time() - t_start
            pct = ((game_idx + 1) / n) * 100.0
            cur_wr = (banker_wins / (game_idx + 1)) * 100.0
            print(f"   [{label}] {game_idx + 1:6,d} / {n:,} ({pct:5.1f}%) | WR Banqueiros: {cur_wr:5.2f}% | Tempo: {el:4.1f}s")
            sys.stdout.flush()

    return {
        "banker_wr": (banker_wins / n) * 100.0,
        "intern_wr": (intern_wins / n) * 100.0,
        "insolvency_pct": (insolvencies / max(1, intern_wins)) * 100.0,
        "avg_rounds": sum(rounds_list) / len(rounds_list)
    }

if __name__ == '__main__':
    print("=" * 80)
    print(" ESTUDO DE IMPACTO: CARTAS GENÉRICAS / CAIXA NO BALANCEAMENTO ")
    print("=" * 80)
    
    # 1. 0 Genéricos (100% Recursos: 26 Co, 20 Vn, 9 Ti, 3 Sf, 2 W = 60 cartas)
    deck_0g = [Card.CO]*26 + [Card.VN]*20 + [Card.TI]*9 + [Card.SF]*3 + [Card.WILD]*2
    
    # 2. 12 Genéricos / Caixa (20 Co, 15 Vn, 8 Ti, 3 Sf, 2 W, 12 Caixa = 60 cartas)
    deck_12g = [Card.CO]*20 + [Card.VN]*15 + [Card.TI]*8 + [Card.SF]*3 + [Card.WILD]*2 + [Card.CASH]*12
    
    # 3. 24 Genéricos / Caixa (15 Co, 12 Vn, 6 Ti, 2 Sf, 1 W, 24 Caixa = 60 cartas)
    deck_24g = [Card.CO]*15 + [Card.VN]*12 + [Card.TI]*6 + [Card.SF]*2 + [Card.WILD]*1 + [Card.CASH]*24

    r0 = run_experiment_with_logs("Cenário A: 0 Genéricos (100% Recursos)", deck_0g, 30000)
    r12 = run_experiment_with_logs("Cenário B: 12 Genéricos (Caixa Moderado)", deck_12g, 30000)
    r24 = run_experiment_with_logs("Cenário C: 24 Genéricos (Alta Diluição)", deck_24g, 30000)

    print("\n" + "=" * 80)
    print("                RESULTADOS COMPARATIVOS FINAIS")
    print("=" * 80)
    print(f"{'Cenário':<40} | {'WR Banqueiros':<15} | {'WR Estagiários':<15} | {'Insolvência':<12}")
    print("-" * 80)
    print(f"{'0 Genéricos (100% Recursos)':<40} | {r0['banker_wr']:>13.2f}% | {r0['intern_wr']:>13.2f}% | {r0['insolvency_pct']:>10.2f}%")
    print(f"{'12 Genéricos (Caixa/Liquidez)':<40} | {r12['banker_wr']:>13.2f}% | {r12['intern_wr']:>13.2f}% | {r12['insolvency_pct']:>10.2f}%")
    print(f"{'24 Genéricos (Alta Diluição)':<40} | {r24['banker_wr']:>13.2f}% | {r24['intern_wr']:>13.2f}% | {r24['insolvency_pct']:>10.2f}%")
    print("=" * 80)
