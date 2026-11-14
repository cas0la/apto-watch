---
name: Busca de apartamentos
description: Personal rental-listing aggregator, drawn as a real-estate "Aluga-se" sign.
colors:
  ground: "#f6f5f1"
  sheet: "#ffffff"
  sign: "#ffd23f"
  ink: "#141414"
  ink-2: "#3d3d3a"
  muted: "#686862"
  rule: "#d9d7cf"
  chip: "#efeee8"
  tarja: "#d7261e"
  tarja-ink: "#ffffff"
  ink-hover: "#2b2b2b"
  sign-faded: "#e9e7df"
  sign-wash: "#fbf6dd"
  on-ink: "#f1efe6"
  on-ink-2: "#b9b6aa"
typography:
  display:
    fontFamily: "Archivo Narrow, Arial Narrow, sans-serif"
    fontSize: "clamp(26px, 6.4vw, 40px)"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "0.005em"
  price:
    fontFamily: "Archivo Narrow, Arial Narrow, sans-serif"
    fontSize: "30px"
    fontWeight: 700
    lineHeight: 1
  figure:
    fontFamily: "Archivo Narrow, Arial Narrow, sans-serif"
    fontSize: "28px"
    fontWeight: 700
    lineHeight: 1
  headline:
    fontFamily: "Archivo Narrow, Arial Narrow, sans-serif"
    fontSize: "22px"
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "0.01em"
  title:
    fontFamily: "Archivo Narrow, Arial Narrow, sans-serif"
    fontSize: "16px"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "0.03em"
  tab:
    fontFamily: "Archivo Narrow, Arial Narrow, sans-serif"
    fontSize: "14px"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "0.04em"
  label:
    fontFamily: "Archivo Narrow, Arial Narrow, sans-serif"
    fontSize: "13px"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "0.05em"
  flag:
    fontFamily: "Archivo Narrow, Arial Narrow, sans-serif"
    fontSize: "12px"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "0.06em"
  body:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.5
    fontFeature: "tnum"
  address:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 600
    lineHeight: 1.3
  body-sm:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.5
  caption:
    fontFamily: "Archivo, system-ui, sans-serif"
    fontSize: "12px"
    fontWeight: 600
    lineHeight: 1
rounded:
  sign: "2px"
spacing:
  tight: "6px"
  stack: "10px"
  card: "12px"
  gap: "16px"
components:
  button:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.sign}"
    padding: "0 10px"
    height: "44px"
  button-hover:
    backgroundColor: "{colors.sign}"
    textColor: "{colors.ink}"
  button-pressed:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.sign}"
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.sign}"
    typography: "{typography.label}"
    rounded: "{rounded.sign}"
    padding: "0 10px"
    height: "44px"
  button-primary-hover:
    backgroundColor: "{colors.ink-hover}"
    textColor: "{colors.sign}"
  button-danger:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.tarja}"
    typography: "{typography.label}"
    rounded: "{rounded.sign}"
    height: "44px"
  button-danger-hover:
    backgroundColor: "{colors.tarja}"
    textColor: "{colors.tarja-ink}"
  tab:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.on-ink}"
    typography: "{typography.tab}"
    padding: "14px 12px"
  tab-active:
    backgroundColor: "{colors.sign}"
    textColor: "{colors.ink}"
  sign-strip:
    backgroundColor: "{colors.sign}"
    textColor: "{colors.ink}"
    typography: "{typography.price}"
    padding: "8px 12px"
  sign-strip-rented:
    backgroundColor: "{colors.sign-faded}"
    textColor: "{colors.ink}"
  card:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sign}"
    padding: "12px 12px 14px"
  tarja:
    backgroundColor: "{colors.tarja}"
    textColor: "{colors.tarja-ink}"
    typography: "{typography.price}"
    padding: "8px 0"
  mini-tarja:
    backgroundColor: "{colors.tarja}"
    textColor: "{colors.tarja-ink}"
    padding: "3px 0"
  flag:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.sign}"
    typography: "{typography.flag}"
    padding: "6px 8px"
  flag-light:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.ink}"
    typography: "{typography.flag}"
    padding: "4px 6px"
  period:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.ink}"
    typography: "{typography.figure}"
    padding: "10px"
  period-active:
    backgroundColor: "{colors.sign}"
    textColor: "{colors.ink}"
  input:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sign}"
    padding: "7px 9px"
    height: "40px"
  tag:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.ink}"
    typography: "{typography.caption}"
    rounded: "{rounded.sign}"
    padding: "5px 7px"
  tag-good:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.sheet}"
