# 📜 Manual de Regras & Game Design Oficial: BTG Madagascar (v14.0)

---

## 🏛️ 1. Visão Geral & Tema
**BTG Madagascar** é um jogo de dedução social estratégica, gestão de commodities e governança corporativa para **5 jogadores**.
* **3 Banqueiros de Investimento (Equipe Leal):** Buscam aprovar 4 contratos legítimos nos 7 Tiers de expansão econômica.
* **2 Estagiários Infiltrados (Equipe Dissidente):** Buscam sabotar e reprovar 4 contratos através de fraudes, retenção econômica ou quebra de insumos.

---

## 💼 2. A Economia Base de Recursos & Gestão de Carteira

### 🔹 Carteira Inicial Estruturada (Kit C)
Para eliminar a disparidade da sorte sem trivializar as cotas iniciais, todo operador inicia o jogo com uma carteira balanceada e sutilmente assimétrica:
* **1x Cobalto (+1)**
* **1x Titânio (+3)**
* **2x Cartas Secretas do Topo** (Deck Fechado)

> **Nota de Design (Kit C):** A Baunilha (+2) não é garantida de largada. Ela torna-se um ativo valioso de mercado, fazendo com que missões com cota de Baunilha exijam compras públicas no Balcão ou dependam de quem a comprou secretamente, gerando atrito e blefe autêntico desde o Tier 1.

### 🔹 O Mercado de Balcão Aberto
* No centro da mesa, há **3 cartas de Commodities sempre abertas** + o Deck Fechado.
* Ao comprar recursos, os operadores podem escolher entre o **Mercado Aberto** (compra visível para sinalizar cooperação) ou o **Topo Fechado** (compra anônima/secreta).

### 🔹 Dinâmica Econômica de Depleção & Dividendo Completo de Banco
* **Depleção por Participação:** Membros de comitês executados gastam suas cartas na operação e **não repõem recursos** na rodada seguinte.
* **Dividendo Completo de Banco (Bench Players):** Apenas os operadores que **ficarem de fora** do comitê aprovado recebem a bonificação da rodada, acumulando **duas vantagens econômicas vitais**:
  * **1. Rendimento de Capital (+1 Token de Rendimento / Juros):** Acumulado na carteira pessoal (+1 ponto de liquidez direta no cofre, teto de 3 tokens).
  * **2. Recomposição de Carteira (+1 Carta de Recurso):** Comprada do **Mercado Aberto** (sinalização pública de lealdade/cooperação) ou do **Topo Fechado** (estratégia anônima).
* **Impacto no Design:** Os jogadores que descansam no banco retornam nos comitês de 3 membros (Tiers 3, 4 e 5) com carteiras ricas (tokens de liquidez e recursos específicos de mercado), permitindo ao Banco absorver comitês mais caros e contrabalançar sabotagens no mid-game.

### 🔹 Plausibilidade Negável e o Triângulo de Culpa
* Ao final de cada operação, a mesa vê **quais cartas** foram jogadas no cofre, mas **não por quem**. Funciona como *The Resistance*: a revelação é coletiva, não individual.
* **Tiers 1–2 (assimetria inicial sutil):** Como todos iniciam com Cobalto e Titânio mas a Baunilha é incerta, alegar falta de Baunilha é plausível, enquanto a ausência de Cobalto ou Titânio nos primeiros turnos gera suspeita imediata.
* **Tiers 3–7 (mãos diferenciadas):** Conforme os jogadores no banco adquirem cartas distintas no mercado aberto ou fechado, a deniability material aumenta — é genuinamente possível não ter certos insumos, tornando as acusações mais ambíguas e ricas.

### 🔹 Sistema de Créditos de Sucesso
* Todo membro de um comitê **aprovado** recebe **+1 Crédito de Sucesso** ao final da operação.
* Ao acumular **2 Créditos**, o operador pode adquirir **1 Ativo Especial** do estoque:
  * **Banqueiro:** recebe **Ouro Líquido (+4 / Coringa)** — recurso premium para missões tardias.
  * **Estagiário:** recebe **Ativo Tóxico (−4)** — arma de sabotagem adquirida sob disfarce de lealdade.
