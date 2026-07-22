# HAL Budget

**Track:** Edge / On-Device — GDG Windsor Build with AI Gemma Hackathon  
**Tagline:** A local-first AI finance assistant that answers natural-language questions about your money and reads itemized receipts — no cloud, no API keys.

## Team

- **HAL** — *Hacking All LLMs* — project lead & AI architect
- **Steve Vogelaar** — co-builder, demo assistant, and edge-device tester

---

## What it does

HAL Budget is a personal-finance prototype that keeps all data on your machine. It lets you:

- **Ask questions in plain English** about spending, balances, budgets, bills, and savings.
- **Scan (simulated) receipts** and save them as itemized transactions.
- **Explore a dashboard** with monthly cash flow, upcoming bills, savings goals, and top merchants.
- **Switch between local Gemma 4 models** and reset demo data from the Settings tab.

Everything runs locally: the app, the SQLite database, and the language model through Ollama.

---

## Why Gemma 4?

Gemma 4 is the core reasoning engine behind the natural-language SQL feature. When you ask a question, the model:

1. Reads the database schema prompt.
2. Generates a safe, read-only SQLite query in JSON mode.
3. Returns a concise natural-language answer.

If Ollama is unavailable, the app falls back to a rule-based engine so it keeps working.

This project is intentionally built for the **Edge / On-Device Track**: it demonstrates how an open model can run on a laptop without sending financial data to the cloud.

---

## Tech stack

- **Frontend/UI:** Streamlit
- **Language:** Python 3
- **Database:** SQLite
- **Local LLM:** Ollama running Gemma 4 (or any local model you have pulled)
- **Optional OCR:** Tesseract + Pillow

---

## Setup

1. **Install Ollama** and pull a Gemma 4 model:
   ```bash
   ollama pull gemma4:e2b
   ```

2. **Clone the repository** and install dependencies:
   ```bash
   git clone <repo-url>
   cd HAL-Budget
   pip install -r requirements.txt
   ```

3. **Seed the demo database** (creates `hal_budget.db`):
   ```bash
   python seed_data.py
   ```

4. **Run the app**:
   ```bash
   streamlit run app.py
   ```

The app will open at `http://localhost:8502`.

> **Windows:** You can also double-click `Start-HALBudget.bat` after installing dependencies.

---

## Project structure

```
HAL-Budget/
├── app.py                  # Streamlit UI
├── budget_engine.py        # Natural-language query engine
├── llm_sql_engine.py       # Ollama SQL generation + safety
├── receipt_scanner.py      # Mock/Tesseract receipt parser
├── seed_data.py            # Demo database seeder
├── hal_budget_schema.sql   # SQLite schema
├── Hal-Budget-Logo.png     # App logo
├── Start-HALBudget.bat     # Windows launcher
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Demo

See the included `demo.mp4` for a walkthrough of:

- Asking spending questions in the Chat tab
- Scanning and saving an itemized receipt
- Viewing the Dashboard
- Checking model status in Settings

---

## License

MIT License — see [LICENSE](LICENSE).

---

*Built for the GDG Windsor — Build with AI — Gemma Hackathon. This is a prototype for experimentation, not production financial software.*
