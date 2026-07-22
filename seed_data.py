#!/usr/bin/env python3
"""
HAL Budget - Seed Database with Realistic Fake Data
Creates SQLite database at hal_budget.db with 6 months of transactions
"""

import sqlite3
import random
from datetime import datetime, timedelta

def connect():
    return sqlite3.connect('hal_budget.db')

def reset_db(conn):
    cursor = conn.cursor()
    with open('hal_budget_schema.sql', 'r') as f:
        cursor.executescript(f.read())
    conn.commit()

def seed_accounts(cursor):
    accounts = [
        (1, 'Main Checking', 'checking', '00123456789', 3250.00, 3250.00, None, 1),
        (2, 'Visa Credit', 'credit_card', '4512****3456', 0.00, -1247.33, 5000.00, 1),
        (3, 'Cash Wallet', 'cash', None, 200.00, 45.00, None, 1)
    ]
    cursor.executemany("""
        INSERT INTO accounts (id, name, type, account_number, opening_balance, current_balance, credit_limit, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, accounts)

def seed_categories(cursor):
    categories = [
        (1, 'Income', 'income', 'Paychecks, freelance, gifts', 0),
        (2, 'Rent', 'expense', 'Monthly apartment rent', 0),
        (3, 'Utilities', 'expense', 'Hydro, gas, water, internet', 0),
        (4, 'Groceries', 'expense', 'Food and household supplies', 0),
        (5, 'Transportation', 'expense', 'Gas, transit, parking, maintenance', 0),
        (6, 'Subscriptions', 'expense', 'Netflix, Spotify, gym, etc.', 0),
        (7, 'Entertainment', 'expense', 'Movies, events, hobbies', 0),
        (8, 'Dining Out', 'expense', 'Restaurants, fast food, coffee', 0),
        (9, 'Shopping', 'expense', 'Clothing, electronics, Amazon', 0),
        (10, 'Healthcare', 'expense', 'Pharmacy, dental, vision', 0),
        (11, 'Savings', 'savings', 'Money set aside', 0),
        (12, 'Cash Withdrawal', 'expense', 'ATM withdrawals', 0),
    ]
    cursor.executemany("""
        INSERT INTO categories (id, name, type, description, is_user_created)
        VALUES (?, ?, ?, ?, ?)
    """, categories)

def seed_recurring(cursor):
    today = datetime.now().date()
    recurring = [
        (1, 1, 2, 'Rent Payment', 'Apartment rent', 1450.00, 'monthly', 1, None, '2026-01-01', None, (today.replace(day=1) + timedelta(days=31)).replace(day=1), 1),
        (2, 2, 6, 'Netflix', 'Streaming subscription', 15.49, 'monthly', 15, None, '2026-01-01', None, '2026-08-15', 1),
        (3, 2, 6, 'Spotify', 'Music subscription', 10.99, 'monthly', 20, None, '2026-01-01', None, '2026-08-20', 1),
        (4, 2, 6, 'Gym Membership', 'Fit4Less', 24.99, 'biweekly', None, 2, '2026-01-01', None, '2026-08-07', 1),
        (5, 1, 5, 'Car Payment', 'Honda Civic lease', 385.00, 'monthly', 5, None, '2026-01-01', '2028-05-05', '2026-08-05', 1),
        (6, 1, 3, 'Hydro', 'Electricity bill', 85.00, 'monthly', 10, None, '2026-01-01', None, '2026-08-10', 1),
        (7, 1, 3, 'Internet', 'Bell Fibe 500', 89.99, 'monthly', 12, None, '2026-01-01', None, '2026-08-12', 1),
        (8, 2, 6, 'Phone Plan', 'Koodo mobile', 55.00, 'monthly', 1, None, '2026-01-01', None, '2026-08-01', 1),
    ]
    cursor.executemany("""
        INSERT INTO recurring_items 
        (id, account_id, category_id, name, description, amount, frequency, day_of_month, day_of_week, start_date, end_date, next_due_date, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, recurring)

def seed_savings_goals(cursor):
    goals = [
        (1, 'Vacation Fund', 3000.00, 1200.00, '2026-12-15', 11, 1),
        (2, 'Emergency Fund', 10000.00, 3500.00, None, 11, 1),
        (3, 'New Laptop', 1800.00, 600.00, '2026-11-01', 11, 1),
    ]
    cursor.executemany("""
        INSERT INTO savings_goals (id, name, target_amount, current_amount, target_date, category_id, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, goals)

def seed_budgets(cursor):
    budgets = [
        (2, 1450.00, '2026-07'), (3, 250.00, '2026-07'), (4, 500.00, '2026-07'),
        (5, 300.00, '2026-07'), (6, 150.00, '2026-07'), (7, 100.00, '2026-07'),
        (8, 200.00, '2026-07'), (9, 200.00, '2026-07'), (10, 100.00, '2026-07'),
    ]
    cursor.executemany("""
        INSERT INTO budgets (category_id, amount, year_month)
        VALUES (?, ?, ?)
    """, budgets)

def seed_receipts(cursor):
    """Seed itemized receipts with line-item detail for granular queries."""
    from datetime import datetime
    
    cat_ids = {
        'Income': 1, 'Rent': 2, 'Utilities': 3, 'Groceries': 4,
        'Transportation': 5, 'Subscriptions': 6, 'Entertainment': 7,
        'Dining Out': 8, 'Shopping': 9, 'Healthcare': 10, 'Savings': 11
    }
    
    # Use explicit high IDs so they don't collide with generate_transactions
    receipt_data = [
        {
            'id': 9001,
            'tx_id': 9001,
            'merchant': 'Walmart Supercentre',
            'date': '2026-07-08',
            'payment_method': 'debit',
            'category': 'Groceries',
            'items': [
                ('2% Milk 4L', 'Groceries', 2, 4.99, 9.98),
                ('Large Eggs 18pk', 'Groceries', 1, 6.49, 6.49),
                ('Whole Wheat Bread', 'Groceries', 1, 3.29, 3.29),
                ('Ground Coffee 340g', 'Groceries', 1, 8.99, 8.99),
                ('Bananas Bunch', 'Groceries', 1, 2.49, 2.49),
                ('Chicken Breasts 1kg', 'Groceries', 1, 14.99, 14.99),
            ],
            'tax': 0.00,
        },
        {
            'id': 9002,
            'tx_id': 9002,
            'merchant': 'Amazon.ca',
            'date': '2026-07-18',
            'payment_method': 'credit',
            'category': 'Shopping',
            'items': [
                ('USB-C Cable 2-pack', 'Shopping', 1, 19.99, 19.99),
                ('Running Socks 6-pack', 'Shopping', 1, 24.99, 24.99),
                ('Vitamin D3 1000IU', 'Healthcare', 1, 12.99, 12.99),
                ('Kindle eBook', 'Entertainment', 1, 14.99, 14.99),
                ('Notebook Set', 'Shopping', 1, 11.99, 11.99),
            ],
            'tax': 5.21,
        },
        {
            'id': 9003,
            'tx_id': 9003,
            'merchant': 'Shoppers Drug Mart',
            'date': '2026-07-12',
            'payment_method': 'debit',
            'category': 'Healthcare',
            'items': [
                ('Toothpaste 3pk', 'Healthcare', 1, 9.99, 9.99),
                ('Shampoo 900ml', 'Healthcare', 1, 7.99, 7.99),
                ('Advil 200mg 100ct', 'Healthcare', 1, 14.99, 14.99),
                ('Allergy Pills 60ct', 'Healthcare', 1, 18.99, 18.99),
                ('Body Wash', 'Healthcare', 1, 6.99, 6.99),
            ],
            'tax': 7.60,
        },
        {
            'id': 9004,
            'tx_id': 9004,
            'merchant': 'Shell',
            'date': '2026-07-15',
            'payment_method': 'credit',
            'category': 'Transportation',
            'items': [
                ('Regular Gas 45L', 'Transportation', 1, 62.55, 62.55),
                ('Car Wash', 'Transportation', 1, 14.99, 14.99),
                ('Energy Drink', 'Dining Out', 1, 3.49, 3.49),
                ('Bag of Chips', 'Dining Out', 1, 2.99, 2.99),
            ],
            'tax': 10.40,
        },
        {
            'id': 9005,
            'tx_id': 9005,
            'merchant': 'Starbucks',
            'date': '2026-07-06',
            'payment_method': 'credit',
            'category': 'Dining Out',
            'items': [
                ('Grande Latte', 'Dining Out', 1, 5.65, 5.65),
                ('Blueberry Muffin', 'Dining Out', 1, 3.45, 3.45),
                ('Breakfast Sandwich', 'Dining Out', 1, 6.75, 6.75),
                ('Cold Brew Coffee', 'Dining Out', 1, 4.95, 4.95),
            ],
            'tax': 2.76,
        },
        {
            'id': 9006,
            'tx_id': 9006,
            'merchant': 'FreshCo',
            'date': '2026-07-20',
            'payment_method': 'debit',
            'category': 'Groceries',
            'items': [
                ('Skim Milk 2L', 'Groceries', 1, 3.99, 3.99),
                ('Ground Coffee 454g', 'Groceries', 1, 10.99, 10.99),
                ('Rice 2kg', 'Groceries', 1, 6.99, 6.99),
                ('Bell Peppers 3pk', 'Groceries', 1, 4.99, 4.99),
                ('Ground Beef 500g', 'Groceries', 1, 9.99, 9.99),
                ('Pasta 900g', 'Groceries', 2, 2.49, 4.98),
            ],
            'tax': 0.00,
        },
        {
            'id': 9007,
            'tx_id': 9007,
            'merchant': 'Canadian Tire',
            'date': '2026-07-03',
            'payment_method': 'credit',
            'category': 'Transportation',
            'items': [
                ('Snow Brush', 'Transportation', 1, 19.99, 19.99),
                ('5W-30 Motor Oil 5L', 'Transportation', 1, 34.99, 34.99),
                ('Wiper Blades', 'Transportation', 2, 18.99, 37.98),
                ('Air Freshener', 'Transportation', 1, 4.99, 4.99),
            ],
            'tax': 12.40,
        },
        {
            'id': 9008,
            'tx_id': 9008,
            'merchant': 'McDonalds',
            'date': '2026-07-10',
            'payment_method': 'debit',
            'category': 'Dining Out',
            'items': [
                ('Big Mac Combo', 'Dining Out', 1, 11.99, 11.99),
                ('6pc McNuggets', 'Dining Out', 1, 7.99, 7.99),
                ('Large Coffee', 'Dining Out', 1, 2.29, 2.29),
                ('Sundae', 'Dining Out', 1, 3.49, 3.49),
            ],
            'tax': 3.52,
        },
    ]
    
    for r in receipt_data:
        subtotal = sum(item[4] for item in r['items'])
        total = round(subtotal + r['tax'], 2)
        account_id = 2 if r['payment_method'] == 'credit' else 1
        cat_id = cat_ids[r['category']]
        
        # Insert transaction
        cursor.execute("""
            INSERT INTO transactions (id, account_id, category_id, transaction_date, description, merchant, amount, type, payment_method)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'expense', ?)
        """, (r['tx_id'], account_id, cat_id, r['date'], r['category'], r['merchant'], total, r['payment_method']))
        
        # Insert receipt
        cursor.execute("""
            INSERT INTO receipts (id, transaction_id, merchant, transaction_date, subtotal, tax, total, payment_method)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (r['id'], r['tx_id'], r['merchant'], r['date'], subtotal, r['tax'], total, r['payment_method']))
        
        # Insert line items
        for item in r['items']:
            item_name, item_category, qty, unit_price, line_total = item
            item_cat_id = cat_ids.get(item_category, cat_id)
            cursor.execute("""
                INSERT INTO receipt_items (receipt_id, name, category_id, quantity, unit_price, line_total)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (r['id'], item_name, item_cat_id, qty, unit_price, line_total))


def seed_affordability(cursor):
    # Calculate current monthly income and expenses for what-if scenarios
    # Calculate current monthly income and expenses for what-if scenarios
    current_income = 6400.00  # 2 paychecks
    current_expenses = 3847.00  # Rough avg
    disposable = current_income - current_expenses
    
    # Scenario 1: New Car ($45k, 48mo, 6.9% APR, $5k down)
    car_price = 45000.00
    down = 5000.00
    financed = car_price - down
    apr = 6.9
    months = 48
    monthly_rate = apr / 100 / 12
    monthly_payment = financed * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
    
    extra_monthly = 180.00 + 120.00 + 85.00  # insurance, gas increase, maintenance
    total_new_monthly = monthly_payment + extra_monthly
    new_disposable = disposable - total_new_monthly
    
    verdict = "Technically affordable but tight. You would have $" + str(round(new_disposable, 2)) + " left each month after all expenses."
    recommendation = "Consider a cheaper vehicle or larger down payment. Ensure your emergency fund stays above 3 months expenses ($11,500+)."
    is_safe = 1 if new_disposable > 500 else 0
    
    cursor.execute("""
        INSERT INTO affordability_checks 
        (name, total_cost, down_payment, financing_amount, apr, term_months, monthly_payment, extra_monthly_cost,
         current_income, current_expenses, disposable_income, post_purchase_cash, verdict, recommendation, is_safe)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'New Car - Honda Accord Sport',
        car_price, down, financed, apr, months, round(monthly_payment, 2), extra_monthly,
        current_income, current_expenses, disposable,
        new_disposable, verdict, recommendation, is_safe
    ))
    
    check_id = cursor.lastrowid
    
    # What-if expenses for the car
    what_if = [
        (check_id, 'Car Insurance (full coverage)', 180.00, 'monthly', 'Required for financed vehicle'),
        (check_id, 'Extra Gas', 120.00, 'monthly', 'Commute increase from bus to car'),
        (check_id, 'Maintenance/Oil', 85.00, 'monthly', 'Averaged annual maintenance'),
        (check_id, 'Parking', 75.00, 'monthly', 'Downtown work parking'),
    ]
    cursor.executemany("""
        INSERT INTO what_if_expenses (affordability_check_id, name, amount, frequency, description)
        VALUES (?, ?, ?, ?, ?)
    """, what_if)
    
    # Scenario 2: New Shoes ($80)
    cursor.execute("""
        INSERT INTO affordability_checks 
        (name, total_cost, down_payment, financing_amount, apr, term_months, monthly_payment, extra_monthly_cost,
         current_income, current_expenses, disposable_income, post_purchase_cash, verdict, recommendation, is_safe)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'New Running Shoes',
        80.00, 80.00, 0.00, 0.00, 0, 0.00, 0.00,
        current_income, current_expenses, disposable,
        disposable - 80.00,
        'Yes, easily affordable.',
        'Go for it! This is a small discretionary purchase.',
        1
    ))
    
    # Scenario 3: New Laptop ($1800, 12mo 0% financing)
    cursor.execute("""
        INSERT INTO affordability_checks 
        (name, total_cost, down_payment, financing_amount, apr, term_months, monthly_payment, extra_monthly_cost,
         current_income, current_expenses, disposable_income, post_purchase_cash, verdict, recommendation, is_safe)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'New MacBook Air',
        1800.00, 0.00, 1800.00, 0.00, 12, 150.00, 0.00,
        current_income, current_expenses, disposable,
        disposable - 150.00,
        'Yes, affordable with 0% financing. Monthly payment fits comfortably in budget.',
        'Use the 0% financing but set up auto-pay so you never miss a payment.',
        1
    ))

