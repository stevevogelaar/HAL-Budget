#!/usr/bin/env python3
"""
HAL Budget LLM-SQL Engine
Natural language -> local Ollama LLM -> safe read-only SQL -> natural answer.
All inference and data stay on this machine.
"""

import json
import re
import sqlite3
from pathlib import Path
from typing import Optional, Tuple

import requests


DEFAULT_MODEL = "gemma4:e2b"
OLLAMA_URL = "http://localhost:11434/api/generate"


def _normalize_question(question: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", question.lower()).strip()


SCHEMA_PROMPT = """You are the Budget assistant's SQL translator. Your job is to turn the user's natural-language question into a single safe read-only SQL query for a local SQLite personal-finance database, then summarize what the query will return.

Database schema:

accounts(id, name, type ['checking','savings','credit_card'], account_number, opening_balance, current_balance, credit_limit, is_active, created_at)
categories(id, name, type ['income','expense'], description, is_user_created, created_at)
transactions(id, account_id -> accounts.id, category_id -> categories.id, transaction_date DATE, description, merchant, amount REAL, type ['income','expense'], payment_method, notes, created_at)
recurring_items(id, account_id, category_id, name, description, amount, frequency ['weekly','biweekly','monthly','quarterly','annual'], day_of_month, day_of_week, start_date, end_date, next_due_date, is_active, created_at)
savings_goals(id, name, target_amount, current_amount, target_date, category_id, is_active, created_at)
budgets(id, category_id, amount, year_month 'YYYY-MM', is_active, created_at)
affordability_checks(id, name, total_cost, down_payment, financing_amount, apr, term_months, monthly_payment, extra_monthly_cost, current_income, current_expenses, disposable_income, post_purchase_cash, verdict, recommendation, is_safe, created_at)
receipts(id, transaction_id, merchant, transaction_date DATE, subtotal, tax, total, payment_method, ocr_text, image_path, created_at)
receipt_items(id, receipt_id, name, category_id, quantity, unit_price, line_total, created_at)

Useful views:
v_account_balances(id, name, type, account_number, opening_balance, calculated_balance, credit_limit, is_active)
v_monthly_summary(year_month, total_income, total_expenses, net_cashflow)
v_category_monthly(category_name, year_month, total_spent)
v_upcoming_recurring(id, name, amount, frequency, next_due_date, account_name, category_name)
v_savings_progress(name, target_amount, current_amount, percent_complete, target_date, daily_needed)
v_budget_vs_actual(category_name, budgeted, actual_spent, remaining)
v_affordability_summary(name, total_cost, monthly_payment, extra_monthly_cost, disposable_income, post_purchase_cash, verdict, is_safe, safe_flag)

Rules:
- Generate ONLY a read-only SELECT or WITH query. NEVER INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, ATTACH, DETACH, PRAGMA, or any data-modifying statement.
- For spending, filter type = 'expense'. For income, filter type = 'income'.
- Use LIKE with wildcards for merchant/description matching (e.g., merchant LIKE '%shell%').
- Use strftime('%Y-%m', transaction_date) for month grouping. 'now' refers to today.
- If the user asks for "subscriptions", query the `recurring_items` table where the category is 'Subscriptions'. Also include `next_due_date` and `frequency` when relevant.
- When returning a list of items (subscriptions, upcoming bills, recurring payments), sort by next_due_date or amount, and include all relevant fields.
- When the user asks "do I only buy gas at X?", search broadly for gas-like transactions (Transportation category, or merchant/description containing gas/shell/esso/petro/mobil/bp/etc.) and group by merchant so we can see all gas vendors.
- If the question asks for a list, include ORDER BY date DESC and limit to a reasonable number (e.g., 50).
- If a value judgment like "is it expensive?" or "better deal?" is requested, write a query that returns the spending facts the user would need, but the final answer should note what we can and cannot conclude.
- For comparisons ("cheaper than", "more than", "vs"), write a query that returns totals for BOTH merchants/categories side-by-side.
- If the user asks about a specific product, brand, or item (e.g., "how much did I spend on coffee?", "show me all milk purchases", "Advil spending", "how much Starbucks?"), query `receipt_items` joined to `receipts`. Use `receipt_items.name LIKE '%coffee%'` for item matching. Do NOT search transactions for product names.

Return strictly valid JSON in this format (no markdown fences, no extra prose):

{"sql": "SELECT ...", "intent": "one-sentence summary of what the query does"}

Examples:

Q: How much did I spend on Amazon?
{"sql": "SELECT SUM(amount) AS total, COUNT(*) AS count FROM transactions WHERE merchant LIKE '%amazon%' AND type = 'expense';", "intent": "Total Amazon spending and transaction count"}

Q: Do I only buy gas at Shell?
{"sql": "SELECT merchant, COUNT(*) AS visits, SUM(amount) AS total FROM transactions WHERE type = 'expense' AND (category_id = (SELECT id FROM categories WHERE name = 'Transportation') OR description LIKE '%gas%' OR merchant LIKE '%shell%' OR merchant LIKE '%esso%' OR merchant LIKE '%petro%' OR merchant LIKE '%mobil%' OR merchant LIKE '%bp%') GROUP BY merchant ORDER BY total DESC;", "intent": "All gas-like vendors and their totals"}

Q: What's my checking balance?
{"sql": "SELECT name, calculated_balance FROM v_account_balances WHERE type = 'checking';", "intent": "Current checking account balance"}

Q: What are my subscriptions?
{"sql": "SELECT r.name, r.amount, r.frequency, r.next_due_date FROM recurring_items r JOIN categories c ON r.category_id = c.id WHERE c.name = 'Subscriptions' AND r.is_active = 1 ORDER BY r.next_due_date;", "intent": "Active subscription recurring payments"}

Q: Is Walmart cheaper than Amazon?
{"sql": "SELECT CASE WHEN merchant LIKE '%amazon%' THEN 'Amazon' WHEN merchant LIKE '%walmart%' THEN 'Walmart' ELSE 'Other' END AS vendor, SUM(amount) AS total, COUNT(*) AS visits FROM transactions WHERE type = 'expense' AND (merchant LIKE '%amazon%' OR merchant LIKE '%walmart%') GROUP BY vendor;", "intent": "Compare total spending at Amazon vs Walmart"}

Q: Am I spending too much on dining out?
{"sql": "SELECT SUM(t.amount) AS dining_spent, (SELECT SUM(amount) FROM transactions WHERE type = 'expense') AS total_spent, (SELECT budgeted FROM v_budget_vs_actual WHERE category_name = 'Dining Out') AS budgeted FROM transactions t JOIN categories c ON t.category_id = c.id WHERE c.name = 'Dining Out' AND t.type = 'expense';", "intent": "Dining spending vs total spending and budget"}

Q: How much do I spend per month on average on groceries?
{"sql": "SELECT AVG(monthly_total) AS avg_monthly_groceries FROM (SELECT strftime('%Y-%m', transaction_date) AS month, SUM(amount) AS monthly_total FROM transactions t JOIN categories c ON t.category_id = c.id WHERE c.name = 'Groceries' AND t.type = 'expense' GROUP BY month);", "intent": "Average monthly grocery spending"}

Q: What did I spend this month?
{"sql": "SELECT SUM(amount) AS total FROM transactions WHERE type = 'expense' AND strftime('%Y-%m', transaction_date) = strftime('%Y-%m', 'now');", "intent": "Total spending for the current month"}

Q: How much did I spend on coffee?
{"sql": "SELECT SUM(ri.line_total) AS total, COUNT(*) AS purchases FROM receipt_items ri JOIN receipts r ON ri.receipt_id = r.id WHERE ri.name LIKE '%coffee%' OR ri.name LIKE '%latte%' OR ri.name LIKE '%brew%';", "intent": "Total spending on coffee items across all receipts"}

Q: Show me all milk purchases.
{"sql": "SELECT r.transaction_date, r.merchant, ri.name, ri.quantity, ri.unit_price, ri.line_total FROM receipt_items ri JOIN receipts r ON ri.receipt_id = r.id WHERE ri.name LIKE '%milk%' ORDER BY r.transaction_date DESC;", "intent": "All milk purchases with merchant, date, and price"}
"""


ANSWER_PROMPT = """You are a friendly local-first financial assistant. The user asked a question, you generated a SQL query, and the database returned rows.

Your job: write a concise, natural-language answer for the user using ONLY the facts in the rows. Do not invent data. If the rows don't fully answer the question, say what we can conclude and what we can't.

Keep it to 2-4 sentences plus a short list if needed. Use dollar formatting.

Return strictly valid JSON in this format (no markdown fences):

{{"answer": "your natural-language response here"}}

Question: <<QUESTION>>
SQL: <<SQL>>
Rows (JSON): <<ROWS>>
"""


def _strip_ansi(text: str) -> str:
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


def _sanitize_json(raw: str) -> str:
    raw = _strip_ansi(raw).strip()
    # Remove any markdown code fences the model might emit
    raw = re.sub(r"```(?:json)?", "", raw)
    raw = raw.replace("```", "").strip()
    # If the model prefixed/append thinking text, try to extract the first {...}
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        raw = match.group(0)
    return raw


def _is_read_only_sql(sql: str) -> bool:
    """Reject any statement that could modify the database."""
    cleaned = re.sub(r"--.*?\n", "\n", sql)
    cleaned = re.sub(r"/\*.*?\*/", " ", cleaned, flags=re.DOTALL)
    upper = cleaned.upper().strip()
    forbidden = [
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE",
        "ATTACH", "DETACH", "PRAGMA", "VACUUM", "REPLACE", "COPY", "EXEC"
    ]
    for token in forbidden:
        if re.search(rf"\b{token}\b", upper):
            return False
    allowed_starts = ("SELECT", "WITH", "EXPLAIN")
    if not any(upper.startswith(s) for s in allowed_starts):
        return False
    return True


def ollama_available(model: str = DEFAULT_MODEL, timeout: int = 4) -> bool:
    """Check whether Ollama is reachable and the requested model is pulled."""
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=timeout)
        if r.status_code != 200:
            return False
        data = r.json()
        models = [m.get("name", m.get("model", "")) for m in data.get("models", [])]
        return model in models or model.split(":")[0] in {m.split(":")[0] for m in models}
    except Exception:
        return False


