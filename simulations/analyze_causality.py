# -*- coding: utf-8 -*-
"""
BTG Madagascar - Módulo de Análise Causal & SHAP (v14.0)
======================================================
Utiliza Machine Learning Interpretável (Árvores de Decisão, Random Forest,
Regressão Logística com Odds Ratios e SHAP Values) sobre os logs de simulação
para extrair regras causais, gargalos de design e pontos de inflexão do jogo.
"""

import sys
import os
import time
import argparse
import json
from typing import List, Dict, Tuple, Optional
import numpy as np
import pandas as pd

from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.inspection import permutation_importance
import shap

# Garante acesso aos módulos do projeto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

from src.btg import Role, InternProfile, BankerProfile, simulate_single_match
from simulations.run_monte_carlo import run_monte_carlo


FEATURE_DESCRIPTIONS = {
    'intern_comm_appearances': 'Total de Infiltrações de Estagiários nos Comitês',
    'suspicion_gap': 'Diferencial de Suspeita (Suspeita Estagiário - Suspeita Banqueiro)',
    'avg_intern_sus': 'Suspeita Média Final sobre Estagiários',
    'avg_banker_sus': 'Suspeita Média Final sobre Banqueiros (Ruído/Falso Positivo)',
    'interns_unmasked': 'Estagiários Totalmente Desmascarados (Suspeita 1.0)',
    'first_intern_round': 'Primeira Rodada em que um Estagiário Infiltrou',
    'total_tokens_spent': 'Total de Tokens de Rendimento Utilizados no Jogo',
    'total_toxic_played': 'Total de Ativos Tóxicos Jogados no Cofre',
    'total_vetoes': 'Total de Vetos a Comitês Ocorridos',
    'forced_committees': 'Comitês Forçados após 3 Vetos Consecutivos',
    'r5_expanded': 'Megaconsórcio Expandido para 4 Membros (R5)',
    'r1_success': 'Sucesso da Operação no Tier 1 (Abertura)',
    'r2_success': 'Sucesso da Operação no Tier 2 (Aperto)',
    'r3_success': 'Sucesso da Operação no Tier 3 (Comitê de 3)',
    'banker_lead_r2': 'Saldo do Placar após R2 (+2, 0 ou -2)',
    'banker_lead_r3': 'Saldo do Placar após R3 (+3, +1, -1 ou -3)',
    'r1_intern': 'Estagiário Presente no Comitê da R1',
    'r2_intern': 'Estagiário Presente no Comitê da R2',
    'r3_intern': 'Estagiário Presente no Comitê da R3',
    'r2_tokens': 'Tokens de Rendimento Gastos na R2',
    'r3_tokens': 'Tokens de Rendimento Gastos na R3',
    'avg_hand_size': 'Média de Cartas Restantes na Mão'
}


