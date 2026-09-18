import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match, Role, BankerProfile, InternProfile
from src.btg.player import PlayerAI
import src.btg.engine as engine
import numpy as np

# Vamos testar essas correções essenciais em um script isolado

# 1. Dedução Global do Pigeonhole (Gabinete de Crise Lógico)
# Se há 2 pares de conflito disjuntos {A, B} e {C, D} em 5 jogadores:
# O 5º jogador é matematicamente 100% Banqueiro!
# E para os membros de cada par, seu parceiro é 100% Estagiário, e o outro par tem prob 50%.

# 2. Votação Sensata dos Banqueiros:
# Um Banqueiro NUNCA veta um comitê se:
# - Não tem traidor conhecido (known_traitors)
# - Não coloca 2 membros de um mesmo par de conflito juntos
# - Se a média de suspeita do comitê for razoável (< 0.50)
# - E na tentativa 3 (consecutive_vetoes >= 2), NUNCA VETA a menos que haja um traidor óbvio comprovado!

original_vote = PlayerAI.vote_on_proposal

def human_like_banker_vote(self, proposer, committee, contract, round_num, conflict_pairs=None, consecutive_vetoes=0, declarations=None):
    if self.role == Role.BANKER:
        # Rejeição se propositor ou membro é traidor conhecido
        if proposer in self.known_traitors or self.suspicions[proposer] >= 0.85:
            return False
        for p in committee:
            if p in self.known_traitors or self.suspicions[p] >= 0.85:
                return False

        # Nunca aprovar 2 membros do mesmo par de conflito juntos
        if conflict_pairs:
            for cp in conflict_pairs:
                if sum(1 for pid in committee if pid in cp) > 1:
                    return False

        # VETO DE EMERGÊNCIA (Tentativa 3 antes de comitê forçado):
        # Na mesa real, humanos NUNCA deixam cair no Banco Central se não houver traidores conhecidos!
        if consecutive_vetoes >= 2:
            return True

        # Rejeição técnica de insumo (só nas tentativas 1 e 2):
        if contract.req_commodity is not None and declarations:
            suppliers_in_comm = [pid for pid in committee if declarations[pid].claims_req]
            if len(suppliers_in_comm) < contract.req_commodity_count:
                return False

        # Rejeição por déficit de liquidez irrecuperável (> 3 pontos abaixo da meta)
        if declarations:
            total_declared = sum(declarations[pid].claimed_value for pid in committee)
            if total_declared < contract.target_value - 3:
                return False

        # Avaliação de confiança média da proposta:
        if self.id in committee:
            others = [p for p in committee if p != self.id]
            avg_sus = sum(self.suspicions[p] for p in others) / len(others) if others else 0.0
            return avg_sus <= 0.52
        else:
            avg_sus = sum(self.suspicions[p] for p in committee) / len(committee)
            return avg_sus <= 0.48

    return original_vote(self, proposer, committee, contract, round_num, conflict_pairs, consecutive_vetoes, declarations)

PlayerAI.vote_on_proposal = human_like_banker_vote

# 3. Refinar choose_optimal_committee para Banqueiros
original_choose = engine.choose_optimal_committee

