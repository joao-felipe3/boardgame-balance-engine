# -*- coding: utf-8 -*-
"""
BTG Madagascar - Motor Oficial do Jogo (Engine v14.0)
"""

import random
import time
import itertools
import numpy as np
from typing import List, Dict, Tuple, Optional, Union

from .constants import CardType, Role, InternProfile, BankerProfile, ContractSpec, SEVEN_TIERS_CATALOG
from .deck import ResourceCard, DeckManager
from .player import PlayerAI, PlayerDeclaration


def evaluate_contract_outcome(
    submitted_cards: List[ResourceCard],
    total_tokens_used: int,
    contract: ContractSpec,
    is_pure_banker_committee: bool = False
) -> Tuple[bool, int, bool]:
    """Avalia se um contrato cumpriu a meta de pontos e as cotas de insumos."""
    total_val = sum(c.base_value for c in submitted_cards) + total_tokens_used
    has_req = True

    if contract.req_commodity is not None:
        matching_count = sum(1 for c in submitted_cards if c.card_type in (contract.req_commodity, CardType.WILD))
        has_req = (matching_count >= contract.req_commodity_count)

    is_success = (total_val >= contract.target_value) and has_req
    return is_success, total_val, has_req


def choose_optimal_committee(
    chair: PlayerAI,
    players: List[PlayerAI],
    contract: ContractSpec,
    declarations: Dict[int, PlayerDeclaration],
    conflict_pairs: Optional[List[set]] = None
) -> Tuple[List[int], Optional[int]]:
    """O Chairman seleciona o comitê ótimo priorizando menor suspeita média."""
    c_size = contract.committee_size
    clean_pids = [p.id for p in players if p.id not in chair.known_traitors and chair.suspicions[p.id] < 0.60]
    if len(clean_pids) < c_size:
        clean_pids = [p.id for p in players if p.id not in chair.known_traitors]
    if len(clean_pids) < c_size:
        clean_pids = [p.id for p in players]

    all_comms = list(itertools.combinations(clean_pids, c_size))
    # Regra de Resistance (Sugestão C): Nunca colocar 2 membros do mesmo par de conflito juntos
    candidate_comms = [
        cm for cm in all_comms
        if not (conflict_pairs and any(sum(1 for pid in cm if pid in cp) > 1 for cp in conflict_pairs))
    ]
    if not candidate_comms:
        candidate_comms = all_comms

    evaluated_comms = []

    for comm in candidate_comms:
        supplier_ids = []
        if contract.req_commodity is not None:
            suppliers = [pid for pid in comm if declarations[pid].claims_req]
            if len(suppliers) >= contract.req_commodity_count:
                suppliers.sort(key=lambda pid: (chair.suspicions[pid], -declarations[pid].req_commodity_value))
                supplier_ids = suppliers[:contract.req_commodity_count]

        # True somente quando há declarantes suficientes para cobrir a cota do insumo.
        has_req_coverage = (
            contract.req_commodity is None or
            len(supplier_ids) >= contract.req_commodity_count
        )

        total_declared = sum(declarations[pid].claimed_value for pid in comm)
        is_viable = (total_declared >= contract.target_value)
        avg_sus = sum(chair.suspicions[pid] for pid in comm if pid != chair.id) / len(comm)
        has_chair = (chair.id in comm)
        bench_count = sum(1 for pid in comm if declarations[pid].prefers_bench)

        # Em comitês de 2 membros, dá preferência a testar quem estava fora do conflito
        conflict_penalty = sum(1 for pid in comm if any(pid in cp for cp in conflict_pairs)) if (conflict_pairs and c_size == 2) else 0

        evaluated_comms.append({
            'comm': list(comm),
            'supplier_ids': supplier_ids,
            'supplier_id': supplier_ids[0] if supplier_ids else None,
            'has_req_coverage': has_req_coverage,
            'is_viable': is_viable,
            'avg_sus': avg_sus,
            'has_chair': has_chair,
            'bench_count': bench_count,
            'conflict_penalty': conflict_penalty,
            'total_declared': total_declared
        })

    if getattr(chair, 'profile', None) == BankerProfile.CONSERVATIVE:
        evaluated_comms.sort(key=lambda x: (
            not x['has_req_coverage'],
            not x['is_viable'],
            x['conflict_penalty'],
            round(x['avg_sus'], 2),
            not x['has_chair'],
            x['bench_count'],
            -x['total_declared']
        ))
    elif getattr(chair, 'profile', None) == BankerProfile.PRAGMATIC:
        evaluated_comms.sort(key=lambda x: (
            not x['has_req_coverage'],
            not x['is_viable'],
            -x['total_declared'],
            round(x['avg_sus'], 2),
            x['conflict_penalty'],
            x['bench_count'],
            not x['has_chair']
        ))
    elif getattr(chair, 'profile', None) == BankerProfile.STRATEGIST:
        evaluated_comms.sort(key=lambda x: (
            not x['has_req_coverage'],
            not x['is_viable'],
            round(x['avg_sus'], 2),
            x['bench_count'],
            not x['has_chair'],
            -x['total_declared']
        ))
    else:
        evaluated_comms.sort(key=lambda x: (
            not x['has_req_coverage'],  # 1º: cobertura do insumo obrigatória
            not x['is_viable'],         # 2º: viabilidade de liquidez total declarada
            x['conflict_penalty'],      # 3º: em comitê de 2, prefere testar jogadores fora do par de conflito
            round(x['avg_sus'], 2),     # 4º: menor suspeita média entre os membros
            x['bench_count'],           # 5º: evitar membros que preferem o banco
            not x['has_chair'],         # 6º: preferência por incluir o Chairman
            -x['total_declared']        # 7º: maior valor total declarado como desempate
        ))

    best = evaluated_comms[0]
    return best['comm'], best['supplier_ids']


