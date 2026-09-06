# -*- coding: utf-8 -*-
"""
Analisador de Cenários e Árvore de Decisão Determinística - BTG Madagascar
========================================================================
Este script simula partidas com LOG DETALHADO PASSO A PASSO (trace completo)
para inspecionar cada decisão, voto, dedução de 100% e gestão de recursos.
"""

import random
import sys
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Tuple, Optional, Set

class Card(Enum):
    CO = 'Cobalto'
    VN = 'Baunilha'
    TI = 'Titanio'
    SF = 'Safira'
    WILD = 'Coringa'

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


class TableDeductionTracker:
    """
    Rastreador de Conhecimento Compartilhado e Dedução Booleana da Mesa.
    Modela a conversa de mesa real entre jogadores humanos.
    """
    def __init__(self):
        # Possíveis mundos: quais pares de jogadores podem ser os 2 Estagiários?
        # Inicialmente todas as combinações C(5, 2) = 10 mundos possíveis
        from itertools import combinations
        self.all_possible_traitor_pairs = list(combinations(range(5), 2))
        self.suspect_pairs = set(self.all_possible_traitor_pairs)
        self.confirmed_traitors = set()
        self.confirmed_innocents = set()

    def register_mission_failure(self, committee: List[int], round_num: int):
        """Uma missão falhou: sabemos que PELO MENOS 1 membro do comitê é traidor."""
        # Filtra pares que não contêm nenhum membro desse comitê
        self.suspect_pairs = {pair for pair in self.suspect_pairs if any(p in pair for p in committee)}
        self._update_confirmed()

    def register_mission_success(self, committee: List[int], round_num: int):
        """Uma missão teve sucesso."""
        pass

    def register_banker_accusation(self, accuser: int, accused: int):
        """Um Banqueiro 'accuser' acusa com 100% de certeza o 'accused' de ter fraudado."""
        # Se accuser for inocente, então accused É traidor.
        # Os outros banqueiros sabem: se accuser for Banqueiro -> accused é Estagiário.
        pass

    def _update_confirmed(self):
        # Se um jogador aparece em TODOS os pares suspeitos restantes -> Ele é 100% Traidor!
        for p in range(5):
            if all(p in pair for pair in self.suspect_pairs):
                self.confirmed_traitors.add(p)
            if all(p not in pair for pair in self.suspect_pairs):
                self.confirmed_innocents.add(p)


def evaluate_recipe(submitted_cards: List[Card], recipe: ContractRecipe) -> Tuple[bool, Counter]:
    pool_counts = Counter(submitted_cards)
    recipe_counts = recipe.get_recipe_counter()
    wildcards = pool_counts[Card.WILD]
    deficits = Counter()

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
                uncovered = deficit - wildcards
                deficits[commodity] = uncovered
                wildcards = 0

    return (sum(deficits.values()) == 0), deficits


