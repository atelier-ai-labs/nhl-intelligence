# NHL Intelligence

A standalone, grounded conversational layer for the NHL Dashboard. It reads structured data from the dashboard public API, so it never receives dashboard database credentials.

## Phase 1

- Player, team, and standings questions
- Evidence labels showing which dashboard data was used
- No game recap claims until Phase 2 adds game-level data

## Run locally

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8001
```

Set `OPENAI_API_KEY` in `.env`. It is used only by this service and must never be sent to the browser.
