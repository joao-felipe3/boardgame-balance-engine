# -*- coding: utf-8 -*-
"""
Experimento: O que acontece se os Banqueiros fizerem Gestao Cooperativa de Carteira
(economizando recursos nobres e evitando overkill desnecessario)?
"""
import sys
import os
import random
import itertools
import numpy as np
from collections import defaultdict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import src.btg.player as player_mod
import src.btg.engine as engine_mod
from src.btg import Role, simulate_single_match, BankerProfile, InternProfile
from src.btg.constants import CardType

# Vamos criar uma versao inteligente de plan_honest_contribution que:
# 1. NUNCA despeja recursos cegamente se a meta ja esta coberta com folga.
# 2. Poupa Safiras e Titanios para os Tiers 6 e 7 sempre que cartas menores forem suficientes.
# 3. Nao gasta tokens de rendimento alem de uma margem segura de +1 ou +2 pts.

orig_plan_honest = player_mod.PlayerAI.plan_honest_contribution

def smart_cooperative_plan_honest(self, contract, round_num, is_responsible_for_req, quota_needed, is_match_point=False):
    cost = contract.cost_per_player
    pos_cards = [c for c in self.hand if c.card_type != CardType.TOXIC]
    if not pos_cards:
        return self.hand[:cost], 0, sum(c.base_value for c in self.hand[:cost])

    valid_combos = list(itertools.combinations(pos_cards, cost))
    if not valid_combos:
        valid_combos = list(itertools.combinations(self.hand, cost))
    if not valid_combos:
        return self.hand[:cost], 0, sum(c.base_value for c in self.hand[:cost])

    # Se responsavel por insumo, filtra combos que contenham o insumo
    if is_responsible_for_req and contract.req_commodity is not None:
        req_combos = [cb for cb in valid_combos if any(c.card_type in (contract.req_commodity, CardType.WILD) for c in cb)]
        if req_combos:
            valid_combos = req_combos

    # Nos Tiers 6 e 7 (onde o custo e 2 cartas e meta e pesada), joga o melhor combo
    if contract.tier >= 6:
        best_combo = max(valid_combos, key=lambda cb: sum(c.base_value for c in cb))
        needed_tok = max(0, int(np.ceil(quota_needed - sum(c.base_value for c in best_combo))))
        best_tokens = min(self.interest_tokens, needed_tok if not is_match_point else self.interest_tokens)
        return list(best_combo), best_tokens, sum(c.base_value for c in best_combo) + best_tokens

    # Nos Tiers 1 a 5: Gestao Cooperativa e Poupanca Ativa de Recursos Nobres!
    best_combo = None
    best_tokens = 0
    best_val = -999
    best_score = (9999, 9999, 9999, 9999)

    # Margem de seguranca prudente contra sabotador (se match-point, quer +2 de folga; senao quer bater a meta exata)
    safety_margin = 2 if is_match_point else (1 if round_num >= 3 else 0)
    target_for_p = max(cost, quota_needed + safety_margin)

    for cb in valid_combos:
        base_v = sum(c.base_value for c in cb)
        needed_tokens = max(0, int(np.ceil(target_for_p - base_v)))
        tokens_to_use = min(self.interest_tokens, needed_tokens)
        total_v = base_v + tokens_to_use

        # Penalidade para preservar Safiras e Wilds para o Tier 6/7
        has_safira = any(c.card_type in (CardType.SF, CardType.WILD) for c in cb)
        safira_penalty = 15 if (has_safira and contract.req_commodity != CardType.SF and contract.tier < 6) else 0

        # Penalidade para preservar Titanio se nao for o insumo exigido
        has_titanio = any(c.card_type == CardType.TI for c in cb)
        titanio_penalty = 8 if (has_titanio and not is_responsible_for_req and contract.req_commodity != CardType.TI and contract.tier < 5) else 0

        # Penalidade por gastar tokens desnecessarios
        token_penalty = tokens_to_use * 2

        # Avaliacao de adequacao a cota
        if total_v >= quota_needed:
            # Bateu a cota necessaria! Menor desperdicio (overkill) e menor queima de nobres
            overkill = total_v - quota_needed
            score = (0, safira_penalty + titanio_penalty, token_penalty, overkill)
        else:
            # Nao bateu a cota: tenta chegar o mais perto possivel gastando o minimo
            deficit = quota_needed - total_v
            score = (1, deficit, safira_penalty + titanio_penalty, -total_v)

        if best_combo is None or score < best_score:
            best_combo = cb
            best_tokens = tokens_to_use
            best_val = total_v
            best_score = score

    return list(best_combo), best_tokens, best_val

def test_economic_coordination(n_games=2000):
    print(f"Testando Gestao Cooperativa de Carteira em {n_games} partidas...")
    
    # 1. Baseline Atual
    wins_base = 0
    for i in range(n_games):
        res = simulate_single_match(i, seed=800000+i, record_trace=False)
        if res['winner'] == 'Banqueiro':
            wins_base += 1
    wr_base = wins_base / n_games * 100
    print(f"1. Baseline Atual: {wr_base:.2f}% Win Rate Banco")

    # 2. Com Gestao Cooperativa de Carteira (Poupanca de Nobres e Controle de Overkill)
    player_mod.PlayerAI.plan_honest_contribution = smart_cooperative_plan_honest
    wins_smart = 0
    for i in range(n_games):
        res = simulate_single_match(i, seed=800000+i, record_trace=False)
        if res['winner'] == 'Banqueiro':
            wins_smart += 1
    wr_smart = wins_smart / n_games * 100
    print(f"2. Com Gestao Cooperativa de Carteira: {wr_smart:.2f}% Win Rate Banco")
    print(f"-> Impacto da Poupanca Economica: {wr_smart - wr_base:+.2f} p.p.!")
    
    # Restaura
    player_mod.PlayerAI.plan_honest_contribution = orig_plan_honest

if __name__ == '__main__':
    test_economic_coordination(2000)
