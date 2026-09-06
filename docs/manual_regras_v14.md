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

Resultados validados empiricamente sob a dinâmica de **Kit C**, **Opção 3 (Aperto de Liquidez no Tier 2)**, **Despertar do Sleeper na R2**, **Dividendo Completo de Banco** e **Catálogo Recalibrado**:

| Métrica | Valor | Avaliação & Impacto no Jogo |
|---|:---:|---|
| **Win Rate Global Banqueiros** | **52.38%** (15.714 vitórias) | 🎯 Equilíbrio competitivo padrão ouro (gap de apenas 4.76 p.p.) |
| **Win Rate Global Estagiários** | **47.62%** (14.286 vitórias) | 🎯 Ampla competitividade e chances equilibradas para ambos os lados |
| **Taxa de 4x0 (Sweep Banqueiros)** | **21.64%** (6.493 vitórias) | 🛡️ **Redução de ~10 p.p.** (caiu de 31.31% para 21.64%, rompendo passeios automáticos) |
| **Taxa de Clímax (Decisão na R7 — 3x4 / 4x3)** | **28.46%** (8.537 partidas) | 🔥 Altíssima tensão dramática: quase 30% das partidas vão até o último comitê! |
| **Vitórias Épicas de Banqueiros na R7 (4x3)** | **6.56%** (1.967 jogos) | 🚀 Resgate histórico: aprovação de 23.0% no Tier 7 (1.967 de 8.537) |
| **Placar Mais Frequente da Mesa** | **3 x 4 (21.90%)** | 🏆 O desfecho unitário mais comum é o clímax emocionante da 7ª rodada |
| **Duração Média das Partidas** | **5.60 ± 1.11 rodadas** | ✅ Partidas longas, altamente disputadas e com envolvimento de toda a mesa |
| **Massacre de Estagiários (0x4)** | **0.00%** (1 jogo em 30.000) | 💀 Virtualmente impossível de ocorrer na prática |

### 🎭 Performance por Perfil de IA
* **Perfil A — Agressivo / Blefe Imediato:** **55.11% Intern WR** (redução massiva em relação ao baseline de 72.84% e aos 60.87% anteriores, domesticado pelo Veto e Aperto do Tier 2).
* **Perfil B — Sleeper / Infiltração Profunda:** **46.32% Intern WR** (perfil estratégico altamente imprevisível e balanceado com o Despertar na R2).
* **Perfil C — Hedge / Retenção Econômica:** **41.43% Intern WR** (estratégia paciente que busca a explosão no mid/late game).

### 📈 Taxa de Aprovação por Tier
* **Tier 1:** 87.8% (26.333 de 30.000 tentativas)
* **Tier 2:** 62.4% (18.721 de 30.000 tentativas — queda intencional pela Opção 3, bloqueando o lock-out)
* **Tier 3:** 58.2% (17.468 de 30.000 tentativas — estabilização compensatória com meta 6)
* **Tier 4:** 50.9% (15.264 de 30.000 tentativas)
* **Tier 5:** 44.1% (10.355 de 23.506 tentativas)
* **Tier 6:** 29.1% (4.670 de 16.050 tentativas)
* **Tier 7:** 23.0% (1.967 de 8.537 tentativas — alta viabilidade no clímax final)
