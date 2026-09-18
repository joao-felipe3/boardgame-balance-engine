import sys, os
sys.path.insert(0, os.path.abspath('.'))
from src.btg import simulate_single_match, Role, BankerProfile, InternProfile
from collections import Counter

# Forensic breakdown of 1,000 matches
total_matches = 1000
intern_entry_method = Counter() # How did intern get into failing committee?
fail_causes_by_round = {r: Counter() for r in range(1, 8)}
intern_count_in_fails = {r: Counter() for r in range(1, 8)}

for s in range(total_matches):
    res = simulate_single_match(s, seed=112233 + s, record_trace=True)
    meta = res['players_metadata']
    roles = {p['id']: p['role'] for p in meta}
    for r in res['rounds_data']:
        rnd = r['round_num']
        if not r['is_success']:
            comm = r['committee']
            ch = r['chair_id']
            ch_role = roles[ch]
            num_interns = sum(1 for pid in comm if roles[pid] == 'Estagiario')
            intern_count_in_fails[rnd][num_interns] += 1
            
            # Why did it fail?
            c = r['contract']
            has_toxic = any(c['type'] == 'TOXIC' for cd in r['submitted'] for c in cd['cards'])
            has_req = r['has_req']
            pts = r['total_value']
            tgt = c['target']
            
            if not has_req:
                fail_causes_by_round[rnd]['missing_req'] += 1
            elif has_toxic:
                fail_causes_by_round[rnd]['toxic'] += 1
            else:
                fail_causes_by_round[rnd]['value_deficit'] += 1
                
            if num_interns > 0:
                # How did intern enter?
                # Check consecutive_vetoes
                v_count = r.get('consecutive_vetoes', 0)
                # If v_count >= 3: it was forced
                # Wait, let's see if it was proposed by Banker or Intern
                if ch_role == 'Estagiario':
                    intern_entry_method[f"R{rnd}_chair_was_intern"] += 1
                else:
                    intern_entry_method[f"R{rnd}_chair_was_banker"] += 1

print(f"ANÁLISE FORENSE DE {total_matches} PARTIDAS:")
for rnd in range(1, 8):
    print(f"\n--- Rodada {rnd} ---")
    print(f"  Causas de Falha: {dict(fail_causes_by_round[rnd])}")
    print(f"  Estagiários no Comitê que falhou: {dict(intern_count_in_fails[rnd])}")

print("\n--- Como o Estagiário entrou no comitê que falhou? ---")
for k, v in intern_entry_method.most_common(20):
    print(f"  {k:35s}: {v:5d}")
