# -*- coding: utf-8 -*-
"""
Simulador com Negociação Inteligente de Mão e Dedução por Eliminação de Hipóteses
"""
import random
import time
import sys
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Tuple, Optional, Set
import itertools
import pandas as pd
import numpy as np


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
    A_AGGRESSIVE = 'A (Agressivo / Sabotagem Cedo)'
    B_SLEEPER = 'B (Late-Game Sleeper / Camuflado)'
    C_HEDGE = 'C (Hedge / Estrangulamento de Recursos)'

@dataclass
class ContractRecipe:
    name: str
    tier: int
    committee_size: int
    cost_per_player: int
    req_co: int = 0
    req_vn: int = 0
    req_ti: int = 0
    req_sf: int = 0
    req_wild: int = 0

    @property
    def total_cards(self) -> int:
        return self.committee_size * self.cost_per_player

    def get_recipe_counter(self) -> Counter:
        return Counter({
            Card.CO: self.req_co,
            Card.VN: self.req_vn,
            Card.TI: self.req_ti,
            Card.SF: self.req_sf,
            Card.WILD: self.req_wild
        })

CONTRACT_CATALOG = {
    1: [
        ContractRecipe("Arbitragem Simples", 1, committee_size=2, cost_per_player=1, req_co=1, req_vn=1),
        ContractRecipe("Extração de Cobalto", 1, committee_size=2, cost_per_player=1, req_co=2),
        ContractRecipe("Remessa de Baunilha", 1, committee_size=2, cost_per_player=1, req_vn=2),
    ],
    2: [
        ContractRecipe("Sindicato Agrícola", 2, committee_size=3, cost_per_player=1, req_vn=2, req_co=1),
        ContractRecipe("Fundição de Titânio", 2, committee_size=3, cost_per_player=1, req_ti=1, req_co=1, req_vn=1),
        ContractRecipe("Logística Portuária", 2, committee_size=3, cost_per_player=1, req_co=2, req_ti=1),
    ],
    3: [
        ContractRecipe("Refino Metalúrgico", 3, committee_size=2, cost_per_player=2, req_ti=2, req_co=2),
        ContractRecipe("Exportação Especial de Safira", 3, committee_size=2, cost_per_player=2, req_sf=1, req_vn=2, req_co=1),
        ContractRecipe("Lote de Titânio & Baunilha", 3, committee_size=2, cost_per_player=2, req_ti=1, req_vn=2, req_co=1),
    ],
    4: [
        ContractRecipe("Consórcio Safira", 4, committee_size=3, cost_per_player=2, req_sf=1, req_ti=2, req_co=2, req_vn=1),
        ContractRecipe("Expansão Greenfield", 4, committee_size=3, cost_per_player=2, req_ti=2, req_vn=2, req_co=2),
    ],
    5: [
        ContractRecipe("Holding Global BTG", 5, committee_size=3, cost_per_player=2, req_sf=1, req_ti=1, req_vn=2, req_co=2),
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


def evaluate_recipe(submitted_cards: List[Card], recipe: ContractRecipe) -> bool:
    pool_counts = Counter(submitted_cards)
    recipe_counts = recipe.get_recipe_counter()
    wildcards = pool_counts[Card.WILD]

    for commodity in [Card.SF, Card.TI, Card.VN, Card.CO]:
        needed = recipe_counts[commodity]
        available = pool_counts[commodity]

        if available >= needed:
            pool_counts[commodity] -= needed
        else:
            deficit = needed - available
            if wildcards >= deficit:
                wildcards -= deficit
                pool_counts[commodity] = 0
            else:
                return False

    return True


def smart_team_negotiate_and_submit(
    committee: List[int],
    roles: Dict[int, Role],
    hands: Dict[int, List[Card]],
    profile: InternProfile,
    recipe: ContractRecipe,
    round_num: int
) -> List[Card]:
    """
    Simula a negociação real de mesa entre jogadores humanos:
    - O comitê encontra a combinação ótima de cartas que cobre a receita.
    - Banqueiros colocam EXATAMENTE as cartas que prometeram.
    - Estagiários: se forem sabotar, substituem a carta prometida por lixo (Cobalto).
    """
    cost_per_p = recipe.cost_per_player
    recipe_counter = recipe.get_recipe_counter()
    needed_cards = []
    for c, cnt in recipe_counter.items():
        needed_cards.extend([c] * cnt)

    # Verifica quais cartas os membros têm disponíveis
    # Encontra uma alocação viável da receita entre os membros
    all_player_cards = {p: hands[p].copy() for p in committee}
    promised_assignment: Dict[int, List[Card]] = {p: [] for p in committee}

    # Distribui os requisitos para quem realmente tem a carta
    remaining_needed = needed_cards.copy()
    for card in needed_cards:
        for p in committee:
            if len(promised_assignment[p]) < cost_per_p and card in all_player_cards[p]:
                promised_assignment[p].append(card)
                all_player_cards[p].remove(card)
                remaining_needed.remove(card)
                break

    # Se sobrou requisitos, tenta cobrir com Coringas
    for card in remaining_needed.copy():
        for p in committee:
            if len(promised_assignment[p]) < cost_per_p and Card.WILD in all_player_cards[p]:
                promised_assignment[p].append(Card.WILD)
                all_player_cards[p].remove(Card.WILD)
                remaining_needed.remove(card)
                break

    # Completa as cotas restantes de quem ainda tem vaga
    for p in committee:
        while len(promised_assignment[p]) < cost_per_p:
            if all_player_cards[p]:
                card = min(all_player_cards[p], key=lambda c: CARD_RARITY[c])
                all_player_cards[p].remove(card)
                promised_assignment[p].append(card)
            else:
                promised_assignment[p].append(Card.CO)

    # Agora cada jogador decide o que REALMENTE enviar
    submitted_all: List[Card] = []
    for p in committee:
        is_banker = (roles[p] == Role.BANKER)
        cost = cost_per_p

        if is_banker:
            # Banqueiro entrega exatamente o que prometeu
            cards_to_play = promised_assignment[p]
            for c in cards_to_play:
                if c in hands[p]:
                    hands[p].remove(c)
                elif Card.WILD in hands[p]:
                    hands[p].remove(Card.WILD)
                elif hands[p]:
                    hands[p].pop()
            submitted_all.extend(cards_to_play)
        else:
            # Estagiário
            should_sab = False
            if profile == InternProfile.A_AGGRESSIVE:
                should_sab = True
            elif profile == InternProfile.B_SLEEPER:
                should_sab = (round_num >= 3)
            elif profile == InternProfile.C_HEDGE:
                should_sab = (round_num >= 3 or random.random() < 0.60)

            if not should_sab:
                # Sleeper / Camuflado cumpre o acordo
                cards_to_play = promised_assignment[p]
                for c in cards_to_play:
                    if c in hands[p]:
                        hands[p].remove(c)
                    elif hands[p]:
                        hands[p].pop()
                submitted_all.extend(cards_to_play)
            else:
                # Sabota: joga Cobalto em vez da carta nobre prometida
                junk = [c for c in hands[p] if c in (Card.CO, Card.VN)]
                if len(junk) >= cost:
                    cards_to_play = junk[:cost]
                else:
                    cards_to_play = hands[p][:cost]
                for c in cards_to_play:
                    if c in hands[p]:
                        hands[p].remove(c)
                submitted_all.extend(cards_to_play)

    return submitted_all


def simulate_full_game_with_smart_deduction(
    profile: InternProfile,
    seed: Optional[int] = None
) -> Tuple[str, str, int, Counter]:
    rng = random.Random(seed)
    deck = DeckManager(seed=rng.randint(0, 10**9))

    roles = [Role.BANKER] * 3 + [Role.INTERN] * 2
    rng.shuffle(roles)
    role_map = {i: roles[i] for i in range(5)}

    hands = {i: deck.draw(3) for i in range(5)}

    # Espaço de Hipóteses Compartilhado da Mesa
    # 10 pares possíveis no início: [(0,1), (0,2), ..., (3,4)]
    possible_traitor_pairs = set(itertools.combinations(range(5), 2))
    known_traitors_by_bankers: Set[int] = set()

    banker_score = 0
    intern_score = 0
    curr_chair = 0
    ops = [rng.choice(CONTRACT_CATALOG[t]) for t in range(1, 6)]

    for r_idx, op in enumerate(ops):
        r_num = r_idx + 1

        # Compra
        for i in range(5):
            hands[i].extend(deck.draw(1))

        # Proposição de Comitê
        chair = curr_chair
        chair_role = role_map[chair]

        if chair_role == Role.BANKER:
            # Banqueiro escolhe apenas jogadores que NÃO estão confirmados como traidores
            # e que minimizam a presença nos pares suspeitos
            sus_scores = {i: 0 for i in range(5)}
            for pair in possible_traitor_pairs:
                sus_scores[pair[0]] += 1
                sus_scores[pair[1]] += 1

            cands = [i for i in range(5) if i != chair and i not in known_traitors_by_bankers]
            cands.sort(key=lambda p: sus_scores[p])
            if len(cands) < op.committee_size - 1:
                cands = [i for i in range(5) if i != chair]
                cands.sort(key=lambda p: sus_scores[p])
            comm = [chair] + cands[:op.committee_size - 1]
        else:
            # Estagiário
            others = [i for i in range(5) if i != chair]
            rng.shuffle(others)
            comm = [chair] + others[:op.committee_size - 1]

        # Votação dos Banqueiros
        # Banqueiros votam NÃO se souberem que há um traidor confirmado no comitê
        has_known_traitor = any(p in known_traitors_by_bankers for p in comm)
        if has_known_traitor and chair_role == Role.INTERN:
            # Rejeição em massa pelos 3 Banqueiros
            votes_sim = 2 # Apenas os 2 estagiários votariam SIM
            # Passa para o próximo Chairman
            curr_chair = (curr_chair + 1) % 5
            chair = curr_chair
            chair_role = role_map[chair]
            # Novo Chairman propõe
            if chair_role == Role.BANKER:
                cands = [i for i in range(5) if i != chair and i not in known_traitors_by_bankers]
                comm = [chair] + cands[:op.committee_size - 1]
            else:
                others = [i for i in range(5) if i != chair]
                comm = [chair] + others[:op.committee_size - 1]

        # Hold fora do comitê
        for i in range(5):
            if i not in comm:
                counts = Counter(hands[i])
                for c, cnt in counts.items():
                    if c != Card.WILD and cnt >= 2:
                        hands[i].remove(c)
                        hands[i].remove(c)
                        hands[i].append(Card.WILD)
                        break

        # Envio de cartas
        submitted = smart_team_negotiate_and_submit(comm, role_map, hands, profile, op, r_num)
        deck.discard(submitted)

        # Auditoria de Conformidade
        is_compliant = evaluate_recipe(submitted, op)

        if is_compliant:
            banker_score += 1
        else:
            intern_score += 1
            # Atualização de Dedução Booleana
            # Pelo menos 1 membro do comitê é traidor
            possible_traitor_pairs = {pair for pair in possible_traitor_pairs if any(p in pair for p in comm)}

            # Se era comitê de 2: o Banqueiro que estava lá descobre o traidor com 100%
            if len(comm) == 2:
                p1, p2 = comm
                if role_map[p1] == Role.BANKER and role_map[p2] == Role.INTERN:
                    known_traitors_by_bankers.add(p2)
                elif role_map[p2] == Role.BANKER and role_map[p1] == Role.INTERN:
                    known_traitors_by_bankers.add(p1)

            # Se todos os pares restantes apontam para um jogador específico -> Traidor Confirmado
            for p in range(5):
                if all(p in pair for pair in possible_traitor_pairs):
                    known_traitors_by_bankers.add(p)

        if banker_score >= 3:
            return Role.BANKER.value, "Vitoria Banqueiros", r_num, Counter()
        elif intern_score >= 3:
            return Role.INTERN.value, "Inconformidade/Fraude", r_num, Counter()

        curr_chair = (curr_chair + 1) % 5

    winner = Role.BANKER.value if banker_score > intern_score else Role.INTERN.value
    return winner, "Fim de Rodadas", 5, Counter()


def run_benchmark_smart_deduction(n=50000):
    profiles = [InternProfile.A_AGGRESSIVE, InternProfile.B_SLEEPER, InternProfile.C_HEDGE]
    print("=" * 80)
    print(" SIMULAÇÃO COM NEGOCIAÇÃO INTELIGENTE DE MÃO E DEDUÇÃO BOOLEANA ESTREITA ")
    print("=" * 80)

    for prof in profiles:
        print(f"\n[BENCHMARK] Executando {n:,} partidas para {prof.value}...")
        t0 = time.time()
        b_wins, i_wins = 0, 0
        rounds_list = []

        for i in range(n):
            winner, cause, r_cnt, _ = simulate_full_game_with_smart_deduction(prof, seed=800000 + i)
            if winner == Role.BANKER.value:
                b_wins += 1
            else:
                i_wins += 1
            rounds_list.append(r_cnt)

            if (i + 1) % 10000 == 0:
                cur_bw = (b_wins / (i + 1)) * 100.0
                print(f"   [{prof.name[:10]}] {i + 1:6,d} / {n:,} | WR Banqueiros: {cur_bw:5.2f}% | Tempo: {time.time() - t0:4.1f}s")
                sys.stdout.flush()

        print(f"-> {prof.value}: Banqueiros = {(b_wins/n)*100:.2f}% | Estagiários = {(i_wins/n)*100:.2f}% | Duração: {np.mean(rounds_list):.2f} ops")

if __name__ == '__main__':
    run_benchmark_smart_deduction(50000)
