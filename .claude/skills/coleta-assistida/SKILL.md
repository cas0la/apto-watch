---
name: coleta-assistida
description: Varre os portais que recusam robôs (VivaReal, ZAP, OLX) pelo Chrome do usuário e importa os anúncios no apto-watch. Use quando o usuário pedir "coleta assistida", "varre os portais", "atualiza VivaReal/OLX" ou similar.
---

# Coleta assistida dos portais

Os portais VivaReal, ZAP e OLX recusam o watcher identificado como robô (HTTP 403). A coleta deles é feita
aqui, pelo Chrome do usuário, quando ele pedir, e importada com `python -m watcher --ingest`.

## Regras

- Navegue como uma pessoa navegaria: uma página por vez, 3 a 5 segundos entre páginas, poucas páginas por execução.
- Se aparecer "Confirme que é humano" ou outro desafio, **pare e peça ao usuário** para clicar. Nunca tente resolver.
- Se o site devolver 429 ou bloquear, pare essa fonte e siga com as outras; diga ao usuário o que ficou de fora.
- Não altere favoritos e descartes: eles ficam no Supabase e o `--ingest` não mexe neles.

## Passos

1. Leia `config.yaml`: as buscas com `modo: assistido` e os `criteria`.
2. Carregue as ferramentas do Chrome numa única chamada do ToolSearch e abra uma aba nova.
3. **VivaReal/ZAP**: para cada URL, abra a página 1 e as seguintes com `&pagina=N` até o total do `<h1>`
   (30 por página). Em cada página, rode o coletor abaixo e acumule em `localStorage` (a navegação
   reinicia o JavaScript da página).
4. **Detalhes**: para cada anúncio que passa nos critérios do `config.yaml`, busque a página de detalhe
   (mesmo domínio, `fetch`) com 3,5 s de intervalo, rodando em segundo plano e conferindo o progresso,
   porque cada chamada do `javascript_tool` tem limite de 45 s.
5. **OLX**: abra cada URL (e `?o=2`, `?o=3`…), leia o bloco `{"ads":[...]}` com o coletor OLX abaixo.
6. Exporte o resultado: escreva o JSON no `<body>` da aba e leia com `get_page_text`. Se passar de 50 mil
   caracteres, exporte em partes.
7. Grave em `coleta/AAAA-MM-DD.json` e rode:
   `.venv/bin/python -m watcher --ingest coleta/AAAA-MM-DD.json`
8. Mostre ao usuário o resumo: novos, reduções de preço, duplicados juntados, alertas enviados e o que ficou de fora.

## Formato do JSON (uma lista)

```json
[{"id": "2914186158", "source": "vivareal", "url": "https://www.vivareal.com.br/imovel/...-id-2914186158/",
  "addr": "Rua Recanto dos Santos, 110 - Pedra Branca, Palhoça - SC", "street": "Rua Recanto dos Santos, 110",
  "bairro": "Pedra Branca", "cidade": "Palhoça", "rent": 2380, "cond": 394, "iptu": "R$ 144",
  "area": 65, "quartos": 2, "banheiros": 2, "vagas": 1, "amenities": ["5º andar", "Cozinha"],
  "descricao": "...", "photos": ["https://resizedimgs.vivareal.com/img/vr-listing/<hash>/f.webp?action=fit-in&dimension=800x600"],
  "lat": -27.63, "lon": -48.69}]
```

`id` do OLX: `olx-<listId>`. Campos ausentes podem ser omitidos.

## Coletor VivaReal/ZAP (cards da lista)

