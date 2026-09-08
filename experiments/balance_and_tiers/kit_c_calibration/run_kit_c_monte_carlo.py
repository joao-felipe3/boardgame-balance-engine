#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BTG Madagascar - Simulação Monte Carlo Oficial: Kit C & Nova Economia
====================================================================
Configuração:
  - Carteira Inicial: Kit C (1x Cobalto, 1x Titânio, 2x Secretas)
  - Economia: Depleção por Participação + Dividendo de Banco (+1 Carta, +1 Token)
  - Catálogo: 7 Tiers Calibrados (T1: 3/4, T2: 4/5, T3: 7/6, T4: 8/8, T5: 10, T6: 13/14, T7: 16)
  - IA: Defesa Realista de Match Point + Perfis A, B e C
"""

import sys
import os
import time
import random
import argparse
from collections import Counter
from typing import Dict, List, Optional
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
sys.path.insert(0, os.path.dirname(__file__))

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

from btg.constants import CardType, Role, InternProfile, ContractSpec
from btg.player import PlayerAI
from btg.deck import ResourceCard, DeckManager
import btg.engine as engine_mod
from run_comparison import _update_suspicions

# Catálogo Oficial Calibrado para a Nova Economia (Kit C)
CATALOG_OFFICIAL_KIT_C = {
    1: [
        ContractSpec("Arbitragem Simples", 1, committee_size=2, cost_per_player=1, target_value=3),
        ContractSpec("Exportacao de Baunilha", 1, committee_size=2, cost_per_player=1, target_value=4,
                     req_commodity=CardType.VN, req_commodity_count=1),
    ],
    2: [
        ContractSpec("Mineracao de Cobalto", 2, committee_size=2, cost_per_player=1, target_value=5,
                     req_commodity=CardType.CO, req_commodity_count=1),
        ContractSpec("Lote Agricola", 2, committee_size=2, cost_per_player=1, target_value=5,
                     req_commodity=CardType.VN, req_commodity_count=1),
    ],
    3: [
        ContractSpec("Sindicato de Titanio", 3, committee_size=3, cost_per_player=1, target_value=6,
                     req_commodity=CardType.TI, req_commodity_count=2),
        ContractSpec("Logistica Portuaria", 3, committee_size=3, cost_per_player=1, target_value=6,
                     req_commodity=CardType.CO, req_commodity_count=2),
    ],
    4: [
        ContractSpec("Refino Metalurgico", 4, committee_size=3, cost_per_player=1, target_value=7,
                     req_commodity=CardType.TI, req_commodity_count=2),
        ContractSpec("Consorcio Agro-Industrial", 4, committee_size=3, cost_per_player=1, target_value=8,
                     req_commodity=CardType.VN, req_commodity_count=2),
    ],
    5: [
        ContractSpec("Megaconsorcio Industrial", 5, committee_size=3, cost_per_player=1, target_value=10,
                     req_commodity=CardType.TI, req_commodity_count=2,
                     expandable_on_prior_failure=True, expanded_committee_size=4),
        ContractSpec("Cofre de Commodities", 5, committee_size=3, cost_per_player=1, target_value=10,
                     req_commodity=CardType.VN, req_commodity_count=2,
                     expandable_on_prior_failure=True, expanded_committee_size=4),
    ],
    6: [
        ContractSpec("Complexo Greenfield", 6, committee_size=3, cost_per_player=2, target_value=13,
                     req_commodity=CardType.TI, req_commodity_count=2),
        ContractSpec("Consorcio Safira", 6, committee_size=3, cost_per_player=2, target_value=14,
                     req_commodity=CardType.SF, req_commodity_count=2),
    ],
    7: [
        ContractSpec("Holding Global BTG", 7, committee_size=3, cost_per_player=2, target_value=15,
                     req_commodity=CardType.SF, req_commodity_count=1),
        ContractSpec("Fundo Soberano Madagascar", 7, committee_size=3, cost_per_player=2, target_value=16,
                     req_commodity=CardType.TI, req_commodity_count=2),
    ],
}


def simulate_one_match(game_idx: int, profile: InternProfile, seed: Optional[int] = None) -> Dict:
    rng = random.Random(seed if seed is not None else (int(time.time() * 1000) ^ game_idx))
    roles = [Role.BANKER] * 3 + [Role.INTERN] * 2
    rng.shuffle(roles)
    intern_count = 0
    players = []
    for i in range(5):
        is_active = (roles[i] == Role.INTERN and intern_count == 0)
        if roles[i] == Role.INTERN:
            intern_count += 1
        players.append(PlayerAI(i, roles[i], profile, rng, is_active_saboteur=is_active))

    deck = DeckManager(seed=rng.randint(0, 10**9))
    deck.refill_open_market(3)

    # Kit C: 1 Cobalto, 1 Titânio, 2 Secretas
    for p in players:
        p.hand = [ResourceCard(CardType.CO), ResourceCard(CardType.TI)] + deck.draw_blind(2)

    banker_score = 0
    intern_score = 0
    round_count = 0
    prev_tier3_failed = False
    prev_tier4_failed = False
    tier_outcomes = {}
    conflict_pairs: List[set] = []
    has_played = {p.id: False for p in players}
    r2_passed_comm: List[int] = []

    while banker_score < 4 and intern_score < 4 and round_count < 7:
        round_count += 1
        tier_num = round_count
        contract_spec = rng.choice(CATALOG_OFFICIAL_KIT_C[tier_num])

        # Expansão para 4 ops no Megaconsórcio se T3 ou T4 falhou
        if contract_spec.expandable_on_prior_failure and (tier_num == 5 and (prev_tier3_failed or prev_tier4_failed)):
            contract = ContractSpec(
                contract_spec.name, contract_spec.tier,
                committee_size=contract_spec.expanded_committee_size,
                cost_per_player=contract_spec.cost_per_player,
                target_value=contract_spec.target_value,
                req_commodity=contract_spec.req_commodity,
                req_commodity_count=contract_spec.req_commodity_count,
                expandable_on_prior_failure=True,
                expanded_committee_size=contract_spec.expanded_committee_size
            )
        else:
            contract = contract_spec

        curr_chair = (round_count - 1) % 5
        consecutive_vetoes = 0
        approved_committee = None
        promised_supplier = None
        all_declarations = {}

        while consecutive_vetoes < 3 and approved_committee is None:
            chair = players[curr_chair]
            declarations = {p.id: p.make_public_declaration(contract, round_count) for p in players}
            all_declarations = declarations

            chosen_comm, assigned_req_player = engine_mod.choose_optimal_committee(
                chair, players, contract, declarations, conflict_pairs=conflict_pairs
            )

            votes = {p.id: p.vote_on_proposal(curr_chair, chosen_comm, contract, round_count) for p in players}

            if sum(votes.values()) >= 3:
                approved_committee = chosen_comm
                promised_supplier = assigned_req_player
            else:
                consecutive_vetoes += 1
                curr_chair = (curr_chair + 1) % 5

        if approved_committee is None:
            import itertools
            all_comms = list(itertools.combinations(range(5), contract.committee_size))

            def _forced_score(cm):
                supplier_count = 0
                if contract.req_commodity is not None and all_declarations:
                    supplier_count = sum(
                        1 for pid in cm
                        if all_declarations.get(pid) and all_declarations[pid].claims_req
                    )
                has_coverage = (
                    contract.req_commodity is None or
                    supplier_count >= contract.req_commodity_count
                )
                bench_in_comm = sum(
                    1 for pid in cm
                    if all_declarations.get(pid) and all_declarations[pid].prefers_bench
                )
                total_sus = sum(
                    sum(p.suspicions[cid] for p in players if p.role == Role.BANKER)
                    for cid in cm
                )
                return (not has_coverage, bench_in_comm, total_sus)

            best_comm = min(all_comms, key=_forced_score)
            approved_committee = list(best_comm)

            if contract.req_commodity is not None and all_declarations:
                forced_suppliers = [
                    pid for pid in approved_committee
                    if all_declarations.get(pid) and all_declarations[pid].claims_req
                ]
                if len(forced_suppliers) >= contract.req_commodity_count:
                    forced_suppliers.sort(
                        key=lambda pid: all_declarations[pid].req_commodity_value,
                        reverse=True
                    )
                    promised_supplier = forced_suppliers[:contract.req_commodity_count]
                else:
                    promised_supplier = None
            else:
                promised_supplier = None

        for pid in approved_committee:
            has_played[pid] = True

        # Dividendo de Banco Completo (+1 Carta E +1 Token de Juros):
        # O operador que fica no banco acumula rendimento de capital (+1 Token, teto 3)
        # e recompõe sua carteira com 1 nova carta de insumo.
        for p in players:
            if p.id not in approved_committee:
                p.accumulate_holding_interest()
                if p.role == Role.BANKER:
                    preferred = None
                    for ct in [contract.req_commodity, CardType.WILD, CardType.SF, CardType.TI]:
                        if ct is not None and ct in deck.open_market:
                            preferred = ct
                            break
                    if preferred:
                        c = deck.draw_from_market(preferred)
                        p.public_known_cards.append(preferred)
                    else:
                        c = deck.draw_blind(1)[0]
                else:
                    c = deck.draw_blind(1)[0]
                p.hand.append(c)

        comm_objs = [players[pid] for pid in approved_committee]

        # Contribuições
        submitted_all_cards: List[ResourceCard] = []
        total_tokens_spent = 0
        is_match_point = (banker_score == 3)

        sup_list = [promised_supplier] if isinstance(promised_supplier, int) else (list(promised_supplier) if promised_supplier else [])
        planning_order = []
        for s_id in sup_list:
            sup_obj = next((p for p in comm_objs if p.id == s_id), None)
            if sup_obj and sup_obj not in planning_order:
                planning_order.append(sup_obj)
        for p in comm_objs:
            if p not in planning_order:
                planning_order.append(p)

        cumulative_committed_val = 0
        for idx, p in enumerate(planning_order):
            is_req_responsible = (p.id in sup_list)
            rem_members = len(planning_order) - idx
            rem_target = max(0, contract.target_value - cumulative_committed_val)
            quota_p = rem_target / rem_members

            should_sabotage = False
            if p.role == Role.INTERN:
                # Defesa de match point: nenhum traidor deixa o adversário fechar o jogo de graça
                if is_match_point:
                    should_sabotage = True
                elif p.profile == InternProfile.A_AGGRESSIVE:
                    # B.2: Se a R1 já falhou (intern_score >= 1), o estagiário na R2 joga camuflado
                    # para ganhar crédito de sucesso e não entregar 0x2 óbvio.
                    if round_count == 2 and intern_score >= 1:
                        should_sabotage = False
                    else:
                        should_sabotage = True
                elif p.profile == InternProfile.B_SLEEPER:
                    if round_count >= 3:
                        # Sleeper ativo: sabotagem total a partir da R3
                        should_sabotage = True
                    elif round_count == 2 and banker_score >= 1:
                        # Despertar do Sleeper: se o Banco abriu 1x0 na R1, o Sleeper
                        # tem 50% de chance de agir para impedir que os legalistas abram 2x0 de graça
                        should_sabotage = (rng.random() < 0.50)
                    else:
                        should_sabotage = False
                elif p.profile == InternProfile.C_HEDGE:
                    has_toxic = any(c.card_type == CardType.TOXIC for c in p.hand)
                    toxic_sab = has_toxic and round_count >= 3
                    # Negação de cota: antecipado de R4 para R3 (Tier 3 já exige 2x insumos)
                    quota_sab = is_req_responsible and contract.req_commodity is not None and round_count >= 3
                    # Sabotagem geral: antecipado de R5 para R4
                    should_sabotage = toxic_sab or quota_sab or (round_count >= 4)

            if not should_sabotage:
                actual_cards, actual_tokens, honest_val = p.plan_honest_contribution(
                    contract, round_count, is_req_responsible, quota_p, is_match_point=is_match_point
                )
                cumulative_committed_val += honest_val
            else:
                actual_cards, actual_tokens = p.plan_sabotage_contribution(contract, round_count, is_req_responsible)

            p.interest_tokens -= actual_tokens
            total_tokens_spent += actual_tokens
            for c in actual_cards:
                if c in p.hand:
                    p.hand.remove(c)
                if c.card_type in p.public_known_cards:
                    p.public_known_cards.remove(c.card_type)
            submitted_all_cards.extend(actual_cards)

        deck.discard(submitted_all_cards)
        is_pure = all(p.role == Role.BANKER for p in comm_objs)
        is_success, total_val, has_req = engine_mod.evaluate_contract_outcome(
            submitted_all_cards, total_tokens_spent, contract, is_pure_banker_committee=is_pure
        )

        tier_outcomes[tier_num] = is_success
        if tier_num == 3:
            prev_tier3_failed = not is_success
        elif tier_num == 4:
            prev_tier4_failed = not is_success

        if is_success:
            banker_score += 1
            for p in comm_objs:
                p.claim_success_credit()
            if round_count == 2:
                r2_passed_comm = list(approved_committee)
        else:
            intern_score += 1

        _update_suspicions(
            players, comm_objs, is_success,
            contract=contract, has_req=has_req, sup_list=sup_list, conflict_pairs=conflict_pairs,
            has_played=has_played, r2_passed_comm=r2_passed_comm, round_count=round_count
        )

    winner = Role.BANKER.value if banker_score >= 4 else Role.INTERN.value
    score_str = f"{banker_score} x {intern_score}"

    return {
        'game_idx': game_idx,
        'profile': profile.value,
        'b_score': banker_score,
        'i_score': intern_score,
        'score': score_str,
        'rounds': round_count,
        'winner': winner,
        'tier_outcomes': tier_outcomes
    }


def run_monte_carlo_kit_c(n_games: int = 100000, seed_base: int = 424242):
    print("=" * 80)
    print(f" SIMULAÇÃO MONTE CARLO OFICIAL: KIT C & NOVA ECONOMIA ({n_games:,} PARTIDAS) ")
    print("=" * 80)
    print(f" * Kit Inicial : Cobalto (+1), Titânio (+3), 2 Secretas")
    print(f" * Economia    : Depleção por Participação & Dividendo de Banco (+1 Carta, +1 Token)")
    print(f" * Catálogo    : 7 Tiers Recalibrados")
    print("-" * 80)

    t0 = time.time()
    results = []
    profiles = [InternProfile.A_AGGRESSIVE, InternProfile.B_SLEEPER, InternProfile.C_HEDGE]

    for i in range(n_games):
        prof = profiles[i % 3]
        res = simulate_one_match(i, prof, seed=seed_base + i)
        results.append(res)

        if (i + 1) % max(1, (n_games // 10)) == 0 or (i + 1) == n_games:
            pct = (i + 1) / n_games * 100
            print(f"   [Progresso] {i + 1:7,d} / {n_games:,} ({pct:5.1f}%) | Tempo decorrido: {time.time() - t0:4.1f}s")
            sys.stdout.flush()

    elapsed = time.time() - t0
    df = pd.DataFrame(results)

    b_wins = (df["winner"] == Role.BANKER.value).sum()
    i_wins = (df["winner"] == Role.INTERN.value).sum()
    b_wr = b_wins / n_games * 100
    i_wr = i_wins / n_games * 100

    print("\n" + "=" * 80)
    print(f"             RELATÓRIO DE BALANCEAMENTO & DISTRIBUIÇÃO ({n_games:,} PARTIDAS)")
    print("=" * 80)
    print(f"\n1. EQUILÍBRIO GLOBAL")
    print(f"   - [Banqueiros]  : {b_wr:6.2f}% ({b_wins:,} vitórias)")
    print(f"   - [Estagiários] : {i_wr:6.2f}% ({i_wins:,} vitórias)")
    print(f"   - Duração Média : {df['rounds'].mean():.2f} ± {df['rounds'].std():.2f} rodadas")
    print(f"   - Tempo Total   : {elapsed:.1f} segundos ({n_games/elapsed:.0f} partidas/seg)")

    print(f"\n2. MATRIZ COMPLETA DE PLACARES FINAIS")
    print("-" * 80)
    print(f"{'Placar':<15} | {'Ocorrências':<12} | {'Frequência':<10} | {'Classificação & Impacto Dramático'}")
    print("-" * 80)

    score_counts = df["score"].value_counts()
    all_possible_scores = [
        "4 x 0", "4 x 1", "4 x 2", "4 x 3",
        "3 x 4", "2 x 4", "1 x 4", "0 x 4"
    ]

    for sc in all_possible_scores:
        cnt = score_counts.get(sc, 0)
        pct = cnt / n_games * 100
        desc = ""
        if sc == "4 x 0":
            desc = "⚠️ Sweep Banqueiros (Alvo: controlado < 15%)"
        elif sc in ("4 x 3", "3 x 4"):
            desc = "🔥 Clímax da 7ª Rodada (Decisão no limite)"
        elif sc in ("4 x 2", "2 x 4"):
            desc = "⚖️ Disputa Equilibrada de 6 Rodadas"
        elif sc in ("4 x 1", "1 x 4"):
            desc = "🎯 Vitória Sólida de 5 Rodadas"
        elif sc == "0 x 4":
            desc = "💀 Massacre Estagiários"

        print(f"{sc:<15} | {cnt:>10,d}  | {pct:>8.2f}% | {desc}")

    climax_count = score_counts.get("4 x 3", 0) + score_counts.get("3 x 4", 0)
    climax_pct = climax_count / n_games * 100
    four_zero_pct = score_counts.get("4 x 0", 0) / n_games * 100

    print("-" * 80)
    print(f"   * Taxa Total de Clímax (Decisão na R7 - 4x3 ou 3x4): {climax_pct:5.2f}%")
    print(f"   * Taxa de 4x0 (Sweep Banqueiros): {four_zero_pct:5.2f}%")

    print(f"\n3. PERFORMANCE COMPARATIVA POR PERFIL DE IA")
    print("-" * 80)
    print(f"{'Perfil do Estagiário':<38} | {'WR Estagiários':<16} | {'WR Banqueiros':<15} | {'Duração':<10}")
    print("-" * 80)
    for prof in profiles:
        sub = df[df["profile"] == prof.value]
        sub_iw = (sub["winner"] == Role.INTERN.value).sum()
        sub_bw = (sub["winner"] == Role.BANKER.value).sum()
        sub_len = len(sub)
        print(f"{prof.value:<38} | {(sub_iw/sub_len)*100:>14.2f}% | {(sub_bw/sub_len)*100:>13.2f}% | {sub['rounds'].mean():>6.2f} ops")

    print(f"\n4. TAXA DE APROVAÇÃO POR TIER")
    print("-" * 80)
    for t in range(1, 8):
        t_games = [r['tier_outcomes'][t] for r in results if t in r['tier_outcomes']]
        if t_games:
            t_succ = sum(1 for x in t_games if x)
            print(f"   * Tier {t}: {t_succ/len(t_games)*100:5.1f}% de aprovação ({t_succ:,} de {len(t_games):,} tentativas)")

    print("=" * 80)
    return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Monte Carlo Kit C e Nova Economia")
    parser.add_argument("--games", "-n", type=int, default=30000, help="Número de partidas (padrão: 30000)")
    args = parser.parse_args()
    run_monte_carlo_kit_c(args.games)
