# -*- coding: utf-8 -*-
"""
Reconstrói o match_visualizer.html puramente como VISUALIZADOR DE TRACES SIMULADOS,
com a identidade visual cartoon do deserto (monólito com arco + Joshua tree),
e um botão de destaque para abrir o jogo interativo (game.html).
"""

import json
import os

def build_pure_visualizer():
    traces_path = os.path.join(os.path.dirname(__file__), 'data', 'game_traces.json')
    with open(traces_path, 'r', encoding='utf-8') as f:
        traces_data = json.load(f)

    traces_json_str = json.dumps(traces_data, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BTG Madagascar • Auditoria de Simulação & Traces Monte Carlo</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&family=JetBrains+Mono:wght@600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --ink: #2b180d;
      --sand-bg: #f9f3e6;
      --sand-card: #fffdf8;
      --sand-accent: #e29547;
      --joshua-green: #2d6a4f;
      --sky-blue: #0284c7;
      --desert-gold: #f59e0b;
    }}
    
    body {{
      font-family: 'Plus Jakarta Sans', sans-serif;
      background: linear-gradient(180deg, #38bdf8 0px, #bae6fd 140px, #fde68a 320px, #fdf6ea 520px, #f5ecd7 100%);
      background-attachment: fixed;
      color: #2b180d;
      min-height: 100vh;
    }}

    .font-cartoon {{
      font-family: 'Fredoka', cursive, sans-serif;
    }}

    /* Card com borda cartoon espessa e sombra rígida tátil */
    .cartoon-card {{
      background: #fffdf8;
      border: 3.5px solid #2b180d;
      border-radius: 28px;
      box-shadow: 0 8px 0 #2b180d, 0 16px 26px rgba(43, 24, 13, 0.12);
      transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}

    .cartoon-card-subtle {{
      background: #fbf6ec;
      border: 2.5px solid #2b180d;
      border-radius: 20px;
      box-shadow: 0 4px 0 #2b180d;
    }}

    /* Botões táteis que afundam com o clique */
    .cartoon-btn {{
      font-family: 'Fredoka', cursive, sans-serif;
      font-weight: 700;
      border: 3px solid #2b180d;
      border-radius: 18px;
      box-shadow: 0 5px 0 #2b180d;
      transition: all 0.12s cubic-bezier(0.34, 1.56, 0.64, 1);
      user-select: none;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      text-decoration: none;
    }}
    .cartoon-btn:hover {{
      transform: translateY(-2px);
      box-shadow: 0 7px 0 #2b180d;
    }}
    .cartoon-btn:active {{
      transform: translateY(4px);
      box-shadow: 0 1px 0 #2b180d;
    }}

    /* Carimbos oficiais APROVADO / SABOTADO */
    .stamp-approved {{
      font-family: 'Fredoka', cursive, sans-serif;
      font-weight: 700;
      letter-spacing: 0.06em;
      border: 3.5px dashed #059669;
      color: #065f46;
      background: #ecfdf5;
      box-shadow: 0 4px 0 #059669;
      transform: rotate(-2deg);
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    
    .stamp-sabotaged {{
      font-family: 'Fredoka', cursive, sans-serif;
      font-weight: 700;
      letter-spacing: 0.06em;
      border: 3.5px dashed #dc2626;
      color: #991b1b;
      background: #fef2f2;
      box-shadow: 0 4px 0 #dc2626;
      transform: rotate(2deg);
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}

    /* Moeda cartoon de Ariary com relevo dourado */
    .coin-badge {{
      background: linear-gradient(180deg, #fef08a 0%, #f59e0b 100%);
      border: 2px solid #854d0e;
      color: #78350f;
      font-family: 'Fredoka', cursive, sans-serif;
      font-weight: 700;
      box-shadow: 0 2.5px 0 #854d0e;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}

    /* Scrollbar */
    ::-webkit-scrollbar {{
      width: 10px;
      height: 10px;
    }}
    ::-webkit-scrollbar-track {{
      background: #f5ecd7;
    }}
    ::-webkit-scrollbar-thumb {{
      background: #d4a373;
      border: 2px solid #2b180d;
      border-radius: 9999px;
    }}
  </style>
</head>
<body class="p-3 md:p-8 antialiased">

  <div class="max-w-7xl mx-auto space-y-7">

    <!-- BARRA SUPERIOR DE NAVEGAÇÃO -->
    <div class="flex flex-col sm:flex-row justify-between items-center gap-4 bg-white/95 border-[3.5px] border-[#2b180d] p-3 md:p-4 rounded-3xl shadow-[0_6px_0_#2b180d]">
      <div class="flex items-center gap-3">
        <span class="text-2xl p-2 bg-[#fef3c7] rounded-2xl border-2 border-[#b45309]">🇲🇬</span>
        <div>
          <span class="text-[11px] font-cartoon font-bold text-[#8c4314] uppercase tracking-wider">BTG Pactual • Ilha de Madagascar</span>
          <h3 class="font-cartoon text-lg md:text-xl font-bold text-[#2b180d]">Visualizador de Partidas Simuladas (Traces v14.0)</h3>
        </div>
      </div>

      <!-- BOTÃO PARA ABRIR O JOGO INTERATIVO -->
      <div class="flex items-center gap-3">
        <a href="game.html" class="cartoon-btn px-6 py-2.5 bg-[#fde047] hover:bg-[#facc15] text-[#451a03] text-sm flex items-center gap-2">
          <span>🎮</span> JOGAR PARTIDA INTERATIVA (game.html) ➔
        </a>
      </div>
    </div>

    <!-- BANNER HERO COM ILUSTRAÇÃO CARTOON DO DESERTO (MONÓLITO DE ARENITO COM ARCO + JOSHUA TREE) -->
    <header class="cartoon-card overflow-hidden relative">
      <div class="w-full h-44 md:h-52 relative bg-gradient-to-b from-[#38bdf8] via-[#7dd3fc] to-[#fde68a] overflow-hidden border-b-[3.5px] border-[#2b180d]">
        
        <!-- Sol Cartoon -->
        <div class="absolute top-4 right-16 w-20 h-20 bg-[#fde047] border-[3px] border-[#2b180d] rounded-full shadow-[0_0_24px_rgba(253,224,71,0.7)] flex items-center justify-center">
          <div class="w-14 h-14 bg-[#fef08a] rounded-full"></div>
        </div>

        <!-- Nuvens Cartoon -->
        <div class="absolute top-6 left-12 flex items-center opacity-90 pointer-events-none">
          <div class="w-16 h-8 bg-white border-[2.5px] border-[#2b180d] rounded-full"></div>
          <div class="w-10 h-10 bg-white border-[2.5px] border-[#2b180d] rounded-full -ml-4 -mt-2"></div>
          <div class="w-14 h-8 bg-white border-[2.5px] border-[#2b180d] rounded-full -ml-4"></div>
        </div>

        <!-- SVG da Paisagem: Monólito com Arco + Joshua Tree + Dunas -->
        <svg class="absolute bottom-0 w-full h-full pointer-events-none" viewBox="0 0 1200 240" fill="none" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
          <path d="M-50 240 Q180 130 420 180 T900 170 Q1050 140 1250 240 Z" fill="#e9c46a" stroke="#2b180d" stroke-width="3" />
          <path d="M-30 240 Q250 170 560 210 T1250 200 L1250 240 Z" fill="#f4a261" stroke="#2b180d" stroke-width="3" />

          <!-- O MONÓLITO DE ARENITO COM ARCO/CAVERNA -->
          <g id="sandstone-monolith">
            <ellipse cx="230" cy="225" rx="140" ry="16" fill="#c77d40" />
            <path d="M120 230 C110 160 140 30 220 25 C295 20 330 110 340 180 C345 205 340 230 340 230 Z" 
                  fill="#d48b47" stroke="#2b180d" stroke-width="4" stroke-linejoin="round" />
            <path d="M150 210 C145 150 165 50 220 40 C265 40 290 100 300 160" 
                  stroke="#eeb979" stroke-width="6" stroke-linecap="round" fill="none" opacity="0.8" />
            <path d="M220 50 Q215 100 230 145" stroke="#8c4314" stroke-width="3" stroke-linecap="round" fill="none" />
            <path d="M260 90 Q270 130 255 160" stroke="#8c4314" stroke-width="2.5" stroke-linecap="round" fill="none" />
            <circle cx="270" cy="180" r="10" fill="#a0521e" stroke="#2b180d" stroke-width="2" />
            <!-- Abertura em Arco da Foto -->
            <path d="M155 230 C155 195 180 165 195 165 C210 165 235 195 235 230 Z" 
                  fill="#1f140d" stroke="#2b180d" stroke-width="3.5" />
            <path d="M165 230 C165 205 185 180 195 180 C205 180 225 205 225 230 Z" 
                  fill="#0c0704" />
            <ellipse cx="130" cy="226" rx="14" ry="7" fill="#b06830" stroke="#2b180d" stroke-width="2" />
            <ellipse cx="250" cy="227" rx="16" ry="8" fill="#945322" stroke="#2b180d" stroke-width="2.5" />
            <ellipse cx="280" cy="229" rx="12" ry="6" fill="#b06830" stroke="#2b180d" stroke-width="2" />
          </g>

          <!-- JOSHUA TREE COM POMPONS ESPINHOSOS -->
          <g id="joshua-tree" transform="translate(930, 20)">
            <ellipse cx="80" cy="210" rx="35" ry="8" fill="#b06830" stroke="#2b180d" stroke-width="2" />
            <path d="M75 210 L82 125 L65 75 L62 45 M82 125 L110 85 L125 50 M72 100 L45 75 L35 50" 
                  stroke="#5c3d2e" stroke-width="9" stroke-linecap="round" stroke-linejoin="round" />
            <path d="M75 210 L82 125 L65 75 L62 45 M82 125 L110 85 L125 50 M72 100 L45 75 L35 50" 
                  stroke="#8c5836" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" />
            <!-- Pompons de Folhagem Pontiaguda -->
            <g transform="translate(60, 42)">
              <circle cx="0" cy="0" r="18" fill="#1e4d38" stroke="#2b180d" stroke-width="2.5" />
              <circle cx="-5" cy="-5" r="8" fill="#2d6a4f" />
              <path d="M-15 -5 L-25 -8 M-12 -15 L-20 -22 M0 -18 L0 -28 M12 -15 L20 -22 M15 -5 L25 -8" stroke="#1e4d38" stroke-width="3" stroke-linecap="round" />
            </g>
            <g transform="translate(125, 48)">
              <circle cx="0" cy="0" r="16" fill="#1e4d38" stroke="#2b180d" stroke-width="2.5" />
              <circle cx="-3" cy="-4" r="7" fill="#2d6a4f" />
              <path d="M-12 -12 L-18 -18 M0 -15 L0 -24 M12 -12 L18 -18 M14 -2 L22 -4" stroke="#1e4d38" stroke-width="3" stroke-linecap="round" />
            </g>
            <g transform="translate(35, 48)">
              <circle cx="0" cy="0" r="15" fill="#1e4d38" stroke="#2b180d" stroke-width="2.5" />
              <circle cx="-3" cy="-3" r="6" fill="#2d6a4f" />
              <path d="M-12 -12 L-18 -18 M0 -15 L0 -22 M-14 -2 L-22 -4" stroke="#1e4d38" stroke-width="3" stroke-linecap="round" />
            </g>
            <g transform="translate(65, 75)">
              <circle cx="0" cy="0" r="12" fill="#2d6a4f" stroke="#2b180d" stroke-width="2" />
            </g>
          </g>

          <!-- Arbustos do Deserto e Pedrinhas -->
          <g id="desert-bushes">
            <ellipse cx="480" cy="225" rx="22" ry="12" fill="#3a5a40" stroke="#2b180d" stroke-width="2" />
            <ellipse cx="680" cy="228" rx="18" ry="10" fill="#588157" stroke="#2b180d" stroke-width="2" />
            <circle cx="750" cy="230" r="6" fill="#c77d40" stroke="#2b180d" stroke-width="1.5" />
            <circle cx="762" cy="232" r="4" fill="#a0521e" stroke="#2b180d" stroke-width="1.5" />
          </g>
        </svg>

        <!-- Selo de Marca Cartoon -->
        <div class="absolute bottom-3 left-6 z-10 flex items-center gap-3 bg-white/90 border-[2.5px] border-[#2b180d] px-4 py-1.5 rounded-2xl shadow-[0_4px_0_#2b180d]">
          <span class="text-xl">🏜️</span>
          <div>
            <span class="text-[10px] font-cartoon font-bold text-[#8c4314] tracking-wider uppercase">Ambiente de Testes Monte Carlo</span>
            <h4 class="font-cartoon text-xs md:text-sm font-bold text-[#2b180d]">Reserva Natural de Isalo • Madagascar</h4>
          </div>
        </div>
      </div>
    </header>

    <!-- CONTEÚDO PRINCIPAL DO VISUALIZADOR DE TRACES -->
    <div class="space-y-7">
      
      <!-- CONTROLES DO VISUALIZADOR (SELETOR DE CENÁRIO) -->
      <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white p-5 rounded-3xl border-[3.5px] border-[#2b180d] shadow-[0_6px_0_#2b180d]">
        <div>
          <span class="text-xs font-cartoon font-bold text-[#b45309] uppercase tracking-wider">🔬 Auditoria Causal de Comportamento</span>
          <h2 class="text-2xl md:text-3xl font-cartoon font-bold text-[#2b180d]">Terminal de Auditoria dos 5 Perfis de IA</h2>
          <p class="text-xs md:text-sm text-[#6b472e] max-w-2xl font-medium">Inspecione partidas simuladas completas geradas pelo motor Monte Carlo, analisando a dedução bayesiana e o comportamento de infiltração.</p>
        </div>

        <div class="cartoon-card-subtle p-4 space-y-2 min-w-[290px] w-full md:w-auto bg-[#fef8ed]">
          <div class="flex justify-between items-center">
            <label class="text-xs font-cartoon font-bold text-[#b45309] uppercase tracking-wider flex items-center gap-1.5">
              <span>🎯</span> Cenário de Auditoria:
            </label>
            <span class="text-[10px] font-cartoon font-bold text-[#78350f] bg-[#fde68a] px-2 py-0.5 rounded-full border border-[#b45309]">5 Perfis</span>
          </div>
          <select id="scenario-select" onchange="changeScenario(this.value)" class="w-full bg-white border-[2.5px] border-[#2b180d] text-[#2b180d] text-xs font-bold rounded-xl px-3 py-2.5 shadow-[0_3px_0_#2b180d] focus:outline-none focus:ring-2 focus:ring-[#e29547] transition-all cursor-pointer">
            <option value="sleeper_game">🎭 Sleeper Estratégico (Infiltração em Toamasina)</option>
            <option value="aggressive_game">⚔️ Agressivo (Blefe Imediato na Costa de Sava)</option>
            <option value="hedge_game">🛡️ Hedge Econômico (Retenção em Ilakaka)</option>
            <option value="opportunist_game">🦎 Oportunista (Camaleão das Terras Altas)</option>
            <option value="technician_game">🔬 Técnico (Fraude Cirúrgica / Falsa Idoneidade)</option>
          </select>
        </div>
      </div>

      <!-- PLACAR SOBERANO & STEPPER DO VISUALIZADOR -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-7">
        <div class="lg:col-span-4 cartoon-card p-6 flex flex-col justify-between bg-gradient-to-b from-[#fffdf9] to-[#faf1dc]">
          <div>
            <div class="flex justify-between items-center pb-3 border-b-2 border-[#2b180d]/20">
              <span class="text-xs font-cartoon font-bold text-[#78350f] uppercase tracking-wider flex items-center gap-1.5">
                <span>🏛️</span> Conselho vs Infiltrados
              </span>
              <span id="round-badge" class="text-xs font-cartoon bg-[#e29547] text-white font-bold px-3 py-0.5 rounded-full border-2 border-[#2b180d]">
                R1 de 7
              </span>
            </div>
            <div class="grid grid-cols-2 gap-4 my-5 text-center">
              <div class="bg-gradient-to-b from-[#e0f2fe] to-[#bae6fd] rounded-2xl p-4 border-[2.5px] border-[#0284c7] shadow-[0_4px_0_#0284c7]">
                <div class="text-xs font-cartoon text-[#0369a1] font-bold uppercase">🏛️ Banqueiros</div>
                <div id="banker-score" class="text-5xl font-cartoon font-bold text-[#0284c7] mt-1">0</div>
                <div class="text-[10px] font-bold text-[#075985] mt-1 bg-white/70 py-0.5 rounded-full border border-[#0284c7]/40">Meta: 4 Contratos</div>
              </div>
              <div class="bg-gradient-to-b from-[#ffe4e6] to-[#fecdd3] rounded-2xl p-4 border-[2.5px] border-[#e11d48] shadow-[0_4px_0_#e11d48]">
                <div class="text-xs font-cartoon text-[#9f1239] font-bold uppercase">🕵️ Estagiários</div>
                <div id="intern-score" class="text-5xl font-cartoon font-bold text-[#e11d48] mt-1">0</div>
                <div class="text-[10px] font-bold text-[#881337] mt-1 bg-white/70 py-0.5 rounded-full border border-[#e11d48]/40">Meta: 4 Sabotagens</div>
              </div>
            </div>
          </div>
          <div id="game-status-banner" class="text-xs text-center py-2.5 px-4 rounded-xl font-cartoon font-bold border-2 border-[#2b180d] shadow-[0_3px_0_#2b180d]">
            Partida em Andamento
          </div>
        </div>

        <div class="lg:col-span-8 cartoon-card p-6 flex flex-col justify-between bg-[#fffdf9]">
          <div>
            <div class="flex justify-between items-center pb-3 border-b-2 border-[#2b180d]/20">
              <span class="text-xs font-cartoon font-bold text-[#2b180d] uppercase tracking-wider flex items-center gap-2">
                <span>📍</span> Rota de Expansão em Madagascar (Tiers 1 a 7)
              </span>
              <span class="text-xs font-cartoon font-bold text-[#b45309]">Clique no posto para avançar</span>
            </div>
            <div id="timeline-stepper" class="grid grid-cols-7 gap-2.5 my-5">
              <!-- Injetado via JS -->
            </div>
          </div>
          <div class="flex justify-between items-center pt-3 border-t-2 border-[#2b180d]/20">
            <button onclick="prevRound()" class="cartoon-btn px-4 py-2 bg-[#fef3c7] hover:bg-[#fde68a] text-xs text-[#78350f] flex items-center gap-1.5">
              <span>◀</span> Rodada Anterior
            </button>
            <span id="step-indicator" class="text-xs font-cartoon font-bold text-[#8c4314]">Rodada 1 de 7</span>
            <button onclick="nextRound()" class="cartoon-btn px-4 py-2 bg-[#fef3c7] hover:bg-[#fde68a] text-xs text-[#78350f] flex items-center gap-1.5">
              Próxima Rodada <span>▶</span>
            </button>
          </div>
        </div>
      </div>

      <!-- DETALHE DO CONTRATO REGIONAL & COFRE DO VISUALIZADOR -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-7">
        <div class="lg:col-span-8 space-y-7">
          <div class="cartoon-card p-6 md:p-8 space-y-6 bg-gradient-to-b from-[#fffefc] to-[#fbf5e7]">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div>
                <div class="flex flex-wrap items-center gap-2">
                  <span id="tier-badge" class="bg-[#e29547] text-white text-xs font-cartoon font-bold px-3 py-0.5 rounded-full border-2 border-[#2b180d]">Tier 1</span>
                  <span id="region-badge" class="bg-[#dcfce7] text-[#166534] text-xs font-cartoon font-bold px-3 py-0.5 rounded-full border-2 border-[#15803d]">🌿 Sava</span>
                </div>
                <h2 id="contract-name" class="text-2xl md:text-3xl font-cartoon font-bold text-[#2b180d] mt-2 tracking-tight">Exportação de Baunilha</h2>
                <p id="contract-desc" class="text-xs text-[#6b472e] mt-1 font-medium">Comitê de 2 membros • Meta: 4 pts</p>
              </div>
              <div id="outcome-pill" class="px-5 py-2 rounded-2xl"><span>APROVADO</span></div>
            </div>

            <div class="grid grid-cols-2 md:grid-cols-4 gap-3 pt-2">
              <div class="cartoon-card-subtle p-3.5 bg-white text-center">
                <div class="text-[10px] font-cartoon text-[#8c4314] uppercase font-bold">Pontuação Obtida</div>
                <div id="total-score-val" class="text-xl font-cartoon font-bold text-[#2b180d] mt-0.5">5 / 4 pts</div>
              </div>
              <div class="cartoon-card-subtle p-3.5 bg-white text-center">
                <div class="text-[10px] font-cartoon text-[#8c4314] uppercase font-bold">Insumo Exigido</div>
                <div id="req-commodity-val" class="text-xs font-cartoon font-bold text-[#d97706] mt-1">Baunilha (x1)</div>
              </div>
              <div class="cartoon-card-subtle p-3.5 bg-white text-center">
                <div class="text-[10px] font-cartoon text-[#8c4314] uppercase font-bold">Insumo Entregue?</div>
                <div id="commodity-delivered-val" class="text-xs font-cartoon font-bold text-[#059669] mt-1">✅ Sim</div>
              </div>
              <div class="cartoon-card-subtle p-3.5 bg-white text-center">
                <div class="text-[10px] font-cartoon text-[#8c4314] uppercase font-bold">Queima de Moedas</div>
                <div id="tokens-spent-val" class="text-xs font-cartoon font-bold text-[#b45309] mt-1">0 🪙 Ariary</div>
              </div>
            </div>

            <!-- Diretiva Regulatória da Rodada -->
            <div id="directive-container">
              <!-- Injetado via JS -->
            </div>

            <!-- Cartas Depositadas no Cofre Secreto -->
            <div class="space-y-3 pt-2">
              <div class="flex justify-between items-center">
                <span class="text-xs font-cartoon font-bold text-[#2b180d] uppercase tracking-wider flex items-center gap-1.5">
                  <span>🗳️</span> Cartas Depositadas no Cofre do Banco
                </span>
                <span class="text-[11px] font-cartoon text-[#8c4314] bg-[#fef3c7] px-2.5 py-0.5 rounded-full border border-[#b45309]">Sigilo Quebrado</span>
              </div>
              <div id="submitted-cards-grid" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                <!-- Injetado via JS -->
              </div>
            </div>

            <!-- Votação de Governança -->
            <div class="space-y-3 pt-2 border-t-2 border-[#2b180d]/15">
              <span class="text-xs font-cartoon font-bold text-[#2b180d] uppercase tracking-wider flex items-center gap-1.5">
                <span>🗳️</span> Votos da Mesa de Governança
              </span>
              <div id="votes-row" class="grid grid-cols-5 gap-2">
                <!-- Injetado via JS -->
              </div>
            </div>
          </div>

          <!-- MÃOS SECRETAS DE CADA OPERADOR ANTES DA RODADA -->
          <div class="cartoon-card p-6 md:p-8 space-y-4 bg-white">
            <div class="flex justify-between items-center pb-2 border-b-2 border-[#2b180d]/15">
              <div>
                <span class="text-xs font-cartoon font-bold text-[#b45309] uppercase tracking-wider flex items-center gap-1.5">
                  <span>🗂️</span> Carteiras Privadas dos 5 Operadores
                </span>
                <h3 class="font-cartoon text-lg font-bold text-[#2b180d]">Composição de Mão Pré-Expedição</h3>
              </div>
              <span class="text-[11px] text-[#6b472e] bg-[#fbf5e7] px-3 py-1 rounded-full border border-[#2b180d]/20 font-medium">Snapshot do Motor</span>
            </div>
            <div id="players-hands-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 pt-2">
              <!-- Injetado via JS -->
            </div>
          </div>
        </div>

        <!-- RADAR BAYESIANO & ROSTER -->
        <div class="lg:col-span-4 space-y-7">
          
          <!-- Radar de Suspeição Bayesiana -->
          <div class="cartoon-card p-6 space-y-5 bg-white">
            <div class="flex justify-between items-start pb-2 border-b-2 border-[#2b180d]/15">
              <div>
                <span class="text-xs font-cartoon font-bold text-[#dc2626] uppercase tracking-wider flex items-center gap-1.5">
                  <span>🧠</span> Motor Bayesiano
                </span>
                <h3 class="font-cartoon text-lg font-bold text-[#2b180d]">Termômetro de Infiltração</h3>
              </div>
              <span class="text-xl">🕵️</span>
            </div>

            <!-- Seletor de Perspectiva de Banqueiro -->
            <div class="cartoon-card-subtle p-3 space-y-1.5 bg-[#fef8ed]">
              <label class="text-[10px] font-cartoon font-bold text-[#8c4314] uppercase">Perspectiva do Observador:</label>
              <select id="banker-perspective-select" onchange="changePerspective(this.value)" class="w-full bg-white border-2 border-[#2b180d] text-[#2b180d] text-xs font-bold rounded-xl px-2.5 py-1.5 shadow-[0_2px_0_#2b180d] focus:outline-none">
                <option value="avg">Média do Banco (Visão Consolidada)</option>
              </select>
            </div>

            <div id="suspicion-bars-container" class="space-y-3.5">
              <!-- Injetado via JS -->
            </div>

            <p class="text-[11px] text-[#8c4314] bg-[#fef3c7] p-3 rounded-2xl border border-[#b45309] leading-relaxed font-medium">
              💡 <strong>Regra de Bayes:</strong> Operadores que não entregam o insumo prometido ou acumulam moedas sobem bruscamente no termômetro.
            </p>
          </div>

          <!-- Roster da Partida -->
          <div class="cartoon-card p-6 space-y-4 bg-white">
            <div class="flex justify-between items-center pb-2 border-b-2 border-[#2b180d]/15">
              <span class="text-xs font-cartoon font-bold text-[#2b180d] uppercase tracking-wider flex items-center gap-1.5">
                <span>👥</span> Identidades Ocultas
              </span>
              <span class="text-xs font-bold text-[#166534] bg-[#dcfce7] px-2.5 py-0.5 rounded-full border border-[#15803d]">Gabarito</span>
            </div>
            <div id="roster-list" class="space-y-2.5">
              <!-- Injetado via JS -->
            </div>
          </div>
        </div>
      </div>

    </div>

  </div>

  <!-- JAVASCRIPT EXCLUSIVO DO VISUALIZADOR DE TRACES -->
  <script>
    const tracesData = {traces_json_str};

    const regions = [
      {{ tier: 1, name: "Sava", icon: "🌿", color: "bg-emerald-100 text-emerald-900 border-emerald-500" }},
      {{ tier: 2, name: "Analanjirofo", icon: "🌴", color: "bg-teal-100 text-teal-900 border-teal-500" }},
      {{ tier: 3, name: "Atsinanana", icon: "⚓", color: "bg-cyan-100 text-cyan-900 border-cyan-500" }},
      {{ tier: 4, name: "Alaotra-Mangoro", icon: "🌾", color: "bg-amber-100 text-amber-900 border-amber-500" }},
      {{ tier: 5, name: "Analamanga", icon: "🏛️", color: "bg-sky-100 text-sky-900 border-sky-500" }},
      {{ tier: 6, name: "Menabe", icon: "🪵", color: "bg-orange-100 text-orange-900 border-orange-500" }},
      {{ tier: 7, name: "Ihorombe", icon: "💎", color: "bg-rose-100 text-rose-900 border-rose-500" }}
    ];

    const playerThemes = [
      {{ name: "Op 0", color: "#e11d48", bg: "#ffe4e6", border: "#f43f5e" }},
      {{ name: "Op 1", color: "#2563eb", bg: "#dbeafe", border: "#3b82f6" }},
      {{ name: "Op 2", color: "#059669", bg: "#d1fae5", border: "#10b981" }},
      {{ name: "Op 3", color: "#d97706", bg: "#fef3c7", border: "#f59e0b" }},
      {{ name: "Op 4", color: "#7c3aed", bg: "#ede9fe", border: "#8b5cf6" }}
    ];

    let currentScenarioKey = 'sleeper_game';
    let currentRoundIndex = 0;
    let currentPerspective = 'avg';

    function changeScenario(key) {{
      currentScenarioKey = key;
      currentRoundIndex = 0;
      populateBankerPerspectiveSelect();
      updateView();
    }}

    function populateBankerPerspectiveSelect() {{
      const match = tracesData[currentScenarioKey];
      if (!match) return;
      const select = document.getElementById('banker-perspective-select');
      select.innerHTML = '<option value="avg">Média do Banco (Visão Consolidada)</option>';
      match.banker_ids.forEach(bId => {{
        select.innerHTML += `<option value="${{bId}}">Visão do Operador ${{bId}} (Banqueiro Leal)</option>`;
      }});
      currentPerspective = 'avg';
    }}

    function changePerspective(val) {{
      currentPerspective = val;
      renderSuspicionBars();
    }}

    function nextRound() {{
      const match = tracesData[currentScenarioKey];
      if (currentRoundIndex < match.rounds.length - 1) {{
        currentRoundIndex++;
        updateView();
      }}
    }}

    function prevRound() {{
      if (currentRoundIndex > 0) {{
        currentRoundIndex--;
        updateView();
      }}
    }}

    function goToRound(idx) {{
      currentRoundIndex = idx;
      updateView();
    }}

    function formatCardBadge(card) {{
      let style = 'bg-[#fbf6ec] text-[#2b180d] border-[#2b180d]';
      let icon = '📦';
      if (card.type === 'VN') {{
        style = 'bg-amber-100 text-amber-900 border-amber-600';
        icon = '🌾';
      }} else if (card.type === 'SF') {{
        style = 'bg-blue-100 text-blue-900 border-blue-600';
        icon = '💎';
      }} else if (card.type === 'TI') {{
        style = 'bg-slate-200 text-slate-900 border-slate-600';
        icon = '⚙️';
      }} else if (card.type === 'CO') {{
        style = 'bg-indigo-100 text-indigo-900 border-indigo-600';
        icon = '🔩';
      }} else if (card.type === 'WILD') {{
        style = 'bg-yellow-200 text-yellow-950 border-yellow-600';
        icon = '🌟';
      }} else if (card.type === 'TOXIC') {{
        style = 'bg-red-100 text-red-950 border-red-600';
        icon = '☣️';
      }}
      return `
        <div class="flex justify-between items-center text-xs px-2.5 py-1.5 rounded-xl border-2 ${{style}} font-medium">
          <span class="flex items-center gap-1.5"><span>${{icon}}</span> ${{card.name}}</span>
          <span class="font-cartoon font-bold">${{card.base > 0 ? '+' + card.base : card.base}} pts</span>
        </div>
      `;
    }}

    function updateView() {{
      const match = tracesData[currentScenarioKey];
      if (!match) return;
      const round = match.rounds[currentRoundIndex];
      const maxR = match.rounds.length;

      document.getElementById('round-badge').innerText = `R${{round.round_num}} de ${{maxR}}`;
      document.getElementById('banker-score').innerText = round.banker_score;
      document.getElementById('intern-score').innerText = round.intern_score;

      const isOver = currentRoundIndex === maxR - 1;
      const statusBanner = document.getElementById('game-status-banner');
      if (isOver) {{
        const winner = match.final_winner === 'Banqueiro' ? 'VITÓRIA DO CONSELHO BTG' : 'VITÓRIA DOS INFILTRADOS';
        const winColor = match.final_winner === 'Banqueiro' ? 'bg-[#dcfce7] text-[#166534] border-[#15803d]' : 'bg-[#fee2e2] text-[#991b1b] border-[#dc2626]';
        statusBanner.className = `text-xs text-center py-2.5 px-4 rounded-xl font-cartoon font-bold border-2 ${{winColor}} shadow-[0_3px_0_#2b180d]`;
        statusBanner.innerText = `🏆 FIM DE PARTIDA: ${{winner}} (${{match.final_score}})`;
      }} else {{
        statusBanner.className = 'text-xs text-center py-2.5 px-4 rounded-xl font-cartoon font-bold border-2 border-[#2b180d] bg-[#fef3c7] text-[#78350f] shadow-[0_3px_0_#2b180d]';
        statusBanner.innerText = `Rodada ${{round.round_num}} em Execução • Presidente: Op ${{round.chair_id}}`;
      }}

      // Stepper
      const stepper = document.getElementById('timeline-stepper');
      stepper.innerHTML = '';
      for (let i = 1; i <= 7; i++) {{
        const rMatch = match.rounds.find(r => r.round_num === i);
        const reg = regions[i - 1];
        let stateStyle = 'bg-white/60 border-dashed border-[#2b180d]/40 opacity-50';
        let badge = `<span class="text-[9px] font-cartoon font-bold text-[#8c4314]">${{reg.name.substring(0, 4)}}</span>`;

        if (rMatch) {{
          const isPassed = rMatch.is_success;
          const isCurrent = i === round.round_num;
          const bgStatus = isPassed ? 'bg-[#dcfce7] border-[#15803d] text-[#166534]' : 'bg-[#fee2e2] border-[#dc2626] text-[#991b1b]';
          const icon = isPassed ? '✓' : '✗';
          const currentBorder = isCurrent ? 'ring-4 ring-[#e29547] scale-105 shadow-[0_5px_0_#2b180d]' : 'shadow-[0_2px_0_#2b180d]';

          stateStyle = `border-[2.5px] ${{bgStatus}} ${{currentBorder}} cursor-pointer`;
          badge = `<span class="text-sm font-cartoon font-bold">${{icon}}</span>`;
        }}

        stepper.innerHTML += `
          <div onclick="goToRound(${{i - 1}})" class="flex flex-col items-center justify-center p-2 rounded-2xl transition-all ${{stateStyle}}">
            <span class="text-[10px] font-cartoon font-bold uppercase">T${{i}}</span>
            ${{badge}}
          </div>
        `;
      }}
      document.getElementById('step-indicator').innerText = `Rodada ${{round.round_num}} de ${{maxR}} (${{match.profile}})`;

      // Contrato
      const tier = round.contract.tier || round.round_num;
      const reg = regions[tier - 1] || regions[0];
      document.getElementById('tier-badge').innerText = `Tier ${{tier}}`;
      document.getElementById('region-badge').className = `text-xs font-cartoon font-bold px-3 py-0.5 rounded-full border-2 ${{reg.color}}`;
      document.getElementById('region-badge').innerText = `${{reg.icon}} ${{reg.name}}`;
      document.getElementById('contract-name').innerText = round.contract.name;
      document.getElementById('contract-desc').innerText = `Comitê de ${{round.contract.committee_size}} membros • Custo: ${{round.contract.cost_per_player}} carta(s)/membro • Meta: ${{round.contract.target}} pts`;

      const outcomePill = document.getElementById('outcome-pill');
      if (round.is_success) {{
        outcomePill.className = 'stamp-approved px-5 py-2 rounded-2xl';
        outcomePill.innerHTML = '<span>APROVADO PELO BANCO</span>';
      }} else {{
        outcomePill.className = 'stamp-sabotaged px-5 py-2 rounded-2xl';
        outcomePill.innerHTML = '<span>💥 SABOTADO / DÉFICIT</span>';
      }}

      document.getElementById('total-score-val').innerText = `${{round.total_value}} / ${{round.contract.target}} pts`;
      document.getElementById('req-commodity-val').innerText = round.contract.req_commodity ? `${{round.contract.req_commodity}} (x${{round.contract.req_count}})` : 'Nenhum (Livre)';
      document.getElementById('commodity-delivered-val').innerHTML = round.has_req ? '<span class="text-[#059669]">✅ Entregue</span>' : '<span class="text-[#dc2626]">❌ Faltando</span>';
      document.getElementById('tokens-spent-val').innerText = `${{round.total_tokens_spent}} 🪙 Ariary`;

      // Diretiva
      const directiveContainer = document.getElementById('directive-container');
      if (round.directive) {{
        directiveContainer.innerHTML = `
          <div class="bg-[#fef3c7] border-2 border-[#b45309] rounded-2xl p-3 text-xs text-[#78350f] flex items-center justify-between shadow-sm">
            <span class="flex items-center gap-2"><span>📜</span> <strong>Evento Regulatório:</strong> ${{round.directive.name}} (${{round.directive.category}})</span>
            <span class="text-[10px] font-cartoon font-bold text-[#b45309] bg-white px-2.5 py-0.5 rounded-full border border-[#b45309]">Ativo</span>
          </div>
        `;
      }} else {{
        directiveContainer.innerHTML = `
          <div class="bg-white border-2 border-[#2b180d]/30 rounded-2xl p-3 text-xs text-[#6b472e] flex items-center justify-between shadow-sm">
            <span class="flex items-center gap-2"><span>🏛️</span> <strong>Sessão Ordinária do Banco:</strong> Governança padrão (Sem intervenção de Clima ou CVM).</span>
            <span class="text-[10px] font-cartoon font-bold text-[#92400e] bg-[#fef3c7] px-2.5 py-0.5 rounded-full border border-[#b45309]">Padrão</span>
          </div>
        `;
      }}

      // Cartas enviadas
      const submittedGrid = document.getElementById('submitted-cards-grid');
      submittedGrid.innerHTML = '';
      round.submitted.forEach(sub => {{
        const isBanker = match.banker_ids.includes(sub.player_id);
        const roleLabel = isBanker ? 'Banqueiro' : 'Estagiário';
        const roleBadge = isBanker ? 'bg-[#e0f2fe] text-[#0369a1] border-[#0284c7]' : 'bg-[#fee2e2] text-[#991b1b] border-[#dc2626]';
        const isSupplier = sub.is_req_responsible ? '<span class="text-[10px] bg-[#fef3c7] text-[#92400e] px-2 py-0.5 rounded-full border border-[#b45309] font-cartoon font-bold">Fornecedor Designado</span>' : '';

        let cardsHtml = '';
        sub.cards.forEach(c => {{
          cardsHtml += formatCardBadge(c);
        }});

        submittedGrid.innerHTML += `
          <div class="bg-white border-[2.5px] border-[#2b180d] rounded-2xl p-4 space-y-3 shadow-[0_4px_0_#2b180d]">
            <div class="flex justify-between items-center">
              <div class="flex items-center gap-2">
                <span class="font-cartoon font-bold text-sm text-[#2b180d]">Operador ${{sub.player_id}}</span>
                <span class="text-[10px] px-2.5 py-0.5 rounded-full border-2 font-cartoon font-bold ${{roleBadge}}">${{roleLabel}}</span>
                ${{isSupplier}}
              </div>
              <span class="coin-badge text-xs px-2.5 py-0.5 rounded-full">
                ${{sub.tokens_spent > 0 ? '+' + sub.tokens_spent + ' 🪙 MGA' : '0 🪙'}}
              </span>
            </div>
            <div class="space-y-1.5">
              ${{cardsHtml}}
            </div>
          </div>
        `;
      }});

      // Votação de governança
      const votesRow = document.getElementById('votes-row');
      votesRow.innerHTML = '';
      match.players.forEach(p => {{
        const v = round.votes ? round.votes[p.id] : true;
        const vBadge = v ? 'bg-[#dcfce7] text-[#166534] border-[#15803d]' : 'bg-[#fee2e2] text-[#991b1b] border-[#dc2626]';
        const vIcon = v ? 'SIM' : 'NÃO';
        votesRow.innerHTML += `
          <div class="text-center p-2 rounded-xl border-2 ${{vBadge}} font-cartoon font-bold text-xs shadow-[0_2px_0_#2b180d]">
            <div>Op ${{p.id}}</div>
            <div class="text-sm mt-0.5">${{vIcon}}</div>
          </div>
        `;
      }});

      // Carteiras privadas antes da rodada
      const handsGrid = document.getElementById('players-hands-grid');
      handsGrid.innerHTML = '';
      match.players.forEach(p => {{
        const inComm = round.committee.includes(p.id);
        const pHand = round.hands_before[p.id];
        const pTheme = playerThemes[p.id % playerThemes.length];
        const cardBorder = inComm 
          ? 'border-[3px] border-[#b45309] bg-gradient-to-b from-[#fefce8] to-[#fef08a] shadow-[0_5px_0_#b45309]' 
          : 'border-[2.5px] border-[#2b180d] bg-white shadow-[0_3px_0_#2b180d]';

        let cardsMiniHtml = '';
        pHand.cards.forEach(c => {{
          const isToxic = c.type === 'TOXIC';
          const badgeClass = isToxic ? 'bg-rose-100 text-rose-950 border-rose-500 font-bold' : 'bg-[#f8f5ee] text-[#2b180d] border-[#2b180d]/30 font-medium';
          cardsMiniHtml += `
            <div class="text-[10px] py-1 px-2 rounded-lg border ${{badgeClass}} flex justify-between items-center">
              <span class="truncate">${{c.name.split(' ')[0]}}</span>
              <span class="font-cartoon font-bold">${{c.base > 0 ? '+' + c.base : c.base}}</span>
            </div>
          `;
        }});

        handsGrid.innerHTML += `
          <div class="${{cardBorder}} rounded-2xl p-3.5 space-y-2.5 transition-all">
            <div class="flex justify-between items-center">
              <span class="font-cartoon font-bold text-xs text-[#2b180d] flex items-center gap-1.5">
                <span class="w-3 h-3 rounded-full border border-[#2b180d]" style="background: ${{pTheme.color}}"></span>
                Op ${{p.id}}
              </span>
              <span class="coin-badge text-[10px] px-2 py-0.5 rounded-full">${{pHand.tokens}} 🪙</span>
            </div>
            <div class="space-y-1">${{cardsMiniHtml}}</div>
            ${{inComm ? '<div class="text-[9px] text-center text-[#78350f] font-cartoon font-bold bg-[#fef08a] py-1 rounded-xl border border-[#b45309]">NO COMITÊ</div>' : '<div class="text-[9px] text-center text-[#166534] font-cartoon font-bold bg-[#dcfce7] py-1 rounded-xl border border-[#15803d]">NO BANCO</div>'}}
          </div>
        `;
      }});

      // Roster
      const rosterList = document.getElementById('roster-list');
      rosterList.innerHTML = '';
      match.players.forEach(p => {{
        const isBanker = match.banker_ids.includes(p.id);
        const badge = isBanker ? 'bg-[#e0f2fe] text-[#0369a1] border-[#0284c7]' : 'bg-[#fee2e2] text-[#991b1b] border-[#dc2626]';
        rosterList.innerHTML += `
          <div class="flex justify-between items-center py-2 border-b border-[#2b180d]/15">
            <span class="font-cartoon font-bold text-[#2b180d] flex items-center gap-1.5">
              <span>${{isBanker ? '🏛️' : '🕵️'}}</span> Operador ${{p.id}}
            </span>
            <span class="text-[10px] px-3 py-0.5 rounded-full border-2 font-cartoon font-bold ${{badge}} uppercase">${{p.role}}</span>
          </div>
        `;
      }});

      renderSuspicionBars();
    }}

    function renderSuspicionBars() {{
      const match = tracesData[currentScenarioKey];
      if (!match) return;
      const round = match.rounds[currentRoundIndex];
      const container = document.getElementById('suspicion-bars-container');
      if (!container) return;
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

        let barColor = 'bg-[#0284c7]';
        let tagStatus = '';

        if (currentPerspective !== 'avg' && parseInt(currentPerspective) === p.id) {{
          tagStatus = '<span class="text-[10px] text-[#0369a1] font-cartoon font-bold bg-[#e0f2fe] px-2 py-0.5 rounded-full border border-[#0284c7]">EU MESMO</span>';
          barColor = 'bg-[#0284c7]';
        }} else if (susVal >= 0.85) {{
          tagStatus = '<span class="text-[10px] text-[#991b1b] font-cartoon font-bold bg-[#fee2e2] px-2 py-0.5 rounded-full border border-[#b91c1c]">💥 TRAIDOR CONFIRMADO</span>';
          barColor = 'bg-gradient-to-r from-red-600 to-rose-500';
        }} else if (susVal >= 0.50) {{
          tagStatus = '<span class="text-[10px] text-[#92400e] font-cartoon font-bold bg-[#fef3c7] px-2 py-0.5 rounded-full border border-[#b45309]">⚠️ SUSPEITO</span>';
          barColor = 'bg-gradient-to-r from-amber-500 to-orange-500';
        }} else if (susVal <= 0.20) {{
          tagStatus = '<span class="text-[10px] text-[#166534] font-cartoon font-bold bg-[#dcfce7] px-2 py-0.5 rounded-full border border-[#15803d]">🛡️ AUDITADO & IDÔNEO</span>';
          barColor = 'bg-gradient-to-r from-emerald-500 to-teal-500';
        }} else {{
          tagStatus = '<span class="text-[10px] text-[#6b7280] font-cartoon font-bold bg-slate-100 px-2 py-0.5 rounded-full border border-slate-300">NEUTRO</span>';
          barColor = 'bg-slate-400';
        }}

        container.innerHTML += `
          <div class="space-y-1.5 text-xs bg-white p-3 rounded-2xl border-2 border-[#2b180d] shadow-[0_3px_0_#2b180d]">
            <div class="flex justify-between items-center">
              <div class="flex items-center gap-2">
                <span class="font-cartoon font-bold text-sm" style="color: ${{pTheme.color}}">Op ${{p.id}}</span>
                <span class="text-[10px] font-bold text-[#6b472e]">(${{isBanker ? 'Banqueiro' : 'Estagiário'}})</span>
                ${{tagStatus}}
              </div>
              <span class="font-cartoon font-bold text-sm text-[#2b180d]">${{(susVal * 100).toFixed(0)}}%</span>
            </div>
            <div class="w-full bg-[#f3ede0] h-3 rounded-full overflow-hidden border border-[#2b180d]/30">
              <div class="${{barColor}} h-full transition-all duration-500 rounded-full" style="width: ${{Math.min(100, Math.max(0, susVal * 100))}}%"></div>
            </div>
          </div>
        `;
      }});
    }}

    // Inicialização direta do visualizador de simulações
    populateBankerPerspectiveSelect();
    updateView();
  </script>
</body>
</html>
"""

    out_path = os.path.join(os.path.dirname(__file__), 'match_visualizer.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Generated pure trace visualizer at {{out_path}} ({{len(html_content)}} bytes)")

if __name__ == '__main__':
    build_pure_visualizer()