---

# Design System: Busca de apartamentos

## Overview

**Creative North Star: "Placa de Aluga-se"**

Every listing is a real-estate rental sign. A solid yellow strip carries the word ALUGA-SE, the neighbourhood and the condensed monthly total; black condensed capitals and 2px black rules frame it; a red ALUGADO band is pasted diagonally over the photo when the flat is gone. The page reads like a wall of those signs on an off-white ground, not like a portal's grid of soft white cards with heart icons.

The system is light mode only, mobile-first and dense. One column on a phone (390px is the reference width), an auto-fill grid on desktop for calm comparison. Decoration is limited to sign material: full-bleed yellow strips, black bars, square corners, flat ink. Depth comes from borders and colour blocks, never from shadows. The only motion is the tarja "sticking" once when a listing is marked rented.

**Key Characteristics:**
- Yellow is a sign colour, used in full strips (header, price strip, active tab, active period, hover), never as a thin accent.
- Black does the structural work: 2px rules, the tab bar, pressed buttons, flags.
- Red appears only for ALUGADO and errors.
- Archivo Narrow uppercase is the sign voice; Archivo is the reading voice.
- Square corners (2px), no shadows, 2px-stroke line icons.

## Colors

A three-ink sign palette (yellow, black, red) printed on warm off-white paper, with a short neutral ladder for secondary text and hairlines.

### Primary
- **Placa Yellow** (sign): the sign itself. Header band, the ALUGA-SE price strip, the active tab, the active period button, button hover, text selection, and the yellow text on black pressed buttons and flags. Also the browser `theme-color`.
- **Faded Placa** (sign-faded): the price strip of a rented listing; a sign left in the sun.
- **Placa Wash** (sign-wash): hover fill on alert opportunity rows; the only tint of yellow.

### Secondary
- **Tarja Red** (tarja): the ALUGADO band, the mini-tarja on alert rows, the rented-note border and its bold lead, the danger button, sync errors and a failing source dot.
- **Tarja Ink** (tarja-ink): white lettering on the red band and on the danger button hover.

### Neutral
- **Sign Black** (ink): text, 2px borders, the tab bar background, pressed and primary buttons, flags, focus rings, checkbox and range accents.
- **Ink Hover** (ink-hover): hover on black primary buttons.
- **Graphite** (ink-2): secondary text (breakdown, conditions, form labels, period labels), the border of a rented card.
- **Muted Stone** (muted): tertiary text (hints, source tag, listing code, `h2` counts).
- **Off-white Ground** (ground): page background and the opened-opportunity well.
- **Sheet White** (sheet): cards, alert blocks, forms, inputs, default buttons, filters bar.
- **Hairline** (rule): 1px internal separators (filters bar, details, links row, opportunity rows) and the source tag border.
- **Chip** (chip): photo placeholder and the paused pill.
- **On-ink** (on-ink) and **On-ink Dim** (on-ink-2): tab labels and tab counts on the black bar.

### Named Rules
**The Three Inks Rule.** Yellow, black and red are the only chromatic statements. Every other value is a neutral step between ink and sheet.

**The Red Means Gone Rule.** Tarja red marks a rented listing, a destructive action or an error. It never decorates.

**The Full Strip Rule.** Yellow is applied as a solid block that fills its container's width (strip, band, tab cell, period cell). It is not used for thin underlines, dots or text on white.

## Typography

**Display Font:** Archivo Narrow (with Arial Narrow, sans-serif), weights 500/600/700
**Body Font:** Archivo (with system-ui, sans-serif), weights 400/500/600/800

**Character:** Archivo Narrow in capitals is the lettering painted on the sign; Archivo is the small print an agent writes underneath. Body text uses tabular figures so prices align.

### Hierarchy
- **Display** (700, clamp(26px, 6.4vw, 40px), 1, uppercase): the page title in the yellow header only.
- **Price** (700, 30px, 1): the total in the ALUGA-SE strip. The single largest number on a card.
- **Figure** (700, 28px, 1): period counts in the alert block. Opportunity-row totals use the same voice at 22px.
- **Headline** (700, 22px, 1.1, uppercase, 0.01em): region headings and alert names (forms use 20px).
- **Title** (700, 16px, 1.2, uppercase, 0.03em): the header summary line ("17 EM ANÁLISE · 4 NOVOS HOJE").
- **Tab** (600, 14px, 1, uppercase, 0.04em; 12px and 0.02em at ≤420px): tab labels.
- **Label** (700, 13px, uppercase, 0.05em): buttons, the strip's ALUGA-SE line, details summaries, filter summary, count. Period labels use 600 12px.
- **Flag** (700, 12px, uppercase, 0.06em; pill 11px/0.08em; mini-tarja 10px/0.14em): small sign plates.
- **Body** (Archivo 400, 15px, 1.5): running text; ledes cap at 66ch.
- **Address** (Archivo 600, 16px, 1.3): the street line, with specs below at 500 14px.
- **Body-sm** (Archivo 13px): breakdown, conditions, notes, references, rent note.
- **Caption** (Archivo 600, 12px): tags, photo counter, "há 3 h" timestamps, hints (500).

