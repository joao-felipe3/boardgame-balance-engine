import sys, os
sys.path.insert(0, os.path.abspath('.'))
from src.btg import simulate_single_match

for s in range(5):
    res = simulate_single_match(s, seed=20260900 + s, record_trace=True)
    print('='*70)
    w = res['winner']
    v = res['total_vetoes']
    fc = res['forced_committees']
    print(f'JOGO {s}: Winner={w}, Vetoes={v}, Forced={fc}')
    meta = res['players_metadata']
    print('Jogadores:', {p['id']: p['role'] for p in meta})
    for r in res['rounds_data']:
        rnd = r['round_num']
        c = r['contract']
        c_tier = c['tier']
        c_tgt = c['target']
        c_req = c['req_commodity']
        ch = r['chair_id']
        cm = r['committee']
        suc = r['is_success']
        tok = r['total_tokens_spent']
        print(f'  R{rnd} (Tier {c_tier}, Meta {c_tgt}, Req {c_req}) : Chair={ch}, Comm={cm}, Suc={suc}, Tok={tok}')
        if not suc:
            cards = [(cd['player_id'], cd['cards'], cd['tokens_spent']) for cd in r['submitted']]
            print(f'    FALHA! Submetido={cards}')
