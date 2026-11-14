---
version: 1
slug: "web-index-html"
primary_target: "web/index.html"
related_targets: []
---

# Busca de apartamentos (web/index.html)

Modo: Operate. Celular primeiro (chegada pelo aviso do Telegram), desktop para comparar.
Tarefa: decidir rápido o que visitar (favoritar, descartar, marcar alugado) e ver, por alerta, o que é novo nas últimas 24h, 7 dias e mês.
Escopo desta rodada: identidade nova (modo claro), aba Alertas = lista de alertas + oportunidades novas por período, criar/editar alerta em painel próprio, alugado automático (saiu do ar) e manual, desabilitado com aviso.

## Direction contract

THESIS: Cada anúncio é uma placa de imobiliária: faixa amarela com o total, letra condensada preta, tarja vermelha ALUGADO colada por cima. Recusa a grade de cards brancos com coração dos portais.
OWN-WORLD: Fundo branco-gelo, amarelo de placa em faixas cheias (cabeçalho, faixa de preço, aba ativa), preto em bordas de 2px e texto, vermelho só para ALUGADO e erros. Archivo Narrow em caixa-alta para a voz de placa, Archivo no corpo. Cantos retos, sem sombra, ícones em traço de 2px.
STORY: Quem chega do Telegram lê o total na faixa amarela, entende o bairro e decide em um toque; na aba Alertas vê só o que cada alerta trouxe de novo, por período.
FIRST VIEWPORT: Em 390px: cabeçalho amarelo com nome e status das fontes; barra preta de abas com a ativa em amarelo; primeiro card com foto, faixa ALUGA-SE + bairro + total, endereço, specs e ações Favoritar, Descartar, Alugado. Assinatura: a tarja ALUGADO diagonal, que cola uma vez ao marcar.
FORM: Placa de Aluga-se, primeira da lista ordenada (escolha do Impeccable), seed fe51a84f.
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
