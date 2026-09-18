import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.btg import simulate_single_match, InternProfile, BankerProfile
from collections import Counter

print("=" * 80)
print("AUDITORIA CONSOLIDADA DE EQUILÍBRIO (2000 PARTIDAS POR CENÁRIO)")
print("=" * 80)

# Cenário 1: Mesa padrão equilibrada (Auditores Padrão vs Sleeper/Mixed)
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
    
    n_games = 1000
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

    print(f"\n[{label}]", flush=True)
    print(f"  Vitórias Banqueiros : {b_wins:4d} ({b_wins/n_games*100:5.1f}%)", flush=True)
    print(f"  Vitórias Estagiários: {i_wins:4d} ({i_wins/n_games*100:5.1f}%)", flush=True)
    print(f"  Média de Vetos/Jogo : {vetoes_total/n_games:4.2f}", flush=True)
    print(f"  Comitês Forçados    : {forced_total:4d} ({forced_total/n_games*100:5.1f}% das partidas)", flush=True)
    print(f"  Taxa de Lockout     : {lockouts:4d} ({lockouts/n_games*100:5.1f}%)", flush=True)