* **Design Intent:** Incentiva os Estagiários a participarem "honestamente" de missões para acumular Tóxicos; cria uma narrativa de cobertura plausível (*"estou cumprindo missões para avançar na carreira"*). Banqueiros são recompensados com Wild cards pela coordenação leal.

---

## 🏛️ 3. Governança Corporativa
* **Chairman (Presidente da Rodada):** Propõe a composição do comitê e o fornecedor do insumo prometido.
* **Votação Aberta (maioria simples ≥ 3/5):** A mesa vota abertamente SIM ou NÃO ao comitê proposto.
* **Mecanismo de Veto:** Até **3 vetos consecutivos** antes de resolução forçada.
* **Resolução Forçada:** Após 3 vetos, o Chairman atual monta o comitê de menor suspeita agregada e este é executado sem nova votação.
* O cargo de Chairman passa para o próximo jogador (sentido horário) ao início de cada nova rodada.

---

## 📜 4. Catálogo Oficial dos 7 Tiers & Cotas Coletivas

| Tier | Nome da Operação | Comitê | Custo / Membro | Meta de Liquidez | Cota Coletiva de Insumos | Justificativa de Design |
| :---: | :--- | :---: | :---: | :---: | :--- | :--- |
| **1** | **Arbitragem Simples** | 2 ops | 1 carta | **$\ge 3$ pts** | *Nenhum* | Abertura justa: permite testar cooperação inicial sem risco desmedido. |
| **1** | **Exportação de Baunilha** | 2 ops | 1 carta | **$\ge 4$ pts** | $\ge 1\text{x}$ **Baunilha (+2)** | Teste de mercado: como VN não é garantida no Kit C, exige compra ou sorte de topo. |
| **2** | **Mineração de Cobalto** | 2 ops | 1 carta | **$\ge 5$ pts** ⚡ | $\ge 1\text{x}$ **Cobalto (+1)** | **Aperto de Liquidez (Opção 3):** Exige 5 pts. Dois operadores depletados na R1 não passam no piloto automático com 1+3=4; demanda token de rendimento ou banco fresco. |
| **2** | **Lote Agrícola** | 2 ops | 1 carta | **$\ge 5$ pts** | $\ge 1\text{x}$ **Baunilha (+2)** | Baunilha (+2) + Titânio (+3) = 5 pts. Exige compromisso de compra nobre ou token de rendimento. |
| **3** | **Sindicato de Titânio** | 3 ops | 1 carta | **$\ge 6$ pts** ⚖️ | **$\ge 2\text{x}$ Titânio (+3)** ⚡ | Primeiro comitê de 3. Meta compensatória: 2x TI (+6) cumprem o alvo, estabilizando a mesa. |
| **3** | **Logística Portuária** | 3 ops | 1 carta | **$\ge 6$ pts** ⚖️ | **$\ge 2\text{x}$ Cobalto (+1)** ⚡ | Escoamento acessível: 2x CO (+2) + 1x TI (+3) + 1 token = 6 pts. Valoriza o Cobalto do banco. |
| **4** | **Refino Metalúrgico** | 3 ops | 1 carta | **$\ge 7$ pts** ⚖️ | **$\ge 2\text{x}$ Titânio (+3)** ⚡ | Filtro equilibrado: 2x TI (+6) + 1x CO (+1) = 7 pts. Viável para comitê misturado com bench. |
| **4** | **Consórcio Agro-Industrial**| 3 ops | 1 carta | **$\ge 8$ pts** | **$\ge 2\text{x}$ Baunilha (+2)** ⚡ | Demanda de mercado: 2x VN (+4) + 1x TI (+3) + 1 token = 8 pts. |
| **5** | **Megaconsórcio Industrial** | **3→4 ops** 🔥 | 1 carta | **$\ge 10$ pts** | **$\ge 2\text{x}$ Titânio (+3)** ⚡ | Expande para 4 ops se T3 ou T4 falhou. Com 4 membros a meta facilita, mas infiltra traidor. |
| **5** | **Cofre de Commodities** | **3→4 ops** 🔥 | 1 carta | **$\ge 10$ pts** | **$\ge 2\text{x}$ Baunilha (+2)** ⚡ | Expande para 4 ops se T3 ou T4 falhou. Absorve Ativos Tóxicos via tokens de banco. |
| **6** | **Complexo Greenfield** | 3 ops | **2 cartas** | **$\ge 13$ pts** | **$\ge 2\text{x}$ Titânio (+3)** ⚡ | Entrada na fase pesada (6 cartas totais). Premia quem descansou no banco e estocou cartas. |
| **6** | **Consórcio Safira** | 3 ops | **2 cartas** | **$\ge 14$ pts** | **$\ge 2\text{x}$ Safira (+4)** ⚡ | Requer 2x Safiras (+8 pts) + 4 cartas médias = 14 pts. Recompensa compras nobres. |
| **7** | **Holding Global BTG (Clímax)**| 3 ops | **2 cartas** | **$\ge 15$ pts** | **$\ge 1\text{x}$ Safira (+4)** 🔥 | Opção Alpha: 6 cartas exigindo 1 Safira e queima de tokens de rendimento. |
| **7** | **Fundo Soberano Madagascar**| 3 ops | **2 cartas** | **$\ge 16$ pts** | **$\ge 2\text{x}$ Titânio (+3)** 🔥 | Opção Beta: 6 cartas exigindo 2 Titânios. Viabiliza o clímax via economia de metal base. |

