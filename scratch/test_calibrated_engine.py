import sys, os
sys.path.insert(0, os.path.abspath('.'))
import numpy as np
import itertools
from src.btg import Role, BankerProfile, InternProfile
from src.btg.constants import CardType, ContractSpec, SEVEN_TIERS_CATALOG
from src.btg.deck import DeckManager, ResourceCard
from src.btg.player import PlayerAI, PlayerDeclaration
import src.btg.engine as engine_module

# Test the calibrated changes
print("Rodando bateria de teste para comparar...")
