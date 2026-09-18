import sys, os
sys.path.insert(0, os.path.abspath('.'))
import numpy as np
import itertools
from src.btg import Role, BankerProfile, InternProfile
from src.btg.constants import CardType, ContractSpec, SEVEN_TIERS_CATALOG
from src.btg.deck import DeckManager, ResourceCard
from src.btg.player import PlayerAI, PlayerDeclaration
import src.btg.engine as engine_module

# Let's inspect simulate_single_match by overriding the post-mission failure logic in a modified runner
# To be 100% clean, let's copy simulate_single_match into test_root_cause_fix.py with our 5 fixes applied:

print("Testando...")
