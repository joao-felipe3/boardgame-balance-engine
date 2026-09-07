# -*- coding: utf-8 -*-
"""
BTG Madagascar - Benchmark Comparativo de Perfis de IA
======================================================
Executa partidas controladas avaliando a eficácia e dinâmicas
de cada perfil de Banqueiro e Estagiário, além da matriz de confronto.
"""

import sys
import os
import argparse
import pandas as pd

# Garante acesso aos módulos do projeto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

from src.btg import Role, InternProfile, BankerProfile, simulate_single_match


def benchmark_profiles(n_per_profile: int = 5000, matrix_sample: int = 1000):
    print("=" * 86)
    print(f"   BENCHMARK COMPARATIVO DE PERFIS - BTG MADAGASCAR v14.0")
    print(f"   ({n_per_profile:,} partidas por perfil | {matrix_sample:,} por célula da matriz)")
    print("=" * 86)

    # 1. PERFIS DE ESTAGIÁRIO (vs Banqueiros Equilibrados)
    print("\n" + "-" * 86)
    print(" 1. DESEMPENHO DOS PERFIS DE ESTAGIÁRIO (vs Banqueiros Equilibrados)")
    print("-" * 86)
    print(f"{'Perfil do Estagiário':<38} | {'WR Estag':<9} | {'WR Banco':<9} | {'Duração':<8} | {'Clímax R7':<9}")
    print("-" * 86)

    for prof in InternProfile:
        results = []
        for i in range(n_per_profile):
            res = simulate_single_match(
                i,
                intern_profile=prof,
                banker_profile=BankerProfile.BALANCED,
                seed=500000 + i
            )
            results.append(res)
        df = pd.DataFrame(results)
        iw = (df["winner"] == Role.INTERN.value).sum() / n_per_profile * 100
        bw = (df["winner"] == Role.BANKER.value).sum() / n_per_profile * 100
        df["score"] = df["b_score"].astype(str) + " x " + df["i_score"].astype(str)
        climax = ((df["score"].isin(["4 x 3", "3 x 4"])).sum() / n_per_profile) * 100
        print(f"{prof.value:<38} | {iw:7.2f}% | {bw:7.2f}% | {df['rounds'].mean():6.2f}   | {climax:7.2f}%")

    # 2. PERFIS DE BANQUEIRO (vs Estagiários Infiltração Profunda / Sleeper)
    print("\n" + "-" * 86)
    print(" 2. DESEMPENHO DOS PERFIS DE BANQUEIRO (vs Estagiários Sleeper Padrão)")
    print("-" * 86)
    print(f"{'Perfil do Banqueiro':<38} | {'WR Banco':<9} | {'WR Estag':<9} | {'Duração':<8} | {'Vetos Méd':<9}")
    print("-" * 86)

    for bprof in BankerProfile:
        results = []
        for i in range(n_per_profile):
            res = simulate_single_match(
                i,
                intern_profile=InternProfile.B_SLEEPER,
                banker_profile=bprof,
                seed=600000 + i
            )
            results.append(res)
        df = pd.DataFrame(results)
        bw = (df["winner"] == Role.BANKER.value).sum() / n_per_profile * 100
        iw = (df["winner"] == Role.INTERN.value).sum() / n_per_profile * 100
        vetoes = df["total_vetoes"].mean()
        print(f"{bprof.value:<38} | {bw:7.2f}% | {iw:7.2f}% | {df['rounds'].mean():6.2f}   | {vetoes:7.2f}")

    # 3. MATRIZ DE CONFRONTO CRUZADO (4 BANQUEIROS x 5 ESTAGIÁRIOS)
    if matrix_sample > 0:
        print("\n" + "-" * 86)
        print(f" 3. MATRIZ DE CONFRONTO COMPLETA (WR BANQUEIROS) — {matrix_sample} JOGOS/CÉLULA")
        print("-" * 86)
        header = f"{'Banqueiro \\ Estagiário':<24} | " + " | ".join([f"{p.name[:9]:<9}" for p in InternProfile])
        print(header)
        print("-" * len(header))

        for bp in BankerProfile:
            row_str = []
            for ip in InternProfile:
                bw_count = 0
                for i in range(matrix_sample):
                    res = simulate_single_match(
                        i,
                        intern_profile=ip,
                        banker_profile=bp,
                        seed=700000 + i
                    )
                    if res["winner"] == Role.BANKER.value:
                        bw_count += 1
                wr = (bw_count / matrix_sample) * 100
                row_str.append(f"{wr:7.1f}% ")
            print(f"{bp.name:<24} | " + " | ".join(row_str))

    print("=" * 86)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Benchmark de Perfis de IA - BTG Madagascar v14.0")
    parser.add_argument("--games", "-n", type=int, default=5000, help="Partidas por perfil isolado (padrão: 5.000)")
    parser.add_argument("--matrix-sample", "-m", type=int, default=1000, help="Partidas por célula da matriz (padrão: 1.000)")
    args = parser.parse_args()

    benchmark_profiles(args.games, args.matrix_sample)
