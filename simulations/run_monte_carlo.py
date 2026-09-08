# -*- coding: utf-8 -*-
"""
BTG Madagascar - Simulador Monte Carlo Massivo em Alta Performance
===================================================================
Executa simulações paralelas (100.000+ partidas) e compila telemetria
multidimensional detalhada sobre o andamento e a dinâmica dos jogos.
"""

import sys
import os
import time
import random
import argparse
from typing import List, Dict, Tuple, Optional
from collections import Counter
import multiprocessing as mp
import numpy as np
import pandas as pd

# Garante acesso aos módulos do projeto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

from src.btg import Role, InternProfile, BankerProfile, simulate_single_match


def _worker_simulate_chunk(args: Tuple) -> List[Dict]:
    """Executa um lote (chunk) de partidas em um processo trabalhador com suporte a múltiplos perfis e DLC."""
    start_idx, count, seed_base, banker_prof_opt, intern_prof_opt, enable_directives, directive_regime = args
    all_intern_profs = list(InternProfile)
    all_banker_profs = list(BankerProfile)
    chunk_results = []
    for i in range(count):
        game_idx = start_idx + i
        rng = random.Random(seed_base + game_idx)

        # Perfil do estagiário
        if intern_prof_opt is None or intern_prof_opt in ('all', 'random'):
            i_prof = rng.choice(all_intern_profs)
        elif intern_prof_opt.lower() == 'mixed':
            i_prof = 'MIXED'
        else:
            i_prof = intern_prof_opt

        # Perfil do banqueiro
        if banker_prof_opt is None or banker_prof_opt in ('all', 'random'):
            b_prof = rng.choice(all_banker_profs)
        elif banker_prof_opt.lower() == 'mixed':
            b_prof = 'MIXED'
        else:
            b_prof = banker_prof_opt

        res = simulate_single_match(
            game_idx,
            seed=seed_base + game_idx,
            record_trace=False,
            banker_profile=b_prof,
            intern_profile=i_prof,
            enable_directives=enable_directives,
            directive_regime=directive_regime
        )
        chunk_results.append(res)
    return chunk_results