---

## 🏛️ 5. Governança Corporativa & Dedução de Cofre

### 5.1 Veto a Presidente sob Suspeita
* **Princípio da Prudência:** Jogadores leais rejeitam comitês propostos por qualquer Chairman sob suspeita ativa ($\ge 0.50$) ou envolvido em um Par de Conflito não resolvido.
* **Rotação Natural:** O veto transfere a presidência no sentido horário, assegurando que comitês em rodadas críticas (especialmente a R3) sejam formados por banqueiros idôneos.

### 5.2 Aritmética do Cofre & Mentira de Liquidez (Comitês de 2 membros)
Todas as cartas e tokens entram no cofre virados para baixo. No momento da revelação coletiva:
* **Caso A (Quebra de Insumo):** Faltou a commodity exigida $\rightarrow$ O fornecedor designado assume **0.80 de suspeita**; o parceiro fica em **0.48**.
* **Caso B (Quebra de Liquidez):** A commodity foi entregue, mas a pontuação total falhou $\rightarrow$ O fornecedor que cumpriu a promessa cai para **0.35 de suspeita** (parceiro honesto em processo de vindicação); o parceiro que mentiu a liquidez sobe para **0.82 de suspeita**.
* **Caso C (Arbitragem Pura):** Contrato sem commodity exigida $\rightarrow$ Ambos dividem suspeita simétrica de **0.52** (par de conflito estilo *The Resistance*).
* **Vindicação Definitiva (R3 / 1-Difference):** Se a dupla aprovada da R2 recebe um suspeito na R3 e a missão falha, o suspeito é isolado como 1.00 traidor e o banqueiro inocente que ficou no banco recebe alívio imediato de **-0.20 de suspeita**.

### 5.3 O Despertar do Sleeper na R2 (Reação ao 1x0 do Banco)
* **Ativação Orgânica:** Se o Banco aprova o Tier 1 abrindo **1 x 0**, o estagiário Sleeper incluído na proposta da R2 não permanece inerte: possui **50% de probabilidade** de despertar e sabotar imediatamente a operação.
* **Ruptura de Sweeps:** Essa mecânica reduz os passeios automáticos de 4x0 (onde os banqueiros controlavam a mesa do início ao fim sem atrito), diminuindo os sweeps de **31.31%** para a faixa controlada de **~22%**, sem tornar as jogadas iniciais previsíveis.

---

## ⚖️ 6. Estatísticas de Balanceamento (Monte Carlo — 30.000 partidas oficiais)

Resultados validados empiricamente sob a dinâmica consolidada da **v14.0** com **Kit C**, **Opção 3 (Aperto de Liquidez no Tier 2)**, **Despertar do Sleeper na R2**, **Dividendo Completo de Banco**, **Mesas Heterogêneas (5 Perfis)** e **Catálogo Recalibrado**:

