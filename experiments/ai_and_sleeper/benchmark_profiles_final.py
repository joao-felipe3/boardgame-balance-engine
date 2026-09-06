# -*- coding: utf-8 -*-
"""
Benchmark Detalhado dos 3 Perfis de IA dos Estagiários no Modelo Final Calibrado
(Hold 100% | 4 Coringas | Tiered Ops com Op 4 exigindo 2 Sabotagens | Custo Simétrico)
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
    CO = 'Cobalto'      # 25 cartas
    VN = 'Baunilha'     # 19 cartas
    TI = 'Titanio'      # 9 cartas
    SF = 'Safira'       # 3 cartas
    WILD = 'Coringa'    # 4 cartas (Ouro Líquido)

CARD_RARITY = {Card.CO: 1, Card.VN: 2, Card.TI: 3, Card.SF: 4, Card.WILD: 5}

INITIAL_DECK = (
    [Card.CO] * 25 +
    [Card.VN] * 19 +
    [Card.TI] * 9 +
    [Card.SF] * 3 +
    [Card.WILD] * 4
)

class Role(Enum):
    BANKER = 'Banqueiro'
    INTERN = 'Estagiario'

class InternProfile(Enum):
    A_AGGRESSIVE = 'A (Agressivo / Rush)'
    B_SLEEPER = 'B (Late-Game Sleeper)'
    C_HEDGE = 'C (Hedge / Manipulação Econômica)'

@dataclass
class OperationTemplate:
    name: str
    tier: int
    committee_size: int
    cost_per_player: int
    req_co: int = 0
    req_ti: int = 0
    req_vn: int = 0
    req_sf_or_wild: int = 0
    req_wild: int = 0
    sabotages_to_fail: int = 1

# Pool estruturado por Tiers (Progressão Crescente com Sorteio)
TIERED_POOLS = {
    1: [
        OperationTemplate("Arbitragem Rápida", 1, committee_size=2, cost_per_player=1, sabotages_to_fail=1),
        OperationTemplate("Exportação de Baunilha", 1, committee_size=2, cost_per_player=1, req_vn=1, sabotages_to_fail=1),
        OperationTemplate("Mineração de Cobalto", 1, committee_size=2, cost_per_player=1, req_co=1, sabotages_to_fail=1),
    ],
    2: [
        OperationTemplate("Sindicato Agrícola", 2, committee_size=3, cost_per_player=1, req_vn=1, sabotages_to_fail=1),
        OperationTemplate("Fundição de Titânio", 2, committee_size=3, cost_per_player=1, req_ti=1, sabotages_to_fail=1),
        OperationTemplate("Infraestrutura Portuária", 2, committee_size=3, cost_per_player=1, req_co=1, req_ti=1, sabotages_to_fail=1),
    ],
    3: [
        OperationTemplate("Refino Metalúrgico", 3, committee_size=2, cost_per_player=2, req_co=1, req_ti=1, sabotages_to_fail=1),
        OperationTemplate("Cofre de Gemas", 3, committee_size=2, cost_per_player=2, req_sf_or_wild=1, sabotages_to_fail=1),
    ],
    4: [
        OperationTemplate("Consórcio Safira", 4, committee_size=3, cost_per_player=2, req_sf_or_wild=2, sabotages_to_fail=2),
        OperationTemplate("Expansão Greenfield", 4, committee_size=3, cost_per_player=2, req_ti=1, req_sf_or_wild=1, sabotages_to_fail=2),
    ],
    5: [
        OperationTemplate("Holding Global BTG", 5, committee_size=3, cost_per_player=2, req_co=1, req_ti=1, req_vn=1, req_sf_or_wild=1, sabotages_to_fail=1),
    ]
}

class DeckManager:
    __slots__ = ('draw_pile', 'discard_pile', 'rng')

    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.draw_pile: List[Card] = []
        self.discard_pile: List[Card] = []
        self.reset()

    def reset(self):
        self.draw_pile = INITIAL_DECK.copy()
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
        """Hold 100%: 1 par de cartas iguais troca garantidamente por 1 Coringa."""
        counts = Counter(self.hand)
        for card, count in counts.items():
            if card == Card.WILD:
                continue
            if count >= 2:
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
                if op_spec.tier <= 2:
                    return True
                return (self.id in committee) or (self.rng.random() < 0.35)
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


def solve_symmetric_resource_payment(
    committee_players: List[PlayerAI],
    op_spec: OperationTemplate
) -> Tuple[bool, Dict[int, List[Card]]]:
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

    def get_player_combos(p_id: int):
        cards = available_map[p_id]
        combos = list(set(combinations(range(len(cards)), c_per_p)))
        return [[cards[idx] for idx in c] for c in combos]

    player_combos = [get_player_combos(p.id) for p in committee_players]

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


def deduct_symmetric_cards(committee_players: List[PlayerAI], paid_map: Dict[int, List[Card]], deck: DeckManager):
    total_paid = []
    for p in committee_players:
        for c in paid_map[p.id]:
            p.hand.remove(c)
        total_paid.extend(paid_map[p.id])
    deck.discard(total_paid)


def simulate_game_profile(game_idx: int, profile: InternProfile, seed: Optional[int] = None):
    rng = random.Random(seed if seed is not None else (int(time.time() * 1000) ^ game_idx))
    deck = DeckManager(seed=rng.randint(0, 10**9))

    roles = [Role.BANKER] * 3 + [Role.INTERN] * 2
    rng.shuffle(roles)
    players = [PlayerAI(pid, r, profile, rng) for pid, r in enumerate(roles)]

    for p in players:
        p.hand = deck.draw(3)

    banker_wins = 0
    intern_wins = 0
    round_count = 0
    current_chairman = 0

    # Sorteia 1 operação de cada Tier (Dificuldade Crescente com Variabilidade)
    chosen_ops = [rng.choice(TIERED_POOLS[tier]) for tier in range(1, 6)]

    for op_idx in range(5):
        round_count += 1
        op_spec = chosen_ops[op_idx]

        for p in players:
            p.hand.extend(deck.draw(1))

        consecutive_vetoes = 0
        approved_committee = None
        forced_execution = False

        while consecutive_vetoes < 3 and approved_committee is None:
            chairman_player = players[current_chairman]
            if chairman_player.role == Role.BANKER:
                candidates = [p.id for p in players if p.id != chairman_player.id]
                candidates.sort(key=lambda pid: chairman_player.suspicions[pid])
                committee = [chairman_player.id] + candidates[:op_spec.committee_size - 1]
            else:
                other_pids = [p.id for p in players if p.id != chairman_player.id]
                rng.shuffle(other_pids)
                committee = [chairman_player.id] + other_pids[:op_spec.committee_size - 1]

            votes = [p.vote_on_proposal(current_chairman, committee, op_spec) for p in players]
            if sum(votes) >= 3:
                approved_committee = committee
            else:
                consecutive_vetoes += 1
                current_chairman = (current_chairman + 1) % 5

        if approved_committee is None:
            forced_execution = True
            chairman_player = players[current_chairman]
            other_pids = [p.id for p in players if p.id != chairman_player.id]
            approved_committee = [chairman_player.id] + other_pids[:op_spec.committee_size - 1]

        for p in players:
            if p.id not in approved_committee:
                p.apply_hold_yield()

        committee_objs = [players[pid] for pid in approved_committee]
        can_pay, paid_map = solve_symmetric_resource_payment(committee_objs, op_spec)

        if forced_execution and not can_pay:
            return Role.INTERN, "Insolvencia", round_count, True

        if not can_pay:
            intern_wins += 1
            for bp in players:
                if bp.role == Role.BANKER:
                    for cid in approved_committee:
                        if cid != bp.id:
                            bp.suspicions[cid] = min(1.0, bp.suspicions[cid] + 0.20)
        else:
            deduct_symmetric_cards(committee_objs, paid_map, deck)
            sabotage_count = sum(
                1 for p in committee_objs if p.role == Role.INTERN and p.decide_sabotage(op_spec, round_count)
            )

            if sabotage_count >= op_spec.sabotages_to_fail:
                intern_wins += 1
                for bp in players:
                    if bp.role == Role.BANKER:
                        for cid in approved_committee:
                            if cid != bp.id:
                                bp.suspicions[cid] = min(1.0, bp.suspicions[cid] + 0.35)
            else:
                banker_wins += 1
                for bp in players:
                    if bp.role == Role.BANKER:
                        for cid in approved_committee:
                            if cid != bp.id:
                                bp.suspicions[cid] = max(0.05, bp.suspicions[cid] - 0.15)

        if banker_wins >= 3:
            return Role.BANKER, "Vitoria Banqueiros", round_count, False
        elif intern_wins >= 3:
            return Role.INTERN, "Sabotagens", round_count, False

        current_chairman = (current_chairman + 1) % 5

    winner = Role.BANKER if banker_wins > intern_wins else Role.INTERN
    cause = "Vitoria Banqueiros" if winner == Role.BANKER else "Sabotagens"
    return winner, cause, round_count, False


def run_profile_study(profile: InternProfile, n: int = 30000) -> Dict[str, float]:
    banker_wins = 0
    intern_wins = 0
    insolvencies = 0
    sabotage_losses = 0
    rounds_list = []
    t_start = time.time()

    print(f"\n[BENCHMARK] Testando Perfil: {profile.value} (30.000 partidas)...")
    sys.stdout.flush()

    for i in range(n):
        winner, cause, r_count, ins = simulate_game_profile(i, profile, seed=900000 + i)
        if winner == Role.BANKER:
            banker_wins += 1
        else:
            intern_wins += 1
            if ins:
                insolvencies += 1
            else:
                sabotage_losses += 1
        rounds_list.append(r_count)

        if (i + 1) % 5000 == 0 or (i + 1) == n:
            el = time.time() - t_start
            pct = ((i + 1) / n) * 100.0
            cur_i_wr = (intern_wins / (i + 1)) * 100.0
            print(f"   [{profile.name[:10]}] {i + 1:6,d} / {n:,} ({pct:5.1f}%) | WR Estagiários: {cur_i_wr:5.2f}% | Tempo: {el:4.1f}s")
            sys.stdout.flush()

    total_losses = max(1, intern_wins)
    return {
        "intern_wr": (intern_wins / n) * 100.0,
        "banker_wr": (banker_wins / n) * 100.0,
        "insolvency_pct_of_losses": (insolvencies / total_losses) * 100.0,
        "sabotage_pct_of_losses": (sabotage_losses / total_losses) * 100.0,
        "avg_rounds": sum(rounds_list) / len(rounds_list)
    }

if __name__ == '__main__':
    print("=" * 80)
    print("      ESTUDO COMPARATIVO DE IA: OS 3 PERFIS DOS ESTAGIÁRIOS      ")
    print("=" * 80)

    res_a = run_profile_study(InternProfile.A_AGGRESSIVE, 30000)
    res_b = run_profile_study(InternProfile.B_SLEEPER, 30000)
    res_c = run_profile_study(InternProfile.C_HEDGE, 30000)

    print("\n" + "=" * 80)
    print("                    TABELA COMPARATIVA DE PERFORMANCE")
    print("=" * 80)
    print(f"{'Perfil de IA':<25} | {'WR Estagiários':<16} | {'WR Banqueiros':<15} | {'Insolvência':<12} | {'Duração':<10}")
    print("-" * 80)
    print(f"{'A (Agressivo / Rush)':<25} | {res_a['intern_wr']:>14.2f}% | {res_a['banker_wr']:>13.2f}% | {res_a['insolvency_pct_of_losses']:>10.2f}% | {res_a['avg_rounds']:>6.2f} ops")
    print(f"{'B (Late-Game Sleeper)':<25} | {res_b['intern_wr']:>14.2f}% | {res_b['banker_wr']:>13.2f}% | {res_b['insolvency_pct_of_losses']:>10.2f}% | {res_b['avg_rounds']:>6.2f} ops")
    print(f"{'C (Hedge Econômico)':<25} | {res_c['intern_wr']:>14.2f}% | {res_c['banker_wr']:>13.2f}% | {res_c['insolvency_pct_of_losses']:>10.2f}% | {res_c['avg_rounds']:>6.2f} ops")
    print("=" * 80)
