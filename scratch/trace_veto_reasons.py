import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from collections import Counter
from src.btg import simulate_single_match, Role

# Vamos rastrear porque os vetos acontecem
# Podemos instrumentar temporariamente ou checar via simulação
print("Rastreando motivos de vetos...")