| Métrica Global | Valor (Jogo Base v14.0) | Valor com DLC Ativa (Regime 1d6) | Avaliação & Impacto no Jogo |
|---|:---:|:---:|---|
| **Win Rate Global Banqueiros** | **46.20%** | **48.97%** | 🎯 Equilíbrio competitivo padrão ouro (gap de apenas 1.03 p.p.) |
| **Win Rate Global Estagiários** | **53.80%** | **51.03%** | 🎯 Ampla competitividade e chances perfeitamente simétricas |
| **Taxa de 4x0 (Sweep Banqueiros)** | **14.23%** | **14.57%** | 🛡️ Passeios automáticos eliminados em relação às versões iniciais (eram >31%) |
| **Taxa de Clímax (Decisão na R7 — 3x4 / 4x3)** | **29.79%** | **30.72%** | 🔥 Altíssima tensão dramática: ~31% das partidas vão até o último comitê! |
| **Placar Mais Frequente da Mesa** | **3 x 4 (27.66%)** | **3 x 4 (24.90%)** | 🏆 O desfecho unitário mais comum é o clímax emocionante da 7ª rodada |
| **Duração Média das Partidas** | **5.75 ± 1.08 rodadas** | **5.75 ± 1.05 rodadas** | ✅ Partidas longas, altamente disputadas e com envolvimento de toda a mesa |
| **Massacre de Estagiários (0x4)** | **1.17%** | **0.56%** | 💀 Virtualmente impossível de ocorrer na prática |

### 🎭 Performance por Perfil de IA (5 Perfis de Estagiário vs 4 de Banqueiro)
* **Perfil A — Agressivo / Blefe Imediato:** **53.61% Intern WR** (blefe agressivo inicial controlado pelo Veto e Aperto do Tier 2).
* **Perfil B — Sleeper / Infiltração Profunda:** **50.59% Intern WR** (perfil altamente imprevisível equilibrado pelo Despertar na R2).
* **Perfil C — Hedge / Retenção Econômica:** **42.45% Intern WR** (estratégia paciente de asfixia econômica de insumos).
* **Perfil D — Oportunista / Camaleão Adaptativo:** **46.61% Intern WR** (reage dinamicamente ao placar da mesa em tempo real).
* **Perfil E — Técnico / Falsa Idoneidade:** **48.69% Intern WR** (equilibra a entrega de commodities com sabotagens cirúrgicas de valor).

### 📈 Funil de Aprovação por Tier (Taxas de Sucesso Empíricas)
* **Tier 1 (Abertura Neutra):** 88.0% de sucesso (apenas 47% de infiltração permitida pela mesa).
* **Tier 2 (Aperto de Liquidez - Opção 3):** 69.5% de sucesso (exige 5 pts, bloqueando lock-outs automáticos).
* **Tier 3 (Primeiro Comitê de 3 Membros):** 48.2% de sucesso (estabilização compensatória via meta 6).
* **Tier 4 (Filtro Crítico de Alavancagem):** 41.2% de sucesso (comitê exige 2x insumos nobres).
* **Tier 5 (Megaconsórcio / Expansão Condicional):** 47.9% de sucesso (comitê expande para 4 membros sob falha prévia).
* **Tier 6 (Complexos Pesados - 2 Cartas/Membro):** 38.9% de sucesso (6 cartas totais, premia estoque do banco).
* **Tier 7 (Clímax - Holding Global):** 19.8% de sucesso (confronto decisivo no desempate de 3x3).

---

## 🏛️ 7. Módulo Oficial de Expansão (DLC: Diretrizes Regulatórias & Poderes Corporativos)

A expansão de Diretrizes Regulatórias é um módulo opcional que introduz um baralho de **17 cartas de eventos físicos analógicos**, trazendo variabilidade dinâmica sem quebrar a espinha dorsal matemática do jogo base.

