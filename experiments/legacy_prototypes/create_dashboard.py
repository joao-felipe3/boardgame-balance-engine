# -*- coding: utf-8 -*-
"""
Gerador do Dashboard HTML de Visualização de Partida v12.0 (Sistema de Tokens de Juros)
"""

import json
import os

with open('game_traces.json', 'r', encoding='utf-8') as f:
    traces = json.load(f)

html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BTG Madagascar - Visualizador de Dedução & Tokens de Juros</title>
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
          <span class="bg-blue-600/20 text-blue-400 text-xs font-semibold px-2.5 py-1 rounded-full border border-blue-500/30 uppercase tracking-wider">Simulador Oficial v12.0</span>
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

        <div class="grid grid-cols-2 gap-4 my-4">
          <div class="bg-blue-950/40 border border-blue-800/40 rounded-xl p-4 text-center">
            <div class="text-xs text-blue-300 font-medium">🏛️ Banqueiros</div>
            <div id="score-banker" class="text-3xl font-extrabold text-blue-400 mt-1">0</div>
            <div class="text-[10px] text-blue-400/70 mt-1">Meta: 4 Vitórias</div>
          </div>
          <div class="bg-red-950/40 border border-red-800/40 rounded-xl p-4 text-center">
            <div class="text-xs text-red-300 font-medium">🎭 Estagiários</div>
            <div id="score-intern" class="text-3xl font-extrabold text-red-400 mt-1">0</div>
            <div class="text-[10px] text-red-400/70 mt-1">Meta: 4 Fraudes</div>
          </div>
        </div>

        <!-- CONTROLE DO STEPPER -->
        <div class="space-y-2">
          <div class="flex justify-between text-xs text-[#94a3b8]">
            <span>Navegar Rodadas:</span>
            <span id="step-indicator" class="font-semibold text-white">R1 / 7</span>
          </div>
          <div class="flex items-center gap-2">
            <button onclick="prevRound()" id="btn-prev" class="flex-1 bg-[#1e293b] hover:bg-[#334155] text-white font-medium py-2 rounded-xl text-sm transition-all disabled:opacity-30 disabled:cursor-not-allowed">◀ Anterior</button>
            <button onclick="nextRound()" id="btn-next" class="flex-1 bg-blue-600 hover:bg-blue-500 text-white font-medium py-2 rounded-xl text-sm transition-all shadow-lg shadow-blue-600/20 disabled:opacity-30 disabled:cursor-not-allowed">Próxima ▶</button>
          </div>
        </div>
      </div>

      <!-- CARD DO CONTRATO DA RODADA -->
      <div class="lg:col-span-8 bg-[#131b2e] border border-[#1e293b] rounded-2xl p-5 card-shadow">
        <div class="flex justify-between items-center pb-3 border-b border-[#1e293b]">
          <div class="flex items-center gap-2">
            <span class="text-amber-400 text-lg">📜</span>
            <span id="contract-tier" class="text-xs font-bold text-amber-400 uppercase tracking-wider">TIER 1</span>
            <span id="contract-name" class="text-base font-bold text-white ml-2">Arbitragem Simples</span>
          </div>
          <div id="contract-status" class="text-xs font-bold px-3 py-1 rounded-full">EM ANDAMENTO</div>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-3 my-4">
          <div class="bg-[#0f172a] p-3 rounded-xl border border-[#1e293b]">
            <div class="text-[11px] text-[#94a3b8]">Meta de Liquidez:</div>
            <div id="contract-target" class="text-lg font-bold text-emerald-400 mt-0.5">≥ 3 pts</div>
          </div>
          <div class="bg-[#0f172a] p-3 rounded-xl border border-[#1e293b]">
            <div class="text-[11px] text-[#94a3b8]">Cota de Insumos:</div>
            <div id="contract-req" class="text-sm font-bold text-amber-300 mt-0.5">Nenhum</div>
          </div>
          <div class="bg-[#0f172a] p-3 rounded-xl border border-[#1e293b]">
            <div class="text-[11px] text-[#94a3b8]">Chairman da Rodada:</div>
            <div id="contract-chair" class="text-sm font-bold text-blue-400 mt-0.5">Jogador 0</div>
          </div>
          <div class="bg-[#0f172a] p-3 rounded-xl border border-[#1e293b]">
            <div class="text-[11px] text-[#94a3b8]">Comitê Aprovado:</div>
            <div id="contract-comm" class="text-sm font-bold text-purple-300 mt-0.5">[P0, P1]</div>
          </div>
        </div>

        <!-- SONDAGEM & AUDITORIA DA RODADA -->
        <div class="bg-[#0b1120] rounded-xl p-3 border border-[#1e293b] text-xs space-y-2">
          <div class="flex items-start gap-2 text-[#94a3b8]">
            <span class="font-semibold text-blue-400 whitespace-nowrap">💬 Diálogo Social:</span>
            <span id="dialogue-text" class="text-slate-300">Líder consultou a mesa.</span>
          </div>
          <div class="flex items-start gap-2 text-[#94a3b8]">
            <span class="font-semibold text-emerald-400 whitespace-nowrap">🔍 Aporte Coordenado:</span>
            <span id="audit-text" class="text-slate-300">Aportes revelados na mesa.</span>
          </div>
        </div>

      </div>

    </div>

    <!-- SEÇÃO PRINCIPAL: RECURSOS POR JOGADOR & MATRIZ DE SUSPEITA -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

      <!-- COLUNA DA ESQUERDA: AS MÃOS E TOKENS DOS 5 JOGADORES -->
      <div class="lg:col-span-7 space-y-4">
        <div class="flex justify-between items-center px-1">
          <h2 class="text-lg font-bold text-white flex items-center gap-2">
            <span>💼</span> Recursos & Tokens por Carteira
          </h2>
          <span class="text-xs text-[#94a3b8]">Cartas em mão + Tokens de Juros (+1)</span>
        </div>

        <div id="players-container" class="space-y-3">
          <!-- Renderizado dinamicamente via JS -->
        </div>
      </div>

      <!-- COLUNA DA DIREITA: PAINEL DE DEDUÇÃO E SUSPEITA POR BANQUEIRO -->
      <div class="lg:col-span-5 space-y-4">
        <div class="flex justify-between items-center px-1">
          <h2 class="text-lg font-bold text-white flex items-center gap-2">
            <span>📈</span> Termômetro de Suspeita
          </h2>
          
          <!-- SELETOR DE PERSPECTIVA POR BANQUEIRO -->
          <div class="flex items-center gap-1 bg-[#1e293b] p-1 rounded-xl border border-[#334155]">
            <span class="text-[11px] text-[#94a3b8] px-2">Visão:</span>
            <select id="banker-perspective-select" onchange="changePerspective(this.value)" class="bg-[#0f172a] text-white text-xs font-semibold rounded-lg px-2 py-1 outline-none">
              <option value="avg">🌐 Média dos Banqueiros</option>
            </select>
          </div>
        </div>

        <div class="bg-[#131b2e] border border-[#1e293b] rounded-2xl p-5 card-shadow space-y-4">
          
          <!-- CABEÇALHO DO MODO DE PERSPECTIVA -->
          <div id="perspective-badge-container" class="bg-[#0b1120] p-2.5 rounded-xl border border-[#1e293b] flex items-center justify-between text-xs">
            <span class="text-slate-400 font-medium">Avaliador Ativo:</span>
            <span id="perspective-desc" class="font-bold text-blue-400">Consenso da Mesa (Média Geral)</span>
          </div>

          <!-- GRÁFICO SVG INTERATIVO DE SUSPEITA -->
          <div class="relative bg-[#0b1120] rounded-xl p-3 border border-[#1e293b]">
            <svg id="suspicion-chart" class="w-full h-48" viewBox="0 0 400 180">
              <line x1="40" y1="20" x2="380" y2="20" stroke="#1e293b" stroke-dasharray="3,3" />
              <line x1="40" y1="65" x2="380" y2="65" stroke="#1e293b" stroke-dasharray="3,3" />
              <line x1="40" y1="110" x2="380" y2="110" stroke="#1e293b" stroke-dasharray="3,3" />
              <line x1="40" y1="155" x2="380" y2="155" stroke="#334155" />

              <text x="30" y="24" fill="#64748b" font-size="9" text-anchor="end">100%</text>
              <text x="30" y="69" fill="#64748b" font-size="9" text-anchor="end">70%</text>
              <text x="30" y="114" fill="#64748b" font-size="9" text-anchor="end">40%</text>
              <text x="30" y="158" fill="#64748b" font-size="9" text-anchor="end">0%</text>

              <g id="chart-lines"></g>
            </svg>

            <div id="chart-legend" class="flex flex-wrap justify-center gap-3 mt-2 text-[11px]"></div>
          </div>

          <!-- TABELA DE NOTAS DE SUSPEITA DA RODADA ATUAL -->
          <div class="space-y-2">
            <div class="text-xs font-semibold text-[#94a3b8] flex justify-between">
              <span>Classificação na Rodada Atual:</span>
              <span id="perspective-sub-desc" class="text-slate-400">0% (Inocente) a 100% (Traidor)</span>
            </div>
            <div id="suspicion-bars" class="space-y-2"></div>
          </div>

        </div>
      </div>

    </div>

  </div>

  <script>
    const TRACES = {json.dumps(traces, ensure_ascii=False)};

    let currentScenarioKey = 'sleeper_game';
    let currentRoundIdx = 0;
    let currentPerspective = 'avg';

    const PLAYER_COLORS = [
      {{ border: '#3b82f6', bg: 'rgba(59, 130, 246, 0.15)', text: 'text-blue-400', line: '#3b82f6' }},
      {{ border: '#10b981', bg: 'rgba(16, 185, 129, 0.15)', text: 'text-emerald-400', line: '#10b981' }},
      {{ border: '#f59e0b', bg: 'rgba(245, 158, 11, 0.15)', text: 'text-amber-400', line: '#f59e0b' }},
      {{ border: '#ef4444', bg: 'rgba(239, 68, 68, 0.15)', text: 'text-red-400', line: '#ef4444' }},
      {{ border: '#8b5cf6', bg: 'rgba(139, 92, 246, 0.15)', text: 'text-purple-400', line: '#8b5cf6' }}
    ];

    function changeScenario(key) {{
      currentScenarioKey = key;
      currentRoundIdx = 0;
      currentPerspective = 'avg';
      populateBankerPerspectiveSelect();
      updateView();
    }}

    function changePerspective(val) {{
      currentPerspective = val;
      updatePerspectiveUI();
    }}

    function populateBankerPerspectiveSelect() {{
      const match = TRACES[currentScenarioKey];
      const select = document.getElementById('banker-perspective-select');
      select.innerHTML = '<option value="avg">🌐 Média dos Banqueiros</option>';
      
      match.banker_ids.forEach(bid => {{
        const opt = document.createElement('option');
        opt.value = bid.toString();
        opt.textContent = `🏛️ Banqueiro P${{bid}}`;
        select.appendChild(opt);
      }});
      select.value = currentPerspective;
    }}

    function prevRound() {{
      if (currentRoundIdx > 0) {{
        currentRoundIdx--;
        updateView();
      }}
    }}

    function nextRound() {{
      const match = TRACES[currentScenarioKey];
      if (currentRoundIdx < match.rounds.length - 1) {{
        currentRoundIdx++;
        updateView();
      }}
    }}

    function updateView() {{
      const match = TRACES[currentScenarioKey];
      const rData = match.rounds[currentRoundIdx];
      const totalRounds = match.rounds.length;

      const badges = {{
        'sleeper_game': {{ text: 'Sleeper Estratégico (Infiltração Profunda)', class: 'bg-purple-600/20 text-purple-300 border-purple-500/30' }},
        'aggressive_game': {{ text: 'Agressivo (Blefe Imediato & Sabotagem)', class: 'bg-red-600/20 text-red-300 border-red-500/30' }},
        'hedge_game': {{ text: 'Hedge Econômico (Retenção & Clímax na R7)', class: 'bg-amber-600/20 text-amber-300 border-amber-500/30' }}
      }};
      document.getElementById('match-badge').textContent = badges[currentScenarioKey].text;
      document.getElementById('match-badge').className = 'text-xs font-semibold px-2.5 py-1 rounded-full border ' + badges[currentScenarioKey].class;

      document.getElementById('round-badge').textContent = `Rodada ${{rData.round_num}} de 7`;
      document.getElementById('score-banker').textContent = rData.banker_score;
      document.getElementById('score-intern').textContent = rData.intern_score;
      document.getElementById('step-indicator').textContent = `R${{rData.round_num}} / ${{totalRounds}}`;

      document.getElementById('btn-prev').disabled = (currentRoundIdx === 0);
      document.getElementById('btn-next').disabled = (currentRoundIdx === totalRounds - 1);

      document.getElementById('contract-tier').textContent = `TIER ${{rData.contract.tier}}`;
      document.getElementById('contract-name').textContent = rData.contract.name;
      document.getElementById('contract-target').textContent = `≥ ${{rData.contract.target}} pts (${{rData.contract.committee_size}} ops x ${{rData.contract.cost_per_player}} carta)`;
      
      const reqCount = rData.contract.req_count || 1;
      const reqText = rData.contract.req_commodity 
        ? (reqCount > 1 ? `≥ ${{reqCount}}x ${{rData.contract.req_commodity}}` : `${{rData.contract.req_commodity}}`)
        : 'Nenhum';
      document.getElementById('contract-req').textContent = reqText;

      document.getElementById('contract-chair').textContent = `Jogador ${{rData.chair_id}} (${{match.players[rData.chair_id].role}})`;
      document.getElementById('contract-comm').textContent = `[${{rData.committee.map(id => 'P' + id).join(', ')}}]`;

      const statusBadge = document.getElementById('contract-status');
      if (rData.is_success) {{
        statusBadge.textContent = '✓ CONCLUÍDO COM SUCESSO';
        statusBadge.className = 'text-xs font-bold px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30';
      }} else {{
        statusBadge.textContent = '✗ REPROVADO POR FRAUDE/DÉFICIT';
        statusBadge.className = 'text-xs font-bold px-3 py-1 rounded-full bg-red-500/20 text-red-400 border border-red-500/30';
      }}

      let declDetails = [];
      Object.keys(rData.declarations).forEach(pid => {{
        const d = rData.declarations[pid];
        let tag = d.prefers_bench ? ' [✋ Pede Banco]' : ` [💬 ${{"Oferece " + d.offered_desc}}]`;
        if (d.claims_req) tag += ' [🏷️ Tem Insumo]';
        declDetails.push(`P${{pid}}:${{tag}}`);
      }});

      document.getElementById('dialogue-text').textContent = declDetails.join(' | ');

      const subCardsDetail = rData.submitted.map(s => {{
        const cStr = s.cards.map(c => `${{c.name}} (${{c.base}}pts)`).join(' + ');
        const tokStr = s.tokens_spent > 0 ? ` + ${{s.tokens_spent}}🪙` : '';
        return `P${{s.player_id}}: [${{cStr}}${{tokStr}}]`;
      }}).join(' + ');

      document.getElementById('audit-text').textContent = `${{subCardsDetail}} = ${{rData.total_value}} pts (Meta: ${{rData.contract.target}} pts | Req: ${{rData.has_req ? 'OK' : 'FALTOU'}}).`;

      renderPlayersHands(match, rData);
      updatePerspectiveUI();
    }}

    function updatePerspectiveUI() {{
      const match = TRACES[currentScenarioKey];
      const rData = match.rounds[currentRoundIdx];

      if (currentPerspective === 'avg') {{
        document.getElementById('perspective-desc').textContent = '🌐 Consenso Geral da Mesa (Média dos Banqueiros)';
        document.getElementById('perspective-sub-desc').textContent = 'Média das notas de suspeita';
      }} else {{
        const bId = parseInt(currentPerspective);
        document.getElementById('perspective-desc').textContent = `🏛️ Ponto de Vista do Banqueiro P${{bId}}`;
        document.getElementById('perspective-sub-desc').textContent = `Avaliação contábil pessoal de P${{bId}}`;
      }}

      renderSuspicionChart(match, currentRoundIdx);
      renderSuspicionBars(match, rData);
    }}

    function renderPlayersHands(match, rData) {{
      const container = document.getElementById('players-container');
      container.innerHTML = '';

      match.players.forEach(p => {{
        const isChair = (p.id === rData.chair_id);
        const inComm = rData.committee.includes(p.id);
        const pHandData = rData.hands_before[p.id];
        const cards = pHandData.cards || pHandData;
        const tokens = pHandData.tokens || 0;
        const color = PLAYER_COLORS[p.id];
        const decl = rData.declarations[p.id];

        const isBanker = (p.role === 'Banqueiro');
        const roleBadge = isBanker 
          ? '<span class="bg-blue-900/40 text-blue-300 text-[10px] font-bold px-2 py-0.5 rounded border border-blue-700/40">BANQUEIRO</span>'
          : '<span class="bg-red-900/40 text-red-300 text-[10px] font-bold px-2 py-0.5 rounded border border-red-700/40">ESTAGIÁRIO</span>';

        let tags = '';
        if (isChair) tags += '<span class="bg-amber-900/40 text-amber-300 text-[10px] font-bold px-1.5 py-0.5 rounded border border-amber-700/40">CHAIRMAN</span> ';
        if (inComm) tags += '<span class="bg-purple-900/40 text-purple-300 text-[10px] font-bold px-1.5 py-0.5 rounded border border-purple-700/40">COMITÊ</span> ';
        if (decl && decl.prefers_bench) tags += '<span class="bg-slate-700/50 text-slate-300 text-[10px] font-medium px-1.5 py-0.5 rounded border border-slate-600/50">PEDIU BANCO</span> ';

        let tokensHtml = '';
        if (tokens > 0) {{
          tokensHtml = `
            <div class="border border-amber-500/40 bg-amber-950/40 text-amber-300 font-bold px-2 py-1 rounded-lg text-xs flex items-center gap-1 shadow-sm">
              <span>🪙 Tokens Juros:</span>
              <span class="font-mono text-amber-200">+${{tokens}} pts</span>
            </div>
          `;
        }}

        let cardsHtml = cards.map(c => {{
          let cardColor = 'bg-slate-800 text-slate-200 border-slate-700';
          if (c.type === 'CO') cardColor = 'bg-slate-800/80 text-blue-300 border-blue-800/50';
          if (c.type === 'VN') cardColor = 'bg-emerald-950/70 text-emerald-300 border-emerald-800/50';
          if (c.type === 'TI') cardColor = 'bg-amber-950/70 text-amber-300 border-amber-800/50';
          if (c.type === 'SF') cardColor = 'bg-cyan-950/80 text-cyan-300 border-cyan-700/60 font-semibold';
          if (c.type === 'WILD') cardColor = 'bg-yellow-950 text-yellow-300 border-yellow-500 font-bold';
          if (c.type === 'TOXIC') cardColor = 'bg-red-950 text-red-400 border-red-600 font-bold';

          return `
            <div class="border rounded-lg px-2 py-1 text-xs flex items-center justify-between gap-1.5 ${{cardColor}}">
              <span>${{c.name.split(' ')[0]}}</span>
              <span class="font-mono font-bold">${{c.base}}pt</span>
            </div>
          `;
        }}).join('');

        const playerCard = document.createElement('div');
        playerCard.className = `bg-[#131b2e] border rounded-xl p-3 flex flex-col md:flex-row md:items-center justify-between gap-3 ${{inComm ? 'border-purple-500/50 shadow-sm shadow-purple-500/10' : 'border-[#1e293b]'}}`;
        playerCard.innerHTML = `
          <div class="flex items-center gap-2.5 min-w-[210px]">
            <div class="w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs" style="background: ${{color.bg}}; color: ${{color.line}}; border: 1px solid ${{color.border}};">
              P${{p.id}}
            </div>
            <div>
              <div class="flex items-center gap-1.5">
                <span class="font-bold text-sm text-white">Jogador ${{p.id}}</span>
                ${{roleBadge}}
              </div>
              <div class="mt-1 flex flex-wrap items-center gap-1">${{tags}}</div>
            </div>
          </div>

          <div class="flex-1 flex flex-wrap items-center gap-1.5">
            ${{tokensHtml}}
            ${{cardsHtml}}
          </div>
        `;
        container.appendChild(playerCard);
      }});
    }}

    function getPlayerSuspicionInRound(match, rIdx, targetId) {{
      const r = match.rounds[rIdx];
      if (currentPerspective === 'avg') {{
        return r.suspicions.avg[targetId];
      }} else {{
        const bId = parseInt(currentPerspective);
        return r.suspicions.by_banker[bId][targetId];
      }}
    }}

    function renderSuspicionChart(match, activeRoundIdx) {{
      const svgLines = document.getElementById('chart-lines');
      const legend = document.getElementById('chart-legend');
      svgLines.innerHTML = '';
      legend.innerHTML = '';

      const totalRounds = match.rounds.length;
      const xStep = (380 - 40) / Math.max(1, totalRounds - 1);

      match.players.forEach(p => {{
        const color = PLAYER_COLORS[p.id];
        const isB = (p.role === 'Banqueiro');

        legend.innerHTML += `
          <div class="flex items-center gap-1.5">
            <span class="w-2.5 h-2.5 rounded-full" style="background: ${{color.line}}"></span>
            <span class="text-slate-300">P${{p.id}} (${{isB ? 'Banq' : 'Estag'}})</span>
          </div>
        `;

        let points = [];
        for (let r = 0; r <= activeRoundIdx; r++) {{
          const susVal = getPlayerSuspicionInRound(match, r, p.id);
          const x = 40 + r * xStep;
          const y = 155 - (susVal * (155 - 20));
          points.push({{ x, y, sus: susVal }});
        }}

        if (points.length > 0) {{
          let d = `M ${{points[0].x}} ${{points[0].y}}`;
          for (let i = 1; i < points.length; i++) {{
            d += ` L ${{points[i].x}} ${{points[i].y}}`;
          }}

          const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
          path.setAttribute('d', d);
          path.setAttribute('fill', 'none');
          path.setAttribute('stroke', color.line);
          path.setAttribute('stroke-width', '2.5');
          path.setAttribute('stroke-linecap', 'round');
          svgLines.appendChild(path);

          const lastPt = points[points.length - 1];
          const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
          circle.setAttribute('cx', lastPt.x);
          circle.setAttribute('cy', lastPt.y);
          circle.setAttribute('r', '4.5');
          circle.setAttribute('fill', color.line);
          circle.setAttribute('stroke', '#0b1120');
          circle.setAttribute('stroke-width', '1.5');
          svgLines.appendChild(circle);
        }}
      }});
    }}

    function renderSuspicionBars(match, rData) {{
      const container = document.getElementById('suspicion-bars');
      container.innerHTML = '';

      match.players.forEach(p => {{
        const susVal = getPlayerSuspicionInRound(match, currentRoundIdx, p.id);
        const color = PLAYER_COLORS[p.id];
        const isBanker = (p.role === 'Banqueiro');

        let tagStatus = '';
        let barColor = 'bg-blue-500';

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

artifact_path = os.path.join(r'C:\Users\najoa\.gemini\antigravity\brain\d2191cbb-fe5a-4e6b-a45e-24c2278f7400', 'match_visualizer.html')
with open(artifact_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Dashboard v12.0 gerado com sucesso em: {artifact_path}")
