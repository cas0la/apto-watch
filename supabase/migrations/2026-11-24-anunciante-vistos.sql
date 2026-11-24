-- 24/11/2026: anunciante (imobiliária) de cada anúncio e "visto" por pessoa.
-- Rode uma vez no SQL Editor do Supabase. Pode rodar de novo sem estragar nada.

-- Quem anuncia: a imobiliária (ou "Particular"). Nas imobiliárias lidas direto, é a própria.
alter table listings add column if not exists anunciante text;
update listings set anunciante = 'Ibagy Imóveis' where source = 'ibagy' and anunciante is null;
update listings set anunciante = 'Isci Imóveis' where source = 'isci' and anunciante is null;
update listings set anunciante = 'QuintoAndar' where source = 'quintoandar' and anunciante is null;

-- Anúncios que cada pessoa já abriu (ficha ampliada ou link do anúncio).
create table if not exists views (
  listing_id text not null references listings (id) on delete cascade,
  email      text not null,
  at         timestamptz not null default now(),
  primary key (listing_id, email)
);
alter table views enable row level security;
-- Cada pessoa vê e grava só as próprias visualizações.
drop policy if exists views_own on views;
create policy views_own on views for all to authenticated
  using (is_member() and lower(email) = lower(auth.jwt() ->> 'email'))
  with check (is_member() and lower(email) = lower(auth.jwt() ->> 'email'));