def build_causal_dataframe(results: List[Dict]) -> pd.DataFrame:
    """Extrai features causais tabulares ricas de cada partida simulada."""
    rows = []
    for res in results:
        tt = res.get("tier_telemetry", {})
        r1 = tt.get(1, {})
        r2 = tt.get(2, {})
        r3 = tt.get(3, {})

        r1_success = 1 if r1.get('success', False) else 0
        r1_intern = 1 if r1.get('intern_count', 0) > 0 else 0
        r1_tokens = r1.get('tokens_spent', 0)

        r2_success = 1 if r2.get('success', False) else 0
        r2_intern = 1 if r2.get('intern_count', 0) > 0 else 0
        r2_tokens = r2.get('tokens_spent', 0)

        r3_success = 1 if r3.get('success', False) else 0
        r3_intern = 1 if r3.get('intern_count', 0) > 0 else 0
        r3_tokens = r3.get('tokens_spent', 0)

        banker_lead_r2 = (1 if r1_success else -1) + (1 if r2_success else -1)
        banker_lead_r3 = banker_lead_r2 + (1 if r3_success else -1)

        first_ir = res.get("first_intern_round")
        if first_ir is None or (isinstance(first_ir, float) and np.isnan(first_ir)):
            first_ir_val = 8
        else:
            first_ir_val = int(first_ir)

        avg_int_s = res.get("avg_intern_sus", 0.5)
        avg_bnk_s = res.get("avg_banker_sus", 0.4)
        susp_gap = round(avg_int_s - avg_bnk_s, 3)

        row = {
            'banker_won': 1 if res['winner'] == Role.BANKER.value else 0,
            'rounds': res.get('rounds', 5),
            'b_score': res.get('b_score', 0),
            'i_score': res.get('i_score', 0),
            'banker_profile': res.get('banker_profile', 'Equilibrado'),
            'intern_profile': res.get('intern_profile', 'Sleeper'),
            # Features Causais
            'intern_comm_appearances': res.get('intern_comm_appearances', 0),
            'suspicion_gap': susp_gap,
            'avg_intern_sus': avg_int_s,
            'avg_banker_sus': avg_bnk_s,
            'interns_unmasked': res.get('interns_unmasked', 0),
            'first_intern_round': first_ir_val,
            'total_tokens_spent': res.get('total_tokens_spent', 0),
            'total_toxic_played': res.get('total_toxic_played', 0),
            'total_vetoes': res.get('total_vetoes', 0),
            'forced_committees': res.get('forced_committees', 0),
            'r5_expanded': 1 if res.get('r5_expanded') else 0,
            'r1_success': r1_success,
            'r2_success': r2_success,
            'r3_success': r3_success,
            'banker_lead_r2': banker_lead_r2,
            'banker_lead_r3': banker_lead_r3,
            'r1_intern': r1_intern,
            'r2_intern': r2_intern,
            'r3_intern': r3_intern,
            'r2_tokens': r2_tokens,
            'r3_tokens': r3_tokens,
            'avg_hand_size': res.get('avg_hand_size', 3.5)
        }
        rows.append(row)

    return pd.DataFrame(rows)


def extract_decision_rules(tree_model: DecisionTreeClassifier, feature_names: List[str]) -> List[Dict]:
    """Traduz as ramificações de uma Árvore de Decisão em regras legíveis em português."""
    tree_ = tree_model.tree_
    feature_name = [
        feature_names[i] if i >= 0 else "undefined!"
        for i in tree_.feature
    ]

    rules = []

    def recurse(node, current_conditions):
        if tree_.feature[node] >= 0:
            name = feature_name[node]
            threshold = tree_.threshold[node]

            # Ramo Esquerdo: <= threshold
            left_cond = f"{FEATURE_DESCRIPTIONS.get(name, name)} <= {threshold:.2f}"
            recurse(tree_.children_left[node], current_conditions + [left_cond])

            # Ramo Direito: > threshold
            right_cond = f"{FEATURE_DESCRIPTIONS.get(name, name)} > {threshold:.2f}"
            recurse(tree_.children_right[node], current_conditions + [right_cond])
        else:
            # Folha
            counts = tree_.value[node][0]
            total = sum(counts)
            p_banker = counts[1] / total if total > 0 else 0.0
            rules.append({
                'conditions': list(current_conditions),
                'p_banker_win': p_banker,
                'p_intern_win': 1.0 - p_banker,
                'samples': int(tree_.n_node_samples[node]),
                'confidence': f"{p_banker*100:.1f}%" if p_banker >= 0.5 else f"{(1-p_banker)*100:.1f}%"
            })

    recurse(0, [])
    # Ordena regras da maior probabilidade de vitória do banco para a menor
    rules.sort(key=lambda r: -r['p_banker_win'])
    return rules


