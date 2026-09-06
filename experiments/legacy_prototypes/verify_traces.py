# -*- coding: utf-8 -*-
import json

with open('game_traces.json', 'r', encoding='utf-8') as f:
    traces = json.load(f)

for key, match in traces.items():
    print(f"\n=== {key.upper()} (Vencedor: {match['final_winner']} em {match['total_rounds']} rodadas) ===")
    for r in match['rounds']:
        sub_desc = ' + '.join([f"P{s['player_id']}: {s['cards'][0]['name']}({s['cards'][0]['effective']}pts)" for s in r['submitted']])
        print(f"  R{r['round_num']} ({r['contract']['name']} - Target {r['contract']['target']}): {sub_desc} => Total {r['total_value']} pts (Sucesso: {r['is_success']})")
