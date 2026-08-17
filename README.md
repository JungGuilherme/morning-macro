# Morning Macro

Página diária automática de cenário macro (agenda, clipping de notícias, mercados ao vivo e operações), publicada via GitHub Pages e atualizada por GitHub Actions.

## Como funciona

- `index.html` + `assets/` — site estático, sem build.
- `data/*.json` — gerado automaticamente pelo workflow `update-data.yml` (roda 2x por dia útil).
- `scripts/` — scripts Python que buscam:
  - `fetch_news.py` — RSS públicos (InfoMoney, Money Times, CNN Brasil, Investing.com), filtrados por palavras-chave macro.
  - `fetch_calendar.py` — calendário econômico via [Financial Modeling Prep](https://site.financialmodelingprep.com/).
  - `fetch_operacoes.py` — planilha do Google Sheets publicada como CSV.

## Configuração necessária (GitHub Secrets)

Em **Settings → Secrets and variables → Actions**, adicione:

| Secret | Descrição |
|---|---|
| `FMP_API_KEY` | Chave da API gratuita da Financial Modeling Prep |
| `SHEET_CSV_URL` | Link CSV publicado da planilha "Operações" (Arquivo → Compartilhar → Publicar na Web) |

## Rodando localmente

```bash
pip install -r requirements.txt
python scripts/fetch_news.py
python scripts/fetch_calendar.py
python scripts/fetch_operacoes.py
```

Depois abra `index.html` num servidor local (ex: `python -m http.server`) — não abra via `file://` porque o `fetch()` dos JSONs é bloqueado por CORS nesse modo.

## Deploy

O workflow `deploy.yml` publica o repositório inteiro no GitHub Pages a cada push na branch `main` (Settings → Pages → Source: GitHub Actions).
