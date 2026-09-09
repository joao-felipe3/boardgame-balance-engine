# -*- coding: utf-8 -*-
"""
BTG Madagascar - Gerador do Visualizador HTML de Partida (Dashboard v14.0)
Identidade Visual Temática: Madagascar (L'Île Rouge, Floresta Tropical & Commodities do Oceano Índico)
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
  <title>BTG Madagascar: Terminal de Commodities & Auditoria de Risco</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    body {{
      font-family: 'Plus Jakarta Sans', sans-serif;
      background: radial-gradient(circle at 15% 15%, rgba(194, 65, 12, 0.14) 0%, transparent 45%),
                  radial-gradient(circle at 85% 85%, rgba(16, 185, 129, 0.12) 0%, transparent 45%),
                  radial-gradient(circle at 50% 50%, rgba(2, 132, 199, 0.08) 0%, transparent 60%),
                  #070d14;
    }}
    h1, h2, h3, .font-heading {{ font-family: 'Outfit', sans-serif; }}
    .card-glass {{
      background: rgba(13, 23, 34, 0.78);
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
      border: 1px solid rgba(41, 62, 82, 0.55);
      box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.45);
    }}
    .card-glass:hover {{
      border-color: rgba(224, 109, 68, 0.4);
    }}
    .glow-gold {{
      box-shadow: 0 0 18px -2px rgba(245, 158, 11, 0.35);
    }}
    .glow-emerald {{
      box-shadow: 0 0 18px -2px rgba(16, 185, 129, 0.35);
    }}
    .glow-terracota {{
      box-shadow: 0 0 18px -2px rgba(224, 109, 68, 0.35);
    }}
    .baobab-bg {{
      background-image: radial-gradient(rgba(245, 158, 11, 0.06) 1px, transparent 0);
      background-size: 24px 24px;
    }}
    .commodity-badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 9999px;
      font-weight: 600;
      font-size: 11px;
      letter-spacing: 0.02em;
    }}
  </style>
</head>
<body class="text-[#e2e8f0] min-h-screen p-3 md:p-8 antialiased baobab-bg">

  <div class="max-w-7xl mx-auto space-y-6">

    <!-- HEADER / TOP BAR COM IDENTIDADE DE MADAGASCAR -->
    <header class="card-glass rounded-3xl p-6 md:p-8 border-t-2 border-t-[#e06d44] flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
      <div class="space-y-2">
        <div class="flex flex-wrap items-center gap-2.5">
          <span class="bg-[#e06d44]/20 text-[#f08a5d] text-xs font-bold px-3 py-1 rounded-full border border-[#e06d44]/40 flex items-center gap-1.5 uppercase tracking-wider">
            <span>🇲🇬</span> REPUBLIKAN'I MADAGASIKARA
          </span>
          <span class="bg-emerald-500/15 text-emerald-400 text-xs font-bold px-3 py-1 rounded-full border border-emerald-500/30 flex items-center gap-1.5 uppercase tracking-wider">
            <span>🌿</span> SUCURSAL OCEANO ÍNDICO
          </span>
          <span class="bg-amber-500/15 text-amber-300 text-xs font-bold px-3 py-1 rounded-full border border-amber-500/30 flex items-center gap-1.5 uppercase tracking-wider">
            <span>⚖️</span> SIMULADOR v14.0
          </span>
        </div>
        
        <h1 class="text-3xl md:text-4xl font-extrabold text-white tracking-tight flex items-center gap-3">
          <span>BTG Pactual</span>
          <span class="text-transparent bg-clip-text bg-gradient-to-r from-[#e06d44] via-amber-400 to-emerald-400">Madagascar</span>
        </h1>
        <p class="text-sm text-slate-400 max-w-2xl leading-relaxed">
          Terminal executivo de custódia e auditoria: acompanhe o fluxo de commodities de <strong class="text-slate-200">Sava, Ambatovy, Tolagnaro e Ilakaka</strong>, monitore a queima de tokens de rendimento em <strong class="text-amber-300">Ariary Malgaxe (MGA)</strong> e inspecione a rede de confiança bayesiana do Conselho.
        </p>
      </div>

      <!-- SELETOR DE CENÁRIO / PERFIL DE IA -->
      <div class="bg-[#0b131e]/90 p-4 rounded-2xl border border-[#233547] space-y-2 min-w-[280px]">
        <div class="flex justify-between items-center">
          <label class="text-xs text-amber-400 font-bold uppercase tracking-wider flex items-center gap-1.5">
            <span>🎯</span> Cenário de Auditoria:
          </label>
          <span class="text-[10px] text-slate-400">5 Perfis de IA</span>
        </div>
        <select id="scenario-select" onchange="changeScenario(this.value)" class="w-full bg-[#142232] border border-[#2e4760] text-white text-xs font-semibold rounded-xl px-3 py-2.5 focus:ring-2 focus:ring-[#e06d44] outline-none transition-all cursor-pointer">
          <option value="sleeper_game">🎭 Sleeper Estratégico (Infiltração em Toamasina)</option>
          <option value="aggressive_game">⚔️ Agressivo (Blefe Imediato na Costa de Sava)</option>
          <option value="hedge_game">🛡️ Hedge Econômico (Retenção em Ilakaka)</option>
          <option value="opportunist_game">🦎 Oportunista (Camaleão das Terras Altas)</option>
          <option value="technician_game">🔬 Técnico (Fraude Cirúrgica / Falsa Idoneidade)</option>
        </select>
      </div>
    </header>

    <!-- PLACAR SOBERANO & STEPPER GEOGRÁFICO DE MADAGASCAR -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      
      <!-- CARD DO PLACAR SOBERANO -->
      <div class="lg:col-span-4 card-glass rounded-3xl p-6 flex flex-col justify-between relative overflow-hidden">
        <div class="absolute -right-8 -bottom-8 w-36 h-36 bg-amber-500/5 rounded-full blur-2xl pointer-events-none"></div>

        <div class="flex justify-between items-center pb-3 border-b border-[#1f3144]">
          <span class="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <span>🏛️</span> Conselho do Banco vs Operações Offshore
          </span>
          <span id="round-badge" class="text-xs bg-[#e06d44]/20 text-[#f08a5d] font-extrabold px-2.5 py-0.5 rounded-full border border-[#e06d44]/30 font-mono">
            R1 de 7
          </span>
        </div>

        <div class="grid grid-cols-2 gap-4 my-5 text-center">
          <div class="bg-gradient-to-br from-[#0c2236]/90 to-[#081726]/90 rounded-2xl p-4 border border-blue-500/30">
            <div class="text-xs text-blue-300 font-bold uppercase tracking-wider flex items-center justify-center gap-1">
              <span>🏛️</span> Banqueiros
            </div>
            <div id="banker-score" class="text-4xl font-extrabold text-blue-400 mt-1 font-heading">0</div>
            <div class="text-[10px] text-blue-200/60 mt-1 font-medium">Meta: 4 Contratos</div>
          </div>
          
          <div class="bg-gradient-to-br from-[#2a1310]/90 to-[#1b0a08]/90 rounded-2xl p-4 border border-red-500/30">
            <div class="text-xs text-red-300 font-bold uppercase tracking-wider flex items-center justify-center gap-1">
              <span>🕵️</span> Estagiários
            </div>
            <div id="intern-score" class="text-4xl font-extrabold text-red-400 mt-1 font-heading">0</div>
            <div class="text-[10px] text-red-200/60 mt-1 font-medium">Meta: 4 Sabotagens</div>
          </div>
        </div>

        <div id="game-status-banner" class="text-xs text-center py-2.5 px-4 rounded-xl font-bold transition-all shadow-inner">
          Partida em Andamento
        </div>
      </div>

      <!-- LINHA DO TEMPO DAS 7 REGIÕES ECONÔMICAS DE MADAGASCAR -->
      <div class="lg:col-span-8 card-glass rounded-3xl p-6 flex flex-col justify-between">
        <div>
          <div class="flex justify-between items-center pb-3 border-b border-[#1f3144]">
            <span class="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <span>📍</span> Rota de Expansão em Madagascar (Tiers 1 a 7)
            </span>
            <span class="text-xs text-amber-400/80 font-medium">Selecione para navegar pelas rodadas</span>
          </div>

          <!-- BOTÕES DO STEPPER COM PROVÍNCIAS MALGAXES -->
          <div id="timeline-stepper" class="grid grid-cols-7 gap-2 my-4">
            <!-- Injetado via JS -->
          </div>
        </div>

        <!-- CONTROLES NAVEGACIONAIS -->
        <div class="flex justify-between items-center pt-3 border-t border-[#1f3144]">
          <button onclick="prevRound()" class="px-4 py-2 bg-[#142232] hover:bg-[#1f364d] text-xs font-bold rounded-xl transition-all text-slate-200 border border-[#2e4760] flex items-center gap-1.5">
            <span>◀</span> Rodada Anterior
          </button>
          <span id="step-indicator" class="text-xs text-slate-400 font-medium font-mono">
            Rodada 1 de 7
          </span>
          <button onclick="nextRound()" class="px-4 py-2 bg-[#142232] hover:bg-[#1f364d] text-xs font-bold rounded-xl transition-all text-slate-200 border border-[#2e4760] flex items-center gap-1.5">
            Próxima Rodada <span>▶</span>
          </button>
        </div>
      </div>

    </div>

    <!-- PAINEL CENTRAL: CONTRATO REGIONAL & AUDITORIA DE COFRE -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

      <!-- COLUNA DA ESQUERDA (8 COLUNAS): CONTRATO, DIRETRIZ REGULATÓRIA & COFRE -->
      <div class="lg:col-span-8 space-y-6">

        <!-- CARD DO CONTRATO REGIONAL -->
        <div class="card-glass rounded-3xl p-6 md:p-8 space-y-5 border-l-4 border-l-[#e06d44]">
          <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
              <div class="flex flex-wrap items-center gap-2">
                <span id="tier-badge" class="bg-[#e06d44]/20 text-[#f08a5d] text-xs font-extrabold px-2.5 py-0.5 rounded-lg border border-[#e06d44]/40 font-mono uppercase">
                  Tier 1
                </span>
                <span id="region-badge" class="bg-emerald-500/15 text-emerald-300 text-xs font-bold px-2.5 py-0.5 rounded-lg border border-emerald-500/30">
                  🌿 Sava (Costa da Baunilha)
                </span>
              </div>
              <h2 id="contract-name" class="text-2xl font-extrabold text-white mt-1.5 font-heading tracking-tight">
                Exportação de Baunilha Bourbon
              </h2>
              <p id="contract-desc" class="text-xs text-slate-400 mt-1">
                Comitê de 2 membros • Meta de Liquidez: 4 pontos • Custo: 1 carta por membro
              </p>
            </div>
            
            <div id="outcome-pill" class="px-5 py-2 rounded-2xl font-extrabold text-sm uppercase tracking-wider flex items-center gap-2 shadow-lg">
              <span>APROVADO</span>
            </div>
          </div>

          <!-- MÉTRICAS DO RESULTADO DO CONTRATO -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3 pt-2">
            <div class="bg-[#0b1420]/80 p-3.5 rounded-2xl border border-[#203447]">
              <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Pontuação Atingida</div>
              <div id="total-score-val" class="text-xl font-extrabold text-white mt-0.5 font-mono">5 / 4</div>
            </div>
            <div class="bg-[#0b1420]/80 p-3.5 rounded-2xl border border-[#203447]">
              <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Cota de Insumo</div>
              <div id="req-commodity-val" class="text-sm font-bold text-amber-300 mt-1">Baunilha (x1)</div>
            </div>
            <div class="bg-[#0b1420]/80 p-3.5 rounded-2xl border border-[#203447]">
              <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Tokens de Ariary Usados</div>
              <div id="tokens-used-val" class="text-xl font-extrabold text-amber-400 mt-0.5 font-mono">0 🪙</div>
            </div>
            <div class="bg-[#0b1420]/80 p-3.5 rounded-2xl border border-[#203447]">
              <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Chairman da Pauta</div>
              <div id="chair-val" class="text-sm font-extrabold text-blue-300 mt-1">Operador 0</div>
            </div>
          </div>

          <!-- CARD DA DIRETRIZ REGULATÓRIA / PODER CORPORATIVO (DLC) -->
          <div id="directive-card-container" class="pt-3 border-t border-[#1f3144]">
            <!-- Injetado via JS -->
          </div>

          <!-- AUDITORIA DO COFRE DE CONTRIBUIÇÃO SECRETA -->
          <div class="pt-4 border-t border-[#1f3144]">
            <div class="flex justify-between items-center mb-3">
              <span class="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <span>🔒</span> Cofre de Liquidação (Cartas Depositadas em Sigilo)
              </span>
              <span class="text-[10px] text-amber-300 font-bold bg-amber-950/50 px-2.5 py-1 rounded-full border border-amber-600/40 uppercase">
                Auditoria de Revelação
              </span>
            </div>

            <div id="submitted-cards-grid" class="grid grid-cols-1 md:grid-cols-2 gap-3.5">
              <!-- Injetado via JS -->
            </div>
          </div>
        </div>

        <!-- CARTEIRA DE COMMODITIES & RESERVA DE ARIARY (TODOS OS OPERADORES) -->
        <div class="card-glass rounded-3xl p-6 md:p-8 space-y-4">
          <div class="flex justify-between items-center pb-3 border-b border-[#1f3144]">
            <div class="space-y-0.5">
              <span class="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                <span>💼</span> Carteiras de Commodities & Saldo de Ariary (MGA)
              </span>
              <p class="text-[11px] text-slate-400">Operadores no banco recebem +1 Carta do Mercado e +1 Token de Rendimento da reserva</p>
            </div>
            <span class="text-[11px] font-bold text-emerald-400 bg-emerald-950/40 px-2.5 py-1 rounded-lg border border-emerald-700/40">
              5 Operadores Ativos
            </span>
          </div>

          <div id="players-hands-grid" class="grid grid-cols-1 md:grid-cols-5 gap-3">
            <!-- Injetado via JS -->
          </div>
        </div>

      </div>

      <!-- COLUNA DA DIREITA (4 COLUNAS): RADAR BAYESIANO & GABARITO CORPORATIVO -->
      <div class="lg:col-span-4 space-y-6">

        <!-- CARD DO RADAR DE DEDUÇÃO BAYESIANA -->
        <div class="card-glass rounded-3xl p-6 md:p-7 space-y-4">
          <div class="pb-3 border-b border-[#1f3144] space-y-1">
            <span class="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <span>📡</span> Radar de Risco & Suspeita
            </span>
            <p class="text-[11px] text-slate-400 leading-tight">Inspecione como cada Banqueiro enxerga a lealdade dos seus colegas na mesa</p>
          </div>

          <!-- SELETOR DE PONTO DE VISTA -->
          <div class="space-y-1.5">
            <label class="text-[11px] text-amber-400/90 font-bold uppercase tracking-wider">Perspectiva do Banqueiro:</label>
            <select id="banker-perspective-select" onchange="changePerspective(this.value)" class="w-full bg-[#101b27] border border-[#2a4055] text-white text-xs font-semibold rounded-xl px-3 py-2.5 outline-none focus:ring-2 focus:ring-[#e06d44] transition-all cursor-pointer">
              <!-- Injetado via JS -->
            </select>
          </div>

          <!-- BARRAS DE SUSPEITA COM IDENTIDADE VISUAL -->
          <div id="suspicion-bars-container" class="space-y-3 pt-2">
            <!-- Injetado via JS -->
          </div>

          <div class="text-[11px] text-slate-400 bg-[#0b131e]/90 p-3.5 rounded-2xl border border-[#203447] leading-relaxed">
            💡 <strong class="text-slate-200">Dedução Bayesiana da Mesa:</strong>
            Falhas em comitês de 2 membros geram suspeita mútua imediata. Comitês aprovados reduzem a desconfiança, permitindo ao Banco mapear gradualmente os sabotadores sem depender de palpites cegos.
          </div>
        </div>

        <!-- GABARITO DE IDENTIDADES CORPORATIVAS -->
        <div class="card-glass rounded-3xl p-6 md:p-7 space-y-3">
          <div class="flex justify-between items-center pb-2 border-b border-[#1f3144]">
            <span class="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <span>📂</span> Gabarito de Identidades
            </span>
            <span class="text-[10px] text-slate-400">Auditoria Externa</span>
          </div>
          <div id="roster-list" class="space-y-2 text-xs">
            <!-- Injetado via JS -->
          </div>
        </div>

        <!-- GUIA DE COMMODITIES DE MADAGASCAR -->
        <div class="card-glass rounded-3xl p-5 space-y-3">
          <span class="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5">
            <span>💎</span> Índice de Ativos Malgaxes
          </span>
          <div class="grid grid-cols-2 gap-2 text-[11px]">
            <div class="bg-[#101a26] p-2 rounded-xl border border-indigo-900/40">
              <span class="font-bold text-indigo-300">⛏️ Cobalto (+1)</span>
              <p class="text-[9px] text-slate-400">Ambatovy (Base industrial)</p>
            </div>
            <div class="bg-[#101a26] p-2 rounded-xl border border-amber-900/40">
              <span class="font-bold text-amber-300">🌿 Baunilha (+2)</span>
              <p class="text-[9px] text-slate-400">Sava (Agronegócio nobre)</p>
            </div>
            <div class="bg-[#101a26] p-2 rounded-xl border border-sky-900/40">
              <span class="font-bold text-sky-300">🛡️ Titânio (+3)</span>
              <p class="text-[9px] text-slate-400">Tolagnaro (Insumo nobre)</p>
            </div>
            <div class="bg-[#101a26] p-2 rounded-xl border border-blue-900/40">
              <span class="font-bold text-blue-300">💎 Safira (+4)</span>
              <p class="text-[9px] text-slate-400">Ilakaka (Gema rara)</p>
            </div>
            <div class="bg-[#101a26] p-2 rounded-xl border border-yellow-900/40">
              <span class="font-bold text-yellow-300">🌟 Ouro Líquido (+4)</span>
              <p class="text-[9px] text-slate-400">Coringa leal do Banco</p>
            </div>
            <div class="bg-[#101a26] p-2 rounded-xl border border-red-900/40">
              <span class="font-bold text-red-300">☣️ Ativo Tóxico (-4)</span>
              <p class="text-[9px] text-slate-400">Fraude do Estagiário</p>
            </div>
          </div>
        </div>

      </div>

    </div>

  </div>

  <!-- JAVASCRIPT DE DINÂMICA & RENDERIZAÇÃO TEMÁTICA -->
  <script>
    const tracesData = {traces_json_str};
    let currentScenarioKey = 'sleeper_game';
    let currentRoundIndex = 0;
    let currentPerspective = 'avg';

    const madagascarRegions = {{
      1: {{ name: "🌿 Sava (Costa da Baunilha)", code: "SAVA" }},
      2: {{ name: "⛏️ Ambatovy (Bacia de Cobalto & Níquel)", code: "AMBAT" }},
      3: {{ name: "⚓ Tolagnaro (Porto Ehoala de Titânio)", code: "EHOALA" }},
      4: {{ name: "🏭 Antsirabe (Complexo Agro-Industrial)", code: "ANTSIR" }},
      5: {{ name: "🚢 Toamasina (Megaconsórcio Portuário)", code: "TOAMAS" }},
      6: {{ name: "💎 Ilakaka (Garganta de Safiras)", code: "ILAKAK" }},
      7: {{ name: "🏛️ Antananarivo (Holding Global BTG)", code: "TANA" }}
    }};

    const playerThemes = [
      {{ name: 'P0', color: '#60a5fa', border: '#2563eb', bg: '#0c2236' }},
      {{ name: 'P1', color: '#34d399', border: '#059669', bg: '#062619' }},
      {{ name: 'P2', color: '#f59e0b', border: '#d97706', bg: '#291809' }},
      {{ name: 'P3', color: '#f87171', border: '#dc2626', bg: '#260b09' }},
      {{ name: 'P4', color: '#a78bfa', border: '#7c3aed', bg: '#1c0f33' }}
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
      select.innerHTML = '<option value="avg">📊 Média Consolidada dos Banqueiros</option>';

      match.players.forEach(p => {{
        if (match.banker_ids.includes(p.id)) {{
          select.innerHTML += `<option value="${{p.id}}">👁️ Perspectiva do Operador ${{p.id}} (Banqueiro Leal)</option>`;
        }}
      }});
      select.value = currentPerspective;
    }}

    function formatCardBadge(card) {{
      const type = card.type || '';
      const name = card.name || '';
      const base = card.base || 0;

      if (type === 'TOXIC') {{
        return `
          <div class="bg-gradient-to-r from-red-950 to-red-900 border border-red-600/60 text-red-200 rounded-xl p-2.5 flex justify-between items-center text-xs shadow-md">
            <span class="font-bold flex items-center gap-1.5"><span>☣️</span> ${{name}}</span>
            <span class="font-mono font-extrabold text-red-400 bg-black/40 px-2 py-0.5 rounded">${{base}} pts</span>
          </div>
        `;
      }} else if (type === 'WILD') {{
        return `
          <div class="bg-gradient-to-r from-amber-950 to-yellow-950 border border-amber-500/60 text-amber-200 rounded-xl p-2.5 flex justify-between items-center text-xs shadow-md">
            <span class="font-bold flex items-center gap-1.5"><span>🌟</span> ${{name}}</span>
            <span class="font-mono font-extrabold text-amber-300 bg-black/40 px-2 py-0.5 rounded">+${{base}} pts</span>
          </div>
        `;
      }} else if (type === 'SF') {{
        return `
          <div class="bg-gradient-to-r from-blue-950 to-indigo-950 border border-blue-500/60 text-blue-200 rounded-xl p-2.5 flex justify-between items-center text-xs shadow-md">
            <span class="font-bold flex items-center gap-1.5"><span>💎</span> ${{name}}</span>
            <span class="font-mono font-extrabold text-blue-300 bg-black/40 px-2 py-0.5 rounded">+${{base}} pts</span>
          </div>
        `;
      }} else if (type === 'TI') {{
        return `
          <div class="bg-gradient-to-r from-slate-900 to-sky-950 border border-sky-500/50 text-sky-200 rounded-xl p-2.5 flex justify-between items-center text-xs shadow-md">
            <span class="font-bold flex items-center gap-1.5"><span>🛡️</span> ${{name}}</span>
            <span class="font-mono font-extrabold text-sky-300 bg-black/40 px-2 py-0.5 rounded">+${{base}} pts</span>
          </div>
        `;
      }} else if (type === 'VN') {{
        return `
          <div class="bg-gradient-to-r from-[#291809] to-[#3a200b] border border-amber-600/50 text-amber-200 rounded-xl p-2.5 flex justify-between items-center text-xs shadow-md">
            <span class="font-bold flex items-center gap-1.5"><span>🌿</span> ${{name}}</span>
            <span class="font-mono font-extrabold text-amber-300 bg-black/40 px-2 py-0.5 rounded">+${{base}} pts</span>
          </div>
        `;
      }} else {{
        return `
          <div class="bg-gradient-to-r from-indigo-950 to-slate-900 border border-indigo-500/40 text-indigo-200 rounded-xl p-2.5 flex justify-between items-center text-xs shadow-md">
            <span class="font-bold flex items-center gap-1.5"><span>⛏️</span> ${{name}}</span>
            <span class="font-mono font-extrabold text-indigo-300 bg-black/40 px-2 py-0.5 rounded">+${{base}} pts</span>
          </div>
        `;
      }}
    }}

    function updateView() {{
      const match = tracesData[currentScenarioKey];
      const round = match.rounds[currentRoundIndex];
      const totalRounds = match.rounds.length;
      const tierNum = round.contract.tier;
      const region = madagascarRegions[tierNum] || {{ name: "Madagascar", code: "MADA" }};

      // 1. Placar Global & Status da Partida
      document.getElementById('banker-score').innerText = round.banker_score;
      document.getElementById('intern-score').innerText = round.intern_score;
      document.getElementById('round-badge').innerText = `Rodada ${{round.round_num}} de ${{totalRounds}}`;
      document.getElementById('step-indicator').innerText = `Visualizando Rodada ${{round.round_num}} de ${{totalRounds}} • Tier ${{tierNum}}`;

      const statusBanner = document.getElementById('game-status-banner');
      if (currentRoundIndex === totalRounds - 1) {{
        const isBankerWin = match.final_winner.includes('Banqueiro');
        statusBanner.className = isBankerWin 
          ? 'text-xs text-center py-2.5 px-4 rounded-xl font-extrabold bg-blue-950/90 text-blue-300 border border-blue-600 glow-emerald uppercase tracking-wider' 
          : 'text-xs text-center py-2.5 px-4 rounded-xl font-extrabold bg-red-950/90 text-red-300 border border-red-600 glow-terracota uppercase tracking-wider';
        statusBanner.innerText = `🏆 Fim de Jogo: ${{match.final_winner}} Venceu (${{match.final_score}})`;
      }} else {{
        statusBanner.className = 'text-xs text-center py-2.5 px-4 rounded-xl font-bold bg-[#142232] text-slate-300 border border-[#24394f] uppercase tracking-wider';
        statusBanner.innerText = '🚢 Operações em Andamento no Canal de Moçambique';
      }}

      // 2. Stepper Geográfico de Madagascar
      const stepper = document.getElementById('timeline-stepper');
      stepper.innerHTML = '';
      match.rounds.forEach((r, idx) => {{
        const isActive = idx === currentRoundIndex;
        const isSuccess = r.is_success;
        const rTier = r.contract.tier;
        const rReg = madagascarRegions[rTier] || {{ code: `T${{rTier}}` }};

        let btnStyle = isActive 
          ? 'ring-2 ring-amber-400 bg-gradient-to-b from-[#1c3046] to-[#122030] border-[#e06d44]' 
          : 'bg-[#0a1520]/80 hover:bg-[#142334] border-[#1f3144]';
        let statusDot = isSuccess ? 'bg-emerald-400 shadow-[0_0_8px_#10b981]' : 'bg-red-500 shadow-[0_0_8px_#ef4444]';

        stepper.innerHTML += `
          <button onclick="setRound(${{idx}})" class="${{btnStyle}} border rounded-2xl p-2.5 flex flex-col items-center justify-between transition-all transform hover:-translate-y-0.5 shadow-sm">
            <span class="text-[10px] text-slate-400 font-bold font-mono">R${{r.round_num}}</span>
            <div class="w-3 h-3 rounded-full ${{statusDot}} my-1.5"></div>
            <span class="text-[9px] font-extrabold text-amber-300/90 tracking-tight truncate max-w-[50px]">${{rReg.code}}</span>
          </button>
        `;
      }});

      // 3. Contrato da Rodada Ativa
      document.getElementById('tier-badge').innerText = `Tier ${{tierNum}}`;
      document.getElementById('region-badge').innerText = region.name;
      document.getElementById('contract-name').innerText = round.contract.name;
      document.getElementById('contract-desc').innerText = `Comitê de ${{round.contract.committee_size}} operadores • Meta: ${{round.contract.target}} pontos de liquidez • Custo: ${{round.contract.cost_per_player}} carta(s) por membro`;

      const outcomePill = document.getElementById('outcome-pill');
      if (round.is_success) {{
        outcomePill.className = 'px-5 py-2 rounded-2xl font-extrabold text-xs uppercase tracking-wider flex items-center gap-2 bg-emerald-950/80 text-emerald-300 border border-emerald-500 glow-emerald';
        outcomePill.innerHTML = '<span>✅</span> CONTRATO APROVADO';
      }} else {{
        outcomePill.className = 'px-5 py-2 rounded-2xl font-extrabold text-xs uppercase tracking-wider flex items-center gap-2 bg-red-950/80 text-red-300 border border-red-500 glow-terracota';
        outcomePill.innerHTML = '<span>❌</span> CONTRATO SABOTADO';
      }}

      document.getElementById('total-score-val').innerText = `${{round.total_value}} / ${{round.contract.target}} pts`;
      document.getElementById('req-commodity-val').innerText = round.contract.req_commodity ? `${{round.contract.req_commodity}} (x${{round.contract.req_count}})` : 'Livre (Arbitragem)';
      document.getElementById('tokens-used-val').innerText = `${{round.total_tokens_spent}} 🪙 Ariary`;
      document.getElementById('chair-val').innerText = `Operador ${{round.chair_id}}`;

      // 4. Card da Diretriz Regulatória (DLC)
      const directiveContainer = document.getElementById('directive-card-container');
      if (round.directive) {{
        directiveContainer.innerHTML = `
          <div class="bg-gradient-to-r from-amber-950/50 via-[#1f160e]/70 to-[#0f1b29]/80 border border-amber-600/40 rounded-2xl p-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-3">
            <div class="flex items-center gap-3">
              <span class="text-2xl p-2 bg-amber-500/20 rounded-xl border border-amber-500/30">📜</span>
              <div>
                <div class="flex items-center gap-2">
                  <span class="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                    Diretriz Regulatória Ativa (${{round.directive.category}})
                  </span>
                </div>
                <h4 class="text-sm font-extrabold text-white mt-0.5">${{round.directive.name}}</h4>
              </div>
            </div>
            <span class="text-[11px] text-amber-200/80 italic bg-black/40 px-3 py-1.5 rounded-xl border border-amber-800/40">
              Decreto Oficial de Conformidade
            </span>
          </div>
        `;
      }} else {{
        directiveContainer.innerHTML = `
          <div class="bg-[#0a1420]/60 border border-[#1e2f42] rounded-2xl p-3 text-xs text-slate-400 flex items-center justify-between">
            <span class="flex items-center gap-2"><span>🏛️</span> <strong>Sessão Ordinária de Conselho:</strong> Regras clássicas de dedução e governança (Dado 1d6 inerte nesta rodada).</span>
            <span class="text-[10px] font-mono text-slate-500">Sem Evento</span>
          </div>
        `;
      }}

      // 5. Cartas Depositadas no Cofre
      const submittedGrid = document.getElementById('submitted-cards-grid');
      submittedGrid.innerHTML = '';
      round.submitted.forEach(sub => {{
        const isBanker = match.banker_ids.includes(sub.player_id);
        const roleLabel = isBanker ? 'Banqueiro' : 'Estagiário';
        const roleBadge = isBanker ? 'bg-blue-900/60 text-blue-300 border-blue-700/40' : 'bg-red-900/60 text-red-300 border-red-700/40';
        const isSupplier = sub.is_req_responsible ? '<span class="text-[10px] bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded-full border border-amber-500/40 font-bold">Fornecedor Designado</span>' : '';

        let cardsHtml = '';
        sub.cards.forEach(c => {{
          cardsHtml += formatCardBadge(c);
        }});

        submittedGrid.innerHTML += `
          <div class="bg-gradient-to-b from-[#0e1b29]/90 to-[#08121d]/90 border border-[#23384c] rounded-2xl p-4 space-y-3 shadow-md">
            <div class="flex justify-between items-center">
              <div class="flex items-center gap-2">
                <span class="font-extrabold text-sm text-white">Operador ${{sub.player_id}}</span>
                <span class="text-[10px] px-2 py-0.5 rounded-full border font-bold ${{roleBadge}}">${{roleLabel}}</span>
                ${{isSupplier}}
              </div>
              <span class="text-xs text-amber-300 font-extrabold font-mono bg-amber-950/60 px-2 py-0.5 rounded border border-amber-700/40">
                ${{sub.tokens_spent > 0 ? '+' + sub.tokens_spent + ' 🪙 MGA' : '0 🪙'}}
              </span>
            </div>
            <div class="space-y-1.5">
              ${{cardsHtml}}
            </div>
          </div>
        `;
      }});

      // 6. Carteiras dos Jogadores
      const handsGrid = document.getElementById('players-hands-grid');
      handsGrid.innerHTML = '';
      match.players.forEach(p => {{
        const inComm = round.committee.includes(p.id);
        const pHand = round.hands_before[p.id];
        const pTheme = playerThemes[p.id % playerThemes.length];
        const cardBorder = inComm 
          ? 'border-amber-500/60 bg-gradient-to-b from-[#18283a] to-[#0c1824]' 
          : 'border-[#1f3144] bg-[#09131d]/70';

        let cardsMiniHtml = '';
        pHand.cards.forEach(c => {{
          const isToxic = c.type === 'TOXIC';
          const badgeClass = isToxic 
            ? 'bg-red-950/80 text-red-300 border border-red-800/50' 
            : 'bg-[#121f2e] text-slate-300 border border-[#233547]';

          cardsMiniHtml += `
            <div class="text-[10px] py-1 px-2 rounded-lg ${{badgeClass}} flex justify-between items-center font-medium">
              <span class="truncate">${{c.name.split(' ')[0]}}</span>
              <span class="font-mono font-bold">${{c.base > 0 ? '+' + c.base : c.base}}</span>
            </div>
          `;
        }});

        handsGrid.innerHTML += `
          <div class="${{cardBorder}} border rounded-2xl p-3.5 space-y-2.5 transition-all shadow-sm">
            <div class="flex justify-between items-center">
              <span class="font-extrabold text-xs text-white flex items-center gap-1">
                <span class="w-2 h-2 rounded-full" style="background: ${{pTheme.color}}"></span>
                Op ${{p.id}}
              </span>
              <span class="text-[10px] text-amber-300 font-extrabold bg-amber-950/70 px-2 py-0.5 rounded-full border border-amber-700/50 font-mono">
                ${{pHand.tokens}} 🪙
              </span>
            </div>
            <div class="space-y-1">
              ${{cardsMiniHtml}}
            </div>
            ${{inComm ? '<div class="text-[9px] text-center text-amber-300/90 font-bold bg-amber-950/40 py-0.5 rounded border border-amber-800/30">NO COMITÊ</div>' : '<div class="text-[9px] text-center text-emerald-300/90 font-bold bg-emerald-950/40 py-0.5 rounded border border-emerald-800/30">NO BANCO</div>'}}
          </div>
        `;
      }});

      // 7. Gabarito de Roster
      const rosterList = document.getElementById('roster-list');
      rosterList.innerHTML = '';
      match.players.forEach(p => {{
        const isBanker = match.banker_ids.includes(p.id);
        const badge = isBanker 
          ? 'bg-blue-900/40 text-blue-300 border-blue-700/60' 
          : 'bg-red-900/40 text-red-300 border-red-700/60';
        rosterList.innerHTML += `
          <div class="flex justify-between items-center py-1.5 border-b border-[#1f3144]">
            <span class="font-bold text-white flex items-center gap-1.5">
              <span>${{isBanker ? '🏛️' : '🕵️'}}</span> Operador ${{p.id}}
            </span>
            <span class="text-[10px] px-2.5 py-0.5 rounded-full border font-extrabold ${{badge}} uppercase">${{p.role}}</span>
          </div>
        `;
      }});

      // 8. Radar de Suspeita
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
        const pTheme = playerThemes[p.id % playerThemes.length];

        let barColor = 'bg-blue-500';
        let tagStatus = '';

        if (currentPerspective !== 'avg' && parseInt(currentPerspective) === p.id) {{
          tagStatus = '<span class="text-[10px] text-blue-300 font-extrabold bg-blue-950/80 px-2 py-0.5 rounded border border-blue-600">EU MESMO</span>';
          barColor = 'bg-blue-500';
        }} else if (susVal >= 0.85) {{
          tagStatus = '<span class="text-[10px] text-red-300 font-extrabold bg-red-950/80 px-2 py-0.5 rounded border border-red-600 glow-terracota">💥 TRAIDOR CONFIRMADO</span>';
          barColor = 'bg-gradient-to-r from-red-600 to-red-500';
        }} else if (susVal >= 0.50) {{
          tagStatus = '<span class="text-[10px] text-amber-300 font-bold bg-amber-950/80 px-2 py-0.5 rounded border border-amber-600">⚠️ SUSPEITO</span>';
          barColor = 'bg-gradient-to-r from-amber-600 to-amber-500';
        }} else if (susVal <= 0.20) {{
          tagStatus = '<span class="text-[10px] text-emerald-300 font-bold bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-600 glow-emerald">🛡️ AUDITADO & IDÔNEO</span>';
          barColor = 'bg-gradient-to-r from-emerald-600 to-emerald-500';
        }} else {{
          tagStatus = '<span class="text-[10px] text-slate-400 bg-slate-800 px-2 py-0.5 rounded">NEUTRO</span>';
          barColor = 'bg-slate-500';
        }}

        container.innerHTML += `
          <div class="space-y-1.5 text-xs bg-[#0a1420]/60 p-2.5 rounded-xl border border-[#1f3144]">
            <div class="flex justify-between items-center">
              <div class="flex items-center gap-2">
                <span class="font-extrabold" style="color: ${{pTheme.color}}">Op ${{p.id}}</span>
                <span class="text-[10px] text-slate-400">(${{isBanker ? 'Banqueiro' : 'Estagiário'}})</span>
                ${{tagStatus}}
              </div>
              <span class="font-mono font-extrabold text-white">${{(susVal * 100).toFixed(0)}}%</span>
            </div>
            <div class="w-full bg-[#12202e] h-2 rounded-full overflow-hidden">
              <div class="${{barColor}} h-full transition-all duration-500 rounded-full" style="width: ${{Math.min(100, Math.max(0, susVal * 100))}}%"></div>
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

    artifact_dir = r'C:\Users\najoa\.gemini\antigravity-ide\brain\83d1a824-37b7-437a-9fef-843634e7e21c'
    artifact_path = os.path.join(artifact_dir, 'match_visualizer.html')
    if os.path.exists(artifact_dir):
        with open(artifact_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    print(f"Dashboard v14.0 gerado com sucesso em: {local_html_path}")
    print(f"Artefato sincronizado em: {artifact_path}")


if __name__ == '__main__':
    generate_dashboard()
