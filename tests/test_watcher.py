"""Testes com HTML sintético que reproduz a estrutura observada nos sites em 06/11/2026.
Se os sites mudarem o HTML, estes testes continuam passando: o sinal de quebra real é o
status 'erro' ou 0 cards no `python -m watcher --dry-run`.
"""
import json

import pytest

from watcher import criteria, run as runmod
from watcher.sources import ibagy, olx, quintoandar, vivareal

CRIT = {
    "max_total": 3500, "min_banheiros": 2, "min_vagas": 1,
    "regioes": {"Palhoça": {"incluir": ["Pedra Branca"]}, "São José": {"excluir": ["Areias", "Serraria"]},
                "Florianópolis": {"incluir": ["Estreito", "Centro"]}},
}

VR_CARD = """
<li data-cy="rp-property-cd"><a href="https://www.vivareal.com.br/imovel/apartamento-2-quartos-pedra-branca-id-{id}/?source=x">
<img src="https://resizedimgs.vivareal.com/img/vr-listing/{h}/foto.webp?action=fit-in">
<h2 data-cy="card-property-content">Apartamento para alugar com 70 m², 2 quartos</h2>
<div data-cy="rp-cardProperty-price-txt"><span>R$ {rent}</span><span>/mês</span><p>Cond. R$ {cond} • IPTU R$ 880</p></div>
<span data-cy="rp-cardProperty-propertyArea-txt">Tamanho do imóvel 70 m²</span>
<span data-cy="rp-cardProperty-bedroomQuantity-txt">Quantidade de quartos 2</span>
<span data-cy="rp-cardProperty-bathroomQuantity-txt">Quantidade de banheiros {ban}</span>
<span data-cy="rp-cardProperty-parkingSpacesQuantity-txt">Quantidade de vagas de garagem 1</span>
<span data-cy="rp-cardProperty-location-txt">{bairro}, {cidade}</span>
<span data-cy="rp-cardProperty-street-txt">Avenida Pedra Branca</span></a></li>"""


def vr_list(cards, n=None):
    body = "".join(VR_CARD.format(**c) for c in cards)
    return f"<html><body><h1>{n or len(cards)} Apartamentos para alugar</h1><ul>{body}</ul></body></html>"


def card(id="2914776416", rent="3.000", cond="450", ban=2, bairro="Pedra Branca", cidade="Palhoça", h="a" * 32):
    return dict(id=id, rent=rent, cond=cond, ban=ban, bairro=bairro, cidade=cidade, h=h)


def test_vivareal_list():
    items = vivareal.parse_list(vr_list([card()], n=41))
    assert len(items) == 1
    it = items[0]
    assert it["id"] == "2914776416" and it["rent"] == 3000 and it["cond"] == 450
    assert (it["area"], it["quartos"], it["banheiros"], it["vagas"]) == (70, 2, 2, 1)
    assert (it["bairro"], it["cidade"]) == ("Pedra Branca", "Palhoça")
    assert it["url"].endswith("-id-2914776416/")
    assert it["photos"][0].startswith("https://resizedimgs.vivareal.com/img/vr-listing/" + "a" * 32)
    assert vivareal.total_pages(vr_list([card()], n=41)) == 2


def test_vivareal_page_url():
    u = "https://www.vivareal.com.br/aluguel/sc/x/?banheiros=2,3,4&precoMaximo=3500"
    assert "pagina=3" in vivareal.page_url(u, 3) and "banheiros=2,3,4" in vivareal.page_url(u, 3)
    assert "pagina" not in vivareal.page_url(u, 1)


def test_vivareal_detail():
    h1, h2 = "b" * 32, "c" * 32
    html = f"""<html><body>
    <p data-testid="location-address">Rua das Siriemas, 106 - Pedra Branca, Palhoça - SC</p>
    <span data-testid="condoFee">R$ 370/mês</span><span data-testid="iptu">R$ 200</span>
    <ul data-testid="amenities-list"><li>65 m²</li><li>0 suítes</li><li>2º andar</li><li>Aceita animais</li></ul>
    <div data-testid="description-content">Apartamento com gás central e elevador.</div>
    <iframe data-testid="map-iframe" src="https://www.google.com/maps/embed/v1/place?key=K&q=-27.626673%2C-48.67825"></iframe>
    <script>self.__next_f.push([1,"{{\\"images\\":[{{\\"dangerousSrc\\":\\"-listing/{h1}/x.webp\\"}},{{\\"dangerousSrc\\":\\"vr-listing/{h2}/x.webp\\"}}],\\"monthly\\":{{\\"condo_fee\\":370,\\"price\\":2000,\\"yearly_iptu\\":200}}}}"])</script>
    </body></html>"""
    d = vivareal.parse_detail(html)
    assert d["addr"].startswith("Rua das Siriemas") and d["cond"] == 370 and d["rent"] == 2000
    assert d["iptu"] == "R$ 200" and "0 suítes" not in d["amenities"] and "Aceita animais" in d["amenities"]
    assert (d["lat"], d["lon"]) == (-27.626673, -48.67825)
    assert len(d["photos"]) == 1 or len(d["photos"]) == 2  # 'vr-listing/' precisa aparecer no caminho
    assert all("vr-listing" in p for p in d["photos"])


