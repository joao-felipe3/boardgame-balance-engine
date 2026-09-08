# -*- coding: utf-8 -*-
"""
BTG Madagascar - CLI Principal & Ponto de Entrada do Projeto
============================================================
Uso:
  python run.py --sim 50000       # Executa simulação Monte Carlo de 50k jogos
  python run.py --benchmark       # Executa benchmark isolado de perfis
  python run.py --dashboard       # Gera traces e atualiza o visualizador HTML
  python run.py --all             # Executa simulação, traces e dashboard
"""

import sys
import os
import argparse

from simulations.run_monte_carlo import run_monte_carlo
from simulations.benchmark_profiles import benchmark_profiles
from simulations.analyze_causality import run_causal_analysis
from visualizer.create_dashboard import generate_dashboard
from src.btg.tracer import generate_trace_dataset


def main():
    parser = argparse.ArgumentParser(description="BTG Madagascar CLI Runner")
    parser.add_argument("--sim", type=int, default=None, help="Executar simulação Monte Carlo com N partidas")
    parser.add_argument("--workers", "-w", type=int, default=None, help="Número de workers paralelos para simulação")
    parser.add_argument("--export", "-e", type=str, default=None, help="Caminho para exportar relatório estatístico em JSON")
    parser.add_argument("--banker-profile", "-bp", type=str, default=None, help="Perfil dos banqueiros (ex: BALANCED, CONSERVATIVE, PRAGMATIC, STRATEGIST, mixed, all)")
    parser.add_argument("--intern-profile", "-ip", type=str, default=None, help="Perfil dos estagiários (ex: A_AGGRESSIVE, B_SLEEPER, C_HEDGE, D_OPPORTUNIST, E_TECHNICIAN, mixed, all)")
    parser.add_argument("--benchmark", action="store_true", help="Executar benchmark comparativo dos perfis")
    parser.add_argument("--causal", action="store_true", help="Executar Análise Causal, Árvores de Decisão e SHAP")
    parser.add_argument("--dashboard", action="store_true", help="Gerar traces e atualizar visualizador HTML")
    parser.add_argument("--all", action="store_true", help="Executar simulação, benchmark, análise causal e atualizar dashboard")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        # Padrão se rodar sem argumentos: rodar 30k simulação + gerar dashboard
        print("Executando fluxo padrão: Simulação 30k + Atualização do Dashboard...\n")
        run_monte_carlo(30000, num_workers=args.workers)
        print("\nGerando Traces e Visualizador...")
        generate_trace_dataset("visualizer/data/game_traces.json")
        generate_dashboard()
        return

    if args.all:
        run_monte_carlo(
            50000,
            num_workers=args.workers,
            export_json=args.export,
            banker_profile=args.banker_profile,
            intern_profile=args.intern_profile
        )
        benchmark_profiles(2000, matrix_sample=500)
        run_causal_analysis(20000, num_workers=args.workers, export_json="visualizer/data/causal_analysis_summary.json")
        generate_trace_dataset("visualizer/data/game_traces.json")
        generate_dashboard()
        return

    if args.sim is not None:
        run_monte_carlo(
            args.sim,
            num_workers=args.workers,
            export_json=args.export,
            banker_profile=args.banker_profile,
            intern_profile=args.intern_profile
        )

    if args.benchmark:
        benchmark_profiles(2000, matrix_sample=500)

    if args.causal:
        n_games = args.sim if args.sim is not None else 20000
        export_p = args.export or "visualizer/data/causal_analysis_summary.json"
        run_causal_analysis(n_games, num_workers=args.workers, export_json=export_p)

    if args.dashboard:
        print("Gerando Traces e Visualizador...")
        generate_trace_dataset("visualizer/data/game_traces.json")
        generate_dashboard()


if __name__ == '__main__':
    main()
