#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BTG Madagascar - Comparação de 3 Configurações Econômicas
=========================================================
Opção A: Economia antiga (replenishment completo, targets validados ~52%)
Opção B: Nova economia + Profile C ativado mais cedo (Tier 2, 30%)
Opção C: Nova economia + Kit inicial sem VN garantido (CO+TI+2 secrets)

Cada opção roda partidas de forma independente sem alterar o engine oficial.
"""

import sys
import os
import random
import time
import itertools
from typing import List, Dict, Tuple, Optional
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import btg.engine as engine_mod
import btg.constants as constants_mod
from btg.constants import CardType, Role, InternProfile, ContractSpec
from btg.player import PlayerAI, PlayerDeclaration
from btg.deck import ResourceCard, DeckManager

# ─────────────────────────────────────────────────────────────────────────────
# CATÁLOGOS DE MISSÕES POR OPÇÃO
# ─────────────────────────────────────────────────────────────────────────────

CATALOG_A = {
    1: [
        ContractSpec("Arbitragem Simples", 1, committee_size=2, cost_per_player=1, target_value=3),
        ContractSpec("Exportacao de Baunilha", 1, committee_size=2, cost_per_player=1, target_value=4,
                     req_commodity=CardType.VN, req_commodity_count=1),
    ],
    2: [
        ContractSpec("Mineracao de Cobalto", 2, committee_size=2, cost_per_player=1, target_value=4,
                     req_commodity=CardType.CO, req_commodity_count=1),
        ContractSpec("Lote Agricola", 2, committee_size=2, cost_per_player=1, target_value=4,
                     req_commodity=CardType.VN, req_commodity_count=1),
    ],
    3: [
        ContractSpec("Sindicato de Titanio", 3, committee_size=3, cost_per_player=1, target_value=8,
                     req_commodity=CardType.TI, req_commodity_count=2),
        ContractSpec("Logistica Portuaria", 3, committee_size=3, cost_per_player=1, target_value=7,
                     req_commodity=CardType.CO, req_commodity_count=2),
    ],
    4: [
        ContractSpec("Refino Metalurgico", 4, committee_size=3, cost_per_player=1, target_value=9,
                     req_commodity=CardType.TI, req_commodity_count=2),
        ContractSpec("Consorcio Agro-Industrial", 4, committee_size=3, cost_per_player=1, target_value=9,
                     req_commodity=CardType.VN, req_commodity_count=2),
    ],
    5: [
        ContractSpec("Megaconsorcio Industrial", 5, committee_size=3, cost_per_player=1, target_value=12,
                     req_commodity=CardType.TI, req_commodity_count=2,
                     expandable_on_prior_failure=True, expanded_committee_size=4),
        ContractSpec("Cofre de Commodities", 5, committee_size=3, cost_per_player=1, target_value=12,
                     req_commodity=CardType.VN, req_commodity_count=2,
                     expandable_on_prior_failure=True, expanded_committee_size=4),
    ],
    6: [
        ContractSpec("Complexo Greenfield", 6, committee_size=3, cost_per_player=2, target_value=16,
                     req_commodity=CardType.TI, req_commodity_count=2),
        ContractSpec("Consorcio Safira", 6, committee_size=3, cost_per_player=2, target_value=17,
                     req_commodity=CardType.SF, req_commodity_count=2),
    ],
    7: [
        ContractSpec("Holding Global BTG", 7, committee_size=3, cost_per_player=2, target_value=18,
                     req_commodity=CardType.SF, req_commodity_count=2),
    ],
}

CATALOG_BC = {
    1: [
        ContractSpec("Arbitragem Simples", 1, committee_size=2, cost_per_player=1, target_value=4),
        ContractSpec("Exportacao de Baunilha", 1, committee_size=2, cost_per_player=1, target_value=6,
                     req_commodity=CardType.VN, req_commodity_count=1),
    ],
    2: [
        ContractSpec("Mineracao de Cobalto", 2, committee_size=2, cost_per_player=1, target_value=4,
                     req_commodity=CardType.CO, req_commodity_count=1),
        ContractSpec("Lote Agricola", 2, committee_size=2, cost_per_player=1, target_value=6,
                     req_commodity=CardType.VN, req_commodity_count=1),
    ],
    3: [
        ContractSpec("Sindicato de Titanio", 3, committee_size=3, cost_per_player=1, target_value=7,
                     req_commodity=CardType.TI, req_commodity_count=2),
        ContractSpec("Logistica Portuaria", 3, committee_size=3, cost_per_player=1, target_value=6,
                     req_commodity=CardType.CO, req_commodity_count=2),
    ],
    4: [
        ContractSpec("Refino Metalurgico", 4, committee_size=3, cost_per_player=1, target_value=8,
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


def _run_game_loop(players, deck, rng, profile, catalog, economy='new', profile_c_early=False):
    banker_score = 0
    intern_score = 0
    round_count = 0
    score_log = []
    prev_tier3_failed = False
    prev_tier4_failed = False

    tiers_sequence = list(range(1, 8))
    tier_idx = 0

    while banker_score < 4 and intern_score < 4 and tier_idx < len(tiers_sequence):
        tier_num = tiers_sequence[tier_idx]
        tier_idx += 1
        round_count += 1

        available = catalog[tier_num]
        contract = rng.choice(available)

        if contract.expandable_on_prior_failure:
            if tier_num == 5 and prev_tier4_failed:
                contract = ContractSpec(
                    contract.name, contract.tier,
                    committee_size=contract.expanded_committee_size,
                    cost_per_player=contract.cost_per_player,
                    target_value=contract.target_value,
                    req_commodity=contract.req_commodity,
                    req_commodity_count=contract.req_commodity_count,
                    expandable_on_prior_failure=True,
                    expanded_committee_size=contract.expanded_committee_size
                )

        if economy == 'old':
            for p in players:
                needed = max(0, 4 - len(p.hand))
                for _ in range(needed):
                    if p.role == Role.BANKER and contract.req_commodity in deck.open_market:
                        c = deck.draw_from_market(contract.req_commodity)
                        p.public_known_cards.append(contract.req_commodity)
                    elif p.role == Role.BANKER and any(card in deck.open_market for card in [CardType.SF, CardType.WILD, CardType.TI]):
                        noble = next(card for card in [CardType.WILD, CardType.SF, CardType.TI] if card in deck.open_market)
                        c = deck.draw_from_market(noble)
                        p.public_known_cards.append(noble)
                    else:
                        c = deck.draw_blind(1)[0]
                    p.hand.append(c)

        consecutive_vetoes = 0
        approved_committee = None
        promised_supplier = None
        all_declarations = {}
        curr_chair = (round_count - 1) % 5

        while consecutive_vetoes < 3 and approved_committee is None:
            chair = players[curr_chair]
            declarations = {p.id: p.make_public_declaration(contract, round_count) for p in players}
            all_declarations = declarations

            chosen_comm, assigned_req_player = engine_mod.choose_optimal_committee(
                chair, players, contract, declarations
            )

            votes = {p.id: p.vote_on_proposal(curr_chair, chosen_comm, contract, round_count) for p in players}
            if sum(votes.values()) >= 3:
                approved_committee = chosen_comm
                promised_supplier = assigned_req_player
            else:
                consecutive_vetoes += 1
                curr_chair = (curr_chair + 1) % 5

        if approved_committee is None:
            all_comms = list(itertools.combinations(range(5), contract.committee_size))
            best_comm = min(all_comms, key=lambda cm: sum(
                sum(p.suspicions[cid] for p in players if p.role == Role.BANKER)
                for cid in cm
            ))
            approved_committee = list(best_comm)
            promised_supplier = None

        if economy == 'new':
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
        else:
            for p in players:
                if p.id not in approved_committee:
                    p.accumulate_holding_interest()

        comm_objs = [players[pid] for pid in approved_committee]

        submitted_cards, total_tokens, submitted_data, promised_vals = _coordinate_contributions(
            comm_objs, contract, round_count, promised_supplier, all_declarations, banker_score,
            profile_c_early=profile_c_early, rng=rng
        )

        deck.discard(submitted_cards)
        is_pure = all(p.role == Role.BANKER for p in comm_objs)
        is_success, total_val, has_req = engine_mod.evaluate_contract_outcome(
            submitted_cards, total_tokens, contract, is_pure_banker_committee=is_pure
        )

        if contract.tier == 3:
            prev_tier3_failed = not is_success
        elif contract.tier == 4:
            prev_tier4_failed = not is_success

        if is_success:
            banker_score += 1
            score_log.append('B')
            for p in comm_objs:
                p.claim_success_credit()
        else:
            intern_score += 1
            score_log.append('I')

        _update_suspicions(players, comm_objs, is_success)

    return {
        'banker_score': banker_score,
        'intern_score': intern_score,
        'rounds': round_count,
        'winner': 'BANKER' if banker_score >= 4 else 'INTERN',
        'score_key': f"{banker_score}x{intern_score}",
    }


def _coordinate_contributions(comm_objs, contract, round_num, promised_supplier_id,
                              all_declarations, banker_score, profile_c_early, rng):
    planning_order = []
    if promised_supplier_id is not None:
        sup_obj = next((p for p in comm_objs if p.id == promised_supplier_id), None)
        if sup_obj:
            planning_order.append(sup_obj)
    for p in comm_objs:
        if p not in planning_order:
            planning_order.append(p)

    submitted_all_cards: List[ResourceCard] = []
    total_tokens_spent = 0
    submitted_cards_data = []
    cumulative_committed_val = 0
    is_match_point = (banker_score == 3)
    promised_values = {}

    for idx, p in enumerate(planning_order):
        is_req_responsible = (p.id == promised_supplier_id)
        remaining_members = len(planning_order) - idx
        remaining_target = max(0, contract.target_value - cumulative_committed_val)
        quota_for_p = remaining_target / remaining_members

        declared_p_val = all_declarations[p.id].claimed_value if p.id in all_declarations else 0
        if p.role == Role.BANKER and round_num >= 3 and contract.target_value >= 8:
            quota_for_p = max(quota_for_p, min(declared_p_val, contract.target_value / contract.committee_size))

        should_sabotage = False
        if p.role == Role.INTERN:
            if p.profile == InternProfile.A_AGGRESSIVE:
                should_sabotage = True
            elif p.profile == InternProfile.B_SLEEPER:
                if p.is_active_saboteur:
                    should_sabotage = (round_num >= 3)
                else:
                    should_sabotage = (round_num >= 4)
            elif p.profile == InternProfile.C_HEDGE:
                if profile_c_early and contract.tier >= 2:
                    sabotage_prob = {2: 0.30, 3: 0.50, 4: 0.70}.get(contract.tier, 1.0)
                    should_sabotage = (rng.random() < sabotage_prob)
                else:
                    has_toxic = any(c.card_type == CardType.TOXIC for c in p.hand)
                    toxic_sabotage = has_toxic and round_num >= 3
                    quota_denial = is_req_responsible and contract.req_commodity is not None and round_num >= 4
                    late_sabotage = round_num >= 5
                    should_sabotage = toxic_sabotage or quota_denial or late_sabotage

        honest_cards, honest_tokens, honest_val = p.plan_honest_contribution(
            contract, round_num, is_req_responsible, quota_for_p, is_match_point=is_match_point
        )
        cumulative_committed_val += honest_val
        promised_values[p.id] = honest_val

        if not should_sabotage:
            actual_cards = honest_cards
            actual_tokens = honest_tokens
        else:
            actual_cards, actual_tokens = p.plan_sabotage_contribution(contract, round_num, is_req_responsible)

        p.interest_tokens -= actual_tokens
        total_tokens_spent += actual_tokens

        for c in actual_cards:
            if c in p.hand:
                p.hand.remove(c)
            if c.card_type in p.public_known_cards:
                p.public_known_cards.remove(c.card_type)

        submitted_all_cards.extend(actual_cards)
        submitted_cards_data.append({
            'player_id': p.id,
            'is_req_responsible': is_req_responsible,
            'tokens_spent': actual_tokens,
            'cards': [{'type': c.card_type.name, 'name': c.card_type.value, 'base': c.base_value} for c in actual_cards]
        })

    return submitted_all_cards, total_tokens_spent, submitted_cards_data, promised_values


def _update_suspicions(players, comm_objs, is_success, contract=None, has_req=True, sup_list=None, conflict_pairs=None, has_played=None, r2_passed_comm=None, round_count=None):
    bankers = [p for p in players if p.role == Role.BANKER]
    comm_ids = [p.id for p in comm_objs]

    if is_success:
        for b in bankers:
            for cid in comm_ids:
                if b.id != cid and cid not in b.known_traitors:
                    b.suspicions[cid] = max(0.05, b.suspicions[cid] - 0.06)
        if all(p.role == Role.BANKER for p in comm_objs):
            for b in bankers:
                for cid in comm_ids:
                    if b.id != cid and cid not in b.known_traitors:
                        b.suspicions[cid] = max(0.05, b.suspicions[cid] - 0.04)

        # Dedução de Vindicação (The Resistance / Sugestão C):
        if conflict_pairs is not None:
            for cp in list(conflict_pairs):
                v_members = [cid for cid in comm_ids if cid in cp]
                if len(v_members) == 1:
                    vindicated_pid = v_members[0]
                    traitor_pid = next(other for other in cp if other != vindicated_pid)
                    for b in bankers:
                        b.suspicions[traitor_pid] = 1.00
                        b.known_traitors.add(traitor_pid)
                        if b.id != vindicated_pid:
                            b.suspicions[vindicated_pid] = max(0.05, b.suspicions[vindicated_pid] - 0.15)
                    conflict_pairs.remove(cp)
    else:
        comm_size = len(comm_objs)
        sup_pids = sup_list if sup_list is not None else []
        if isinstance(sup_pids, int):
            sup_pids = [sup_pids]

        if comm_size == 2:
            if conflict_pairs is not None:
                conflict_pairs.append(set(comm_ids))
            partner_of = {cid: next(other for other in comm_ids if other != cid) for cid in comm_ids}
            for b in bankers:
                if b.id in comm_ids:
                    # Banqueiro DENTRO do comitê de 2: certeza absoluta de que o parceiro é traidor
                    partner_id = partner_of[b.id]
                    b.suspicions[partner_id] = 1.00
                    b.known_traitors.add(partner_id)
                else:
                    # Banqueiros de FORA: modulam a suspeita com base na evidência do cofre
                    if contract is not None and contract.req_commodity is not None:
                        if not has_req and sup_pids:
                            # Caso A: Faltou a commodity prometida (ex: Baunilha)
                            for cid in comm_ids:
                                if cid in sup_pids:
                                    b.suspicions[cid] = max(b.suspicions[cid], 0.80)
                                else:
                                    b.suspicions[cid] = max(b.suspicions[cid], 0.48)
                        else:
                            # Caso B: Commodity veio, mas faltou pontuação (< target_value) - Mentira de Liquidez
                            for cid in comm_ids:
                                if cid in sup_pids:
                                    b.suspicions[cid] = min(b.suspicions[cid], 0.35)
                                else:
                                    b.suspicions[cid] = max(b.suspicions[cid], 0.82)
                    else:
                        # Caso C: Arbitragem Simples (sem commodity, falha por pontuação <= 2 ou tóxico)
                        # Conflito 1v1 simétrico estilo Resistance: 0.52 (50% de probabilidade, sem lockout do inocente!)
                        for cid in comm_ids:
                            b.suspicions[cid] = 0.52

                non_comm = [pid for pid in range(5) if pid not in comm_ids and pid != b.id]
                for nc in non_comm:
                    if has_played is not None and not has_played.get(nc, False):
                        b.suspicions[nc] = max(0.42, b.suspicions[nc])
                    else:
                        b.suspicions[nc] = max(0.0, b.suspicions[nc] - 0.03)
        else:
            # Comitês de 3 ou mais membros
            # DEDUÇÃO DA DIFERENÇA SIMPLES (1-Difference Deduction):
            new_members = [cid for cid in comm_ids if cid not in r2_passed_comm] if (r2_passed_comm and len(r2_passed_comm) == 2) else []
            if round_count == 3 and len(new_members) == 1:
                culprit = new_members[0]
                for b in bankers:
                    if b.id != culprit:
                        b.suspicions[culprit] = 0.88
                        if conflict_pairs:
                            for cp in list(conflict_pairs):
                                if culprit in cp:
                                    vindicated = next(other for other in cp if other != culprit)
                                    b.suspicions[vindicated] = max(0.05, b.suspicions[vindicated] - 0.20)
                                    b.suspicions[culprit] = 1.00
                                    b.known_traitors.add(culprit)
                                    conflict_pairs.remove(cp)
                    for r2_id in r2_passed_comm:
                        if b.id != r2_id:
                            b.suspicions[r2_id] = min(0.40, b.suspicions[r2_id])
            else:
                if not has_req and sup_pids:
                    if len(sup_pids) == 1:
                        s_id = sup_pids[0]
                        for b in bankers:
                            if b.id != s_id:
                                b.suspicions[s_id] = 1.00
                                b.known_traitors.add(s_id)
                    else:
                        for b in bankers:
                            if b.id in sup_pids:
                                other_sups = [sid for sid in sup_pids if sid != b.id]
                                for osid in other_sups:
                                    b.suspicions[osid] = 1.00
                                    b.known_traitors.add(osid)

                penalty = 0.15 if comm_size >= 4 else 0.25
                for b in bankers:
                    for cid in comm_ids:
                        if b.id != cid and cid not in b.known_traitors:
                            b.suspicions[cid] = min(0.85, b.suspicions[cid] + penalty)

            non_comm = [pid for pid in range(5) if pid not in comm_ids and pid != b.id]
            for nc in non_comm:
                if has_played is not None and not has_played.get(nc, False):
                    b.suspicions[nc] = max(0.42, b.suspicions[nc])
                else:
                    b.suspicions[nc] = max(0.0, b.suspicions[nc] - 0.03)


def simulate_match_A(game_idx: int, profile: InternProfile, seed: Optional[int] = None) -> Dict:
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
    for p in players:
        p.hand = [ResourceCard(CardType.CO), ResourceCard(CardType.VN), ResourceCard(CardType.TI)] + deck.draw_blind(1)

    return _run_game_loop(players, deck, rng, profile, CATALOG_A, economy='old')


def simulate_match_B(game_idx: int, profile: InternProfile, seed: Optional[int] = None) -> Dict:
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
    for p in players:
        p.hand = [ResourceCard(CardType.CO), ResourceCard(CardType.VN), ResourceCard(CardType.TI)] + deck.draw_blind(1)

    return _run_game_loop(players, deck, rng, profile, CATALOG_BC, economy='new', profile_c_early=True)


def simulate_match_C(game_idx: int, profile: InternProfile, seed: Optional[int] = None) -> Dict:
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
    for p in players:
        p.hand = [ResourceCard(CardType.CO), ResourceCard(CardType.TI)] + deck.draw_blind(2)

    return _run_game_loop(players, deck, rng, profile, CATALOG_BC, economy='new', profile_c_early=False)


def run_option(name: str, sim_fn, n_games: int = 50000):
    profiles = [InternProfile.A_AGGRESSIVE, InternProfile.B_SLEEPER, InternProfile.C_HEDGE]
    all_results = []
    profile_results = {p: [] for p in profiles}
    score_counter = Counter()

    t0 = time.time()
    print(f"\n[{name}] Iniciando {n_games:,} partidas...")

    for i in range(n_games):
        prof = profiles[i % 3]
        res = sim_fn(i, prof)
        all_results.append(res)
        profile_results[prof].append(res)
        score_counter[res['score_key']] += 1

        if (i + 1) % 10000 == 0:
            elapsed = time.time() - t0
            pct = (i + 1) / n_games * 100
            print(f"   [{name}] {i+1:>6,} / {n_games:,} ({pct:5.1f}%) | Tempo: {elapsed:.1f}s")

    elapsed = time.time() - t0
    banker_wins = sum(1 for r in all_results if r['winner'] == 'BANKER')
    intern_wins = n_games - banker_wins
    avg_rounds = sum(r['rounds'] for r in all_results) / n_games

    print(f"\n{'='*70}")
    print(f"  RESULTADOS — {name}")
    print(f"{'='*70}")
    print(f"  Banqueiros: {banker_wins/n_games*100:.2f}% ({banker_wins:,} vitorias)")
    print(f"  Estagiarios: {intern_wins/n_games*100:.2f}% ({intern_wins:,} vitorias)")
    print(f"  Duracao Media: {avg_rounds:.2f} rodadas | Tempo: {elapsed:.1f}s")
    print(f"\n  PLACARES:")
    for score_key, count in sorted(score_counter.items(), key=lambda x: -x[1]):
        label = " [Climax]" if score_key in ("3x4", "4x3") else ""
        print(f"    {score_key:6s} : {count:>6,} ({count/n_games*100:5.1f}%){label}")

    print(f"\n  POR PERFIL:")
    for prof in profiles:
        pres = profile_results[prof]
        bw = sum(1 for r in pres if r['winner'] == 'BANKER')
        iw = len(pres) - bw
        print(f"    {prof.value[:30]:30s} | Intern: {iw/len(pres)*100:.2f}% | Banker: {bw/len(pres)*100:.2f}%")

    return {
        'name': name,
        'banker_wr': banker_wins/n_games*100,
        'intern_wr': intern_wins/n_games*100,
        'avg_rounds': avg_rounds,
        'score_counter': dict(score_counter),
        'n_games': n_games,
    }


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--games', type=int, default=30000)
    args = parser.parse_args()

    N = args.games
    print("=" * 70)
    print("  BTG MADAGASCAR — SIMULACAO COMPARATIVA DAS 3 OPCOES")
    print("=" * 70)
    print(f"  Partidas por opcao: {N:,}")

    res_A = run_option("OPCAO A (Economia Antiga / Baseline Validado)", simulate_match_A, N)
    res_B = run_option("OPCAO B (Nova Econ + Perfil C Antecipado)", simulate_match_B, N)
    res_C = run_option("OPCAO C (Nova Econ + Kit s/ VN Garantido)", simulate_match_C, N)

    print("\n" + "=" * 75)
    print("  RESUMO COMPARATIVO CONSOLIDADO")
    print("=" * 75)
    print(f"  {'Opcao':<40} {'Intern WR':>10} {'Banker WR':>10} {'4x0':>7} {'3x4':>7} {'Dur.':>6}")
    print("  " + "-" * 73)
    for r in [res_A, res_B, res_C]:
        sc = r['score_counter']
        tot = r['n_games']
        f_zero = sc.get('4x0', 0) / tot * 100
        t_four = sc.get('3x4', 0) / tot * 100
        print(f"  {r['name']:<40} {r['intern_wr']:>9.2f}% {r['banker_wr']:>9.2f}% {f_zero:>6.1f}% {t_four:>6.1f}% {r['avg_rounds']:>5.2f}")
    print("=" * 75)
