# Session Checkpoint — HAL Budget + Brianne's Pantry Agent

## HAL Budget Video Project (COMPLETE / PARKED)
All assets rendered and ready for editing in Resolve.

### Location
`C:\Users\Steve Vogelaar\Documents\_IT Oversight\Hackathon\HAL-Budget\video\`

### Assets Ready
| Asset | File | Duration |
|---|---|---|
| Intro card video | `intro_card_10s.mp4` | 10s |
| Intro music | `hal-budget-intro.mp3` | ~10s |
| Outro card video | `outro_card_10s.mp4` | 10s |
| Outro music | `hal-budget-outro.mp3` | ~10s |
| Shot 01 — Home | `shots/01_home.mp4` | 35.5s |
| Shot 02 — Chat Amazon | `shots/02_chat_amazon.mp4` | 19s |
| Shot 03 — Chat Coffee | `shots/03_chat_coffee.mp4` | 15s |
| Shot 04 — Guardrail | `shots/04_chat_guardrail.mp4` | 14s |
| Shot 05 — Scan Receipt | `shots/05_scan_receipt.mp4` | 16s |
| Shot 06 — Dashboard | `shots/06_dashboard.mp4` | 12s |
| Shot 07 — All Transactions | `shots/07_transactions.mp4` | 11s |
| Shot 08 — Settings | `shots/08_settings.mp4` | 14s |
| Shot 09 — Outro | `shots/09_outro.mp4` | 20s |
| Live B-roll | `shots/b-roll.mp4` | 270s |

### Overlay Subtitles (transparent PNGs)
Located in `video/subtitles/`:
- `subtitle_amazon.png`
- `subtitle_coffee.png`
- `subtitle_guardrail.png`
- `subtitle_scan.png`
- `subtitle_transactions.png`
- `subtitle_settings.png`

### Edit Reference
- Printable cut list: `video/cut_list.html`
- Email to Tom (sent): `video/email_to_tom.txt`

---

## NEW PROJECT: Brianne's Pantry Agent
Autonomous Agent Track entry for Kaggle Gemma Hackathon.

### Concept
Smart inventory + auto-shopping bot for small business / home pantry.
- Track stock levels in SQLite
- Predict run-out dates based on usage rates
- Auto-generate shopping lists
- Draft supplier emails
- Schedule deliveries
- Reason via Gemma 4 local LLM

### Design Decisions
- **Input:** Text-only for MVP. Voice backend stub prepared but hidden.
- **UI:** Streamlit (new app, separate port from HAL Budget)
- **Brain:** Gemma 4 via Ollama API
- **Data:** SQLite inventory + usage tracking
- **Tools:** Python functions for stock check, list generation, email draft, scheduling

### Architecture Pattern
Same as HAL Budget: LLM-first reasoning with JSON plan output, then tool execution.

### Next Session Goals
1. Scaffold Streamlit app structure
2. Build SQLite schema (inventory, suppliers, usage rates)
3. Create tool functions
4. Engineer Gemma 4 prompt for autonomous planning
5. Build demo pantry UI
6. Package for Kaggle submission

### Deadline
Thursday-Friday build, submit before weekend.
