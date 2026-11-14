---
name: Busca de apartamentos
description: Personal rental-listing aggregator, drawn as an inspection sheet (ficha de vistoria).
colors:
  pen: "#1f4fd1"
  pen-deep: "#173ea8"
  pen-wash: "#e8eefc"
  pen-soft: "#a9bff5"
  stamp: "#c8322b"
  stamp-deep: "#a3241f"
  stamp-wash: "#fbecea"
  ok: "#2f7d55"
  ground: "#eef1f4"
  sheet: "#ffffff"
  ink: "#1c2733"
  ink-2: "#4a5867"
  muted: "#5f6c79"
  rule: "#c9d2dc"
  hair: "#e3e8ee"
  chip: "#dde3e9"
  hover: "#f5f7fa"
typography:
  total:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "28px"
    fontWeight: 800
    lineHeight: 1
    letterSpacing: "-0.02em"
    fontFeature: "tnum"
  total-row:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "22px"
    fontWeight: 800
    lineHeight: 1
    letterSpacing: "-0.02em"
    fontFeature: "tnum"
  figure:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "20px"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "-0.01em"
    fontFeature: "tnum"
  headline:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "clamp(18px, 4.6vw, 22px)"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.01em"
  title:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "16px"
    fontWeight: 600
    lineHeight: 1.3
  body:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.5
    fontFeature: "tnum"
  control:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "14px"
    fontWeight: 600
    lineHeight: 1
  section:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "12px"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "0.08em"
  label:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "11px"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "0.08em"
  stamp:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "clamp(22px, 7vw, 28px)"
    fontWeight: 800
    lineHeight: 1
    letterSpacing: "0.24em"
rounded:
  tag: "4px"
  control: "6px"
  sheet: "8px"
  pill: "10px"
  round: "50%"
spacing:
  tight: "6px"
  field: "12px"
  gap: "16px"
  section: "28px"
components:
  button:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.ink}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "0 12px"
    height: "44px"
  button-hover:
    backgroundColor: "{colors.hover}"
  button-primary:
    backgroundColor: "{colors.pen}"
    textColor: "{colors.sheet}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "0 12px"
    height: "44px"
  button-primary-hover:
    backgroundColor: "{colors.pen-deep}"
  button-pressed:
    backgroundColor: "{colors.pen}"
    textColor: "{colors.sheet}"
  button-danger:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.stamp}"
    rounded: "{rounded.control}"
    height: "44px"
  button-danger-hover:
    backgroundColor: "{colors.stamp-wash}"
  button-danger-confirm:
    backgroundColor: "{colors.stamp}"
    textColor: "{colors.sheet}"
  sheet-card:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sheet}"
  sheet-field:
    backgroundColor: "{colors.sheet}"
    padding: "10px 12px"
  field-label:
    textColor: "{colors.muted}"
    typography: "{typography.label}"
  total-value:
    textColor: "{colors.pen}"
    typography: "{typography.total}"
  input:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "9px 10px"
    height: "44px"
  tab:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.ink-2}"
    typography: "{typography.control}"
    padding: "15px 10px 13px"
    height: "48px"
  tab-active:
    textColor: "{colors.pen}"
  photo-flag:
    backgroundColor: "{colors.pen}"
    textColor: "{colors.sheet}"
    rounded: "{rounded.tag}"
    padding: "6px 8px"
  status-pill:
    backgroundColor: "{colors.pen-wash}"
    textColor: "{colors.pen}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "5px 8px"
  rented-stamp:
    backgroundColor: "{colors.stamp}"
    textColor: "{colors.sheet}"
    typography: "{typography.stamp}"
    padding: "9px 0"
  rent-note:
    backgroundColor: "{colors.stamp-wash}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "8px 10px"
  period-cell-active:
    backgroundColor: "{colors.pen-wash}"
    textColor: "{colors.pen}"
  toast:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.sheet}"
    rounded: "{rounded.sheet}"
    padding: "10px 10px 10px 16px"
  toast-error:
    backgroundColor: "{colors.stamp-deep}"
---

# Design System: Busca de apartamentos

## Overview

**Creative North Star: "The Inspection Sheet"**

Every listing is a ficha de vistoria: a white sheet with thin ruled fields, each field in a fixed position with a small uppercase label, the deciding items checked off in boxes. The person arriving from a Telegram alert reads the total in blue pen in the TOTAL / MÊS field, scans the checked items, and decides. The sheet's ruling is the card's grid; fields never move between listings, so two sheets compare at a glance like boarding passes.

