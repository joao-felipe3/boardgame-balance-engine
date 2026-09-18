import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match, Role, BankerProfile, InternProfile
from src.btg.player import PlayerAI
import src.btg.engine as engine
import numpy as np

# Vamos testar o impacto dessas 4 correções no equilíbrio do jogo:
# 1. choose_optimal_committee prioriza Confiança/Idoneidade ANTES de promessas de insumo
original_choose = engine.choose_optimal_committee

def refined_choose(chair, players, contract, declarations, conflict_pairs=None, quarantined_pid=None, public_accused=None, passed_members=None):
    if chair.role == Role.BANKER:
        # Chairman Banqueiro: Confiança e Idoneidade são prioritárias
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
            
            # Penalidade máxima para traidores conhecidos ou acusados públicos
            traitor_count = sum(1 for pid in comm if pid in chair.known_traitors or chair.suspicions[pid] >= 0.80)
            accused_count = sum(1 for pid in comm if pid in accused_set or (conflict_pairs and any(pid in cp for cp in conflict_pairs)))
            
            # Membros de alta confiança (passaram missões ou suspeita baixa)
            avg_sus = sum(chair.suspicions[pid] for pid in comm if pid != chair.id) / len(comm)
            untested_count = sum(1 for pid in comm if pid != chair.id and pid not in passed_set and chair.suspicions[pid] >= 0.25)
            bench_count = sum(1 for pid in comm if declarations[pid].prefers_bench)
            has_chair = (chair.id in comm)

            evaluated.append({
                'comm': list(comm),
                'supplier_ids': supplier_ids,
                'has_req_cov': has_req_cov,
                'is_viable': is_viable,
                'traitor_count': traitor_count,
                'accused_count': accused_count,
                'untested_count': untested_count,
                'avg_sus': avg_sus,
                'bench_count': bench_count,
                'has_chair': has_chair,
                'total_dec': total_dec
            })

        # ORDENAÇÃO RACIONAL HUMANA:
        # 1. Zero traidores conhecidos
        # 2. Mínimo de acusados / pares de conflito
        # 3. Menor número de operadores não testados (priorizar o núcleo confiável)
        # 4. Menor suspeita média
        # 5. Cobertura de insumo (dentro do grupo idôneo)
        # 6. Viabilidade de liquidez declarada
        # 7. Presença do Chairman
        # 8. Evitar banco
        # 9. Maior valor declarado
        evaluated.sort(key=lambda x: (
            x['traitor_count'],
            x['accused_count'],
            x['untested_count'],
            round(x['avg_sus'], 2),
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

engine.choose_optimal_committee = refined_choose

# 2. Votação de Emergência na 3ª tentativa
original_vote = PlayerAI.vote_on_proposal

def refined_vote(self, proposer, committee, contract, round_num, conflict_pairs=None, consecutive_vetoes=0, declarations=None):
    if self.role == Role.BANKER:
        # Se é a 3ª tentativa (consecutive_vetoes >= 2):
        # Na mesa real, os banqueiros votam SIM a qualquer proposta que não tenha traidores óbvios (suspeita >= 0.70)
        # para evitar a perda de controle da mesa pelo Banco Central!
        if consecutive_vetoes >= 2:
            if proposer in self.known_traitors or self.suspicions[proposer] >= 0.75:
                return False
            if any(p in self.known_traitors or self.suspicions[p] >= 0.75 for p in committee):
                return False
            return True

    return original_vote(self, proposer, committee, contract, round_num, conflict_pairs, consecutive_vetoes, declarations)

PlayerAI.vote_on_proposal = refined_vote

print("=" * 80)
print("TESTE DAS HEURÍSTICAS REFINADAS (2000 PARTIDAS POR CENÁRIO)")
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
