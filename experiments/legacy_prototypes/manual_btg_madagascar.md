# 📜 Manual de Regras & Game Design Oficial: BTG Madagascar (v14.0)

---

## 🏛️ 1. Visão Geral & Tema
**BTG Madagascar** é um jogo de dedução social estratégica, gestão de commodities e governança corporativa para **5 jogadores**.
* **3 Banqueiros de Investimento (Equipe Leal):** Buscam aprovar 4 contratos legítimos nos 7 Tiers de expansão econômica.
* **2 Estagiários Infiltrados (Equipe Dissidente):** Buscam sabotar e reprovar 4 contratos através de fraudes, retenção econômica ou quebra de insumos.

---

## 💼 2. A Economia Base de Recursos & Gestão de Carteira

### 🔹 Carteira Inicial Estruturada (Kit Padrão)
Para eliminar a disparidade da sorte na largada, todo operador inicia o jogo com uma carteira balanceada:
* **1x Cobalto (+1)**
* **1x Baunilha (+2)**
* **1x Titânio (+3)**
* **1x Carta Secreta do Topo**

### 🔹 O Mercado de Balcão Aberto
* No centro da mesa, há **3 cartas de Commodities sempre abertas** + o Deck Fechado.
* Ao recompor a mão, os operadores podem escolher entre comprar do **Mercado Aberto** (compra visível para sinalizar cooperação) ou do **Topo Fechado** (compra anônima/secreta).

### 🔹 Recomposição de Mão Fixa (4 Cartas)
* No início de cada rodada, todos os jogadores compram cartas até voltarem a ter **exatamente 4 cartas na mão**.

### 🔹 Tokens Pessoais de Rendimento (+1🪙)
* Ficar no banco concede **+1 Token de Juros** na carteira pessoal (máximo de 3 tokens).
* Os Banqueiros acumulam esses tokens nas Rodadas 1 a 4 para **combater Ativos Tóxicos no Megaconsórcio da Rodada 5**.

---

## 📜 3. Catálogo Oficial dos 7 Tiers & Cotas Coletivas

| Tier | Nome da Operação | Comitê | Custo / Membro | Meta de Liquidez | Cota Coletiva de Insumos |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **1** | **Arbitragem Simples** | 2 ops | 1 carta | **$\ge 3$ pts** | *Nenhum* |
| **1** | **Exportação de Baunilha** | 2 ops | 1 carta | **$\ge 4$ pts** | $\ge 1\text{x}$ **Baunilha (+2)** |
| **2** | **Mineração de Cobalto** | 2 ops | 1 carta | **$\ge 4$ pts** | $\ge 1\text{x}$ **Cobalto (+1)** |
| **2** | **Lote Agrícola** | 2 ops | 1 carta | **$\ge 4$ pts** | $\ge 1\text{x}$ **Baunilha (+2)** |
| **3** | **Sindicato de Titânio** | 3 ops | 1 carta | **$\ge 8$ pts** | **$\ge 2\text{x}$ Titânio (+3)** ⚡ *(Triângulo de Culpa)* |
| **3** | **Logística Portuária** | 3 ops | 1 carta | **$\ge 7$ pts** | **$\ge 2\text{x}$ Cobalto (+1)** ⚡ |
| **4** | **Refino Metalúrgico** | 3 ops | 1 carta | **$\ge 10$ pts** | **$\ge 2\text{x}$ Titânio (+3)** ⚡ |
| **4** | **Consórcio Agro-Industrial**| 3 ops | 1 carta | **$\ge 10$ pts** | **$\ge 2\text{x}$ Baunilha (+2)** ⚡ |
| **5** | **Megaconsórcio Industrial** | **4 ops** 🔥 | 1 carta | **$\ge 14$ pts** | **$\ge 2\text{x}$ Titânio (+3)** ⚡ *(O Comitê de 4 na R5)* |
| **5** | **Cofre de Commodities** | **4 ops** 🔥 | 1 carta | **$\ge 14$ pts** | **$\ge 2\text{x}$ Baunilha (+2)** ⚡ |
| **6** | **Complexo Greenfield** | 3 ops | 2 cartas | **$\ge 16$ pts** | **$\ge 2\text{x}$ Titânio (+3)** ⚡ |
| **6** | **Consórcio Safira** | 3 ops | 2 cartas | **$\ge 17$ pts** | **$\ge 2\text{x}$ Safira (+4)** ⚡ |
| **7** | **Holding Global BTG (Climax)**| 3 ops | 2 cartas | **$\ge 20$ pts** | **$\ge 2\text{x}$ Safira (+4)** 🔥 |

*(Nota: Ouro Líquido Coringa conta como qualquer insumo exigido).*

---

## ⚖️ 4. Estatísticas Consolidadas da Simulação (Motor v14.0)

* **Equilíbrio Global Perfeito:** **50.38% Banqueiros vs 49.62% Estagiários** (Literal 50/50!).
* **Clímax na 7ª Rodada:** **43.25%** de todas as partidas são decididas no clímax final ($3\text{ x }4$ ou $4\text{ x }3$).
* **Win Rate do Sleeper:** **51.43%** (o perfil mais estratégico e vitorioso dos dissidentes).
* **Duração Média das Partidas:** **5.99 rodadas** (6 rodadas inteiras de dedução intensa).
