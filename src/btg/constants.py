# -*- coding: utf-8 -*-
"""
BTG Madagascar - Constantes, Enums e Catálogos de Regras
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, List


class CardType(Enum):
    CO = 'Cobalto (+1)'
    VN = 'Baunilha (+2)'
    TI = 'Titanio (+3)'
    SF = 'Safira (+4)'
    WILD = 'Ouro Liquido (+4 / Coringa)'
    TOXIC = 'Ativo Toxico (-4)'


CARD_BASE_VALUES: Dict[CardType, int] = {
    CardType.CO: 1,
    CardType.VN: 2,
    CardType.TI: 3,
    CardType.SF: 4,
    CardType.WILD: 4,
    CardType.TOXIC: -4
}

INITIAL_COMMERCIAL_DECK: List[CardType] = (
    [CardType.CO] * 22 +
    [CardType.VN] * 18 +
    [CardType.TI] * 10 +
    [CardType.SF] * 6 +
    [CardType.WILD] * 2 +
    [CardType.TOXIC] * 2
)


class Role(Enum):
    BANKER = 'Banqueiro'
    INTERN = 'Estagiario'


class BankerProfile(Enum):
    BALANCED = 'Equilibrado (Auditoria v14 Padrão)'
    CONSERVATIVE = 'Conservador (Auditor Rígido / Veto Firme)'
    PRAGMATIC = 'Pragmático (Foco em Liquidez e Metas)'
    STRATEGIST = 'Estrategista (Rotação de Banco e Ativos)'


class InternProfile(Enum):
    A_AGGRESSIVE = 'A (Agressivo / Blefe Imediato)'
    B_SLEEPER = 'B (Infiltracao Profunda / Sleeper)'
    C_HEDGE = 'C (Hedge / Retencao Economica)'
    D_OPPORTUNIST = 'D (Oportunista / Camaleão Adaptativo)'
    E_TECHNICIAN = 'E (Técnico / Falsa Idoneidade)'


@dataclass
class ContractSpec:
    name: str
    tier: int
    committee_size: int          # Tamanho efetivo do comitê (pode ser expandido em runtime)
    cost_per_player: int
    target_value: int
    req_commodity: Optional[CardType] = None
    req_commodity_count: int = 1
    # Se True, o comitê só é expandido ao tamanho 4 se o Tier anterior falhou
    # (Tier 5: comitê base=3, expande para 4 apenas após derrota no Tier 4)
    expandable_on_prior_failure: bool = False
    expanded_committee_size: int = 0  # Tamanho expandido (0 = sem expansão possível)


SEVEN_TIERS_CATALOG: Dict[int, List[ContractSpec]] = {
    # ─── NOTA DE CALIBRAÇÃO ────────────────────────────────────────────────────
    # Nova economia de recursos: kit inicial = 3 cartas (CO+VN+1 secreta).
    # Sem recomposição de mão geral: bench players compram 1 carta por rodada;
    # membros do comitê não repõem até ficarem no banco.
    #
    # Média de contribuição por carta ao longo das primeiras rodadas:
    #   CO=1, VN=2, TI=3 (mercado), SF=4 (mercado tardio), avg ~2.0–2.5 pts
    #   Banco acumula: 1 carta/rodada → jogador que benchou N rodadas tem N cartas extras.
    # ───────────────────────────────────────────────────────────────────────────
    1: [
        ContractSpec("Arbitragem Simples", 1, committee_size=2, cost_per_player=1, target_value=3),
        ContractSpec("Exportacao de Baunilha", 1, committee_size=2, cost_per_player=1, target_value=4, req_commodity=CardType.VN, req_commodity_count=1),
    ],
    2: [
        ContractSpec("Mineracao de Cobalto", 2, committee_size=2, cost_per_player=1, target_value=5, req_commodity=CardType.CO, req_commodity_count=1),
        ContractSpec("Lote Agricola", 2, committee_size=2, cost_per_player=1, target_value=5, req_commodity=CardType.VN, req_commodity_count=1),
    ],
    3: [
        # 3 ops, 1 carta cada. Quota de 2x TI → Banqueiros precisam comprar TI no mercado.
        # Bench players ricos em recurso entram aqui.
        # Alvo ≥6 simétrico: acessível com 2x TI (3+3=6), permitindo aos banqueiros estabilizar a R3.
        ContractSpec("Sindicato de Titanio", 3, committee_size=3, cost_per_player=1, target_value=6, req_commodity=CardType.TI, req_commodity_count=2),
        ContractSpec("Logistica Portuaria", 3, committee_size=3, cost_per_player=1, target_value=6, req_commodity=CardType.CO, req_commodity_count=2),
    ],
    4: [
        # 3 ops, 1 carta cada. Mix: 1–2 players desgastados + 1 bench rico.
        # Avg contrib: 2.5 pts × 3 = 7.5 pts + tokens. Alvo ≥8.
        ContractSpec("Refino Metalurgico", 4, committee_size=3, cost_per_player=1, target_value=7, req_commodity=CardType.TI, req_commodity_count=2),
        ContractSpec("Consorcio Agro-Industrial", 4, committee_size=3, cost_per_player=1, target_value=8, req_commodity=CardType.VN, req_commodity_count=2),
    ],
    5: [
        # 3–4 ops, 1 carta cada. Com bench players com 5–6 cartas,
        # avg contrib sobe para 3.0 pts × 3 = 9 pts + tokens (2–3) = ~11–12 pts.
        # Alvo ≥10 (expansão: 4 membros = mais fácil de atingir, mas abre janela para Intern).
        ContractSpec("Megaconsorcio Industrial", 5, committee_size=3, cost_per_player=1, target_value=10,
                     req_commodity=CardType.TI, req_commodity_count=2,
                     expandable_on_prior_failure=True, expanded_committee_size=4),
        ContractSpec("Cofre de Commodities", 5, committee_size=3, cost_per_player=1, target_value=10,
                     req_commodity=CardType.VN, req_commodity_count=2,
                     expandable_on_prior_failure=True, expanded_committee_size=4),
    ],
    6: [
        # 3 ops, 2 cartas cada. Bench players com 5–7 cartas contribuem 2 × ~3.5 = 7 pts.
        # 3 membros × 7 = 21 pts. Alvo ≥13–14 pts: acessível com boa acumulação.
        ContractSpec("Complexo Greenfield", 6, committee_size=3, cost_per_player=2, target_value=13, req_commodity=CardType.TI, req_commodity_count=2),
        ContractSpec("Consorcio Safira", 6, committee_size=3, cost_per_player=2, target_value=14, req_commodity=CardType.SF, req_commodity_count=2),
    ],
    7: [
        # 3 ops, 2 cartas cada. Clímax da Rodada 7 (Opção 2 - Catálogo Duplo):
        # Opção A: Holding Global BTG (Meta 15 pts, 1x Safira) - caminho nobre/financeiro
        ContractSpec("Holding Global BTG", 7, committee_size=3, cost_per_player=2, target_value=15, req_commodity=CardType.SF, req_commodity_count=1),
        # Opção B: Fundo Soberano Madagascar (Meta 16 pts, 2x Titânio) - caminho industrial/commodities pesadas
        ContractSpec("Fundo Soberano Madagascar", 7, committee_size=3, cost_per_player=2, target_value=16, req_commodity=CardType.TI, req_commodity_count=2),
    ],
}