def test_olx_list():
    ads = [{"listId": 123, "subject": "Apto 2 quartos", "priceValue": "R$ 2.800", "url": "https://sc.olx.com.br/x-123?y=1",
            "locationDetails": {"municipality": "São José", "neighbourhood": "Barreiros"},
            "properties": [{"name": "condominio", "value": "R$ 450"}, {"name": "iptu", "value": "R$ 0"},
                           {"name": "size", "value": "70m²"}, {"name": "rooms", "value": "2"},
                           {"name": "bathrooms", "value": "2"}, {"name": "garage_spaces", "value": "1"},
                           {"name": "re_features", "value": "Aceita animais, Piscina"}],
            "images": [{"original": "https://img.olx.com.br/1.jpg"}]}]
    payload = json.dumps('0:["$","x",null,' + json.dumps({"ads": ads}, separators=(",", ":")) + "]")[1:-1]
    html = f'<html><script>self.__next_f.push([1,"{payload}"])</script></html>'
    it = olx.parse_list(html)[0]
    assert it["id"] == "olx-123" and it["rent"] == 2800 and it["cond"] == 450 and it["iptu"] is None
    assert (it["area"], it["quartos"], it["banheiros"], it["vagas"]) == (70, 2, 2, 1)
    assert it["bairro"] == "Barreiros" and it["url"] == "https://sc.olx.com.br/x-123"
    assert "pagina" not in olx.page_url("https://www.olx.com.br/a", 2) and "o=2" in olx.page_url("https://www.olx.com.br/a", 2)


@pytest.mark.parametrize("text,expected", [
    ("Não são aceitos animais de estimação.", "NAO"),
    ("Proibido pets no condomínio", "NAO"),
    ("Piso sem carpete, ótimo estado", "?"),
    ("Aceita animais", "SIM"),
    ("Apartamento amplo", "?"),
])
def test_pet(text, expected):
    assert criteria.pet_status(text)[0] == expected


def test_base_ok():
    ok = {"rent": 3000, "cond": 450, "banheiros": 2, "vagas": 1, "cidade": "Palhoça", "bairro": "Pedra Branca"}
    assert criteria.base_ok(ok, CRIT)[0]
    assert not criteria.base_ok({**ok, "cond": 600}, CRIT)[0]               # 3600 > 3500
    assert not criteria.base_ok({**ok, "bairro": "Aririú"}, CRIT)[0]         # Palhoça fora de Pedra Branca
    assert not criteria.base_ok({**ok, "cidade": "São José", "bairro": "Areias"}, CRIT)[0]
    assert criteria.base_ok({**ok, "cidade": "Sao Jose", "bairro": "Barreiros"}, CRIT)[0]
    assert not criteria.base_ok({**ok, "banheiros": 1}, CRIT)[0]
    assert not criteria.base_ok({**ok, "pet": "NAO"}, CRIT)[0]


def test_alert_match():
    l = {"rent": 2500, "cond": 400, "regiao": "São José", "bairro": "Kobrasol", "quartos": 2, "banheiros": 2, "vagas": 1, "pet": "?"}
    assert criteria.alert_match(l, {"max_total": 3000})
    assert not criteria.alert_match(l, {"max_total": 2800})
    assert not criteria.alert_match(l, {"regioes": ["Florianópolis"]})
    assert criteria.alert_match(l, {"bairros_incluir": ["kobrasol"]})
    assert not criteria.alert_match(l, {"bairros_excluir": ["Kobrasol"]})
    assert not criteria.alert_match(l, {"min_quartos": 3})
    assert not criteria.alert_match(l, {"exigir_pet": True})


