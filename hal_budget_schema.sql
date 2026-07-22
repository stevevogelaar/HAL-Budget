-- HAL Budget SQLite Schema v2
-- Created: 2026-07-22
-- For: GDG Windsor Gemma Hackathon 2026
-- All data stays local on your machine

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Drop views and tables if they exist (clean slate for rebuilds)
DROP VIEW IF EXISTS v_affordability_summary;
DROP VIEW IF EXISTS v_budget_vs_actual;
DROP VIEW IF EXISTS v_savings_progress;
DROP VIEW IF EXISTS v_upcoming_recurring;
DROP VIEW IF EXISTS v_category_monthly;
DROP VIEW IF EXISTS v_monthly_summary;
DROP VIEW IF EXISTS v_account_balances;
DROP TABLE IF EXISTS receipt_items;
DROP TABLE IF EXISTS receipts;
DROP TABLE IF EXISTS what_if_expenses;
DROP TABLE IF EXISTS affordability_checks;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS recurring_items;
DROP TABLE IF EXISTS budgets;
DROP TABLE IF EXISTS savings_goals;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS accounts;

-- Accounts: checking, savings, credit cards, cash
CREATE TABLE accounts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    type            TEXT NOT NULL CHECK (type IN ('checking', 'savings', 'credit_card', 'cash')),
    account_number  TEXT,
    opening_balance REAL DEFAULT 0.00,
    current_balance REAL DEFAULT 0.00,
    credit_limit    REAL,
    is_active       INTEGER DEFAULT 1,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Categories: user can add more
