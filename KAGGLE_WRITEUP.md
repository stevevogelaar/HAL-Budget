# HAL Budget — Local AI Finance Assistant

**Track:** Edge / On-Device  
**Team:** HAL (*Hacking All LLMs*) — project lead & AI architect; Steve Vogelaar — co-builder, demo assistant, and edge-device tester  
**Tagline:** A privacy-first personal finance demo powered by Gemma 4 on your own machine.

## The Problem

Most AI finance tools send your transactions, balances, and questions to the cloud. That creates real privacy and reliability concerns: outages, data leaks, subscription costs, and the nagging feeling that your money details are someone else's product. We wanted to see if a useful, conversational finance assistant could run entirely on a laptop, keep everything local, and still feel intelligent.

HAL Budget is that experiment.

## What HAL Budget Does

HAL Budget is a single-file-style Streamlit app that acts as a local personal-finance companion:

- **Natural-language chat.** Ask "How much did I spend on Amazon?", "When is my next rent payment?", or "Can I afford a new car?" and get back a plain-English answer grounded in your own data.
- **Itemized receipt scanning.** A simulated receipt scanner parses a mock receipt into line items, then saves the transaction, receipt, and every item into a local SQLite database.
- **Dashboard.** See monthly cash flow, upcoming bills, savings goals, and top merchants.
- **Settings.** Pick which local Ollama model powers the chat, check the local AI status, and reset demo data with one click.
- **Safety fallback.** If the local model is unavailable, the app falls back to a rule-based engine so the demo never dies on stage.

All data lives in a SQLite file on your machine. There is no cloud API, no API key, and no network dependency after the model is downloaded.

## Architecture

The app is intentionally small so the engineering is easy to audit:

- `app.py` — Streamlit UI with five tabs (Chat, Scan Receipt, Dashboard, All Transactions, Settings).
- `budget_engine.py` — Main query router. Tries the local LLM first, then falls back to rule-based patterns.
- `llm_sql_engine.py` — Ollama integration. Sends a JSON-mode schema prompt to Gemma 4, validates the returned SQL is read-only, executes it, and formats the rows into a friendly answer.
- `receipt_scanner.py` — Mock-first receipt parser with optional Tesseract OCR support.
- `seed_data.py` — Seeds the SQLite database with six months of realistic fake transactions, eight itemized receipts, recurring bills, savings goals, and affordability scenarios.
- `hal_budget_schema.sql` — Database schema including views for live balances, monthly summaries, and budget-vs-actual.
- `.streamlit/config.toml` — Theme config: green primary color, dark base, and the app logo.

The entire project is a few hundred lines of Python and SQL, which makes it easy for judges to see exactly how Gemma 4 is wired in.

## How We Used Gemma 4

Gemma 4 is the core reasoning layer of the chat feature. The prompt sent to the model includes the full SQLite schema, a strict "read-only SELECT only" rule, and several examples of the SQL we expect. The model returns JSON with `sql` and `intent` fields. We then:

1. Check that the SQL starts with `SELECT` or `WITH` and contains no forbidden keywords.
2. Run the query against the local SQLite database.
3. Use a lightweight heuristic formatter to turn the rows back into a natural answer.

Because the model runs through Ollama, we can also swap to smaller models (`qwen2.5-coder:1.5b`, `tinyllama`, etc.) from the Settings tab for faster demos. A local `sql_cache.json` stores generated SQL for the built-in demo questions so the first in-person demo is instant, even if the cold model load takes 30–45 seconds.

## Challenges We Overcame

1. **Cold LLM latency.** The first Gemma 4 query can take tens of seconds. We solved this with a warm SQL cache for the demo questions and a clear UI status indicator so the audience knows when the model is loading.
2. **Safety.** A local model can hallucinate SQL. We added a read-only whitelist, banned destructive keywords, and a rule-based fallback that never runs untrusted SQL.
3. **User statements vs. questions.** Early tests showed the LLM would try to answer "I just bought a car for $21,000" with a number rather than explaining it cannot add transactions. We added an intent guard that catches data-entry statements and responds honestly.
4. **Ollama going down mid-demo.** The Settings tab detects Ollama health and offers a one-click "Open PowerShell & start Ollama" button for non-technical users.
5. **UI consistency.** We moved from a fixed dark theme to a `prefers-color-scheme` media query so the app stays readable in both light and dark browser modes.

## Technical Choices

- **Streamlit** for the UI because it is the fastest way to turn Python into a working web app for a hackathon.
- **SQLite** because it is zero-config, file-based, and perfect for a local-only demo.
- **Ollama + Gemma 4** because it is the easiest path to a local, open-weights model that the judges can also run.
- **Rule-based fallback** because a demo that falls back gracefully is better than a demo that crashes when the model is cold.
- **Itemized receipts** because item-level queries ("How much did I spend on coffee?") are a genuine advantage over tools that only see totals.

## Why This Matters

HAL Budget shows that a useful, conversational AI assistant for a sensitive domain can run on ordinary hardware without surrendering data to a cloud provider. The Edge / On-Device track is exactly the right fit: the model is local, the database is local, and the UI is local. The only thing leaving the machine is the final answer shown to the user.

## What's Next

This is a sprint prototype, not a production finance app. Future improvements would include real Tesseract OCR for paper receipts, voice chat, multi-account sync, and more robust handling of ambiguous questions. For the hackathon, the goal was to prove the core idea: a local, Gemma 4-powered finance assistant that is genuinely useful and easy to demo.

---

**Public code:** https://github.com/stevevogelaar/HAL-Budget  
**Live demo:** [demo video attached]