def run_monte_carlo(
    n_games: int = 100000,
    seed_base: int = 420000,
    num_workers: Optional[int] = None,
    export_json: Optional[str] = None,
    banker_profile: Optional[str] = None,
    intern_profile: Optional[str] = None,
    enable_directives: bool = False,
    directive_regime: str = "DICE_50"
) -> pd.DataFrame:
    """Executa simulação Monte Carlo massiva paralelizada com telemetria rica."""
    if num_workers is None:
        num_workers = max(1, os.cpu_count() or 4)

    print("=" * 84)
    dlc_status = f" | DLC ATIVA ({directive_regime})" if enable_directives else ""
    print(f"       SIMULADOR MONTE CARLO MASSIVO - BTG MADAGASCAR v14.0 ({n_games:,} JOGOS){dlc_status}")
    print(f"       Processamento Paralelo: {num_workers} workers multinúcleo")
    if banker_profile or intern_profile:
        print(f"       Perfis: Banqueiro = {banker_profile or 'Aleatório/Todos'} | Estagiário = {intern_profile or 'Aleatório/Todos'}")
    print("=" * 84)

    t0 = time.time()

    # Divide a carga de trabalho em chunks balanceados
    chunk_size = max(500, n_games // (num_workers * 8))
    tasks = []
    curr = 0
    while curr < n_games:
        count = min(chunk_size, n_games - curr)
        tasks.append((curr, count, seed_base, banker_profile, intern_profile, enable_directives, directive_regime))
        curr += count

    results = []
    completed = 0
    last_print = t0

    with mp.Pool(processes=num_workers) as pool:
        for chunk in pool.imap_unordered(_worker_simulate_chunk, tasks):
            results.extend(chunk)
            completed += len(chunk)
            now = time.time()
            if (completed == n_games) or (now - last_print >= 2.0):
                pct = completed / n_games * 100
                elapsed = now - t0
                rate = completed / max(0.001, elapsed)
                eta = (n_games - completed) / max(0.001, rate)
                print(f"   [Progresso] {completed:8,d} / {n_games:,} ({pct:5.1f}%) | "
                      f"Velocidade: {rate:6.0f} jogos/s | Tempo: {elapsed:4.1f}s (ETA: {eta:3.0f}s)")
                sys.stdout.flush()
                last_print = now

    total_time = time.time() - t0
    print(f"\n   Simulação concluída em {total_time:.2f}s ({n_games / max(0.001, total_time):.0f} partidas/segundo)")

    # Compilação e Análise Estatística
    df = pd.DataFrame(results)
    df["score"] = df["b_score"].astype(str) + " x " + df["i_score"].astype(str)

    b_wins = (df["winner"] == Role.BANKER.value).sum()
    i_wins = (df["winner"] == Role.INTERN.value).sum()
    b_pct = (b_wins / n_games) * 100
    i_pct = (i_wins / n_games) * 100

    # -------------------------------------------------------------------------
    # 1. RELATÓRIO DE EQUILÍBRIO GLOBAL & PLACARES
    # -------------------------------------------------------------------------
    print("\n" + "=" * 84)
    print(" 1. EQUILÍBRIO GLOBAL & MATRIZ DE PLACARES")
    print("=" * 84)
    print(f"  * Banqueiros  : {b_pct:6.2f}% ({b_wins:,} vitórias)")
    print(f"  * Estagiários : {i_pct:6.2f}% ({i_wins:,} vitórias)")
    print(f"  * Gap Global  : {abs(b_pct - i_pct):5.2f} p.p.")
    print(f"  * Duração     : {df['rounds'].mean():.2f} ± {df['rounds'].std():.2f} rodadas")

    print("\n  DISTRIBUIÇÃO DOS 8 PLACARES POSSÍVEIS (Primeiro a 4 Pontos):")
    print("  " + "-" * 78)
    score_order = ['4 x 0', '4 x 1', '4 x 2', '4 x 3', '3 x 4', '2 x 4', '1 x 4', '0 x 4']
    score_counts = Counter(df["score"])
    
    tags = {
        '4 x 0': '🛡️ Sweep Banqueiros (Lockout / Deteccao Perfeita)',
        '4 x 1': '🎯 Vitoria Solida dos Banqueiros (5 Rodadas)',
        '4 x 2': '⚖️ Disputa Equilibrada (Decisao na 6a Rodada)',
        '4 x 3': '🔥 Climax Epico Banqueiros (Decisao na 7a Rodada)',
        '3 x 4': '🔥 Climax Epico Estagiarios (Decisao na 7a Rodada)',
        '2 x 4': '⚖️ Disputa Equilibrada (Decisao na 6a Rodada)',
        '1 x 4': '🎯 Vitoria Solida dos Estagiarios (5 Rodadas)',
        '0 x 4': '💀 Massacre Estagiarios (Falha de Insumos/Abertura)'
    }

    for sc in score_order:
        cnt = score_counts[sc]
        pct = (cnt / n_games) * 100
        tag = tags.get(sc, '')
        print(f"    {sc:<8} | {cnt:8,d} ({pct:5.2f}%) | {tag}")

    climax_matches = score_counts['4 x 3'] + score_counts['3 x 4']
    deep_matches = climax_matches + score_counts['4 x 2'] + score_counts['2 x 4']
    print("  " + "-" * 78)
    print(f"  * Jogos de Clímax na 7ª Rodada (4x3 e 3x4)   : {climax_matches:8,d} ({(climax_matches/n_games)*100:5.2f}%)")
    print(f"  * Partidas Longas e Disputadas (R6 e R7)     : {deep_matches:8,d} ({(deep_matches/n_games)*100:5.2f}%)")

    # -------------------------------------------------------------------------
    # 2. FUNIL DE OPERAÇÕES & ANDAMENTO POR TIER (1 A 7)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 84)
    print(" 2. FUNIL DE OPERAÇÕES & ANDAMENTO POR TIER (R1 a R7)")
    print("=" * 84)

    tier_stats = {t: {'played': 0, 'success': 0, 'intern_in': 0, 'sab_in': 0,
                      'fail_insumo': 0, 'fail_valor': 0, 'fail_toxico': 0,
                      'tokens_spent': 0} for t in range(1, 8)}

    for row in results:
        t_data = row.get('tier_telemetry', {})
        for r_num, t_info in t_data.items():
            t = t_info['tier']
            tier_stats[t]['played'] += 1
            if t_info['success']:
                tier_stats[t]['success'] += 1
            else:
                fc = t_info.get('fail_cause', 'valor')
                if fc == 'insumo':
                    tier_stats[t]['fail_insumo'] += 1
                elif fc == 'toxico':
                    tier_stats[t]['fail_toxico'] += 1
                else:
                    tier_stats[t]['fail_valor'] += 1

            if t_info.get('intern_count', 0) > 0:
                tier_stats[t]['intern_in'] += 1
            if t_info.get('saboteur_in_comm', False):
                tier_stats[t]['sab_in'] += 1
            tier_stats[t]['tokens_spent'] += t_info.get('tokens_spent', 0)

    print(f"{'Tier':<6} | {'Disputado':<12} | {'Taxa Sucesso':<13} | {'Infiltração':<12} | {'Sabotado se Infiltr.':<22} | {'Causa Falha Predominante':<20}")
    print("-" * 95)
    for t in range(1, 8):
        st = tier_stats[t]
        pl = st['played']
        if pl == 0:
            continue
        suc_pct = (st['success'] / pl) * 100
        inf_pct = (st['intern_in'] / pl) * 100
        sab_eff = ((st['intern_in'] - (st['success'] if st['intern_in'] >= st['success'] else 0)) / max(1, st['intern_in'])) * 100
        fails = pl - st['success']
        if fails > 0:
            c_ins = st['fail_insumo'] / fails * 100
            c_val = st['fail_valor'] / fails * 100
            c_tox = st['fail_toxico'] / fails * 100
            cause_desc = f"Val {c_val:.0f}% / Ins {c_ins:.0f}% / Tox {c_tox:.0f}%"
        else:
            cause_desc = "N/A (100% Sucesso)"

        print(f"Tier {t:<1} | {pl:7,d} ({pl/n_games*100:4.1f}%) | {suc_pct:10.2f}%   | {inf_pct:9.2f}%   | {sab_eff:18.2f}%   | {cause_desc}")

    # -------------------------------------------------------------------------
    # 3. POLÍTICA, GOVERNANÇA & REGRA DE EXPANSÃO (R5)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 84)
    print(" 3. GOVERNANÇA, POLÍTICA DA MESA & REGRA DE EXPANSÃO (R5)")
    print("=" * 84)
    avg_vetoes = df["total_vetoes"].mean()
    games_with_forced = (df["forced_committees"] > 0).sum()
    r5_exp_count = df["r5_expanded"].sum()
    r5_eligible = (df["rounds"] >= 5).sum()

    print(f"  * Média de Vetos por Partida             : {avg_vetoes:.2f} vetos")
    print(f"  * Média de Vetos por Rodada Disputada    : {df['total_vetoes'].sum() / df['rounds'].sum():.2f} vetos/rodada")
    print(f"  * Partidas com Comitê Forçado (3 Vetos)  : {games_with_forced:7,d} ({(games_with_forced/n_games)*100:5.2f}%)")
    print(f"  * Expansão da Rodada 5 para 4 Operadores : {r5_exp_count:7,d} ({(r5_exp_count/max(1, r5_eligible))*100:5.2f}% das partidas que chegam à R5)")

    # -------------------------------------------------------------------------
    # 4. DINÂMICA ECONÔMICA, RENDIMENTOS & TOXICIDADE
    # -------------------------------------------------------------------------
    print("\n" + "=" * 84)
    print(" 4. DINÂMICA ECONÔMICA, RENDIMENTOS & ATIVOS TÓXICOS")
    print("=" * 84)
    avg_tokens = df["total_tokens_spent"].mean()
    total_toxic = df["total_toxic_played"].sum()
    games_with_toxic = (df["total_toxic_played"] > 0).sum()
    avg_hand_end = df["avg_hand_size"].mean()

    print(f"  * Tokens de Rendimento Gastos por Jogo   : {avg_tokens:.2f} tokens")
    print(f"  * Média de Cartas na Mão ao Fim do Jogo  : {avg_hand_end:.2f} cartas/jogador")
    print(f"  * Partidas com Ativo Tóxico Jogado       : {games_with_toxic:7,d} ({(games_with_toxic/n_games)*100:5.2f}%)")
    print(f"  * Total de Cartas Tóxicas Utilizadas     : {total_toxic:7,d} ({total_toxic / max(1, games_with_toxic):.2f} por jogo tóxico)")

    # -------------------------------------------------------------------------
    # 5. DEDUÇÃO SOCIAL, LOCKOUT & DESMASCARAMENTO
    # -------------------------------------------------------------------------
    print("\n" + "=" * 84)
    print(" 5. DEDUÇÃO SOCIAL, LOCKOUT & IDENTIFICAÇÃO DE TRAIDORES")
    print("=" * 84)
    lockout_count = df["intern_lockout"].sum()
    unmasked_avg = df["interns_unmasked"].mean()
    unmasked_both = (df["interns_unmasked"] == 2).sum()
    unmasked_one = (df["interns_unmasked"] == 1).sum()
    avg_int_sus = df["avg_intern_sus"].mean()
    avg_bnk_sus = df["avg_banker_sus"].mean()

    print(f"  * Taxa de Lockout (0 comitês p/ Estagiários) : {lockout_count:7,d} ({(lockout_count/n_games)*100:5.2f}%)")
    print(f"  * Estagiários Desmascarados por Jogo (0 a 2) : {unmasked_avg:.2f} estagiários")
    print(f"    - Ambos Desmascarados (Suspeita 1.0)       : {unmasked_both:7,d} ({(unmasked_both/n_games)*100:5.2f}%)")
    print(f"    - Apenas 1 Desmascarado                   : {unmasked_one:7,d} ({(unmasked_one/n_games)*100:5.2f}%)")
    print(f"    - Nenhum Desmascarado (Camuflagem Total)   : {n_games - unmasked_both - unmasked_one:7,d} ({((n_games - unmasked_both - unmasked_one)/n_games)*100:5.2f}%)")
    print(f"  * Suspeita Média Final Atribuída pelo Banco  :")
    print(f"    - Sobre Estagiários Infiltrados            : {avg_int_sus:.3f} (alta detecção)")
    print(f"    - Sobre Banqueiros Honestos                : {avg_bnk_sus:.3f} (baixo ruído)")

    # -------------------------------------------------------------------------
    # 6. ANÁLISE COMPARATIVA POR PERFIL DE ESTAGIÁRIO
    # -------------------------------------------------------------------------
    print("\n" + "=" * 84)
    print(" 6. COMPARATIVO MULTIDIMENSIONAL POR PERFIL DE ESTAGIÁRIO")
    print("=" * 84)
    print(f"{'Perfil Estagiário':<36} | {'WR Estag':<9} | {'WR Banco':<9} | {'Duração':<8} | {'Lockout':<8} | {'Desmasc.':<9} | {'Placar Top':<10}")
    print("-" * 98)
    
    intern_summary = {}
    for prof in InternProfile:
        sub = df[df["intern_profile"] == prof.value]
        sub_len = len(sub)
        if sub_len == 0:
            continue
        sub_iw = (sub["winner"] == Role.INTERN.value).sum() / sub_len * 100
        sub_bw = (sub["winner"] == Role.BANKER.value).sum() / sub_len * 100
        sub_dur = sub["rounds"].mean()
        sub_lock = (sub["intern_lockout"]).sum() / sub_len * 100
        sub_unm = sub["interns_unmasked"].mean()
        top_sc = sub["score"].value_counts().index[0]
        top_sc_pct = sub["score"].value_counts().iloc[0] / sub_len * 100
        top_str = f"{top_sc} ({top_sc_pct:.1f}%)"

        print(f"{prof.value:<36} | {sub_iw:7.2f}% | {sub_bw:7.2f}% | {sub_dur:6.2f}   | {sub_lock:6.2f}%  | {sub_unm:6.2f}    | {top_str:<10}")

        intern_summary[prof.value] = {
            'wr_interns': sub_iw,
            'wr_bankers': sub_bw,
            'avg_rounds': sub_dur,
            'lockout_pct': sub_lock,
            'avg_unmasked': sub_unm,
            'top_score': top_sc
        }

    # -------------------------------------------------------------------------
    # 7. ANÁLISE COMPARATIVA POR PERFIL DE BANQUEIRO
    # -------------------------------------------------------------------------
    print("\n" + "=" * 84)
    print(" 7. COMPARATIVO MULTIDIMENSIONAL POR PERFIL DE BANQUEIRO")
    print("=" * 84)
    print(f"{'Perfil Banqueiro':<36} | {'WR Banco':<9} | {'WR Estag':<9} | {'Duração':<8} | {'Vetos Méd':<10} | {'Desmasc.':<9}")
    print("-" * 98)
    
    banker_summary = {}
    for bprof in BankerProfile:
        sub = df[df["banker_profile"] == bprof.value]
        sub_len = len(sub)
        if sub_len == 0:
            continue
        sub_bw = (sub["winner"] == Role.BANKER.value).sum() / sub_len * 100
        sub_iw = (sub["winner"] == Role.INTERN.value).sum() / sub_len * 100
        sub_dur = sub["rounds"].mean()
        sub_vet = sub["total_vetoes"].mean()
        sub_unm = sub["interns_unmasked"].mean()

        print(f"{bprof.value:<36} | {sub_bw:7.2f}% | {sub_iw:7.2f}% | {sub_dur:6.2f}   | {sub_vet:7.2f}    | {sub_unm:6.2f}")

        banker_summary[bprof.value] = {
            'wr_bankers': sub_bw,
            'wr_interns': sub_iw,
            'avg_rounds': sub_dur,
            'avg_vetoes': sub_vet,
            'avg_unmasked': sub_unm
        }

    # -------------------------------------------------------------------------
    # 8. MATRIZ DE CONFRONTO CRUZADO (BANKERS vs INTERNS)
    # -------------------------------------------------------------------------
    matchup_summary = {}
    if "banker_profile" in df.columns and "intern_profile" in df.columns:
        print("\n" + "=" * 84)
        print(" 8. MATRIZ DE CONFRONTO CRUZADO (TAXA DE VITÓRIA DOS BANQUEIROS)")
        print("=" * 84)
        header = f"{'Banqueiro \\ Estagiário':<28} | " + " | ".join([f"{p.name[:8]:<8}" for p in InternProfile])
        print(header)
        print("-" * len(header))
        for bp in BankerProfile:
            row_vals = []
            for ip in InternProfile:
                sub = df[(df["banker_profile"] == bp.value) & (df["intern_profile"] == ip.value)]
                if len(sub) > 0:
                    wr = (sub["winner"] == Role.BANKER.value).sum() / len(sub) * 100
                    row_vals.append(f"{wr:6.1f}% ")
                    matchup_summary[f"{bp.name} vs {ip.name}"] = float(wr)
                else:
                    row_vals.append("   -    ")
            print(f"{bp.name:<28} | " + " | ".join(row_vals))
    print("=" * 84)

    if export_json:
        import json
        summary_payload = {
            'n_games': n_games,
            'total_time_seconds': total_time,
            'banker_win_rate': b_pct,
            'intern_win_rate': i_pct,
            'avg_rounds': float(df['rounds'].mean()),
            'score_distribution': {k: int(v) for k, v in score_counts.items()},
            'tier_funnel': tier_stats,
            'governance': {
                'avg_vetoes': float(avg_vetoes),
                'games_with_forced': int(games_with_forced),
                'r5_expansion_count': int(r5_exp_count)
            },
            'economy': {
                'avg_tokens_spent': float(avg_tokens),
                'avg_hand_end': float(avg_hand_end),
                'total_toxic_played': int(total_toxic)
            },
            'deduction': {
                'lockout_count': int(lockout_count),
                'avg_unmasked': float(unmasked_avg),
                'avg_intern_sus': float(avg_int_sus),
                'avg_banker_sus': float(avg_bnk_sus)
            },
            'by_intern_profile': intern_summary,
            'by_banker_profile': banker_summary,
            'by_matchup': matchup_summary,
            'by_profile': intern_summary
        }
        with open(export_json, 'w', encoding='utf-8') as f:
            json.dump(summary_payload, f, indent=2, ensure_ascii=False)
        print(f"\n📁 Relatório consolidado exportado com sucesso em: {export_json}")

    return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Simulador Monte Carlo Massivo - BTG Madagascar v14.0")
    parser.add_argument("--games", "-n", type=int, default=100000, help="Número de partidas a simular (padrão: 100.000)")
    parser.add_argument("--workers", "-w", type=int, default=None, help="Número de workers paralelos (padrão: CPU count)")
    parser.add_argument("--export", "-e", type=str, default=None, help="Caminho para exportar resumo em JSON")
    parser.add_argument("--banker-profile", "-bp", type=str, default=None, help="Perfil dos banqueiros (ex: BALANCED, CONSERVATIVE, PRAGMATIC, STRATEGIST, mixed, all)")
    parser.add_argument("--intern-profile", "-ip", type=str, default=None, help="Perfil dos estagiários (ex: A_AGGRESSIVE, B_SLEEPER, C_HEDGE, D_OPPORTUNIST, E_TECHNICIAN, mixed, all)")
    args = parser.parse_args()

    run_monte_carlo(
        n_games=args.games,
        num_workers=args.workers,
        export_json=args.export,
        banker_profile=args.banker_profile,
        intern_profile=args.intern_profile
    )
