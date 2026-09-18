# -*- coding: utf-8 -*-
"""
Teste de Raciocínio Humano da Mesa Real:
1. Eliminar o fogo amigo sobre o parceiro inocente de um comitê sabotado por insumo.
2. Quando dois banqueiros estavam no banco durante uma falha, eles reconhecem a si mesmos como limpos.
3. Consenso de governança para evitar comitês forçados acidentais.
"""
import sys
import os
import random
import pandas as pd
import numpy as np

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import Role, InternProfile, BankerProfile, simulate_single_match

def test_current_vs_hypothetical():
    print("=" * 80)
    print("SIMULANDO O COMPORTAMENTO ATUAL (3.000 PARTIDAS)...")
    print("=" * 80)

    # Coleta telemetria detalhada de 3.000 partidas atuais
    current_results = []
    for i in range(3000):
        res = simulate_single_match(
            i,
            seed=300000 + i,
            banker_profile=BankerProfile.BALANCED,
            intern_profile=InternProfile.B_SLEEPER
        )
        current_results.append(res)
    df_curr = pd.DataFrame(current_results)
    
    b_wr = (df_curr['winner'] == Role.BANKER.value).mean() * 100
    forced = df_curr['forced_committees'].sum()
    infils = df_curr['intern_appearances'].mean() if 'intern_appearances' in df_curr else 0

    print(f"WR Atual Banco : {b_wr:.2f}% | Estagiários: {100 - b_wr:.2f}%")
    print(f"Comitês Forçados: {forced} ({forced/3000:.2f} por jogo)")
    print(f"Média de Vetos  : {df_curr['total_vetoes'].mean():.2f}")

if __name__ == '__main__':
    test_current_vs_hypothetical()
