# -*- coding: utf-8 -*-
"""
BTG Madagascar - Gerador do Visualizador HTML de Partida (Dashboard v14.0)
"""

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.btg.tracer import generate_trace_dataset


def generate_dashboard(force_regenerate: bool = True):
    traces_file = os.path.join(os.path.dirname(__file__), 'data', 'game_traces.json')
    if force_regenerate or not os.path.exists(traces_file):
        generate_trace_dataset(traces_file)

    with open(traces_file, 'r', encoding='utf-8') as f:
        traces = json.load(f)

    traces_json_str = json.dumps(traces, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BTG Madagascar - Visualizador de Dedução & Tokens de Juros (v14.0)</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    body {{ font-family: 'Inter', sans-serif; }}
    .card-shadow {{ box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.25); }}
  </style>
</head>
<body class="bg-[#0b0f19] text-[#e2e8f0] min-h-screen p-4 md:p-8 antialiased">

  <div class="max-w-7xl mx-auto space-y-6">

    <!-- HEADER / TOP BAR -->
    <div class="bg-[#131b2e] border border-[#1e293b] rounded-2xl p-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 card-shadow">
      <div>
        <div class="flex items-center gap-3">
          <span class="bg-blue-600/20 text-blue-400 text-xs font-semibold px-2.5 py-1 rounded-full border border-blue-500/30 uppercase tracking-wider">Simulador Oficial v14.0</span>
          <span id="match-badge" class="bg-purple-600/20 text-purple-300 text-xs font-semibold px-2.5 py-1 rounded-full border border-purple-500/30">Tokens de Rendimento da Carteira</span>
        </div>
        <h1 class="text-2xl md:text-3xl font-bold mt-2 text-white">BTG Madagascar: Dashboard de Auditoria & Dedução</h1>
        <p class="text-sm text-[#94a3b8] mt-1">Navegue pelas rodadas, investigue a carteira e tokens de cada operador e analise a suspeita na perspectiva individual de cada Banqueiro.</p>
      </div>

      <!-- SELETOR DE PARTIDA / CENÁRIO -->
      <div class="flex flex-wrap items-center gap-3">
        <label class="text-xs text-[#94a3b8] font-medium">Cenário de Teste:</label>
        <select id="scenario-select" onchange="changeScenario(this.value)" class="bg-[#1e293b] border border-[#334155] text-white text-sm rounded-xl px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none">
          <option value="sleeper_game">🎭 Sleeper Estratégico (Infiltração Profunda)</option>
          <option value="aggressive_game">⚔️ Agressivo (Blefe Imediato & Sabotagem)</option>
          <option value="hedge_game">🛡️ Hedge Econômico (Retenção & Clímax na R7)</option>
        </select>
      </div>
    </div>

    <!-- PLACAR GLOBAL & LINHA DO TEMPO (STEPPER) -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      
      <!-- CARD DO PLACAR ATUAL -->
      <div class="lg:col-span-4 bg-[#131b2e] border border-[#1e293b] rounded-2xl p-5 card-shadow flex flex-col justify-between">
        <div class="flex justify-between items-center pb-3 border-b border-[#1e293b]">
          <span class="text-xs font-semibold text-[#94a3b8] uppercase tracking-wider">Placar da Mesa</span>
          <span id="round-badge" class="text-xs bg-blue-500/20 text-blue-400 font-bold px-2.5 py-0.5 rounded-full border border-blue-500/30">Rodada 1 de 7</span>
        </div>

        <div class="grid grid-cols-2 gap-4 my-4 text-center">
          <div class="bg-[#1e293b]/60 rounded-xl p-3 border border-[#334155]/40">
            <div class="text-xs text-blue-400 font-medium">🏛️ Banqueiros</div>
            <div id="banker-score" class="text-3xl font-extrabold text-blue-400 mt-1">0</div>
            <div class="text-[10px] text-[#94a3b8] mt-0.5">Meta: 4 Aprovados</div>
          </div>
          <div class="bg-[#1e293b]/60 rounded-xl p-3 border border-[#334155]/40">
            <div class="text-xs text-red-400 font-medium">🎭 Estagiários</div>
            <div id="intern-score" class="text-3xl font-extrabold text-red-400 mt-1">0</div>
            <div class="text-[10px] text-[#94a3b8] mt-0.5">Meta: 4 Reprovados</div>
          </div>
        </div>

        <div id="game-status-banner" class="text-xs text-center py-2 px-3 rounded-lg font-medium bg-slate-800 text-slate-300">
          Partida em Andamento
        </div>
      </div>

      <!-- LINHA DO TEMPO INTERATIVA (STEPPER DE 7 RODADAS) -->
      <div class="lg:col-span-8 bg-[#131b2e] border border-[#1e293b] rounded-2xl p-5 card-shadow flex flex-col justify-between">
        <div>
          <div class="flex justify-between items-center pb-3 border-b border-[#1e293b]">
            <span class="text-xs font-semibold text-[#94a3b8] uppercase tracking-wider">Linha do Tempo dos Contratos (1 a 7)</span>
            <span class="text-xs text-[#64748b]">Clique em qualquer rodada para inspecionar</span>
          </div>

          <!-- BOTÕES DO STEPPER -->
          <div id="timeline-stepper" class="grid grid-cols-7 gap-2 my-4">
            <!-- Gerado via JS -->
          </div>
        </div>

        <!-- CONTROLES DE REPRODUÇÃO -->
        <div class="flex justify-between items-center pt-2 border-t border-[#1e293b]">
          <button onclick="prevRound()" class="px-4 py-1.5 bg-[#1e293b] hover:bg-[#334155] text-xs font-semibold rounded-lg transition-all text-slate-200">
            ◀ Rodada Anterior
          </button>
          <span id="step-indicator" class="text-xs text-slate-400 font-medium">Visualizando Rodada 1 de 6</span>
          <button onclick="nextRound()" class="px-4 py-1.5 bg-[#1e293b] hover:bg-[#334155] text-xs font-semibold rounded-lg transition-all text-slate-200">
            Próxima Rodada ▶
          </button>
        </div>
      </div>

    </div>

    <!-- PAINEL CENTRAL DA RODADA ATIVA -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

      <!-- COLUNA DA ESQUERDA: DETALHES DO CONTRATO & AUDITORIA DE CARTAS -->
      <div class="lg:col-span-8 space-y-6">

        <!-- CARD DO CONTRATO & RESULTADO DA AUDITORIA -->
        <div class="bg-[#131b2e] border border-[#1e293b] rounded-2xl p-6 card-shadow space-y-4">
          <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-3">
            <div>
              <div class="flex items-center gap-2">
                <span id="tier-badge" class="bg-blue-500/20 text-blue-400 text-xs font-bold px-2 py-0.5 rounded">Tier 1</span>
                <h2 id="contract-name" class="text-xl font-bold text-white">Arbitragem Simples</h2>
              </div>
              <p id="contract-desc" class="text-xs text-[#94a3b8] mt-1">Comitê de 2 membros • Meta: 3 pontos</p>
            </div>
            
            <div id="outcome-pill" class="px-4 py-1.5 rounded-full font-bold text-sm uppercase tracking-wide flex items-center gap-1.5 bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              <span>APROVADO</span>
            </div>
          </div>

          <!-- MÉTRICAS DO RESULTADO -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3 pt-2">
            <div class="bg-[#1e293b]/50 p-3 rounded-xl border border-[#334155]/30">
              <div class="text-[10px] text-[#94a3b8] uppercase font-semibold">Pontos Atingidos</div>
              <div id="total-score-val" class="text-lg font-extrabold text-white mt-0.5">5 / 3</div>
            </div>
            <div class="bg-[#1e293b]/50 p-3 rounded-xl border border-[#334155]/30">
              <div class="text-[10px] text-[#94a3b8] uppercase font-semibold">Cota de Insumo</div>
              <div id="req-commodity-val" class="text-lg font-extrabold text-white mt-0.5">Não exigido</div>
            </div>
            <div class="bg-[#1e293b]/50 p-3 rounded-xl border border-[#334155]/30">
              <div class="text-[10px] text-[#94a3b8] uppercase font-semibold">Tokens Usados</div>
              <div id="tokens-used-val" class="text-lg font-extrabold text-purple-300 mt-0.5">0 🪙</div>
            </div>
            <div class="bg-[#1e293b]/50 p-3 rounded-xl border border-[#334155]/30">
              <div class="text-[10px] text-[#94a3b8] uppercase font-semibold">Chairman Líder</div>
              <div id="chair-val" class="text-lg font-extrabold text-blue-400 mt-0.5">Jogador 0</div>
            </div>
          </div>

          <!-- AUDITORIA DE CARTAS E TOKENS DEPOSITADOS NO COFRE -->
          <div class="pt-3 border-t border-[#1e293b]">
            <div class="flex justify-between items-center mb-3">
              <span class="text-xs font-semibold text-[#94a3b8] uppercase tracking-wider">Cofre de Resolução (Cartas Jogadas em Segredo)</span>
              <span class="text-[11px] text-amber-400/90 font-medium bg-amber-950/40 px-2 py-0.5 rounded border border-amber-800/40">Revelação de Auditoria</span>
            </div>

            <div id="submitted-cards-grid" class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <!-- Gerado via JS -->
            </div>
          </div>
        </div>

        <!-- MÃOS DOS JOGADORES & CARTEIRA DE TOKENS -->
        <div class="bg-[#131b2e] border border-[#1e293b] rounded-2xl p-6 card-shadow">
          <div class="flex justify-between items-center pb-3 border-b border-[#1e293b] mb-4">
            <span class="text-xs font-semibold text-[#94a3b8] uppercase tracking-wider">Carteira & Tokens de Todos os Operadores</span>
            <span class="text-[11px] text-slate-400">Tokens acumulam quando o jogador fica no banco</span>
          </div>

          <div id="players-hands-grid" class="grid grid-cols-1 md:grid-cols-5 gap-3">
            <!-- Gerado via JS -->
          </div>
        </div>

      </div>

      <!-- COLUNA DA DIREITA: RADAR DE DEDUÇÃO E PERSPECTIVA INDIVIDUAL -->
      <div class="lg:col-span-4 space-y-6">

        <!-- CARD DO RADAR DE SUSPEITA -->
        <div class="bg-[#131b2e] border border-[#1e293b] rounded-2xl p-6 card-shadow space-y-4">
          <div class="flex justify-between items-center pb-3 border-b border-[#1e293b]">
            <div>
              <span class="text-xs font-semibold text-[#94a3b8] uppercase tracking-wider">Radar de Suspeita Individual</span>
              <p class="text-[10px] text-slate-400">Selecione o Banqueiro para ver como ELE enxerga a mesa</p>
            </div>
          </div>

          <!-- SELETOR DE PERSPECTIVA DO BANQUEIRO -->
          <div class="space-y-1.5">
            <label class="text-xs text-slate-300 font-medium">Perspectiva do Ponto de Vista:</label>
            <select id="banker-perspective-select" onchange="changePerspective(this.value)" class="w-full bg-[#1e293b] border border-[#334155] text-white text-xs rounded-xl px-3 py-2 outline-none focus:ring-2 focus:ring-blue-500">
              <!-- Gerado via JS -->
            </select>
          </div>

          <!-- GRÁFICO DE BARRAS DE SUSPEITA -->
          <div id="suspicion-bars-container" class="space-y-3 pt-2">
            <!-- Gerado via JS -->
          </div>

          <div class="text-[11px] text-slate-400 bg-[#1e293b]/60 p-3 rounded-xl border border-[#334155]/30 leading-relaxed">
            💡 <strong>Regra de Decisão Bayesiana:</strong> Banqueiros usam o histórico dos comitês para deduzir traidores. Se uma missão de 2 falha, o parceiro sobe para 100%. Comitês de sucesso reduzem a desconfiança.
          </div>
        </div>

        <!-- PAINEL DE ROLES DOS JOGADORES NA PARTIDA -->
        <div class="bg-[#131b2e] border border-[#1e293b] rounded-2xl p-6 card-shadow space-y-3">
          <span class="text-xs font-semibold text-[#94a3b8] uppercase tracking-wider">Gabarito da Partida</span>
          <div id="roster-list" class="space-y-2 text-xs">
            <!-- Gerado via JS -->
          </div>
        </div>

      </div>

    </div>

  </div>

  <!-- SCRIPT DE INTERATIVIDADE -->
  <script>
    const tracesData = {traces_json_str};
    let currentScenarioKey = 'sleeper_game';
    let currentRoundIndex = 0;
    let currentPerspective = 'avg';

    const playerColors = [
      {{ bg: '#1e3a8a', border: '#3b82f6', line: '#60a5fa' }},
      {{ bg: '#14532d', border: '#22c55e', line: '#4ade80' }},
      {{ bg: '#701a75', border: '#d946ef', line: '#f472b6' }},
      {{ bg: '#7c2d12', border: '#f97316', line: '#fb923c' }},
      {{ bg: '#312e81', border: '#6366f1', line: '#818cf8' }}
    ];

    function changeScenario(key) {{
      currentScenarioKey = key;
      currentRoundIndex = 0;
      currentPerspective = 'avg';
      populateBankerPerspectiveSelect();
      updateView();
    }}

    function changePerspective(val) {{
      currentPerspective = val;
      renderSuspicionBars();
    }}

    function setRound(idx) {{
      currentRoundIndex = idx;
      updateView();
    }}

    function prevRound() {{
      if (currentRoundIndex > 0) {{
        currentRoundIndex--;
        updateView();
      }}
    }}

    function nextRound() {{
      const match = tracesData[currentScenarioKey];
      if (currentRoundIndex < match.rounds.length - 1) {{
        currentRoundIndex++;
        updateView();
      }}
    }}

    function populateBankerPerspectiveSelect() {{
      const match = tracesData[currentScenarioKey];
      const select = document.getElementById('banker-perspective-select');
      select.innerHTML = '<option value="avg">📊 Média do Conselho de Banqueiros</option>';

      match.players.forEach(p => {{
        if (match.banker_ids.includes(p.id)) {{
          select.innerHTML += `<option value="${{p.id}}">👁️ Ponto de Vista do Jogador ${{p.id}} (Banqueiro)</option>`;
        }}
      }});
      select.value = currentPerspective;
    }}

    function updateView() {{
      const match = tracesData[currentScenarioKey];
      const round = match.rounds[currentRoundIndex];
      const totalRounds = match.rounds.length;

      // 1. Placar Global & Status
      document.getElementById('banker-score').innerText = round.banker_score;
      document.getElementById('intern-score').innerText = round.intern_score;
      document.getElementById('round-badge').innerText = `Rodada ${{round.round_num}} de ${{totalRounds}}`;
      document.getElementById('step-indicator').innerText = `Visualizando Rodada ${{round.round_num}} de ${{totalRounds}}`;

      const statusBanner = document.getElementById('game-status-banner');
      if (currentRoundIndex === totalRounds - 1) {{
        const isBankerWin = match.final_winner.includes('Banqueiro');
        statusBanner.className = isBankerWin 
          ? 'text-xs text-center py-2 px-3 rounded-lg font-bold bg-blue-950 text-blue-300 border border-blue-800' 
          : 'text-xs text-center py-2 px-3 rounded-lg font-bold bg-red-950 text-red-300 border border-red-800';
        statusBanner.innerText = `Fim de Jogo: ${{match.final_winner}} Venceu (${{match.final_score}})`;
      }} else {{
        statusBanner.className = 'text-xs text-center py-2 px-3 rounded-lg font-medium bg-slate-800 text-slate-300';
        statusBanner.innerText = 'Partida em Andamento';
      }}

      // 2. Renderizar Stepper da Linha do Tempo
      const stepper = document.getElementById('timeline-stepper');
      stepper.innerHTML = '';
      match.rounds.forEach((r, idx) => {{
        const isActive = idx === currentRoundIndex;
        const isSuccess = r.is_success;
        const btnBg = isActive ? 'ring-2 ring-blue-400 bg-[#1e293b]' : 'bg-[#0f172a]/80 hover:bg-[#1e293b]';
        const badgeColor = isSuccess ? 'bg-emerald-500' : 'bg-red-500';

        stepper.innerHTML += `
          <button onclick="setRound(${{idx}})" class="${{btnBg}} border border-[#334155]/60 rounded-xl p-2.5 flex flex-col items-center justify-between transition-all">
            <span class="text-[10px] text-[#94a3b8] font-semibold uppercase">R${{r.round_num}}</span>
            <div class="w-2.5 h-2.5 rounded-full ${{badgeColor}} my-1"></div>
            <span class="text-[9px] text-slate-300 font-mono">${{r.contract.tier}}º Tier</span>
          </button>
        `;
      }});

      // 3. Contrato da Rodada Ativa
      document.getElementById('tier-badge').innerText = `Tier ${{round.contract.tier}}`;
      document.getElementById('contract-name').innerText = round.contract.name;
      document.getElementById('contract-desc').innerText = `Comitê de ${{round.contract.committee_size}} membros • Meta: ${{round.contract.target}} pontos • Custo: ${{round.contract.cost_per_player}} carta(s)/membro`;

      const outcomePill = document.getElementById('outcome-pill');
      if (round.is_success) {{
        outcomePill.className = 'px-4 py-1.5 rounded-full font-bold text-xs uppercase tracking-wide flex items-center gap-1.5 bg-emerald-500/20 text-emerald-400 border border-emerald-500/30';
        outcomePill.innerHTML = '✅ APROVADO';
      }} else {{
        outcomePill.className = 'px-4 py-1.5 rounded-full font-bold text-xs uppercase tracking-wide flex items-center gap-1.5 bg-red-500/20 text-red-400 border border-red-500/30';
        outcomePill.innerHTML = '❌ REPROVADO';
      }}

      document.getElementById('total-score-val').innerText = `${{round.total_value}} / ${{round.contract.target}}`;
      document.getElementById('req-commodity-val').innerText = round.contract.req_commodity ? `${{round.contract.req_commodity}} (x${{round.contract.req_count}})` : 'Não exigido';
      document.getElementById('tokens-used-val').innerText = `${{round.total_tokens_spent}} 🪙`;
      document.getElementById('chair-val').innerText = `Jogador ${{round.chair_id}}`;

      // 4. Cartas Depositadas no Cofre
      const submittedGrid = document.getElementById('submitted-cards-grid');
      submittedGrid.innerHTML = '';
      round.submitted.forEach(sub => {{
        const isBanker = match.banker_ids.includes(sub.player_id);
        const roleLabel = isBanker ? 'Banqueiro' : 'Estagiário';
        const roleBadge = isBanker ? 'bg-blue-900/60 text-blue-300' : 'bg-red-900/60 text-red-300';
        const isSupplier = sub.is_req_responsible ? '<span class="text-[9px] bg-amber-500/20 text-amber-300 px-1.5 py-0.5 rounded border border-amber-500/30">Fornecedor Prometido</span>' : '';

        let cardsHtml = '';
        sub.cards.forEach(c => {{
          const isToxic = c.type === 'TOXIC';
          const cardColor = isToxic ? 'bg-red-950 border-red-700 text-red-200' : 'bg-[#1e293b] border-[#334155] text-slate-200';
          cardsHtml += `
            <div class="${{cardColor}} border rounded-lg p-2 flex justify-between items-center text-xs">
              <span class="font-medium">${{c.name}}</span>
              <span class="font-bold ${{isToxic ? 'text-red-400' : 'text-emerald-400'}}">${{c.base > 0 ? '+' + c.base : c.base}} pts</span>
            </div>
          `;
        }});

        submittedGrid.innerHTML += `
          <div class="bg-[#1e293b]/40 border border-[#334155]/40 rounded-xl p-3 space-y-2">
            <div class="flex justify-between items-center">
              <div class="flex items-center gap-1.5">
                <span class="font-bold text-xs text-white">Jogador ${{sub.player_id}}</span>
                <span class="text-[9px] px-1.5 py-0.5 rounded font-medium ${{roleBadge}}">${{roleLabel}}</span>
                ${{isSupplier}}
              </div>
              <span class="text-xs text-purple-300 font-semibold font-mono">${{sub.tokens_spent > 0 ? '+' + sub.tokens_spent + ' 🪙' : '0 🪙'}}</span>
            </div>
            <div class="space-y-1.5">
              ${{cardsHtml}}
            </div>
          </div>
        `;
      }});

      // 5. Carteiras de Todos os Jogadores
      const handsGrid = document.getElementById('players-hands-grid');
      handsGrid.innerHTML = '';
      match.players.forEach(p => {{
        const isBanker = match.banker_ids.includes(p.id);
        const inComm = round.committee.includes(p.id);
        const pHand = round.hands_before[p.id];
        const cardBorder = inComm ? 'border-blue-500/60 bg-[#1e293b]' : 'border-[#334155]/30 bg-[#0f172a]/60';

        let cardsMiniHtml = '';
        pHand.cards.forEach(c => {{
          const isToxic = c.type === 'TOXIC';
          cardsMiniHtml += `
            <div class="text-[10px] py-0.5 px-1.5 rounded ${{isToxic ? 'bg-red-950 text-red-300' : 'bg-[#1e293b] text-slate-300'}} flex justify-between">
              <span class="truncate">${{c.name.split(' ')[0]}}</span>
              <span class="font-mono">${{c.base > 0 ? '+' + c.base : c.base}}</span>
            </div>
          `;
        }});

        handsGrid.innerHTML += `
          <div class="${{cardBorder}} border rounded-xl p-3 space-y-2">
            <div class="flex justify-between items-center">
              <span class="font-bold text-xs text-white">P${{p.id}}</span>
              <span class="text-[10px] text-purple-300 font-bold bg-purple-950/60 px-1.5 py-0.5 rounded border border-purple-800/40">${{pHand.tokens}} 🪙</span>
            </div>
            <div class="space-y-1">
              ${{cardsMiniHtml}}
            </div>
          </div>
        `;
      }});

      // 6. Roster Gabarito
      const rosterList = document.getElementById('roster-list');
      rosterList.innerHTML = '';
      match.players.forEach(p => {{
        const isBanker = match.banker_ids.includes(p.id);
        const badge = isBanker ? 'bg-blue-900/40 text-blue-300 border-blue-700/50' : 'bg-red-900/40 text-red-300 border-red-700/50';
        rosterList.innerHTML += `
          <div class="flex justify-between items-center py-1 border-b border-[#1e293b]">
            <span class="font-semibold text-white">Jogador ${{p.id}}</span>
            <span class="text-[10px] px-2 py-0.5 rounded border font-medium ${{badge}}">${{p.role}}</span>
          </div>
        `;
      }});

      // 7. Radar de Suspeita
      renderSuspicionBars();
    }}

    function renderSuspicionBars() {{
      const match = tracesData[currentScenarioKey];
      const round = match.rounds[currentRoundIndex];
      const container = document.getElementById('suspicion-bars-container');
      container.innerHTML = '';

      let susMap = {{}};
      if (currentPerspective === 'avg') {{
        susMap = round.suspicions.avg;
      }} else {{
        const bId = currentPerspective;
        susMap = round.suspicions.by_banker[bId] || {{}};
      }}

      match.players.forEach(p => {{
        const isBanker = match.banker_ids.includes(p.id);
        const susVal = susMap[p.id] !== undefined ? susMap[p.id] : 0.0;
        const color = playerColors[p.id % playerColors.length];

        let barColor = 'bg-blue-500';
        let tagStatus = '';

        if (currentPerspective !== 'avg' && parseInt(currentPerspective) === p.id) {{
          tagStatus = '<span class="text-[10px] text-blue-400 font-bold bg-blue-950/60 px-1.5 py-0.5 rounded border border-blue-800">EU MESMO</span>';
          barColor = 'bg-blue-600';
        }} else if (susVal >= 0.85) {{
          tagStatus = '<span class="text-[10px] text-red-400 font-bold bg-red-950/60 px-1.5 py-0.5 rounded border border-red-800">💥 TRAIDOR CONFIRMADO</span>';
          barColor = 'bg-red-500';
        }} else if (susVal >= 0.50) {{
          tagStatus = '<span class="text-[10px] text-amber-400 font-semibold bg-amber-950/60 px-1.5 py-0.5 rounded border border-amber-800">⚠️ SUSPEITO</span>';
          barColor = 'bg-amber-500';
        }} else if (susVal <= 0.20) {{
          tagStatus = '<span class="text-[10px] text-emerald-400 font-semibold bg-emerald-950/60 px-1.5 py-0.5 rounded border border-emerald-800">🛡️ CONFIÁVEL</span>';
          barColor = 'bg-emerald-500';
        }} else {{
          tagStatus = '<span class="text-[10px] text-slate-400 bg-slate-800 px-1.5 py-0.5 rounded">NEUTRO</span>';
          barColor = 'bg-blue-400';
        }}

        container.innerHTML += `
          <div class="space-y-1 text-xs">
            <div class="flex justify-between items-center">
              <div class="flex items-center gap-2">
                <span class="font-bold" style="color: ${{color.line}}">P${{p.id}}</span>
                <span class="text-[10px] text-slate-400">(${{isBanker ? 'Banqueiro' : 'Estagiário'}})</span>
                ${{tagStatus}}
              </div>
              <span class="font-mono font-bold text-white">${{(susVal * 100).toFixed(0)}}%</span>
            </div>
            <div class="w-full bg-[#1e293b] h-2 rounded-full overflow-hidden">
              <div class="${{barColor}} h-full transition-all duration-300 rounded-full" style="width: ${{Math.min(100, Math.max(0, susVal * 100))}}%"></div>
            </div>
          </div>
        `;
      }});
    }}

    populateBankerPerspectiveSelect();
    updateView();
  </script>
</body>
</html>"""

    local_html_path = os.path.join(os.path.dirname(__file__), 'match_visualizer.html')
    with open(local_html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    artifact_dir = r'C:\Users\najoa\.gemini\antigravity-ide\brain\d051bdd2-12ba-4bfe-83ce-6c5751d378ee'
    artifact_path = os.path.join(artifact_dir, 'match_visualizer.html')
    if os.path.exists(artifact_dir):
        with open(artifact_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    print(f"Dashboard v14.0 gerado com sucesso em: {local_html_path}")
    print(f"Artefato sincronizado em: {artifact_path}")


if __name__ == '__main__':
    generate_dashboard()