The world is cool, flat and administrative. A cool blue-grey ground carries white sheets with 1px rules; text is slate; values written by the system or by the two users (the total, marks, the active tab, pressed actions) are in blue pen ink. Red is reserved for the stamp: the diagonal ALUGADO band, exclusions and errors. Nothing floats; there are no shadows. One family, Public Sans with tabular figures, carries everything from the 11px field labels to the 28px total.

States are stages of the same sheet, not different cards: a favorite gets a pen-blue double edge, a discarded sheet fades, a rented sheet goes grayscale under a red stamp. The system is light mode only, by the user's decision.

**Key Characteristics:**
- Ruled fields in fixed positions, labelled in small uppercase (11px, 0.08em tracking).
- Blue pen ink for values and marks; slate for text; red only for the stamp, exclusions and errors.
- Checked-item board: ✓ confirmed, ✗ refuted, dashed empty box when the listing does not say.
- The monthly total is the largest number on every surface.
- Flat white sheets on a cool ground, 1px rules, 6-8px corners, no shadows.
- Public Sans throughout, tabular figures on by default.
- Light mode only.

## Colors

A cool, low-chroma slate system with one blue pen and one red stamp.

### Primary
- **Ballpoint Blue** (pen): the ink of values and marks. The total, the summary count, links, the active tab underline and count, pressed action buttons, primary buttons, photo flags (Novo, Baixou), checked item boxes, focus rings, caret and range/checkbox accents.
- **Pressed Ballpoint** (pen-deep): hover state of every pen-filled control and link; selection text.
- **Pen Wash** (pen-wash): the faint blue fill behind an active period cell, an expanded opportunity row, the Ativo pill and the active tab count chip.
- **Faded Pen** (pen-soft): the action text inside the dark toast (Desfazer), where full pen would fail on ink.

### Secondary
- **Stamp Red** (stamp): the ALUGADO band (full and mini), danger button text and confirm fill, error dots in the source status, sync error text.
- **Dried Stamp** (stamp-deep): the error toast background and the bold lead of the rented note.
- **Stamp Wash** (stamp-wash): the rented-note panel and the danger button hover.

### Tertiary
- **Ledger Green** (ok): only the 7px status dot of a source that was read successfully. Never text, never fills.

### Neutral
- **Cool Desk** (ground): page background behind sheets, and the inset behind an opened opportunity sheet.
- **Sheet White** (sheet): every sheet, header, tab bar, filter bar, form, button default fill, and text on pen or stamp fills.
- **Slate Ink** (ink): primary text, addresses, fact values, the toast surface.
- **Pencil Slate** (ink-2): secondary text (spec line, composition, conditions, lede), unselected tabs, item-box strokes, input hover border.
- **Field Grey** (muted): field labels, counts, metadata, timestamps, the not-informed state, the rented total.
- **Rule Line** (rule): the 1px rules that outline sheets and divide fields; input and button borders; the dashed empty box.
- **Hairline** (hair): the lighter internal rules inside the item board, opportunity list and details.
- **Photo Mat** (chip): the placeholder fill behind photos and thumbnails.
- **Hover Tint** (hover): hover fill on buttons, period cells and rows; inactive pill and tab-count chip.

### Named Rules
**The Pen And Stamp Rule.** Blue is ink the system or the users wrote: values, marks, the active choice. Red is a stamp: ALUGADO, exclusion, error. Neither is decoration, and no third accent exists (green is a 7px status dot only).

**The Slate Text Rule.** Running text is always ink, ink-2 or muted on sheet or ground; never pen-colored paragraphs.

## Typography

**Display Font:** Public Sans (with system-ui, -apple-system, Segoe UI, sans-serif)
**Body Font:** Public Sans
**Label/Mono Font:** Public Sans, uppercase at 11-12px; no mono face.

**Character:** A plain civic grotesque that reads like a printed government form. Tabular figures are set on the body, so every price, count and area aligns in columns.