# ---------- fluxo completo com fakes ----------
class FakeClient:
    def __init__(self, pages):
        self.pages = pages

    def get(self, url):
        for k, v in self.pages.items():
            if k in url:
                return v
        return "<html><h1>0</h1></html>"


class FakeStore:
    def __init__(self, existing=None, marks=None, alerts=None):
        self.rows = dict(existing or {})
        self._marks = marks or {}
        self._alerts = alerts or []
        self.history, self.updates, self.sent_keys, self.runs = [], [], set(), []

    def listings_by_id(self, ids):
        return {i: self.rows[i] for i in ids if i in self.rows}

    def listings_missing_details(self, limit):
        return []

    def find_duplicate(self, l, key):
        for r in self.rows.values():
            if r.get("source") != l["source"] and key and runmod._street_key(r) == key and r["total"] == runmod._total(l):
                return r
        return None

    def add_alt_url(self, lid, current, item):
        self.rows[lid]["alt_urls"] = current + [item]

    def upsert_listings(self, rows):
        for r in rows:
            self.rows[r["id"]] = {**r, "total": (r.get("rent") or 0) + (r.get("cond") or 0)}

    def update_listing(self, lid, data):
        self.updates.append((lid, data))

    def add_price(self, lid, total):
        self.history.append((lid, total))

    def deactivate_stale(self, sources, before):
        self.deactivated = sources

    def marks(self):
        return self._marks

    def alerts(self):
        return self._alerts

    def sent(self, lid, aid, kind):
        return (lid, aid, kind) in self.sent_keys

    def mark_sent(self, lid, aid, kind):
        self.sent_keys.add((lid, aid, kind))

    def start_run(self, source):
        self.runs.append(source)
        return len(self.runs)

    def finish_run(self, rid, **data):
        pass


class FakeTG:
    enabled = True

    def __init__(self):
        self.msgs = []

    def send(self, text, preview=None):
        self.msgs.append(text)
        return True


def test_run_new_and_drop(monkeypatch):
    html = vr_list([card(id="1111111111", rent="3.000", cond="450"),            # novo
                    card(id="2222222222", rent="2.500", cond="400"),            # já existe, baixou de 3200 para 2900
                    card(id="3333333333", rent="2.000", cond="300", ban=1)])    # fora (1 banheiro)
    client = FakeClient({"vivareal.com.br/aluguel": html})
    monkeypatch.setattr(runmod, "PoliteClient", lambda *a, **k: client)
    monkeypatch.setattr(runmod, "fetch_details", lambda c, l: {"details_at": "x", "descricao": "Aceita animais"})
    store = FakeStore(existing={"2222222222": {"id": "2222222222", "total": 3200, "rent": 2800, "cond": 400}},
                      marks={"2222222222": {"status": "desc", "at": "2026-11-01T00:00:00+00:00"}},
                      alerts=[{"id": "A", "name": "Geral", "max_total": 3500, "avisar_reducao": True}])
    tg = FakeTG()
    cfg = {"user_agent": "t", "delay_seconds": 0, "max_pages_per_search": 1, "detail_limit": 5, "criteria": CRIT,
           "searches": [{"source": "vivareal", "url": "https://www.vivareal.com.br/aluguel/x/"}]}
    s = runmod.run(cfg, store, tg, page_url="https://x")
    assert s["new"] == 1 and s["drops"] == 1 and s["alerts"] == 2
    assert "1111111111" in store.rows and store.rows["1111111111"]["pet"] == "SIM"
    assert "3333333333" not in store.rows
    upd = dict(store.updates)["2222222222"]
    assert upd["prev_total"] == 3200 and "price_drop_at" in upd
    assert any("Novo imóvel" in m for m in tg.msgs) and any("Baixou R$ 300" in m for m in tg.msgs)
    # segunda execução não repete avisos
    s2 = runmod.run(cfg, store, tg)
    assert s2["alerts"] == 0


