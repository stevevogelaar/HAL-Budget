#!/usr/bin/env python3
"""
HAL Budget Engine
Natural Language to SQL for Local Personal Finance
All data stays in SQLite on your machine
"""

import sqlite3
import re
import json
from datetime import datetime

from llm_sql_engine import LLMSQLEngine, ollama_available

class BudgetEngine:
    def __init__(self, db_path='hal_budget.db', model=None):
        self.db_path = db_path
        if model is None:
            from llm_sql_engine import DEFAULT_MODEL
            model = DEFAULT_MODEL
        self.llm_engine = LLMSQLEngine(db_path=db_path, model=model)
        
    def query(self, user_question):
        """
        Main entry point: natural language question -> SQL -> natural language answer.
        Uses local Ollama LLM first; falls back to rule-based if Ollama is unavailable.
        """
        question = user_question.lower().strip()
        
        # Catch questions we know we cannot answer before asking the model
        unsupported = self._detect_unsupported_intent(question)
        if unsupported:
            return unsupported
        
        # Try local LLM SQL generation first (robust, flexible)
        if ollama_available(self.llm_engine.model):
            result = self.llm_engine.ask(user_question)
            if result.get("success"):
                return result["answer"]
            # If LLM fails for some reason, fall through to rules
        
        # Fallback: rule-based pattern matching
        answer = self._rule_based_query(question)
        if answer:
            return answer
        
        # Final fallback
        return self._fallback_response(question)
    
    def _rule_based_query(self, q):
        """Pattern match common questions to SQL queries"""
        
        # === BUDGET VS ACTUAL (check early — contains 'vs') ===
        if 'budget vs actual' in q or 'budget versus actual' in q or 'show me my budget' in q:
            return self._handle_budget_query(q)
        
        # === COMPARISONS ===
        if 'cheaper' in q or 'more than' in q or 'compare' in q or ' vs ' in q or ' versus ' in q:
            return self._handle_comparison_query(q)
        
        # === ANALYSIS QUESTIONS WE CANNOT ANSWER (be honest) ===
        # If user asks for value judgment we don't have data for
        if any(word in q for word in ['better', 'worse', 'good deal', 'worth it', 'expensive', 'cheap']):
            return self._handle_unanswerable_query(q)
        
        # === AFFORDABILITY (overlaps with car, shoes, laptop) ===
        if 'can i afford' in q or 'afford' in q:
            return self._handle_affordability_query(q)
        
        # === MERCHANT-SPECIFIC ===
        if 'amazon' in q or 'walmart' in q or 'mcdonalds' in q:
            return self._handle_merchant_query(q)
        
        # === CATEGORY-SPECIFIC (except transport — 'car' overlaps with affordability) ===
        if 'groceries' in q or 'food' in q:
            return self._handle_category_query(q, 'Groceries')
        if 'rent' in q:
            return self._handle_rent_query(q)
        if 'subscription' in q or 'netflix' in q or 'spotify' in q:
            return self._handle_subscriptions_query(q)
        if 'dining' in q or 'restaurant' in q or 'eating out' in q:
            return self._handle_category_query(q, 'Dining Out')
        
        # === TRANSPORT (checked after affordability) ===
        if 'transport' in q or 'gas' in q or 'car' in q:
            return self._handle_transport_query(q)
        
        # === UPCOMING / RECURRING ===
        if 'next' in q and ('payment' in q or 'due' in q or 'bill' in q):
            return self._handle_upcoming_query(q)
        if 'when' in q and ('due' in q or 'end' in q):
            return self._handle_when_due_query(q)
        
        # === BUDGET VS ACTUAL ===
        if 'budget' in q:
            return self._handle_budget_query(q)
        
        # === BALANCE / ACCOUNT ===
        if 'balance' in q or 'how much (money|cash)' in q:
            return self._handle_balance_query(q)
        
        # === SAVINGS GOALS ===
        if 'savings' in q or 'saved' in q or 'vacation' in q or 'emergency fund' in q or 'goal' in q:
            return self._handle_savings_query(q)
        
        # === MONTHLY SUMMARY ===
        if 'this month' in q or 'last month' in q or 'monthly' in q:
            return self._handle_monthly_summary(q)
        
        # === INCOME / EXPENSE SUMMARY (generic, check last) ===
        if re.search(r'how much (did|do) i (spend|make|earn)', q):
            return self._handle_spend_earn_query(q)
        
        return None
    
    def _run_sql(self, sql, params=()):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(sql, params)
        result = cursor.fetchall()
        conn.close()
        return result
    
    def _handle_spend_earn_query(self, q):
        """How much did I spend/make/earn"""
        if 'spend' in q:
            result = self._run_sql("SELECT SUM(amount) FROM transactions WHERE type = 'expense'")
            total = result[0][0] if result and result[0][0] else 0
            return f"You have spent ${total:,.2f} total across all accounts and categories."
        else:
            result = self._run_sql("SELECT SUM(amount) FROM transactions WHERE type = 'income'")
            total = result[0][0] if result and result[0][0] else 0
            return f"You have earned ${total:,.2f} total across the tracked period."
    
    def _handle_merchant_query(self, q):
        """Amazon, Walmart, etc."""
        merchant = 'Amazon' if 'amazon' in q else 'Walmart' if 'walmart' in q else 'McDonalds'
        
        # Check if user wants a LIST of transactions, not just a total
        wants_list = any(word in q for word in ['all', 'list', 'details', 'transactions', 'show me'])
        
        if wants_list:
            result = self._run_sql(
                """SELECT transaction_date, description, amount, payment_method 
                   FROM transactions 
                   WHERE merchant LIKE ? AND type = 'expense'
                   ORDER BY transaction_date DESC""",
                (f'%{merchant}%',)
            )
            if not result:
                return f"No transactions found at {merchant}."
            
            lines = [f"Your transactions at {merchant}:", ""]
            total = 0
            for row in result:
                date, desc, amount, method = row
                total += amount
                lines.append(f"  {date} | ${amount:.2f} | {desc} ({method})")
            lines.append("")
            lines.append(f"Total: ${total:,.2f} across {len(result)} transactions")
            return "\n".join(lines)
        
        # Default: just the summary
        result = self._run_sql(
            "SELECT SUM(amount) FROM transactions WHERE merchant LIKE ? AND type = 'expense'",
            (f'%{merchant}%',)
        )
        total = result[0][0] if result and result[0][0] else 0
        count = self._run_sql(
            "SELECT COUNT(*) FROM transactions WHERE merchant LIKE ? AND type = 'expense'",
            (f'%{merchant}%',)
        )[0][0]
        return f"You spent ${total:,.2f} at {merchant} across {count} transactions."
    
    def _handle_category_query(self, q, category):
        """Category spending"""
        result = self._run_sql(
            """SELECT SUM(t.amount) FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE c.name = ? AND t.type = 'expense'""",
            (category,)
        )
        total = result[0][0] if result and result[0][0] else 0
        return f"You spent ${total:,.2f} on {category} across all tracked months."
    
    def _handle_rent_query(self, q):
        """Rent-specific queries"""
        if 'when' in q or 'next' in q or 'due' in q:
            result = self._run_sql(
                "SELECT next_due_date FROM recurring_items WHERE name LIKE '%Rent%'"
            )
            if result:
                return f"Your next rent payment is due {result[0][0]}."
        result = self._run_sql(
            """SELECT SUM(t.amount) FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE c.name = 'Rent' AND t.type = 'expense'"""
        )
        total = result[0][0] if result and result[0][0] else 0
        return f"You have paid ${total:,.2f} in rent across the tracked period."
    
    def _handle_subscriptions_query(self, q):
        """Subscriptions and recurring services"""
        result = self._run_sql(
            """SELECT r.name, r.amount, r.next_due_date FROM recurring_items r
            JOIN categories c ON r.category_id = c.id
            WHERE c.name = 'Subscriptions' AND r.is_active = 1
            ORDER BY r.next_due_date"""
        )
        if not result:
            return "No active subscriptions found."
        
        total = sum(row[1] for row in result)
        details = "\n".join([f"  - {row[0]}: ${row[1]:.2f}/mo (next: {row[2]})" for row in result])
        return f"Your active subscriptions total ${total:.2f}/month:\n{details}"
    
    def _handle_transport_query(self, q):
        """Transportation / car"""
        if 'car payment' in q or 'lease' in q:
            result = self._run_sql(
                "SELECT amount, next_due_date, end_date FROM recurring_items WHERE name LIKE '%Car Payment%'"
            )
            if result:
                end = result[0][2] or 'unknown'
                return f"Your car payment is ${result[0][0]:.2f}/mo. Next due: {result[0][1]}. Ends: {end}."
        result = self._run_sql(
            """SELECT SUM(t.amount) FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE c.name = 'Transportation' AND t.type = 'expense'"""
        )
        total = result[0][0] if result and result[0][0] else 0
        return f"You spent ${total:,.2f} on transportation (gas, transit, car payment)."
    
    def _handle_upcoming_query(self, q):
        """Upcoming payments"""
        result = self._run_sql(
            """SELECT name, amount, next_due_date FROM recurring_items
            WHERE is_active = 1 AND next_due_date IS NOT NULL
            ORDER BY next_due_date LIMIT 5"""
        )
        if not result:
            return "No upcoming payments found."
        details = "\n".join([f"  - {row[0]}: ${row[1]:.2f} on {row[2]}" for row in result])
        return f"Your next 5 upcoming payments:\n{details}"
    
    def _handle_when_due_query(self, q):
        """When is something due / ending"""
        if 'car' in q:
            result = self._run_sql(
                "SELECT end_date FROM recurring_items WHERE name LIKE '%Car%'"
            )
            if result and result[0][0]:
                return f"Your car payment ends on {result[0][0]}."
        return self._handle_upcoming_query(q)
    
    def _handle_budget_query(self, q):
        """Budget vs actual"""
        result = self._run_sql("SELECT * FROM v_budget_vs_actual LIMIT 5")
        if not result:
            return "No budget data found."
        
        lines = []
        for row in result:
            cat, budgeted, actual, remaining = row[0], row[1] or 0, row[2] or 0, row[3] or 0
            status = "over" if remaining < 0 else "under"
            lines.append(f"  - {cat}: ${actual:.2f} spent (budget: ${budgeted:.2f}, {status} by ${abs(remaining):.2f})")
        return "Budget vs Actual (July 2026):\n" + "\n".join(lines)
    
    def _handle_affordability_query(self, q):
        """Can I afford X?"""
        if 'car' in q:
            result = self._run_sql(
                "SELECT * FROM affordability_checks WHERE name LIKE '%Car%'"
            )
            if result:
                row = result[0]
                safe = "Yes" if row[15] else "Tight"
                return f"{safe}. {row[13]}"
        if 'shoe' in q:
            result = self._run_sql(
                "SELECT * FROM affordability_checks WHERE name LIKE '%Shoe%'"
            )
            if result:
                return result[0][13]
        if 'laptop' in q or 'macbook' in q:
            result = self._run_sql(
                "SELECT * FROM affordability_checks WHERE name LIKE '%MacBook%'"
            )
            if result:
                return result[0][13]
        
        # Generic: find closest match
        result = self._run_sql("SELECT name, verdict FROM affordability_checks LIMIT 1")
        if result:
            return f"Closest match: {result[0][0]} — {result[0][1]}"
        return "I don't have a what-if scenario for that yet. You can add one!"
    
    def _handle_balance_query(self, q):
        """Account balances — LIVE from v_account_balances"""
        result = self._run_sql("SELECT name, calculated_balance, type FROM v_account_balances WHERE is_active = 1")
        if not result:
            return "No account data found."
        
        lines = []
        for row in result:
            name, bal, acct_type = row[0], row[1], row[2]
            if acct_type == 'credit_card':
                lines.append(f"  - {name}: ${bal:,.2f} (credit limit: $5,000)")
            else:
                lines.append(f"  - {name}: ${bal:,.2f}")
        return "Current balances:\n" + "\n".join(lines)
    
    def _handle_savings_query(self, q):
        """Savings goals"""
        result = self._run_sql(
            "SELECT name, target_amount, current_amount, target_date FROM savings_goals WHERE is_active = 1"
        )
        if not result:
            return "No savings goals set."
        
        lines = []
        for row in result:
            name, target, current, target_date = row
            pct = (current / target * 100) if target else 0
            lines.append(f"  - {name}: ${current:,.2f} / ${target:,.2f} ({pct:.1f}%)")
        return "Savings goals:\n" + "\n".join(lines)
    
    def _handle_monthly_summary(self, q):
        """Monthly summary"""
        month = '2026-07' if 'this month' in q or 'july' in q else '2026-06'
        result = self._run_sql(
            "SELECT total_income, total_expenses, net_cashflow FROM v_monthly_summary WHERE year_month = ?",
            (month,)
        )
        if result:
            inc, exp, net = result[0]
            return f"{month}: Income ${inc:,.2f}, Expenses ${exp:,.2f}, Net ${net:,.2f}"
        return "No data for that month."
    
    def _handle_comparison_query(self, q):
        """Comparisons like 'Is Walmart cheaper than Amazon?'"""
        # Extract both merchants from the question
        merchants = []
        if 'amazon' in q:
            merchants.append('Amazon')
        if 'walmart' in q:
            merchants.append('Walmart')
        if 'mcdonalds' in q:
            merchants.append('McDonalds')
        if 'tim hortons' in q:
            merchants.append('Tim Hortons')
        if 'shell' in q:
            merchants.append('Shell')
        
        if len(merchants) >= 2:
            m1, m2 = merchants[0], merchants[1]
            r1 = self._run_sql("SELECT SUM(amount), COUNT(*) FROM transactions WHERE merchant LIKE ? AND type = 'expense'", (f'%{m1}%',))
            r2 = self._run_sql("SELECT SUM(amount), COUNT(*) FROM transactions WHERE merchant LIKE ? AND type = 'expense'", (f'%{m2}%',))
            
            t1, c1 = (r1[0][0] or 0, r1[0][1] or 0)
            t2, c2 = (r2[0][0] or 0, r2[0][1] or 0)
            
            avg1 = t1 / c1 if c1 else 0
            avg2 = t2 / c2 if c2 else 0
            
            return (
                f"Here's what I know:\n"
                f"  - {m1}: ${t1:.2f} across {c1} transactions (avg ${avg1:.2f}/visit)\n"
                f"  - {m2}: ${t2:.2f} across {c2} transactions (avg ${avg2:.2f}/visit)\n\n"
                f"But I can't tell you which is 'cheaper' — that depends on what you buy. "
                f"I only track how much you spent, not the price per item."
            )
        
        return "I can compare spending between two merchants if you name them both."
    
    def _handle_unanswerable_query(self, q):
        """Honest responses for questions beyond our data."""
        if 'better' in q or 'worth' in q:
            return (
                "I don't have enough information to answer that.\n\n"
                "I track your spending, but I don't know:\n"
                "  - Current market prices\n"
                "  - Product quality or reviews\n"
                "  - Your personal preferences\n\n"
                "I can tell you how much you've spent at each place, though!"
            )
        
        if 'expensive' in q or 'cheap' in q:
            return (
                "I can't judge what's expensive or cheap — that's subjective and varies by product.\n\n"
                "What I can tell you: how much you've spent at a store, or whether a purchase fits your budget."
            )
        
        return (
            "I don't have the data to answer that question.\n\n"
            "I know your transactions, balances, and budgets — but not external pricing, quality, or opinions. "
            "Ask me about spending, upcoming bills, or whether you can afford something instead!"
        )
    
    def _detect_unsupported_intent(self, q):
        """
        Detect questions that sound like data-entry or real-world events
        we don't have the power to act on (e.g., 'I just bought a car').
        Returns a friendly 'Unable' message, or None if we should try to answer.
        """
        # Recording a new transaction / purchase / income event
        record_verbs = ['bought', 'purchased', 'paid', 'spent', 'got', 'received', 'made', 'earned', 'cost me']
        explicit_record = any(v in q for v in ['add', 'record', 'enter'])
        has_first_person = bool(re.search(r'\b(i|my|we|our)\b', q))
        # Match $12,345.67, $123, 21,000, 500 dollars, or bare large numbers like 21000
        has_amount = bool(re.search(r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*(?:dollars|usd|cad)\b|\b\d{1,3}(?:,\d{3})+\b|\b\d{4,}\b', q))
        
        if (has_first_person or explicit_record) and has_amount and (any(v in q for v in record_verbs) or explicit_record):
            return (
                "Unable to record that. I can't add new transactions or change your bank balance from chat yet.\n\n"
                "To track this purchase, use the **Receipt Scanner** tab, or add it directly to the database.\n\n"
                "I can still tell you how much you've already spent, what your balance is, or whether a purchase fits your budget."
            )
        
        # Income events described in first person (paycheck, bonus, etc.)
        income_nouns = ['paycheck', 'paycheque', 'salary', 'bonus', 'deposit', 'refund', 'dividend']
        if has_first_person and has_amount and any(n in q for n in income_nouns):
            return (
                "Unable to record that income. I can't add new transactions or change your account balance from chat yet.\n\n"
                "Use the Receipt Scanner tab or update the database directly."
            )
        
        # Explicit request to add/modify data
        if explicit_record and ('transaction' in q or 'expense' in q or 'income' in q or 'purchase' in q):
            return (
                "Unable to add that transaction. I can only read your existing data.\n\n"
                "Use the Receipt Scanner tab or update the database directly."
            )
        
        return None
    
    def _fallback_response(self, q):
        """When no rule matches"""
        return (
            f"Unable to answer that right now. I heard: '{q}'.\n\n"
            "I can help with:\n"
            "  - Spending by category or merchant\n"
            "  - Upcoming bills and due dates\n"
            "  - 'Can I afford [item]?'\n"
            "  - Account balances and savings goals"
        )
    
    def demo_queries(self):
        """Return a list of demo-ready questions"""
        return [
            "How much did I spend on Amazon?",
            "When is my next rent payment?",
            "Can I afford a new car?",
            "What are my subscriptions?",
            "How much do I spend on groceries?",
            "What's my checking balance?",
            "Show me my budget vs actual",
            "When does my car payment end?",
            "How much have I saved?",
            "What did I spend this month?"
        ]
    
    def close(self):
        # No persistent connection to close since we open per-query
        pass

# === Quick test ===
if __name__ == '__main__':
    engine = BudgetEngine()
    
    print("HAL Budget Engine Demo")
    print("=" * 50)
    
    for q in engine.demo_queries():
        print(f"\nQ: {q}")
        print(f"A: {engine.query(q)}")
    
    engine.close()
