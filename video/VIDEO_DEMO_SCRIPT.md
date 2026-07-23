# HAL Budget — YouTube Demo Video Script & Shotlist

**Goal:** A 3–4 minute first-person screen demo for YouTube. The AI assistant speaks directly to the viewer, walks through every page, and thanks the judges at the end.

**Who is driving the screen:** The AI assistant controls the browser via Playwright. Steve records/produces the final upload.

**Audio:** This is a silent video with burned-in captions. Steve can add typing sounds and background music in post if desired.

**Stopping and restarting:** If the recording needs to pause, Steve can stop at any shot. The assistant can resume from that shot — long pauses can be edited out later.

---

## Vision / Introduction

The assistant introduces itself as the AI behind HAL Budget, a local-first finance app that runs Gemma 4 on the user's own machine. The video walks through every page, explains what each page does today, and teases the `.bot` upgrade coming to each page in the future. The assistant thanks the judges at the end.

---

## Recording Setup

1. Start Ollama and make sure `gemma4:e2b` is pulled.
2. Start HAL Budget: `streamlit run app.py` (or `Start-HALBudget.bat`).
3. Warm the cache by clicking the four demo questions in the app once.
4. Start screen recording.
5. The assistant runs the Playwright driver and executes the shotlist.

---

## Shot-by-Shot Script

### Shot 1 — Opening / Home Page (0:00–0:25)

**Screen:** HAL Budget homepage, dark mode. Logo and green header visible.

**Caption (first person):**
> "Hi. I'm the AI assistant behind HAL Budget. Most finance apps send your money data to the cloud — I don't. I run Gemma 4 right on your machine, keep everything in a local SQLite file, and answer plain-English questions about your finances. I'm HAL's project: a local-first AI finance assistant with no cloud and no API keys."

**Action:** Hold on the homepage for the full shot.

**Future .bot upgrade:** Home.bot will greet you with a daily money briefing and proactive alerts.

---

### Shot 2 — Chat Page: Spending Question (0:25–0:55)

**Screen:** Chat tab. Click demo button: *"How much did I spend on Amazon?"*

**Caption (first person):**
> "This is the Chat page. Ask me a question like 'How much did I spend on Amazon?' and I'll translate it into a safe, read-only SQL query through Gemma 4 and give you the answer."

**Action:** Click the button. Wait for the answer box. Hold for 3 seconds.

**Future .bot upgrade:** Chat.bot will handle follow-up questions, remember context, and suggest next questions.

---

### Shot 3 — Chat Page: Itemized Receipt Query (0:55–1:20)

**Screen:** Chat tab. Click demo button: *"How much did I spend on coffee?"*

**Caption (first person):**
> "I can go deeper than totals. Ask 'How much did I spend on coffee?' and I'll search itemized receipts, not just merchants, so you see exactly what you bought."

**Action:** Click the button. Wait for answer. Hold for 3 seconds.

**Future .bot upgrade:** Chat.bot will combine receipts, track trends, and warn you before you blow a budget.

---

### Shot 4 — Chat Page: Guardrail (1:20–1:45)

**Screen:** Chat tab. Type: *"I just bought a car for $21,000"*

**Caption (first person):**
> "I'm read-only. If you tell me 'I just bought a car for $21,000,' I'll be honest: I can't add transactions yet. No made-up numbers."

**Action:** Type the message, press Enter. Wait for the "Unable to record" answer. Hold for 3 seconds.

**Future .bot upgrade:** Chat.bot will let you add transactions conversationally and double-check them before saving.

---

### Shot 5 — Scan Receipt Page (1:45–2:20)

**Screen:** Scan Receipt tab. Select the Walmart mock receipt, click **Scan Receipt**, then **Save to Transactions**.

**Caption (first person):**
> "The Scan Receipt page breaks receipts into line items. Scan a Walmart receipt, hit Save, and I'll store the transaction, the receipt, and every item separately."

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

**Caption (first person):**
> "The Dashboard shows your cash flow, upcoming bills, savings goals, and where you spend the most — all live from your local database."

**Action:** Click the Dashboard tab. Scroll slowly through the charts. Hold for 5 seconds.

**Future .bot upgrade:** Dashboard.bot will generate plain-English summaries and flag unusual spending automatically.

---

### Shot 7 — All Transactions Page (2:50–3:05)

**Screen:** All Transactions tab.

**Caption (first person):**
> "All Transactions is your searchable, filterable history. You can drill into dates, categories, merchants, or payment methods."

**Action:** Click the All Transactions tab. Scroll the table. Hold for 3 seconds.

**Future .bot upgrade:** All Transactions.bot will let you search with natural language like 'show me every coffee purchase in July'.

---

### Shot 8 — Settings Page: Local AI Proof (3:05–3:35)

**Screen:** Settings tab.

**Caption (first person):**
> "In Settings, you can see the local AI status and switch between Ollama models. If the model goes down, there's a button to restart it — no cloud required."

**Action:** Click the Settings tab. Pause on the Ollama status. Optionally click the model dropdown. Hold for 5 seconds.

**Future .bot upgrade:** Settings.bot will auto-tune model selection based on speed vs. accuracy and warn you before a model download finishes.

---

### Shot 9 — Outro (3:35–3:55)

**Screen:** Back to the homepage, or show the GitHub repo in a browser tab.

**Caption (first person):**
> "That's HAL Budget — your money, your machine, your answers. Built by the HAL team and Steve for the Edge/On-Device track. Code and demo are at github.com/stevevogelaar/HAL-Budget. Thank you, judges, for watching."

**Action:** Hold for 6–8 seconds. End recording.

---

## Pacing Notes

- Total runtime target: **3:30–4:00**.
- Every click is followed by a 2–3 second hold.
- Use cached demo questions for instant answers.
- Keep the "LLM engine online" status visible when possible.
- Long pauses or mistakes can be edited out; each shot is independent.

---

## Restart Points

If the recording is stopped mid-take, resume from any of these clean points:

1. Homepage
2. Chat tab (before clicking a demo question)
3. Scan Receipt tab (before clicking Scan Receipt)
4. Dashboard tab
5. All Transactions tab
6. Settings tab

---

## Roles

- **The AI assistant:** Controls the browser, executes clicks, types messages, controls timing, provides first-person captions.
- **Steve:** Produces the final video, adds optional sound effects/music, uploads to YouTube, attaches to Kaggle.
