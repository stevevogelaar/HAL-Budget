# HAL Budget — YouTube Demo Video Script & Shotlist

**Goal:** A 3–4 minute screen demo that shows HAL Budget as a real, local, Gemma 4-powered finance assistant. Friendly, fast, and focused on the Edge/On-Device track.

**Who is driving the screen:** The AI assistant is controlling the browser via Playwright. Steve is recording the screen and adding narration/captions afterward.

**Stopping and restarting:** If the recording needs to pause, Steve can stop at any shot. The assistant can resume exactly from that shot — long pauses can be edited out later.

---

## Vision / Introduction

Cloud AI finance apps send your transactions, balances, and questions to someone else's server. HAL Budget does the opposite: it runs Gemma 4 locally, stores everything in a SQLite file on your laptop, and answers plain-English questions about your money. **HAL's project** is a local-first AI finance assistant built to prove that useful, private AI can live right on your machine — no cloud, no API keys, no data leaving the box.

The video moves through every page of the app and shows what it does today, plus the `.bot` upgrade each page will get in the future.

---

## Recording Setup

1. Start Ollama and make sure `gemma4:e2b` is pulled.
2. Start HAL Budget: `streamlit run app.py` (or `Start-HALBudget.bat`).
3. Warm the cache by clicking the four demo questions in the app once. This creates `sql_cache.json` so answers are instant.
4. Start screen recording.
5. The assistant runs the Playwright driver; Steve adds narration/captions in post.

---

## Shot-by-Shot Script

### Shot 1 — Opening / Home Page (0:00–0:25)

**Screen:** HAL Budget homepage, dark mode. Logo and green header visible.

**Narration / Caption:**
> "Most AI finance apps send your transactions to the cloud. HAL Budget doesn't. It runs Gemma 4 locally, keeps your data in SQLite, and answers plain-English questions about your money. HAL's project is a local-first AI finance assistant — no cloud, no API keys."

**Action:** Hold on the homepage for 6–8 seconds.

**Future .bot upgrade:** Home.bot will greet you with a daily money briefing and proactive alerts.

---

### Shot 2 — Chat Page: Spending Question (0:25–0:55)

**Screen:** Chat tab. Click the demo button: *"How much did I spend on Amazon?"*

**Narration / Caption:**
> "The Chat page is where you ask questions. 'How much did I spend on Amazon?' The agent translates that into a safe, read-only SQL query through Gemma 4 and gives you the answer."

**Action:** Click the button. Wait for the answer box. Hold for 3 seconds.

**Future .bot upgrade:** Chat.bot will handle follow-up questions, remember context across sessions, and suggest next questions.

---

### Shot 3 — Chat Page: Itemized Receipt Query (0:55–1:20)

**Screen:** Chat tab. Click the demo button: *"How much did I spend on coffee?"*

**Narration / Caption:**
> "It can go deeper than totals. 'How much did I spend on coffee?' searches itemized receipts, not just merchants, so you see exactly what you bought."

**Action:** Click the button. Wait for answer. Hold for 3 seconds.

**Future .bot upgrade:** Chat.bot will combine multiple receipts, track spending trends, and warn you before you blow a budget.

---

### Shot 4 — Chat Page: Guardrail (1:20–1:45)

**Screen:** Chat tab. Type: *"I just bought a car for $21,000"*

**Narration / Caption:**
> "The agent is read-only. If you try to add a purchase, it tells you honestly that it can't change your balance yet. No made-up numbers."

**Action:** Type the message, press Enter. Wait for the "Unable to record" answer. Hold for 3 seconds.

**Future .bot upgrade:** Chat.bot will let you add transactions conversationally and double-check them before saving.

---

### Shot 5 — Scan Receipt Page (1:45–2:20)

**Screen:** Scan Receipt tab. Select the Walmart mock receipt, click **Scan Receipt**, then **Save to Transactions**.

**Narration / Caption:**
> "The Scan Receipt page breaks a receipt into line items. Scan a Walmart receipt, save it, and the agent stores the transaction, the receipt, and every item separately."

**Action:**
1. Click the Scan Receipt tab.
2. Click **Scan Receipt**.
3. Wait for the receipt to render.
4. Click **Save to Transactions**.
5. Wait for the success message.

**Future .bot upgrade:** Scan Receipt.bot will use real OCR on phone photos and auto-categorize every line item.

---

### Shot 6 — Dashboard Page (2:20–2:50)

**Screen:** Dashboard tab.

**Narration / Caption:**
> "The Dashboard page shows your cash flow, upcoming bills, savings goals, and where you spend the most — all live from your local database."

**Action:** Click the Dashboard tab. Scroll slowly through the charts. Hold for 5 seconds.

**Future .bot upgrade:** Dashboard.bot will generate plain-English summaries and flag unusual spending automatically.

---

### Shot 7 — All Transactions Page (2:50–3:05)

**Screen:** All Transactions tab.

**Narration / Caption:**
> "The All Transactions page is your searchable, filterable history. You can drill into dates, categories, merchants, or payment methods."

**Action:** Click the All Transactions tab. Scroll the table. Hold for 3 seconds.

**Future .bot upgrade:** All Transactions.bot will let you search with natural language like 'show me every coffee purchase in July'.

---

### Shot 8 — Settings Page: Local AI Proof (3:05–3:35)

**Screen:** Settings tab.

**Narration / Caption:**
> "The Settings page shows the local AI status. You can switch between Ollama models, and if the model is down, there's a button to restart it. No cloud required."

**Action:** Click the Settings tab. Pause on the Ollama status. Optionally click the model dropdown to show available models. Hold for 5 seconds.

**Future .bot upgrade:** Settings.bot will auto-tune model selection based on speed vs. accuracy and warn you before a model download finishes.

---

### Shot 9 — Outro (3:35–3:55)

**Screen:** Back to the homepage, or show the GitHub repo in a browser tab.

**Narration / Caption:**
> "HAL Budget — your money, your machine, your answers. Built by the HAL team and Steve for the Edge/On-Device track. Code and demo at github.com/stevevogelaar/HAL-Budget."

**Action:** Hold for 6–8 seconds. End recording.

---

## Pacing Notes

- Total runtime target: **3:30–4:00**.
- Every click should be followed by a 2–3 second hold so the viewer can read the result.
- Use the cached demo questions for speed.
- If the LLM status indicator shows "LLM engine online" in the Chat tab, keep it visible — it reinforces the local model angle.
- Long pauses or mistakes can be edited out; each shot is independent.

---

## Restart Points

If the recording is stopped mid-take, resume from any of these clean restart points:

1. Homepage
2. Chat tab (before clicking a demo question)
3. Scan Receipt tab (before clicking Scan Receipt)
4. Dashboard tab
5. All Transactions tab
6. Settings tab

Just tell the assistant which shot to resume from.

---

## Roles

- **The AI assistant:** Controls the browser, executes clicks, types messages, controls timing.
- **Steve:** Records the screen, reads or pastes captions, edits the final video, uploads to YouTube.

*This video demo is performed by the AI assistant, with Steve as producer.*