def run_causal_analysis(
    n_games: int = 30000,
    seed_base: int = 840000,
    num_workers: Optional[int] = None,
    export_json: Optional[str] = None
) -> Dict:
    """Executa o pipeline completo de Análise Causal, Árvores de Decisão e SHAP."""
    print("=" * 86)
    print(f"       ANÁLISE CAUSAL & MACHINE LEARNING INTERPRETÁVEL (SHAP / ÁRVORES)")
    print(f"       Base: {n_games:,} Partidas Simuladas | Motor: BTG Madagascar v14.0")
    print("=" * 86)

    t0 = time.time()

    # 1. Geração / Simulação dos Dados
    print(f"\n[1/5] Executando simulação massiva de telemetria ({n_games:,} jogos)...")
    df_raw = run_monte_carlo(n_games=n_games, seed_base=seed_base, num_workers=num_workers)

    print("\n[2/5] Estruturando vetor de atributos causais...")
    feature_cols = [
        'intern_comm_appearances', 'suspicion_gap', 'avg_intern_sus', 'avg_banker_sus',
        'interns_unmasked', 'first_intern_round', 'total_tokens_spent', 'total_toxic_played',
        'total_vetoes', 'forced_committees', 'r5_expanded',
        'r1_success', 'r2_success', 'r3_success', 'banker_lead_r2', 'banker_lead_r3',
        'r1_intern', 'r2_intern', 'r3_intern', 'r2_tokens', 'r3_tokens', 'avg_hand_size'
    ]

    # Prepara matriz X e alvo y
    # Se df_raw já tiver as colunas calculadas diretamente pelo run_monte_carlo ou via build_causal_dataframe
    if 'suspicion_gap' not in df_raw.columns:
        df = build_causal_dataframe(df_raw.to_dict(orient='records'))
    else:
        df = df_raw.copy()

    X = df[feature_cols].copy().fillna(0).astype(float)
    y = df['banker_won'].copy().astype(int)

    b_win_base = y.mean() * 100
    print(f"  * Baseline Global: Banqueiros {b_win_base:.2f}% | Estagiários {100 - b_win_base:.2f}%")

    # 2. Árvore de Decisão Rasa e Extração de Regras Explícitas
    print("\n[3/5] Treinando Árvore de Decisão Rasa (Max Depth = 3)...")
    dt = DecisionTreeClassifier(max_depth=3, min_samples_leaf=0.03, random_state=42)
    dt.fit(X, y)
    rules = extract_decision_rules(dt, feature_cols)

    print("\n" + "=" * 86)
    print(" 1. REGRAS DE DECISÃO CAUSAIS EXTRAÍDAS (SE -> ENTÃO)")
    print("=" * 86)
    for idx, r in enumerate(rules, 1):
        outcome = "VITÓRIA BANQUEIROS" if r['p_banker_win'] >= 0.5 else "VITÓRIA ESTAGIÁRIOS"
        color_marker = "🟢" if r['p_banker_win'] >= 0.70 else ("🔴" if r['p_banker_win'] <= 0.30 else "🟡")
        print(f"\n{color_marker} REGRA #{idx} -> {outcome} (Probabilidade Banco: {r['p_banker_win']*100:5.1f}% | {r['samples']:,} jogos):")
        for cond in r['conditions']:
            print(f"     • {cond}")

    # 3. Modelos Comparativos: Random Forest & Regressão Logística (Odds Ratios)
    print("\n" + "=" * 86)
    print(" 2. RANKING DE IMPORTÂNCIA DE FEATURES & ODDS RATIOS")
    print("=" * 86)

    # Random Forest
    rf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42, n_jobs=-1)
    rf.fit(X, y)
    rf_importances = rf.feature_importances_

    # Regressão Logística Padronizada para Odds Ratios
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X_scaled, y)
    odds_ratios = np.exp(lr.coef_[0])

    # Compilação em Tabela
    importance_df = pd.DataFrame({
        'feature': feature_cols,
        'description': [FEATURE_DESCRIPTIONS.get(f, f) for f in feature_cols],
        'rf_importance': rf_importances,
        'odds_ratio': odds_ratios
    }).sort_values(by='rf_importance', ascending=False)

    print(f"{'Atributo':<26} | {'Importância RF':<14} | {'Odds Ratio (Efeito)':<22} | {'Interpretação':<20}")
    print("-" * 92)
    for _, row in importance_df.head(12).iterrows():
        or_val = row['odds_ratio']
        if or_val > 1.15:
            effect_str = f"{or_val:5.2f}x (Favorece Banco 🟢)"
            interp = "Fator Crítico de Vitória"
        elif or_val < 0.85:
            effect_str = f"{or_val:5.2f}x (Favorece Estag 🔴)"
            interp = "Fator Crítico de Falha"
        else:
            effect_str = f"{or_val:5.2f}x (Neutro ⚪)"
            interp = "Equilibrado / Contextual"

        print(f"{row['feature']:<26} | {row['rf_importance']*100:11.2f}% | {effect_str:<22} | {interp:<20}")

    # 4. Cálculo de Valores SHAP
    print("\n[4/5] Calculando Atribuições Marginais SHAP (TreeExplainer)...")
    sample_size = min(3000, len(X))
    X_shap_sample = X.sample(n=sample_size, random_state=42)
    explainer = shap.TreeExplainer(rf)
    shap_values = explainer.shap_values(X_shap_sample)

    # shap_values[1] é a classe positiva (Vitória dos Banqueiros)
    if isinstance(shap_values, list) and len(shap_values) == 2:
        shap_banker = shap_values[1]
    elif isinstance(shap_values, np.ndarray) and len(shap_values.shape) == 3:
        shap_banker = shap_values[:, :, 1]
    else:
        shap_banker = shap_values

    mean_abs_shap = np.abs(shap_banker).mean(axis=0)
    # Direcionalidade: correlação entre o valor da feature e o valor de shap
    shap_df = pd.DataFrame({
        'feature': feature_cols,
        'mean_abs_shap': mean_abs_shap,
    }).sort_values(by='mean_abs_shap', ascending=False)

    print("\n" + "=" * 86)
    print(" 3. TOP 8 FATORES DE MAIOR IMPACTO MARGINAL (SHAP VALUES)")
    print("=" * 86)
    print(f"{'Atributo Causal':<26} | {'Impacto Médio |SHAP|':<20} | {'Direção do Impacto':<32}")
    print("-" * 86)
    for _, row in shap_df.head(8).iterrows():
        f = row['feature']
        feat_vals = X_shap_sample[f].values
        col_idx = feature_cols.index(f)
        f_shap = shap_banker[:, col_idx]
        std_feat = np.std(feat_vals)
        std_shap = np.std(f_shap)
        if std_feat > 1e-9 and std_shap > 1e-9:
            corr = np.corrcoef(feat_vals, f_shap)[0, 1]
            corr = 0.0 if np.isnan(corr) else corr
        else:
            corr = 0.0
        direction = "Mais alto aumenta chance de Vitória do Banco 🟢" if corr > 0 else "Mais alto reduz chance do Banco (Favorece Estagiários 🔴)"
        print(f"{f:<26} | {row['mean_abs_shap']:18.4f} | {direction:<32}")

    # 5. PONTOS DE INFLEXÃO NÃO ÓBVIOS (GAME DESIGN TIPPING POINTS)
    print("\n" + "=" * 86)
    print(" 4. PONTOS DE INFLEXÃO NÃO ÓBVIOS & CAUSALIDADES DO DESIGN")
    print("=" * 86)

    # 5.1 O Tipping Point das Infiltrações
    print("\n📌 [Ponto de Inflexão 1] A Fronteira das Infiltrações de Estagiários:")
    for app in range(5):
        sub = df[df['intern_comm_appearances'] == app]
        if len(sub) > 0:
            wr = sub['banker_won'].mean() * 100
            flag = "✅ Seguro" if wr >= 65 else ("⚠️ Perigo" if wr >= 45 else "💀 Fatal")
            print(f"   • {app} Infiltração(ões) no jogo : WR Banco = {wr:5.1f}% ({len(sub):6,d} jogos) -> {flag}")

    # 5.2 O Mito do Tier 1 vs O Divisor de Águas do Tier 3
    wr_r1_win = df[df['r1_success'] == 1]['banker_won'].mean() * 100
    wr_r1_loss = df[df['r1_success'] == 0]['banker_won'].mean() * 100
    wr_r3_win = df[df['r3_success'] == 1]['banker_won'].mean() * 100
    wr_r3_loss = df[df['r3_success'] == 0]['banker_won'].mean() * 100

    print("\n📌 [Ponto de Inflexão 2] Comparativo de Impacto Causal: Tier 1 vs Tier 3:")
    print(f"   • Tier 1 Aprovado : WR Banco = {wr_r1_win:5.1f}% | Tier 1 Falhou : WR Banco = {wr_r1_loss:5.1f}% (Impacto: {wr_r1_win - wr_r1_loss:+.1f} p.p.)")
    print(f"   • Tier 3 Aprovado : WR Banco = {wr_r3_win:5.1f}% | Tier 3 Falhou : WR Banco = {wr_r3_loss:5.1f}% (Impacto: {wr_r3_win - wr_r3_loss:+.1f} p.p.)")
    if (wr_r3_win - wr_r3_loss) > (wr_r1_win - wr_r1_loss):
        print(f"   👉 Conclusão Causal: O Tier 3 possui {(wr_r3_win - wr_r3_loss) / max(0.1, (wr_r1_win - wr_r1_loss)):.1f}x mais peso no resultado final que o Tier 1.")

    # 5.3 O Dilema da Queima de Tokens
    t_low = df[df['total_tokens_spent'] <= 3]['banker_won'].mean() * 100
    t_med = df[(df['total_tokens_spent'] >= 4) & (df['total_tokens_spent'] <= 6)]['banker_won'].mean() * 100
    t_high = df[df['total_tokens_spent'] >= 7]['banker_won'].mean() * 100
    print("\n📌 [Ponto de Inflexão 3] Retorno Marginal do Uso de Tokens de Rendimento:")
    print(f"   • Uso Baixo (0 a 3 tokens)   : WR Banco = {t_low:5.1f}%")
    print(f"   • Uso Médio (4 a 6 tokens)   : WR Banco = {t_med:5.1f}%")
    print(f"   • Uso Alto (7+ tokens)       : WR Banco = {t_high:5.1f}%")

    total_time = time.time() - t0
    print(f"\n⚡ Pipeline causal executado com sucesso em {total_time:.2f}s!")

    # Exportação JSON
    if export_json:
        payload = {
            'n_games': n_games,
            'total_time_seconds': total_time,
            'baseline_banker_win_rate': float(b_win_base),
            'top_rules': rules[:6],
            'feature_importance': [
                {
                    'feature': r['feature'],
                    'description': r['description'],
                    'rf_importance': float(r['rf_importance']),
                    'odds_ratio': float(r['odds_ratio'])
                } for _, r in importance_df.iterrows()
            ],
            'shap_ranking': [
                {
                    'feature': r['feature'],
                    'mean_abs_shap': float(r['mean_abs_shap'])
                } for _, r in shap_df.iterrows()
            ],
            'tipping_points': {
                'intern_appearances_wr': {
                    str(app): float(df[df['intern_comm_appearances'] == app]['banker_won'].mean() * 100)
                    for app in range(5) if len(df[df['intern_comm_appearances'] == app]) > 0
                },
                'tier1_impact': {'win': float(wr_r1_win), 'loss': float(wr_r1_loss)},
                'tier3_impact': {'win': float(wr_r3_win), 'loss': float(wr_r3_loss)},
                'token_usage_wr': {'0_3': float(t_low), '4_6': float(t_med), '7_plus': float(t_high)}
            }
        }
        os.makedirs(os.path.dirname(export_json), exist_ok=True)
        with open(export_json, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        print(f"📁 Relatório causal exportado com sucesso em: {export_json}")

    return {
        'rules': rules,
        'importance': importance_df,
        'shap': shap_df
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Análise Causal & SHAP - BTG Madagascar v14.0")
    parser.add_argument("--games", "-n", type=int, default=20000, help="Número de partidas a simular (padrão: 20.000)")
    parser.add_argument("--workers", "-w", type=int, default=None, help="Número de workers paralelos (padrão: CPU count)")
    parser.add_argument("--export", "-e", type=str, default="visualizer/data/causal_analysis_summary.json", help="Caminho para exportar relatório em JSON")
    args = parser.parse_args()

    run_causal_analysis(n_games=args.games, num_workers=args.workers, export_json=args.export)
