# -*- coding: utf-8 -*-
"""
BTG Madagascar - DLC: Diretrizes Regulatórias & Poderes Corporativos (v14.0)
=============================================================================
Módulo que implementa o baralho de eventos e poderes que modificam dinamicamente
as regras de rodada, auditoria, governança e economia sem quebrar a espinha
dorsal do jogo base.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import random


class DirectiveCategory(str, Enum):
    COMPLIANCE = "Compliance & Auditoria"
    ECONOMY = "Economia & Commodities"
    GOVERNANCE = "Governança & Votação"
    OPERATIONS = "Estrutura Operacional"


class DirectiveTriggerRegime(str, Enum):
    ALWAYS = "ALWAYS"          # Uma carta por rodada (R1 a R7)
    DICE_50 = "DICE_50"        # Dado 1d6: ativa se >= 4 (50% de chance por rodada)
    MIDGAME = "MIDGAME"        # Apenas nas rodadas críticas de virada (R3, R4, R5)
    CATCHUP = "CATCHUP"        # Apenas após a reprovação de um contrato anterior


@dataclass
class DirectiveCard:
    id: str
    name: str
    category: DirectiveCategory
    description: str
    flavor: str


# -----------------------------------------------------------------------------
# CATÁLOGO OFICIAL DE 14 DIRETRIZES REGULATÓRIAS
# -----------------------------------------------------------------------------
DIRECTIVES_CATALOG: List[DirectiveCard] = [
    # Categoria A: Compliance & Auditoria
    DirectiveCard(
        id="AUDITORIA_CVM",
        name="Auditoria CVM (Due Diligence)",
        category=DirectiveCategory.COMPLIANCE,
        description="O Chairman inspeciona 1 carta enviada ao cofre após a resolução, ganhando certeza dedutiva.",
        flavor="Uma intimação regulatória exige abertura pontual de sigilo fiscal da operação."
    ),
    DirectiveCard(
        id="QUARENTENA_REGULATORIA",
        name="Quarentena Regulatória",
        category=DirectiveCategory.COMPLIANCE,
        description="O operador sob maior suspeita pelo Chairman não pode ser escalado no comitê desta rodada.",
        flavor="Operador sob investigação formal tem credenciais suspensas provisoriamente."
    ),
    DirectiveCard(
        id="SEGURO_CONTRA_SINISTRO",
        name="Seguro Contra Sinistro (Hedge)",
        category=DirectiveCategory.COMPLIANCE,
        description="Se houver Ativo Tóxico no cofre revelado, a apólice anula o tóxico e o descarta, avaliando apenas cartas válidas.",
        flavor="Contrato de hedge corporativo cobre perdas decorrentes de fraudes e ativos podres na carteira."
    ),
    DirectiveCard(
        id="INSPECAO_DE_CARTEIRA",
        name="Inspeção de Carteira (Due Diligence)",
        category=DirectiveCategory.COMPLIANCE,
        description="O Chairman aponta 1 operador, que deve escolher e revelar 1 carta física da sua mão abertamente para a mesa.",
        flavor="Auditoria de conformidade exige demonstração pública de liquidez e idoneidade de ativos."
    ),
    DirectiveCard(
        id="CONTABILIDADE_SEGREGADA",
        name="Contabilidade Segregada (Auditoria Segmentada)",
        category=DirectiveCategory.COMPLIANCE,
        description="Nesta rodada, as cartas do comitê são colocadas em pilhas separadas por membro; o Chairman inspeciona as cartas de 1 membro antes de juntar tudo no cofre.",
        flavor="Procedimento de segregação de funções audita a custódia individual de cada operador do comitê."
    ),

    # Categoria B: Economia & Mercado de Commodities
    DirectiveCard(
        id="SUBSIDIO_GOVERNAMENTAL",
        name="Subsídio Governamental",
        category=DirectiveCategory.ECONOMY,
        description="Apoio público reduz a meta de liquidez do contrato em -2 pontos (mínimo de 3 pts).",
        flavor="Incentivo fiscal de fomento à infraestrutura em Madagascar alivia a meta de fechamento."
    ),
    DirectiveCard(
        id="CRISE_DE_OFERTA",
        name="Crise de Oferta (Choque de Custo)",
        category=DirectiveCategory.ECONOMY,
        description="Turbulência logística aumenta a meta de liquidez do contrato em +2 pontos.",
        flavor="Bloqueio portuário em Toamasina encarece as margens operacionais de remessa."
    ),
    DirectiveCard(
        id="SWAP_DE_COMMODITY",
        name="Swap Cambial de Commodities",
        category=DirectiveCategory.ECONOMY,
        description="A cota de insumo obrigatório do contrato é cancelada, transformando-o em Arbitragem Pura de valor.",
        flavor="Derivativo financeiro permite liquidar o contrato em dólares sintéticos em vez de commodity física."
    ),
    DirectiveCard(
        id="LEILAO_DE_BALCAO",
        name="Leilão Extraordinário de Balcão",
        category=DirectiveCategory.ECONOMY,
        description="Antes da votação, todos os operadores compram 1 carta adicional do topo para enriquecer as carteiras.",
        flavor="Liquidação relâmpago no pregão aberto injeta liquidez geral nas mãos dos operadores."
    ),
    DirectiveCard(
        id="REESTRUTURACAO_OFFSHORE",
        name="Reestruturação de Portfólio (Swap de Mão)",
        category=DirectiveCategory.ECONOMY,
        description="Antes da proposta, cada operador pode descartar até 2 cartas da mão e comprar 2 novas cartas do topo do baralho.",
        flavor="Mesa de câmbio reestrutura posições ilíquidas por ativos negociáveis no mercado spot."
    ),
    DirectiveCard(
        id="CHAMADA_DE_MARGEM",
        name="Chamada de Margem (Aporte de Liquidez)",
        category=DirectiveCategory.ECONOMY,
        description="Se o contrato falhar exclusivamente por falta de insumo obrigatório, a mesa pode queimar 2 Tokens de Rendimento para suprir a cota faltante e salvar a operação.",
        flavor="Aporte de capital emergencial dos sócios integraliza a garantia física pendente no contrato."
    ),
    DirectiveCard(
        id="LINHA_DE_CREDITO_SINDICAL",
        name="Linha de Crédito Sindical (Injeção de Liquidez)",
        category=DirectiveCategory.ECONOMY,
        description="Todos os operadores da mesa recebem imediatamente +1 Token de Rendimento da reserva antes da formação do comitê.",
        flavor="Consórcio bancário libera adiantamento de dividendos a todos os associados da mesa."
    ),

    # Categoria C: Governança Corporativa & Votação
    DirectiveCard(
        id="GOLDEN_SHARE",
        name="Golden Share (Voto de Minerva)",
        category=DirectiveCategory.GOVERNANCE,
        description="O voto do Chairman tem peso duplo (2 votos), facilitando a aprovação de propostas leais.",
        flavor="Ações de classe especial do acionista controlador conferem poder de desempate à presidência."
    ),
    DirectiveCard(
        id="PEDIDO_DE_VISTA",
        name="Pedido de Vista (Veto de Bancada)",
        category=DirectiveCategory.GOVERNANCE,
        description="Qualquer operador pode descartar 1 Token de Rendimento pessoal para cancelar a proposta sem queimar veto da mesa.",
        flavor="Conselheiro dissidente usa prerrogativa regimental para suspender pauta suspeita à custa de dividendos próprios."
    ),
    DirectiveCard(
        id="PACTO_DE_ACIONISTAS",
        name="Pacto de Acionistas (Aliança de Confiança)",
        category=DirectiveCategory.GOVERNANCE,
        description="O Chairman e mais 1 operador à sua escolha mostram secretamente 1 carta da mão um para o outro e a devolvem, verificando idoneidade mútua.",
        flavor="Acordo parassocial de acionistas estabelece aliança estratégica e verificação recíproca de ativos."
    ),
    DirectiveCard(
        id="SUPERMAIORIA_EXIGIDA",
        name="Supermaioria Qualificada",
        category=DirectiveCategory.GOVERNANCE,
        description="O comitê exige 4 votos favoráveis (em vez de 3) para ser aprovado pela mesa.",
        flavor="Cláusula pétrea do estatuto exige consenso de 80% do conselho para operações extraordinárias."
    ),
    DirectiveCard(
        id="DECRETO_PRESIDENCIAL",
        name="Decreto de Diretoria",
        category=DirectiveCategory.GOVERNANCE,
        description="O Chairman pode aprovar o comitê com apenas 2 votos favoráveis, superando vetos da oposição.",
        flavor="Resolução de urgência em gabinete dispensa quórum ordinário para evitar paralisia."
    ),

    # Categoria D: Estrutura Operacional
    DirectiveCard(
        id="COMITE_EXPANDIDO",
        name="Comitê Interdepartamental (+1 Membro)",
        category=DirectiveCategory.OPERATIONS,
        description="O tamanho do comitê aumenta em +1 operador (máximo de 4), adicionando mais um par de mãos.",
        flavor="Exigência de compliance agrega auditor adjunto à execução do contrato."
    ),
    DirectiveCard(
        id="FORCA_TAREFA_ENXUTA",
        name="Força-Tarefa Enxuta (-1 Membro)",
        category=DirectiveCategory.OPERATIONS,
        description="O tamanho do comitê é reduzido em -1 operador (mínimo de 2), exigindo mais compromisso individual.",
        flavor="Operação sigilosa restringe o número de operadores com acesso à chave do cofre."
    )
]


class DirectivesDeck:
    """Gerencia o baralho de cartas de diretrizes regulatórias da DLC."""

    def __init__(self, rng: Optional[random.Random] = None):
        self.rng = rng or random.Random()
        self.draw_pile: List[DirectiveCard] = list(DIRECTIVES_CATALOG)
        self.discard_pile: List[DirectiveCard] = []
        self.shuffle()

    def shuffle(self):
        self.rng.shuffle(self.draw_pile)

    def draw(self) -> Optional[DirectiveCard]:
        if not self.draw_pile:
            if not self.discard_pile:
                return None
            self.draw_pile = list(self.discard_pile)
            self.discard_pile = []
            self.shuffle()
        card = self.draw_pile.pop(0)
        self.discard_pile.append(card)
        return card

    def should_trigger(
        self,
        round_num: int,
        regime: DirectiveTriggerRegime,
        last_round_success: Optional[bool] = None
    ) -> bool:
        """Determina se uma diretriz deve ser sacada nesta rodada de acordo com o regime configurado."""
        if regime == DirectiveTriggerRegime.ALWAYS:
            return True

        elif regime == DirectiveTriggerRegime.DICE_50:
            # Dado d6: 1, 2, 3 = Inerte; 4, 5, 6 = Ativa (50%)
            roll = self.rng.randint(1, 6)
            return roll >= 4

        elif regime == DirectiveTriggerRegime.MIDGAME:
            # Janela de pico dedutivo (R3, R4 e R5)
            return round_num in (3, 4, 5)

        elif regime == DirectiveTriggerRegime.CATCHUP:
            # Ativa apenas se a rodada anterior falhou (mecanismo compensatório)
            if round_num == 1:
                return False
            return last_round_success is False

        return False