```js
const num = s => s ? parseInt(s.replace(/\D/g, '')) || 0 : 0;
const M = JSON.parse(localStorage.getItem('__coleta') || '{}');
document.querySelectorAll('[data-cy="rp-property-cd"]').forEach(c => {
  const t = k => c.querySelector(`[data-cy="${k}"]`)?.textContent.replace(/\s+/g, ' ').trim() || '';
  const a = c.querySelector('a[href*="-id-"]'); const id = a?.href.match(/-id-(\d+)/)?.[1]; if (!id) return;
  const price = t('rp-cardProperty-price-txt');
  const [bairro, cidade] = t('rp-cardProperty-location-txt').split(/,\s*(?=[^,]+$)/);
  M[id] = { id, source: location.host.includes('zap') ? 'zap' : 'vivareal', url: a.href.split('?')[0],
    rent: num((price.match(/R\$\s*([\d.]+)\s*\/\s*m[êe]s/) || [])[1]), cond: num((price.match(/Cond\.\s*R\$\s*([\d.]+)/) || [])[1]),
    area: num(t('rp-cardProperty-propertyArea-txt')), quartos: num(t('rp-cardProperty-bedroomQuantity-txt')),
    banheiros: num(t('rp-cardProperty-bathroomQuantity-txt')), vagas: num(t('rp-cardProperty-parkingSpacesQuantity-txt')),
    bairro, cidade, street: t('rp-cardProperty-street-txt') };
});
localStorage.setItem('__coleta', JSON.stringify(M)); Object.keys(M).length
```

## Detalhe VivaReal (rodar com `fetch` no mesmo domínio)

```js
async id => { const h = await (await fetch('/imovel/apartamento-2-quartos-sao-jose-com-garagem-id-' + id + '/')).text();
  const d = new DOMParser().parseFromString(h, 'text/html'); const q = s => d.querySelector(`[data-testid="${s}"]`)?.textContent.replace(/\s+/g, ' ').trim() || '';
  const i = h.search(/\\?"images\\?":\[/); const seg = h.slice(i, h.indexOf(']', i));
  const ph = [...new Set([...seg.matchAll(/vr-listing\/([a-f0-9]{32})\//g)].map(m => m[1]))];
  const g = h.match(/maps\/embed\/v1\/place[^"]*?q=(-?[\d.]+)%2C(-?[\d.]+)/);
  return { addr: q('location-address'), cond: parseInt(q('condoFee').replace(/\D/g, '')) || 0, iptu: q('iptu'),
    amenities: [...(d.querySelector('[data-testid="amenities-list"]')?.children || [])].map(e => e.textContent.trim()).filter(Boolean),
    descricao: d.querySelector('[data-testid="description-content"]')?.textContent.trim(),
    photos: ph.map(x => `https://resizedimgs.vivareal.com/img/vr-listing/${x}/f.webp?action=fit-in&dimension=800x600`),
    lat: g ? +g[1] : null, lon: g ? +g[2] : null }; }
```

## Coletor OLX

```js
const t = [...document.scripts].map(s => s.textContent).join('\n');
const f = (t.match(/self\.__next_f\.push\(\[1,"(.*?)"\]\)/gs) || []).map(x => { try { return JSON.parse(x.slice(19, -1))[1] } catch (e) { return '' } }).join('');
const i = f.indexOf('{"ads":['); let dep = 0, j = i + 7; for (; j < f.length; j++) { if (f[j] == '[') dep++; else if (f[j] == ']' && !--dep) break; }
JSON.parse(f.slice(i + 7, j + 1)).map(a => { const p = Object.fromEntries((a.properties || []).map(x => [x.name, x.value])); const n = s => parseInt(String(s || '').replace(/\D/g, '')) || 0;
  return { id: 'olx-' + a.listId, source: 'olx', url: String(a.url).split('?')[0], title: a.subject, rent: n(a.priceValue), cond: n(p.condominio),
    area: n(p.size), quartos: n(p.rooms), banheiros: n(p.bathrooms), vagas: n(p.garage_spaces), bairro: a.locationDetails?.neighbourhood,
    cidade: a.locationDetails?.municipality, amenities: String(p.re_features || '').split(',').map(s => s.trim()).filter(Boolean),
    photos: (a.images || []).map(x => x.original).filter(Boolean).slice(0, 30) }; })
```
