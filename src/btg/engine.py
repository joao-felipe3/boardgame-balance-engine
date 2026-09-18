# -*- coding: utf-8 -*-
"""
BTG Madagascar - Motor Oficial do Jogo (Engine v14.0)
"""

import random
import time
import itertools
import numpy as np
from typing import List, Dict, Tuple, Optional, Union, Set

from .constants import CardType, Role, InternProfile, BankerProfile, ContractSpec, SEVEN_TIERS_CATALOG
from .deck import ResourceCard, DeckManager
from .player import PlayerAI, PlayerDeclaration
from .events import DirectivesDeck, DirectiveTriggerRegime, DirectiveCard


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
    conflict_pairs: Optional[List[set]] = None,
    quarantined_pid: Optional[int] = None,
    public_accused: Optional[Set[int]] = None,
    passed_members: Optional[Set[int]] = None
) -> Tuple[List[int], Optional[int]]:
    """O Chairman seleciona o comitê ótimo priorizando menor suspeita média e consciência social."""
    c_size = contract.committee_size
    valid_players = [p for p in players if p.id != quarantined_pid]
    if len(valid_players) < c_size:
        valid_players = players

    accused_set = public_accused or set()

    # Priorização social da mesa: banqueiro leal evita convocar acusados públicos se houver operadores limpos
    if chair.role == Role.BANKER and accused_set:
        unaccused_clean = [
            p.id for p in valid_players
            if p.id not in chair.known_traitors and p.id not in accused_set and chair.suspicions[p.id] < 0.60
        ]
        if len(unaccused_clean) >= c_size:
            clean_pids = unaccused_clean
        else:
            clean_pids = [
                p.id for p in valid_players
                if p.id not in chair.known_traitors and chair.suspicions[p.id] < 0.60
            ]
    else:
        clean_pids = [
            p.id for p in valid_players
            if p.id not in chair.known_traitors and chair.suspicions[p.id] < 0.60
        ]

    if len(clean_pids) < c_size:
        clean_pids = [p.id for p in valid_players if p.id not in chair.known_traitors]
    if len(clean_pids) < c_size:
        clean_pids = [p.id for p in valid_players]

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
        partners = [pid for pid in comm if pid != chair.id]
        avg_sus = sum(chair.suspicions[pid] for pid in partners) / len(partners) if partners else 0.0
        has_chair = (chair.id in comm)
        bench_count = sum(1 for pid in comm if declarations[pid].prefers_bench)
        # Incógnitas / membros não comprovados para o Chairman (sus >= 0.30 ou fora de passed_members):
        untrusted_count = sum(1 for pid in comm if pid != chair.id and (chair.suspicions[pid] >= 0.30 or pid not in passed_members))
        intruders_count = sum(1 for pid in comm if pid != chair.id and chair.suspicions[pid] >= 0.35)

        # Penalidade por membros em par de conflito ou acusados abertos
        conflict_penalty = 0
        if conflict_pairs:
            for cp in conflict_pairs:
                cp_count = sum(1 for pid in comm if pid in cp)
                if cp_count > 1:
                    conflict_penalty += 10  # NUNCA colocar 2 do mesmo conflito juntos
                elif cp_count == 1:
                    conflict_penalty += 1
        if accused_set:
            conflict_penalty += sum(1 for pid in comm if pid in accused_set)

        traitor_count = sum(1 for pid in comm if pid in chair.known_traitors or chair.suspicions[pid] >= 0.80)

        total_tokens = sum(declarations[pid].tokens_offered for pid in comm)
        fatigue_count = sum(1 for pid in comm if players[pid].consecutive_rounds >= 2)
        public_req_count = sum(
            1 for pid in comm
            if contract.req_commodity is not None and (
                contract.req_commodity in players[pid].public_known_cards or
                CardType.WILD in players[pid].public_known_cards
            )
        )

        evaluated_comms.append({
            'comm': list(comm),
            'supplier_ids': supplier_ids,
            'supplier_id': supplier_ids[0] if supplier_ids else None,
            'has_req_coverage': has_req_coverage,
            'is_viable': is_viable,
            'avg_sus': avg_sus,
            'has_chair': has_chair,
            'bench_count': bench_count,
            'untrusted_count': untrusted_count,
            'intruders_count': intruders_count,
            'conflict_penalty': conflict_penalty,
            'traitor_count': traitor_count,
            'total_declared': total_declared,
            'total_tokens': total_tokens,
            'fatigue_count': fatigue_count,
            'public_req_count': public_req_count
        })

    if getattr(chair, 'profile', None) == BankerProfile.CONSERVATIVE:
        evaluated_comms.sort(key=lambda x: (
            x['traitor_count'],
            not x['has_chair'],
            x['conflict_penalty'],
            not x['has_req_coverage'],
            not x['is_viable'],
            x['untrusted_count'],       # Priorizar comitê puro leal ou com no máximo 1 teste
            round(x['avg_sus'], 3),
            -x['total_declared'],       # Maior folga para garantir meta
            x['fatigue_count'],
            -x['public_req_count'],
            -x['total_tokens'],
            x['bench_count']
        ))
    elif getattr(chair, 'profile', None) == BankerProfile.PRAGMATIC:
        evaluated_comms.sort(key=lambda x: (
            x['traitor_count'],
            not x['has_chair'],
            x['conflict_penalty'],
            not x['has_req_coverage'],
            not x['is_viable'],
            x['untrusted_count'],
            round(x['avg_sus'], 3),
            -x['total_declared'],
            -x['total_tokens'],
            x['fatigue_count'],
            -x['public_req_count'],
            x['bench_count']
        ))
    elif getattr(chair, 'profile', None) == BankerProfile.STRATEGIST:
        evaluated_comms.sort(key=lambda x: (
            x['traitor_count'],
            not x['has_chair'],
            x['conflict_penalty'],
            not x['has_req_coverage'],
            not x['is_viable'],
            x['untrusted_count'],
            round(x['avg_sus'], 3),
            -x['total_declared'],
            x['fatigue_count'],
            -x['total_tokens'],
            -x['public_req_count'],
            x['bench_count']
        ))
    else:
        evaluated_comms.sort(key=lambda x: (
            x['traitor_count'],         # 1º: zero traidores conhecidos
            not x['has_chair'],         # 2º: Chairman leal SEMPRE se inclui para controle de variável
            x['conflict_penalty'],      # 3º: evitar membros em conflito aberto
            not x['has_req_coverage'],  # 4º: cobertura do insumo necessária
            not x['is_viable'],         # 5º: viabilidade matemática de liquidez (atingir a meta!)
            x['untrusted_count'],       # 6º: ISOLAMENTO DE VARIÁVEL! Priorizar 0 incógnitas (núcleo puro), depois 1 incógnita (teste controlado). Evitar 2+ incógnitas!
            round(x['avg_sus'], 3),     # 7º: menor suspeita média real exata
            -x['total_declared'],       # 8º: maior folga para bater a meta com segurança
            x['fatigue_count'],         # 9º: evitar fadiga econômica excessiva
            -x['total_tokens'],         # 10º: priorizar tokens de liquidez reais acumulados do banco
            -x['public_req_count'],     # 11º: priorizar insumos verificados no balcão aberto
            x['bench_count']            # 12º: evitar membros que preferem o banco
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

        # Gestão Cooperativa: Banqueiros poupam recursos se membros anteriores já cobriram a meta
        if p.role == Role.BANKER:
            quota_for_p = max(float(contract.cost_per_player), quota_for_p)

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
    intern_profile: Optional[Union[InternProfile, str]] = None,
    enable_directives: bool = False,
    directive_regime: Union[DirectiveTriggerRegime, str] = DirectiveTriggerRegime.DICE_50
) -> Dict:
    """Executa uma partida completa de BTG Madagascar v14.0 com suporte a múltiplos perfis e DLC de Diretrizes."""
    rng = random.Random(seed if seed is not None else (int(time.time() * 1000) ^ game_idx))
    
    if isinstance(directive_regime, str):
        try:
            directive_regime = DirectiveTriggerRegime[directive_regime.upper()]
        except KeyError:
            directive_regime = DirectiveTriggerRegime.DICE_50
    directives_deck = DirectivesDeck(rng=rng) if enable_directives else None
    last_round_success: Optional[bool] = None

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
    public_accused: Set[int] = set()
    has_played = {p.id: False for p in players}
    passed_members: Set[int] = set()
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
        active_directive: Optional[DirectiveCard] = None

        if enable_directives and directives_deck is not None:
            if directives_deck.should_trigger(round_count, directive_regime, last_round_success):
                active_directive = directives_deck.draw()

        c_size = contract.committee_size
        target_val = contract.target_value
        req_comm = contract.req_commodity
        req_count = contract.req_commodity_count

        # Expansão condicional do comitê: Tier 5 expande para 4 membros se o Tier 3 OU Tier 4 falhou.
        tier5_should_expand = prev_tier3_failed or prev_tier4_failed
        if contract.expandable_on_prior_failure and tier5_should_expand and contract.expanded_committee_size > 0:
            r5_expanded = True
            c_size = contract.expanded_committee_size

        # Modificadores de Diretrizes da DLC:
        if active_directive is not None:
            if active_directive.id == "COMITE_EXPANDIDO":
                c_size = min(4, c_size + 1)
            elif active_directive.id == "FORCA_TAREFA_ENXUTA":
                c_size = max(2, c_size - 1)
            elif active_directive.id == "SUBSIDIO_GOVERNAMENTAL":
                target_val = max(3, target_val - 2)
            elif active_directive.id == "CRISE_DE_OFERTA":
                target_val = target_val + 2
            elif active_directive.id == "SWAP_DE_COMMODITY":
                req_comm = None
            elif active_directive.id == "LEILAO_DE_BALCAO":
                for p in players:
                    p.hand.append(deck.draw_blind(1)[0])
            elif active_directive.id == "REESTRUTURACAO_OFFSHORE":
                for p in players:
                    if len(p.hand) >= 2:
                        weak_cards = [
                            c for c in p.hand
                            if (p.role == Role.BANKER and c.card_type != contract.req_commodity and c.card_type != CardType.SF) or
                               (p.role == Role.INTERN and c.card_type != CardType.TOXIC)
                        ]
                        weak_cards.sort(key=lambda c: c.base_value)
                        to_discard = weak_cards[:2]
                        for c in to_discard:
                            p.hand.remove(c)
                            deck.discard([c])
                        new_cards = deck.draw_blind(len(to_discard))
                        p.hand.extend(new_cards)
            elif active_directive.id == "LINHA_DE_CREDITO_SINDICAL":
                for p in players:
                    p.interest_tokens += 1

        contract = ContractSpec(
            name=contract.name,
            tier=contract.tier,
            committee_size=c_size,
            cost_per_player=contract.cost_per_player,
            target_value=target_val,
            req_commodity=req_comm,
            req_commodity_count=req_count,
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

        # Inspeção de Carteira (Due Diligence) da DLC:
        if active_directive and active_directive.id == "INSPECAO_DE_CARTEIRA":
            chair_initial = players[curr_chair]
            candidates = [p for p in players if p.id != chair_initial.id]
            if candidates:
                target_player = max(candidates, key=lambda p: chair_initial.suspicions[p.id])
                if target_player.hand:
                    valid_cards = [c for c in target_player.hand if c.card_type != CardType.TOXIC]
                    if valid_cards:
                        revealed_card = max(valid_cards, key=lambda c: (c.card_type in (CardType.SF, contract.req_commodity), c.base_value))
                    else:
                        revealed_card = target_player.hand[0]

                    if revealed_card.card_type == CardType.TOXIC:
                        for bp in players:
                            if bp.role == Role.BANKER:
                                bp.suspicions[target_player.id] = 1.00
                                bp.known_traitors.add(target_player.id)
                    elif revealed_card.card_type in (CardType.SF, CardType.TI, contract.req_commodity) or revealed_card.base_value >= 3:
                        for bp in players:
                            if bp.role == Role.BANKER:
                                bp.suspicions[target_player.id] = max(0.05, bp.suspicions[target_player.id] - 0.30)

        # Pacto de Acionistas (Aliança de Confiança) da DLC:
        if active_directive and active_directive.id == "PACTO_DE_ACIONISTAS":
            chair_initial = players[curr_chair]
            candidates = [p for p in players if p.id != chair_initial.id]
            if candidates:
                partner = min(candidates, key=lambda p: abs(chair_initial.suspicions[p.id] - 0.35))
                if partner.role == Role.BANKER:
                    chair_initial.suspicions[partner.id] = max(0.05, chair_initial.suspicions[partner.id] - 0.40)
                    partner.suspicions[chair_initial.id] = max(0.05, partner.suspicions[chair_initial.id] - 0.40)
                else:
                    valid_c = [c for c in partner.hand if c.card_type != CardType.TOXIC and c.base_value >= 3]
                    if valid_c and rng.random() < 0.60:
                        chair_initial.suspicions[partner.id] = max(0.15, chair_initial.suspicions[partner.id] - 0.25)

        consecutive_vetoes = 0
        approved_committee = None
        promised_supplier = None
        all_declarations = {}

        while consecutive_vetoes < 3 and approved_committee is None:
            chair = players[curr_chair]
            declarations = {p.id: p.make_public_declaration(contract, round_count) for p in players}
            all_declarations = declarations

            # Quarentena Regulatória da DLC
            quarantined_pid: Optional[int] = None
            if active_directive and active_directive.id == "QUARENTENA_REGULATORIA":
                c_pids = [p.id for p in players if p.id != chair.id]
                quarantined_pid = max(c_pids, key=lambda pid: chair.suspicions[pid])

            chosen_comm, assigned_req_player = choose_optimal_committee(
                chair, players, contract, declarations, conflict_pairs=conflict_pairs,
                quarantined_pid=quarantined_pid, public_accused=public_accused,
                passed_members=passed_members
            )

            # Votação com cautela (Veto do banqueiro injustiçado / Disciplina de Conflito)
            votes = {}
            for p in players:
                if p.role == Role.BANKER and conflict_pairs and consecutive_vetoes < 1:
                    # Se o banqueiro faz parte de um par de conflito e seu rival foi colocado sem ele: veto automático
                    in_rivalry_without_self = False
                    for cp in conflict_pairs:
                        if p.id in cp:
                            rivals = [other for other in cp if other != p.id]
                            if any(r_id in chosen_comm for r_id in rivals) and p.id not in chosen_comm:
                                in_rivalry_without_self = True
                                break
                    if in_rivalry_without_self:
                        votes[p.id] = False
                        continue
                votes[p.id] = p.vote_on_proposal(curr_chair, chosen_comm, contract, round_count, conflict_pairs=conflict_pairs, consecutive_vetoes=consecutive_vetoes, declarations=declarations)

            votes_for = sum(1 for v in votes.values() if v)
            if active_directive and active_directive.id == "GOLDEN_SHARE" and votes.get(curr_chair, False):
                votes_for += 1

            threshold_required = 3
            if active_directive:
                if active_directive.id == "SUPERMAIORIA_EXIGIDA":
                    threshold_required = 4
                elif active_directive.id == "DECRETO_PRESIDENCIAL":
                    threshold_required = 2

            if votes_for >= threshold_required:
                # Pedido de Vista (DLC): Qualquer operador com Token de Rendimento pessoal pode gastar 1 token
                # para cancelar a proposta e passar o martelo sem queimar veto da mesa
                pedido_de_vista_used = False
                if active_directive and active_directive.id == "PEDIDO_DE_VISTA":
                    for p in players:
                        if p.id != curr_chair and p.interest_tokens >= 1:
                            if p.role == Role.BANKER and any(p.suspicions[cid] >= 0.50 or cid in p.known_traitors for cid in chosen_comm):
                                p.interest_tokens -= 1
                                pedido_de_vista_used = True
                                break
                            elif p.role == Role.INTERN and all(players[cid].role == Role.BANKER for cid in chosen_comm) and rng.random() < 0.35:
                                p.interest_tokens -= 1
                                pedido_de_vista_used = True
                                break

                if pedido_de_vista_used:
                    curr_chair = (curr_chair + 1) % 5
                    continue

                approved_committee = chosen_comm
                promised_supplier = assigned_req_player
            else:
                consecutive_vetoes += 1
                curr_chair = (curr_chair + 1) % 5

        total_vetoes += consecutive_vetoes
        if approved_committee is None:
            forced_committees += 1
            all_comms = list(itertools.combinations(range(5), contract.committee_size))

            def _forced_score(cm):
                # Intervenção Regulatória do Banco Central:
                # O regulador JAMAIS nomeia operadores acusados de fraude ou em conflito aberto,
                # e prioriza a idoneidade cadastral média (menor suspeita acumulada pela mesa).
                accused_count = sum(1 for cid in cm if cid in public_accused or (conflict_pairs and any(cid in cp for cp in conflict_pairs)))
                total_sus = sum(
                    sum(p.suspicions[cid] for p in players if p.role == Role.BANKER)
                    for cid in cm
                )
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
                return (accused_count, total_sus, not has_coverage, bench_in_comm)

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
                    # Prioridade de Balcão Aberto:
                    # 1. WILD (Coringa absoluto)
                    # 2. Insumo exigido pelo contrato atual ou próximo que o banqueiro não possui
                    next_req = ops[r_idx + 1].req_commodity if r_idx + 1 < len(ops) else None
                    needed_reqs = [req for req in [contract.req_commodity, next_req] if req is not None]
                    has_needed = any(any(c.card_type in (req, CardType.WILD) for c in p.hand) for req in needed_reqs)

                    search_order = [CardType.WILD]
                    if not has_needed:
                        search_order.extend(needed_reqs)
                    search_order.extend([CardType.SF, CardType.TI, CardType.VN, CardType.CO])

                    for ct in search_order:
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
        for p in players:
            if len(p.hand) == 0:
                p.hand.append(deck.draw_blind(1)[0])

        comm_objs = [players[pid] for pid in approved_committee]

        submitted_cards, total_tokens_spent, submitted_cards_data, promised_values = coordinate_committee_contributions(
            comm_objs, contract, round_count, promised_supplier, all_declarations, banker_score, intern_score=intern_score
        )

        has_toxic = any(c.card_type == CardType.TOXIC for c in submitted_cards)

        # Seguro Contra Sinistro da DLC: apólice cobre e descarta o ativo tóxico antes da apuração
        if active_directive and active_directive.id == "SEGURO_CONTRA_SINISTRO" and has_toxic:
            submitted_cards = [c for c in submitted_cards if c.card_type != CardType.TOXIC]

        deck.discard(submitted_cards)
        is_pure_bankers = all(p.role == Role.BANKER for p in comm_objs)
        is_success, total_val, has_req = evaluate_contract_outcome(submitted_cards, total_tokens_spent, contract, is_pure_banker_committee=is_pure_bankers)

        # Chamada de Margem da DLC: Se falhou estritamente por insumo e há tokens para cobrir
        if active_directive and active_directive.id == "CHAMADA_DE_MARGEM" and not is_success and not has_req:
            if total_val >= contract.target_value:
                available_tokens = sum(p.interest_tokens for p in players if p.role == Role.BANKER)
                if available_tokens >= 2:
                    needed = 2
                    for p in players:
                        if p.role == Role.BANKER and p.interest_tokens > 0:
                            take = min(needed, p.interest_tokens)
                            p.interest_tokens -= take
                            needed -= take
                            if needed == 0:
                                break
                    has_req = True
                    is_success = True

        # Telemetria do resultado desta rodada
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

        last_round_success = is_success

        # Efeitos de Compliance da DLC pós-resolução:
        if active_directive:
            chair_obj = players[curr_chair]
            if active_directive.id == "AUDITORIA_CVM" and submitted_cards_data:
                audited = rng.choice(submitted_cards_data)
                a_pid = audited['player_id']
                has_toxic_in_audited = any(c['type'] == CardType.TOXIC.name for c in audited['cards'])
                if has_toxic_in_audited:
                    for bp in players:
                        if bp.role == Role.BANKER:
                            bp.suspicions[a_pid] = 1.00
                            bp.known_traitors.add(a_pid)
                elif audited.get('is_req_responsible') and has_req:
                    for bp in players:
                        if bp.role == Role.BANKER:
                            bp.suspicions[a_pid] = max(0.05, bp.suspicions[a_pid] - 0.25)
            elif active_directive.id == "CONTABILIDADE_SEGREGADA" and submitted_cards_data:
                c_candidates = [d for d in submitted_cards_data if d['player_id'] != chair_obj.id]
                if c_candidates:
                    audited = max(c_candidates, key=lambda d: chair_obj.suspicions[d['player_id']])
                    a_pid = audited['player_id']
                    has_toxic_in_audited = any(c['type'] == CardType.TOXIC.name for c in audited['cards'])
                    if has_toxic_in_audited:
                        for bp in players:
                            if bp.role == Role.BANKER:
                                bp.suspicions[a_pid] = 1.00
                                bp.known_traitors.add(a_pid)
                    elif audited.get('is_req_responsible') and has_req:
                        for bp in players:
                            if bp.role == Role.BANKER:
                                bp.suspicions[a_pid] = max(0.05, bp.suspicions[a_pid] - 0.35)
                    else:
                        for bp in players:
                            if bp.role == Role.BANKER:
                                bp.suspicions[a_pid] = max(0.05, bp.suspicions[a_pid] - 0.20)

        credits_awarded = []
        if is_success:
            banker_score += 1
            for p in comm_objs:
                p.claim_success_credit()
                credits_awarded.append(p.id)

            passed_members.update(approved_committee)

            for bp in players:
                if bp.role == Role.BANKER:
                    for cid in approved_committee:
                        if cid != bp.id and cid not in bp.known_traitors:
                            # Calibração Bayesiana Real por Dificuldade e Custo do Tier:
                            if contract.tier == 1:
                                bp.suspicions[cid] = min(0.35, bp.suspicions[cid])
                            elif contract.tier == 2:
                                if bp.id in approved_committee:
                                    bp.suspicions[cid] = min(0.22, bp.suspicions[cid])
                                else:
                                    bp.suspicions[cid] = min(0.28, bp.suspicions[cid])
                            elif contract.tier in (3, 4):
                                if bp.id in approved_committee:
                                    bp.suspicions[cid] = min(0.16, bp.suspicions[cid])
                                else:
                                    bp.suspicions[cid] = min(0.22, bp.suspicions[cid])
                            elif contract.tier == 5:
                                if bp.id in approved_committee:
                                    bp.suspicions[cid] = min(0.12, bp.suspicions[cid])
                                else:
                                    bp.suspicions[cid] = min(0.18, bp.suspicions[cid])
                            else:
                                # Tiers 6+: contratos de custo 2 cartas e metas pesadas
                                if bp.id in approved_committee:
                                    bp.suspicions[cid] = min(0.10, bp.suspicions[cid])
                                else:
                                    bp.suspicions[cid] = min(0.14, bp.suspicions[cid])

            if round_count == 2:
                r2_passed_comm = list(approved_committee)

            # Dedução de Vindicação Calibrada (The Resistance / Sem Falsa Acusação Cega):
            for cp in list(conflict_pairs):
                v_members = [cid for cid in approved_committee if cid in cp]
                if len(cp) == 2 and len(v_members) == 1:
                    vindicated_pid = v_members[0]
                    traitor_pid = next(other for other in cp if other != vindicated_pid)
                    for bp in players:
                        if bp.role == Role.BANKER:
                            # Se o próprio banqueiro foi quem passou a missão (ou se o vindicado já era comprovadamente leal <= 0.08):
                            # Certeza matemática de que o rival do conflito é o traidor.
                            is_proven_vindicated = (bp.id == vindicated_pid or bp.suspicions[vindicated_pid] <= 0.08)
                            if is_proven_vindicated:
                                bp.suspicions[traitor_pid] = 1.00
                                bp.known_traitors.add(traitor_pid)
                                if bp.id != vindicated_pid:
                                    bp.suspicions[vindicated_pid] = max(0.05, bp.suspicions[vindicated_pid] - 0.20)
                            else:
                                # Se o membro que passou não é matematicamente comprovado (pode ter jogado camuflado):
                                # Alivia moderadamente a suspeita do vindicado e eleva a do rival, mas SEM rotulá-lo como traidor absoluto 1.00
                                bp.suspicions[vindicated_pid] = max(0.12, bp.suspicions[vindicated_pid] - 0.15)
                                bp.suspicions[traitor_pid] = min(0.70, max(bp.suspicions[traitor_pid], 0.60))

                    # Se algum banqueiro comprovou, adiciona aos acusados públicos
                    if any(bp.role == Role.BANKER and bp.suspicions[traitor_pid] >= 0.95 for bp in players):
                        public_accused.add(traitor_pid)
                    if vindicated_pid in public_accused:
                        public_accused.remove(vindicated_pid)
                    conflict_pairs.remove(cp)
        else:
            intern_score += 1

            veterans = [cid for cid in approved_committee if cid in passed_members]
            newcomers = [cid for cid in approved_committee if cid not in passed_members]
            sup_pids = [promised_supplier] if isinstance(promised_supplier, int) else (list(promised_supplier) if promised_supplier else [])
            partner_of = {cid: next(other for other in approved_committee if other != cid) for cid in approved_committee} if len(approved_committee) == 2 else {}

            # Caso 1: Falha por quebra de insumo (Fornecedor prometido não entregou)
            submitted_req_count = sum(1 for c in submitted_cards if c.card_type in (contract.req_commodity, CardType.WILD)) if contract.req_commodity else 0
            if contract.req_commodity is not None and not has_req and len(sup_pids) >= 1:
                # Se apenas 1 fornecedor prometeu e não entregou:
                if len(sup_pids) == 1:
                    culprit = sup_pids[0]
                    public_accused.add(culprit)
                    innocent_partners = [cid for cid in approved_committee if cid != culprit]
                    for ip in innocent_partners:
                        if ip in public_accused:
                            public_accused.remove(ip)

                    for bp in players:
                        if bp.role == Role.BANKER:
                            bp.suspicions[culprit] = 1.00
                            bp.known_traitors.add(culprit)
                            for ip in innocent_partners:
                                if bp.id != ip and ip not in bp.known_traitors:
                                    bp.suspicions[ip] = min(0.18, bp.suspicions[ip])

                            if conflict_pairs:
                                for cp in list(conflict_pairs):
                                    if culprit in cp:
                                        vindicated = next(other for other in cp if other != culprit)
                                        bp.suspicions[vindicated] = max(0.05, bp.suspicions[vindicated] - 0.20)
                                        conflict_pairs.remove(cp)

                    for bp in players:
                        if bp.role == Role.BANKER:
                            for op in players:
                                if op.id not in (culprit, bp.id) and op.id not in innocent_partners:
                                    bp.suspicions[op.id] = min(0.35, bp.suspicions[op.id])

                # Se 2 fornecedores prometeram (ex: 2 Baunilhas):
                elif len(sup_pids) == 2:
                    p_a, p_b = sup_pids[0], sup_pids[1]
                    innocent_partners = [cid for cid in approved_committee if cid not in sup_pids]
                    for ip in innocent_partners:
                        if ip in public_accused:
                            public_accused.remove(ip)

                    if submitted_req_count == 0:
                        # NENHUM entregou! Ambos quebraram o contrato e são traidores!
                        for culprit in [p_a, p_b]:
                            public_accused.add(culprit)
                            for bp in players:
                                if bp.role == Role.BANKER:
                                    bp.suspicions[culprit] = 1.00
                                    bp.known_traitors.add(culprit)
                    else:
                        # Exatamente 1 entregou e 1 quebrou:
                        # Se o Banqueiro bp for um dos fornecedores, ele sabe se entregou ou não!
                        for bp in players:
                            if bp.role == Role.BANKER:
                                if bp.id in sup_pids:
                                    other_sup = p_b if bp.id == p_a else p_a
                                    bp.suspicions[other_sup] = 1.00
                                    bp.known_traitors.add(other_sup)
                                    public_accused.add(other_sup)
                                else:
                                    # Para quem está de fora: só condena se 1 fornecedor for matematicamente comprovado (<= 0.08)
                                    proven_sups = [sid for sid in sup_pids if bp.suspicions[sid] <= 0.08]
                                    if len(proven_sups) == 1:
                                        traitor_sup = next(sid for sid in sup_pids if sid not in proven_sups)
                                        bp.suspicions[traitor_sup] = 1.00
                                        bp.known_traitors.add(traitor_sup)
                                        public_accused.add(traitor_sup)
                                    else:
                                        # Ambos não comprovados: par de conflito legítimo
                                        bp.suspicions[p_a] = min(0.70, max(bp.suspicions[p_a], 0.60))
                                        bp.suspicions[p_b] = min(0.70, max(bp.suspicions[p_b], 0.60))
                        
                        sup_set = set(sup_pids)
                        if sup_set not in conflict_pairs:
                            conflict_pairs.append(sup_set)

                    for bp in players:
                        if bp.role == Role.BANKER:
                            for ip in innocent_partners:
                                if bp.id != ip and ip not in bp.known_traitors:
                                    bp.suspicions[ip] = min(0.18, bp.suspicions[ip])

            # Caso 2: Falha em comitê de 2 membros
            elif len(approved_committee) == 2:
                if has_toxic or (contract.req_commodity is not None and not has_req):
                    # Sabotagem real comprovada (Ativo Tóxico ou Quebra de Insumo): Par de Conflito legítimo
                    comm_set = set(approved_committee)
                    if comm_set not in conflict_pairs:
                        conflict_pairs.append(comm_set)
                    for bp in players:
                        if bp.role == Role.BANKER:
                            if bp.id in approved_committee:
                                partner_id = partner_of[bp.id]
                                bp.suspicions[partner_id] = 1.00
                                bp.known_traitors.add(partner_id)
                                public_accused.add(partner_id)
                            else:
                                for cid in approved_committee:
                                    bp.suspicions[cid] = min(0.70, max(bp.suspicions[cid], 0.55))
                else:
                    # Falha puramente numérica de liquidez (ex: 1 Cobalto + 3 Titânio = 4 < 5)
                    for bp in players:
                        if bp.role == Role.BANKER:
                            for cid in approved_committee:
                                if cid != bp.id:
                                    bp.suspicions[cid] = min(0.45, max(bp.suspicions[cid], 0.38))

            # Caso 3: Comitê de 3 ou mais membros (Dedução de Teste Controlado e Conflito de Resistência)
            else:
                toxic_count = sum(1 for c in submitted_cards if c.card_type == CardType.TOXIC)
                new_cp = None

                for bp in players:
                    if bp.role != Role.BANKER:
                        continue

                    # Subcaso 3A: O Banqueiro estava dentro do comitê
                    if bp.id in approved_committee:
                        other_comm = [cid for cid in approved_committee if cid != bp.id]
                        # Parceiro é de confiança se já passou em missão anterior ou tem suspeita <= 0.25 ou é comprovado
                        trusted_partners = [cid for cid in other_comm if bp.suspicions[cid] <= 0.25 or (cid in passed_members and bp.suspicions[cid] < 0.35)]
                        untrusted_members = [cid for cid in other_comm if cid not in trusted_partners]

                        if has_toxic:
                            if toxic_count >= len(other_comm):
                                # Todos os outros membros jogaram tóxico!
                                for cid in other_comm:
                                    bp.suspicions[cid] = 1.00
                                    bp.known_traitors.add(cid)
                                    public_accused.add(cid)
                            else:
                                # Só condena a 1.00 se o parceiro for matematicamente comprovado (pigeonhole / inspeção <= 0.08)
                                proven_partners = [cid for cid in other_comm if bp.suspicions[cid] <= 0.08]
                                if len(proven_partners) == 1:
                                    culprit = next(cid for cid in other_comm if cid not in proven_partners)
                                    bp.suspicions[culprit] = 1.00
                                    bp.known_traitors.add(culprit)
                                    public_accused.add(culprit)
                                elif len(trusted_partners) == 1 and len(untrusted_members) == 1:
                                    # Teste controlado: a incógnita leva a maior suspeita (0.70), parceiro leal protegido de queima
                                    suspect = untrusted_members[0]
                                    tp = trusted_partners[0]
                                    bp.suspicions[suspect] = min(0.75, max(bp.suspicions[suspect], 0.65))
                                    bp.suspicions[tp] = min(0.35, bp.suspicions[tp] + 0.08)
                                    new_cp = set(other_comm)
                                else:
                                    new_cp = set(other_comm)
                                    for cid in other_comm:
                                        bp.suspicions[cid] = min(0.70, max(bp.suspicions[cid], 0.58))
                        else:
                            # Falha numérica de valor
                            for cid in other_comm:
                                bp.suspicions[cid] = min(0.48, bp.suspicions[cid] + 0.08)

                    # Subcaso 3B: O Banqueiro estava fora do comitê (no banco)
                    else:
                        if has_toxic:
                            proven_in_comm = [cid for cid in approved_committee if bp.suspicions[cid] <= 0.08]
                            tp_in_comm = [cid for cid in approved_committee if bp.suspicions[cid] <= 0.25 or (cid in passed_members and bp.suspicions[cid] < 0.35)]
                            untrusted_in_comm = [cid for cid in approved_committee if cid not in tp_in_comm]
                            if len(proven_in_comm) == len(approved_committee) - 1 and toxic_count == 1:
                                culprit = next(cid for cid in approved_committee if cid not in proven_in_comm)
                                bp.suspicions[culprit] = 1.00
                                bp.known_traitors.add(culprit)
                                public_accused.add(culprit)
                            elif len(untrusted_in_comm) == 1 and toxic_count == 1:
                                suspect = untrusted_in_comm[0]
                                bp.suspicions[suspect] = min(0.70, max(bp.suspicions[suspect], 0.60))
                                for tp in tp_in_comm:
                                    bp.suspicions[tp] = min(0.35, bp.suspicions[tp] + 0.06)
                                new_cp = set(approved_committee)
                            else:
                                new_cp = set(untrusted_in_comm if untrusted_in_comm else approved_committee)
                                for cid in approved_committee:
                                    if cid in tp_in_comm:
                                        bp.suspicions[cid] = min(0.35, bp.suspicions[cid] + 0.06)
                                    else:
                                        bp.suspicions[cid] = min(0.65, max(bp.suspicions[cid], 0.52))
                        else:
                            for cid in approved_committee:
                                bp.suspicions[cid] = min(0.45, bp.suspicions[cid] + 0.05)

                if new_cp and new_cp not in conflict_pairs:
                    conflict_pairs.append(new_cp)

                # Alívio para quem ficou de fora do comitê e não participou da falha
                for bp in players:
                    if bp.role == Role.BANKER:
                        for op in players:
                            if op.id not in approved_committee and op.id != bp.id:
                                if has_played.get(op.id, False):
                                    bp.suspicions[op.id] = max(0.05, bp.suspicions[op.id] - 0.03)

            # Dedução do Princípio da Casa dos Pombos (Pigeonhole):
            # 1. Se 2 traidores já são conhecidos, os demais 3 são 100% Banqueiros!
            for bp in players:
                if bp.role == Role.BANKER:
                    if len(bp.known_traitors) >= 2:
                        for other_p in players:
                            if other_p.id not in bp.known_traitors and other_p.id != bp.id:
                                bp.suspicions[other_p.id] = 0.05
                                passed_members.add(other_p.id)

            # 2. Se há 2 pares de conflito disjuntos cobrindo 4 jogadores, o 5º jogador é 100% Banqueiro!
            if len(conflict_pairs) >= 2:
                for i in range(len(conflict_pairs)):
                    for j in range(i + 1, len(conflict_pairs)):
                        cp1, cp2 = conflict_pairs[i], conflict_pairs[j]
                        if len(cp1.intersection(cp2)) == 0 and len(cp1.union(cp2)) == 4:
                            all_cp_players = cp1.union(cp2)
                            fifth_players = [p.id for p in players if p.id not in all_cp_players]
                            if fifth_players:
                                proven_banker = fifth_players[0]
                                passed_members.add(proven_banker)
                                for bp in players:
                                    if bp.role == Role.BANKER:
                                        bp.suspicions[proven_banker] = 0.05

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
                'directive': {
                    'id': active_directive.id,
                    'name': active_directive.name,
                    'category': active_directive.category.value
                } if active_directive else None,
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
