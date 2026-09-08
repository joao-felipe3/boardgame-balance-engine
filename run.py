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

def main():
    parser = argparse.ArgumentParser(description="BTG Madagascar CLI Runner")
    parser.add_argument("--sim", type=int, default=None, help="Executar simulação Monte Carlo com N partidas")
    parser.add_argument("--workers", "-w", type=int, default=None, help="Número de workers paralelos para simulação")
    parser.add_argument("--export", "-e", type=str, default=None, help="Caminho para exportar relatório estatístico em JSON")
    parser.add_argument("--banker-profile", "-bp", type=str, default=None, help="Perfil dos banqueiros (ex: BALANCED, CONSERVATIVE, PRAGMATIC, STRATEGIST, mixed, all)")
    parser.add_argument("--intern-profile", "-ip", type=str, default=None, help="Perfil dos estagiários (ex: A_AGGRESSIVE, B_SLEEPER, C_HEDGE, D_OPPORTUNIST, E_TECHNICIAN, mixed, all)")
    parser.add_argument("--benchmark", action="store_true", help="Executar benchmark comparativo dos perfis")
    parser.add_argument("--causal", action="store_true", help="Executar Análise Causal, Árvores de Decisão e SHAP")
    parser.add_argument("--markov", action="store_true", help="Executar Resolvedor Analítico de Cadeias de Markov")
    parser.add_argument("--nash", "--game-theory", action="store_true", help="Executar Motor de Teoria dos Jogos & Equilíbrio de Nash")
    parser.add_argument("--stress", action="store_true", help="Executar Teste de Estresse Econômico & Choques de Liquidez")
    parser.add_argument("--entropy", "--info", action="store_true", help="Executar Análise de Teoria da Informação & Entropia de Shannon")
    parser.add_argument("--dashboard", action="store_true", help="Gerar traces e atualizar visualizador HTML")
    parser.add_argument("--all", action="store_true", help="Executar suíte analítica completa (sim, benchmark, causal, markov, nash, stress, entropy) e atualizar dashboard")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        # Padrão se rodar sem argumentos: rodar 30k simulação + gerar dashboard
        from simulations.run_monte_carlo import run_monte_carlo
        from src.btg.tracer import generate_trace_dataset
        from visualizer.create_dashboard import generate_dashboard
        print("Executando fluxo padrão: Simulação 30k + Atualização do Dashboard...\n")
        run_monte_carlo(30000, num_workers=args.workers)
        print("\nGerando Traces e Visualizador...")
        generate_trace_dataset("visualizer/data/game_traces.json")
        generate_dashboard()
        return

    if args.all:
        from simulations.run_monte_carlo import run_monte_carlo
        from simulations.benchmark_profiles import benchmark_profiles
        from simulations.analyze_causality import run_causal_analysis
        from simulations.analyze_markov import run_markov_analysis
        from simulations.analyze_game_theory import run_game_theory_analysis
        from simulations.stress_test_economy import run_stress_test
        from simulations.analyze_information import run_information_analysis
        from src.btg.tracer import generate_trace_dataset
        from visualizer.create_dashboard import generate_dashboard

        run_monte_carlo(
            50000,
            num_workers=args.workers,
            export_json=args.export,
            banker_profile=args.banker_profile,
            intern_profile=args.intern_profile
        )
        benchmark_profiles(2000, matrix_sample=500)
        run_causal_analysis(20000, num_workers=args.workers, export_json="visualizer/data/causal_analysis_summary.json")
        run_markov_analysis(10000, num_workers=args.workers, export_json="visualizer/data/markov_chain_summary.json")
        run_game_theory_analysis(export_json="visualizer/data/game_theory_summary.json")
        run_stress_test(n_games_per_scenario=1000, num_workers=args.workers, export_json="visualizer/data/economic_stress_summary.json")
        run_information_analysis(n_games=2000, num_workers=args.workers, export_json="visualizer/data/information_entropy_summary.json")
        generate_trace_dataset("visualizer/data/game_traces.json")
        generate_dashboard()
        return

    special_action = any([args.benchmark, args.causal, args.markov, args.nash, args.stress, args.entropy, args.dashboard])

    if args.sim is not None and not special_action:
        from simulations.run_monte_carlo import run_monte_carlo
        run_monte_carlo(
            args.sim,
            num_workers=args.workers,
            export_json=args.export,
            banker_profile=args.banker_profile,
            intern_profile=args.intern_profile
        )

    if args.benchmark:
        from simulations.benchmark_profiles import benchmark_profiles
        benchmark_profiles(2000, matrix_sample=500)

    if args.causal:
        from simulations.analyze_causality import run_causal_analysis
        n_games = args.sim if args.sim is not None else 20000
        export_p = args.export or "visualizer/data/causal_analysis_summary.json"
        run_causal_analysis(n_games, num_workers=args.workers, export_json=export_p)

    if args.markov:
        from simulations.analyze_markov import run_markov_analysis
        calib_n = args.sim if args.sim is not None else 10000
        export_p = args.export or "visualizer/data/markov_chain_summary.json"
        run_markov_analysis(calibrate_games=calib_n, num_workers=args.workers, export_json=export_p)

    if args.nash:
        from simulations.analyze_game_theory import run_game_theory_analysis
        export_p = args.export or "visualizer/data/game_theory_summary.json"
        run_game_theory_analysis(export_json=export_p)

    if args.stress:
        from simulations.stress_test_economy import run_stress_test
        games_per = args.sim if args.sim is not None else 2000
        export_p = args.export or "visualizer/data/economic_stress_summary.json"
        run_stress_test(n_games_per_scenario=games_per, num_workers=args.workers, export_json=export_p)

    if args.entropy:
        from simulations.analyze_information import run_information_analysis
        n_games = args.sim if args.sim is not None else 3000
        export_p = args.export or "visualizer/data/information_entropy_summary.json"
        run_information_analysis(n_games=n_games, num_workers=args.workers, export_json=export_p)

    if args.dashboard:
        from src.btg.tracer import generate_trace_dataset
        from visualizer.create_dashboard import generate_dashboard
        print("Gerando Traces e Visualizador...")
        generate_trace_dataset("visualizer/data/game_traces.json")
        generate_dashboard()


if __name__ == '__main__':
    main()
