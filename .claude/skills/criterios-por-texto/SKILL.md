---
name: criterios-por-texto
description: Transforma um pedido em texto livre ("quero 2 banheiros, até 3.200, Pedra Branca ou São José sem Kobrasol, aceita pet...") em critérios do apto-watch e alertas do Telegram. Use quando o usuário descrever o que procura, mudar requisitos ou pedir um alerta novo em linguagem natural.
---

# Critérios a partir de texto livre

O usuário descreve a busca em português. Separe o pedido em três níveis e aplique cada um no lugar certo.

| Nível | Exemplos | Onde vai |
|---|---|---|
| **Obrigatório** | "2 banheiros obrigatório", "teto R$ 3.500", "fora Areias", "aceita pet" | `config.yaml > criteria` (entrada na lista) e/ou um alerta |
| **Desejável** | "2 quartos desejável", "1º ou último andar" | alerta separado, mais restrito (ex.: `min_quartos: 2`) |
| **Diferencial** | "gás encanado", "cozinha separada", "só armários de cozinha e banheiro" | não filtra: a página já marca com etiquetas; cite no resumo |

## Passos

1. Leia `config.yaml` e os alertas atuais (`GET {SUPABASE_URL}/rest/v1/alerts` com a service key do `.env`, sem mostrar a chave).
2. Monte a proposta e **mostre ao usuário antes de gravar**: o que muda em `criteria`, quais buscas entram
   ou saem em `searches` e quais alertas serão criados ou alterados.
3. Depois do ok:
   - edite `config.yaml` (teto, banheiros, vagas, regiões, bairros incluídos/excluídos);
   - crie ou atualize alertas com `POST/PATCH {SUPABASE_URL}/rest/v1/alerts` (campos: `name`, `max_total`,
     `regioes`, `bairros_incluir`, `bairros_excluir`, `min_quartos`, `min_banheiros`, `min_vagas`,
     `exigir_pet`, `avisar_reducao`, `enabled`).
4. Rode `.venv/bin/python -m watcher --dry-run` para mostrar quantos anúncios das fontes automáticas passariam.

## Regras de interpretação

- "Aceita pet essencial" sem mais detalhes: exclua só quem diz que **não** aceita (o watcher já faz isso). Use
  `exigir_pet: true` apenas se o usuário pedir anúncios que **declaram** aceitar.
- Teto de gastos = aluguel + condomínio. IPTU fica de fora, a menos que o usuário diga o contrário.
- Região "Grande Florianópolis" do usuário = continente (Estreito, Coqueiros, Capoeiras, Abraão, Jardim Atlântico,
  Coloninha, Balneário, Itaguaçu, Bom Abrigo, Canto, Monte Cristo) + Centro e arredores. Norte e sul da ilha ficam fora.
- Grafias variam entre sites ("Forquilhinhas", "Forquilinhas"): inclua as variantes nas listas.