### Hierarchy
- **Total** (800, 28px, 1; 26px at 420px and below): the monthly total in the sheet's TOTAL / MÊS field, in pen. The largest number on the page.
- **Total Row** (800, 22px, 1): the same total at row scale in alert opportunity rows.
- **Figure** (700, 20px, 1): period counts in the alert period cells.
- **Headline** (700, clamp(18px, 4.6vw, 22px), 1.2): the page name in the header; alert names and form titles at 18px.
- **Title** (600, 16px, 1.3): the street address field.
- **Body** (400, 15px, 1.5): base text; secondary text steps down to 13-14px in ink-2. Ledes cap at 66ch.
- **Control** (600, 14px, 1): buttons, tabs, details summaries (13px), links row.
- **Section** (700, 12px, 0.08em, uppercase): region group headings and the Alertas heading, with the count in 12px muted beside it.
- **Label** (600, 11px, 0.08em, uppercase): field labels (ENDEREÇO, TOTAL / MÊS, COMPOSIÇÃO), item fact keys (0.06em), period names, pills.
- **Stamp** (800, clamp(22px, 7vw, 28px), 0.24em, uppercase): the ALUGADO band only.

### Named Rules
**The One Value Rule.** A total is one component at three scales (28, 22, 20 for counts), always tabular, always pen, always the largest number in its context. Nothing else on a sheet outranks it.

**The Field Label Rule.** Every field states its name in the 11px uppercase label above its value. Labels name the field they sit in; they never introduce a section or carry a slogan.

## Layout

Content sits in a 1200px max container with a 16px gutter (respecting safe-area insets). Sheets flow in an auto-fill grid with a min of 350px and a 16px gap; from 740px, sibling sheets share subgrid rows so photo, head, composition, item board and actions align across a row. Sheets may be grouped under region section headings (optional, toggled by the user); ungrouped, they form one list.

Inside a sheet the order is fixed: photo strip (min(60cqw, 250px) tall), head row (address field | total field, divided by a vertical rule), composition line, two-column item board (36px min rows, six fixed fields), then the body (notes, actions, details, links) at 10-12px padding with 10px gaps. Actions are a three-column grid with 6px gaps; at 900px and up they shrink to content width.

At 420px and below the five tabs become an equal five-column grid with short labels and counts stacked beneath; filters collapse into a summary row showing the current filter state; action buttons tighten to 4px inline padding. The header is never sticky; the tab bar is sticky at the top. The main list reserves 96px at the bottom for the toast.

Alert blocks are full-width sheets: header area, a three-cell period strip, and an opportunity list (88px thumbnail, total and place, time) that becomes two columns at 900px. Opening a row insets the full sheet (max 520px) on the ground color.

## Elevation & Depth

