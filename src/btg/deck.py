# -*- coding: utf-8 -*-
"""
BTG Madagascar - Gerenciador de Baralho, Cartas e Mercado de Balcão Aberto
"""

import random
from typing import List, Optional
from dataclasses import dataclass
from .constants import CardType, CARD_BASE_VALUES, INITIAL_COMMERCIAL_DECK


@dataclass
class ResourceCard:
    card_type: CardType

    @property
    def base_value(self) -> int:
        return CARD_BASE_VALUES[self.card_type]

    def __repr__(self):
        return f"{self.card_type.name}(base={self.base_value})"


class DeckManager:
    __slots__ = ('draw_pile', 'discard_pile', 'open_market', 'rng')

    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
        self.draw_pile: List[CardType] = INITIAL_COMMERCIAL_DECK.copy()
        self.rng.shuffle(self.draw_pile)
        self.discard_pile: List[CardType] = []
        self.open_market: List[CardType] = []

    def refill_open_market(self, target_size: int = 3):
        """Mantém sempre 3 cartas abertas no Mercado de Balcão."""
        while len(self.open_market) < target_size:
            drawn = self.draw_blind(1)
            if drawn:
                self.open_market.append(drawn[0].card_type)
            else:
                break

    def draw_blind(self, n: int = 1) -> List[ResourceCard]:
        """Compra secreta/anônima do topo do baralho."""
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
        """Compra pública do Mercado de Balcão Aberto."""
        if card_type in self.open_market:
            self.open_market.remove(card_type)
            self.refill_open_market()
            return ResourceCard(card_type)
        return self.draw_blind(1)[0]

    def discard(self, cards: List[ResourceCard]):
        """Descarta cartas jogadas."""
        self.discard_pile.extend([c.card_type for c in cards])
