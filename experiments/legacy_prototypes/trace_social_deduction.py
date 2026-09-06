# -*- coding: utf-8 -*-
"""
BTG Madagascar - Simulador Oficial de Dedução Social & Auditoria Forense (v9.0)
==============================================================================
"""

import random
import time
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Tuple, Optional, Set
import itertools
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

INITIAL_CLEAN_DECK = (
    [CardType.CO] * 24 +
    [CardType.VN] * 20 +
    [CardType.TI] * 10 +
    [CardType.SF] * 6
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

SEVEN_TIERS_CATALOG = {
    1: [
        ContractSpec("Arbitragem Simples", 1, committee_size=2, cost_per_player=1, target_value=4),
        ContractSpec("Exportacao de Baunilha", 1, committee_size=2, cost_per_player=1, target_value=4, req_commodity=CardType.VN),
    ],
    2: [
        ContractSpec("Mineracao de Cobalto", 2, committee_size=2, cost_per_player=1, target_value=4, req_commodity=CardType.CO),
        ContractSpec("Lote Agricola", 2, committee_size=2, cost_per_player=1, target_value=5, req_commodity=CardType.VN),
    ],
    3: [
        ContractSpec("Sindicato de Titanio", 3, committee_size=3, cost_per_player=1, target_value=8, req_commodity=CardType.TI),
        ContractSpec("Logistica Portuaria", 3, committee_size=3, cost_per_player=1, target_value=7, req_commodity=CardType.CO),
    ],
    4: [
        ContractSpec("Refino Metalurgico", 4, committee_size=3, cost_per_player=1, target_value=10, req_commodity=CardType.TI),
        ContractSpec("Consorcio Agro-Industrial", 4, committee_size=3, cost_per_player=1, target_value=10, req_commodity=CardType.VN),
    ],
    5: [
        ContractSpec("Cofre de Gemas", 5, committee_size=2, cost_per_player=2, target_value=13, req_commodity=CardType.SF),
        ContractSpec("Fundicao Estrategica", 5, committee_size=2, cost_per_player=2, target_value=12, req_commodity=CardType.TI),
    ],
    6: [
        ContractSpec("Consorcio Safira", 6, committee_size=3, cost_per_player=2, target_value=17, req_commodity=CardType.SF),
        ContractSpec("Complexo Greenfield", 6, committee_size=3, cost_per_player=2, target_value=16, req_commodity=CardType.TI),
    ],
    7: [
        ContractSpec("Holding Global BTG (Climax)", 7, committee_size=3, cost_per_player=2, target_value=21, req_commodity=CardType.SF),
    ]
}

class DeckManager:
    __slots__ = ('draw_pile', 'discard_pile', 'rng')

    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.draw_pile = INITIAL_CLEAN_DECK.copy()
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


class PlayerAI:
    __slots__ = ('id', 'role', 'profile', 'rng', 'hand', 'suspicions', 'known_traitors', 'credits_accumulated')

    def __init__(self, player_id: int, role: Role, profile: InternProfile, rng: random.Random):
        self.id = player_id
        self.role = role
        self.profile = profile
        self.rng = rng
        self.hand: List[ResourceCard] = []
        self.suspicions: Dict[int, float] = {i: 0.40 for i in range(5)}
        self.suspicions[self.id] = 0.0 if role == Role.BANKER else 1.0
        self.known_traitors: Set[int] = set()
        self.credits_accumulated = 0

    def accumulate_holding_interest(self):
        for card in self.hand:
            if card.card_type != CardType.TOXIC:
                card.interest_accumulated += 1

    def claim_success_credit(self):
        self.credits_accumulated += 1
        if self.credits_accumulated >= 2:
            self.credits_accumulated -= 2
            if self.role == Role.BANKER:
                self.hand.append(ResourceCard(CardType.WILD, 0))
            else:
                self.hand.append(ResourceCard(CardType.TOXIC, 0))

    def make_public_declaration(self, contract: ContractSpec, round_num: int) -> PlayerDeclaration:
        has_req_real = False
        if contract.req_commodity is not None:
            has_req_real = any(c.card_type in (contract.req_commodity, CardType.WILD) for c in self.hand)

        cost = contract.cost_per_player
        pos_cards = sorted([c for c in self.hand if c.card_type != CardType.TOXIC], key=lambda c: -c.effective_value)
        best_val = sum(c.effective_value for c in pos_cards[:cost]) if pos_cards else 0

        if self.role == Role.BANKER:
            return PlayerDeclaration(self.id, has_req_real, best_val)
        else:
            if self.profile == InternProfile.A_AGGRESSIVE:
                claims = True if contract.req_commodity is not None else False
                return PlayerDeclaration(self.id, claims, best_val)
            elif self.profile == InternProfile.B_SLEEPER:
                if round_num <= 2:
                    return PlayerDeclaration(self.id, has_req_real, best_val)
                else:
                    has_toxic = any(c.card_type == CardType.TOXIC for c in self.hand)
                    claims = True if (contract.req_commodity is not None and has_toxic) else has_req_real
                    return PlayerDeclaration(self.id, claims, best_val)
            elif self.profile == InternProfile.C_HEDGE:
                return PlayerDeclaration(self.id, has_req_real, best_val)

    def vote_on_proposal(self, proposer: int, committee: List[int], contract: ContractSpec, round_num: int) -> bool:
        if self.role == Role.BANKER:
            for p in committee:
                if p in self.known_traitors or self.suspicions[p] >= 0.90:
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
                if contract.tier <= 2:
                    return True
                if self.id in committee:
                    return True
                return self.rng.random() < 0.15
            elif self.profile == InternProfile.C_HEDGE:
                if self.id in committee:
                    return True
                return self.rng.random() < 0.20
        return True

    def choose_cards_smartly(
        self,
        contract: ContractSpec,
        round_num: int,
        is_responsible_for_req: bool
    ) -> List[ResourceCard]:
        cost = contract.cost_per_player
        should_sabotage = False

        if self.role == Role.INTERN:
            if self.profile == InternProfile.A_AGGRESSIVE:
                should_sabotage = True
            elif self.profile == InternProfile.B_SLEEPER:
                has_toxic = any(c.card_type == CardType.TOXIC for c in self.hand)
                should_sabotage = (round_num >= 3 and has_toxic) or (round_num >= 4)
            elif self.profile == InternProfile.C_HEDGE:
                has_toxic = any(c.card_type == CardType.TOXIC for c in self.hand)
                should_sabotage = (has_toxic and round_num >= 3) or (round_num >= 4)

        if not should_sabotage:
            expected_quota = contract.target_value / contract.committee_size
            pos_cards = [c for c in self.hand if c.card_type != CardType.TOXIC]

            if not pos_cards:
                return self.hand[:cost]

            valid_combos = list(itertools.combinations(pos_cards, cost))
            if not valid_combos:
                return self.hand[:cost]

            if is_responsible_for_req and contract.req_commodity is not None:
                req = contract.req_commodity
                req_combos = [cb for cb in valid_combos if any(c.card_type in (req, CardType.WILD) for c in cb)]
                if req_combos:
                    valid_combos = req_combos

            def combo_score(cb):
                val = sum(c.effective_value for c in cb)
                diff = val - expected_quota
                if diff >= 0:
                    return (0, diff)
                else:
                    return (1, -diff)

            best_combo = min(valid_combos, key=combo_score)
            return list(best_combo)
        else:
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
        has_direct = any(c.card_type == contract.req_commodity for c in submitted_cards)
        has_wild = any(c.card_type == CardType.WILD for c in submitted_cards)
        has_req = (has_direct or has_wild)

    is_success = (total_val >= contract.target_value) and has_req
    return is_success, total_val, has_req


def simulate_game(
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
    ops = [rng.choice(SEVEN_TIERS_CATALOG[t]) for t in range(1, 8)]
    suspicion_history = []

    for r_idx, contract in enumerate(ops):
        round_count += 1

        for p in players:
            p.hand.extend(deck.draw(1))

        bankers = [p for p in players if p.role == Role.BANKER]
        sus_snapshot = {}
        for target_id in range(5):
            sus_vals = [b.suspicions[target_id] for b in bankers if b.id != target_id]
            sus_snapshot[target_id] = np.mean(sus_vals) if sus_vals else 0.0
        suspicion_history.append(sus_snapshot)

        consecutive_vetoes = 0
        approved_committee = None
        promised_supplier = None
        forced_execution = False

        while consecutive_vetoes < 3 and approved_committee is None:
            chair = players[curr_chair]

            candidates_order = [p.id for p in players if p.id != chair.id and p.id not in chair.known_traitors]
            candidates_order.sort(key=lambda pid: chair.suspicions[pid])
            if len(candidates_order) < contract.committee_size - 1:
                candidates_order = [p.id for p in players if p.id != chair.id]
                candidates_order.sort(key=lambda pid: chair.suspicions[pid])

            leader_has_req = False
            if contract.req_commodity is not None:
                leader_has_req = any(c.card_type in (contract.req_commodity, CardType.WILD) for c in chair.hand)

            chosen_comm = [chair.id]
            assigned_req_player = chair.id if leader_has_req else None

            declarations = {pid: players[pid].make_public_declaration(contract, round_count) for pid in candidates_order}

            if not leader_has_req and contract.req_commodity is not None:
                suppliers = [pid for pid in candidates_order if declarations[pid].claims_req]
                if suppliers:
                    assigned_req_player = suppliers[0]
                    chosen_comm.append(suppliers[0])
                    candidates_order.remove(suppliers[0])

            while len(chosen_comm) < contract.committee_size and candidates_order:
                chosen_comm.append(candidates_order.pop(0))

            votes = [p.vote_on_proposal(curr_chair, chosen_comm, contract, round_count) for p in players]
            if sum(votes) >= 3:
                approved_committee = chosen_comm
                promised_supplier = assigned_req_player
            else:
                consecutive_vetoes += 1
                curr_chair = (curr_chair + 1) % 5

        if approved_committee is None:
            forced_execution = True
            chair = players[curr_chair]
            others = [p.id for p in players if p.id != chair.id]
            approved_committee = [chair.id] + others[:contract.committee_size - 1]
            promised_supplier = None

        for p in players:
            if p.id not in approved_committee:
                p.accumulate_holding_interest()

        comm_objs = [players[pid] for pid in approved_committee]

        submitted_all: List[ResourceCard] = []
        for p in comm_objs:
            is_req_responsible = (p.id == promised_supplier)
            sub = p.choose_cards_smartly(contract, round_count, is_req_responsible)
            for c in sub:
                if c in p.hand:
                    p.hand.remove(c)
            submitted_all.extend(sub)

        deck.discard(submitted_all)
        is_success, total_val, has_req = evaluate_contract_outcome(submitted_all, contract)

        if is_success:
            banker_score += 1
            for p in comm_objs:
                p.claim_success_credit()

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
                    "profile": profile.value,
                    "sus_history": suspicion_history
                }

            has_toxic = any(c.card_type == CardType.TOXIC for c in submitted_all)
            broken_promise = (contract.req_commodity is not None and not has_req and promised_supplier is not None)

            for bp in players:
                if bp.role == Role.BANKER:
                    if broken_promise and promised_supplier != bp.id:
                        bp.suspicions[promised_supplier] = 0.95
                        bp.known_traitors.add(promised_supplier)

                    delta = 0.50 if has_toxic else 0.30
                    if len(approved_committee) >= 3:
                        delta *= 0.70

                    for cid in approved_committee:
                        if cid != bp.id and cid != promised_supplier:
                            bp.suspicions[cid] = min(0.95, bp.suspicions[cid] + delta)

        if banker_score >= 4:
            return {
                "winner": Role.BANKER.value,
                "cause": "4 Contratos Concluidos",
                "rounds": round_count,
                "b_score": banker_score,
                "i_score": intern_score,
                "profile": profile.value,
                "sus_history": suspicion_history
            }
        elif intern_score >= 4:
            return {
                "winner": Role.INTERN.value,
                "cause": "4 Contratos Reprovados",
                "rounds": round_count,
                "b_score": banker_score,
                "i_score": intern_score,
                "profile": profile.value,
                "sus_history": suspicion_history
            }

        curr_chair = (curr_chair + 1) % 5

    w = Role.BANKER.value if banker_score > intern_score else Role.INTERN.value
    return {
        "winner": w,
        "cause": "Fim das 7 Rodadas",
        "rounds": 7,
        "b_score": banker_score,
        "i_score": intern_score,
        "profile": profile.value,
        "sus_history": suspicion_history
    }


def run_benchmark_and_suspicion_analysis(n=50000):
    print("=" * 80)
    print(" SIMULADOR DE DEDUCAO SOCIAL & AUDITORIA FORENSE DE PROMESSAS (50.000 JOGOS) ")
    print("=" * 80)
    t0 = time.time()
    results = []
    profiles = [InternProfile.A_AGGRESSIVE, InternProfile.B_SLEEPER, InternProfile.C_HEDGE]

    sus_by_profile_and_round = {
        prof.value: {
            "innocent": defaultdict(list),
            "traitor": defaultdict(list)
        } for prof in profiles
    }

    for i in range(n):
        prof = random.choice(profiles)
        res = simulate_game(i, prof, seed=543210 + i)
        results.append(res)

        hist = res["sus_history"]
        rng_temp = random.Random(543210 + i)
        roles = [Role.BANKER] * 3 + [Role.INTERN] * 2
        rng_temp.shuffle(roles)

        for r_idx, snap in enumerate(hist):
            round_num = r_idx + 1
            for pid, sus_val in snap.items():
                if roles[pid] == Role.BANKER:
                    sus_by_profile_and_round[prof.value]["innocent"][round_num].append(sus_val)
                else:
                    sus_by_profile_and_round[prof.value]["traitor"][round_num].append(sus_val)

        if (i + 1) % 10000 == 0:
            print(f"   [Deducao Social v9.0] {i + 1:6,d} / {n:,} ({(i+1)/n*100:5.1f}%) | Tempo: {time.time() - t0:4.1f}s")
            sys.stdout.flush()

    df = pd.DataFrame(results)
    b_wins = (df["winner"] == Role.BANKER.value).sum()
    i_wins = (df["winner"] == Role.INTERN.value).sum()

    print("\n" + "=" * 80)
    print("             RELATORIO FINAL DE BALANCEAMENTO & WIN RATE")
    print("=" * 80)
    print(f"1. WIN RATE GLOBAL (Meta: 51% a 54% pro-Banqueiros):")
    print(f"   - Banqueiros : {(b_wins/n)*100:6.2f}% ({b_wins:,} vitorias)")
    print(f"   - Estagiarios: {(i_wins/n)*100:6.2f}% ({i_wins:,} vitorias)")
    print(f"   - Duracao Media: {df['rounds'].mean():.2f} +- {df['rounds'].std():.2f} rodadas")

    print(f"\n2. MATRIZ DE PLACARES FINAIS:")
    print("-" * 60)
    df["score"] = df["b_score"].astype(str) + " x " + df["i_score"].astype(str)
    score_counts = df["score"].value_counts()
    for sc, cnt in score_counts.head(7).items():
        tag = "[Climax]" if "4 x 3" in sc or "3 x 4" in sc else ""
        print(f"   * {sc:<15}: {cnt:>8,d} ({(cnt/n)*100:5.2f}%) {tag}")

    print("\n" + "=" * 80)
    print("      EVOLUCAO DA MATRIZ DE SUSPEITA DOS BANQUEIROS (DEDUCAO SOCIAL)")
    print("=" * 80)
    print("Escala de Suspeita: 0.00 (Inocente Certo) <---> 1.00 (Traidor Confirmado)\n")

    for prof_name, data in sus_by_profile_and_round.items():
        print(f"[+] PERFIL DO ESTAGIARIO: {prof_name}")
        print("-" * 75)
        print(f"{'Rodada':<10} | {'Suspeita s/ Inocente':<25} | {'Suspeita s/ Traidor':<25} | {'Diferenca (Delta)'}")
        print("-" * 75)
        for r in range(1, 8):
            inn_vals = data["innocent"][r]
            tra_vals = data["traitor"][r]
            if inn_vals and tra_vals:
                avg_inn = np.mean(inn_vals)
                avg_tra = np.mean(tra_vals)
                diff = avg_tra - avg_inn
                bar = "#" * int(avg_tra * 15)
                print(f"Rodada {r:<3} | {avg_inn:6.2f} ({avg_inn*100:4.1f}%)             | {avg_tra:6.2f} ({avg_tra*100:4.1f}%) [{bar:<15}] | Delta = {diff:+4.2f}")
        print()


if __name__ == '__main__':
    run_benchmark_and_suspicion_analysis(50000)