CREATE TABLE categories (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL UNIQUE,
    type            TEXT NOT NULL CHECK (type IN ('income', 'expense', 'savings')),
    description     TEXT,
    is_user_created INTEGER DEFAULT 0,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions: every spend, income, transfer
CREATE TABLE transactions (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id          INTEGER NOT NULL REFERENCES accounts(id),
    category_id         INTEGER REFERENCES categories(id),
    transaction_date    DATE NOT NULL,
    description         TEXT NOT NULL,
    merchant            TEXT,
    amount              REAL NOT NULL DEFAULT 0.00,
    type                TEXT NOT NULL CHECK (type IN ('income', 'expense', 'transfer')),
    payment_method      TEXT CHECK (payment_method IN ('cash', 'debit', 'credit', 'transfer', 'direct_deposit')),
    notes               TEXT,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Recurring items: rent, subscriptions, car payments with end dates
CREATE TABLE recurring_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id      INTEGER NOT NULL REFERENCES accounts(id),
    category_id     INTEGER REFERENCES categories(id),
    name            TEXT NOT NULL,
    description     TEXT,
    amount          REAL NOT NULL DEFAULT 0.00,
    frequency       TEXT NOT NULL CHECK (frequency IN ('weekly', 'biweekly', 'monthly', 'quarterly', 'annual')),
    day_of_month    INTEGER,
    day_of_week     INTEGER,
    start_date      DATE NOT NULL,
    end_date        DATE,
    next_due_date   DATE,
    is_active       INTEGER DEFAULT 1,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Savings goals: vacation, emergency fund, etc.
CREATE TABLE savings_goals (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    target_amount   REAL NOT NULL DEFAULT 0.00,
    current_amount  REAL NOT NULL DEFAULT 0.00,
    target_date     DATE,
    category_id     INTEGER REFERENCES categories(id),
    is_active       INTEGER DEFAULT 1,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Monthly budgets by category
CREATE TABLE budgets (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id     INTEGER NOT NULL REFERENCES categories(id),
    amount          REAL NOT NULL DEFAULT 0.00,
    year_month      TEXT NOT NULL,
    is_active       INTEGER DEFAULT 1,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(category_id, year_month)
);

-- Affordability checks: "Can I afford X?"
CREATE TABLE affordability_checks (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    name                TEXT NOT NULL,
    total_cost          REAL NOT NULL DEFAULT 0.00,
    down_payment        REAL DEFAULT 0.00,
    financing_amount    REAL DEFAULT 0.00,
    apr                 REAL DEFAULT 0.00,
    term_months         INTEGER,
    monthly_payment     REAL DEFAULT 0.00,
    extra_monthly_cost  REAL DEFAULT 0.00,
    current_income      REAL DEFAULT 0.00,
    current_expenses    REAL DEFAULT 0.00,
    disposable_income   REAL DEFAULT 0.00,
    post_purchase_cash  REAL DEFAULT 0.00,
    verdict             TEXT,
    recommendation      TEXT,
    is_safe             INTEGER DEFAULT 0,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- What-if expenses: potential new costs (insurance, gas for new car, etc.)
CREATE TABLE what_if_expenses (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    affordability_check_id  INTEGER NOT NULL REFERENCES affordability_checks(id),
    name                    TEXT NOT NULL,
    amount                  REAL NOT NULL DEFAULT 0.00,
    frequency               TEXT NOT NULL CHECK (frequency IN ('weekly', 'biweekly', 'monthly', 'quarterly', 'annual')),
    description             TEXT,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Receipts: itemized receipts from OCR/scanned documents
CREATE TABLE receipts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id  INTEGER REFERENCES transactions(id) ON DELETE SET NULL,
    merchant        TEXT NOT NULL,
    transaction_date DATE,
    subtotal        REAL DEFAULT 0.00,
    tax             REAL DEFAULT 0.00,
    total           REAL NOT NULL DEFAULT 0.00,
    payment_method  TEXT,
    ocr_text        TEXT,
    image_path      TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Receipt line items: individual products/services from a receipt
CREATE TABLE receipt_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    receipt_id      INTEGER NOT NULL REFERENCES receipts(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    category_id     INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    quantity        REAL DEFAULT 1,
    unit_price      REAL NOT NULL DEFAULT 0.00,
    line_total      REAL NOT NULL DEFAULT 0.00,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for fast queries
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_account ON transactions(account_id);
CREATE INDEX idx_transactions_category ON transactions(category_id);
CREATE INDEX idx_transactions_merchant ON transactions(merchant);
CREATE INDEX idx_recurring_next_due ON recurring_items(next_due_date);
CREATE INDEX idx_affordability_name ON affordability_checks(name);
CREATE INDEX idx_receipts_merchant ON receipts(merchant);
CREATE INDEX idx_receipts_date ON receipts(transaction_date);
CREATE INDEX idx_receipt_items_name ON receipt_items(name);
CREATE INDEX idx_receipt_items_receipt ON receipt_items(receipt_id);

-- View: live account balances from opening balance + transactions
CREATE VIEW v_account_balances AS
SELECT 
    a.id,
    a.name,
    a.type,
    a.account_number,
    a.opening_balance,
    COALESCE(SUM(CASE WHEN t.type = 'income' THEN t.amount WHEN t.type = 'expense' THEN -t.amount ELSE 0 END), 0) + a.opening_balance AS calculated_balance,
    a.credit_limit,
    a.is_active
FROM accounts a
LEFT JOIN transactions t ON t.account_id = a.id
GROUP BY a.id, a.name, a.type, a.opening_balance, a.credit_limit;

-- View: monthly summary
CREATE VIEW v_monthly_summary AS
SELECT 
    strftime('%Y-%m', transaction_date) AS year_month,
    SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) AS total_income,
    SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) AS total_expenses,
    SUM(CASE WHEN type = 'income' THEN amount ELSE -amount END) AS net_cashflow
FROM transactions
GROUP BY strftime('%Y-%m', transaction_date)
ORDER BY year_month;

-- View: spending by category per month
CREATE VIEW v_category_monthly AS
SELECT 
    c.name AS category_name,
    strftime('%Y-%m', t.transaction_date) AS year_month,
    SUM(t.amount) AS total_spent
FROM transactions t
JOIN categories c ON t.category_id = c.id
WHERE t.type = 'expense'
GROUP BY c.name, strftime('%Y-%m', t.transaction_date)
ORDER BY year_month, total_spent DESC;

-- View: upcoming recurring payments
CREATE VIEW v_upcoming_recurring AS
SELECT 
    r.id,
    r.name,
    r.amount,
    r.frequency,
    r.next_due_date,
    a.name AS account_name,
    c.name AS category_name
FROM recurring_items r
JOIN accounts a ON r.account_id = a.id
LEFT JOIN categories c ON r.category_id = c.id
WHERE r.is_active = 1
    AND (r.end_date IS NULL OR r.end_date >= date('now'))
ORDER BY r.next_due_date;

-- View: savings goal progress
CREATE VIEW v_savings_progress AS
SELECT 
    name,
    target_amount,
    current_amount,
    ROUND((current_amount / target_amount) * 100, 2) AS percent_complete,
    target_date,
    CASE 
        WHEN target_date IS NOT NULL AND julianday(target_date) > julianday('now') 
        THEN ROUND((target_amount - current_amount) / (julianday(target_date) - julianday('now')), 2)
        ELSE NULL 
    END AS daily_needed
FROM savings_goals
WHERE is_active = 1;

-- View: budget vs actual current month
CREATE VIEW v_budget_vs_actual AS
SELECT 
    c.name AS category_name,
    COALESCE(b.amount, 0) AS budgeted,
    COALESCE(SUM(t.amount), 0) AS actual_spent,
    COALESCE(b.amount, 0) - COALESCE(SUM(t.amount), 0) AS remaining
FROM categories c
LEFT JOIN budgets b ON c.id = b.category_id AND b.year_month = strftime('%Y-%m', 'now')
LEFT JOIN transactions t ON c.id = t.category_id 
    AND t.type = 'expense'
    AND strftime('%Y-%m', t.transaction_date) = strftime('%Y-%m', 'now')
WHERE c.type = 'expense'
GROUP BY c.name, b.amount
ORDER BY actual_spent DESC;

-- View: affordability check summary
CREATE VIEW v_affordability_summary AS
SELECT 
    name,
    total_cost,
    monthly_payment,
    extra_monthly_cost,
    disposable_income,
    post_purchase_cash,
    verdict,
    is_safe,
    CASE 
        WHEN is_safe = 1 THEN '✓ Yes, affordable'
        ELSE '⚠ Tight or risky'
    END AS safe_flag
FROM affordability_checks
ORDER BY created_at DESC;
