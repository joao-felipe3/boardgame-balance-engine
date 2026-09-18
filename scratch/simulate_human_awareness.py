import sys, os
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import Role, BankerProfile, InternProfile
from src.btg.constants import SEVEN_TIERS_CATALOG, CardType
from src.btg.deck import DeckManager, ResourceCard
from src.btg.player import PlayerAI
from src.btg.engine import coordinate_committee_contributions, evaluate_contract_outcome
import numpy as np

# Vamos simular como humanos competentes jogam BTG Madagascar presencialmente:
# 1. R1: Chair escolhe a si mesmo e 1 outro operador aleatório (pois é R1).
# 2. R2: Se R1 passou, o novo Chair convoca a si mesmo e um membro FRESCO DO BANCO com token.
# 3. Se R1 falhou: flagrante/conflito! O sabotador é isolado. O Chairman da R2 monta com os outros.
# 4. R3+: Assim que 3 operadores são identificados como o núcleo limpo, ELES TRANCAM A MESA (LOCKOUT)!
#    Eles NUNCA chamam os outros 2, NUNCA votam a favor de propostas dos traidores, e NUNCA deixam dar 3 vetos.

def simulate_human_game(seed):
    rng = np.random.default_rng(seed)
    roles = [Role.BANKER, Role.BANKER, Role.BANKER, Role.INTERN, Role.INTERN]
    rng.shuffle(roles)
    banker_ids = [i for i, r in enumerate(roles) if r == Role.BANKER]
    intern_ids = [i for i, r in enumerate(roles) if r == Role.INTERN]

    deck = DeckManager(seed=seed)
    deck.refill_open_market(3)
    players = [
        PlayerAI(i, roles[i], BankerProfile.BALANCED if roles[i]==Role.BANKER else InternProfile.B_SLEEPER, rng)
        for i in range(5)
    ]
    for p in players:
        p.hand = [ResourceCard(CardType.CO), ResourceCard(CardType.TI)] + deck.draw_blind(2)

    banker_score = 0
    intern_score = 0
    curr_chair = 0
    
    # Memória humana
    known_traitors_by_bankers = set()
    conflict_pairs = []
    passed_clean_members = set()

    for rnd in range(1, 8):
        contract = SEVEN_TIERS_CATALOG[rnd][0]
        c_size = contract.committee_size

        # Quem propõe?
        # Se o Chair da vez for um traidor conhecido por todos os banqueiros:
        # Os banqueiros vetam a proposta do traidor. O martelo passa para o próximo!
        # Se passar 2 vezes e cair no 3º veto, o 3º Chair (se for banqueiro) propõe o comitê limpo e todos aprovam!
        chair = players[curr_chair]
        while chair.id in known_traitors_by_bankers:
            curr_chair = (curr_chair + 1) % 5
            chair = players[curr_chair]

        # Agora o Chair monta a proposta humana:
        declarations = {p.id: p.make_public_declaration(contract, rnd) for p in players}

        if chair.role == Role.BANKER:
            # Humano Banqueiro:
            # 1. Elimina traidores conhecidos
            candidates = [p.id for p in players if p.id not in known_traitors_by_bankers]
            
            # Se já conhecemos os 3 banqueiros (lockout total):
            clean_bankers = [cid for cid in candidates if cid in passed_clean_members]
            if len(clean_bankers) >= c_size:
                chosen_comm = clean_bankers[:c_size]
            else:
                # Prioriza quem tem menor suspeita / está limpo / tem recursos frescos
                # Se rnd == 2 e rnd 1 passou: traz o fresh do banco com token!
                if rnd == 2 and passed_clean_members:
                    bench_fresh = [cid for cid in candidates if cid not in passed_clean_members and players[cid].interest_tokens > 0]
                    partner = bench_fresh[0] if bench_fresh else candidates[1]
                    chosen_comm = [chair.id, partner] if chair.id != partner else [chair.id, candidates[0]]
                else:
                    # Escolhe os candidatos com menor suspeita cadastral
                    candidates.sort(key=lambda cid: (chair.suspicions[cid], -players[cid].interest_tokens))
                    chosen_comm = candidates[:c_size]
        else:
            # Chair é Estagiário (ainda não descoberto): coloca a si mesmo e mais outros
            chosen_comm = [chair.id] + [p.id for p in players if p.id != chair.id][:c_size - 1]

        # Verifica se tem cobertura de insumo
        assigned_sup = None
        if contract.req_commodity:
            sups = [pid for pid in chosen_comm if declarations[pid].claims_req]
            assigned_sup = sups[:contract.req_commodity_count]

        # Execução do Comitê
        comm_objs = [players[pid] for pid in chosen_comm]
        # Bancários no banco acumulam juros e compram mercado
        for p in players:
            if p.id not in chosen_comm:
                p.accumulate_holding_interest()
                if p.role == Role.BANKER:
                    # Compra mercado
                    for ct in [contract.req_commodity, CardType.TI, CardType.SF]:
                        if ct in deck.open_market:
                            c = deck.draw_from_market(ct)
                            p.hand.append(c)
                            break
                    else:
                        p.hand.append(deck.draw_blind(1)[0])
                else:
                    p.hand.append(deck.draw_blind(1)[0])

        submitted_cards, total_tokens_spent, submitted_cards_data, promised_values = coordinate_committee_contributions(
            comm_objs, contract, rnd, assigned_sup, declarations, banker_score, intern_score=intern_score
        )
        deck.discard(submitted_cards)

        is_pure_bankers = all(p.role == Role.BANKER for p in comm_objs)
        is_success, total_val, has_req = evaluate_contract_outcome(submitted_cards, total_tokens_spent, contract, is_pure_banker_committee=is_pure_bankers)

        if is_success:
            banker_score += 1
            passed_clean_members.update(chosen_comm)
            for bp in players:
                if bp.role == Role.BANKER:
                    for cid in chosen_comm:
                        if cid != bp.id:
                            bp.suspicions[cid] = min(0.08, bp.suspicions[cid])
        else:
            intern_score += 1
            # Dedução Humana de Flagrante:
            # 1. Se quebrou insumo com fornecedor único prometido: CULPADO PEGO EM FLAGRANTE!
            if contract.req_commodity is not None and not has_req and assigned_sup and len(assigned_sup) == 1:
                culprit = assigned_sup[0]
                known_traitors_by_bankers.add(culprit)
                for bp in players:
                    if bp.role == Role.BANKER:
                        bp.known_traitors.add(culprit)
                        bp.suspicions[culprit] = 1.0
            # 2. Se falhou com 1 novato entre veteranos: CULPADO PEGO EM FLAGRANTE!
            veterans = [cid for cid in chosen_comm if cid in passed_clean_members]
            newcomers = [cid for cid in chosen_comm if cid not in passed_clean_members]
            if len(newcomers) == 1 and len(veterans) >= 1:
                culprit = newcomers[0]
                known_traitors_by_bankers.add(culprit)
                for bp in players:
                    if bp.role == Role.BANKER:
                        bp.known_traitors.add(culprit)
                        bp.suspicions[culprit] = 1.0
            elif len(chosen_comm) == 2:
                # Par de conflito 50/50
                conflict_pairs.append(set(chosen_comm))
                for bp in players:
                    if bp.role == Role.BANKER:
                        if bp.id in chosen_comm:
                            partner = next(other for other in chosen_comm if other != bp.id)
                            known_traitors_by_bankers.add(partner)
                            bp.known_traitors.add(partner)
                            bp.suspicions[partner] = 1.0

        curr_chair = (curr_chair + 1) % 5

        if banker_score >= 4:
            return 'Banqueiro', banker_score, intern_score
        if intern_score >= 4:
            return 'Estagiário', banker_score, intern_score

    return ('Banqueiro' if banker_score > intern_score else 'Estagiário'), banker_score, intern_score

print("Rodando 2000 partidas com simulação de dedução humana real...")
b_wins = 0
i_wins = 0
for i in range(2000):
    winner, bs, is_ = simulate_human_game(500000 + i)
    if winner == 'Banqueiro':
        b_wins += 1
    else:
        i_wins += 1

print(f"Vitórias dos Banqueiros : {b_wins:4d} ({b_wins/2000*100:5.1f}%)")
print(f"Vitórias dos Estagiários: {i_wins:4d} ({i_wins/2000*100:5.1f}%)")
