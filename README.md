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
No topo, **Buscar agora** pede uma leitura das fontes ao PC (veja o passo 3). Nos filtros, *Agrupar por região* liga
ou desliga a divisão por Pedra Branca, São José e Florianópolis; a ordem escolhida vale dentro de cada grupo.

## Instalação

### 1. Supabase (banco e login)

O projeto já criado no supabase.com é o banco e o login da página. São seis passos, todos no navegador, no painel
do projeto (supabase.com/dashboard > seu projeto).

**1.1 Criar as tabelas**

1. No menu da esquerda, abra **SQL Editor** (ícone `>_`).
2. Clique em **New query**.
3. Abra o arquivo `supabase/schema.sql` deste repositório num editor de texto, copie tudo e cole na consulta.
4. Clique em **Run** (ou Ctrl+Enter). O resultado esperado é `Success. No rows returned`.
5. Confira em **Table Editor**: devem aparecer `alerts`, `listings`, `marks`, `members`, `notifications`,
   `price_history`, `rentals`, `runs` e `sync_requests`.

Rodar o arquivo de novo é seguro: ele só cria o que falta.

**1.2 Cadastrar quem pode entrar**

Ainda no SQL Editor, numa consulta nova, troque os e-mails e rode:

```sql
insert into members (email) values ('seu@email.com'), ('email-da-outra-pessoa@exemplo.com');
```

Só esses e-mails veem os anúncios. Quem não estiver na lista consegue receber o link, mas a página fica vazia.

**1.3 Apontar o login para a página**

1. Menu **Authentication** > **URL Configuration**.
2. Em **Site URL**, coloque `https://cas0la.github.io/apto-watch/` e clique em **Save**.
3. Em **Redirect URLs**, clique em **Add URL** e adicione `https://cas0la.github.io/apto-watch/**`.
   Para testar no PC, adicione também `http://127.0.0.1:8766/**`.

Sem isso, o link do e-mail abre `localhost:3000` e o login não completa.

**1.4 Conferir o login por e-mail**

Em **Authentication** > **Sign In / Providers** (ou **Providers**), confira que **Email** está ligado. O plano
gratuito envia poucos e-mails por hora; se o link não chegar, espere alguns minutos e olhe o spam.

**1.5 Ligar o ao vivo (Realtime)**

O `schema.sql` já liga o Realtime para `marks`, `rentals` e `sync_requests`. Para conferir: **Database** >
**Publications** > `supabase_realtime` deve listar essas três tabelas. Se não listar, ligue cada uma ali.

**1.6 Copiar as chaves**

Menu **Project Settings** (engrenagem) > **API Keys** (em projetos antigos, **API**). Você vai ver:

| Onde aparece | O que é | Para onde vai |
|---|---|---|
| **Project URL** (em *Data API*) | `https://xxxx.supabase.co` | `web/config.js` e `.env` (`SUPABASE_URL`) |
| **anon / public** (ou *publishable key*) | chave pública | `web/config.js` (`supabaseAnonKey`) |
| **service_role** (ou *secret key*, clique em *Reveal*) | chave que ignora as regras de acesso | **só** no `.env` (`SUPABASE_SERVICE_KEY`) |

A chave pública pode ir para o GitHub: os dados continuam protegidos pelo login e pela tabela `members`.
A `service_role` dá acesso total ao banco: nunca a coloque no `web/config.js`, num commit ou no chat.

Depois, edite `web/config.js`:

```js
window.APTO = {
  supabaseUrl: "https://xxxx.supabase.co",
  supabaseAnonKey: "cole-a-chave-publica-aqui",
};
```

e crie o `.env` a partir do `.env.example` (passo 3).

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
.venv/bin/python -m pytest -q           # 18 testes
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

**Botão "Buscar agora"** da página: ele grava um pedido na tabela `sync_requests`. Um segundo timer confere a cada
5 minutos se há pedido e, se houver, roda o watcher (`python -m watcher --if-requested`). Se as fontes foram lidas
há menos de 20 minutos, ele só responde que a lista já está atualizada. Os dois timers usam a mesma trava
(`flock`), então nunca rodam ao mesmo tempo.

```bash
cp deploy/apto-watch-sync.service deploy/apto-watch-sync.timer ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now apto-watch-sync.timer
```

### 4. Página no GitHub Pages

O GitHub Pages já está ativado em `https://cas0la.github.io/apto-watch/`. O workflow
`.github/workflows/pages.yml` publica a pasta `web/` a cada push que muda algo em `web/`. Depois de preencher o
`web/config.js`, faça commit e push para a página sair do modo demonstração.

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