def rational_choose(chair, players, contract, declarations, conflict_pairs=None, quarantined_pid=None, public_accused=None, passed_members=None):
    if chair.role == Role.BANKER:
        all_comms = list(__import__('itertools').combinations(range(5), contract.committee_size))
        accused_set = set(public_accused or [])
        passed_set = set(passed_members or [])
        evaluated = []

        for comm in all_comms:
            supplier_ids = []
            if contract.req_commodity is not None:
                suppliers = [pid for pid in comm if declarations[pid].claims_req]
                if len(suppliers) >= contract.req_commodity_count:
                    suppliers.sort(key=lambda pid: (chair.suspicions[pid], -declarations[pid].req_commodity_value))
                    supplier_ids = suppliers[:contract.req_commodity_count]

            has_req_cov = (contract.req_commodity is None or len(supplier_ids) >= contract.req_commodity_count)
            total_dec = sum(declarations[pid].claimed_value for pid in comm)
            is_viable = (total_dec >= contract.target_value)
            
            # Penalidade severa para traidores conhecidos
            traitor_count = sum(1 for pid in comm if pid in chair.known_traitors or chair.suspicions[pid] >= 0.80)
            
            # Conflito: membros em par de conflito ou acusados abertos
            conflict_penalty = 0
            if conflict_pairs:
                for cp in conflict_pairs:
                    cp_members = sum(1 for pid in comm if pid in cp)
                    if cp_members > 1:
                        conflict_penalty += 10 # NUNCA colocar os dois juntos
                    elif cp_members == 1:
                        conflict_penalty += 1
            
            # Idoneidade e histórico
            avg_sus = sum(chair.suspicions[pid] for pid in comm if pid != chair.id) / len(comm)
            untested_count = sum(1 for pid in comm if pid != chair.id and pid not in passed_set and chair.suspicions[pid] >= 0.25)
            has_chair = (chair.id in comm)
            bench_count = sum(1 for pid in comm if declarations[pid].prefers_bench)

            evaluated.append({
                'comm': list(comm),
                'supplier_ids': supplier_ids,
                'has_req_cov': has_req_cov,
                'is_viable': is_viable,
                'traitor_count': traitor_count,
                'conflict_penalty': conflict_penalty,
                'untested_count': untested_count,
                'avg_sus': avg_sus,
                'bench_count': bench_count,
                'has_chair': has_chair,
                'total_dec': total_dec
            })

        # ORDENAÇÃO RACIONAL:
        # 1. Zero traidores conhecidos
        # 2. Sem dois do mesmo conflito (conflict_penalty < 10)
        # 3. Menor suspeita média dos membros
        # 4. Menor número de operadores não testados (priorizar o núcleo comprovado)
        # 5. Cobertura de insumo (dentro do grupo confiável)
        # 6. Viabilidade de liquidez
        # 7. Presença do Chairman
        # 8. Evitar banco
        evaluated.sort(key=lambda x: (
            x['traitor_count'],
            x['conflict_penalty'],
            round(x['avg_sus'], 2),
            x['untested_count'],
            not x['has_req_cov'],
            not x['is_viable'],
            not x['has_chair'],
            x['bench_count'],
            -x['total_dec']
        ))
        best = evaluated[0]
        return best['comm'], best['supplier_ids']
    else:
        return original_choose(chair, players, contract, declarations, conflict_pairs, quarantined_pid, public_accused, passed_members)

engine.choose_optimal_committee = rational_choose

print("=" * 80)
print("AUDITORIA COM GOVERNANÇA RACIONAL E DEDUÇÃO HUMANA (2000 PARTIDAS POR CENÁRIO)")
print("=" * 80)

for label, bp_mode, ip_mode in [
    ("Mesa Real Mista (Human-like Mixed)", "MIXED", "MIXED"),
    ("Auditores Equilibrados vs Sleepers", BankerProfile.BALANCED, InternProfile.B_SLEEPER),
    ("Auditores Pragmáticos vs Blefadores", BankerProfile.PRAGMATIC, InternProfile.A_AGGRESSIVE),
    ("Auditores Conservadores vs Oportunistas", BankerProfile.CONSERVATIVE, InternProfile.D_OPPORTUNIST),
]:
    b_wins = 0
    i_wins = 0
    vetoes_total = 0
    forced_total = 0
    lockouts = 0
    
    n_games = 2000
    for i in range(n_games):
        res = simulate_single_match(i, seed=20260900 + i, banker_profile=bp_mode, intern_profile=ip_mode)
        if res['winner'] == 'Banqueiro':
            b_wins += 1
        else:
            i_wins += 1
        vetoes_total += res['total_vetoes']
        forced_total += res['forced_committees']
        if res['intern_lockout']:
            lockouts += 1

    print(f"\n[{label}]")
    print(f"  Vitórias Banqueiros : {b_wins:4d} ({b_wins/n_games*100:5.1f}%)")
    print(f"  Vitórias Estagiários: {i_wins:4d} ({i_wins/n_games*100:5.1f}%)")
    print(f"  Média de Vetos/Jogo : {vetoes_total/n_games:4.2f}")
    print(f"  Comitês Forçados    : {forced_total:4d} ({forced_total/n_games*100:5.1f}% das partidas)")
    print(f"  Taxa de Lockout     : {lockouts:4d} ({lockouts/n_games*100:5.1f}%)")