IBAGY_BOX = """<div class="col-xs-12 imovel-box-single" data-codigo="97691"><div class="swiper-container">
<a class="swiper-wrapper" href="https://ibagy.com.br/imovel/97691/apartamento-2-quartos-x-pedra-branca-palhoça/">
<div class="swiper-slide foto-imovel" style="background-image: url(https://rocketstatic4.com.br/media/ibagy/imo-fotos/97691/a.jpg.webp?v=1);"></div>
<div class="swiper-slide foto-imovel" data-background="https://rocketstatic4.com.br/media/ibagy/imo-fotos/97691/b.jpg.webp?v=2"></div></a></div>
<h2 class="titulo-grid">Apartamento 2 Quartos Pedra Branca 56m²</h2>
<h3>Rua dos Cravos, 220, Cidade Universitária Pedra Branca - Palhoça <font>/Sc</font> <small>BOULEVARD</small></h3>
<span class="item-price-rent">Aluguel R$ 2.200,00</span><span class="item-price-condominio">Taxa condominial Aprox. R$ 451,00</span>
<span class="item-price-iptu">IPTU Aprox. R$ 126,00</span>
<div><span>2</span><small>Quartos</small><span>1</span><small>Suíte</small><span>1</span><small>Vaga</small></div></div>"""


def test_ibagy():
    html = f"<html><body><p>60 imóveis encontrados</p>{IBAGY_BOX}</body></html>"
    it = ibagy.parse_list(html, "ibagy", {"banheiros": 2})[0]
    assert it["id"] == "ibagy-97691" and it["rent"] == 2200 and it["cond"] == 451 and it["iptu"] == "R$ 126"
    assert (it["quartos"], it["vagas"], it["banheiros"], it["area"]) == (2, 1, 2, 56)
    assert it["bairro"] == "Cidade Universitária Pedra Branca" and it["cidade"] == "Palhoça"
    assert len(it["photos"]) == 2 and ibagy.total_pages(html) == 5
    assert criteria.base_ok(it, CRIT)[0]  # 'Cidade Universitária Pedra Branca' conta como Pedra Branca


def test_quintoandar():
    data = {"props": {"pageProps": {"initialState": {"houses": {"numberOfListingsViewed": 3, "895": {
        "id": "895", "forRent": True, "rentPrice": 2490, "condoIptu": 600, "bathrooms": 2, "parkingSpots": 1, "bedrooms": 2,
        "area": 70, "neighbourhood": "Barreiros", "address": {"address": "Rua X", "city": "São José"},
        "isFurnished": True, "amenities": ["AREA_DE_SERVICO"], "installations": ["PISCINA"],
        "photos": [{"url": "https://quintoandar.com.br/img/v2/med/photo/a.jpg"}]}}}}}}
    html = f'<html><script id="__NEXT_DATA__" type="application/json">{json.dumps(data)}</script></html>'
    it = quintoandar.parse_list(html)[0]
    assert it["id"] == "qa-895" and it["rent"] == 2490 and it["cond"] == 600 and "Mobiliado" in it["amenities"]
    assert it["url"] == "https://www.quintoandar.com.br/imovel/895" and criteria.base_ok(it, CRIT)[0]


def test_assisted_sources_are_skipped(monkeypatch):
    calls = []
    class C:
        def get(self, url):
            calls.append(url)
            return "<html></html>"
    cfg = {"searches": [{"source": "vivareal", "modo": "assistido", "url": "https://www.vivareal.com.br/x"}]}
    seen, report = runmod.collect(cfg, C())
    assert calls == [] and report == []


def test_ingest_and_dedupe(tmp_path):
    rows = [{"id": "2914186158", "source": "vivareal", "url": "https://vr/1", "street": "Rua Recanto dos Santos, 110",
             "bairro": "Pedra Branca", "cidade": "Palhoça", "rent": 2380, "cond": 394, "banheiros": 2, "vagas": 1, "area": 65,
             "descricao": "Cozinha planejada"}]
    f = tmp_path / "coleta.json"
    f.write_text(json.dumps(rows))
    seen, report = runmod.ingest_file(str(f))
    store = FakeStore(existing={}, alerts=[])
    store.rows["ibagy-1"] = {"id": "ibagy-1", "source": "ibagy", "street": "R. Recanto dos Santos, 110", "total": 2774, "area": 65}
    cfg = {"criteria": CRIT, "detail_limit": 0}
    s = runmod.process(cfg, store, None, seen, report)
    assert s["dupes"] == 1 and s["new"] == 0
    assert store.rows["ibagy-1"]["alt_urls"] == [{"source": "vivareal", "url": "https://vr/1"}]


def test_robots_blocks():
    from watcher.http import Blocked, PoliteClient
    c = PoliteClient("apto-watch/test", 0)
    rp = __import__("urllib.robotparser").robotparser.RobotFileParser()
    rp.parse(["User-agent: *", "Disallow: /"])
    c._robots["https://exemplo.com"] = rp
    with pytest.raises(Blocked):
        c.get("https://exemplo.com/aluguel")
