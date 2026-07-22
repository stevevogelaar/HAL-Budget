# HAL Budget

**Privacy-First Personal Finance Assistant**

🔒 All data stays on your machine. No cloud. No API keys. No data ever leaves your laptop.

---

## What It Does

HAL Budget is a fully offline AI-powered personal finance tracker. Ask it questions in plain English about your money, scan receipts, check budgets, or see if you can afford something new.

**Demo-ready questions:**
- "How much did I spend on Amazon?"
- "When is my next rent payment?"
- "Can I afford a new car?"
- "What are my subscriptions?"
- "How much do I spend on groceries?"
- "What's my checking balance?"
- "Show me my budget vs actual"
- "How much have I saved?"
- "Do I only buy gas at Shell?"
- "Which category do I spend the most on?"
- "How much did I spend on coffee?"
- "Show me all milk purchases"

---

## Current Features (Working Now)

| Feature | Status |
|---------|--------|
| 💬 Natural language queries | ✅ Local LLM (Gemma 4 via Ollama) generates safe read-only SQL |
| 📊 Monthly cash flow tracking | ✅ SQLite-backed, 7 months history |
| 📅 Recurring bill reminders | ✅ 8 active subscriptions/bills |
| 💰 Account balances | ✅ Live calculated from transactions |
| 📷 Receipt scanner | ✅ Mock receipts with structured line items saved to DB |
| 🧾 Item-level spending | ✅ Query individual products/brands (coffee, milk, Advil) |
| 📈 Spending by merchant | ✅ Any merchant via LLM SQL |
| 🎯 Savings goals | ✅ 3 active goals with progress |
| ⚖️ Budget vs actual | ✅ Monthly category comparison |
| 🧮 Affordability checker | ✅ "Can I afford X?" calculations |
| 🔒 SQL safety | ✅ Whitelist of read-only SELECT statements only |

---

## Tech Stack (All Local)

| Layer | Tool | Why |
|-------|------|-----|
| UI | Streamlit | Runs in browser, no install |
| Database | SQLite | Zero-config, portable |
| Query Engine | Python + Ollama + Gemma 4 | LLM generates safe read-only SQL; regex heuristics for formatting |
| Receipt Parser | Mock data + Tesseract-ready | Saves transactions + itemized receipt lines |
| OCR (future) | Tesseract / EasyOCR | Real image-to-receipt extraction |
| Speech (future) | Whisper via Ollama or browser API | Voice questions |

---

## Future Roadmap

### Phase 2 — Smart Assistant
- **Document parser** — Scan/photo/upload a receipt → auto-extract merchant, amount, items → save to DB
- **Voice mode** — "Hey HAL, how much do I spend on coffee?"
- **Saved conversations / named queries** — Bookmark questions you ask repeatedly

### Phase 3 — Predictive
- **Cash flow forecasting** — "Based on your patterns, you'll run tight in November"
- **Smart savings suggestions** — "You spent $200 less on groceries this month. Auto-save the difference?"
- **Bill negotiation tracker** — "Your internet bill went up 15% in 2 years. Time to shop around?"

### Phase 4 — Multi-User
- **Family sync** — Household budget, shared goals
- **Small business** — Invoice tracking, expense categorization, tax prep
- **Export** — PDF reports, CSV for accountants

---

## Model & Cache Notes

- First-time questions may take 10–20 seconds while Gemma 4 generates SQL.
- Demo questions are pre-warmed in `sql_cache.json` for instant answers.
- Cache warms automatically when the app starts.
- If Ollama is unavailable, HAL falls back to a fast rule-based engine.

---

## Why This Matters

Most finance apps require:
- Bank account logins (security risk)
- Cloud storage (privacy risk)
- Monthly subscriptions (cost)

**HAL Budget requires:**
- A laptop
- Python
- That's it.

Your financial data is yours. HAL Budget keeps it that way.

---

## How to Run

```bash
pip install streamlit pandas
python seed_data.py    # Creates database with demo data
streamlit run app.py   # Opens in browser
```

No API keys. No accounts. No internet required after setup.

---

## Hackathon Context

**Event:** GDG Windsor Build with AI — Gemma Hackathon 2026
**Track:** Edge / On-Device
**Team:** Steve Vogelaar + HAL (AI collaborator)
**Entry #2** (also submitted: HAL Guardian — privacy-first security scanner)

---

*Built in 1 day by a human and an AI who never sleep.* 🚀