def coordinate_committee_contributions(
    comm_objs: List[PlayerAI],
    contract: ContractSpec,
    round_num: int,
    promised_suppliers,
    declarations: Dict[int, PlayerDeclaration],
    banker_score: int,
    intern_score: int = 0
) -> Tuple[List[ResourceCard], int, List[Dict], Dict[int, int]]:
    """Coordena aportes secretos dos membros convocados."""
    if isinstance(promised_suppliers, int):
        sup_list = [promised_suppliers]
    elif isinstance(promised_suppliers, (list, tuple, set)):
        sup_list = list(promised_suppliers)
    else:
        sup_list = []

    planning_order = []
    for s_id in sup_list:
        sup_obj = next((p for p in comm_objs if p.id == s_id), None)
        if sup_obj and sup_obj not in planning_order:
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
        is_req_responsible = (p.id in sup_list)
        remaining_members = len(planning_order) - idx
        remaining_target = max(0, contract.target_value - cumulative_committed_val)
        quota_for_p = remaining_target / remaining_members

        declared_p_val = declarations[p.id].claimed_value if p.id in declarations else 0
        if p.role == Role.BANKER and round_num >= 3 and contract.target_value >= 8:
            quota_for_p = max(quota_for_p, min(declared_p_val, contract.target_value / contract.committee_size))

        should_sabotage = False
        if p.role == Role.INTERN:
            if is_match_point:
                # Sobrevivência natural: em match-point (3xX), nenhum traidor entrega o jogo
                should_sabotage = True
            elif p.profile == InternProfile.A_AGGRESSIVE:
                # B.2: Se a R1 já falhou (intern_score >= 1), o estagiário na R2 joga camuflado
                # para ganhar crédito de sucesso e não entregar 0x2 óbvio.
                if round_num == 2 and intern_score >= 1:
                    should_sabotage = False
                else:
                    should_sabotage = True
            elif p.profile == InternProfile.B_SLEEPER:
                if round_num >= 3:
                    should_sabotage = True
                elif round_num == 2 and banker_score >= 1:
                    # Despertar orgânico do Sleeper na R2 (50% de chance de sabotagem caso o Banco abra 1x0)
                    should_sabotage = (p.rng.random() < 0.50)
                else:
                    should_sabotage = False
            elif p.profile == InternProfile.C_HEDGE:
                has_toxic = any(c.card_type == CardType.TOXIC for c in p.hand)
                # FASE 1 (Tiers 1-2): Coopera completamente para manter suspição baixa
                # FASE 2 (Tier 3+): Usa Tóxico se disponível — principal arma do Hedge
                # FASE 3 (Tiers 3+): Nega cota prometida quando responsável pelo insumo
                # FASE 4 (Tiers 4+): Sabotagem geral de valor baixo
                #
                # Tóxico a partir da rodada 3 (arma principal, não depende de insumo)
                toxic_sabotage = has_toxic and round_num >= 3
                # Negação de cota: rodada 3+ (antecipado de 4).
                # Tier 3 já exige 2x insumos — alta deniability por "ausência de mercado".
                quota_denial = is_req_responsible and contract.req_commodity is not None and round_num >= 3
                # Sabotagem geral: rodada 4+ (antecipado de 5)
                late_sabotage = round_num >= 4
                should_sabotage = toxic_sabotage or quota_denial or late_sabotage
            elif p.profile == InternProfile.D_OPPORTUNIST:
                if banker_score >= 2:
                    # Banco ameaça fechar o jogo: sabotagem agressiva
                    should_sabotage = True
                elif intern_score >= 2 and round_num <= 4:
                    # Estagiários já liderando: joga camuflado para ganhar créditos e despistar
                    should_sabotage = False
                elif round_num >= 3:
                    should_sabotage = True
                else:
                    # R1 honesto, R2 desperta se 1x0
                    should_sabotage = (round_num == 2 and banker_score >= 1 and p.rng.random() < 0.40)
            elif p.profile == InternProfile.E_TECHNICIAN:
                # Técnico: joga cooperativo na R1 para acumular cartas; na R2 desperta cirúrgico se 1x0 (45%), e ataca a partir da R3
                if round_num == 1:
                    should_sabotage = False
                elif round_num == 2:
                    should_sabotage = (banker_score >= 1 and p.rng.random() < 0.45)
                else:
                    should_sabotage = True

        honest_cards, honest_tokens, honest_val = p.plan_honest_contribution(contract, round_num, is_req_responsible, quota_for_p, is_match_point=is_match_point)
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
            'cards': [{
                'type': c.card_type.name,
                'name': c.card_type.value,
                'base': c.base_value
            } for c in actual_cards]
        })

    return submitted_all_cards, total_tokens_spent, submitted_cards_data, promised_values