### Named Rules
**The Sign Voice Rule.** Anything that would be painted on a sign (titles, prices, labels, buttons, tabs, flags) is Archivo Narrow uppercase with positive tracking. Anything a person reads as a sentence is Archivo in sentence case.

**The Total Leads Rule.** On a listing, the total in the strip is the largest type after the page title. Nothing on the card competes with it.

## Layout

Single centred column, max 1200px, side gutters max(16px, safe-area inset). The header and black tab bar run full-bleed; the tab bar is sticky at the top. Listings sit in an auto-fill grid with a 350px minimum track and 16px gap, so phones get one column and desktop gets three. A single-listing view caps the card at 560px; an opened opportunity card caps at 520px.

Spacing is tight and sign-like: 12px card padding, 10px vertical stack inside a card, 6px between tags, buttons and flags, 16px between cards. Sections open with 30px above region headings.

Breakpoints are two:
- **≤420px:** the tab bar becomes a 5-column grid with stacked short label + count (min 52px tall); filters collapse into a "Filtros" disclosure with a two-column grid; card action buttons tighten to 12px type with 16px icons.
- **≥900px:** card actions shrink to content width and left-align; alert opportunities run in two columns separated by a hairline.

## Elevation & Depth

Flat. There is no `box-shadow` anywhere in the system. Layering is expressed by colour blocks and rules: a 3px black rule under the yellow header, a black bar for navigation, 2px black frames on cards and alert blocks, and a 3px outline added around a favourited card. The opened opportunity sits in a ground-coloured well under a 2px rule.

### Named Rules
**The No Shadow Rule.** Signs are flat. Separate surfaces with a 2px ink rule or a colour change, never with a shadow or blur.

## Shapes

Square-cornered plates with a 2px radius that only takes the edge off. The border language has four weights, each with a job: 2px solid ink for every frame (cards, alerts, buttons, inputs, strip top and bottom, period dividers); 3px for emphasis (header bottom rule, favourite outline); 1.5px for small plates (tags, notes); 1px hairline in rule colour for internal separators. A dashed border means provisional: "semimobiliado"/warning tags, free-text notes and a paused alert. Icons are SVG line icons at 18px, 2px stroke, square caps and mitred joins. The tarja is the one diagonal in the system, rotated -14deg and allowed to overrun its photo.

## Components

### Buttons
Blunt sign plates.
- **Shape:** square plate (2px radius), 2px ink border, min height 44px (38px in alert actions, 36px in the rent note).
- **Default:** sheet background, ink label in the label voice, optional 18px line icon left of the label.
- **Hover:** fills Placa Yellow; 150ms background transition, removed under reduced motion.
- **Pressed (`aria-pressed=true`):** ink fill with yellow label. Used for Favorito, Descartado ("Voltar") and Alugado.
- **Primary:** ink fill with yellow label; hover lifts to ink-hover. Used for "Novo alerta" and the login submit.
- **Danger:** red label and border on sheet; hover fills red with white label. Used for Excluir.
- **Disabled:** 40% opacity on sheet. **Pressed + disabled** keeps the ink fill and yellow label at 55% opacity, so a rented listing still shows which mark was on.
- **Focus:** 2.5px ink outline, 2px offset (yellow and inset -3px on the tab bar).

### Chips
- **Tags:** Archivo 600 12px, 1.5px ink border. Good facts ("gás encanado", "aceita pet") invert to ink fill with white text; warnings ("semimobiliado", "condomínio não informado") use a dashed border; the source tag drops to a hairline border and muted text.
- **Pill:** alert status. "Ativo" is ink with yellow lettering; "Pausado" is chip with graphite.

