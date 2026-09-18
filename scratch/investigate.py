# -*- coding: utf-8 -*-
"""
Script de Investigacao: Por que req_commodity_count = 3 causou colapso do Win Rate do Banco?
"""
import sys
import os
import random
from collections import Counter

# Adiciona diretorio raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.btg import Role, InternProfile, BankerProfile, simulate_single_match
from src.btg.constants import CardType

def run_diagnostic(n_games=1000):
    print(f"Executando diagnostico com {n_games} partidas com trace detalhado...")

    t3_stats = {
        'total': 0,
        # Distribuicao de comite
        'pure_banker': 0,
        'pure_banker_win': 0,
        'pure_banker_fail_insumo': 0,
        'pure_banker_fail_val': 0,

        'one_intern': 0,
        'one_intern_win': 0,
        'one_intern_fail_insumo': 0,
        'one_intern_fail_val': 0,

        'two_intern': 0,
        'two_intern_win': 0,
        'two_intern_fail_insumo': 0,

        # Declaracoes e Maos no Tier 3
        'bankers_with_req': [], # quantos dos 3 banqueiros tinham a carta
        'interns_claiming_req': [], # quantos dos 2 estagiarios alegaram ter a carta
        'forced_committees_t3': 0,
    }

    t4_stats = {
        'total': 0,
        'pure_banker': 0,
        'pure_banker_win': 0,
        'one_intern': 0,
        'one_intern_win': 0,
        'one_intern_fail_insumo': 0,
    }

    banker_wins = 0

    for g_idx in range(n_games):
        seed = 100000 + g_idx
        # Perfil aleatorio
        res = simulate_single_match(g_idx, seed=seed, record_trace=True)
        if res['winner'] == 'Banqueiro':
            banker_wins += 1

        players_meta = {p['id']: p for p in res['players_metadata']}
        banker_ids = [p['id'] for p in res['players_metadata'] if p['role'] == Role.BANKER.value]
        intern_ids = [p['id'] for p in res['players_metadata'] if p['role'] == Role.INTERN.value]

        for r in res['rounds_data']:
            tier = r['contract']['tier']
            comm = r['committee']
            is_success = r['is_success']
            has_req = r['has_req']
            total_val = r['total_value']
            target_val = r['contract']['target']
            req_comm = r['contract']['req_commodity']
            req_cnt = r['contract']['req_count']

            num_interns = sum(1 for pid in comm if pid in intern_ids)

            if tier == 3:
                t3_stats['total'] += 1
                
                # Checar maos antes da rodada 3
                hands_before = r['hands_before']
                # Quantos banqueiros tinham o insumo (ou WILD)?
                b_with_req = 0
                for bid in banker_ids:
                    hand = hands_before.get(bid, [])
                    if any(req_comm in c or 'Ouro' in c or 'WILD' in c for c in hand):
                        b_with_req += 1
                t3_stats['bankers_with_req'].append(b_with_req)

                # Quantos estagiarios declararam claims_req?
                decls = r['declarations']
                i_claims = sum(1 for iid in intern_ids if decls[iid]['claims_req'])
                t3_stats['interns_claiming_req'].append(i_claims)

                if num_interns == 0:
                    t3_stats['pure_banker'] += 1
                    if is_success:
                        t3_stats['pure_banker_win'] += 1
                    elif not has_req:
                        t3_stats['pure_banker_fail_insumo'] += 1
                    else:
                        t3_stats['pure_banker_fail_val'] += 1
                elif num_interns == 1:
                    t3_stats['one_intern'] += 1
                    if is_success:
                        t3_stats['one_intern_win'] += 1
                    elif not has_req:
                        t3_stats['one_intern_fail_insumo'] += 1
                    else:
                        t3_stats['one_intern_fail_val'] += 1
                else:
                    t3_stats['two_intern'] += 1
                    if is_success:
                        t3_stats['two_intern_win'] += 1
                    elif not has_req:
                        t3_stats['two_intern_fail_insumo'] += 1

            elif tier == 4:
                t4_stats['total'] += 1
                if num_interns == 0:
                    t4_stats['pure_banker'] += 1
                    if is_success:
                        t4_stats['pure_banker_win'] += 1
                elif num_interns == 1:
                    t4_stats['one_intern'] += 1
                    if is_success:
                        t4_stats['one_intern_win'] += 1
                    elif not has_req:
                        t4_stats['one_intern_fail_insumo'] += 1

    print("\n" + "="*70)
    print(f"DIAGNOSTICO CONCLUIDO ({n_games} partidas):")
    print(f"  Win Rate Global dos Banqueiros: {banker_wins / n_games * 100:.2f}%")
    print("="*70)
    
    tot3 = t3_stats['total']
    pb3 = t3_stats['pure_banker']
    oi3 = t3_stats['one_intern']
    ti3 = t3_stats['two_intern']
    
    print("\n1. DISSECAÇÃO DO TIER 3 (3 membros, 1 carta/membro, meta=6, req_count=3):")
    print(f"  Total disputado: {tot3}")
    print(f"  -> Quantos Banqueiros (dos 3 no jogo) tinham o insumo requerido na mão?")
    b_counts = Counter(t3_stats['bankers_with_req'])
    for k in sorted(b_counts.keys()):
        print(f"     * {k} banqueiro(s) tinham o insumo: {b_counts[k]} vezes ({b_counts[k]/tot3*100:.1f}%)")
    
    print(f"  -> Quantos Estagiarios (dos 2 no jogo) declararam claims_req?")
    i_counts = Counter(t3_stats['interns_claiming_req'])
    for k in sorted(i_counts.keys()):
        print(f"     * {k} estagiario(s) declararam claims_req: {i_counts[k]} vezes ({i_counts[k]/tot3*100:.1f}%)")

    print(f"\n  COMPOSIÇÃO DO COMITÊ NO TIER 3:")
    print(f"  A) Comitê Puro Banqueiro (3 Banqueiros, 0 Estagiários): {pb3} vezes ({pb3/tot3*100:.1f}%)")
    if pb3 > 0:
        print(f"     - Taxa de Sucesso: {t3_stats['pure_banker_win']/pb3*100:.1f}%")
        print(f"     - Falhas por Insumo (mesmo sem traidor!): {t3_stats['pure_banker_fail_insumo']/pb3*100:.1f}% ({t3_stats['pure_banker_fail_insumo']}/{pb3})")
        print(f"     - Falhas por Valor: {t3_stats['pure_banker_fail_val']/pb3*100:.1f}%")

    print(f"  B) Comitê com 1 Estagiário (2 Banqueiros, 1 Estagiário): {oi3} vezes ({oi3/tot3*100:.1f}%)")
    if oi3 > 0:
        print(f"     - Taxa de Sucesso: {t3_stats['one_intern_win']/oi3*100:.1f}%")
        print(f"     - Falhas por Insumo: {t3_stats['one_intern_fail_insumo']/oi3*100:.1f}% ({t3_stats['one_intern_fail_insumo']}/{oi3})")
        print(f"     - Falhas por Valor: {t3_stats['one_intern_fail_val']/oi3*100:.1f}%")

    print(f"  C) Comitê com 2 Estagiários: {ti3} vezes ({ti3/tot3*100:.1f}%)")
    if ti3 > 0:
        print(f"     - Taxa de Sucesso: {t3_stats['two_intern_win']/ti3*100:.1f}%")
        print(f"     - Falhas por Insumo: {t3_stats['two_intern_fail_insumo']/ti3*100:.1f}%")

    print("\n2. DISSECAÇÃO DO TIER 4 (3 membros, 1 carta/membro, meta=7-8, req_count=3):")
    tot4 = t4_stats['total']
    pb4 = t4_stats['pure_banker']
    oi4 = t4_stats['one_intern']
    print(f"  Total disputado: {tot4}")
    print(f"  A) Puro Banqueiro: {pb4} ({pb4/tot4*100:.1f}%) | Sucesso: {t4_stats['pure_banker_win']/pb4*100:.1f}%" if pb4 else "  A) Puro: 0")
    print(f"  B) Com 1 Estagiário: {oi4} ({oi4/tot4*100:.1f}%) | Sucesso: {t4_stats['one_intern_win']/oi4*100:.1f}% | Falha Insumo: {t4_stats['one_intern_fail_insumo']/oi4*100:.1f}%" if oi4 else "  B) Com 1 Estag: 0")

if __name__ == '__main__':
    run_diagnostic(1000)
