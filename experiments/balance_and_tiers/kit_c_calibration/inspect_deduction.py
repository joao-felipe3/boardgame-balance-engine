#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise Profunda do Sistema de Dedução dos Banqueiros
Mede acurácia dedutiva, identificação de traidores e impacto na formação de comitês.
"""

import sys
import os
import random
import time
from collections import defaultdict
import numpy as np

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
from run_kit_c_monte_carlo import CATALOG_OFFICIAL_KIT_C


def analyze_deduction_and_mechanics(n_games: int = 10000):
    print("=" * 80)
    print(f" DIAGNÓSTICO DO SISTEMA DE DEDUÇÃO E FORMAÇÃO DE COMITÊS ({n_games:,} PARTIDAS)")
    print("=" * 80)

    profiles = [InternProfile.A_AGGRESSIVE, InternProfile.B_SLEEPER, InternProfile.C_HEDGE]

    # Métricas a coletar por Round (1 a 7)
    interns_in_committee = defaultdict(list)
    committee_pure_bankers = defaultdict(int)
    committee_total = defaultdict(int)
    
    # Falhas por motivo: Sabotagem vs Falha Natural (falta de pontos/cota)
    failures_by_tier = defaultdict(lambda: {'total': 0, 'sabotage': 0, 'natural': 0})
    successes_by_tier = defaultdict(int)

    # Acurácia de dedução por Round:
    # Para cada Banqueiro, qual a média de suspeita atribuída aos Estagiários vs Banqueiros?
    sus_interns_by_round = defaultdict(list)
    sus_bankers_by_round = defaultdict(list)
    traitor_detected_count = defaultdict(list) # quantos dos 2 traidores foram detectados (sus >= 0.70 ou known_traitors)

    for g_idx in range(n_games):
        rng = random.Random(555000 + g_idx)
        prof = profiles[g_idx % 3]
        roles = [Role.BANKER] * 3 + [Role.INTERN] * 2
        rng.shuffle(roles)
        intern_count = 0
        players = []
        for i in range(5):
            is_active = (roles[i] == Role.INTERN and intern_count == 0)
            if roles[i] == Role.INTERN:
                intern_count += 1
            players.append(PlayerAI(i, roles[i], prof, rng, is_active_saboteur=is_active))

        deck = DeckManager(seed=rng.randint(0, 10**9))
        deck.refill_open_market(3)
        for p in players:
            p.hand = [ResourceCard(CardType.CO), ResourceCard(CardType.TI)] + deck.draw_blind(2)

        banker_pids = [p.id for p in players if p.role == Role.BANKER]
        intern_pids = [p.id for p in players if p.role == Role.INTERN]

        b_score = 0
        i_score = 0
        round_count = 0
        prev_tier3_failed = False
        prev_tier4_failed = False

        while b_score < 4 and i_score < 4 and round_count < 7:
            round_count += 1
            contract_spec = rng.choice(CATALOG_OFFICIAL_KIT_C[round_count])
            if contract_spec.expandable_on_prior_failure and (round_count == 5 and (prev_tier3_failed or prev_tier4_failed)):
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

            chair = players[(round_count - 1) % 5]
            decs = {p.id: p.make_public_declaration(contract, round_count) for p in players}
            chosen_comm, assigned_req = engine_mod.choose_optimal_committee(chair, players, contract, decs)

            # Votação
            votes = {p.id: p.vote_on_proposal(chair.id, chosen_comm, contract, round_count) for p in players}
            if sum(votes.values()) < 3:
                # veto: passa pro próximo
                chair = players[(chair.id + 1) % 5]
                chosen_comm, assigned_req = engine_mod.choose_optimal_committee(chair, players, contract, decs)

            # Bench dividend
            for p in players:
                if p.id not in chosen_comm:
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

            # Estatística de Comitê
            comm_interns = [pid for pid in chosen_comm if pid in intern_pids]
            interns_in_committee[round_count].append(len(comm_interns))
            committee_total[round_count] += 1
            if len(comm_interns) == 0:
                committee_pure_bankers[round_count] += 1

            # Aportes
            comm_objs = [players[pid] for pid in chosen_comm]
            submitted_cards = []
            total_tokens = 0
            any_sabotage = False
            is_match_point = (b_score == 3)

            for p in comm_objs:
                is_req_resp = (p.id == assigned_req)
                should_sab = False
                if p.role == Role.INTERN:
                    if is_match_point:
                        should_sab = True
                    elif p.profile == InternProfile.A_AGGRESSIVE:
                        should_sab = True
                    elif p.profile == InternProfile.B_SLEEPER:
                        should_sab = (round_count >= 3) if p.is_active_saboteur else (round_count >= 4)
                    elif p.profile == InternProfile.C_HEDGE:
                        has_toxic = any(c.card_type == CardType.TOXIC for c in p.hand)
                        toxic_sab = has_toxic and round_count >= 3
                        quota_sab = is_req_resp and contract.req_commodity is not None and round_count >= 4
                        should_sab = toxic_sab or quota_sab or (round_count >= 5)

                if should_sab:
                    any_sabotage = True
                    c, t = p.plan_sabotage_contribution(contract, round_count, is_req_resp)
                else:
                    c, t, _ = p.plan_honest_contribution(
                        contract, round_count, is_req_resp, contract.target_value / len(chosen_comm),
                        is_match_point=is_match_point
                    )
                submitted_cards.extend(c)
                total_tokens += t
                p.interest_tokens -= t
                for card in c:
                    if card in p.hand: p.hand.remove(card)

            deck.discard(submitted_cards)
            is_pure = (len(comm_interns) == 0)
            is_success, total_val, has_req = engine_mod.evaluate_contract_outcome(
                submitted_cards, total_tokens, contract, is_pure_banker_committee=is_pure
            )

            if round_count == 3:
                prev_tier3_failed = not is_success
            elif round_count == 4:
                prev_tier4_failed = not is_success

            if is_success:
                b_score += 1
                successes_by_tier[round_count] += 1
                for p in comm_objs: p.claim_success_credit()
                # Atualiza suspeitas no sucesso (regras engine v14.0)
                decay = 0.05 if contract.tier <= 2 else (0.15 if contract.tier <= 4 else 0.30)
                for bp_id in banker_pids:
                    bp = players[bp_id]
                    for cid in chosen_comm:
                        if cid != bp.id and cid not in bp.known_traitors:
                            bp.suspicions[cid] = max(0.05, bp.suspicions[cid] - decay)
            else:
                i_score += 1
                failures_by_tier[round_count]['total'] += 1
                if any_sabotage:
                    failures_by_tier[round_count]['sabotage'] += 1
                else:
                    failures_by_tier[round_count]['natural'] += 1

                # Atualiza suspeitas na falha (regras engine v14.0)
                for bp_id in banker_pids:
                    bp = players[bp_id]
                    if len(chosen_comm) == 2 and bp.id in chosen_comm:
                        partner = next(cid for cid in chosen_comm if cid != bp.id)
                        bp.suspicions[partner] = 1.00
                        bp.known_traitors.add(partner)
                    elif len(chosen_comm) == 2 and bp.id not in chosen_comm:
                        for cid in chosen_comm:
                            bp.suspicions[cid] = min(0.60, bp.suspicions[cid] + 0.20)
                    else:
                        penalty = 0.15 if len(chosen_comm) >= 4 else 0.25
                        for cid in chosen_comm:
                            if cid != bp.id:
                                bp.suspicions[cid] = min(0.85, bp.suspicions[cid] + penalty)

            # Medição da percepção dedutiva dos Banqueiros no final desta rodada
            for bp_id in banker_pids:
                bp = players[bp_id]
                # Média de suspeita que este Banqueiro tem sobre os 2 Estagiários
                intern_sus = [bp.suspicions[ip] for ip in intern_pids]
                banker_sus = [bp.suspicions[other_b] for other_b in banker_pids if other_b != bp.id]
                sus_interns_by_round[round_count].append(np.mean(intern_sus))
                sus_bankers_by_round[round_count].append(np.mean(banker_sus))
                
                # Traidores com suspeita >= 0.65 ou em known_traitors
                detected = sum(1 for ip in intern_pids if bp.suspicions[ip] >= 0.65 or ip in bp.known_traitors)
                traitor_detected_count[round_count].append(detected)

    print("\n1. EVOLUÇÃO DEDUTIVA DOS BANQUEIROS (POR RODADA)")
    print("-" * 80)
    print(f"{'Rodada':<8} | {'Suspeita Méd. Estagiários':<26} | {'Suspeita Méd. Banqueiros':<25} | {'Traidores Detectados (de 2)':<25}")
    print("-" * 80)
    for r in range(1, 8):
        if sus_interns_by_round[r]:
            m_i = np.mean(sus_interns_by_round[r])
            m_b = np.mean(sus_bankers_by_round[r])
            m_det = np.mean(traitor_detected_count[r])
            print(f"Tier {r:<3} | {m_i*100:>23.1f}% | {m_b*100:>22.1f}% | {m_det:>20.2f} / 2.00")

    print("\n2. INFILTRAÇÃO E COMPOSIÇÃO DOS COMITÊS")
    print("-" * 80)
    print(f"{'Rodada':<8} | {'Total Tentativas':<17} | {'Comitê 100% Banqueiro':<23} | {'Média Estagiários no Comitê'}")
    print("-" * 80)
    for r in range(1, 8):
        tot = committee_total[r]
        if tot > 0:
            pure = committee_pure_bankers[r]
            pct_pure = pure / tot * 100
            avg_interns = np.mean(interns_in_committee[r])
            print(f"Tier {r:<3} | {tot:>14,d}  | {pure:>10,d} ({pct_pure:5.1f}%)   | {avg_interns:4.2f} estagiários")

    print("\n3. RAIO-X DAS FALHAS: SABOTAGEM VS FALHA NATURAL (FALTA DE RECURSOS/COTA)")
    print("-" * 80)
    print(f"{'Rodada':<8} | {'Taxa Sucesso':<13} | {'Total Falhas':<13} | {'Por Sabotagem (Traição)':<25} | {'Falha Natural (Recursos)'}")
    print("-" * 80)
    for r in range(1, 8):
        succ = successes_by_tier[r]
        f_data = failures_by_tier[r]
        tot_f = f_data['total']
        tot_attempts = succ + tot_f
        if tot_attempts > 0:
            succ_rate = succ / tot_attempts * 100
            sab_pct = f_data['sabotage'] / tot_f * 100 if tot_f > 0 else 0
            nat_pct = f_data['natural'] / tot_f * 100 if tot_f > 0 else 0
            print(f"Tier {r:<3} | {succ_rate:>10.1f}%  | {tot_f:>10,d}   | {f_data['sabotage']:>8,d} ({sab_pct:5.1f}%)        | {f_data['natural']:>8,d} ({nat_pct:5.1f}%)")

    print("=" * 80)


if __name__ == '__main__':
    analyze_deduction_and_mechanics(10000)