### Cards / Containers
- **Corner Style:** 2px.
- **Background:** sheet on ground.
- **Shadow Strategy:** none (see Elevation & Depth).
- **Border:** 2px ink; favourite adds a 3px ink outline; rented switches the frame to graphite.
- **Internal Padding:** 12px sides, 14px bottom, 10px stack.
- **Order:** photo carousel (snap-scroll, square nav buttons, ink photo counter), ALUGA-SE strip, body (rent note if rented, breakdown, address and specs, tags, note, actions, "Perto daqui" and description disclosures, links row).
- **Discarded:** photo, address, breakdown and tags drop to 60% opacity.

### Inputs / Fields
- **Style:** sheet background, 2px ink border, 2px radius, 7px 9px padding, min 40px, Archivo 500 15px.
- **Checkbox and range:** native controls with ink accent colour.
- **Focus:** the global 2.5px ink outline.

### Navigation
- **Header:** full-bleed yellow band with the display title, the summary line, source status (8px square ink dots, red when a source fails) and the sync line; 3px ink rule below.
- **Tab bar:** sticky full-bleed black bar. Tabs are on-ink sign voice with an on-ink-2 count. The active tab is a solid yellow cell with ink text and count. Above 420px the tabs scroll horizontally, with a fade mask when they overflow; at ≤420px they become a 5-column grid with short labels ("Análise", "Não fav.", "Favoritos", "Descartes", "Alertas") over the count.
- **Back link:** in single-listing view, an uppercase "Ver a lista" with a left chevron.

### ALUGA-SE Strip (signature)
A full-width yellow band between photo and body, 2px ink rules top and bottom, 8px 12px padding. Left: "ALUGA-SE · {bairro}" in the label voice. Right: the total in the price voice, with the previous total struck through above it in 12px graphite when the price dropped. On a rented listing the band turns sign-faded.

### ALUGADO Tarja (signature)
A red band lettered "ALUGADO" in white (700, clamp(22px, 7vw, 30px), 0.18em tracking), rotated -14deg across the photo and overrunning it by 20% each side. Photos go grayscale at 65% opacity underneath, and the card's flags are hidden. On the action that marks a listing rented, it sticks once: 450ms from 1.25 scale and -6deg to rest, cubic-bezier(.16, 1, .3, 1); no animation under reduced motion. A rent note sits at the top of the body in a 2px red frame:
- **Automatic:** "**Provavelmente alugado.** Saiu do ar no {fonte} em {data}." No undo; the Alugado button shows pressed + disabled.
- **Manual:** "**Marcado como alugado.** Por {pessoa} em {data}." with a "Desfazer" button (undo icon); the Alugado button stays pressed and active.

Either way Favoritar and Descartar are disabled.
- **Mini-tarja:** on alert opportunity rows, the same red band at 10px across the 96×72 thumbnail, with the thumbnail grayscale and the total in muted.

### Flags
Small plates pinned to the photo's top-left. "Novo" and "Baixou R$ x" are ink plates with yellow lettering. "Favorito · {pessoa}", "Descartado · {pessoa}" and "Era descartado" (a reopened discard whose price dropped) are light plates: sheet, ink lettering, 2px ink border.

### Alert Block
A sheet container with a 2px ink frame (dashed when paused). The top holds the alert name (headline voice), status pill, conditions line (body-sm, graphite) and Editar / Pausar / Excluir buttons. Under a 2px rule, three equal period cells divided by 2px ink: "Últimas 24h", "Últimos 7 dias", "Último mês", each a period label over its count in the figure voice. The selected cell fills yellow. Below, opportunity rows (96×72 thumbnail, 22px total, neighbourhood and specs, relative time), separated by hairlines, wash-yellow on hover, solid yellow when expanded; an expanded row opens the full card in a ground-coloured well.

## Do's and Don'ts

### Do:
- **Do** put the total in the yellow strip at 30px Archivo Narrow 700 and keep it the largest number on the card.
- **Do** frame every surface and control with a 2px ink border and a 2px radius.
- **Do** show state with colour blocks: yellow fill for active/hover, ink fill with yellow lettering for pressed.
- **Do** keep a rented listing's pressed mark visible when disabled (ink fill, yellow label, 55% opacity).
- **Do** use the dashed border for provisional or paused things only.
- **Do** draw icons as 2px-stroke SVG lines with square caps.

### Don't:
- **Don't** add shadows, blur or gradients to surfaces (the tab bar's overflow fade mask is functional, not a surface).
- **Don't** use tarja red for anything except rented, destructive and error states.
- **Don't** round corners beyond 2px or build soft white cards with heart overlays like the portals.
- **Don't** use yellow as text on white or as a thin accent line.
- **Don't** add a dark mode; the sign is printed on light stock.