def trace_sample_game(profile: InternProfile, seed: int = 42):
    """Executa e imprime um trace detalhado de uma partida inteira."""
    print("=" * 80)
    print(f" TRACE DETALHADO DE UMA PARTIDA COM PERFIL: {profile.value} (Seed={seed})")
    print("=" * 80)

    rng = random.Random(seed)
    deck = DeckManager(seed=seed)

    roles = [Role.BANKER, Role.BANKER, Role.BANKER, Role.INTERN, Role.INTERN]
    rng.shuffle(roles)

    print("\n[SETUP DA MESA]")
    for i in range(5):
        print(f"  Jogador P{i}: {roles[i].value}")

    hands = {i: deck.draw(3) for i in range(5)}
    for i in range(5):
        c_str = ", ".join([c.value for c in hands[i]])
        print(f"  Mão Inicial P{i}: [{c_str}]")

    tracker = TableDeductionTracker()
    banker_score = 0
    intern_score = 0
    curr_chair = 0

    ops = [rng.choice(CONTRACT_CATALOG[t]) for t in range(1, 6)]

    for r_idx, op in enumerate(ops):
        r_num = r_idx + 1
        print(f"\n" + "-" * 80)
        print(f"--- RODADA {r_num} (Tier {op.tier}): {op.name.upper()} ---")
        rec_str = ", ".join([f"{cnt}x {card.value}" for card, cnt in op.get_recipe_counter().items() if cnt > 0])
        print(f"Requisitos: Comitê de {op.committee_size} membros | {op.cost_per_player} carta(s) cada | Receita: [{rec_str}]")

        # Compra
        for i in range(5):
            drawn = deck.draw(1)[0]
            hands[i].append(drawn)

        # Proposição de Comitê
        chair = curr_chair
        print(f"Chairman da Rodada: P{chair} ({roles[chair].value})")

        # Escolha de Comitê inteligente
        if roles[chair] == Role.BANKER:
            # Banqueiro escolhe a si mesmo + jogadores com menor probabilidade de serem traidores
            # baseado nos pares suspeitos
            sus_scores = {i: 0 for i in range(5)}
            for pair in tracker.suspect_pairs:
                sus_scores[pair[0]] += 1
                sus_scores[pair[1]] += 1

            cands = [i for i in range(5) if i != chair and i not in tracker.confirmed_traitors]
            cands.sort(key=lambda p: sus_scores[p])
            comm = [chair] + cands[:op.committee_size - 1]
        else:
            # Estagiário
            others = [i for i in range(5) if i != chair]
            rng.shuffle(others)
            comm = [chair] + others[:op.committee_size - 1]

        comm_str = ", ".join([f"P{p} ({roles[p].value})" for p in comm])
        print(f"Comitê Proposto: [{comm_str}]")

        # Votação
        votes = []
        for i in range(5):
            if roles[i] == Role.BANKER:
                # Vota NÃO se souber que tem traidor confirmado
                has_traitor = any(p in tracker.confirmed_traitors for p in comm)
                votes.append(not has_traitor)
            else:
                votes.append(True)

        v_sim = sum(1 for v in votes if v)
        print(f"Votação: {v_sim} SIM vs {5 - v_sim} NÃO -> Comitê {'APROVADO' if v_sim >= 3 else 'VETADO'}")

        # Hold fora do comitê
        for i in range(5):
            if i not in comm:
                counts = Counter(hands[i])
                for c, cnt in counts.items():
                    if c != Card.WILD and cnt >= 2:
                        hands[i].remove(c)
                        hands[i].remove(c)
                        hands[i].append(Card.WILD)
                        print(f"  [Hold] P{i} ({roles[i].value}) converteu 2x {c.value} em 1x Coringa!")
                        break

        # Envio de cartas
        submitted = []
        for p in comm:
            cost = op.cost_per_player
            # Se for Banqueiro: entrega a melhor combinação
            if roles[p] == Role.BANKER:
                # Pega as cartas mais adequadas
                p_sub = hands[p][:cost]
                for c in p_sub:
                    hands[p].remove(c)
                submitted.extend(p_sub)
                print(f"  P{p} (Banqueiro) jogou secretamente: {[c.value for c in p_sub]}")
            else:
                # Estagiário
                if profile == InternProfile.A_AGGRESSIVE or (profile == InternProfile.B_SLEEPER and r_num >= 3):
                    # Sabota jogando lixo
                    junks = [c for c in hands[p] if c in (Card.CO, Card.VN)]
                    p_sub = junks[:cost] if len(junks) >= cost else hands[p][:cost]
                    for c in p_sub:
                        hands[p].remove(c)
                    submitted.extend(p_sub)
                    print(f"  P{p} (Estagiário - Sabotando) jogou secretamente: {[c.value for c in p_sub]}")
                else:
                    # Sleeper coopera
                    p_sub = hands[p][:cost]
                    for c in p_sub:
                        hands[p].remove(c)
                    submitted.extend(p_sub)
                    print(f"  P{p} (Estagiário - Camuflado) jogou secretamente: {[c.value for c in p_sub]}")

        # Auditoria
        is_comp, defs = evaluate_recipe(submitted, op)
        sub_str = ", ".join([c.value for c in submitted])
        print(f"Cartas Abertas na Mesa: [{sub_str}]")

        if is_comp:
            banker_score += 1
            print(f"Resultado: SUCESSO! A receita foi cumprida com conformidade. Placar: Banqueiros {banker_score} x {intern_score} Estagiários")
        else:
            intern_score += 1
            def_str = ", ".join([f"{cnt}x {card.value}" for card, cnt in defs.items()])
            print(f"Resultado: FALHA POR INCONFORMIDADE! Faltou: [{def_str}]. Placar: Banqueiros {banker_score} x {intern_score} Estagiários")
            tracker.register_mission_failure(comm, r_num)
            print(f"  [Dedução] Pares de Traidores Possíveis Restantes: {len(tracker.suspect_pairs)}")
            if tracker.confirmed_traitors:
                print(f"  [Dedução] Traidores 100% Confirmados pela Mesa: {[f'P{p}' for p in tracker.confirmed_traitors]}")

        if banker_score >= 3:
            print("\n" + "=" * 80)
            print(f" FIM DE JOGO: VITÓRIA DOS BANQUEIROS POR 3 A {intern_score}! ")
            print("=" * 80)
            return
        elif intern_score >= 3:
            print("\n" + "=" * 80)
            print(f" FIM DE JOGO: VITÓRIA DOS ESTAGIÁRIOS POR 3 A {banker_score}! ")
            print("=" * 80)
            return

        curr_chair = (curr_chair + 1) % 5

if __name__ == '__main__':
    # Roda traces de exemplo
    trace_sample_game(InternProfile.A_AGGRESSIVE, seed=101)
    trace_sample_game(InternProfile.A_AGGRESSIVE, seed=202)
