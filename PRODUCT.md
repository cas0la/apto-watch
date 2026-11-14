# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Duas pessoas que vão morar juntas e procuram um apartamento para alugar na Grande Florianópolis
(Pedra Branca em Palhoça, São José e o continente/centro de Florianópolis). Usam a plataforma
**principalmente no celular**, muitas vezes chegando por um aviso do Telegram; o desktop serve para
comparar com calma. O trabalho delas: não perder um bom apartamento, decidir juntas o que visitar e
descartar o resto sem rever a mesma coisa duas vezes.

## Product Purpose

Agregador pessoal de anúncios de aluguel: junta imobiliárias (lidas automaticamente) e portais
(VivaReal, ZAP, OLX, por coleta assistida) numa lista só, filtrada por critérios que os portais não
oferecem. Sucesso = encontrar e visitar os apartamentos certos cedo, antes de serem alugados.

## Positioning

- Uma lista para várias fontes, com o mesmo imóvel de dois sites juntado num card.
- Critérios descritos em texto livre (obrigatório, desejável, diferencial), traduzidos pelo Claude Code.
- Lê o anúncio por elas: gás, cozinha separada, andar, pet, vaga só de moto, prédio sem elevador,
  referências próximas (OpenStreetMap).
- Memória compartilhada: favoritos e descartes das duas pessoas; um descartado que baixa de preço volta.
- Alertas próprios no Telegram, cada um com suas condições.

## Operating Context

- Watcher no PC do usuário (systemd, a cada 3 h) para fontes que aceitam robô identificado; coleta
  assistida via Chrome para portais que recusam robôs. Dados no Supabase; página no GitHub Pages.
- Alertas chegam num canal do Telegram; o toque leva à página.
- Valores em reais; total = aluguel + condomínio (IPTU à parte, período varia por anúncio).

## Capabilities and Constraints

- Abas: Em análise, Não favoritados, Favoritos, Descartados, Alertas.
- Alertas: vários; cada um lista as **oportunidades = anúncios novos** que atenderam às condições,
  agrupadas em Últimas 24h, Últimos 7 dias e Último mês. Reduções de preço não contam como oportunidade
  (continuam como etiqueta nos cards e aviso no Telegram).
- Apartamento alugado: **automático** (anúncio saiu do ar na fonte → "Provavelmente alugado") **e manual**
  (botão "Alugado"); aparece desabilitado com o aviso.
- Página estática (HTML/CSS/JS sem build) com supabase-js; login por link mágico; só membros veem dados.
- Volume típico: 50–300 anúncios ativos; 10–40 fotos por anúncio; poucos alertas (1–6).

## Evidence on Hand

- 73 anúncios reais e 66 marcas da busca de 06/11/2026 (`seed/`, fora do git).
- Fotos hotlinkadas das fontes (VivaReal, Ibagy, QuintoAndar, OLX).
- Não há marca, logo ou identidade visual prévia.

## Product Principles

- Decidir rápido no celular: preço total, onde fica e o que muda a decisão aparecem antes de tudo.
- Nunca esconder o que o anúncio não diz: "não informado" é informação.
- O que as duas pessoas marcam é sagrado: nada do sistema sobrescreve favoritos e descartes.
- Honestidade sobre a origem: cada dado mostra de onde veio e quando foi visto.
