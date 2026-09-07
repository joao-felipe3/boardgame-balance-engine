# -*- coding: utf-8 -*-
"""
BTG Madagascar - Core Package
"""

from .constants import (
    CardType,
    CARD_BASE_VALUES,
    INITIAL_COMMERCIAL_DECK,
    Role,
    BankerProfile,
    InternProfile,
    ContractSpec,
    SEVEN_TIERS_CATALOG
)
from .deck import ResourceCard, DeckManager
from .player import PlayerAI, PlayerDeclaration
from .engine import (
    evaluate_contract_outcome,
    choose_optimal_committee,
    coordinate_committee_contributions,
    simulate_single_match
)

__all__ = [
    'CardType',
    'CARD_BASE_VALUES',
    'INITIAL_COMMERCIAL_DECK',
    'Role',
    'BankerProfile',
    'InternProfile',
    'ContractSpec',
    'SEVEN_TIERS_CATALOG',
    'ResourceCard',
    'DeckManager',
    'PlayerAI',
    'PlayerDeclaration',
    'evaluate_contract_outcome',
    'choose_optimal_committee',
    'coordinate_committee_contributions',
    'simulate_single_match'
]