Flat. No surface has a box-shadow. Depth is expressed by tone (white sheet on cool ground, ground inset for an opened opportunity), by 1px rules, and by state edges (a favorite's 1px pen border plus a 1px inset pen outline). The only things that sit above the page are the sticky tab bar (separated by a rule, not a shadow), photo overlays (translucent white nav circles, ink-80% photo count) and the dark toast, which is distinguished by its ink fill.

### Named Rules
**The Ruled Not Raised Rule.** Separate with a 1px rule or a tone change, never with a shadow.

## Shapes

Corners are modest and consistent: 8px on sheets, alert blocks, forms and the toast; 6px on buttons, inputs, notes and the rented note; 4px on photo flags, thumbnails, the photo count and item boxes; 10px on pills and tab-count chips; full circles only for photo nav buttons and status dots. Rules are 1px solid; a dashed rule means "missing or paused" (empty item box, author note, paused alert). Icons are inline SVG strokes, 2px, round caps and joins, 18px (16px in tight action rows, 13px at 3px stroke inside item boxes). The one rotated shape in the system is the stamp: a full-bleed band at -12 degrees.

## Components

### Buttons
Plain form controls: white, ruled, quietly firm.
- **Shape:** gently rounded (6px), 44px min height, 0 12px padding, 7px icon gap.
- **Default:** sheet fill, rule border, ink text.
- **Hover / Active:** border darkens to ink-2 with the hover tint; active uses the hairline tint. Transitions 0.15s on color properties only.
- **Pressed (toggle):** pen fill, white text; hover deepens to pen-deep. Used for Favorito / Voltar / Alugado states.
- **Primary:** pen fill, white text (Novo alerta, Criar alerta, Enviar link).
- **Danger:** stamp text on white; hover gets stamp-wash and stamp border; the confirm step fills with stamp.
- **Disabled:** 45% opacity; a pressed disabled button keeps its pen fill at 50%.
- **Sync (Buscar agora):** a default button in the header with a pen-colored sync icon that spins (1.1s linear) while busy.

### Chips
- **Photo flags:** pen fill, white 11px bold text, 4px corners, top-left of the photo (Novo, Baixou R$ x); a light variant (95% white, ink text) for Favorito / Descartado / Era descartado attributions.
- **Status pill:** 11px uppercase label in pen on pen-wash, 10px corners (Ativo); inactive variant in muted on hover tint (Pausado).

### Cards / Containers
- **Corner Style:** 8px.
- **Background:** sheet on ground.
- **Shadow Strategy:** none (see Elevation & Depth).
- **Border:** 1px rule; favorite adds a pen border and a 1px pen outline inset 2px.
- **Internal Padding:** fields 10px 12px; body 10px 12px 12px.
- **States:** discarded fades photo, head, items and composition to 62%; leaving collapses height (0.28s, cubic-bezier(.2,.8,.2,1)) and fades (0.18s).

### Inputs / Fields
- **Style:** sheet fill, 1px rule border, 6px corners, 15px medium ink text, 9px 10px padding, 44px min height. Checkboxes and ranges use the pen accent.
- **Focus:** border turns pen, plus the global 2px pen focus ring.
- **Hover:** border ink-2.

### Navigation
- **Tabs:** sticky white bar with a bottom rule; 14px semibold ink-2 tabs, 48px tall, each with a count chip. Active tab: pen text, 2px pen underline, count on pen-wash. At 420px and below: five equal columns, short label over a bold count, 54px tall.
- **Filters:** a white bar under the tabs; on phones it collapses into a summary (Filtros + current state + count) with a plus/minus toggle.

### Inspection Sheet (signature)
The listing card. Photo strip with scroll-snap and nav circles; head row of two labelled fields (ENDEREÇO with address and spec line, TOTAL / MÊS with the pen total, a struck-through previous total above it after a price drop); a COMPOSIÇÃO line where a missing condominium reads "não informado" with a dashed underline; the item board of six fixed fields: three criteria boxes (Aceita pet, Gás encanado, Cozinha separada) and three facts (Andar, Mobília, Elevador) written out or "não informado" in muted.

### Checked-Item Board (signature)
17px boxes with 1.5px strokes and 4px corners. Confirmed: pen box with a check. Refuted: ink-2 box with an x. Not stated: dashed rule box, empty, muted label, with a screen-reader "(não informado)".

### ALUGADO Stamp (signature, kept by the user)
A red band across the photo at -12 degrees, 22-28px 800 white uppercase tracked 0.24em, bleeding past both edges. The sheet beneath goes grayscale (photo 60%, head/items/composition 70%, total muted) and a stamp-wash rented note explains who marked it and when, or that it left the source. The band lands with a 0.45s scale-in (cubic-bezier(.16,1,.3,1)) when freshly marked. A mini band sits across rented thumbnails in alert rows.

### Alert Block
A sheet with name, status pill, a conditions line and Editar / Pausar / Excluir; a three-cell period strip (label over 20px count; active cell pen-wash with a 2px pen underline); then opportunity rows (thumb, pen total at 22px, place, time) that expand in place into a full inspection sheet.

### Toast
Fixed bottom-center, ink fill, white 14px text, 8px corners, pen-soft text action (Desfazer); error variant on stamp-deep. Rises in over 0.22s. Motion is removed under reduced-motion.

## Do's and Don'ts

### Do:
- **Do** put every value in a labelled field at a fixed position, with an 11px uppercase label above it.
- **Do** write the monthly total in pen at 28px 800 with tabular figures, and keep it the largest number on the surface.
- **Do** show what the listing does not say as a dashed empty box or the words "não informado" in muted.
- **Do** separate with 1px rule or hair lines and tone changes; keep sheets at 8px and controls at 6px corners.
- **Do** mark rented listings with the diagonal red ALUGADO band and a grayscale sheet, never by removing them.
- **Do** keep icons as 2px stroke SVG and touch targets at 44px minimum.
- **Do** stay in light mode; the system has no dark theme by decision.

### Don't:
- **Don't** use red for anything but the stamp, exclusions and errors; never as a price-drop or "new" highlight.
- **Don't** add shadows, gradients or lifted cards; the sheet is flat paper.
- **Don't** use rounded portal cards with heart overlays and colored amenity chips; amenities belong in the item board or the description.
- **Don't** introduce a second typeface or a third accent hue.
- **Don't** use the uppercase label style as a kicker above headings; labels name fields only.
- **Don't** set text below 11px.
