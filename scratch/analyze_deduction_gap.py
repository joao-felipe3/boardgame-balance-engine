# -*- coding: utf-8 -*-
"""
Script de Analise: Comparando a Deducao da Simulacao vs Deducao Humana Real
Mede:
1. Quantas vezes um Banqueiro sabe quem e o traidor, mas a informacao fica "presa" e outro Banqueiro convoca o traidor?
2. Quantas vezes ha quebra de promessa de insumo/valor que humanos deduziriam instantaneamente, mas os bots tratam como suspeita generica?
3. Qual o impacto no Win Rate se os banqueiros se comunicassem como humanos?
"""
import sys
import os
import random
from collections import Counter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.btg import Role, InternProfile, BankerProfile, simulate_single_match
from src.btg.constants import CardType

def analyze_information_leak_and_deduction(n_games=1000):
    print(f"Analisando {n_games} partidas para mapear o gap de deducao (Simulacao vs Jogo Real)...")
    
    stats = {
        'total_games': n_games,
        'traitor_reinvited_by_clean_banker': 0, # Banqueiro limpo chamou traidor que OUTRO banqueiro ja sabia que era traidor
        'total_invitations_after_discovery': 0,
        'v14_failures_with_exact_promise_break': 0, # Quebra obvia de promessa de insumo
        'human_deducible_traitors': 0, # Casos onde mesa humana deduziria 100% mas a simulacao manteve sus < 0.99
    }

    for g_idx in range(n_games):
        seed = 200000 + g_idx
        res = simulate_single_match(g_idx, seed=seed, record_trace=True)
        banker_ids = [p['id'] for p in res['players_metadata'] if p['role'] == Role.BANKER.value]
        intern_ids = [p['id'] for p in res['players_metadata'] if p['role'] == Role.INTERN.value]
        
        # Rastreia o que cada banqueiro sabia rodada a rodada
        # Em cada rodada, verificamos se o Chairman (se for banqueiro) convocou alguem que OUTRO banqueiro ja conhecia como traidor
        for r_idx, r in enumerate(res['rounds_data']):
            chair_id = r['chair_id']
            comm = r['committee']
            sus_data = r['suspicions']
            known_dict = sus_data.get('known_traitors', {})
            
            # Uniao dos traidores conhecidos por QUALQUER banqueiro ate o fim da rodada anterior
            # (informacao que em mesa humana e falada publicamente)
            if chair_id in banker_ids and r_idx > 0:
                prev_r = res['rounds_data'][r_idx - 1]
                prev_known = prev_r['suspicions'].get('known_traitors', {})
                all_known_by_any_banker = set()
                for bid, kset in prev_known.items():
                    all_known_by_any_banker.update(kset)
                
                chair_own_known = set(prev_known.get(chair_id, []))
                
                # Traidores que OUTRO banqueiro conhecia, mas o chair nao tinha marcado individualmente
                blind_spots = all_known_by_any_banker - chair_own_known
                for cid in comm:
                    if cid in blind_spots:
                        stats['traitor_reinvited_by_clean_banker'] += 1
                        break
                        
            # Verifica quebra de promessa nesta rodada
            decls = r['declarations']
            has_req = r['has_req']
            is_success = r['is_success']
            req_comm = r['contract']['req_commodity']
            req_cnt = r['contract']['req_count']
            
            if not is_success and not has_req and req_comm is not None:
                # Insumo prometido faltou
                promisers = [pid for pid, d in decls.items() if pid in comm and d['claims_req']]
                if len(promisers) == req_cnt:
                    # Exatamente os que prometeram foram convocados e faltou!
                    # Na mesa real, o banqueiro honesto entre eles SABE quem e o sabotador com 100%
                    stats['v14_failures_with_exact_promise_break'] += 1

    print("\n" + "="*70)
    print("RELATÓRIO DO GAP DE DEDUÇÃO (HUMANO REAL VS SIMULAÇÃO):")
    print("="*70)
    print(f"1. EFEITO 'FALTA DE COMUNICAÇÃO ENTRE BANQUEIROS':")
    print(f"   Quantas vezes um Chairman Banqueiro convocou um Estagiário que OUTRO Banqueiro")
    print(f"   já sabia com 100% de certeza que era traidor:")
    print(f"   -> {stats['traitor_reinvited_by_clean_banker']} partidas ({stats['traitor_reinvited_by_clean_banker']/n_games*100:.1f}% das partidas!)")
    print("\n2. QUEBRA DETERMINÍSTICA DE PROMESSAS DE INSUMO:")
    print(f"   Missões onde o insumo faltou exatamente após promessas diretas:")
    print(f"   -> {stats['v14_failures_with_exact_promise_break']} ocorrências")
    print("="*70)

if __name__ == '__main__':
    analyze_information_leak_and_deduction(1000)