def generate_transactions(cursor):
    merchants = {
        'Groceries': [('FreshCo', 'debit'), ('Walmart Supercentre', 'debit'), ('No Frills', 'debit'), ('Farm Boy', 'debit')],
        'Dining Out': [('McDonalds', 'debit'), ('Tim Hortons', 'debit'), ('Subway', 'debit'), ('Wendys', 'debit'), 
                       ('Mandarin Restaurant', 'credit'), ('Swiss Chalet', 'credit'), ('Starbucks', 'credit')],
        'Shopping': [('Amazon.ca', 'credit'), ('Amazon.ca', 'credit'), ('Amazon.ca', 'credit'), 
                     ('Walmart', 'debit'), ('Canadian Tire', 'credit'), ('Shoppers Drug Mart', 'debit')],
        'Transportation': [('Shell', 'credit'), ('Petro-Canada', 'credit'), ('Esso', 'credit'),
                           ('Uber', 'credit'), ('Go Transit', 'debit')],
        'Entertainment': [('Cineplex', 'credit'), ('Steam', 'credit'), ('Xbox Live', 'credit')],
        'Subscriptions': [('Netflix', 'credit'), ('Spotify', 'credit'), ('Disney+', 'credit'), ('Crave', 'credit')],
        'Healthcare': [('Shoppers Drug Mart', 'debit'), ('Rexall', 'debit'), ('London Drugs', 'debit')],
    }
    
    cat_ids = {
        'Income': 1, 'Rent': 2, 'Utilities': 3, 'Groceries': 4,
        'Transportation': 5, 'Subscriptions': 6, 'Entertainment': 7,
        'Dining Out': 8, 'Shopping': 9, 'Healthcare': 10, 'Savings': 11
    }
    
    tx_id = 1
    start_date = datetime(2026, 1, 1).date()
    months = []
    for m in range(7):
        month_date = datetime(2026, 1 + m, 1).date()
        months.append(month_date)
    
    for month_start in months:
        
        # Biweekly paychecks
        payday = month_start.replace(day=7)
        if payday.weekday() >= 5:
            payday += timedelta(days=7 - payday.weekday())
        
        for _ in range(2):
            cursor.execute("""
                INSERT INTO transactions (id, account_id, category_id, transaction_date, description, merchant, amount, type, payment_method)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'income', 'direct_deposit')
            """, (tx_id, 1, cat_ids['Income'], payday.strftime('%Y-%m-%d'), 'Paycheck', 'Employer Inc.', 3200.00))
            tx_id += 1
            payday += timedelta(days=14)
        
        # Rent
        rent_date = month_start.replace(day=1)
        cursor.execute("""
            INSERT INTO transactions (id, account_id, category_id, transaction_date, description, merchant, amount, type, payment_method)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'expense', 'transfer')
        """, (tx_id, 1, cat_ids['Rent'], rent_date.strftime('%Y-%m-%d'), 'Rent Payment', 'Landlord', 1450.00))
        tx_id += 1
        
        # Random expenses
        for cat_name, merchant_list in merchants.items():
            num_purchases = random.randint(1, 4)
            for _ in range(num_purchases):
                day = random.randint(1, 28)
                tx_date = month_start.replace(day=day)
                merchant, method = random.choice(merchant_list)
                
                if cat_name == 'Groceries':
                    amount = round(random.uniform(35.00, 180.00), 2)
                elif cat_name == 'Dining Out':
                    amount = round(random.uniform(8.50, 65.00), 2)
                elif cat_name == 'Shopping':
                    amount = round(random.uniform(15.00, 120.00), 2)
                elif cat_name == 'Transportation':
                    amount = round(random.uniform(25.00, 80.00), 2)
                elif cat_name == 'Entertainment':
                    amount = round(random.uniform(15.00, 45.00), 2)
                elif cat_name == 'Subscriptions':
                    amount = round(random.uniform(10.00, 20.00), 2)
                elif cat_name == 'Healthcare':
                    amount = round(random.uniform(12.00, 55.00), 2)
                else:
                    amount = round(random.uniform(10.00, 50.00), 2)
                
                account_id = 2 if method == 'credit' else 1
                cursor.execute("""
                    INSERT INTO transactions (id, account_id, category_id, transaction_date, description, merchant, amount, type, payment_method)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'expense', ?)
                """, (tx_id, account_id, cat_ids[cat_name], tx_date.strftime('%Y-%m-%d'), cat_name, merchant, amount, method))
                tx_id += 1
        
        # Cash withdrawals
        for _ in range(random.randint(2, 3)):
            day = random.randint(1, 28)
            tx_date = month_start.replace(day=day)
            amount = random.choice([40.00, 60.00, 80.00, 100.00, 120.00])
            cursor.execute("""
                INSERT INTO transactions (id, account_id, category_id, transaction_date, description, merchant, amount, type, payment_method)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'expense', 'cash')
            """, (tx_id, 1, 12, tx_date.strftime('%Y-%m-%d'), 'ATM Withdrawal', 'TD Bank ATM', amount))
            tx_id += 1
        
        # Monthly savings transfer
        savings_day = random.randint(25, 28)
        savings_date = month_start.replace(day=savings_day)
        cursor.execute("""
            INSERT INTO transactions (id, account_id, category_id, transaction_date, description, merchant, amount, type, payment_method)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'expense', 'transfer')
        """, (tx_id, 1, cat_ids['Savings'], savings_date.strftime('%Y-%m-%d'), 'Monthly Savings Transfer', 'Savings', 500.00))
        tx_id += 1
        
        # Utilities
        utilities = [
            (cat_ids['Utilities'], 'Hydro Bill', 'Hydro One', round(random.uniform(75.00, 120.00), 2)),
            (cat_ids['Utilities'], 'Internet Bill', 'Bell Fibe', 89.99),
            (cat_ids['Utilities'], 'Phone Bill', 'Koodo', 55.00),
        ]
        for util in utilities:
            day = random.randint(8, 15)
            tx_date = month_start.replace(day=day)
            cursor.execute("""
                INSERT INTO transactions (id, account_id, category_id, transaction_date, description, merchant, amount, type, payment_method)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'expense', ?)
            """, (tx_id, 1, util[0], tx_date.strftime('%Y-%m-%d'), util[1], util[2], util[3], 'debit'))
            tx_id += 1
        
        # Car payment
        if month_start < datetime(2028, 5, 5).date():
            cursor.execute("""
                INSERT INTO transactions (id, account_id, category_id, transaction_date, description, merchant, amount, type, payment_method)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'expense', 'transfer')
            """, (tx_id, 1, cat_ids['Transportation'], month_start.replace(day=5).strftime('%Y-%m-%d'), 'Car Payment', 'Honda Finance', 385.00))
            tx_id += 1