### 7.1 Regra do Gatilho do Dado 1d6 (Regime Recomendado)
Ao início de cada rodada (antes da escolha do Chairman e das declarações):
* O Chairman rola **1 dado de 6 faces (1d6)**:
  * **Resultado 1, 2 ou 3:** *Rodada Ordinária.* Nenhuma diretriz é ativada. A mesa joga sob as regras clássicas de dedução e governança.
  * **Resultado 4, 5 ou 6:** *Diretriz Extraordinária Ativa!* O Chairman saca a carta do topo do Baralho de Diretrizes, lê em voz alta e aplica seu efeito.
* **Impacto no Design:** Mantém média de **2.87 cartas por partida** (~3 eventos ao longo do jogo), criando suspense genuíno na rolagem inicial sem saturar a memória de trabalho dos jogadores.

### 7.2 Catálogo Oficial das 17 Diretrizes Físicas de Mesa

Todas as cartas são **100% universais** (podem ser jogadas em qualquer rodada) e operam com **componentes tangíveis** (cartas da mão, tokens de rendimento e gavetas de votação):

| ID / Nome | Categoria | Mecânica Física de Mesa | Racional de Game Design |
| :--- | :--- | :--- | :--- |
| **`AUDITORIA_CVM`**<br>*(Due Diligence)* | Compliance | O Chairman inspeciona 1 carta física colocada no cofre após a resolução. | Dedução pontual de certeza física para o auditor leal. |
| **`QUARENTENA_REGULATORIA`**<br>*(Suspensão Provisória)* | Compliance | O operador sob maior suspeita da mesa não pode ser escalado no comitê desta rodada. | Isolamento cautelar regimental de membros sob escrutínio. |
| **`SEGURO_CONTRA_SINISTRO`**<br>*(Hedge Corporativo)* | Compliance | Se houver Ativo Tóxico no cofre revelado, a apólice anula e descarta o tóxico, avaliando apenas recursos válidos. | Cria o momento empolgante onde o sabotador é revelado, mas o contrato é salvo pela apólice. |
| **`INSPECAO_DE_CARTEIRA`**<br>*(Auditoria de Balcão)* | Compliance | O Chairman aponta 1 operador, que deve escolher e revelar abertamente 1 carta física da mão para a mesa. | Permite a um jogador provar publicamente idoneidade com um insumo nobre. |
| **`CONTABILIDADE_SEGREGADA`**<br>*(Auditoria Segmentada)* | Compliance | As cartas do comitê são postas em pilhas separadas por membro; o Chairman inspeciona a pilha de 1 membro antes de misturar ao cofre. | Neutraliza o escudo de anonimato em comitês expandidos de 4 membros (Tier 5). |
| **`SUBSIDIO_GOVERNAMENTAL`**<br>*(Incentivo Fiscal)* | Economia | Reduz a meta de liquidez do contrato em -2 pontos (mínimo de 3 pts). | Alívio fiscal em rodadas de arrocho econômico. |
| **`CRISE_DE_OFERTA`**<br>*(Choque Logístico)* | Economia | Aumenta a meta de liquidez do contrato em +2 pontos. | Choque de custo inflacionário que testa a reserva de tokens. |
| **`SWAP_DE_COMMODITY`**<br>*(Arbitragem Pura)* | Economia | Cancela a cota de insumo obrigatório do contrato, avaliando apenas o valor numérico bruto. | Desbloqueia contratos quando há escassez de commodities no mercado. |
| **`LEILAO_DE_BALCAO`**<br>*(Pregão Extraordinário)* | Economia | Todos os 5 operadores compram 1 carta adicional do topo do baralho fechado. | Injeção geral de liquidez nas mãos de todos os jogadores. |
| **`REESTRUTURACAO_OFFSHORE`**<br>*(Swap de Portfólio)* | Economia | Antes da proposta, cada operador pode descartar até 2 cartas da mão e comprar 2 novas do topo. | Elimina o gargalo da "mão travada" do banqueiro sem exigir descanso no banco. |
| **`CHAMADA_DE_MARGEM`**<br>*(Aporte Emergencial)* | Economia | Se falhar exclusivamente por falta de insumo, a mesa pode queimar 2 Tokens de Rendimento coletivos para suprir a cota. | Impede que o blefe da omissão de commodity cause derrotas irreversíveis. |
| **`LINHA_DE_CREDITO_SINDICAL`**<br>*(Injeção Universal)* | Economia | Todos os 5 operadores recebem imediatamente +1 Token de Rendimento da reserva. | Reabastece o combustível econômico da mesa para contratos de alta demanda. |
| **`GOLDEN_SHARE`**<br>*(Voto de Minerva)* | Governança | O voto do Chairman tem peso duplo (2 votos) na votação do comitê. | Prerrogativa presidencial de desempate estatutário. |
| **`PEDIDO_DE_VISTA`**<br>*(Veto de Bancada)* | Governança | Qualquer operador pode descartar 1 Token pessoal para cancelar a proposta sem queimar veto da mesa. | Evita o pânico do 3º veto e a queda no comitê forçado aleatório. |
| **`PACTO_DE_ACIONISTAS`**<br>*(Aliança de Confiança)* | Governança | O Chairman e mais 1 operador mostram secretamente 1 carta da mão um ao outro e a devolvem. | Quebra a paranoia fratricida entre banqueiros honestos (evita a Regra #6). |
| **`SUPERMAIORIA_EXIGIDA`**<br>*(Cláusula Pétrea)* | Governança | O comitê exige 4 votos favoráveis (em vez de 3) para ser aprovado. | Exige consenso de 80% do conselho para operações de alto risco. |
| **`DECRETO_PRESIDENCIAL`**<br>*(Gabinete de Crise)* | Governança | O Chairman aprova o comitê com apenas 2 votos favoráveis, superando vetos da oposição. | Permite aprovar comitês de confiança mesmo contra a sabotagem de dissidentes. |
| **`COMITE_EXPANDIDO`**<br>*(Auditor Adjunto)* | Operações | Aumenta o tamanho do comitê em +1 membro (máximo de 4). | Adiciona mais mãos para cumprir metas pesadas de pontuação. |
| **`FORCA_TAREFA_ENXUTA`**<br>*(Operação Sigilosa)* | Operações | Reduz o tamanho do comitê em -1 membro (mínimo de 2). | Restringe o acesso à chave do cofre, reduzindo a chance de infiltração. |

---

## 📜 8. Histórico de Versões, Experimentos & Evolução do Game Design (v1.0 à v14.0)

A trajetória de desenvolvimento do **BTG Madagascar** baseou-se em ciclos iterativos de modelagem matemática, experimentos controlados e simulações estocásticas de larga escala:

### 🔹 Fase 1: v1.0 – v5.0 (A Gênese & Síndrome de The Resistance)
* **Estrutura Original:** Regras inspiradas diretamente em jogos de dedução clássicos (*The Resistance / Avalon*), com cartas abstratas de Sucesso/Falha e contagem estática de pontos.
* **Diagnóstico de Falha:**
  * **Win Rate de Estagiários > 72%:** Os traidores venciam com facilidade explorando a fragilidade dedutiva da mesa.
  * **Falta de Plausibilidade Negável Material:** Sem commodities ou economia, qualquer falha no cofre permitia isolar culpados de forma trivial ou meramente barulhenta.
  * **Efeito Bola de Neve (Snowball):** O Banco entrava em paralisia após o primeiro revés, sem mecanismos econômicos de recuperação.

### 🔹 Fase 2: v6.0 – v9.0 (A Economia de Commodities & O Mercado de Balcão)
* **Inovações Introduzidas:**
  * Criação das 4 commodities temáticas: Cobalto (+1), Baunilha (+2), Titânio (+3), Safira (+4) e Coringa (+4).
  * Criação do **Mercado de Balcão Aberto (3 cartas visíveis)**: Introduziu a decisão estratégica entre compras públicas (sinalização transparente de honestidade) e compras fechadas (anonimato tático). O teste de estresse provou que o balcão confere um **Prêmio de Liquidez de +4.55 p.p.** ao Banco.
  * **Créditos de Sucesso:** Criação de incentivos positivos para o Estagiário participar de missões honestas visando acumular Ativos Tóxicos (-4).

### 🔹 Fase 3: v10.0 – v12.0 (Depleção Econômica, Kit C e Dividendo de Banco)
* **Experimentos de Mão Inicial:**
  * *Kit A (Aleatório):* Dispersão de sorte inaceitável.
  * *Kit B (Simétrico Total):* Todos sabiam o que o outro tinha, eliminando o blefe inicial.
  * *Kit C (Estruturado Asimétrico):* **1 Cobalto, 1 Titânio, 2 cartas do topo.** A Baunilha não garantida gerou o atrito de abertura perfeito.
* **Dividendo Completo de Banco (Bench Dividends):**
  * Operadores fora do comitê passaram a receber **+1 carta e +1 Token de Rendimento** (+1 ponto direto de liquidez). Isso transformou os jogadores do banco no motor de sustentação econômica dos Tiers tardios.
* **O Despertar do Sleeper na R2:**
  * Ao detectar liderança de 1x0 do Banco, o estagiário Sleeper na R2 ganhou 50% de chance de ativação. Reduziu os sweeps automáticos de 4x0 de **31.31% para ~21%**.

### 🔹 Fase 4: v13.0 (Calibração Atuarial dos 7 Tiers de Operação)
* **Aperto de Liquidez no Tier 2 (Opção 3):** Elevação da meta para 5 pts, impedindo que dois jogadores esgotados da R1 passassem automaticamente com 1+3=4 sem queimar tokens ou usar o banco fresco.
* **Expansão Dinâmica da R5:** Comitês de 3 membros que expandem para 4 sob falha prévia nos Tiers 3 ou 4, equilibrando a dificuldade do meio de jogo.
* **Revolução do Clímax na R7:** Reestruturação das Holdings Globais (metas de 15 e 16 pts com cotas de metal e gemas), resgatando a taxa de vitórias épicas no Tier 7 de 0% para 23%.

### 🔹 Fase 5: v14.0 (Modelagem Avançada de IA & Dedução Estocástica)
* **Diversidade de Agentes:** Formalização dos 4 perfis de Banqueiro (`BALANCED`, `CONSERVATIVE`, `PRAGMATIC`, `STRATEGIST`) e 5 perfis de Estagiário (`A_AGGRESSIVE`, `B_SLEEPER`, `C_HEDGE`, `D_OPPORTUNIST`, `E_TECHNICIAN`).
* **Correção do Técnico (`E_TECHNICIAN`):** Calibração do arquétipo que antes ajudava involuntariamente o Banco, integrando blefes de insumo a partir da R3 e normalizando seu WR para 48–52%.
* **Suíte Analítica Multidimensional:** Integração dos 5 motores matemáticos avançados:
  * *Árvores Causais & SHAP* (descoberta da Regra #6 e do impacto de 6.3x do Tier 3).
  * *Cadeias de Markov Absorventes* (matriz exata de viradas e elasticidades sistêmicas).
  * *Teoria dos Jogos & Nash* (blefe ótimo de 19.4% no Tier 1 e dinâmicas de Minimax).
  * *Testes de Estresse Econômico* (análise de ruína sob seca de commodities e contágio tóxico).
  * *Teoria da Informação & Entropia de Shannon* (rastreamento do decaimento da incerteza de 2.585 para 1.77 bits).

### 🔹 Fase 6: v14.1 (A Expansão Analógica & Resolução de Gargalos via DLC)
* **Desenvolvimento do Baralho de 17 Diretrizes:** Substituição de mecânicas programáticas por componentes analógicos físicos (revelação aberta, gavetas separadas e queima de tokens).
* **Eliminação de Travas por Tier:** Garantia de que todas as 17 cartas sejam universais e jogáveis em qualquer rodada.
* **Resolução Cirúrgica de Brechas:**
  * `PACTO_DE_ACIONISTAS` dissolve a paranoia fratricida.
  * `REESTRUTURACAO_OFFSHORE` elimina a mão travada.
  * `CHAMADA_DE_MARGEM` e `LINHA_DE_CREDITO_SINDICAL` asseguram liquidez nos Tiers 6 e 7.
  * `CONTABILIDADE_SEGREGADA` neutraliza o anonimato do comitê de 4 membros.
* **Resultado:** Equilíbrio histórico validado em 30.000 partidas com **48.97% Banco vs 51.03% Estagiários** sob o regime de Dado 1d6.
