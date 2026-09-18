# -*- coding: utf-8 -*-
"""
Script de Analise de Overkill e Queima Prematura de Recursos Nobres
Mede:
1. Qual o total de valor jogado no cofre vs o target da missao em comites puros.
2. Quantas Safiras e Titanios sao queimados prematuramente quando cartas menores bastariam.
3. Quantos tokens de rendimento sao gastos em overkill (desperdicados).
"""
import sys
import os
import random
from collections import Counter, defaultdict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.btg import Role, simulate_single_match
from src.btg.constants import CardType

def measure_overkill(n_games=1000):
    print(f"Medindo desperdicio (overkill) e queima de recursos em {n_games} partidas...")
    
    overkill_by_tier = defaultdict(list)
    tokens_wasted_by_tier = defaultdict(list)
    nobles_burned_in_overkill = defaultdict(int) # Safiras e Wilds jogados quando sobrava valor >= 4

    for g_idx in range(n_games):
        res = simulate_single_match(g_idx, seed=700000 + g_idx, record_trace=True)
        banker_ids = [p['id'] for p in res['players_metadata'] if p['role'] == Role.BANKER.value]
        
        for r in res['rounds_data']:
            tier = r['contract']['tier']
            target = r['contract']['target']
            comm = r['committee']
            total_val = r['total_value']
            tokens_spent = r['total_tokens_spent']
            submitted = r['submitted']
            
            # Analisa apenas comites 100% banqueiros
            if all(pid in banker_ids for pid in comm) and r['is_success']:
                margin = total_val - target
                overkill_by_tier[tier].append(margin)
                
                # Se a margem foi maior que os tokens gastos, os tokens foram desperdicados!
                wasted_tok = min(tokens_spent, margin)
                tokens_wasted_by_tier[tier].append(wasted_tok)
                
                # Checar se foram jogadas Safiras ou Wilds que nao eram necessarias
                all_cards = [c for sub in submitted for c in sub['cards']]
                nobles = [c for c in all_cards if c['type'] in ('SF', 'WILD', 'Safira', 'Ouro Liquido')]
                
                # Se a margem de folga foi >= 3, significa que um nobre (+4) ou titanio (+3)
                # poderia ter sido substitudo por um Cobalto (+1) economizando recurso!
                if margin >= 3 and len(nobles) > 0:
                    nobles_burned_in_overkill[tier] += len(nobles)

    print("\n" + "="*80)
    print("ANALISE DE OVERKILL E DESPERDÍCIO DE RECURSOS NOBRES (COMITÊS PUROS)")
    print("="*80)
    print("Tier | Comitês Puros Vencedores | Margem Média (Overkill) | Tokens Desperdiçados Médios | Nobres Queimados s/ Necessidade")
    print("-------------------------------------------------------------------------------------------------------------------------")
    for t in sorted(overkill_by_tier.keys()):
        margins = overkill_by_tier[t]
        n_wins = len(margins)
        avg_margin = sum(margins) / n_wins if n_wins else 0
        wasted_toks = tokens_wasted_by_tier[t]
        avg_wasted_tok = sum(wasted_toks) / n_wins if n_wins else 0
        burned = nobles_burned_in_overkill[t]
        print(f"T{t:02d} | {n_wins:24d} | +{avg_margin:20.2f} pts | {avg_wasted_tok:26.2f} tokens | {burned:30d} cartas")

if __name__ == '__main__':
    measure_overkill(1000)