def update_balances(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE -amount END), 0) 
        FROM transactions WHERE account_id = 1
    """)
    checking_balance = cursor.fetchone()[0] + 3250.00
    
    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE account_id = 2 AND type = 'expense'
    """)
    cc_balance = -cursor.fetchone()[0]
    
    cursor.execute("UPDATE accounts SET current_balance = ? WHERE id = 1", (checking_balance,))
    cursor.execute("UPDATE accounts SET current_balance = ? WHERE id = 2", (cc_balance,))
    conn.commit()

def verify_counts(cursor):
    cursor.execute("SELECT COUNT(*) FROM transactions")
    tx_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM recurring_items")
    rec_count = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'income'")
    total_income = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'expense'")
    total_expense = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM affordability_checks")
    afford_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM receipts")
    receipt_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM receipt_items")
    item_count = cursor.fetchone()[0]
    
    print(f"HAL Budget seeded successfully!")
    print(f"  Transactions: {tx_count}")
    print(f"  Recurring items: {rec_count}")
    print(f"  Affordability checks: {afford_count}")
    print(f"  Itemized receipts: {receipt_count}")
    print(f"  Receipt line items: {item_count}")
    print(f"  Total income (6mo): ${total_income:,.2f}")
    print(f"  Total expenses (6mo): ${total_expense:,.2f}")
    print(f"  Net: ${total_income - total_expense:,.2f}")

def main():
    conn = connect()
    reset_db(conn)
    cursor = conn.cursor()
    
    seed_accounts(cursor)
    seed_categories(cursor)
    seed_recurring(cursor)
    seed_savings_goals(cursor)
    seed_budgets(cursor)
    generate_transactions(cursor)
    seed_receipts(cursor)
    seed_affordability(cursor)
    
    conn.commit()
    verify_counts(cursor)
    
    # Show affordability scenarios
    print("\n--- Affordability Scenarios ---")
    cursor.execute("SELECT name, total_cost, monthly_payment, verdict, is_safe FROM affordability_checks")
    for row in cursor.fetchall():
        safe_icon = "OK" if row[4] else "NO"
        print(f"  [{safe_icon}] {row[0]}: ${row[1]:,.2f} | Monthly: ${row[2]:,.2f} | {row[3]}")
    
    conn.close()

if __name__ == '__main__':
    main()
