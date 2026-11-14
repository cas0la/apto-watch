# apto-watch

Agregador pessoal de anúncios de aluguel na Grande Florianópolis. Junta imobiliárias e portais numa lista só,
com critérios que os portais não oferecem, favoritos e descartes compartilhados, e alertas no Telegram.

## Como funciona

| Fonte | Como entra | Por quê |
|---|---|---|
| Ibagy, QuintoAndar | **Automático**: o watcher roda no seu PC a cada 3 h | Aceitam robô identificado e o `robots.txt` permite |
| VivaReal, ZAP, OLX | **Coleta assistida**: você pede ao Claude Code "faz a coleta assistida" | Recusam robô identificado (HTTP 403) |
| Crédito Real | Coleta assistida (se quiser incluir) | Recusou o robô (HTTP 429) |
| Adriano Imóveis | Fora | O `robots.txt` proíbe robôs |
| Brognoli, Isci | Ainda não | Aceitam o robô, mas a busca é montada por JavaScript; falta escrever o leitor |

O watcher se identifica no `User-Agent`, respeita o `robots.txt`, espera entre requisições e para quando o site
recusa. Ele não tenta contornar bloqueios.

Tudo vai para o mesmo processamento (`watcher/run.py`):

- **Anúncio novo** que passa nos critérios do `config.yaml` entra na lista e dispara os alertas que combinam.
- **Mesmo imóvel em dois sites** (mesma rua e número, total e área parecidos) vira um card só, com os dois links.
- **Redução de preço**: o histórico fica em `price_history`; um anúncio descartado que baixa de preço volta para
  "Em análise" com a etiqueta "baixou R$ X" e pode gerar alerta.
- **Alugado**: depois de 7 dias sem aparecer numa leitura completa da fonte, o anúncio é desativado e aparece como
  "Provavelmente alugado" (tarja ALUGADO, botões desabilitados). Vocês também podem marcar "Alugado" na mão
  (tabela `rentals`, desfazível). Se o anúncio voltar a aparecer na fonte, ele é reativado.

A página (`web/`) mostra as abas **Em análise**, **Não favoritados**, **Favoritos**, **Descartados** e **Alertas**.
Na aba Alertas ficam os alertas criados e, para cada um, os anúncios **novos** que ele encontrou desde que foi
criado, separados em Últimas 24h, Últimos 7 dias e Último mês. Cada aba tem endereço próprio (`#alertas`, `#fav`…),
e `?demo` abre a página com os dados da migração, sem Supabase.

## Instalação

### 1. Supabase (banco e login)

1. Crie um projeto gratuito em supabase.com.
2. No **SQL Editor**, rode `supabase/schema.sql`.
3. Cadastre quem pode usar a página:
   ```sql
   insert into members (email) values ('seu@email.com'), ('email-da-outra-pessoa@exemplo.com');
   ```
4. Em **Authentication > URL Configuration**, coloque o endereço do GitHub Pages em *Site URL* e em *Redirect URLs*.
5. Em **Settings > API**, copie a *Project URL*, a *anon key* (vai em `web/config.js`) e a *service_role key*
   (vai só no `.env`; nunca no repositório nem no chat).

### 2. Telegram

1. No Telegram, fale com **@BotFather**, crie um bot e guarde o token.
2. Crie um canal, adicione o bot como **administrador** com permissão de postar.
3. Descubra o `chat_id` do canal (começa com `-100`): poste algo no canal e abra
   `https://api.telegram.org/bot<TOKEN>/getUpdates` no navegador.

### 3. Watcher no seu PC

```bash
cd ~/Documents/apto-watch
uv venv .venv && uv pip install --python .venv -r requirements.txt
cp .env.example .env        # preencha SUPABASE_URL, SUPABASE_SERVICE_KEY, TELEGRAM_*, PAGE_URL
.venv/bin/python -m pytest -q           # 17 testes
.venv/bin/python scripts/seed.py        # importa os 73 anúncios e as 66 marcas da página antiga
.venv/bin/python -m watcher --test-telegram
.venv/bin/python -m watcher --dry-run   # lê as fontes automáticas sem gravar
```

Agendamento (systemd do usuário):

```bash
mkdir -p ~/.config/systemd/user
cp deploy/apto-watch.service deploy/apto-watch.timer ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now apto-watch.timer
systemctl --user list-timers apto-watch.timer   # próxima execução
journalctl --user -u apto-watch -n 50           # últimas execuções
```

O timer roda às 7h, 10h, 13h, 16h, 19h e 22h (com até 15 min de variação). Só roda com o PC ligado; se o PC estava
desligado no horário, roda ao ligar.

### 4. Página no GitHub Pages

1. Preencha `web/config.js` com a Project URL e a anon key.
2. Crie o repositório no GitHub e envie o código.
3. Em **Settings > Pages**, escolha *GitHub Actions* como fonte. O workflow `.github/workflows/pages.yml`
   publica a pasta `web/` a cada push.

## Coleta assistida e critérios por texto

Duas skills do Claude Code ficam em `.claude/skills/`. Abra o Claude Code nesta pasta e peça:

- **"faz a coleta assistida"**: o Claude varre VivaReal, ZAP e OLX pelo seu Chrome, devagar, e importa com
  `python -m watcher --ingest`. Se aparecer um desafio "Confirme que é humano", ele pede para você clicar.
- **"quero 2 banheiros, até R$ 3.200, Pedra Branca ou São José sem Kobrasol…"**: o Claude separa obrigatório,
  desejável e diferencial, mostra o que vai mudar em `config.yaml` e nos alertas, e grava depois do seu ok.

## Arquivos

```
config.yaml              critérios de entrada e buscas (auto / assistido)
watcher/                 watcher em Python (run.py, sources/, store.py, telegram.py)
supabase/schema.sql      tabelas e regras de acesso
web/                     página (GitHub Pages)
scripts/seed.py          importa a lista da página antiga do claude.ai (dados em seed/, fora do git)
deploy/                  timer do systemd
.claude/skills/          coleta assistida e critérios por texto
tests/                   testes (pytest)
```

## Créditos

Locais de referência: © colaboradores do OpenStreetMap, licença ODbL (`data/pois.json`).
