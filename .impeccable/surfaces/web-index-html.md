---
version: 1
slug: "web-index-html"
primary_target: "web/index.html"
related_targets: []
---

# Busca de apartamentos (web/index.html)

Modo: Operate. Celular primeiro (chegada pelo aviso do Telegram), desktop para comparar. Só modo claro (pedido do usuário).
Tarefa: decidir rápido o que visitar (favoritar, descartar, marcar alugado), ver por alerta o que é novo nas últimas 24h, 7 dias e mês, e pedir uma busca agora.
Escopo desta rodada: troca do mundo visual (pedido: mais frio e clean, sem o amarelo e preto blocado), correção de todos os achados do audit, botão "Buscar agora" (pedido gravado no Supabase, atendido pelo PC), agrupamento por região opcional (a ordenação vale dentro de cada grupo).
Mantidos por pedido: tarja ALUGADO diagonal vermelha, total como maior número do card, agrupamento por região.

## Direction contract

THESIS: Cada anúncio é uma ficha de vistoria: os itens que decidem (pet, gás, cozinha, andar, vaga) vêm conferidos em quadros com ✓, ✗ ou em branco tracejado quando o anúncio não diz. Recusa os cards arredondados com coração e chips coloridos dos portais.
OWN-WORLD: Fundo cinza-azulado frio, ficha branca de borda fina, campos pautados com rótulo em versalete pequeno, valores em tinta de caneta azul (total, marcas, aba ativa), texto em ardósia. Vermelho só para o carimbo ALUGADO, exclusões e erros. Public Sans com algarismos tabulares. Cantos de 6 a 8px, sem sombra; ícones de traço 2px.
STORY: Quem chega do Telegram lê o total em azul no campo TOTAL/MÊS, confere o quadro de itens e decide; descartar recolhe a ficha e a próxima sobe; na aba Alertas vê só o que cada alerta trouxe de novo; "Buscar agora" mostra fila, busca e resultado.
FIRST VIEWPORT: Em 390px: cabeçalho branco com nome, "17 em análise · 4 novos hoje", status das fontes e o botão Buscar agora; abas em grade de 5 com sublinhado azul na ativa; barra de filtros recolhida; primeira ficha com foto, linha Endereço | Total/mês, quadro de 4 itens e ações Favoritar, Descartar, Alugado. Assinatura: o carimbo ALUGADO diagonal e o quadro de itens conferidos; raises: campos em posição fixa (painel de embarque), a pauta é a grade do card (Crouwel), decidir e seguir (feed), um componente de valor em três escalas (Emigre), estados como estágios da mesma ficha (fólio).
FORM: Ficha de vistoria, candidata 3 da minha lista ordenada (sorteio), seed 4efb68b1.
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
