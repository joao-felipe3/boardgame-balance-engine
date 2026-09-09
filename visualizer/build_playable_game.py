# -*- coding: utf-8 -*-
"""
Gerador de visualizer/game.html:
Jogo Interativo Standalone com identidade cartoon do deserto,
personagens animados estilo Duolingo, deliberação interativa de comitê
com perguntas, promessas e confronto no depósito da urna.
"""

import json
import os

def build_game_html():
    out_path = os.path.join(os.path.dirname(__file__), 'game.html')

    html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BTG Madagascar • Jogo Interativo & Mesa de Governança</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&family=JetBrains+Mono:wght@600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {
      --ink: #2b180d;
      --sand-bg: #f9f3e6;
      --sand-card: #fffdf8;
      --sand-accent: #e29547;
      --joshua-green: #2d6a4f;
      --sky-blue: #0284c7;
      --desert-gold: #f59e0b;
    }
    
    body {
      font-family: 'Plus Jakarta Sans', sans-serif;
      background: linear-gradient(180deg, #38bdf8 0px, #bae6fd 140px, #fde68a 320px, #fdf6ea 520px, #f5ecd7 100%);
      background-attachment: fixed;
      color: #2b180d;
      min-height: 100vh;
    }

    .font-cartoon {
      font-family: 'Fredoka', cursive, sans-serif;
    }

    /* Cards cartoon táteis com borda grossa e sombra rígida */
    .cartoon-card {
      background: #fffdf8;
      border: 3.5px solid #2b180d;
      border-radius: 28px;
      box-shadow: 0 8px 0 #2b180d, 0 16px 26px rgba(43, 24, 13, 0.12);
      transition: transform 0.15s ease, box-shadow 0.15s ease;
    }

    .cartoon-card-subtle {
      background: #fbf6ec;
      border: 2.5px solid #2b180d;
      border-radius: 20px;
      box-shadow: 0 4px 0 #2b180d;
    }

    /* Botões táteis com feedback de profundidade */
    .cartoon-btn {
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
    }
    .cartoon-btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 7px 0 #2b180d;
    }
    .cartoon-btn:active {
      transform: translateY(4px);
      box-shadow: 0 1px 0 #2b180d;
    }

    /* Carimbos oficiais APROVADO / SABOTADO */
    .stamp-approved {
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
    }
    
    .stamp-sabotaged {
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
    }

    /* Moeda cartoon Ariary */
    .coin-badge {
      background: linear-gradient(180deg, #fef08a 0%, #f59e0b 100%);
      border: 2px solid #854d0e;
      color: #78350f;
      font-family: 'Fredoka', cursive, sans-serif;
      font-weight: 700;
      box-shadow: 0 2.5px 0 #854d0e;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }

    /* =================================================== */
    /* ANIMAÇÃO DO DADO 1D6 & ESTILO DUOLINGO             */
    /* =================================================== */
    @keyframes roll-die {
      0% { transform: rotate(0deg) scale(1) translateY(0); }
      20% { transform: rotate(-35deg) scale(1.18) translateY(-28px); }
      40% { transform: rotate(35deg) scale(0.88) translateY(0); }
      60% { transform: rotate(-20deg) scale(1.12) translateY(-14px); }
      80% { transform: rotate(15deg) scale(0.96) translateY(0); }
      100% { transform: rotate(0deg) scale(1) translateY(0); }
    }
    .dice-rolling {
      animation: roll-die 0.45s infinite ease-in-out;
      transform-origin: center;
    }

    @keyframes duolingo-bounce {
      0%, 100% { transform: translateY(0) scale(1, 1); }
      50% { transform: translateY(-7px) scale(1.02, 0.98); }
    }
    .duolingo-idle {
      animation: duolingo-bounce 2.2s infinite ease-in-out;
      transform-origin: bottom center;
    }

    @keyframes duolingo-blink {
      0%, 90%, 100% { transform: scaleY(1); }
      95% { transform: scaleY(0.08); }
    }
    .duolingo-eye {
      transform-origin: center;
      animation: duolingo-blink 3.8s infinite;
    }

    @keyframes duolingo-talk {
      0%, 100% { transform: rotate(0deg); }
      25% { transform: rotate(-3deg); }
      75% { transform: rotate(3deg); }
    }
    .duolingo-talking {
      animation: duolingo-talk 0.35s infinite ease-in-out;
      transform-origin: bottom center;
    }

    @keyframes duolingo-sweat-anim {
      0% { opacity: 0; transform: translateY(-6px) scale(0.5); }
      40% { opacity: 1; transform: translateY(0) scale(1.1); }
      80% { opacity: 0.9; transform: translateY(14px) scale(0.9); }
      100% { opacity: 0; transform: translateY(22px) scale(0.7); }
    }
    .sweat-drop {
      animation: duolingo-sweat-anim 1.4s infinite ease-in;
    }

    @keyframes pop-speech {
      0% { opacity: 0; transform: scale(0.75) translateY(12px); }
      70% { transform: scale(1.03) translateY(-2px); }
      100% { opacity: 1; transform: scale(1) translateY(0); }
    }
    .speech-bubble-pop {
      animation: pop-speech 0.28s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
    }

    /* Animação 3D Realista do Dado 1d6 de Governança */
    .dice-scene {
      width: 90px;
      height: 90px;
      perspective: 600px;
      margin: 0 auto;
    }
    .dice-cube {
      width: 90px;
      height: 90px;
      position: relative;
      transform-style: preserve-3d;
      transition: transform 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    .dice-cube.rolling {
      animation: roll-cube-3d 0.35s infinite linear;
    }
    @keyframes roll-cube-3d {
      0% { transform: rotateX(0deg) rotateY(0deg) rotateZ(0deg) translateY(-8px); }
      25% { transform: rotateX(180deg) rotateY(90deg) rotateZ(45deg) translateY(-28px); }
      50% { transform: rotateX(360deg) rotateY(270deg) rotateZ(180deg) translateY(-4px); }
      75% { transform: rotateX(540deg) rotateY(450deg) rotateZ(270deg) translateY(-22px); }
      100% { transform: rotateX(720deg) rotateY(720deg) rotateZ(360deg) translateY(-8px); }
    }
    .dice-shadow {
      width: 80px;
      height: 18px;
      background: radial-gradient(ellipse at center, rgba(43, 24, 13, 0.45) 0%, rgba(43, 24, 13, 0) 75%);
      margin: 14px auto 0;
      border-radius: 50%;
      transition: all 0.3s ease;
    }
    .dice-cube.rolling + .dice-shadow {
      animation: shadow-bounce 0.35s infinite alternate ease-in-out;
    }
    @keyframes shadow-bounce {
      0% { transform: scale(0.6); opacity: 0.25; }
      100% { transform: scale(1.15); opacity: 0.7; }
    }
    .cube-face {
      position: absolute;
      width: 90px;
      height: 90px;
      background: linear-gradient(145deg, #ffffff, #f1f5f9);
      border: 3.5px solid #2b180d;
      border-radius: 20px;
      box-shadow: inset 0 0 8px rgba(0, 0, 0, 0.1), 0 4px 6px rgba(0, 0, 0, 0.12);
      user-select: none;
    }
    .face-front  { transform: rotateY(  0deg) translateZ(45px); }
    .face-back   { transform: rotateY(180deg) translateZ(45px); }
    .face-right  { transform: rotateY( 90deg) translateZ(45px); }
    .face-left   { transform: rotateY(-90deg) translateZ(45px); }
    .face-top    { transform: rotateX( 90deg) translateZ(45px); }
    .face-bottom { transform: rotateX(-90deg) translateZ(45px); }
    .pip {
      width: 14px;
      height: 14px;
      background: #2b180d;
      border-radius: 50%;
      box-shadow: inset 0 2px 2px rgba(0, 0, 0, 0.45);
      align-self: center;
      justify-self: center;
    }
    .pip.red {
      background: #dc2626;
      box-shadow: inset 0 2px 2px rgba(185, 28, 28, 0.65);
    }

    /* Cartas selecionáveis na mão */
    .hand-card-selectable {
      cursor: pointer;
      transition: all 0.15s cubic-bezier(0.34, 1.56, 0.64, 1);
      border: 3px solid #2b180d;
      border-radius: 18px;
      box-shadow: 0 4px 0 #2b180d;
    }
    .hand-card-selectable:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 0 #2b180d;
    }
    .hand-card-selected {
      transform: translateY(-8px) scale(1.03) !important;
      border-color: #e29547 !important;
      box-shadow: 0 10px 0 #b45309, 0 0 16px rgba(226, 149, 71, 0.6) !important;
      background: #fefce8 !important;
    }

    /* Balão de fala estilo cartoon Duolingo */
    .duolingo-bubble {
      position: relative;
      background: #ffffff;
      border: 3.5px solid #2b180d;
      border-radius: 24px;
      box-shadow: 0 6px 0 #2b180d;
    }
    .duolingo-bubble::after {
      content: '';
      position: absolute;
      bottom: -16px;
      left: 36px;
      border-width: 14px 14px 0;
      border-style: solid;
      border-color: #ffffff transparent;
      display: block;
      width: 0;
      z-index: 2;
    }
    .duolingo-bubble::before {
      content: '';
      position: absolute;
      bottom: -20px;
      left: 33px;
      border-width: 16px 16px 0;
      border-style: solid;
      border-color: #2b180d transparent;
      display: block;
      width: 0;
      z-index: 1;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
      width: 10px;
      height: 10px;
    }
    ::-webkit-scrollbar-track {
      background: #f5ecd7;
    }
    ::-webkit-scrollbar-thumb {
      background: #d4a373;
      border: 2px solid #2b180d;
      border-radius: 9999px;
    }
  </style>
</head>
<body class="p-3 md:p-8 antialiased">

  <div class="max-w-7xl mx-auto space-y-7">

    <!-- BARRA SUPERIOR DE NAVEGAÇÃO -->
    <div class="flex flex-col sm:flex-row justify-between items-center gap-4 bg-white/95 border-[3.5px] border-[#2b180d] p-3 md:p-4 rounded-3xl shadow-[0_6px_0_#2b180d]">
      <div class="flex items-center gap-3">
        <span class="text-3xl p-2 bg-[#fef3c7] rounded-2xl border-2 border-[#b45309]">🇲🇬</span>
        <div>
          <span class="text-[11px] font-cartoon font-bold text-[#8c4314] uppercase tracking-wider">BTG Pactual • Ilha de Madagascar</span>
          <h3 class="font-cartoon text-lg md:text-xl font-bold text-[#2b180d]">Mesa de Operações & Governança (Modo Jogável)</h3>
        </div>
      </div>

      <!-- BOTÃO PARA VER TRACES SIMULADOS & CONFIGURAÇÃO -->
      <div class="flex items-center gap-2.5 flex-wrap">
        <button onclick="toggleSetupPanel()" class="cartoon-btn px-4 py-2 bg-white hover:bg-[#fef3c7] text-[#78350f] text-xs flex items-center gap-1.5 shadow-[0_3px_0_#2b180d]">
          <span>⚙️</span> Nova Partida / Regras
        </button>
        <span class="text-xs font-cartoon font-bold text-[#166534] bg-[#dcfce7] px-3 py-1 rounded-full border-2 border-[#15803d]">
          ● Partida Ao Vivo
        </span>
        <a href="match_visualizer.html" class="cartoon-btn px-4 py-2 bg-[#f3ede0] hover:bg-[#e8dec8] text-[#78350f] text-xs flex items-center gap-2">
          <span>📊</span> Ver Auditoria & Traces Monte Carlo
        </a>
      </div>
    </div>

    <!-- BANNER HERO COM ILUSTRAÇÃO CARTOON DO DESERTO -->
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
            <span class="text-[10px] font-cartoon font-bold text-[#8c4314] tracking-wider uppercase">Sessão Ao Vivo Contra Bots</span>
            <h4 class="font-cartoon text-xs md:text-sm font-bold text-[#2b180d]">Comitê de Operações de Madagascar</h4>
          </div>
        </div>
      </div>
    </header>

    <!-- PAINEL DE CONFIGURAÇÃO / NOVO JOGO (MODAL / CARD NO TOPO) -->
    <div id="game-setup-panel" class="cartoon-card p-6 md:p-8 space-y-6 bg-[#fffefb]">
      <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b-2 border-[#2b180d]/15 pb-4">
        <div>
          <span class="text-xs font-cartoon font-bold text-[#b45309] uppercase tracking-wider">🎯 Nova Partida Interativa</span>
          <h2 class="text-2xl md:text-3xl font-cartoon font-bold text-[#2b180d]">Escolha sua Identidade e Regras</h2>
          <p class="text-xs text-[#6b472e]">Regras Oficiais Kit C (v14): Mão inicial de <strong>4 cartas</strong> (1x Cobalto, 1x Titânio + 2 secretas), <strong>0 Ariary</strong> inicial e <strong>Mercado de Balcão com 3 cartas abertas</strong>.</p>
        </div>
        <button onclick="startNewGame()" class="cartoon-btn px-8 py-3.5 bg-[#10b981] hover:bg-[#059669] text-white text-base shadow-[0_6px_0_#065f46]">
          🚀 INICIAR OPERAÇÃO MADAGASCAR
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
        <!-- Papel Escolhido -->
        <div class="cartoon-card-subtle p-4 space-y-3 bg-white">
          <label class="text-xs font-cartoon font-bold text-[#2b180d] uppercase">Sua Identidade Secreta:</label>
          <div class="grid grid-cols-3 gap-2">
            <button type="button" onclick="selectPlayRole('Banqueiro')" id="role-banker-btn" class="cartoon-btn py-2 text-xs bg-[#e0f2fe] text-[#0369a1] border-[#0284c7]">
              🏛️ Banqueiro
            </button>
            <button type="button" onclick="selectPlayRole('Estagiario')" id="role-intern-btn" class="cartoon-btn py-2 text-xs bg-white text-[#991b1b] border-slate-300 opacity-60">
              🕵️ Infiltrado
            </button>
            <button type="button" onclick="selectPlayRole('Random')" id="role-random-btn" class="cartoon-btn py-2 text-xs bg-white text-[#78350f] border-slate-300 opacity-60">
              🎲 Aleatório
            </button>
          </div>
          <p id="role-hint" class="text-[11px] text-[#6b472e]">Banqueiro Leal: Seu objetivo é aprovar contratos legítimos e desmascarar os estagiários infiltrados.</p>
        </div>

        <!-- Pacote de Expansão (DLCs) -->
        <div class="cartoon-card-subtle p-4 space-y-3 bg-white">
          <label class="text-xs font-cartoon font-bold text-[#2b180d] uppercase">Diretivas Regulatórias (DLC):</label>
          <label class="flex items-center gap-3 text-xs font-bold text-[#2b180d] cursor-pointer">
            <input type="checkbox" id="dlc-events-toggle" checked class="w-5 h-5 accent-[#e29547] rounded cursor-pointer">
            <span>Ativar Dado 1d6 de Governança & 9 Cartas DLC</span>
          </label>
          <p class="text-[11px] text-[#6b472e]">Conforme manual v14 (§7.1): Rola 1d6 no início da rodada. 1-3 é Ordinária, 4-6 ativa eventos (Auditoria CVM, Subsídio, Swap, Crise de Oferta, etc.).</p>
        </div>

        <!-- Dificuldade dos Bots -->
        <div class="cartoon-card-subtle p-4 space-y-3 bg-white">
          <label class="text-xs font-cartoon font-bold text-[#2b180d] uppercase">Comportamento dos 4 Bots:</label>
          <select id="bot-profile-select" class="w-full bg-white border-2 border-[#2b180d] text-xs font-bold rounded-xl p-2 shadow-[0_2px_0_#2b180d]">
            <option value="balanced">Equilibrado (IA Bayesiana v14 Padrão)</option>
            <option value="sleeper">Sleeper (Blefe Silencioso e Sabotagem Tardia)</option>
            <option value="aggressive">Agressivo (Confronto Imediato de Balcão)</option>
          </select>
          <p class="text-[11px] text-[#6b472e]">Os bots analisam o histórico de votos e os insumos entregues para deduzir suspeitas.</p>
        </div>
      </div>
    </div>

    <!-- MESA PRINCIPAL DO JOGO -->
    <div id="game-main-arena" class="space-y-7">
      
      <!-- PLACAR SOBERANO DA PARTIDA & STEPPER -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-7">
        <div class="lg:col-span-4 cartoon-card p-6 flex flex-col justify-between bg-gradient-to-b from-[#fffdf9] to-[#faf1dc]">
          <div>
            <div class="flex justify-between items-center pb-3 border-b-2 border-[#2b180d]/20">
              <span class="text-xs font-cartoon font-bold text-[#78350f] uppercase tracking-wider flex items-center gap-1.5">
                <span>🏛️</span> Conselho vs Infiltrados
              </span>
              <span id="game-round-badge" class="text-xs font-cartoon bg-[#e29547] text-white font-bold px-3 py-0.5 rounded-full border-2 border-[#2b180d]">
                R1 de 7
              </span>
            </div>
            <div class="grid grid-cols-2 gap-4 my-5 text-center">
              <div class="bg-gradient-to-b from-[#e0f2fe] to-[#bae6fd] rounded-2xl p-4 border-[2.5px] border-[#0284c7] shadow-[0_4px_0_#0284c7]">
                <div class="text-xs font-cartoon text-[#0369a1] font-bold uppercase">🏛️ Banqueiros</div>
                <div id="game-banker-score" class="text-5xl font-cartoon font-bold text-[#0284c7] mt-1">0</div>
                <div class="text-[10px] font-bold text-[#075985] mt-1 bg-white/70 py-0.5 rounded-full border border-[#0284c7]/40">Vitória: 3 Contratos</div>
              </div>
              <div class="bg-gradient-to-b from-[#ffe4e6] to-[#fecdd3] rounded-2xl p-4 border-[2.5px] border-[#e11d48] shadow-[0_4px_0_#e11d48]">
                <div class="text-xs font-cartoon text-[#9f1239] font-bold uppercase">🕵️ Estagiários</div>
                <div id="game-intern-score" class="text-5xl font-cartoon font-bold text-[#e11d48] mt-1">0</div>
                <div class="text-[10px] font-bold text-[#881337] mt-1 bg-white/70 py-0.5 rounded-full border border-[#e11d48]/40">Vitória: 3 Sabotagens</div>
              </div>
            </div>
          </div>
          <div id="game-status-text" class="text-xs text-center py-2.5 px-4 rounded-xl font-cartoon font-bold border-2 border-[#2b180d] bg-[#fef3c7] text-[#78350f] shadow-[0_3px_0_#2b180d]">
            Fase Atual: Convocação de Comitê
          </div>
        </div>

        <div class="lg:col-span-8 cartoon-card p-6 flex flex-col justify-between bg-[#fffdf9]">
          <div>
            <div class="flex justify-between items-center pb-3 border-b-2 border-[#2b180d]/20">
              <span class="text-xs font-cartoon font-bold text-[#2b180d] uppercase tracking-wider flex items-center gap-2">
                <span>📍</span> Trilha de Contratos Regionais (Tiers 1 a 7)
              </span>
              <span class="text-xs font-cartoon font-bold text-[#b45309]">Progresso da Expedição</span>
            </div>
            <div id="game-timeline-stepper" class="grid grid-cols-7 gap-2.5 my-5">
              <!-- Injetado via JS -->
            </div>
          </div>
          <div class="flex justify-between items-center pt-3 border-t-2 border-[#2b180d]/20 text-xs text-[#6b472e]">
            <span>Presidente Atual: <strong id="current-chair-label" class="text-[#2b180d]">Você (Op 0)</strong></span>
            <span>Vetos Consecutivos: <strong id="consecutive-vetoes-label" class="text-[#dc2626]">0 / 3</strong></span>
          </div>
        </div>
      </div>

      <!-- OS 5 INTEGRANTES DA MESA COM AVATARES ESTILO DUOLINGO & DOSSIÊ DE AUDITORIA -->
      <div class="cartoon-card p-6 md:p-8 space-y-4 bg-white">
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 pb-2 border-b-2 border-[#2b180d]/15">
          <div>
            <span class="text-xs font-cartoon font-bold text-[#b45309] uppercase tracking-wider flex items-center gap-1.5">
              <span>👥</span> Comitê de Operadores de Madagascar
            </span>
            <h3 class="font-cartoon text-xl font-bold text-[#2b180d]">Integrantes da Mesa (Avatares Vivos & Dossiê)</h3>
          </div>
          <div class="flex items-center gap-2 flex-wrap">
            <button onclick="shareDossierWithBoard()" id="share-dossier-btn" class="cartoon-btn px-4 py-2 bg-[#e0f2fe] hover:bg-[#bae6fd] text-[#0369a1] text-xs font-bold border-2 border-[#0284c7] shadow-[0_3px_0_#0284c7] flex items-center gap-1.5">
              <span>📢</span> Compartilhar Dossiê com a Mesa
            </button>
            <span class="text-xs text-[#8c4314] font-medium bg-[#fef3c7] px-3 py-1 rounded-full border border-[#b45309]">
              Dedução do Auditor Ativa
            </span>
          </div>
        </div>

        <!-- Grid dos 5 Personagens Duolingo -->
        <div id="duolingo-characters-roster" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 pt-2">
          <!-- Injetado via JS -->
        </div>
      </div>

      <!-- MERCADO DE BALCÃO ABERTO (3 CARTAS PÚBLICAS + MONTE FECHADO) CONFORME MANUAL V14 §2 -->
      <div id="open-market-card" class="cartoon-card p-5 md:p-6 space-y-4 bg-gradient-to-r from-[#fffdf8] via-[#fefbf0] to-[#fef3c7] border-[3.5px] border-[#2b180d]">
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 pb-2.5 border-b-2 border-[#2b180d]/15">
          <div class="flex items-center gap-2.5">
            <span class="text-2xl p-1.5 bg-[#fef3c7] rounded-xl border-2 border-[#b45309]">🏪</span>
            <div>
              <span class="text-xs font-cartoon font-bold text-[#b45309] uppercase tracking-wider">Mercado de Balcão Aberto (OTC)</span>
              <h3 class="font-cartoon text-lg md:text-xl font-bold text-[#2b180d]">Vitrine Pública de Commodities (3 Cartas Abertas)</h3>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs font-cartoon font-bold text-[#166534] bg-[#dcfce7] px-3 py-1 rounded-full border border-[#15803d]">
              Sinalização Pública de Lealdade
            </span>
          </div>
        </div>

        <div id="open-market-container" class="grid grid-cols-2 sm:grid-cols-4 gap-3.5 pt-1">
          <!-- Injetado dinamicamente via renderOpenMarket() -->
        </div>

        <div id="market-feed-container" class="text-[11px] text-[#6b472e] flex items-center justify-between pt-2 border-t border-[#2b180d]/10">
          <span id="market-last-action">Histórico: Mercado pronto para negociações da rodada.</span>
          <span class="font-cartoon text-[#b45309] font-bold">Manual v14 (§2)</span>
        </div>
      </div>

      <!-- ÁREA DE AÇÃO DA RODADA: PROPOSTA, DELIBERAÇÃO COM PERGUNTAS, VOTAÇÃO E DEPÓSITO -->
      <div id="round-action-container" class="cartoon-card p-6 md:p-8 space-y-6 bg-gradient-to-b from-[#fffefc] to-[#fbf5e7]">
        <!-- Injetado dinamicamente conforme a fase -->
      </div>

      <!-- CARTEIRA PRIVADA DO JOGADOR (CARTAS NA MÃO E MOEDAS) -->
      <div class="cartoon-card p-6 md:p-8 space-y-5 bg-white">
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 pb-3 border-b-2 border-[#2b180d]/15">
          <div>
            <span class="text-xs font-cartoon font-bold text-[#166534] uppercase tracking-wider flex items-center gap-1.5">
              <span>💼</span> Sua Carteira Pessoal (Operador 0)
            </span>
            <h3 class="font-cartoon text-xl font-bold text-[#2b180d]">Cartas Disponíveis & Saldo de Ariary</h3>
          </div>
          <div class="flex items-center gap-3">
            <span id="player-role-badge" class="px-3.5 py-1 rounded-full font-cartoon font-bold text-xs border-2">
              Carregando Papel...
            </span>
            <span class="coin-badge px-3.5 py-1 rounded-full text-xs">
              <span id="player-tokens-display">0</span> 🪙 Ariary
            </span>
          </div>
        </div>

        <div id="player-hand-container" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
          <!-- Injetado via JS -->
        </div>
      </div>

    </div>

  </div>

  <!-- JAVASCRIPT DO MOTOR JOGÁVEL, AVATARES DUOLINGO E DELIBERAÇÃO INTERATIVA -->
  <script>
    // ===================================================
    // DADOS DO SISTEMA E MOTOR JOGÁVEL
    // ===================================================
    const contractsList = [
      { tier: 1, name: "Exportação de Baunilha de Sava", target: 4, req_commodity: "Baunilha (+2)", req_count: 1, committee_size: 2, cost: 1, region: "Sava" },
      { tier: 2, name: "Lavra de Cobalto em Analanjirofo", target: 5, req_commodity: "Cobalto (+1)", req_count: 1, committee_size: 2, cost: 1, region: "Analanjirofo" },
      { tier: 3, name: "Sindicato de Titânio de Atsinanana", target: 6, req_commodity: "Titânio (+3)", req_count: 1, committee_size: 3, cost: 1, region: "Atsinanana" },
      { tier: 4, name: "Safiras de Ilakaka & Alaotra", target: 7, req_commodity: "Safira (+4)", req_count: 1, committee_size: 3, cost: 1, region: "Alaotra-Mangoro" },
      { tier: 5, name: "Fundo Soberano de Analamanga", target: 8, req_commodity: "Baunilha (+2)", req_count: 2, committee_size: 3, cost: 1, region: "Analamanga" },
      { tier: 6, name: "Consórcio Florestal de Menabe", target: 9, req_commodity: "Titânio (+3)", req_count: 2, committee_size: 4, cost: 1, region: "Menabe" },
      { tier: 7, name: "Grande Leilão de Gemas de Ihorombe", target: 11, req_commodity: "Safira (+4)", req_count: 2, committee_size: 4, cost: 1, region: "Ihorombe" }
    ];

    // Catálogo e Baralho Comercial Oficial (60 Cartas conforme Constants.py e Manual v14)
    const INITIAL_DECK_DEF = [
      { type: "CO", name: "Cobalto (+1)", base: 1, count: 22 },
      { type: "VN", name: "Baunilha (+2)", base: 2, count: 18 },
      { type: "TI", name: "Titânio (+3)", base: 3, count: 10 },
      { type: "SF", name: "Safira (+4)", base: 4, count: 6 },
      { type: "WILD", name: "Ouro Líquido (+4)", base: 4, count: 2 },
      { type: "TOXIC", name: "Ativo Tóxico (-4)", base: -4, count: 2 }
    ];

    const cardPool = [
      { type: "VN", name: "Baunilha (+2)", base: 2 },
      { type: "CO", name: "Cobalto (+1)", base: 1 },
      { type: "TI", name: "Titânio (+3)", base: 3 },
      { type: "SF", name: "Safira (+4)", base: 4 },
      { type: "WILD", name: "Ouro Líquido (+4)", base: 4 },
      { type: "TOXIC", name: "Ativo Tóxico (-4)", base: -4 }
    ];

    const dlcDirectives = [
      { id: "AUDITORIA_CVM", name: "Auditoria CVM (Due Diligence)", cat: "Compliance", desc: "O Chairman inspeciona 1 carta colocada no cofre após a resolução." },
      { id: "QUARENTENA_REGULATORIA", name: "Quarentena Regulatória", cat: "Compliance", desc: "O operador sob maior suspeita da mesa não pode ser escalado no comitê desta rodada." },
      { id: "SEGURO_CONTRA_SINISTRO", name: "Seguro Contra Sinistro (Hedge)", cat: "Compliance", desc: "Se houver Ativo Tóxico no cofre revelado, a apólice anula e descarta o tóxico!" },
      { id: "SUBSIDIO_GOVERNAMENTAL", name: "Subsídio Governamental (Incentivo)", cat: "Economia", desc: "Reduz a meta de liquidez do contrato em -2 pontos (mínimo de 3 pts)." },
      { id: "CRISE_DE_OFERTA", name: "Crise de Oferta (Choque Logístico)", cat: "Economia", desc: "Aumenta a meta de liquidez do contrato em +2 pontos." },
      { id: "SWAP_DE_COMMODITY", name: "Swap de Commodity (Arbitragem)", cat: "Economia", desc: "Cancela a cota de insumo obrigatório do contrato nesta rodada!" },
      { id: "LINHA_DE_CREDITO_SINDICAL", name: "Linha de Crédito Sindical", cat: "Economia", desc: "Todos os 5 operadores recebem imediatamente +1 Token de Ariary." },
      { id: "GOLDEN_SHARE", name: "Golden Share (Voto de Minerva)", cat: "Governança", desc: "O voto do Chairman tem peso duplo (2 votos) na votação do comitê." },
      { id: "COMITE_EXPANDIDO", name: "Comitê Interdepartamental (+1 Membro)", cat: "Operações", desc: "Aumenta o tamanho do comitê em +1 membro nesta rodada." }
    ];

    // Personagens Duolingo com traços visuais, falas e expressões
    const characters = [
      {
        id: 0,
        name: "Você (Op 0)",
        title: "Auditor Chefe",
        duoClass: "player",
        color: "#2563eb",
        skin: "#fbd38d",
        hair: "#2b180d",
        shirt: "#0284c7",
        expression: "confident", // confident, sweating, poker, wink
        bubbleText: "Estou pronto para analisar os contratos e garantir a segurança do banco!",
        voiceLines: {
          promiseAsk: "Quero ouvir o compromisso formal de cada membro antes de assinar.",
          promiseMade: "Meu compromisso com a mesa está selado na urna!"
        }
      },
      {
        id: 1,
        name: "Bertrand",
        title: "Banqueiro Sênior",
        duoClass: "banker",
        color: "#1e3a8a",
        skin: "#fde047",
        hair: "#475569",
        shirt: "#1e40af",
        expression: "confident",
        bubbleText: "Ordem e liquidez! Não tolerarei desvios na minha mesa de governança.",
        voiceLines: {
          pointsHigh: "Como banqueiro sênior, coloco uma carta pesada de Titânio (+3) sem hesitar!",
          pointsLow: "Minha carteira está conservadora nesta rodada, ofereço +1 ou +2 no máximo.",
          commodityYes: "Com certeza, disponho da cota de insumo exigida em meus livros.",
          commodityNo: "Não possuo este insumo. Meu papel será injetar liquidez líquida!",
          ariaryBurn: "Vou queimar 1 moeda de Ariary para garantir margem de folga.",
          ariaryNone: "Sem queima de moedas agora, a reserva deve ser poupada.",
          loyaltyLoyal: "Minha lealdade ao BTG é inquestionável! Audite meus votos se duvidar.",
          loyaltyTraitor: "A governança deste banco precisa de... 'reestruturações criativas'."
        }
      },
      {
        id: 2,
        name: "Malala",
        title: "Analista de Riscos",
        duoClass: "analyst",
        color: "#059669",
        skin: "#fcd34d",
        hair: "#1c1917",
        shirt: "#047857",
        expression: "poker",
        bubbleText: "Os números não mentem. Qualquer discrepância na urna será investigada!",
        voiceLines: {
          pointsHigh: "Meus modelos apontam necessidade de margem alta. Contribuo com +3 ou +4!",
          pointsLow: "Posso garantir apenas o custo mínimo contratual (+1 pt).",
          commodityYes: "Tenho o lote inspecionado e pronto para remessa.",
          commodityNo: "Negativo, não tenho esse insumo. Alguém mais deve suprir a cota.",
          ariaryBurn: "Queimarei 1 Ariary como hedge estatístico de segurança.",
          ariaryNone: "Gastar moedas agora tem custo de oportunidade negativo.",
          loyaltyLoyal: "Sou técnica e leal ao conselho. O risco está nos membros novatos.",
          loyaltyTraitor: "Às vezes, um colapso controlado rende excelentes oportunidades..."
        }
      },
      {
        id: 3,
        name: "Tovo",
        title: "Estagiário de Mesa",
        duoClass: "intern",
        color: "#dc2626",
        skin: "#fbcfe8",
        hair: "#ea580c",
        shirt: "#e11d48",
        expression: "sweating", // Gota de suor animada quando sob pressão!
        bubbleText: "E aí, chefe! Pode contar comigo, vou dar o meu melhor aqui na mesa!",
        voiceLines: {
          pointsHigh: "Com certeza vou colocar +3 ou +4 pontos na urna! Pode confiar... 😅",
          pointsLow: "Poxa, só sobrou carta baixinha na minha mão, foi mal aí!",
          commodityYes: "Acho que tenho o insumo sim! Vou botar lá dentro com certeza!",
          commodityNo: "Não tenho o insumo não, chefe! Deixa com o outro operador!",
          ariaryBurn: "Vou queimar moeda sim, tudo pelo time! 🪙",
          ariaryNone: "Tô sem moedas de Ariary, gastei no café da firma...",
          loyaltyLoyal: "Eu quero ser efetivado! Jamais sabotaria uma operação do banco!",
          loyaltyTraitor: "Eu? Sabotar?! Jamais! Olha minha carinha de bom moço... 😅💦"
        }
      },
      {
        id: 4,
        name: "Faly",
        title: "Trader de Campo",
        duoClass: "safari",
        color: "#d97706",
        skin: "#fef08a",
        hair: "#78350f",
        shirt: "#b45309",
        expression: "wink",
        bubbleText: "Conheço cada trilha de Madagascar. Sei exatamente onde as commodities estão.",
        voiceLines: {
          pointsHigh: "Trago +3 ou +4 pontos diretos da mina. Contem comigo para fechar a cota!",
          pointsLow: "O transporte atrasou, só consigo cobrir a cota mínima nesta rodada.",
          commodityYes: "O lote está no galpão pronto para embarque. É comigo!",
          commodityNo: "Não estou com essa commodity no momento, foco em minério pesado.",
          ariaryBurn: "Vou desembolsar 1 Ariary para acelerar a liberação alfandegária.",
          ariaryNone: "Sem queima agora, guardemos as moedas para os Tiers 6 e 7.",
          loyaltyLoyal: "Negócio fechado é negócio cumprido. Minha honra é a idoneidade.",
          loyaltyTraitor: "O deserto ensina que cada um deve proteger seus próprios interesses..."
        }
      }
    ];

    // ESTADO DO JOGO
    let gameState = {
      roundNum: 1,
      bankerScore: 0,
      internScore: 0,
      consecutiveVetoes: 0,
      chairId: 0,
      roles: {}, // id -> 'Banqueiro' | 'Estagiario'
      hands: {}, // id -> [cards]
      tokens: {}, // id -> count
      drawPile: [],
      discardPile: [],
      openMarket: [], // 3 cartas visíveis no balcão
      marketLog: [],
      humanSuspicions: { 1: 40, 2: 40, 3: 40, 4: 40 }, // Porcentagem exata 0% a 100%
      humanDeductions: { 1: 'neutral', 2: 'neutral', 3: 'neutral', 4: 'neutral' },
      botSuspicions: {
        1: { 0: 0.20, 1: 0.0, 2: 0.40, 3: 0.40, 4: 0.40 },
        2: { 0: 0.20, 1: 0.40, 2: 0.0, 3: 0.40, 4: 0.40 },
        3: { 0: 0.50, 1: 0.50, 2: 0.50, 3: 1.0, 4: 0.50 },
        4: { 0: 0.20, 1: 0.40, 2: 0.40, 3: 0.40, 4: 0.0 }
      },
      stage: 'SETUP', // SETUP, DICE_ROLL, PROPOSAL, DELIBERATION, VOTING, DEPOSIT, REVEAL, BENCH_DIVIDEND, GAME_OVER
      proposedCommittee: [],
      designatedSupplier: null,
      playerDeclaredCommodity: null, // 'has' | 'none' | 'liquidity'
      botCommodityClaims: {}, // id -> { claim: bool, text: string }
      promises: {}, // id -> { points, hasCommodity, ariaryBurn, comment }
      deliberationActiveMember: null,
      userPromiseDeclared: false,
      humanSelectedCards: [],
      humanCoinsSpent: 0,
      roundDirective: null,
      lastRevealData: null,
      diceState: { rolling: false, rolled: false, value: 1 }
    };

    let userRolePreference = 'Banqueiro';

    // ===================================================
    // GERENCIAMENTO DE BARALHO & MERCADO DE BALCÃO ABERTO
    // ===================================================
    function createShuffledDeck() {
      let deck = [];
      INITIAL_DECK_DEF.forEach(item => {
        for (let i = 0; i < item.count; i++) {
          deck.push({ type: item.type, name: item.name, base: item.base });
        }
      });
      for (let i = deck.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [deck[i], deck[j]] = [deck[j], deck[i]];
      }
      return deck;
    }

    function drawCardFromDeck() {
      if (!gameState.drawPile || gameState.drawPile.length === 0) {
        if (!gameState.discardPile || gameState.discardPile.length === 0) {
          gameState.discardPile = createShuffledDeck();
        }
        gameState.drawPile = gameState.discardPile.slice();
        gameState.discardPile = [];
        for (let i = gameState.drawPile.length - 1; i > 0; i--) {
          const j = Math.floor(Math.random() * (i + 1));
          [gameState.drawPile[i], gameState.drawPile[j]] = [gameState.drawPile[j], gameState.drawPile[i]];
        }
      }
      return gameState.drawPile.pop();
    }

    function refillOpenMarket(targetCount = 3) {
      if (!gameState.openMarket) gameState.openMarket = [];
      while (gameState.openMarket.length < targetCount) {
        const card = drawCardFromDeck();
        if (card) gameState.openMarket.push(card);
        else break;
      }
      renderOpenMarket();
    }

    function buyFromMarket(playerIndex, marketIndex) {
      if (!gameState.openMarket || !gameState.openMarket[marketIndex]) return null;
      const card = gameState.openMarket.splice(marketIndex, 1)[0];
      gameState.hands[playerIndex].push(card);
      refillOpenMarket(3);
      const char = characters[playerIndex];
      if (!gameState.marketLog) gameState.marketLog = [];
      gameState.marketLog.unshift(`${char.name} comprou ${card.name} do Balcão Aberto.`);
      renderOpenMarket();
      return card;
    }

    function buyFromDeckBlind(playerIndex) {
      const card = drawCardFromDeck();
      gameState.hands[playerIndex].push(card);
      const char = characters[playerIndex];
      if (!gameState.marketLog) gameState.marketLog = [];
      gameState.marketLog.unshift(`${char.name} comprou 1 carta anônima do Topo Fechado.`);
      renderOpenMarket();
      return card;
    }

    function humanDraftBenchCard(choiceType, marketIndex = 0) {
      if (choiceType === 'market') {
        buyFromMarket(0, marketIndex);
      } else {
        buyFromDeckBlind(0);
      }
      // Avança para a próxima rodada
      startRoundFlow();
    }

    // ===================================================
    // CONTROLE GRANULAR DE SUSPEIÇÃO & DOSSIÊ
    // ===================================================
    function updatePlayerSuspicion(targetId, val) {
      if (!gameState.humanSuspicions) gameState.humanSuspicions = { 1: 40, 2: 40, 3: 40, 4: 40 };
      let num = parseInt(val);
      if (isNaN(num)) num = 40;
      num = Math.max(0, Math.min(100, num));
      gameState.humanSuspicions[targetId] = num;
      
      // Sincroniza também humanDeductions para retrocompatibilidade
      if (num <= 25) gameState.humanDeductions[targetId] = 'loyal';
      else if (num >= 65) gameState.humanDeductions[targetId] = 'traitor';
      else gameState.humanDeductions[targetId] = 'neutral';

      renderDuolingoRoster();
    }

    function adjustPlayerSuspicion(targetId, delta) {
      if (!gameState.humanSuspicions) gameState.humanSuspicions = { 1: 40, 2: 40, 3: 40, 4: 40 };
      const cur = gameState.humanSuspicions[targetId] !== undefined ? gameState.humanSuspicions[targetId] : 40;
      updatePlayerSuspicion(targetId, cur + delta);
    }

    function setPlayerDeductionPreset(targetId, preset) {
      let val = 40;
      if (preset === 'loyal') val = 15;
      else if (preset === 'neutral') val = 50;
      else if (preset === 'traitor') val = 85;
      updatePlayerSuspicion(targetId, val);
    }

    function shareDossierWithBoard() {
      // Atualiza a suspeita de todos os bots que são Banqueiros Leais
      let anyBanker = false;
      for (let bId = 1; bId <= 4; bId++) {
        if (gameState.roles[bId] === 'Banqueiro') {
          anyBanker = true;
          if (!gameState.botSuspicions[bId]) gameState.botSuspicions[bId] = {};
          for (let targetId = 1; targetId <= 4; targetId++) {
            const susPct = (gameState.humanSuspicions && gameState.humanSuspicions[targetId] !== undefined)
              ? gameState.humanSuspicions[targetId]
              : 40;
            gameState.botSuspicions[bId][targetId] = susPct / 100;
          }
        }
      }

      // Reação em balão de fala do primeiro Banqueiro bot
      for (let bId = 1; bId <= 4; bId++) {
        if (gameState.roles[bId] === 'Banqueiro') {
          const char = characters[bId];
          char.bubbleText = "Dossiê calibrado acolhido! Votarei contra propostas que incluam operadores acima de 60% de suspeita!";
          char.expression = "confident";
          break;
        }
      }

      alert("📢 Dossiê Calibrado Compartilhado! Os Banqueiros Leais da mesa assimilaram suas porcentagens exatas de suspeita.");
      renderDuolingoRoster();
      updateUI();
    }    // ===================================================
    // DIÁLOGO & SONDAGEM DE INSUMOS (PRÉ-CONVOCAÇÃO)
    // ===================================================
    function declarePlayerCommodity(type) {
      gameState.playerDeclaredCommodity = type;
      const contract = contractsList[gameState.roundNum - 1];
      const char0 = characters[0];

      let claimText = "";
      if (type === 'has') {
        claimText = `Atenção Conselho: Tenho a remessa de ${contract.req_commodity} garantida para a missão!`;
      } else if (type === 'none') {
        claimText = `Atenção Conselho: NÃO possuo ${contract.req_commodity}! Recomendo não me escalarem para o comitê desta rodada.`;
      } else {
        claimText = `Atenção Conselho: Foco em liquidez financeira pesada (+pts). Posso queimar moedas de Ariary se necessário.`;
      }
      char0.bubbleText = claimText;
      char0.expression = type === 'none' ? 'sweating' : 'confident';

      // Se o Presidente for um bot, ele reage à declaração do jogador!
      const chairId = gameState.chairId;
      if (chairId !== 0) {
        const chairChar = characters[chairId];
        const needed = contract.committee_size;

        if (type === 'none' && gameState.proposedCommittee.includes(0)) {
          // Jogador avisou que não tem o insumo: bot presidente substitui o jogador por outro membro
          const others = [1, 2, 3, 4].filter(id => !gameState.proposedCommittee.includes(id) && id !== chairId);
          if (others.length > 0) {
            const replacer = others[0];
            const idx = gameState.proposedCommittee.indexOf(0);
            gameState.proposedCommittee[idx] = replacer;
            if (gameState.designatedSupplier === 0) gameState.designatedSupplier = replacer;

            chairChar.bubbleText = `Compreendido, Op 0! Como você não tem ${contract.req_commodity}, convoquei ${characters[replacer].name} em seu lugar!`;
            chairChar.expression = 'confident';
          }
        } else if (type === 'has' && !gameState.proposedCommittee.includes(0)) {
          // Jogador avisou que tem o insumo: adiciona ao comitê!
          if (gameState.proposedCommittee.length >= needed) {
            gameState.proposedCommittee.pop();
          }
          gameState.proposedCommittee.push(0);
          gameState.designatedSupplier = 0;
          chairChar.bubbleText = `Excelente notícia, Op 0! Como você possui ${contract.req_commodity}, você está oficialmente convocado!`;
          chairChar.expression = 'confident';
        } else {
          chairChar.bubbleText = `Registrado nos anais do conselho, Op 0! Levando sua disponibilidade em conta.`;
        }
      }

      renderDuolingoRoster();
      renderActionCard();
    }

    function inquireBotAboutCommodity(botId) {
      const char = characters[botId];
      const contract = contractsList[gameState.roundNum - 1];
      const isTraitor = gameState.roles[botId] === 'Estagiario';

      const reqKey = contract.req_commodity ? contract.req_commodity.split(' ')[0] : '';
      const reallyHas = (gameState.hands[botId] || []).some(c => c.name.includes(reqKey));

      let claim = false;
      let text = "";
      if (isTraitor) {
        // Traidor blefa com 65% de chance
        claim = reallyHas || (Math.random() < 0.65);
        if (claim) {
          text = `Sim, garanto a entrega de ${contract.req_commodity}! Pode confiar no meu transporte.`;
          char.expression = 'sweating';
        } else {
          text = `Não possuo ${contract.req_commodity}, sugiro convocar outro membro para a cota.`;
          char.expression = 'neutral';
        }
      } else {
        // Banqueiro leal é honesto
        claim = reallyHas;
        if (claim) {
          text = `Tenho a remessa de ${contract.req_commodity} em mãos no cofre! Estou pronto para cobrir a cota.`;
          char.expression = 'confident';
        } else {
          text = `Não possuo ${contract.req_commodity} nesta rodada, apenas ativos de liquidez.`;
          char.expression = 'neutral';
        }
      }

      char.bubbleText = text;
      if (!gameState.botCommodityClaims) gameState.botCommodityClaims = {};
      gameState.botCommodityClaims[botId] = { claim: claim, text: text };

      renderDuolingoRoster();
      renderActionCard();
    }

    // ===================================================
    // DADO 1d6 EM 3D REALISTA & HEADER DA MISSÃO
    // ===================================================
    function generateDiceSVG(value, isRolling) {
      return generate3DDiceHTML(value, isRolling);
    }

    function generate3DDiceHTML(value, isRolling) {
      const orientationMap = {
        1: 'rotateX(0deg) rotateY(0deg)',
        2: 'rotateY(-90deg)',
        3: 'rotateX(-90deg)',
        4: 'rotateX(90deg)',
        5: 'rotateY(90deg)',
        6: 'rotateY(180deg)'
      };
      const transform = !isRolling ? `transform: ${orientationMap[value] || orientationMap[1]};` : '';

      return `
        <div class="dice-scene">
          <div class="dice-cube ${isRolling ? 'rolling' : ''}" style="${transform}">
            <!-- Face 1: Front (1 red pip) -->
            <div class="cube-face face-front flex items-center justify-center">
              <div class="pip red w-6 h-6"></div>
            </div>
            <!-- Face 6: Back (6 pips) -->
            <div class="cube-face face-back grid grid-cols-2 p-3.5">
              <div class="pip self-start justify-self-start"></div>
              <div class="pip self-start justify-self-end"></div>
              <div class="pip self-center justify-self-start"></div>
              <div class="pip self-center justify-self-end"></div>
              <div class="pip self-end justify-self-start"></div>
              <div class="pip self-end justify-self-end"></div>
            </div>
            <!-- Face 2: Right (2 pips) -->
            <div class="cube-face face-right grid grid-cols-2 p-3.5">
              <div class="pip self-start justify-self-start"></div>
              <div></div>
              <div></div>
              <div class="pip self-end justify-self-end"></div>
            </div>
            <!-- Face 5: Left (5 pips) -->
            <div class="cube-face face-left grid grid-cols-3 p-2.5">
              <div class="pip self-start justify-self-start"></div>
              <div></div>
              <div class="pip self-start justify-self-end"></div>
              <div></div>
              <div class="pip red self-center justify-self-center"></div>
              <div></div>
              <div class="pip self-end justify-self-start"></div>
              <div></div>
              <div class="pip self-end justify-self-end"></div>
            </div>
            <!-- Face 3: Top (3 pips) -->
            <div class="cube-face face-top grid grid-cols-3 p-3">
              <div class="pip self-start justify-self-start"></div>
              <div></div>
              <div></div>
              <div></div>
              <div class="pip self-center justify-self-center"></div>
              <div></div>
              <div></div>
              <div></div>
              <div class="pip self-end justify-self-end"></div>
            </div>
            <!-- Face 4: Bottom (4 pips) -->
            <div class="cube-face face-bottom grid grid-cols-2 p-3.5">
              <div class="pip self-start justify-self-start"></div>
              <div class="pip self-start justify-self-end"></div>
              <div class="pip self-end justify-self-start"></div>
              <div class="pip self-end justify-self-end"></div>
            </div>
          </div>
          <div class="dice-shadow"></div>
        </div>
      `;
    }

    function renderMissionHeaderCard(contract, stageBadgeText = "Mesa de Operações") {
      let effectiveTarget = contract.target;
      let targetNotice = "";
      let reqNotice = contract.req_commodity ? `${contract.req_commodity} (x${contract.req_count})` : "Nenhum (Livre)";

      if (gameState.roundDirective) {
        if (gameState.roundDirective.id === "SUBSIDIO_GOVERNAMENTAL") {
          effectiveTarget = Math.max(3, contract.target - 2);
          targetNotice = ` <span class="text-xs font-bold text-[#15803d]">(-2 pts pelo Subsídio!)</span>`;
        } else if (gameState.roundDirective.id === "CRISE_DE_OFERTA") {
          effectiveTarget = contract.target + 2;
          targetNotice = ` <span class="text-xs font-bold text-[#b91c1c]">(+2 pts pela Crise!)</span>`;
        } else if (gameState.roundDirective.id === "SWAP_DE_COMMODITY") {
          reqNotice = "Insumo Isento pelo Swap (Livre!) ✅";
        }
      }

      let directivePill = "";
      if (gameState.roundDirective) {
        directivePill = `
          <div class="bg-[#fef3c7] border-2 border-[#b45309] rounded-2xl p-2.5 text-xs text-[#78350f] flex items-center justify-between shadow-sm">
            <span class="flex items-center gap-2"><span>📜</span> <strong>Diretriz de DLC (${gameState.roundDirective.cat}):</strong> ${gameState.roundDirective.name} — ${gameState.roundDirective.desc}</span>
            <span class="text-[10px] font-cartoon font-bold text-[#b45309] bg-white px-2.5 py-0.5 rounded-full border border-[#b45309]">Ativa</span>
          </div>
        `;
      } else {
        directivePill = `
          <div class="bg-white/80 border border-[#2b180d]/20 rounded-2xl p-2 text-[11px] text-[#6b472e] flex items-center justify-between">
            <span class="flex items-center gap-1.5"><span>🏛️</span> <strong>Sessão Ordinária:</strong> Sem eventos extraordinários. Governança e dedução clássica.</span>
            <span class="text-[9px] font-cartoon font-bold text-[#8c4314] bg-[#fef3c7] px-2.5 py-0.5 rounded-full border border-[#b45309]">Ordinária</span>
          </div>
        `;
      }

      return `
        <div class="cartoon-card-subtle p-4 md:p-5 bg-gradient-to-r from-[#fff9ed] via-[#fffdfa] to-[#fef3c7] border-[3px] border-[#2b180d] shadow-[0_5px_0_#2b180d] space-y-3">
          <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 border-b-2 border-[#2b180d]/15 pb-2.5">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="bg-[#e29547] text-white text-xs font-cartoon font-bold px-3 py-0.5 rounded-full border-2 border-[#2b180d]">
                Tier ${contract.tier} • ${contract.region}
              </span>
              <span class="text-xs font-cartoon font-bold text-[#78350f] uppercase">
                📜 Missão da Rodada:
              </span>
              <h3 class="font-cartoon text-xl md:text-2xl font-bold text-[#2b180d]">${contract.name}</h3>
            </div>
            <span class="stamp-approved px-3.5 py-1 rounded-full text-xs">${stageBadgeText}</span>
          </div>

          <div class="grid grid-cols-2 md:grid-cols-4 gap-2.5 text-center">
            <div class="bg-white p-2.5 rounded-xl border-2 border-[#2b180d] shadow-sm">
              <div class="text-[10px] font-cartoon text-[#8c4314] uppercase font-bold">🎯 Meta de Liquidez</div>
              <div class="font-cartoon font-bold text-base md:text-lg text-[#2b180d] mt-0.5">
                ${effectiveTarget} pts ${targetNotice}
              </div>
            </div>
            <div class="bg-white p-2.5 rounded-xl border-2 border-[#2b180d] shadow-sm">
              <div class="text-[10px] font-cartoon text-[#8c4314] uppercase font-bold">🌾 Insumo Obrigatório</div>
              <div class="font-cartoon font-bold text-xs ${contract.req_commodity ? 'text-[#b45309]' : 'text-[#166534]'} mt-1 truncate">
                ${reqNotice}
              </div>
            </div>
            <div class="bg-white p-2.5 rounded-xl border-2 border-[#2b180d] shadow-sm">
              <div class="text-[10px] font-cartoon text-[#8c4314] uppercase font-bold">👥 Quórum de Comitê</div>
              <div class="font-cartoon font-bold text-xs text-[#2b180d] mt-1">
                ${contract.committee_size} Membros
              </div>
            </div>
            <div class="bg-white p-2.5 rounded-xl border-2 border-[#2b180d] shadow-sm">
              <div class="text-[10px] font-cartoon text-[#8c4314] uppercase font-bold">💳 Custo por Membro</div>
              <div class="font-cartoon font-bold text-xs text-[#2b180d] mt-1">
                ${contract.cost} Carta(s) / Membro
              </div>
            </div>
          </div>

          ${directivePill}
        </div>
      `;
    }
    function generateDuolingoAvatarSVG(char, isTalking = false, expressionOverride = null) {
      const expr = expressionOverride || char.expression;
      const talkingClass = isTalking ? 'duolingo-talking' : '';
      const sweatAnim = expr === 'sweating' ? `
        <!-- Gota de Suor Estilo Duolingo -->
        <g class="sweat-drop" transform="translate(74, 28)">
          <path d="M0 0 C-4 5 -5 9 -2 12 C1 15 7 14 8 10 C9 6 4 3 0 0 Z" fill="#38bdf8" stroke="#2b180d" stroke-width="1.5" />
          <circle cx="2" cy="8" r="1.5" fill="#ffffff" />
        </g>
      ` : '';

      // Boca conforme expressão
      let mouthSvg = '<path d="M42 66 Q50 72 58 66" stroke="#2b180d" stroke-width="3" stroke-linecap="round" fill="none" />';
      if (expr === 'sweating') {
        mouthSvg = '<path d="M44 68 Q50 64 56 68" stroke="#2b180d" stroke-width="3" stroke-linecap="round" fill="none" />';
      } else if (expr === 'confident' || expr === 'wink') {
        mouthSvg = '<path d="M40 64 Q50 75 60 64" fill="#ef4444" stroke="#2b180d" stroke-width="2.5" /><path d="M42 65 Q50 71 58 65" fill="#ffffff" />';
      } else if (expr === 'poker') {
        mouthSvg = '<line x1="42" y1="67" x2="58" y2="67" stroke="#2b180d" stroke-width="3.5" stroke-linecap="round" />';
      }

      // Olhos estilo Duolingo (grandes, redondos, com brilho branco)
      let eyesSvg = `
        <!-- Olho Esquerdo -->
        <g class="duolingo-eye" transform="translate(34, 46)">
          <ellipse cx="0" cy="0" rx="9" ry="12" fill="#ffffff" stroke="#2b180d" stroke-width="3" />
          <circle cx="1" cy="0" r="5.5" fill="#2b180d" />
          <circle cx="3" cy="-3" r="2.2" fill="#ffffff" />
          <circle cx="-1" cy="2" r="1" fill="#ffffff" />
        </g>
        <!-- Olho Direito -->
        <g class="duolingo-eye" transform="translate(66, 46)">
          <ellipse cx="0" cy="0" rx="9" ry="12" fill="#ffffff" stroke="#2b180d" stroke-width="3" />
          <circle cx="-1" cy="0" r="5.5" fill="#2b180d" />
          <circle cx="1" cy="-3" r="2.2" fill="#ffffff" />
          <circle cx="-3" cy="2" r="1" fill="#ffffff" />
        </g>
      `;

      if (expr === 'wink') {
        eyesSvg = `
          <!-- Olho Esquerdo Aberto -->
          <g class="duolingo-eye" transform="translate(34, 46)">
            <ellipse cx="0" cy="0" rx="9" ry="12" fill="#ffffff" stroke="#2b180d" stroke-width="3" />
            <circle cx="1" cy="0" r="5.5" fill="#2b180d" />
            <circle cx="3" cy="-3" r="2.2" fill="#ffffff" />
          </g>
          <!-- Olho Direito Piscando -->
          <path d="M57 47 Q66 55 75 47" stroke="#2b180d" stroke-width="4" stroke-linecap="round" fill="none" />
        `;
      }

      // Acessório específico de cada personagem
      let accessorySvg = '';
      if (char.duoClass === 'player') {
        // Viseira moderna de Auditor BTG
        accessorySvg = `
          <path d="M22 34 Q50 20 78 34 L82 40 Q50 28 18 40 Z" fill="#0284c7" stroke="#2b180d" stroke-width="3" />
          <polygon points="46,26 54,26 50,32" fill="#fde047" stroke="#2b180d" stroke-width="1.5" />
        `;
      } else if (char.duoClass === 'banker') {
        // Monóculo com corrente de ouro + Gravata
        accessorySvg = `
          <!-- Monóculo -->
          <circle cx="66" cy="46" r="12.5" fill="none" stroke="#f59e0b" stroke-width="3" />
          <path d="M78 48 Q86 64 80 82" stroke="#f59e0b" stroke-width="2" fill="none" />
          <!-- Gravata -->
          <polygon points="46,80 54,80 56,104 50,110 44,104" fill="#f59e0b" stroke="#2b180d" stroke-width="2" />
        `;
      } else if (char.duoClass === 'analyst') {
        // Óculos de armação geométrica escura
        accessorySvg = `
          <!-- Óculos -->
          <rect x="23" y="38" width="22" height="18" rx="6" fill="none" stroke="#1e293b" stroke-width="3" />
          <rect x="55" y="38" width="22" height="18" rx="6" fill="none" stroke="#1e293b" stroke-width="3" />
          <line x1="45" y1="46" x2="55" y2="46" stroke="#1e293b" stroke-width="3" />
        `;
      } else if (char.duoClass === 'intern') {
        // Boné virado para trás
        accessorySvg = `
          <path d="M18 36 Q50 12 82 36 Q86 38 88 44 Q50 36 12 44 Z" fill="#ea580c" stroke="#2b180d" stroke-width="3" />
          <circle cx="50" cy="18" r="4" fill="#fde047" stroke="#2b180d" stroke-width="2" />
        `;
      } else if (char.duoClass === 'safari') {
        // Chapéu de safári e bigodinho
        accessorySvg = `
          <!-- Chapéu Safari -->
          <ellipse cx="50" cy="30" rx="44" ry="12" fill="#d97706" stroke="#2b180d" stroke-width="3" />
          <path d="M24 30 C24 12 76 12 76 30" fill="#b45309" stroke="#2b180d" stroke-width="3" />
          <!-- Bigodinho -->
          <path d="M42 61 Q47 57 50 61 Q53 57 58 61" stroke="#2b180d" stroke-width="3.5" stroke-linecap="round" fill="none" />
        `;
      }

      return `
        <svg class="w-full h-full duolingo-idle ${talkingClass}" viewBox="0 0 100 115" fill="none" xmlns="http://www.w3.org/2000/svg">
          <!-- Corpo / Torso com Roupa -->
          <rect x="20" y="76" width="60" height="42" rx="18" fill="${char.shirt}" stroke="#2b180d" stroke-width="3.5" />
          <line x1="50" y1="78" x2="50" y2="114" stroke="#2b180d" stroke-width="2" stroke-dasharray="3 3" />

          <!-- Cabeça redonda estilo Duolingo -->
          <circle cx="50" cy="50" r="34" fill="${char.skin}" stroke="#2b180d" stroke-width="3.5" />

          <!-- Cabelo base -->
          <path d="M20 44 Q50 14 80 44 Q84 28 68 18 Q50 12 32 18 Q16 28 20 44 Z" fill="${char.hair}" stroke="#2b180d" stroke-width="2.5" />

          <!-- Acessórios (Chapéu / Óculos / Monóculo / Viseira) -->
          ${accessorySvg}

          <!-- Olhos -->
          ${eyesSvg}

          <!-- Bochechas rosadas de cartoon -->
          <ellipse cx="27" cy="58" rx="5" ry="3" fill="#f43f5e" opacity="0.45" />
          <ellipse cx="73" cy="58" rx="5" ry="3" fill="#f43f5e" opacity="0.45" />

          <!-- Nariz delicado -->
          <circle cx="50" cy="57" r="2" fill="#8c4314" />

          <!-- Boca -->
          ${mouthSvg}

          <!-- Gota de Suor se nervoso -->
          ${sweatAnim}
        </svg>
      `;
    }

    // ===================================================
    // INICIALIZAÇÃO DE UMA NOVA PARTIDA
    // ===================================================
    function selectPlayRole(role) {
      userRolePreference = role;
      document.getElementById('role-banker-btn').className = role === 'Banqueiro' ? 'cartoon-btn py-2 text-xs bg-[#e0f2fe] text-[#0369a1] border-[#0284c7]' : 'cartoon-btn py-2 text-xs bg-white text-[#0369a1] border-slate-300 opacity-60';
      document.getElementById('role-intern-btn').className = role === 'Estagiario' ? 'cartoon-btn py-2 text-xs bg-[#fee2e2] text-[#991b1b] border-[#dc2626]' : 'cartoon-btn py-2 text-xs bg-white text-[#991b1b] border-slate-300 opacity-60';
      document.getElementById('role-random-btn').className = role === 'Random' ? 'cartoon-btn py-2 text-xs bg-[#fef3c7] text-[#78350f] border-[#b45309]' : 'cartoon-btn py-2 text-xs bg-white text-[#78350f] border-slate-300 opacity-60';

      const hint = document.getElementById('role-hint');
      if (role === 'Banqueiro') hint.innerText = 'Banqueiro Leal: Seu objetivo é aprovar contratos legítimos e desmascarar sabotadores.';
      else if (role === 'Estagiario') hint.innerText = 'Infiltrado / Traidor: Seu objetivo é sabotar 3 contratos secretamente sem ser pego!';
      else hint.innerText = 'Aleatório: O sistema sorteará sua identidade em segredo no início do jogo.';
    }

    function toggleSetupPanel() {
      const panel = document.getElementById('game-setup-panel');
      if (panel) {
        panel.classList.toggle('hidden');
        if (!panel.classList.contains('hidden')) {
          panel.scrollIntoView({ behavior: 'smooth' });
        }
      }
    }

    function restartGameFlow() {
      const panel = document.getElementById('game-setup-panel');
      if (panel) {
        panel.classList.remove('hidden');
        panel.scrollIntoView({ behavior: 'smooth' });
      }
    }

    function startNewGame() {
      // Esconder o painel de setup ao iniciar o jogo para deixar a mesa limpa
      const setupPanel = document.getElementById('game-setup-panel');
      if (setupPanel) {
        setupPanel.classList.add('hidden');
      }

      gameState.roundNum = 1;
      gameState.bankerScore = 0;
      gameState.internScore = 0;
      gameState.consecutiveVetoes = 0;
      gameState.chairId = 0;
      gameState.humanSelectedCards = [];
      gameState.humanCoinsSpent = 0;
      gameState.userPromiseDeclared = false;
      gameState.promises = {};

      // Atribuição de papéis (3 Banqueiros, 2 Estagiários)
      let humanRole = userRolePreference;
      if (humanRole === 'Random') {
        humanRole = Math.random() < 0.6 ? 'Banqueiro' : 'Estagiario';
      }

      gameState.roles[0] = humanRole;

      // Restante dos 4 bots: se humano for Banqueiro, bots tem 2 Banqueiros e 2 Estagiários.
      // Se humano for Estagiário, bots tem 3 Banqueiros e 1 Estagiário.
      let botRoles = humanRole === 'Banqueiro' 
        ? ['Banqueiro', 'Banqueiro', 'Estagiario', 'Estagiario']
        : ['Banqueiro', 'Banqueiro', 'Banqueiro', 'Estagiario'];
      
      // Embaralhar papéis dos bots
      botRoles.sort(() => Math.random() - 0.5);
      for (let i = 1; i <= 4; i++) {
        gameState.roles[i] = botRoles[i - 1];
      }

      // Distribuir mãos iniciais: REGRA OFICIAL KIT C (Manual v14 §2):
      // 1x Cobalto (+1), 1x Titânio (+3) + 2 cartas secretas do Topo Fechado = 4 CARTAS!
      // Saldo Inicial = 0 Ariary (Tokens de rendimento só vêm do descanso no banco de reservas!)
      gameState.drawPile = createShuffledDeck();
      gameState.discardPile = [];
      gameState.openMarket = [];
      refillOpenMarket(3);
      gameState.marketLog = ["Mercado de Balcão Aberto inaugurado com 3 ativos em vitrine pública."];

      for (let i = 0; i < 5; i++) {
        gameState.hands[i] = [
          { type: "CO", name: "Cobalto (+1)", base: 1 },
          { type: "TI", name: "Titânio (+3)", base: 3 },
          drawCardFromDeck(),
          drawCardFromDeck()
        ];
        gameState.tokens[i] = 0; // Inicia com ZERO moedas conforme Kit C oficial
      }

      // Inicia a rodada através do sorteio do Dado 1d6 de Governança
      startRoundFlow();
    }

    function startRoundFlow() {
      const dlcEnabled = document.getElementById('dlc-events-toggle') ? document.getElementById('dlc-events-toggle').checked : true;
      if (dlcEnabled) {
        gameState.stage = 'DICE_ROLL';
        gameState.diceState = { rolling: false, rolled: false, value: 1 };
        gameState.roundDirective = null;
        renderActionCard();
        updateUI();
      } else {
        gameState.roundDirective = null;
        gameState.stage = 'PROPOSAL';
        setupProposalPhase();
        renderActionCard();
        updateUI();
      }
    }

    function rollEventDice() {
      if (gameState.diceState.rolling) return;
      gameState.diceState.rolling = true;
      renderActionCard();

      setTimeout(() => {
        const finalVal = Math.floor(Math.random() * 6) + 1;
        gameState.diceState.rolling = false;
        gameState.diceState.rolled = true;
        gameState.diceState.value = finalVal;

        if (finalVal >= 4) {
          // 4, 5 ou 6 = Diretriz Extraordinária Ativa!
          const chosen = dlcDirectives[Math.floor(Math.random() * dlcDirectives.length)];
          gameState.roundDirective = chosen;
        } else {
          // 1, 2 ou 3 = Rodada Ordinária
          gameState.roundDirective = null;
        }
        renderActionCard();
      }, 900);
    }

    function proceedFromDiceToProposal() {
      gameState.stage = 'PROPOSAL';
      setupProposalPhase();
      renderActionCard();
      updateUI();
    }

    function drawCards(count) {
      let cards = [];
      for (let i = 0; i < count; i++) {
        cards.push(drawCardFromDeck());
      }
      return cards;
    }

    // ===================================================
    // FASE 1: PROPOSTA DE COMITÊ (CHAIRMAN)
    // ===================================================
    function setupProposalPhase() {
      const contract = contractsList[gameState.roundNum - 1];
      gameState.proposedCommittee = [];
      gameState.designatedSupplier = null;
      gameState.userPromiseDeclared = false;
      gameState.promises = {};

      if (gameState.chairId === 0) {
        // Humano é o Presidente: ele escolhe quem convocar
        gameState.proposedCommittee = [0]; // Inclui a si mesmo por padrão
        gameState.designatedSupplier = 0;
      } else {
        // Bot é o Presidente: se for Banqueiro, escolhe membros de menor suspeita no seu dossiê!
        const needed = contract.committee_size;
        let pool = [gameState.chairId];
        let others = [0, 1, 2, 3, 4].filter(id => id !== gameState.chairId);
        
        const isBankerChair = gameState.roles[gameState.chairId] === 'Banqueiro';
        if (isBankerChair && gameState.botSuspicions[gameState.chairId]) {
          others.sort((a, b) => {
            const susA = gameState.botSuspicions[gameState.chairId][a] || 0.40;
            const susB = gameState.botSuspicions[gameState.chairId][b] || 0.40;
            return susA - susB;
          });
        } else {
          others.sort(() => Math.random() - 0.5);
        }

        pool = pool.concat(others.slice(0, needed - 1));
        gameState.proposedCommittee = pool;
        gameState.designatedSupplier = pool[0];
      }
    }

    function toggleCommitteeMember(id) {
      if (gameState.chairId !== 0) return;
      const contract = contractsList[gameState.roundNum - 1];
      const idx = gameState.proposedCommittee.indexOf(id);
      if (idx > -1) {
        if (gameState.proposedCommittee.length > 1) {
          gameState.proposedCommittee.splice(idx, 1);
          if (gameState.designatedSupplier === id) {
            gameState.designatedSupplier = gameState.proposedCommittee[0];
          }
        }
      } else {
        if (gameState.proposedCommittee.length < contract.committee_size) {
          gameState.proposedCommittee.push(id);
        }
      }
      renderActionCard();
    }

    function setDesignatedSupplier(id) {
      if (gameState.chairId !== 0) return;
      gameState.designatedSupplier = id;
      renderActionCard();
    }

    function confirmProposal() {
      const contract = contractsList[gameState.roundNum - 1];
      if (gameState.proposedCommittee.length !== contract.committee_size) {
        alert(`O comitê precisa ter exatamente ${contract.committee_size} membros.`);
        return;
      }
      // Avança para a Fase de Deliberação Interativa de Comitê!
      gameState.stage = 'DELIBERATION';
      setupDeliberationPhase();
      renderActionCard();
      renderDuolingoRoster();
    }

    // ===================================================
    // FASE 2: DELIBERAÇÃO INTERATIVA COM DUOLINGO AVATARS
    // ===================================================
    function setupDeliberationPhase() {
      // Gera promessas iniciais dos bots no comitê
      gameState.proposedCommittee.forEach(id => {
        if (id !== 0 && !gameState.promises[id]) {
          const char = characters[id];
          const isTraitor = gameState.roles[id] === 'Estagiario';
          const points = isTraitor ? (Math.random() < 0.7 ? 3 : 2) : (Math.random() < 0.6 ? 3 : 2);
          const hasCommodity = isTraitor ? (Math.random() < 0.5) : true;
          const ariaryBurn = (gameState.tokens[id] > 0 && Math.random() < 0.4) ? 1 : 0;

          gameState.promises[id] = {
            points: points,
            hasCommodity: hasCommodity,
            ariaryBurn: ariaryBurn,
            loyaltyClaim: isTraitor ? "Estou comprometido em bater a meta!" : "Idoneidade absoluta com o banco!",
            lastAnswer: char.voiceLines.pointsHigh
          };
        }
      });

      // Abre diálogo com o primeiro bot do comitê por padrão
      const botMembers = gameState.proposedCommittee.filter(id => id !== 0);
      gameState.deliberationActiveMember = botMembers.length > 0 ? botMembers[0] : null;
    }

    function selectDeliberationMember(id) {
      gameState.deliberationActiveMember = id;
      renderActionCard();
      renderDuolingoRoster();
    }

    function askCommitteeMember(id, questionType) {
      const char = characters[id];
      const isTraitor = gameState.roles[id] === 'Estagiario';
      const contract = contractsList[gameState.roundNum - 1];
      let answer = "";
      let expr = char.expression;

      if (questionType === 'points') {
        const promisedPts = gameState.promises[id].points;
        answer = promisedPts >= 3 ? char.voiceLines.pointsHigh : char.voiceLines.pointsLow;
        if (isTraitor) expr = 'sweating';
      } else if (questionType === 'commodity') {
        const hasComm = gameState.promises[id].hasCommodity;
        answer = hasComm 
          ? `Sim! Tenho a remessa de ${contract.req_commodity || 'commodities'} garantida no cofre.`
          : `Não possuo ${contract.req_commodity || 'esse insumo'}, foco na liquidez financeira.`;
        if (isTraitor && hasComm) expr = 'sweating';
      } else if (questionType === 'ariary') {
        const burn = gameState.promises[id].ariaryBurn;
        answer = burn > 0 ? char.voiceLines.ariaryBurn : char.voiceLines.ariaryNone;
      } else if (questionType === 'loyalty') {
        answer = isTraitor ? char.voiceLines.loyaltyTraitor : char.voiceLines.loyaltyLoyal;
        expr = isTraitor ? 'sweating' : 'confident';
      }

      gameState.promises[id].lastAnswer = answer;
      char.expression = expr;

      renderActionCard();
      renderDuolingoRoster();
    }

    function declareUserPromise(pts, comm, ariary) {
      gameState.promises[0] = {
        points: parseInt(pts),
        hasCommodity: comm === 'yes',
        ariaryBurn: parseInt(ariary),
        loyaltyClaim: "Declaração formal registrada nos autos da governança."
      };
      gameState.userPromiseDeclared = true;

      // Anima os outros membros reagindo
      characters.forEach(c => {
        if (c.id !== 0) {
          c.bubbleText = `Ouvimos sua promessa, Auditor! Registrado +${pts} pts e ${ariary} moedas.`;
        }
      });

      renderActionCard();
      renderDuolingoRoster();
    }

    function proceedToVoting() {
      gameState.stage = 'VOTING';
      renderActionCard();
      renderDuolingoRoster();
    }

    // ===================================================
    // FASE 3: VOTAÇÃO DE GOVERNANÇA (SIM / NÃO)
    // ===================================================
    function submitHumanVote(approved) {
      const votes = {};
      votes[0] = approved;

      // Votos dos bots:
      // Banqueiros leais consultam suas suspeitas (influenciadas pelo Dossiê do Jogador!)
      // Se qualquer outro membro do comitê tiver suspeita >= 0.65, o Banqueiro leal VETA (Voto NÃO)!
      let yesCount = approved ? 1 : 0;
      for (let i = 1; i <= 4; i++) {
        const isBanker = gameState.roles[i] === 'Banqueiro';
        let botVote = true;
        if (isBanker) {
          const othersInComm = gameState.proposedCommittee.filter(id => id !== i);
          const maxSus = Math.max(...othersInComm.map(id => (gameState.botSuspicions[i] && gameState.botSuspicions[i][id]) || 0.40), 0);
          if (maxSus >= 0.65) {
            botVote = false; // Veto do Banqueiro por suspeita do Dossiê!
          } else {
            botVote = true;
          }
        } else {
          // Estagiário vota SIM se estiver no comitê, ou blefa votando SIM ~55% das vezes
          const inComm = gameState.proposedCommittee.includes(i);
          botVote = inComm ? true : (Math.random() < 0.55);
        }
        votes[i] = botVote;
        if (botVote) yesCount++;
      }

      const passed = yesCount >= 3;

      if (passed) {
        gameState.consecutiveVetoes = 0;
        // Avança para depósito na urna
        gameState.stage = 'DEPOSIT';
        gameState.humanCoinsSpent = 0;
        if (gameState.proposedCommittee.includes(0) && gameState.hands[0] && gameState.hands[0].length > 0) {
          gameState.humanSelectedCards = [0];
        } else {
          gameState.humanSelectedCards = [];
        }
        renderActionCard();
      } else {
        gameState.consecutiveVetoes++;
        if (gameState.consecutiveVetoes >= 3) {
          alert("⚠️ 3 VETOS CONSECUTIVOS! O Banco Central força a execução imediata deste comitê!");
          gameState.consecutiveVetoes = 0;
          gameState.stage = 'DEPOSIT';
          gameState.humanCoinsSpent = 0;
          if (gameState.proposedCommittee.includes(0) && gameState.hands[0] && gameState.hands[0].length > 0) {
            gameState.humanSelectedCards = [0];
          } else {
            gameState.humanSelectedCards = [];
          }
          renderActionCard();
        } else {
          alert(`Comitê vetado pela mesa (${yesCount} votos SIM vs ${5 - yesCount} votos NÃO). A presidência avança.`);
          gameState.chairId = (gameState.chairId + 1) % 5;
          gameState.stage = 'PROPOSAL';
          setupProposalPhase();
          renderActionCard();
        }
      }
      updateUI();
    }

    // ===================================================
    // FASE 4: DEPÓSITO SECRETO NA URNA (VAULT)
    // ===================================================
    function toggleHumanCardSelect(cardIndex) {
      const contract = contractsList[gameState.roundNum - 1];
      const requiredCost = contract.cost || 1;
      const idx = gameState.humanSelectedCards.indexOf(cardIndex);
      if (idx > -1) {
        gameState.humanSelectedCards.splice(idx, 1);
      } else {
        if (gameState.humanSelectedCards.length < requiredCost) {
          gameState.humanSelectedCards.push(cardIndex);
        } else if (requiredCost === 1) {
          gameState.humanSelectedCards = [cardIndex];
        }
      }
      renderPlayerHand();
      renderActionCard();
    }

    function adjustHumanCoins(delta) {
      const maxCoins = gameState.tokens[0] || 0;
      const newVal = gameState.humanCoinsSpent + delta;
      if (newVal >= 0 && newVal <= maxCoins) {
        gameState.humanCoinsSpent = newVal;
        renderActionCard();
      }
    }

    function confirmDeposit() {
      const contract = contractsList[gameState.roundNum - 1];
      const inComm = gameState.proposedCommittee.includes(0);

      if (inComm && gameState.humanSelectedCards.length !== contract.cost) {
        alert(`Você precisa selecionar exatamente ${contract.cost} carta(s) para depositar.`);
        return;
      }

      // Processa depósitos de todos os membros do comitê
      let submittedCards = [];
      let totalPoints = 0;
      let hasRequiredCommodity = false;
      let totalCoinsSpent = 0;
      let auditLog = [];

      gameState.proposedCommittee.forEach(id => {
        let cardsDeposited = [];
        let coinsSpent = 0;

        if (id === 0) {
          // Depósito do jogador
          gameState.humanSelectedCards.sort((a,b) => b - a);
          gameState.humanSelectedCards.forEach(cardIdx => {
            const card = gameState.hands[0].splice(cardIdx, 1)[0];
            cardsDeposited.push(card);
          });
          coinsSpent = gameState.humanCoinsSpent;
          gameState.tokens[0] -= coinsSpent;
        } else {
          // Depósito do bot baseado em seu papel
          const isTraitor = gameState.roles[id] === 'Estagiario';
          const pHand = gameState.hands[id];
          
          if (isTraitor && Math.random() < 0.75) {
            // Tenta sabotar! Procura ativo tóxico ou carta fraca
            const toxicIdx = pHand.findIndex(c => c.type === 'TOXIC');
            if (toxicIdx > -1) {
              cardsDeposited.push(pHand.splice(toxicIdx, 1)[0]);
            } else {
              // Carta de menor valor
              pHand.sort((a,b) => a.base - b.base);
              cardsDeposited.push(pHand.shift());
            }
          } else {
            // Banqueiro leal: prioriza insumo exigido se tiver, e pontos altos
            const reqIdx = contract.req_commodity ? pHand.findIndex(c => c.name.includes(contract.req_commodity.split(' ')[0])) : -1;
            if (reqIdx > -1) {
              cardsDeposited.push(pHand.splice(reqIdx, 1)[0]);
            } else {
              pHand.sort((a,b) => b.base - a.base);
              cardsDeposited.push(pHand.shift());
            }
            // Queima moedas se prometido
            if (gameState.promises[id] && gameState.promises[id].ariaryBurn > 0 && gameState.tokens[id] > 0) {
              coinsSpent = 1;
              gameState.tokens[id] -= 1;
            }
          }
        }

        // Soma pontos e verifica insumo
        let memberPts = coinsSpent;
        cardsDeposited.forEach(c => {
          memberPts += c.base;
          if (contract.req_commodity && c.name.includes(contract.req_commodity.split(' ')[0])) {
            hasRequiredCommodity = true;
          }
        });

        totalPoints += memberPts;
        totalCoinsSpent += coinsSpent;

        // Compara com a promessa feita na deliberação!
        const promise = gameState.promises[id] || { points: 0, hasCommodity: false, ariaryBurn: 0 };
        const promisedTotal = promise.points + (promise.ariaryBurn || 0);
        const fulfilled = memberPts >= promisedTotal;

        auditLog.push({
          playerId: id,
          cards: cardsDeposited,
          coins: coinsSpent,
          pointsEarned: memberPts,
          promised: promisedTotal,
          fulfilled: fulfilled,
          isTraitor: gameState.roles[id] === 'Estagiario'
        });
      });

      // Aplica efeitos das Diretrizes de DLC se ativo
      let effectiveTarget = contract.target;
      let needCommodity = contract.req_commodity !== null;

      if (gameState.roundDirective) {
        if (gameState.roundDirective.id === "SUBSIDIO_GOVERNAMENTAL") {
          effectiveTarget = Math.max(3, contract.target - 2);
        } else if (gameState.roundDirective.id === "CRISE_DE_OFERTA") {
          effectiveTarget = contract.target + 2;
        } else if (gameState.roundDirective.id === "SWAP_DE_COMMODITY") {
          needCommodity = false;
        }
      }

      // Seguro Contra Sinistro: Se ativo e houver tóxico, anula a penalidade do primeiro tóxico
      if (gameState.roundDirective && gameState.roundDirective.id === "SEGURO_CONTRA_SINISTRO") {
        for (let row of auditLog) {
          const toxicCard = row.cards.find(c => c.type === 'TOXIC');
          if (toxicCard && !toxicCard.annulled) {
            toxicCard.annulled = true;
            row.pointsEarned += 4;
            totalPoints += 4;
            break;
          }
        }
      }

      // Regra de Sucesso: totalPoints >= target E (sem exigência ou tem o insumo)
      const isSuccess = (totalPoints >= effectiveTarget) && (!needCommodity || hasRequiredCommodity);

      if (isSuccess) {
        gameState.bankerScore++;
      } else {
        gameState.internScore++;
      }

      // Registra dados para a tela de revelação
      gameState.lastRevealData = {
        contract: contract,
        effectiveTarget: effectiveTarget,
        totalPoints: totalPoints,
        hasRequiredCommodity: hasRequiredCommodity,
        isSuccess: isSuccess,
        auditLog: auditLog,
        totalCoinsSpent: totalCoinsSpent
      };

      gameState.stage = 'REVEAL';
      renderActionCard();
      renderDuolingoRoster();
      updateUI();
    }

    // ===================================================
    // FASE 5: REVELAÇÃO DA URNA & AUDITORIA DE PROMESSAS
    // ===================================================
    function finishRound() {
      const lastComm = gameState.proposedCommittee;
      const benchPlayers = [0, 1, 2, 3, 4].filter(id => !lastComm.includes(id));

      // Dividendos de Banco (Bench Players) conforme manual v14 §2:
      // Operadores que descansaram de fora do comitê executado recebem:
      // 1. +1 Token de Rendimento / Juros (máx 3 tokens)
      // 2. +1 Carta de Recurso (Mercado Aberto ou Topo Fechado)
      benchPlayers.forEach(id => {
        // +1 Token de Ariary (teto de 3)
        if (gameState.tokens[id] < 3) {
          gameState.tokens[id] += 1;
        }

        // Bots no banco pegam suas cartas
        if (id !== 0) {
          const isBanker = gameState.roles[id] === 'Banqueiro';
          const nextContract = contractsList[gameState.roundNum] || contractsList[contractsList.length - 1];
          let pickedMarket = false;
          // Se for banqueiro e houver a commodity exigida aberta no mercado, compra do balcão aberto!
          if (isBanker && nextContract && nextContract.req_commodity) {
            const reqKey = nextContract.req_commodity.split(' ')[0];
            const mIdx = (gameState.openMarket || []).findIndex(c => c.name.includes(reqKey));
            if (mIdx > -1) {
              buyFromMarket(id, mIdx);
              pickedMarket = true;
            }
          }
          if (!pickedMarket) {
            if (Math.random() < 0.65 && gameState.openMarket && gameState.openMarket.length > 0) {
              buyFromMarket(id, 0);
            } else {
              buyFromDeckBlind(id);
            }
          }
        }
      });

      // Regra de segurança: se algum operador estiver com 0 cartas, repõe 1 de emergência
      for (let i = 0; i < 5; i++) {
        if (gameState.hands[i].length === 0) {
          buyFromDeckBlind(i);
        }
      }

      // Verifica condição de término oficial: Primeiro time a atingir 4 vitórias (Melhor de 7) ou ao fim da 7ª rodada
      const gameOver = gameState.bankerScore >= 4 || gameState.internScore >= 4 || gameState.roundNum >= 7;
      if (gameOver) {
        gameState.stage = 'GAME_OVER';
        renderActionCard();
        updateUI();
        return;
      }

      gameState.roundNum++;
      gameState.chairId = (gameState.chairId + 1) % 5;

      // Se o humano estava no banco de reservas, oferecemos a escolha interativa de dividendo!
      if (benchPlayers.includes(0)) {
        gameState.stage = 'BENCH_DIVIDEND';
        renderActionCard();
        updateUI();
      } else {
        startRoundFlow();
      }
    }

    // ===================================================
    // RENDERIZAÇÃO DA INTERFACE
    // ===================================================
    function updateUI() {
      document.getElementById('game-round-badge').innerText = `R${gameState.roundNum} de 7`;
      document.getElementById('game-banker-score').innerText = gameState.bankerScore;
      document.getElementById('game-intern-score').innerText = gameState.internScore;
      document.getElementById('consecutive-vetoes-label').innerText = `${gameState.consecutiveVetoes} / 3`;
      document.getElementById('current-chair-label').innerText = gameState.chairId === 0 ? 'Você (Op 0)' : `Operador ${gameState.chairId}`;

      // Papel do jogador
      const roleBadge = document.getElementById('player-role-badge');
      const isBanker = gameState.roles[0] === 'Banqueiro';
      roleBadge.className = isBanker 
        ? 'px-3.5 py-1 rounded-full font-cartoon font-bold text-xs bg-[#e0f2fe] text-[#0369a1] border-2 border-[#0284c7]'
        : 'px-3.5 py-1 rounded-full font-cartoon font-bold text-xs bg-[#fee2e2] text-[#991b1b] border-2 border-[#dc2626]';
      roleBadge.innerText = isBanker ? '🏛️ Banqueiro Leal' : '🕵️ Estagiário Infiltrado';

      document.getElementById('player-tokens-display').innerText = gameState.tokens[0] || 0;

      // Status text
      const statusLabels = {
        'SETUP': 'Preparação da Mesa',
        'DICE_ROLL': 'Sorteio 1d6 de Governança (DLC)',
        'PROPOSAL': 'Fase 1: Convocação de Comitê',
        'DELIBERATION': 'Fase 2: Negociação & Promessas',
        'VOTING': 'Fase 3: Votação de Confiança',
        'DEPOSIT': 'Fase 4: Depósito na Urna',
        'REVEAL': 'Fase 5: Abertura da Urna & Auditoria',
        'BENCH_DIVIDEND': 'Dividendo de Banco (Recomposição)',
        'GAME_OVER': 'Partida Finalizada'
      };
      const statusEl = document.getElementById('game-status-text');
      if (statusEl) {
        statusEl.innerText = `Fase Atual: ${statusLabels[gameState.stage] || gameState.stage}`;
      }

      renderTimelineStepper();
      renderDuolingoRoster();
      renderOpenMarket();
      renderPlayerHand();
      renderActionCard();
    }

    function renderTimelineStepper() {
      const stepper = document.getElementById('game-timeline-stepper');
      stepper.innerHTML = '';

      for (let i = 1; i <= 7; i++) {
        const contract = contractsList[i - 1];
        let stateStyle = 'bg-white/70 border-dashed border-[#2b180d]/40 opacity-60';
        let badge = `<span class="text-[9px] font-cartoon font-bold text-[#8c4314]">${contract.region.substring(0, 4)}</span>`;

        if (i < gameState.roundNum) {
          // Rodadas passadas
          stateStyle = 'bg-[#dcfce7] border-[2.5px] border-[#15803d] text-[#166534] shadow-[0_2px_0_#2b180d]';
          badge = '<span class="text-sm font-cartoon font-bold">✓</span>';
        } else if (i === gameState.roundNum) {
          stateStyle = 'bg-[#fef08a] border-[3px] border-[#b45309] text-[#78350f] ring-4 ring-[#e29547] scale-105 shadow-[0_5px_0_#2b180d]';
          badge = '<span class="text-xs font-cartoon font-bold">ATUAL</span>';
        }

        stepper.innerHTML += `
          <div class="flex flex-col items-center justify-center p-2 rounded-2xl transition-all ${stateStyle}">
            <span class="text-[10px] font-cartoon font-bold uppercase">T${i}</span>
            ${badge}
          </div>
        `;
      }
    }

    function renderDuolingoRoster() {
      const container = document.getElementById('duolingo-characters-roster');
      container.innerHTML = '';

      characters.forEach(char => {
        const inComm = gameState.proposedCommittee.includes(char.id);
        const isChair = gameState.chairId === char.id;
        const isSelectedForDelib = gameState.deliberationActiveMember === char.id;
        const isHuman = char.id === 0;

        let badgeStatus = '';
        if (isChair) badgeStatus += '<span class="text-[9px] bg-[#fde047] text-[#78350f] px-2 py-0.5 rounded-full border border-[#b45309] font-cartoon font-bold">CHAIRMAN</span> ';
        if (inComm) badgeStatus += '<span class="text-[9px] bg-[#dcfce7] text-[#166534] px-2 py-0.5 rounded-full border border-[#15803d] font-cartoon font-bold">NO COMITÊ</span>';
        else badgeStatus += '<span class="text-[9px] bg-slate-100 text-[#475569] px-2 py-0.5 rounded-full border border-slate-300 font-cartoon font-bold">NO BANCO</span>';

        const cardRing = isSelectedForDelib 
          ? 'ring-4 ring-[#e29547] bg-[#fefce8] border-[#b45309] shadow-[0_8px_0_#b45309]' 
          : 'bg-white border-[#2b180d] shadow-[0_4px_0_#2b180d]';

        const avatarSvg = generateDuolingoAvatarSVG(char, isSelectedForDelib);

        const curSus = (gameState.humanSuspicions && gameState.humanSuspicions[char.id] !== undefined) ? gameState.humanSuspicions[char.id] : 40;
        let susColor = 'text-[#78350f] bg-[#fef3c7] border-[#b45309]';
        let susLabel = `🟡 ${curSus}% Neutro`;
        if (curSus <= 25) {
          susColor = 'text-[#166534] bg-[#dcfce7] border-[#15803d]';
          susLabel = `🟢 ${curSus}% Leal`;
        } else if (curSus >= 65) {
          susColor = 'text-[#991b1b] bg-[#fee2e2] border-[#dc2626]';
          susLabel = `🔴 ${curSus}% Traidor`;
        }

        const commClaim = (gameState.botCommodityClaims && gameState.botCommodityClaims[char.id]);

        let deductionUi = '';
        if (char.id !== 0) {
          deductionUi = `
            <div class="w-full pt-2 border-t border-[#2b180d]/15 space-y-1.5 text-left">
              <div class="flex justify-between items-center text-[10px] font-cartoon font-bold">
                <span class="text-[#6b472e]">Suspeição:</span>
                <span class="px-2 py-0.5 rounded-full border text-[10px] font-bold ${susColor}">
                  ${susLabel}
                </span>
              </div>
              
              <!-- Ajuste Fino (+ / - e Slider Contínuo) -->
              <div class="flex items-center gap-1.5 w-full pt-0.5">
                <button type="button" title="Diminuir Suspeita (-5%)" onclick="event.stopPropagation(); adjustPlayerSuspicion(${char.id}, -5)" class="cartoon-btn w-6 h-6 text-xs bg-slate-100 hover:bg-slate-200 text-[#2b180d] p-0 font-bold border-2">-</button>
                <input type="range" min="0" max="100" step="5" value="${curSus}" oninput="event.stopPropagation(); updatePlayerSuspicion(${char.id}, this.value)" class="w-full accent-[#e29547] cursor-pointer h-2 bg-slate-200 rounded-lg">
                <button type="button" title="Aumentar Suspeita (+5%)" onclick="event.stopPropagation(); adjustPlayerSuspicion(${char.id}, 5)" class="cartoon-btn w-6 h-6 text-xs bg-slate-100 hover:bg-slate-200 text-[#2b180d] p-0 font-bold border-2">+</button>
              </div>

              <!-- Atalhos Rápidos de Dossiê -->
              <div class="grid grid-cols-3 gap-1 pt-0.5">
                <button type="button" onclick="event.stopPropagation(); setPlayerDeductionPreset(${char.id}, 'loyal')" class="cartoon-btn py-0.5 text-[8px] ${curSus <= 25 ? 'bg-[#dcfce7] text-[#166534] border-[#15803d]' : 'bg-white text-slate-500'}">
                  🟢 15%
                </button>
                <button type="button" onclick="event.stopPropagation(); setPlayerDeductionPreset(${char.id}, 'neutral')" class="cartoon-btn py-0.5 text-[8px] ${curSus > 25 && curSus < 65 ? 'bg-[#fef3c7] text-[#78350f] border-[#b45309]' : 'bg-white text-slate-500'}">
                  🟡 50%
                </button>
                <button type="button" onclick="event.stopPropagation(); setPlayerDeductionPreset(${char.id}, 'traitor')" class="cartoon-btn py-0.5 text-[8px] ${curSus >= 65 ? 'bg-[#fee2e2] text-[#991b1b] border-[#dc2626]' : 'bg-white text-slate-500'}">
                  🔴 85%
                </button>
              </div>

              ${commClaim ? `
                <div class="text-[9px] font-cartoon font-bold text-center pt-1">
                  ${commClaim.claim ? '<span class="text-[#166534] bg-[#dcfce7] px-2 py-0.5 rounded-full border border-[#15803d]">🌾 Afirma ter Insumo</span>' : '<span class="text-slate-600 bg-slate-100 px-2 py-0.5 rounded-full border border-slate-300">❌ Sem Insumo</span>'}
                </div>
              ` : ''}
            </div>
          `;
        } else {
          deductionUi = `
            <div class="w-full pt-2 border-t border-[#2b180d]/15 text-center">
              <span class="text-[10px] font-cartoon font-bold text-[#0284c7] bg-[#e0f2fe] px-2.5 py-0.5 rounded-full border border-[#0284c7]">
                Você (Auditor Chefe)
              </span>
            </div>
          `;
        }

        container.innerHTML += `
          <div onclick="selectDeliberationMember(${char.id})" class="cursor-pointer cartoon-card-subtle p-3.5 flex flex-col items-center text-center space-y-2 transition-all ${cardRing}">
            <div class="w-24 h-28 relative">
              ${avatarSvg}
            </div>
            <div>
              <h4 class="font-cartoon font-bold text-sm text-[#2b180d]">${char.name}</h4>
              <p class="text-[10px] text-[#6b472e] font-medium">${char.title}</p>
            </div>
            <div class="flex flex-wrap justify-center gap-1">
              ${badgeStatus}
            </div>
            <div class="text-[11px] font-cartoon font-bold text-[#78350f] bg-[#fef3c7] px-2.5 py-0.5 rounded-full border border-[#b45309]">
              ${gameState.tokens[char.id] || 0} 🪙 Ariary
            </div>
            ${deductionUi}
          </div>
        `;
      });
    }

    function renderOpenMarket() {
      const container = document.getElementById('open-market-container');
      if (!container) return;
      container.innerHTML = '';

      const canDraft = gameState.stage === 'BENCH_DIVIDEND';

      // 3 Cartas Abertas do Balcão
      (gameState.openMarket || []).forEach((card, idx) => {
        let badgeColor = 'bg-[#fbf6ec] border-[#2b180d]';
        let icon = '📦';
        if (card.type === 'VN') { badgeColor = 'bg-amber-100 border-amber-600 text-amber-900'; icon = '🌾'; }
        else if (card.type === 'SF') { badgeColor = 'bg-blue-100 border-blue-600 text-blue-900'; icon = '💎'; }
        else if (card.type === 'TI') { badgeColor = 'bg-slate-200 border-slate-600 text-slate-900'; icon = '⚙️'; }
        else if (card.type === 'CO') { badgeColor = 'bg-indigo-100 border-indigo-600 text-indigo-900'; icon = '🔩'; }
        else if (card.type === 'WILD') { badgeColor = 'bg-yellow-200 border-yellow-600 text-yellow-950'; icon = '🌟'; }
        else if (card.type === 'TOXIC') { badgeColor = 'bg-rose-100 border-rose-600 text-rose-950'; icon = '☣️'; }

        const cardAction = canDraft ? `onclick="humanDraftBenchCard('market', ${idx})"` : '';
        const draftStyle = canDraft ? 'cursor-pointer hover:scale-105 ring-4 ring-[#10b981] animate-pulse' : '';

        container.innerHTML += `
          <div ${cardAction} class="cartoon-card-subtle p-3 text-center space-y-1.5 transition-all ${badgeColor} ${draftStyle}">
            <div class="flex justify-between items-center text-[9px] font-cartoon font-bold opacity-75">
              <span>Balcão #${idx + 1}</span>
              <span>Público</span>
            </div>
            <div class="text-2xl">${icon}</div>
            <div class="font-cartoon font-bold text-xs leading-tight">${card.name}</div>
            <div class="font-cartoon font-bold text-sm bg-white/80 py-0.5 rounded-lg border border-black/20">
              ${card.base > 0 ? '+' + card.base : card.base} pts
            </div>
            ${canDraft ? `<div class="text-[9px] font-cartoon font-bold text-[#166534] bg-[#dcfce7] py-0.5 rounded border border-[#15803d]">Pegar Esta Carta ➔</div>` : ''}
          </div>
        `;
      });

      // 4º slot: Topo Fechado (Deck Anônimo)
      const deckCount = gameState.drawPile ? gameState.drawPile.length : 0;
      const deckAction = canDraft ? `onclick="humanDraftBenchCard('deck')"` : '';
      const deckDraftStyle = canDraft ? 'cursor-pointer hover:scale-105 ring-4 ring-[#38bdf8] animate-pulse' : '';

      container.innerHTML += `
        <div ${deckAction} class="cartoon-card-subtle p-3 bg-gradient-to-b from-slate-100 to-slate-200 border-2 border-slate-700 text-center space-y-1.5 transition-all ${deckDraftStyle}">
          <div class="flex justify-between items-center text-[9px] font-cartoon font-bold text-slate-600">
            <span>Monte</span>
            <span>Anônimo</span>
          </div>
          <div class="text-2xl">🎴</div>
          <div class="font-cartoon font-bold text-xs text-slate-800 leading-tight">Topo Fechado</div>
          <div class="font-cartoon font-bold text-sm bg-white/80 py-0.5 rounded-lg border border-slate-400 text-slate-700">
            ${deckCount} Cartas
          </div>
          ${canDraft ? `<div class="text-[9px] font-cartoon font-bold text-[#0369a1] bg-[#e0f2fe] py-0.5 rounded border border-[#0284c7]">Comprar às Cegas ➔</div>` : ''}
        </div>
      `;

      // Atualiza feed
      const feedEl = document.getElementById('market-last-action');
      if (feedEl && gameState.marketLog && gameState.marketLog.length > 0) {
        feedEl.innerHTML = `<strong>Último Movimento:</strong> ${gameState.marketLog[0]}`;
      }
    }

    function renderPlayerHand() {
      const container = document.getElementById('player-hand-container');
      container.innerHTML = '';

      const hand = gameState.hands[0] || [];
      hand.forEach((card, idx) => {
        const isSelected = gameState.humanSelectedCards.includes(idx);
        let badgeColor = 'bg-[#fbf6ec] border-[#2b180d]';
        let icon = '📦';
        if (card.type === 'VN') { badgeColor = 'bg-amber-100 border-amber-600 text-amber-900'; icon = '🌾'; }
        else if (card.type === 'SF') { badgeColor = 'bg-blue-100 border-blue-600 text-blue-900'; icon = '💎'; }
        else if (card.type === 'TI') { badgeColor = 'bg-slate-200 border-slate-600 text-slate-900'; icon = '⚙️'; }
        else if (card.type === 'CO') { badgeColor = 'bg-indigo-100 border-indigo-600 text-indigo-900'; icon = '🔩'; }
        else if (card.type === 'WILD') { badgeColor = 'bg-yellow-200 border-yellow-600 text-yellow-950'; icon = '🌟'; }
        else if (card.type === 'TOXIC') { badgeColor = 'bg-rose-100 border-rose-600 text-rose-950'; icon = '☣️'; }

        const selectable = gameState.stage === 'DEPOSIT' && gameState.proposedCommittee.includes(0);

        container.innerHTML += `
          <div onclick="${selectable ? `toggleHumanCardSelect(${idx})` : ''}" class="${selectable ? 'hand-card-selectable' : 'border-2 rounded-2xl shadow-sm'} p-3.5 ${badgeColor} ${isSelected ? 'hand-card-selected' : ''} space-y-2 text-center transition-all">
            <div class="text-2xl">${icon}</div>
            <div class="font-cartoon font-bold text-xs leading-tight">${card.name}</div>
            <div class="font-cartoon font-bold text-sm bg-white/80 py-0.5 rounded-lg border border-black/20">
              ${card.base > 0 ? '+' + card.base : card.base} pts
            </div>
          </div>
        `;
      });
    }

    // ===================================================
    // RENDERIZAÇÃO DO CARD DE AÇÃO CENTRAL CONFORME A FASE
    // ===================================================
    function renderActionCard() {
      const container = document.getElementById('round-action-container');
      const contract = contractsList[gameState.roundNum - 1];

      // ================= FASE 0: DADO 1d6 DE GOVERNANÇA (DLC) =================
      if (gameState.stage === 'DICE_ROLL') {
        const isRolled = gameState.diceState.rolled;
        const isRolling = gameState.diceState.rolling;
        const rollVal = gameState.diceState.value;
        const missionCard = renderMissionHeaderCard(contract, "PRÉVIA DA MISSÃO");

        let resultBox = '';
        if (isRolling) {
          resultBox = `
            <div class="p-4 bg-amber-50 border-2 border-amber-300 rounded-2xl text-center space-y-1">
              <p class="font-cartoon font-bold text-amber-900 text-sm animate-pulse">🎲 Rolando o Dado 1d6 de Governança...</p>
              <p class="text-xs text-amber-700">1 a 3: Rodada Ordinária | 4 a 6: Diretriz Extraordinária Ativa</p>
            </div>
          `;
        } else if (isRolled) {
          if (rollVal >= 4 && gameState.roundDirective) {
            resultBox = `
              <div class="cartoon-card-subtle p-4 bg-gradient-to-r from-amber-100 via-yellow-50 to-amber-100 border-[3px] border-amber-600 space-y-2 text-center shadow-[0_4px_0_#b45309]">
                <span class="text-xs font-cartoon font-bold text-amber-900 bg-amber-200 px-3 py-1 rounded-full border border-amber-600">
                  🎉 RESULTADO: DADO ${rollVal} • DIRETRIZ EXTRAORDINÁRIA SORTEADA!
                </span>
                <h4 class="font-cartoon text-xl font-bold text-[#2b180d]">${gameState.roundDirective.name}</h4>
                <p class="text-xs font-medium text-[#78350f]">${gameState.roundDirective.desc}</p>
                <div class="inline-block text-[10px] font-cartoon font-bold text-white bg-amber-600 px-2.5 py-0.5 rounded-full">
                  Categoria: ${gameState.roundDirective.cat}
                </div>
              </div>
            `;
          } else {
            resultBox = `
              <div class="cartoon-card-subtle p-4 bg-emerald-50 border-[3px] border-emerald-600 space-y-2 text-center shadow-[0_4px_0_#059669]">
                <span class="text-xs font-cartoon font-bold text-emerald-900 bg-emerald-200 px-3 py-1 rounded-full border border-emerald-600">
                  🏛️ RESULTADO: DADO ${rollVal} • SESSÃO ORDINÁRIA
                </span>
                <h4 class="font-cartoon text-lg font-bold text-emerald-950">Nenhuma Diretriz Extraordinária Ativada</h4>
                <p class="text-xs text-emerald-800">A rodada segue o fluxo clássico de liquidez, governança e cota de insumo.</p>
              </div>
            `;
          }
        } else {
          resultBox = `
            <div class="p-4 bg-white rounded-2xl border-2 border-[#2b180d] text-center space-y-1">
              <p class="font-cartoon font-bold text-sm text-[#2b180d]">Role o Dado de Governança antes de iniciar as nomeações da rodada!</p>
              <p class="text-xs text-[#6b472e]">Conforme o manual oficial (§7.1), resultados 4, 5 ou 6 ativam cartas da DLC.</p>
            </div>
          `;
        }

        container.innerHTML = `
          <div class="space-y-6">
            ${missionCard}

            <div class="cartoon-card p-6 md:p-8 bg-gradient-to-b from-[#fffefc] to-[#fbf5e7] text-center space-y-5 border-[3.5px] border-[#2b180d]">
              <div class="space-y-1">
                <span class="stamp-approved px-4 py-1 text-xs rounded-full">SORTEIO OFICIAL DE DIRETRIZ</span>
                <h3 class="font-cartoon text-2xl md:text-3xl font-bold text-[#2b180d] mt-2">Dado de Governança & Regulatório</h3>
                <p class="text-xs text-[#6b472e]">Rolar 1d6 para verificar se uma Diretriz Extraordinária entra em vigor nesta rodada.</p>
              </div>

              <!-- Animação do Dado 1d6 -->
              <div class="flex justify-center items-center py-2">
                <div class="cursor-pointer" onclick="${!isRolling && !isRolled ? 'rollEventDice()' : ''}">
                  ${generateDiceSVG(rollVal, isRolling)}
                </div>
              </div>

              ${resultBox}

              <div class="flex justify-center gap-3 pt-2">
                ${!isRolled ? `
                  <button onclick="rollEventDice()" ${isRolling ? 'disabled' : ''} class="cartoon-btn px-8 py-4 bg-[#f59e0b] hover:bg-[#d97706] text-white text-base shadow-[0_6px_0_#b45309] ${isRolling ? 'opacity-50 cursor-not-allowed' : ''}">
                    🎲 Rolar Dado de Governança (1d6)
                  </button>
                ` : `
                  <button onclick="proceedFromDiceToProposal()" class="cartoon-btn px-8 py-4 bg-[#10b981] hover:bg-[#059669] text-white text-base shadow-[0_6px_0_#065f46]">
                    Avançar para a Convocação do Comitê ➔
                  </button>
                `}
              </div>
            </div>
          </div>
        `;
      }

      // ================= FASE 1: PROPOSTA DE COMITÊ =================
      else if (gameState.stage === 'PROPOSAL') {
        const isChair = gameState.chairId === 0;
        const chairChar = characters[gameState.chairId];
        const missionCard = renderMissionHeaderCard(contract, "FASE 1: CONVOCAÇÃO & SONDAGEM");

        let memberCards = '';
        characters.forEach(c => {
          const isSelected = gameState.proposedCommittee.includes(c.id);
          const isSupplier = gameState.designatedSupplier === c.id;
          const isThisChair = gameState.chairId === c.id;
          const commClaim = (gameState.botCommodityClaims && gameState.botCommodityClaims[c.id]);

          let statusClaimBadge = '';
          if (c.id === 0) {
            if (gameState.playerDeclaredCommodity === 'has') {
              statusClaimBadge = '<span class="text-[9px] bg-[#dcfce7] text-[#166534] px-2 py-0.5 rounded-full border border-[#15803d] font-bold">🌾 Declarou ter Insumo</span>';
            } else if (gameState.playerDeclaredCommodity === 'none') {
              statusClaimBadge = '<span class="text-[9px] bg-[#fee2e2] text-[#991b1b] px-2 py-0.5 rounded-full border border-[#dc2626] font-bold">❌ Declarou Sem Insumo</span>';
            } else if (gameState.playerDeclaredCommodity === 'liquidity') {
              statusClaimBadge = '<span class="text-[9px] bg-[#e0f2fe] text-[#0369a1] px-2 py-0.5 rounded-full border border-[#0284c7] font-bold">⚡ Foco em Liquidez</span>';
            }
          } else if (commClaim) {
            statusClaimBadge = commClaim.claim 
              ? '<span class="text-[9px] bg-[#dcfce7] text-[#166534] px-2 py-0.5 rounded-full border border-[#15803d] font-bold">🌾 Afirma ter Insumo</span>'
              : '<span class="text-[9px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full border border-slate-300 font-bold">❌ Sem Insumo</span>';
          }

          memberCards += `
            <div class="cartoon-card-subtle p-3.5 bg-white flex flex-col justify-between gap-2.5 transition-all ${isSelected ? 'border-2 border-[#b45309] bg-[#fefce8] ring-2 ring-[#e29547]' : ''}">
              <div class="flex items-start justify-between gap-2">
                <div class="flex items-center gap-2 cursor-pointer" onclick="${isChair ? `toggleCommitteeMember(${c.id})` : ''}">
                  <span class="text-xl">${isSelected ? '✅' : '⚪'}</span>
                  <div>
                    <h5 class="font-cartoon font-bold text-xs text-[#2b180d] flex items-center gap-1">
                      ${c.name} ${isThisChair ? '<span class="text-[9px] bg-[#fde047] text-[#78350f] px-1.5 py-0.2 rounded border border-[#b45309]">CHAIRMAN</span>' : ''}
                    </h5>
                    <p class="text-[10px] text-[#6b472e]">${c.title}</p>
                  </div>
                </div>
                ${statusClaimBadge}
              </div>

              <!-- Ações da Sondagem / Designação -->
              <div class="flex flex-wrap items-center justify-between gap-1.5 pt-2 border-t border-[#2b180d]/10">
                ${c.id !== 0 ? `
                  <button type="button" onclick="inquireBotAboutCommodity(${c.id})" class="cartoon-btn px-2.5 py-1 text-[10px] bg-sky-50 hover:bg-sky-100 text-sky-800 border-sky-400">
                    ❓ Perguntar Insumo
                  </button>
                ` : `
                  <span class="text-[10px] font-bold text-[#0284c7]">Você (Op 0)</span>
                `}

                ${isChair ? `
                  <div class="flex items-center gap-1">
                    <button type="button" onclick="toggleCommitteeMember(${c.id})" class="cartoon-btn px-2 py-0.5 text-[10px] ${isSelected ? 'bg-rose-50 text-rose-700 border-rose-300' : 'bg-emerald-50 text-emerald-700 border-emerald-300'}">
                      ${isSelected ? 'Remover' : 'Escalar'}
                    </button>
                    ${isSelected ? `
                      <button type="button" onclick="setDesignatedSupplier(${c.id})" class="cartoon-btn px-2 py-0.5 text-[10px] ${isSupplier ? 'bg-[#fde047] text-[#78350f]' : 'bg-slate-100 text-slate-600'}">
                        ${isSupplier ? '⭐ Fornecedor' : 'Fornecedor?'}
                      </button>
                    ` : ''}
                  </div>
                ` : ''}
              </div>
            </div>
          `;
        });

        container.innerHTML = `
          <div class="space-y-6">
            ${missionCard}

            <!-- Seção 1: Sua Declaração para a Mesa / Presidente -->
            <div class="bg-[#fbf6ec] border-2 border-[#2b180d] p-4 md:p-5 rounded-3xl space-y-3 shadow-sm">
              <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-1 border-b border-[#2b180d]/15 pb-2">
                <div class="flex items-center gap-2">
                  <span class="text-xl">📢</span>
                  <h4 class="font-cartoon text-base font-bold text-[#2b180d]">Sua Declaração para a Mesa (Pré-Convocação):</h4>
                </div>
                <span class="text-xs text-[#8c4314]">Avise ao Presidente antes da formação do comitê!</span>
              </div>
              
              <div class="flex flex-wrap items-center gap-2 pt-1">
                <button onclick="declarePlayerCommodity('has')" class="cartoon-btn px-3.5 py-2 text-xs ${gameState.playerDeclaredCommodity === 'has' ? 'bg-[#dcfce7] text-[#166534] border-[#15803d]' : 'bg-white hover:bg-emerald-50 text-[#166534] border-emerald-600'} shadow-[0_3px_0_#15803d]">
                  🌾 Avisar: "TENHO o Insumo (${contract.req_commodity})!"
                </button>
                <button onclick="declarePlayerCommodity('none')" class="cartoon-btn px-3.5 py-2 text-xs ${gameState.playerDeclaredCommodity === 'none' ? 'bg-[#fee2e2] text-[#991b1b] border-[#dc2626]' : 'bg-white hover:bg-rose-50 text-[#991b1b] border-rose-600'} shadow-[0_3px_0_#dc2626]">
                  ❌ Avisar: "NÃO TENHO o Insumo (Não me convoquem)!"
                </button>
                <button onclick="declarePlayerCommodity('liquidity')" class="cartoon-btn px-3.5 py-2 text-xs ${gameState.playerDeclaredCommodity === 'liquidity' ? 'bg-[#e0f2fe] text-[#0369a1] border-[#0284c7]' : 'bg-white hover:bg-sky-50 text-[#0369a1] border-sky-600'} shadow-[0_3px_0_#0284c7]">
                  ⚡ Avisar: "Foco em Alta Liquidez Financeira (+pts)"
                </button>
              </div>
            </div>

            <!-- Seção 2: Membros da Mesa & Composição do Comitê -->
            <div class="space-y-3">
              <div class="flex justify-between items-center">
                <h4 class="font-cartoon text-base font-bold text-[#2b180d]">
                  ${isChair ? `Você é o Presidente! Escolha ${contract.committee_size} membros para a operação:` : `${chairChar.name} é o Presidente e propõe o seguinte comitê:`}
                </h4>
                <span class="text-xs font-cartoon font-bold text-[#b45309] bg-[#fef3c7] px-3 py-1 rounded-full border border-[#b45309]">
                  Comitê: ${gameState.proposedCommittee.length} de ${contract.committee_size} membros
                </span>
              </div>
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                ${memberCards}
              </div>
            </div>

            <div class="flex flex-col sm:flex-row justify-between items-center gap-3 pt-3 border-t-2 border-[#2b180d]/15">
              <span class="text-xs text-[#8c4314]">
                ${isChair ? 'Você pode interrogar qualquer membro sobre o insumo antes de concluir a convocação.' : 'Você pode questionar os outros membros e declarar sua situação para o Presidente.'}
              </span>
              <button onclick="confirmProposal()" class="cartoon-btn px-8 py-3.5 bg-[#e29547] hover:bg-[#d97706] text-white text-base shadow-[0_5px_0_#b45309]">
                Formalizar Convocação & Ir para Negociação ➔
              </button>
            </div>
          </div>
        `;
      }

      // ================= FASE 2: DELIBERAÇÃO COM PERSONAGENS DUOLINGO =================
      else if (gameState.stage === 'DELIBERATION') {
        const missionCard = renderMissionHeaderCard(contract, "FASE 2: NEGOCIAÇÃO & PROMESSAS");
        const activeBotId = gameState.deliberationActiveMember !== null ? gameState.deliberationActiveMember : (gameState.proposedCommittee.find(id => id !== 0) || 1);
        const activeChar = characters[activeBotId];
        const promise = gameState.promises[activeBotId] || { points: 3, hasCommodity: true, ariaryBurn: 0, lastAnswer: activeChar.voiceLines.pointsHigh };

        // Tabela de Promessas Consolidadas
        let promiseRows = '';
        let totalPromisedPts = 0;
        gameState.proposedCommittee.forEach(id => {
          const c = characters[id];
          const p = gameState.promises[id];
          const pts = p ? p.points : 0;
          const comm = p ? (p.hasCommodity ? '✅ Garantido' : '❌ Não possui') : 'Aguardando';
          const coins = p ? `${p.ariaryBurn} 🪙` : '0 🪙';
          totalPromisedPts += pts + (p ? (p.ariaryBurn || 0) : 0);

          promiseRows += `
            <tr class="border-b border-[#2b180d]/10 text-xs">
              <td class="py-2 px-3 font-cartoon font-bold text-[#2b180d] flex items-center gap-1.5">
                <span class="w-2.5 h-2.5 rounded-full" style="background: ${c.color}"></span>
                ${c.name}
              </td>
              <td class="py-2 px-3 font-cartoon font-bold text-[#b45309]">+${pts} pts</td>
              <td class="py-2 px-3">${comm}</td>
              <td class="py-2 px-3">${coins}</td>
            </tr>
          `;
        });

        // Balão de fala estilo Duolingo
        const speechBubble = `
          <div class="duolingo-bubble p-5 space-y-2 speech-bubble-pop">
            <div class="flex justify-between items-center">
              <span class="text-xs font-cartoon font-bold text-[#b45309] uppercase flex items-center gap-1.5">
                <span>💬</span> Resposta de ${activeChar.name}:
              </span>
              <span class="text-[11px] font-cartoon font-bold bg-[#fef3c7] text-[#78350f] px-2.5 py-0.5 rounded-full border border-[#b45309]">
                ${activeChar.title}
              </span>
            </div>
            <p class="text-sm md:text-base font-cartoon font-medium text-[#2b180d] leading-relaxed">
              "${promise.lastAnswer || activeChar.bubbleText}"
            </p>
          </div>
        `;

        container.innerHTML = `
          <div class="space-y-6">
            ${missionCard}

            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 border-b-2 border-[#2b180d]/15 pb-3">
              <div>
                <span class="bg-[#10b981] text-white text-xs font-cartoon font-bold px-3 py-0.5 rounded-full border-2 border-[#2b180d]">Fase 2: Mesa de Negociação</span>
                <h3 class="font-cartoon text-2xl font-bold text-[#2b180d] mt-1">Interrogatório & Promessas do Comitê</h3>
                <p class="text-xs text-[#6b472e]">Consulte os dados da missão acima e interrogue cada membro sobre o que entregarão na urna.</p>
              </div>
              <span class="stamp-approved px-4 py-1.5 rounded-2xl text-xs">DELIBERAÇÃO ATIVA</span>
            </div>

            <!-- Interação com o Personagem Ativo (Estilo Duolingo) -->
            <div class="grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
              <div class="md:col-span-4 flex flex-col items-center text-center space-y-2">
                <div class="w-36 h-40">
                  ${generateDuolingoAvatarSVG(activeChar, true)}
                </div>
                <h4 class="font-cartoon text-lg font-bold text-[#2b180d]">${activeChar.name}</h4>
                <div class="flex gap-1.5 justify-center">
                  ${gameState.proposedCommittee.map(id => `
                    <button onclick="selectDeliberationMember(${id})" class="cartoon-btn px-3 py-1 text-xs ${activeBotId === id ? 'bg-[#e29547] text-white' : 'bg-white text-[#2b180d]'}">
                      Op ${id}
                    </button>
                  `).join('')}
                </div>
              </div>

              <div class="md:col-span-8 space-y-4">
                ${speechBubble}

                <!-- Perguntas que o jogador pode fazer -->
                <div class="space-y-2">
                  <span class="text-xs font-cartoon font-bold text-[#2b180d] uppercase">Perguntar a ${activeChar.name}:</span>
                  <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    <button onclick="askCommitteeMember(${activeBotId}, 'points')" class="cartoon-btn p-2.5 text-xs bg-white hover:bg-[#fefce8] text-[#2b180d] text-left flex items-center gap-2">
                      <span>🎯</span> "Quantos pontos de liquidez você garante?"
                    </button>
                    <button onclick="askCommitteeMember(${activeBotId}, 'commodity')" class="cartoon-btn p-2.5 text-xs bg-white hover:bg-[#fefce8] text-[#2b180d] text-left flex items-center gap-2">
                      <span>🌾</span> "Você vai cobrir o insumo exigido?"
                    </button>
                    <button onclick="askCommitteeMember(${activeBotId}, 'ariary')" class="cartoon-btn p-2.5 text-xs bg-white hover:bg-[#fefce8] text-[#2b180d] text-left flex items-center gap-2">
                      <span>🪙</span> "Você vai queimar moedas de Ariary?"
                    </button>
                    <button onclick="askCommitteeMember(${activeBotId}, 'loyalty')" class="cartoon-btn p-2.5 text-xs bg-white hover:bg-[#fefce8] text-[#991b1b] text-left flex items-center gap-2">
                      <span>🔍</span> "Você é leal ao Banco ou vai sabotar?"
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Formulário de Declaração da sua Própria Promessa (se estiver no comitê) -->
            ${gameState.proposedCommittee.includes(0) ? `
              <div class="cartoon-card-subtle p-4 bg-[#fffdfa] space-y-3">
                <div class="flex justify-between items-center">
                  <span class="text-xs font-cartoon font-bold text-[#b45309] uppercase">Sua Declaração Formal (Operador 0):</span>
                  <span class="text-[10px] font-cartoon text-[#166534] bg-[#dcfce7] px-2.5 py-0.5 rounded-full border border-[#15803d]">
                    ${gameState.userPromiseDeclared ? '✅ Promessa Declarada' : 'Pendente'}
                  </span>
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                  <div>
                    <label class="font-bold text-[#2b180d] block mb-1">Pontos Prometidos:</label>
                    <select id="user-declare-pts" class="w-full bg-white border-2 border-[#2b180d] rounded-xl p-2 font-bold">
                      <option value="4">+4 Pontos (Ouro / Safira)</option>
                      <option value="3" selected>+3 Pontos (Titânio)</option>
                      <option value="2">+2 Pontos (Baunilha)</option>
                      <option value="1">+1 Ponto (Cobalto)</option>
                      <option value="0">0 Pontos (Blefe / Sabotagem)</option>
                    </select>
                  </div>
                  <div>
                    <label class="font-bold text-[#2b180d] block mb-1">Insumo Exigido:</label>
                    <select id="user-declare-comm" class="w-full bg-white border-2 border-[#2b180d] rounded-xl p-2 font-bold">
                      <option value="yes" selected>Vou entregar o Insumo ✅</option>
                      <option value="no">Não possuo o Insumo ❌</option>
                    </select>
                  </div>
                  <div>
                    <label class="font-bold text-[#2b180d] block mb-1">Queima de Moedas:</label>
                    <select id="user-declare-ariary" class="w-full bg-white border-2 border-[#2b180d] rounded-xl p-2 font-bold">
                      <option value="0" selected>0 Ariary</option>
                      <option value="1">1 Moeda de Ariary 🪙</option>
                      <option value="2">2 Moedas de Ariary 🪙🪙</option>
                    </select>
                  </div>
                </div>
                <button onclick="declareUserPromise(document.getElementById('user-declare-pts').value, document.getElementById('user-declare-comm').value, document.getElementById('user-declare-ariary').value)" class="cartoon-btn px-6 py-2.5 bg-[#fde047] text-[#78350f] text-xs">
                  📢 Registrar Minha Declaração à Mesa
                </button>
              </div>
            ` : ''}

            <!-- Placar Consolidado de Promessas -->
            <div class="space-y-2">
              <div class="flex justify-between items-center">
                <span class="text-xs font-cartoon font-bold text-[#2b180d] uppercase">Balanço das Promessas da Mesa:</span>
                <span class="text-xs font-cartoon font-bold ${totalPromisedPts >= contract.target ? 'text-[#059669]' : 'text-[#dc2626]'}">
                  Promessa Total: +${totalPromisedPts} pts (Meta: ${contract.target} pts)
                </span>
              </div>
              <div class="overflow-x-auto bg-white rounded-2xl border-2 border-[#2b180d]">
                <table class="w-full text-left">
                  <thead class="bg-[#fbf5e7] border-b-2 border-[#2b180d] text-[11px] font-cartoon text-[#78350f]">
                    <tr>
                      <th class="py-2 px-3">Membro</th>
                      <th class="py-2 px-3">Pontos</th>
                      <th class="py-2 px-3">Insumo</th>
                      <th class="py-2 px-3">Queima</th>
                    </tr>
                  </thead>
                  <tbody>
                    ${promiseRows}
                  </tbody>
                </table>
              </div>
            </div>

            <div class="flex justify-between items-center pt-3 border-t-2 border-[#2b180d]/15">
              <button onclick="gameState.stage = 'PROPOSAL'; renderActionCard();" class="cartoon-btn px-5 py-2.5 bg-slate-100 text-[#475569] text-xs">
                ◀ Rever Composição
              </button>
              <button onclick="proceedToVoting()" class="cartoon-btn px-8 py-3.5 bg-[#10b981] hover:bg-[#059669] text-white text-base shadow-[0_5px_0_#065f46]">
                Prosseguir para Votação da Mesa ➔
              </button>
            </div>
          </div>
        `;
      }

      // ================= FASE 3: VOTAÇÃO =================
      else if (gameState.stage === 'VOTING') {
        const commNames = gameState.proposedCommittee.map(id => id === 0 ? 'Você (Op 0)' : characters[id].name).join(', ');

        container.innerHTML = `
          <div class="space-y-6 text-center py-4">
            <span class="stamp-approved px-4 py-1 rounded-full text-xs">FASE 3: VOTAÇÃO</span>
            <div class="space-y-2">
              <h3 class="font-cartoon text-3xl font-bold text-[#2b180d]">Aprovar Comissão de Operações?</h3>
              <p class="text-xs text-[#6b472e]">Membros convocados: <strong class="text-[#2b180d]">${commNames}</strong></p>
            </div>

            <div class="flex justify-center items-center gap-4 py-4">
              <button onclick="submitHumanVote(true)" class="cartoon-btn px-8 py-4 bg-[#dcfce7] hover:bg-[#bbf7d0] text-[#166534] text-base border-[3px] border-[#15803d] shadow-[0_6px_0_#15803d]">
                ✅ VOTAR SIM (Aprovar)
              </button>
              <button onclick="submitHumanVote(false)" class="cartoon-btn px-8 py-4 bg-[#fee2e2] hover:bg-[#fecdd3] text-[#991b1b] text-base border-[3px] border-[#b91c1c] shadow-[0_6px_0_#b91c1c]">
                ❌ VOTAR NÃO (Vetar)
              </button>
            </div>
            <p class="text-[11px] text-[#8c4314]">São necessários pelo menos 3 votos SIM para aprovar. 3 vetos consecutivos forçam a execução!</p>
          </div>
        `;
      }

      // ================= FASE 4: DEPÓSITO SECRETO NA URNA =================
      else if (gameState.stage === 'DEPOSIT') {
        const inComm = gameState.proposedCommittee.includes(0);
        const missionCard = renderMissionHeaderCard(contract, "METAS DO CONTRATO NA URNA");

        if (inComm) {
          const requiredCost = contract.cost || 1;
          const playerHand = gameState.hands[0] || [];
          const numSelected = gameState.humanSelectedCards.length;
          const isComplete = numSelected === requiredCost;

          let cardsSelectionHtml = '';
          if (playerHand.length === 0) {
            cardsSelectionHtml = `
              <div class="p-4 bg-rose-50 border-2 border-rose-400 rounded-2xl text-center text-rose-800 font-cartoon">
                ⚠️ Você não possui cartas na mão para depositar!
              </div>
            `;
          } else {
            let cardsGrid = '';
            playerHand.forEach((card, idx) => {
              const isSelected = gameState.humanSelectedCards.includes(idx);
              let badgeBg = 'bg-[#fbf6ec] border-[#2b180d]';
              let icon = '📦';
              if (card.type === 'VN') { badgeBg = 'bg-amber-100 border-amber-600 text-amber-900'; icon = '🌾'; }
              else if (card.type === 'SF') { badgeBg = 'bg-blue-100 border-blue-600 text-blue-900'; icon = '💎'; }
              else if (card.type === 'TI') { badgeBg = 'bg-slate-200 border-slate-600 text-slate-900'; icon = '⚙️'; }
              else if (card.type === 'CO') { badgeBg = 'bg-indigo-100 border-indigo-600 text-indigo-900'; icon = '🔩'; }
              else if (card.type === 'WILD') { badgeBg = 'bg-yellow-200 border-yellow-600 text-yellow-950'; icon = '🌟'; }
              else if (card.type === 'TOXIC') { badgeBg = 'bg-rose-100 border-rose-600 text-rose-950'; icon = '☣️'; }

              const isReqCommodity = contract.req_commodity && card.name.toLowerCase().includes(contract.req_commodity.split(' ')[0].toLowerCase());
              const isToxic = card.type === 'TOXIC';

              let hintBadge = '';
              if (isReqCommodity) {
                hintBadge = '<span class="text-[10px] font-cartoon font-bold bg-[#fef08a] text-[#78350f] px-2 py-0.5 rounded-full border border-[#b45309] shadow-sm">⭐ Insumo da Missão</span>';
              } else if (isToxic) {
                hintBadge = '<span class="text-[10px] font-cartoon font-bold bg-[#fee2e2] text-[#991b1b] px-2 py-0.5 rounded-full border border-[#dc2626] shadow-sm">☣️ Ativo Tóxico</span>';
              } else {
                hintBadge = '<span class="text-[10px] text-[#6b472e] font-cartoon">Ativo Comercial</span>';
              }

              const selectedRing = isSelected 
                ? 'ring-4 ring-[#15803d] border-[#15803d] bg-[#dcfce7] scale-105 shadow-[0_8px_0_#15803d]' 
                : 'border-[#2b180d] hover:scale-102 hover:border-[#b45309] shadow-[0_4px_0_#2b180d]';

              cardsGrid += `
                <div onclick="toggleHumanCardSelect(${idx})" class="cursor-pointer border-[3px] rounded-2xl p-3.5 ${badgeBg} ${selectedRing} space-y-2 text-center transition-all select-none relative flex flex-col justify-between">
                  ${isSelected ? '<span class="absolute -top-3 -right-2 bg-[#15803d] text-white text-[11px] font-cartoon font-bold px-2.5 py-0.5 rounded-full border-2 border-[#2b180d] shadow">✓ NA URNA</span>' : ''}
                  <div>
                    <div class="text-3xl mb-1">${icon}</div>
                    <div class="font-cartoon font-bold text-sm leading-tight text-[#2b180d]">${card.name}</div>
                  </div>
                  <div class="space-y-1 mt-1">
                    <div class="font-cartoon font-bold text-sm bg-white/90 py-1 rounded-xl border border-black/20 text-[#2b180d]">
                      ${card.base > 0 ? '+' + card.base : card.base} pts
                    </div>
                    <div>${hintBadge}</div>
                  </div>
                </div>
              `;
            });

            cardsSelectionHtml = `
              <div class="space-y-3 bg-[#fdfaf3] p-4 md:p-5 rounded-3xl border-[2.5px] border-[#2b180d]">
                <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-1 border-b border-[#2b180d]/15 pb-2">
                  <span class="font-cartoon font-bold text-base text-[#2b180d] flex items-center gap-2">
                    <span>🎴 Clique na Carta para Depositar na Urna:</span>
                    <span class="text-xs bg-[#e29547] text-white px-2.5 py-0.5 rounded-full">${numSelected} de ${requiredCost} selecionada(s)</span>
                  </span>
                  <span class="text-xs font-cartoon font-bold ${isComplete ? 'text-[#15803d]' : 'text-[#b45309]'}">
                    ${isComplete ? '✓ Carta pronta para o depósito' : '👉 Clique em uma das suas cartas abaixo para selecionar'}
                  </span>
                </div>
                <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3.5 pt-1">
                  ${cardsGrid}
                </div>
              </div>
            `;
          }

          container.innerHTML = `
            <div class="space-y-6">
              ${missionCard}

              <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 border-b-2 border-[#2b180d]/15 pb-3">
                <div>
                  <span class="bg-[#e29547] text-white text-xs font-cartoon font-bold px-3 py-0.5 rounded-full border-2 border-[#2b180d]">Fase 4: Urna Lacrada</span>
                  <h3 class="font-cartoon text-2xl md:text-3xl font-bold text-[#2b180d] mt-1">Deposite sua Contribuição Secreta</h3>
                  <p class="text-xs text-[#6b472e]">Você foi designado para o Comitê Operacional. Sua carta será depositada em sigilo absoluto na urna do Banco.</p>
                </div>
                <span class="stamp-sabotaged px-4 py-1.5 rounded-2xl text-xs">SIGILO ABSOLUTO</span>
              </div>

              ${cardsSelectionHtml}

              <!-- Queima de Moedas de Ariary -->
              <div class="bg-white p-4 rounded-2xl border-2 border-[#2b180d] flex justify-between items-center">
                <div>
                  <span class="font-cartoon font-bold text-xs text-[#2b180d]">Queimar Moedas de Ariary (+1 pt cada)</span>
                  <p class="text-[10px] text-[#6b472e]">Disponível na sua carteira: ${gameState.tokens[0]} 🪙</p>
                </div>
                <div class="flex items-center gap-2">
                  <button type="button" onclick="adjustHumanCoins(-1)" class="cartoon-btn w-8 h-8 bg-slate-100 text-sm">-</button>
                  <span class="coin-badge px-3.5 py-1 rounded-full text-xs">${gameState.humanCoinsSpent} 🪙</span>
                  <button type="button" onclick="adjustHumanCoins(1)" class="cartoon-btn w-8 h-8 bg-slate-100 text-sm">+</button>
                </div>
              </div>

              <div class="flex flex-col sm:flex-row justify-between items-center gap-3 pt-3 border-t-2 border-[#2b180d]/15">
                <span class="text-xs text-[#8c4314]">
                  ${isComplete ? 'Contribuição pronta para ser lacrada!' : 'Selecione a sua carta acima antes de lacrar.'}
                </span>
                <button onclick="confirmDeposit()" class="cartoon-btn px-8 py-3.5 ${isComplete ? 'bg-[#10b981] hover:bg-[#059669] text-white shadow-[0_5px_0_#065f46]' : 'bg-[#e2e8f0] text-slate-500 shadow-[0_4px_0_#94a3b8]'} text-base">
                  🗳️ Lacrar Contribuição & Abrir Urna ➔
                </button>
              </div>
            </div>
          `;
        } else {
          const commNames = gameState.proposedCommittee.map(id => characters[id].name).join(', ');
          container.innerHTML = `
            <div class="space-y-6">
              ${missionCard}

              <div class="space-y-6 text-center py-6 bg-[#fbf6ec] rounded-3xl border-2 border-[#2b180d] p-6">
                <span class="stamp-approved px-4 py-1.5 rounded-full text-xs">🛋️ VOCÊ ESTÁ NO BANCO DE RESERVAS</span>
                <div class="space-y-2 max-w-lg mx-auto">
                  <h3 class="font-cartoon text-3xl font-bold text-[#2b180d]">Comitê em Sessão Secreta</h3>
                  <p class="text-xs text-[#6b472e]">
                    Você não está escalado neste comitê! Os membros convocados (<strong>${commNames}</strong>) estão depositando suas contribuições em sigilo.
                  </p>
                  <p class="text-[11px] text-[#8c4314]">
                    Como operador no banco, ao final desta rodada você receberá o <strong>Dividendo de Banco</strong> (+1 Ariary e +1 Carta de reposição à sua escolha).
                  </p>
                </div>
                <div class="py-2">
                  <button onclick="confirmDeposit()" class="cartoon-btn px-8 py-4 bg-[#e29547] hover:bg-[#d97706] text-white text-base shadow-[0_6px_0_#b45309]">
                    🗳️ Assistir aos Depósitos e Abrir a Urna ➔
                  </button>
                </div>
              </div>
            </div>
          `;
        }
      }

      // ================= FASE 5: REVELAÇÃO DA URNA & AUDITORIA =================
      else if (gameState.stage === 'REVEAL') {
        const rev = gameState.lastRevealData;
        const outcomeStamp = rev.isSuccess 
          ? '<span class="stamp-approved px-5 py-2 rounded-2xl text-base">CONTRATO APROVADO! 🎉</span>'
          : '<span class="stamp-sabotaged px-5 py-2 rounded-2xl text-base">💥 SABOTAGEM DETECTADA!</span>';

        // Tabela de comparação: O que prometeram vs O que depositaram!
        let auditRows = '';
        rev.auditLog.forEach(row => {
          const char = characters[row.playerId];
          const cardsLabel = row.cards.map(c => `${c.name} (${c.base > 0 ? '+' + c.base : c.base})`).join(', ');
          const coinLabel = row.coins > 0 ? ` +${row.coins}🪙` : '';
          const statusBadge = row.fulfilled 
            ? '<span class="text-xs font-cartoon font-bold text-[#166534] bg-[#dcfce7] px-2.5 py-0.5 rounded-full border border-[#15803d]">Cumpriu ✅</span>'
            : '<span class="text-xs font-cartoon font-bold text-[#991b1b] bg-[#fee2e2] px-2.5 py-0.5 rounded-full border border-[#dc2626]">Mentiu / Sabotou ❌</span>';

          auditRows += `
            <tr class="border-b border-[#2b180d]/10 text-xs">
              <td class="py-3 px-3 font-cartoon font-bold text-[#2b180d] flex items-center gap-1.5">
                <span class="w-2.5 h-2.5 rounded-full" style="background: ${char.color}"></span>
                ${char.name}
              </td>
              <td class="py-3 px-3 text-[#b45309] font-cartoon font-bold">+${row.promised} pts</td>
              <td class="py-3 px-3 font-medium">${cardsLabel}${coinLabel} (= ${row.pointsEarned} pts)</td>
              <td class="py-3 px-3">${statusBadge}</td>
            </tr>
          `;
        });

        container.innerHTML = `
          <div class="space-y-6">
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 border-b-2 border-[#2b180d]/15 pb-4">
              <div>
                <span class="text-xs font-cartoon font-bold text-[#b45309] uppercase">Resultado da Auditoria da Urna</span>
                <h3 class="font-cartoon text-2xl font-bold text-[#2b180d] mt-1">${rev.contract.name}</h3>
                <p class="text-xs text-[#6b472e]">Total Obtido: <strong>${rev.totalPoints} / ${rev.effectiveTarget || rev.contract.target} pts</strong> • Insumo Entregue: <strong>${rev.hasRequiredCommodity ? 'Sim ✅' : 'Não ❌'}</strong></p>
              </div>
              <div>${outcomeStamp}</div>
            </div>

            <!-- Tabela de Comparação de Promessas -->
            <div class="space-y-3">
              <div class="flex justify-between items-center">
                <h4 class="font-cartoon text-base font-bold text-[#2b180d]">Auditoria Forense de Promessas:</h4>
                <span class="text-[11px] text-[#6b472e]">Verifique quem cumpriu o acordo e quem traiu a comissão!</span>
              </div>
              <div class="overflow-x-auto bg-white rounded-2xl border-2 border-[#2b180d] shadow-sm">
                <table class="w-full text-left">
                  <thead class="bg-[#fbf5e7] border-b-2 border-[#2b180d] text-[11px] font-cartoon text-[#78350f]">
                    <tr>
                      <th class="py-2.5 px-3">Operador</th>
                      <th class="py-2.5 px-3">Prometeu na Mesa</th>
                      <th class="py-2.5 px-3">Depositou na Urna</th>
                      <th class="py-2.5 px-3">Veredito</th>
                    </tr>
                  </thead>
                  <tbody>
                    ${auditRows}
                  </tbody>
                </table>
              </div>
            </div>

            <div class="flex justify-end pt-3 border-t-2 border-[#2b180d]/15">
              <button onclick="finishRound()" class="cartoon-btn px-8 py-3.5 bg-[#e29547] hover:bg-[#d97706] text-white text-base shadow-[0_5px_0_#b45309]">
                Prosseguir para Próxima Rodada ➔
              </button>
            </div>
          </div>
        `;
      }

      // ================= FASE DE DIVIDENDO DE BANCO (BENCH RECOMPOSITION) =================
      else if (gameState.stage === 'BENCH_DIVIDEND') {
        const benchCardsButtons = (gameState.openMarket || []).map((card, idx) => `
          <button onclick="humanDraftBenchCard('market', ${idx})" class="cartoon-btn p-3 bg-white hover:bg-[#fefce8] text-[#2b180d] text-xs flex flex-col items-center gap-1 border-2 border-[#b45309] shadow-[0_4px_0_#b45309]">
            <span class="text-xs font-bold text-[#b45309]">Balcão #${idx + 1}</span>
            <span class="font-bold text-sm">${card.name}</span>
            <span class="text-[10px] bg-slate-100 px-2 py-0.5 rounded-full border">${card.base > 0 ? '+' + card.base : card.base} pts</span>
          </button>
        `).join('');

        container.innerHTML = `
          <div class="space-y-6 text-center py-5">
            <span class="stamp-approved px-5 py-2 rounded-2xl text-sm">DIVIDENDO DE BANCO ATIVO</span>
            <div class="space-y-2 max-w-xl mx-auto">
              <h3 class="font-cartoon text-3xl font-bold text-[#2b180d]">Você Descansou no Banco! ☕</h3>
              <p class="text-sm text-[#6b472e]">
                Conforme as regras oficiais v14 (§2), quem fica de fora do comitê acumula <strong>+1 Token de Rendimento 🪙</strong> (Seu saldo: <strong>${gameState.tokens[0]}/3</strong>) e tem o direito de recompor sua carteira com <strong>+1 Carta</strong>.
              </p>
            </div>

            <div class="p-4 bg-[#fef3c7] rounded-2xl border-2 border-[#b45309] max-w-lg mx-auto text-xs text-[#78350f] space-y-1">
              <p class="font-bold">🎯 Escolha onde deseja comprar sua nova carta:</p>
              <p>• <strong>Mercado Aberto:</strong> Compra pública no balcão (sinaliza cooperação aos outros Banqueiros).</p>
              <p>• <strong>Topo Fechado:</strong> Compra anônima/secreta do monte (oculta suas commodities dos estagiários).</p>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-4 gap-3 max-w-2xl mx-auto pt-2">
              ${benchCardsButtons}
              <button onclick="humanDraftBenchCard('deck')" class="cartoon-btn p-3 bg-gradient-to-b from-slate-100 to-slate-200 hover:bg-slate-300 text-slate-800 text-xs flex flex-col items-center gap-1 border-2 border-slate-700 shadow-[0_4px_0_#334155]">
                <span class="text-xs font-bold text-slate-700">Monte Anônimo</span>
                <span class="font-bold text-sm">Topo Fechado</span>
                <span class="text-[10px] bg-white px-2 py-0.5 rounded-full border">Carta Secreta 🎴</span>
              </button>
            </div>
            <p class="text-[11px] text-[#8c4314]">Você também pode clicar diretamente nas cartas do Mercado de Balcão Aberto acima!</p>
          </div>
        `;
      }

      // ================= FASE 6: FIM DE PARTIDA =================
      else if (gameState.stage === 'GAME_OVER') {
        const bankerWon = gameState.bankerScore >= 4 || (gameState.bankerScore > gameState.internScore);
        const winnerTitle = bankerWon ? '🏆 VITÓRIA DO CONSELHO BTG!' : '💥 VITÓRIA DOS INFILTRADOS!';
        const winColor = bankerWon ? 'bg-[#dcfce7] text-[#166534] border-[#15803d]' : 'bg-[#fee2e2] text-[#991b1b] border-[#dc2626]';

        let rosterReveal = '';
        characters.forEach(c => {
          const role = gameState.roles[c.id];
          const badge = role === 'Banqueiro' ? 'bg-[#e0f2fe] text-[#0369a1] border-[#0284c7]' : 'bg-[#fee2e2] text-[#991b1b] border-[#dc2626]';
          rosterReveal += `
            <div class="flex justify-between items-center p-3 bg-white rounded-2xl border-2 border-[#2b180d]">
              <span class="font-cartoon font-bold text-sm text-[#2b180d] flex items-center gap-2">
                <span>${role === 'Banqueiro' ? '🏛️' : '🕵️'}</span> ${c.name}
              </span>
              <span class="text-xs px-3 py-0.5 rounded-full border-2 font-cartoon font-bold ${badge} uppercase">${role}</span>
            </div>
          `;
        });

        container.innerHTML = `
          <div class="space-y-6 text-center py-6">
            <div class="inline-block p-4 rounded-3xl border-4 ${winColor} shadow-[0_8px_0_#2b180d]">
              <h2 class="font-cartoon text-3xl md:text-4xl font-bold">${winnerTitle}</h2>
              <p class="text-sm font-cartoon mt-1">Placar Final: Banqueiros ${gameState.bankerScore} x ${gameState.internScore} Infiltrados</p>
            </div>

            <div class="space-y-3 max-w-xl mx-auto text-left">
              <h4 class="font-cartoon text-base font-bold text-[#2b180d] text-center">Revelação das Identidades Reais de Toda a Mesa:</h4>
              <div class="space-y-2">
                ${rosterReveal}
              </div>
            </div>

            <div class="flex justify-center gap-4 pt-4">
              <button onclick="restartGameFlow()" class="cartoon-btn px-8 py-4 bg-[#10b981] text-white text-base shadow-[0_6px_0_#065f46]">
                🔄 Jogar Outra Partida
              </button>
              <a href="match_visualizer.html" class="cartoon-btn px-8 py-4 bg-[#fde047] text-[#451a03] text-base shadow-[0_6px_0_#b45309]">
                📊 Ver Traces da IA Monte Carlo
              </a>
            </div>
          </div>
        `;
      }
    }

    // Inicialização ao carregar a página:
    selectPlayRole('Banqueiro');
    startNewGame();
    // Exibe o painel de setup inicialmente para que o jogador possa escolher as opções antes de clicar em Iniciar
    const initialSetupPanel = document.getElementById('game-setup-panel');
    if (initialSetupPanel) {
      initialSetupPanel.classList.remove('hidden');
    }
  </script>
</body>
</html>
"""

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Generated standalone game at {out_path} ({len(html_content)} bytes)")

if __name__ == '__main__':
    build_game_html()
