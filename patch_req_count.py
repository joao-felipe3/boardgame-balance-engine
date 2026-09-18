"""
Patch: eleva req_commodity_count para igualar committee_size
nos comites de 3 membros (Fase 1 da simulacao v15.0).
Executa substituicao cirurgica apenas nas linhas do catalogo afetadas.
"""
import re

with open("src/btg/constants.py", "r", encoding="utf-8") as f:
    content = f.read()

original = content

# Substitui req_commodity_count=2 apenas nas linhas que tambem tem committee_size=3
# Abordagem: processar linha a linha
lines = content.split("\n")
new_lines = []
changes = []

for i, line in enumerate(lines):
    # So modifica linhas ContractSpec com committee_size=3 e req_commodity_count=2
    if "ContractSpec(" in line and "committee_size=3" in line and "req_commodity_count=2" in line:
        new_line = line.replace("req_commodity_count=2", "req_commodity_count=3")
        changes.append(f"  L{i+1}: req_count 2->3  |  {line.strip()[:80]}")
        new_lines.append(new_line)
    # Tier 7 Holding Global: committee_size=3 mas req_count=1 -> 3
    elif "ContractSpec(" in line and "committee_size=3" in line and "req_commodity_count=1" in line:
        new_line = line.replace("req_commodity_count=1", "req_commodity_count=3")
        changes.append(f"  L{i+1}: req_count 1->3  |  {line.strip()[:80]}")
        new_lines.append(new_line)
    else:
        new_lines.append(line)

new_content = "\n".join(new_lines)

if new_content == original:
    print("AVISO: Nenhuma mudanca detectada! Verifique o arquivo.")
else:
    with open("src/btg/constants.py", "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"OK: {len(changes)} linha(s) modificada(s):")
    for c in changes:
        print(c)