def simulate_single_match(
    game_idx: int,
    profile: Optional[InternProfile] = None,
    seed: Optional[int] = None,
    record_trace: bool = False,
    banker_profile: Union[BankerProfile, str] = BankerProfile.BALANCED,
    intern_profile: Optional[Union[InternProfile, str]] = None
) -> Dict:
    """Executa uma partida completa de BTG Madagascar v14.0 com suporte a múltiplos perfis."""
    rng = random.Random(seed if seed is not None else (int(time.time() * 1000) ^ game_idx))
    
    roles = [Role.BANKER] * 3 + [Role.INTERN] * 2
    rng.shuffle(roles)

    if intern_profile is None:
        intern_profile = profile if profile is not None else InternProfile.B_SLEEPER

    all_banker_profs = list(BankerProfile)
    all_intern_profs = list(InternProfile)

    intern_count = 0
    players = []
    for i in range(5):
        if roles[i] == Role.INTERN:
            is_active = (intern_count == 0)
            intern_count += 1
            if intern_profile == "MIXED":
                p_prof = rng.choice(all_intern_profs)
            elif isinstance(intern_profile, InternProfile):
                p_prof = intern_profile
            elif isinstance(intern_profile, str) and intern_profile in InternProfile.__members__:
                p_prof = InternProfile[intern_profile]
            else:
                p_prof = InternProfile.B_SLEEPER
            players.append(PlayerAI(i, roles[i], p_prof, rng, is_active_saboteur=is_active))
        else:
            if banker_profile == "MIXED":
                b_prof = rng.choice(all_banker_profs)
            elif isinstance(banker_profile, BankerProfile):
                b_prof = banker_profile
            elif isinstance(banker_profile, str) and banker_profile in BankerProfile.__members__:
                b_prof = BankerProfile[banker_profile]
            else:
                b_prof = BankerProfile.BALANCED
            players.append(PlayerAI(i, roles[i], b_prof, rng, is_active_saboteur=False))

    players_metadata = [{'id': p.id, 'role': p.role.value, 'profile': p.profile.value} for p in players]

    deck = DeckManager(seed=rng.randint(0, 10**9))
    deck.refill_open_market(3)

    # Carteira Inicial Oficial: Kit C [1x Cobalto (+1), 1x Titânio (+3) + 2 secretas do topo] — 4 cartas.
    for p in players:
        p.hand = [ResourceCard(CardType.CO), ResourceCard(CardType.TI)] + deck.draw_blind(2)

    banker_score = 0
    intern_score = 0
    curr_chair = 0
    round_count = 0
    # Rastreia falha nos Tiers 3 e 4 para expansão condicional do comitê no Tier 5.
    # O Megaconsórcio expande para 4 membros se QUALQUER UM dos dois setores
    # anteriores (Tiers 3 ou 4) foi sabotado. Narrativa: "crise acumulada exige comitê de emergência".
    prev_tier3_failed = False
    prev_tier4_failed = False
    conflict_pairs: List[set] = []
    has_played = {p.id: False for p in players}
    r2_passed_comm: List[int] = []
    ops = [rng.choice(SEVEN_TIERS_CATALOG[t]) for t in range(1, 8)]
    suspicion_history = []
    rounds_data = []

    # Telemetria rica de andamento da partida
    total_vetoes = 0
    forced_committees = 0
    r5_expanded = False
    total_tokens_spent_game = 0
    total_toxic_played_game = 0
    intern_comm_appearances = 0
    first_intern_round = None
    tier_telemetry = {}

    for r_idx, contract in enumerate(ops):
        round_count += 1

        # Expansão condicional do comitê: Tier 5 expande para 4 membros se o Tier 3 OU Tier 4 falhou.
        tier5_should_expand = prev_tier3_failed or prev_tier4_failed
        if contract.expandable_on_prior_failure and tier5_should_expand and contract.expanded_committee_size > 0:
            r5_expanded = True
            contract = ContractSpec(
                name=contract.name,
                tier=contract.tier,
                committee_size=contract.expanded_committee_size,
                cost_per_player=contract.cost_per_player,
                target_value=contract.target_value,
                req_commodity=contract.req_commodity,
                req_commodity_count=contract.req_commodity_count,
                expandable_on_prior_failure=contract.expandable_on_prior_failure,
                expanded_committee_size=contract.expanded_committee_size,
            )

        if record_trace:
            hands_before = {
                p.id: {
                    'cards': [{'type': c.card_type.name, 'name': c.card_type.value, 'base': c.base_value} for c in p.hand],
                    'tokens': p.interest_tokens
                } for p in players
            }
            bankers = [p for p in players if p.role == Role.BANKER]
            sus_avg = {}
            sus_by_banker = {}
            for target_id in range(5):
                sus_vals = [b.suspicions[target_id] for b in bankers if b.id != target_id]
                sus_avg[target_id] = round(float(np.mean(sus_vals)), 2) if sus_vals else 0.0
            for b in bankers:
                sus_by_banker[b.id] = {target_id: round(b.suspicions[target_id], 2) for target_id in range(5)}
            suspicion_history.append(sus_avg)
        else:
            hands_before = None
            sus_avg = None
            sus_by_banker = None

        consecutive_vetoes = 0
        approved_committee = None
        promised_supplier = None
        all_declarations = {}

        while consecutive_vetoes < 3 and approved_committee is None:
            chair = players[curr_chair]
            declarations = {p.id: p.make_public_declaration(contract, round_count) for p in players}
            all_declarations = declarations

            chosen_comm, assigned_req_player = choose_optimal_committee(
                chair, players, contract, declarations, conflict_pairs=conflict_pairs
            )

            # Regra de alternância da R3 (50% testar par de conflito vs 50% testar banco)
            if round_count == 3 and conflict_pairs and contract.committee_size == 3:
                cp = conflict_pairs[0]
                has_cp = any(pid in cp for pid in chosen_comm)
                if rng.random() < 0.50:
                    if not has_cp:
                        cp_candidates = list(cp)
                        cp_candidates.sort(key=lambda pid: (chair.suspicions[pid], -declarations[pid].claimed_value))
                        chosen_cp_member = cp_candidates[0]
                        non_chair = [pid for pid in chosen_comm if pid != chair.id]
                        if non_chair:
                            bench_in_comm = [pid for pid in non_chair if not has_played.get(pid, False)]
                            to_replace = bench_in_comm[0] if bench_in_comm else non_chair[-1]
                            alt_comm = [pid for pid in chosen_comm if pid != to_replace] + [chosen_cp_member]
                            req_cov = (contract.req_commodity is None or len([pid for pid in alt_comm if declarations[pid].claims_req]) >= contract.req_commodity_count)
                            if req_cov:
                                chosen_comm = alt_comm

            # Votação com cautela (Veto do banqueiro injustiçado)
            votes = {}
            for p in players:
                if p.role == Role.BANKER and round_count == 3 and conflict_pairs:
                    cp = conflict_pairs[0]
                    if p.id in cp and p.id not in chosen_comm:
                        if any(not has_played.get(pid, False) for pid in chosen_comm):
                            votes[p.id] = False
                            continue
                votes[p.id] = p.vote_on_proposal(curr_chair, chosen_comm, contract, round_count)

            if sum(votes.values()) >= 3:
                approved_committee = chosen_comm
                promised_supplier = assigned_req_player
            else:
                consecutive_vetoes += 1
                curr_chair = (curr_chair + 1) % 5

        total_vetoes += consecutive_vetoes
        if approved_committee is None:
            forced_committees += 1
            # Resolução forçada: aplica os mesmos critérios de viabilidade do caminho normal.
            # O Chairman original é descartado — todos os jogadores são candidatos.
            all_comms = list(itertools.combinations(range(5), contract.committee_size))

            def _forced_score(cm):
                # 1º: preferir comitês com cobertura do insumo obrigatório
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
                # 2º: evitar membros que declararam preferir o banco
                # (mão vazia ou apenas cartas tóxicas — inclui Banqueiros esgotados)
                bench_in_comm = sum(
                    1 for pid in cm
                    if all_declarations.get(pid) and all_declarations[pid].prefers_bench
                )
                # 3º: menor suspeita total agregada pelos banqueiros
                total_sus = sum(
                    sum(p.suspicions[cid] for p in players if p.role == Role.BANKER)
                    for cid in cm
                )
                return (not has_coverage, bench_in_comm, total_sus)

            best_comm = min(all_comms, key=_forced_score)
            approved_committee = list(best_comm)

            # Atribuir fornecedor prometido mesmo em resolução forçada
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

        for p in players:
            if p.id in approved_committee:
                has_played[p.id] = True
                p.consecutive_rounds += 1
            else:
                p.consecutive_rounds = 0

        # Dividendo de Banco Completo Oficial (+1 Carta E +1 Token de Juros):
        for p in players:
            if p.id not in approved_committee:
                p.accumulate_holding_interest()
                if p.role == Role.BANKER:
                    preferred = None
                    if getattr(p, 'profile', None) == BankerProfile.STRATEGIST:
                        # Estrategista foca em Safira e Wild, depois insumo do contrato e Titânio
                        for ct in [CardType.SF, CardType.WILD, contract.req_commodity, CardType.TI]:
                            if ct is not None and ct in deck.open_market:
                                preferred = ct
                                break
                    else:
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

        submitted_cards, total_tokens_spent, submitted_cards_data, promised_values = coordinate_committee_contributions(
            comm_objs, contract, round_count, promised_supplier, all_declarations, banker_score, intern_score=intern_score
        )

        deck.discard(submitted_cards)
        is_pure_bankers = all(p.role == Role.BANKER for p in comm_objs)
        is_success, total_val, has_req = evaluate_contract_outcome(submitted_cards, total_tokens_spent, contract, is_pure_banker_committee=is_pure_bankers)

        # Telemetria do resultado desta rodada
        has_toxic = any(c.card_type == CardType.TOXIC for c in submitted_cards)
        interns_in_comm = [pid for pid in approved_committee if players[pid].role == Role.INTERN]
        if interns_in_comm:
            intern_comm_appearances += len(interns_in_comm)
            if first_intern_round is None:
                first_intern_round = round_count

        fail_cause = 'none' if is_success else ('insumo' if not has_req else ('toxico' if has_toxic else 'valor'))
        tier_telemetry[round_count] = {
            'tier': contract.tier,
            'target': contract.target_value,
            'success': is_success,
            'fail_cause': fail_cause,
            'tokens_spent': total_tokens_spent,
            'intern_count': len(interns_in_comm),
            'saboteur_in_comm': any(players[pid].role == Role.INTERN and players[pid].is_active_saboteur for pid in approved_committee),
            'has_toxic': has_toxic
        }
        total_tokens_spent_game += total_tokens_spent
        if has_toxic:
            total_toxic_played_game += sum(1 for c in submitted_cards if c.card_type == CardType.TOXIC)

        # Atualiza os flags de falha por tier para a próxima rodada
        if contract.tier == 3:
            prev_tier3_failed = not is_success
        elif contract.tier == 4:
            prev_tier4_failed = not is_success
        else:
            pass

        credits_awarded = []
        if is_success:
            banker_score += 1
            for p in comm_objs:
                p.claim_success_credit()
                credits_awarded.append(p.id)

            decay = 0.05 if contract.tier <= 2 else (0.15 if contract.tier <= 4 else 0.30)
            for bp in players:
                if bp.role == Role.BANKER:
                    for cid in approved_committee:
                        if cid != bp.id and cid not in bp.known_traitors:
                            bp.suspicions[cid] = max(0.05, bp.suspicions[cid] - decay)

            if round_count == 2:
                r2_passed_comm = list(approved_committee)

            # Dedução de Vindicação (The Resistance / Sugestão C):
            for cp in list(conflict_pairs):
                v_members = [cid for cid in approved_committee if cid in cp]
                if len(v_members) == 1:
                    vindicated_pid = v_members[0]
                    traitor_pid = next(other for other in cp if other != vindicated_pid)
                    for bp in players:
                        if bp.role == Role.BANKER:
                            bp.suspicions[traitor_pid] = 1.00
                            bp.known_traitors.add(traitor_pid)
                            if bp.id != vindicated_pid:
                                bp.suspicions[vindicated_pid] = max(0.05, bp.suspicions[vindicated_pid] - 0.15)
                    conflict_pairs.remove(cp)
        else:
            intern_score += 1

            # Dedução inteligente por tipo de falha em comitê de 2 membros (Sugestão C):
            if len(approved_committee) == 2:
                conflict_pairs.append(set(approved_committee))
                sup_pids = [promised_supplier] if isinstance(promised_supplier, int) else (list(promised_supplier) if promised_supplier else [])
                partner_of = {cid: next(other for other in approved_committee if other != cid) for cid in approved_committee}

                for bp in players:
                    if bp.role == Role.BANKER:
                        if bp.id in approved_committee:
                            partner_id = partner_of[bp.id]
                            bp.suspicions[partner_id] = 1.00
                            bp.known_traitors.add(partner_id)
                        else:
                            if contract.req_commodity is not None:
                                if not has_req and sup_pids:
                                    for cid in approved_committee:
                                        if cid in sup_pids:
                                            bp.suspicions[cid] = max(bp.suspicions[cid], 0.80)
                                        else:
                                            bp.suspicions[cid] = max(bp.suspicions[cid], 0.48)
                                else:
                                    for cid in approved_committee:
                                        if cid in sup_pids:
                                            bp.suspicions[cid] = min(bp.suspicions[cid], 0.35)
                                        else:
                                            bp.suspicions[cid] = max(bp.suspicions[cid], 0.82)
                            else:
                                for cid in approved_committee:
                                    bp.suspicions[cid] = 0.52

                        for op in players:
                            if op.id not in approved_committee and op.id != bp.id:
                                if not has_played.get(op.id, False):
                                    bp.suspicions[op.id] = max(0.42, bp.suspicions[op.id])
                                else:
                                    bp.suspicions[op.id] = max(0.05, bp.suspicions[op.id] - 0.03)
            else:
                new_members = [cid for cid in approved_committee if cid not in r2_passed_comm] if r2_passed_comm else []
                if round_count == 3 and len(r2_passed_comm) == 2 and len(new_members) == 1:
                    culprit = new_members[0]
                    for bp in players:
                        if bp.role == Role.BANKER:
                            if bp.id != culprit:
                                bp.suspicions[culprit] = 0.88
                                if conflict_pairs:
                                    for cp in list(conflict_pairs):
                                        if culprit in cp:
                                            vindicated = next(other for other in cp if other != culprit)
                                            bp.suspicions[vindicated] = max(0.05, bp.suspicions[vindicated] - 0.20)
                                            bp.suspicions[culprit] = 1.00
                                            bp.known_traitors.add(culprit)
                                            conflict_pairs.remove(cp)
                            for r2_id in r2_passed_comm:
                                if bp.id != r2_id:
                                    bp.suspicions[r2_id] = min(0.40, bp.suspicions[r2_id])
                else:
                    sup_pids = [promised_supplier] if isinstance(promised_supplier, int) else (list(promised_supplier) if promised_supplier else [])
                    if not has_req and sup_pids:
                        if len(sup_pids) == 1:
                            s_id = sup_pids[0]
                            for bp in players:
                                if bp.role == Role.BANKER and bp.id != s_id:
                                    bp.suspicions[s_id] = 1.00
                                    bp.known_traitors.add(s_id)
                        else:
                            for bp in players:
                                if bp.role == Role.BANKER and bp.id in sup_pids:
                                    other_sups = [sid for sid in sup_pids if sid != bp.id]
                                    for osid in other_sups:
                                        bp.suspicions[osid] = 1.00
                                        bp.known_traitors.add(osid)

                    for bp in players:
                        if bp.role == Role.BANKER:
                            penalty = 0.15 if len(approved_committee) >= 4 else 0.25
                            for cid in approved_committee:
                                if cid != bp.id and cid not in bp.known_traitors:
                                    bp.suspicions[cid] = min(0.85, bp.suspicions[cid] + penalty)

                for bp in players:
                    if bp.role == Role.BANKER:
                        for op in players:
                            if op.id not in approved_committee and op.id != bp.id:
                                if not has_played.get(op.id, False):
                                    bp.suspicions[op.id] = max(0.42, bp.suspicions[op.id])
                                else:
                                    bp.suspicions[op.id] = max(0.05, bp.suspicions[op.id] - 0.03)

        if record_trace:
            rounds_data.append({
                'round_num': round_count,
                'contract': {
                    'name': contract.name,
                    'tier': contract.tier,
                    'target': contract.target_value,
                    'req_commodity': contract.req_commodity.value if contract.req_commodity else None,
                    'req_count': contract.req_commodity_count,
                    'committee_size': contract.committee_size,
                    'cost_per_player': contract.cost_per_player
                },
                'chair_id': curr_chair,
                'committee': approved_committee,
                'promised_supplier': promised_supplier,
                'declarations': {pid: {'claims_req': d.claims_req, 'claimed_val': d.claimed_value, 'tokens_offered': d.tokens_offered, 'prefers_bench': d.prefers_bench, 'offered_desc': d.offered_desc} for pid, d in all_declarations.items()},
                'votes': votes,
                'submitted': submitted_cards_data,
                'total_tokens_spent': total_tokens_spent,
                'total_value': total_val,
                'has_req': has_req,
                'is_success': is_success,
                'banker_score': banker_score,
                'intern_score': intern_score,
                'credits_awarded': credits_awarded,
                'hands_before': hands_before,
                'suspicions': {
                    'avg': sus_avg,
                    'by_banker': sus_by_banker,
                    'known_traitors': {b.id: list(b.known_traitors) for b in bankers}
                }
            })

        def _build_final_dict(winner_role, cause_str, final_rounds):
            bankers_list = [p for p in players if p.role == Role.BANKER]
            interns_list = [p for p in players if p.role == Role.INTERN]
            unmasked = sum(1 for ip in interns_list if any(bp.suspicions[ip.id] >= 0.99 for bp in bankers_list))
            int_sus = [bp.suspicions[ip.id] for bp in bankers_list for ip in interns_list]
            bnk_sus = [bp.suspicions[other.id] for bp in bankers_list for other in bankers_list if other.id != bp.id]
            avg_int_s = float(np.mean(int_sus)) if int_sus else 0.0
            avg_bnk_s = float(np.mean(bnk_sus)) if bnk_sus else 0.0
            avg_hand = float(np.mean([len(p.hand) for p in players]))

            i_prof_names = [ip.profile.value for ip in interns_list]
            b_prof_names = [bp.profile.value for bp in bankers_list]
            i_summary = i_prof_names[0] if len(set(i_prof_names)) == 1 else "Misto (" + "/".join([ip.profile.name for ip in interns_list]) + ")"
            b_summary = b_prof_names[0] if len(set(b_prof_names)) == 1 else "Misto (" + "/".join([bp.profile.name for bp in bankers_list]) + ")"

            rd = {
                "winner": winner_role.value if isinstance(winner_role, Role) else winner_role,
                "cause": cause_str,
                "rounds": final_rounds,
                "b_score": banker_score,
                "i_score": intern_score,
                "profile": i_summary,
                "intern_profile": i_summary,
                "banker_profile": b_summary,
                "matchup": f"{b_summary} vs {i_summary}",
                "tier_telemetry": tier_telemetry,
                "total_vetoes": total_vetoes,
                "forced_committees": forced_committees,
                "r5_expanded": r5_expanded,
                "total_tokens_spent": total_tokens_spent_game,
                "total_toxic_played": total_toxic_played_game,
                "intern_lockout": (intern_comm_appearances == 0),
                "first_intern_round": first_intern_round,
                "intern_comm_appearances": intern_comm_appearances,
                "interns_unmasked": unmasked,
                "avg_intern_sus": round(avg_int_s, 3),
                "avg_banker_sus": round(avg_bnk_s, 3),
                "avg_hand_size": round(avg_hand, 2)
            }
            if record_trace:
                rd['rounds_data'] = rounds_data
                rd['sus_history'] = suspicion_history
                rd['players_metadata'] = players_metadata
            return rd

        if banker_score >= 4:
            return _build_final_dict(Role.BANKER, "4 Contratos Concluidos", round_count)
        elif intern_score >= 4:
            return _build_final_dict(Role.INTERN, "4 Contratos Reprovados", round_count)

        curr_chair = (curr_chair + 1) % 5

    w = Role.BANKER if banker_score > intern_score else Role.INTERN
    return _build_final_dict(w, "Fim das 7 Rodadas", 7)
