// Modo demonstração: substitui o Supabase por dados locais para ver a página sem configurar nada.
// Ativo com ?demo na URL ou enquanto web/config.js não foi preenchido.
// Lê ../seed/listings.json e ../seed/marks.json (servindo a raiz do repositório) e guarda
// favoritos, descartes, alugados e alertas só neste navegador (localStorage).
// Datas de "visto pela primeira vez", saídas do ar e uma redução de preço são simuladas.
(function () {
  const KEY = 'apto-demo-v3';
  const read = () => { try { return JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { return {}; } };
  const write = s => { try { localStorage.setItem(KEY, JSON.stringify(s)); } catch (e) {} };
  const DAY = 864e5, H = 36e5;
  let seed = null;

  async function load() {
    if (seed) return seed;
    const [ls, ms] = await Promise.all([
      fetch('../seed/listings.json').then(r => r.ok ? r.json() : []).catch(() => []),
      fetch('../seed/marks.json').then(r => r.ok ? r.json() : []).catch(() => []),
    ]);
    const now = Date.now();
    const markOf = id => (ms.find(m => m.listing_id === id) || {}).status;
    // Idades simuladas espalhadas pelo último mês, para os períodos dos alertas terem conteúdo.
    const ages = [3 * H, 9 * H, 20 * H, 1.5 * DAY, 2.5 * DAY, 4 * DAY, 6 * DAY, 9 * DAY, 12 * DAY, 16 * DAY, 21 * DAY, 27 * DAY];
    ls.forEach((l, i) => {
      l.total = (l.rent || 0) + (l.cond || 0);
      l.first_seen = new Date(now - (i < ages.length * 2 ? ages[i % ages.length] + i * H : 40 * DAY)).toISOString();
      l.active = true; l.inactive_at = null;
    });
    // Dois anúncios que saíram do ar (provavelmente alugados).
    ls.filter(l => markOf(l.id) === 'desc').slice(1, 3).forEach((l, i) => { l.active = false; l.inactive_at = new Date(now - (2 + i) * DAY).toISOString(); });
    // Um descartado com redução de preço, para mostrar a volta para "Não favoritados".
    const dropped = ls.find(l => markOf(l.id) === 'desc' && l.active);
    if (dropped) { dropped.prev_total = dropped.total + 250; dropped.price_drop_at = new Date(now - 2 * H).toISOString(); }
    const st = read();
    if (!st.marks) st.marks = Object.fromEntries(ms.map(m => [m.listing_id, m]));
    // Um alugado marcado na mão (por quem usa a demonstração), para mostrar o estado manual.
    if (!st.rentals) st.rentals = { '2920108051': { listing_id: '2920108051', by_email: 'voce@demo', at: new Date(now - 26 * H).toISOString() } };
    if (!st.alerts) st.alerts = [
      { id: 'demo-1', name: 'Geral até R$ 3.500', enabled: true, max_total: 3500, regioes: [], bairros_incluir: [], bairros_excluir: [],
        min_quartos: null, min_banheiros: 2, min_vagas: 1, exigir_pet: false, avisar_reducao: true, created_at: new Date(now - 35 * DAY).toISOString() },
      { id: 'demo-2', name: 'Pedra Branca até R$ 3.200', enabled: true, max_total: 3200, regioes: ['Pedra Branca (Palhoça)'], bairros_incluir: [], bairros_excluir: [],
        min_quartos: 2, min_banheiros: 2, min_vagas: 1, exigir_pet: false, avisar_reducao: true, created_at: new Date(now - 35 * DAY).toISOString() },
    ];
    write(st);
    seed = { listings: ls };
    return seed;
  }

  function from(table) {
    const q = { table, op: 'select', filters: [], row: null };
    const api = {
      select() { return api; }, order() { return api; }, limit() { return api; },
      eq(col, val) { q.filters.push([col, val]); return api; },
      delete() { q.op = 'delete'; return api; },
      upsert(row) { q.op = 'upsert'; q.row = row; return api; },
      insert(row) { q.op = 'insert'; q.row = row; return api; },
      update(row) { q.op = 'update'; q.row = row; return api; },
      then(res, rej) { return exec(q).then(res, rej); },
    };
    return api;
  }

  async function exec(q) {
    const { listings } = await load();
    const st = read();
    const match = r => q.filters.every(([c, v]) => r[c] === v);
    if (q.table === 'listings') return { data: listings, error: null };
    if (q.table === 'runs') {
      const t = new Date(Date.now() - 40 * 6e4).toISOString();
      return { data: [{ source: 'ibagy', status: 'ok', finished_at: t }, { source: 'quintoandar', status: 'ok', finished_at: t },
        { source: 'vivareal', status: 'ok', finished_at: new Date(Date.now() - 5 * H).toISOString() }], error: null };
    }
    if (q.table === 'marks' || q.table === 'rentals') {
      const tbl = st[q.table];
      if (q.op === 'select') return { data: Object.values(tbl), error: null };
      if (q.op === 'upsert') tbl[q.row.listing_id] = q.row;
      if (q.op === 'delete') Object.keys(tbl).forEach(k => { if (match(tbl[k])) delete tbl[k]; });
      write(st); return { data: null, error: null };
    }
    if (q.table === 'alerts') {
      if (q.op === 'select') return { data: st.alerts, error: null };
      if (q.op === 'insert') st.alerts.push({ ...q.row, id: 'demo-' + Date.now(), created_at: new Date().toISOString() });
      if (q.op === 'update') st.alerts = st.alerts.map(a => match(a) ? { ...a, ...q.row } : a);
      if (q.op === 'delete') st.alerts = st.alerts.filter(a => !match(a));
      write(st); return { data: null, error: null };
    }
    return { data: [], error: null };
  }

  window.demoClient = () => ({
    from,
    auth: {
      getSession: async () => ({ data: { session: { user: { email: 'voce@demo' } } } }),
      signInWithOtp: async () => ({ error: { message: 'indisponível no modo demonstração' } }),
    },
    channel: () => ({ on() { return this; }, subscribe() { return this; } }),
  });
})();