def _ensure_model_loaded(model: str = DEFAULT_MODEL) -> bool:
    """Make sure the model is loaded in Ollama memory without blocking long."""
    try:
        r = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": "hi", "stream": False, "options": {"num_predict": 1}},
            timeout=30
        )
        return r.status_code == 200
    except Exception:
        return False


def generate_sql(question: str, model: str = DEFAULT_MODEL, cache: Optional[dict] = None) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Ask the local LLM to produce SQL for the user's question.
    Uses an optional cache keyed by a normalized question.
    Returns (sql, intent, error).
    """
    normalized = _normalize_question(question)
    if cache is not None:
        cached = cache.get(normalized)
        if cached:
            return cached.get("sql"), cached.get("intent"), None

    if not ollama_available(model):
        return None, None, "Ollama is not running or model is not pulled."

    _ensure_model_loaded(model)

    prompt = SCHEMA_PROMPT + f"\n\nNow answer this question:\nQ: {question}\n"

    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.0, "num_predict": 800}
            },
            timeout=120
        )
        r.raise_for_status()
    except requests.exceptions.Timeout:
        return None, None, "Ollama timed out generating SQL. The model may be loading."
    except Exception as e:
        return None, None, f"Ollama request failed: {e}"

    try:
        raw = r.json().get("response", "")
        sanitized = _sanitize_json(raw)
        parsed = json.loads(sanitized)
        sql = parsed.get("sql", "").strip()
        intent = parsed.get("intent", "").strip()
    except (json.JSONDecodeError, KeyError) as e:
        return None, None, f"Could not parse LLM response as JSON: {e}\nRaw: {raw[:500]}"

    if not sql:
        return None, None, "LLM returned empty SQL."

    if not _is_read_only_sql(sql):
        return None, None, f"Generated SQL was rejected for safety: {sql}"

    if cache is not None:
        cache[normalized] = {"sql": sql, "intent": intent}

    return sql, intent, None


def execute_sql(db_path: str, sql: str) -> Tuple[Optional[list], Optional[str]]:
    """Run a validated SELECT query and return rows."""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(sql)
        rows = cursor.fetchall()
        columns = [d[0] for d in cursor.description] if cursor.description else []
        conn.close()
        return [dict(zip(columns, row)) for row in rows], None
    except Exception as e:
        return None, f"SQL execution error: {e}"


def _format_answer(question: str, sql: str, rows: list, intent: str, model: str = DEFAULT_MODEL) -> str:
    """Turn SQL result rows into a natural-language answer using fast heuristics."""
    if rows is None:
        return "I couldn't run that query."
    if len(rows) == 0:
        return "I found no matching transactions or records for that question."

    q = question.lower()
    keys = [k.lower() for k in rows[0].keys()]
    first_key = keys[0] if keys else "value"

    # Comparison questions (cheaper, more than, vs)
    if any(word in q for word in ["cheaper", "more than", "vs", "versus", "compare"]):
        lines = []
        for r in rows[:10]:
            label = "Unknown"
            for k in ["vendor", "category", "name", "merchant"]:
                if k in keys:
                    label = r.get(k, label)
                    break
            total = r.get("total", r.get("total_spent", r.get("amount", 0)) or 0)
            visits = r.get("visits", r.get("count", r.get("transactions", None)))
            visits_txt = f" across {visits} visits" if visits else ""
            lines.append(f"  - {label}: ${total:,.2f}{visits_txt}")
        summary = "\n".join(lines)
        return f"Here's the spending comparison:\n{summary}\n\nI can't judge 'cheaper' per item (I don't know prices or quantities), but this is what you spent at each."

    # Value judgment: "too much", "expensive", "over budget"
    if any(word in q for word in ["too much", "over budget", "spending too much", "expensive"]):
        if "budgeted" in keys or "remaining" in keys:
            budgeted = rows[0].get("budgeted", 0) or 0
            actual = rows[0].get("actual_spent", rows[0].get("dining_spent", rows[0].get("total_spent", 0))) or 0
            remaining = rows[0].get("remaining", budgeted - actual)
            if remaining < 0:
                return f"You're over budget by ${abs(remaining):,.2f} (spent ${actual:,.2f} vs budget ${budgeted:,.2f})."
            return f"You're within budget: ${actual:,.2f} spent vs ${budgeted:,.2f} budgeted, with ${remaining:,.2f} remaining."
        if len(rows) == 1 and first_key:
            val = list(rows[0].values())[0]
            if isinstance(val, (int, float)):
                return f"You spent ${val:,.2f}. I can't say if that's 'too much' without a budget or comparison, but that's the total."

    # Which category / top spending
    if any(word in q for word in ["which category", "spend the most", "highest spending", "top category"]):
        name = rows[0].get("name", rows[0].get("category_name", rows[0].get("category", "Unknown")))
        total = rows[0].get("total_spent", rows[0].get("total", rows[0].get("amount", 0)) or 0)
        return f"You spend the most on {name}, with ${total:,.2f} total."

    # Single scalar result
    if len(rows) == 1 and len(keys) == 1:
        val = list(rows[0].values())[0]
        key = keys[0]
        if val is None:
            return "I found no matching data for that."
        if isinstance(val, (int, float)):
            if "count" in key or "visits" in key or "num" in key:
                return f"{int(val)}."
            if "avg" in key or "average" in key:
                return f"${val:,.2f} on average."
            return f"${val:,.2f}."
        return f"{val}."

    # Balance / account result
    if any(k in keys for k in ["calculated_balance", "current_balance"]):
        lines = []
        for r in rows:
            name = r.get("name", "Account")
            bal = r.get("calculated_balance", r.get("current_balance", 0))
            lines.append(f"  - {name}: ${bal:,.2f}")
        return "Current balances:\n" + "\n".join(lines)

    # Recurring / subscription items
    if any(k in keys for k in ["next_due_date", "frequency"]) and "amount" in keys:
        # If question is specifically about subscriptions, only keep Subscription category items
        is_subscription_question = any(w in q for w in ["subscription", "netflix", "spotify"])
        filtered = rows
        if is_subscription_question:
            filtered = [r for r in rows if "subscription" in str(r.get("category_name", r.get("name", ""))).lower()]
        if not filtered:
            filtered = rows
        total = sum(r.get("amount", 0) or 0 for r in filtered)
        lines = []
        for r in filtered:
            name = r.get("name", r.get("description", "Item"))
            amount = r.get("amount", 0)
            freq = r.get("frequency", "")
            nxt = r.get("next_due_date", "")
            extra = f" ({freq}, next: {nxt})" if freq or nxt else ""
            lines.append(f"  - {name}: ${amount:,.2f}{extra}")
        return f"Active recurring items ({len(filtered)}, total ${total:,.2f}):\n" + "\n".join(lines)

    # Gas vendor check
    if any(g in q for g in ["shell", "esso", "petro", "gas"]):
        total = sum(r.get("total", r.get("amount", 0) or 0) for r in rows)
        vendors = [r.get("merchant") or r.get("name") or "Unknown" for r in rows]
        if len(vendors) == 1 and "shell" in str(vendors[0]).lower():
            return (
                f"Yes — all of your gas-like spending is at {vendors[0]}: "
                f"${rows[0].get('total', rows[0].get('amount', 0)):,.2f} across "
                f"{rows[0].get('visits', rows[0].get('count', len(rows)))} visits."
            )
        lines = [f"  - {v}: ${r.get('total', r.get('amount', 0) or 0):,.2f} ({r.get('visits', r.get('count', '?'))} visits)" for v, r in zip(vendors, rows)]
        return (
            f"No, you buy gas (or transportation) at more than one vendor. "
            f"Total gas-like spending: ${total:,.2f}.\n\nBreakdown:\n" + "\n".join(lines)
        )

    # List of receipt items (check before transactions because both may have transaction_date/merchant)
    if "name" in keys and any(k in keys for k in ["unit_price", "line_total", "quantity"]):
        total = sum(r.get("line_total", r.get("amount", 0)) or 0 for r in rows)
        lines = [f"Receipt items ({len(rows)} found, total ${total:,.2f}):", ""]
        for r in rows[:50]:
            date = r.get("transaction_date", "")
            merchant = r.get("merchant", "")
            name = r.get("name", "Item")
            qty = r.get("quantity", 1)
            price = r.get("unit_price", r.get("line_total", 0))
            line_total = r.get("line_total", 0)
            lines.append(f"  {date} | {merchant} | {name} x{qty} @ ${price:,.2f} = ${line_total:,.2f}")
        return "\n".join(lines)

    # List of transactions
    if "transaction_date" in keys or "payment_method" in keys:
        total = sum(r.get("amount", 0) or 0 for r in rows)
        lines = [f"Your transactions ({len(rows)} found, total ${total:,.2f}):", ""]
        for r in rows[:50]:
            date = r.get("transaction_date", "")
            merchant = r.get("merchant", r.get("description", ""))[:30]
            amount = r.get("amount", 0)
            method = r.get("payment_method", "")
            lines.append(f"  {date} | ${amount:,.2f} | {merchant} ({method})")
        return "\n".join(lines)

    # Budget vs actual
    if "remaining" in keys:
        lines = []
        for r in rows[:10]:
            cat = r.get("category_name", "Category")
            actual = r.get("actual_spent", 0) or 0
            budgeted = r.get("budgeted", 0) or 0
            remaining = r.get("remaining", 0) or 0
            status = "over" if remaining < 0 else "under"
            lines.append(f"  - {cat}: ${actual:,.2f} spent (budget ${budgeted:,.2f}, {status} by ${abs(remaining):,.2f})")
        return "Budget vs Actual:\n" + "\n".join(lines)

    # Generic table output
    lines = []
    for r in rows[:30]:
        parts = []
        for k, v in r.items():
            if isinstance(v, float):
                v = f"${v:,.2f}"
            parts.append(f"{k}: {v}")
        lines.append("  - " + ", ".join(parts))
    return f"{intent}:\n" + "\n".join(lines)


class LLMSQLEngine:
    def __init__(self, db_path: str = "hal_budget.db", model: str = DEFAULT_MODEL, cache_path: str = "sql_cache.json"):
        self.db_path = db_path
        self.model = model
        self.cache_path = cache_path
        self._sql_cache = self._load_cache()

    def _load_cache(self) -> dict:
        if not self.cache_path:
            return {}
        try:
            with open(self.cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_cache(self):
        if not self.cache_path:
            return
        try:
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(self._sql_cache, f, indent=2)
        except Exception:
            pass

    def warm_cache(self, questions: list):
        """Pre-generate and cache SQL for known questions so first-time use is fast."""
        if not ollama_available(self.model):
            return
        for q in questions:
            key = _normalize_question(q)
            if key in self._sql_cache:
                continue
            sql, intent, _ = generate_sql(q, self.model)
            if sql and intent:
                self._sql_cache[key] = {"sql": sql, "intent": intent}
        self._save_cache()

    def ask(self, question: str) -> dict:
        """
        Ask a natural-language question, get back SQL + result + natural answer.
        Returns a dict with keys: success, answer, sql, intent, error.
        """
        sql, intent, err = generate_sql(question, self.model, cache=self._sql_cache)
        if err:
            return {"success": False, "answer": None, "sql": None, "intent": None, "error": err}

        rows, exec_err = execute_sql(self.db_path, sql)
        if exec_err:
            return {"success": False, "answer": None, "sql": sql, "intent": intent, "error": exec_err}

        answer = _format_answer(question, sql, rows, intent, self.model)
        return {"success": True, "answer": answer, "sql": sql, "intent": intent, "error": None}

    def clear_cache(self):
        self._sql_cache = {}
        if self.cache_path and Path(self.cache_path).exists():
            Path(self.cache_path).unlink()


if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "How much did I spend on Amazon?"
    engine = LLMSQLEngine()
    result = engine.ask(q)
    print(json.dumps(result, indent=2))
