-- apto-watch: esquema do banco (Supabase / Postgres)
-- Rode este arquivo inteiro no SQL Editor do projeto Supabase.
-- O watcher usa a service_role key (ignora RLS). A página usa a anon key + login,
-- e só quem está na tabela `members` lê ou grava.

create extension if not exists pgcrypto;

-- Quem pode usar a página (e-mails que fazem login por link mágico)
create table if not exists members (
  email text primary key
);

create or replace function is_member() returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from members where lower(email) = lower(auth.jwt() ->> 'email'));
$$;

-- Anúncios encontrados pelo watcher
create table if not exists listings (
  id            text primary key,          -- VivaReal/ZAP: código numérico; OLX: 'olx-<listId>'
  source        text not null,             -- vivareal | zap | olx | imobiliaria:<nome>
  url           text not null,
  title         text,
  addr          text,                      -- endereço como o anúncio mostra
  street        text,
  bairro        text,
  cidade        text,
  regiao        text,                      -- Pedra Branca (Palhoça) | São José | Florianópolis
  rent          integer,
  cond          integer,
  total         integer generated always as (coalesce(rent, 0) + coalesce(cond, 0)) stored,
  iptu          text,                      -- texto do anúncio (o período varia entre anúncios)
  area          integer,
  quartos       integer,
  banheiros     integer,
  vagas         integer,
  amenities     jsonb not null default '[]',
  descricao     text,
  pet           text not null default '?', -- SIM | NAO | ?
  pet_neg       text,                      -- trecho que diz que não aceita pet
  photos        jsonb not null default '[]',  -- URLs das fotos
  lat           double precision,
  lon           double precision,
  refs          jsonb not null default '[]',  -- [[categoria, nome, metros], ...]
  nota          text,
  first_seen    timestamptz not null default now(),
  last_seen     timestamptz not null default now(),
  details_at    timestamptz,               -- quando a página de detalhe foi lida
  prev_total    integer,                   -- total antes da última redução
  price_drop_at timestamptz,               -- quando o total caiu pela última vez
  active        boolean not null default true,
  alt_urls      jsonb not null default '[]',  -- o mesmo imóvel em outros sites: [{source, url}]
  inactive_at   timestamptz                   -- quando saiu do ar na fonte (provavelmente alugado)
);
create index if not exists listings_last_seen on listings (last_seen desc);

create table if not exists price_history (
  listing_id text not null references listings (id) on delete cascade,
  total      integer not null,
  seen_at    timestamptz not null default now()
);
create index if not exists price_history_listing on price_history (listing_id, seen_at);

-- Favoritos e descartes (compartilhados entre os membros)
create table if not exists marks (
  listing_id text primary key references listings (id) on delete cascade,
  status     text not null check (status in ('fav', 'desc')),
  by_email   text,
  at         timestamptz not null default now()
);

-- Marcação manual de "alugado" (independente de favorito/descarte)
create table if not exists rentals (
  listing_id text primary key references listings (id) on delete cascade,
  by_email   text,
  at         timestamptz not null default now()
);

-- Alertas configurados na página
create table if not exists alerts (
  id              uuid primary key default gen_random_uuid(),
  name            text not null,
  enabled         boolean not null default true,
  max_total       integer,
  regioes         text[] not null default '{}',   -- vazio = todas
  bairros_incluir text[] not null default '{}',   -- vazio = todos
  bairros_excluir text[] not null default '{}',
  min_quartos     integer,
  min_banheiros   integer,
  min_vagas       integer,
  exigir_pet      boolean not null default false, -- só anúncios que DECLARAM aceitar pet
  avisar_reducao  boolean not null default true,  -- avisar quando um descartado baixar o preço
  created_by      text,
  created_at      timestamptz not null default now()
);

-- Avisos já enviados (evita repetir)
create table if not exists notifications (
  listing_id text not null references listings (id) on delete cascade,
  alert_id   uuid not null references alerts (id) on delete cascade,
  kind       text not null,          -- novo | reducao:<total>
  sent_at    timestamptz not null default now(),
  primary key (listing_id, alert_id, kind)
);

-- Execuções do watcher (aparece na página como status)
create table if not exists runs (
  id          bigserial primary key,
  started_at  timestamptz not null default now(),
  finished_at timestamptz,
  source      text not null,
  status      text not null,          -- ok | bloqueado | erro
  pages       integer default 0,
  found       integer default 0,
  new_count   integer default 0,
  drops       integer default 0,
  message     text
);

-- Pedidos de "Buscar agora" feitos na página; o PC confere a cada 5 min e roda o watcher
create table if not exists sync_requests (
  id           bigserial primary key,
  requested_by text,
  requested_at timestamptz not null default now(),
  started_at   timestamptz,
  finished_at  timestamptz,
  status       text not null default 'pendente' check (status in ('pendente', 'rodando', 'ok', 'erro')),
  message      text
);
create index if not exists sync_requests_status on sync_requests (status, requested_at);

-- RLS
alter table sync_requests enable row level security;
alter table members       enable row level security;
alter table listings      enable row level security;
alter table price_history enable row level security;
alter table marks         enable row level security;
alter table rentals       enable row level security;
alter table alerts        enable row level security;
alter table notifications enable row level security;
alter table runs          enable row level security;

drop policy if exists members_read on members;
create policy members_read on members for select to authenticated using (is_member());

drop policy if exists listings_read on listings;
create policy listings_read on listings for select to authenticated using (is_member());

drop policy if exists history_read on price_history;
create policy history_read on price_history for select to authenticated using (is_member());

drop policy if exists runs_read on runs;
create policy runs_read on runs for select to authenticated using (is_member());

drop policy if exists notif_read on notifications;
create policy notif_read on notifications for select to authenticated using (is_member());

drop policy if exists marks_all on marks;
create policy marks_all on marks for all to authenticated using (is_member()) with check (is_member());

drop policy if exists rentals_all on rentals;
create policy rentals_all on rentals for all to authenticated using (is_member()) with check (is_member());

drop policy if exists alerts_all on alerts;
create policy alerts_all on alerts for all to authenticated using (is_member()) with check (is_member());

drop policy if exists sync_read on sync_requests;
create policy sync_read on sync_requests for select to authenticated using (is_member());

-- A página só cria pedidos pendentes em nome de quem está logado; quem muda o status é o watcher.
drop policy if exists sync_insert on sync_requests;
create policy sync_insert on sync_requests for insert to authenticated
  with check (is_member() and status = 'pendente' and requested_by = auth.jwt() ->> 'email');

-- Atualização ao vivo dos favoritos na página (Realtime)
do $$ begin
  alter publication supabase_realtime add table marks;
exception when others then null; end $$;
do $$ begin
  alter publication supabase_realtime add table rentals;
exception when others then null; end $$;

do $$ begin
  alter publication supabase_realtime add table sync_requests;
exception when others then null; end $$;

-- Projetos criados antes desta versão
alter table listings add column if not exists inactive_at timestamptz;
