#!/usr/bin/env python3
"""
HAL Receipt Scanner
Mock-first receipt parser with optional Tesseract OCR
"""

import json
import re
from datetime import datetime, date
from pathlib import Path

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

# ---- MOCK RECEIPT DATABASE ----
# Realistic receipts for demo purposes
MOCK_RECEIPTS = {
    "walmart": {
        "merchant": "Walmart Supercentre",
        "date": "2026-07-20",
        "items": [
            {"name": "Milk 4L", "category": "Groceries", "quantity": 1, "unit_price": 4.89, "line_total": 4.89},
            {"name": "Bread", "category": "Groceries", "quantity": 1, "unit_price": 2.99, "line_total": 2.99},
            {"name": "Eggs (dozen)", "category": "Groceries", "quantity": 1, "unit_price": 3.79, "line_total": 3.79},
            {"name": "Ground Beef", "category": "Groceries", "quantity": 1, "unit_price": 12.49, "line_total": 12.49},
            {"name": "Toilet Paper (12pk)", "category": "Groceries", "quantity": 1, "unit_price": 6.99, "line_total": 6.99},
            {"name": "Laundry Detergent", "category": "Groceries", "quantity": 1, "unit_price": 8.97, "line_total": 8.97},
            {"name": "Bananas", "category": "Groceries", "quantity": 1, "unit_price": 1.79, "line_total": 1.79},
            {"name": "Frozen Pizza", "category": "Groceries", "quantity": 1, "unit_price": 5.49, "line_total": 5.49}
        ],
        "tax": 5.89,
        "total": 52.29,
        "payment_method": "debit",
        "category": "Groceries"
    },
    "shell": {
        "merchant": "Shell Canada",
        "date": "2026-07-19",
        "items": [
            {"name": "Regular Unleaded", "category": "Transportation", "quantity": 1, "unit_price": 58.45, "line_total": 58.45}
        ],
        "tax": 7.60,
        "total": 66.05,
        "payment_method": "credit",
        "category": "Transportation"
    },
    "timhortons": {
        "merchant": "Tim Hortons",
        "date": "2026-07-21",
        "items": [
            {"name": "Large Double-Double", "category": "Dining Out", "quantity": 1, "unit_price": 2.15, "line_total": 2.15},
            {"name": "Breakfast Sandwich", "category": "Dining Out", "quantity": 1, "unit_price": 4.99, "line_total": 4.99},
            {"name": "Donut", "category": "Dining Out", "quantity": 1, "unit_price": 1.29, "line_total": 1.29}
        ],
        "tax": 0.82,
        "total": 9.25,
        "payment_method": "debit",
        "category": "Dining Out"
    },
    "canadiantire": {
        "merchant": "Canadian Tire",
        "date": "2026-07-18",
        "items": [
            {"name": "Car Oil (5L)", "category": "Transportation", "quantity": 1, "unit_price": 24.99, "line_total": 24.99},
            {"name": "Windshield Wipers", "category": "Transportation", "quantity": 1, "unit_price": 18.99, "line_total": 18.99},
            {"name": "Air Filter", "category": "Transportation", "quantity": 1, "unit_price": 14.99, "line_total": 14.99}
        ],
        "tax": 7.67,
        "total": 66.64,
        "payment_method": "credit",
        "category": "Transportation"
    },
    "shoppers": {
        "merchant": "Shoppers Drug Mart",
        "date": "2026-07-17",
        "items": [
            {"name": "Multivitamins", "category": "Healthcare", "quantity": 1, "unit_price": 12.99, "line_total": 12.99},
            {"name": "Advil (100ct)", "category": "Healthcare", "quantity": 1, "unit_price": 11.99, "line_total": 11.99},
            {"name": "Hand Sanitizer", "category": "Healthcare", "quantity": 1, "unit_price": 4.99, "line_total": 4.99}
        ],
        "tax": 3.77,
        "total": 33.74,
        "payment_method": "debit",
        "category": "Healthcare"
    },
    "mcdonalds": {
        "merchant": "McDonalds",
        "date": "2026-07-20",
        "items": [
            {"name": "Big Mac Meal", "category": "Dining Out", "quantity": 1, "unit_price": 10.99, "line_total": 10.99},
            {"name": "Medium Fries", "category": "Dining Out", "quantity": 1, "unit_price": 3.79, "line_total": 3.79},
            {"name": "Coke (Large)", "category": "Dining Out", "quantity": 1, "unit_price": 2.39, "line_total": 2.39}
        ],
        "tax": 2.23,
        "total": 16.40,
        "payment_method": "cash",
        "category": "Dining Out"
    }
}

def try_ocr(image_path):
    """Attempt real OCR with Tesseract. Returns text or None."""
    if not TESSERACT_AVAILABLE:
        return None
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        print(f"OCR failed: {e}")
        return None

def parse_mock_receipt(receipt_type):
    """Return a mock receipt by type (walmart, shell, etc.) or random if unknown."""
    if receipt_type in MOCK_RECEIPTS:
        return MOCK_RECEIPTS[receipt_type].copy()
    
    # Return random receipt for demo
    import random
    key = random.choice(list(MOCK_RECEIPTS.keys()))
    return MOCK_RECEIPTS[key].copy()

def parse_receipt_image(image_path):
    """
    Main entry point: Try OCR first, fallback to mock
    
    Returns dict with:
    - source: 'ocr' or 'mock'
    - merchant
    - date
    - items: [{desc, price}, ...]
    - tax
    - total
    - payment_method
    - category
    - confidence: 0-1 (OCR confidence or mock flag)
    """
    # Try real OCR
    ocr_text = try_ocr(image_path)
    
    if ocr_text:
        # Parse OCR text (basic extraction)
        return parse_ocr_text(ocr_text)
    
    # Fallback: determine mock type from filename
    path_lower = str(image_path).lower()
    for key in MOCK_RECEIPTS:
        if key in path_lower:
            result = parse_mock_receipt(key)
            result["source"] = "mock"
            result["confidence"] = 0.0
            result["note"] = "Tesseract OCR not available. This is a realistic mock receipt for demonstration."
            return result
    
    # Random fallback
    result = parse_mock_receipt("random")
    result["source"] = "mock"
    result["confidence"] = 0.0
    result["note"] = "Tesseract OCR not available. This is a realistic mock receipt for demonstration."
    return result

def parse_ocr_text(text):
    """Basic OCR text parser - extracts merchant, total, date from OCR output."""
    lines = text.strip().split('\n')
    
    result = {
        "source": "ocr",
        "merchant": "Unknown Merchant",
        "date": date.today().isoformat(),
        "items": [],
        "tax": 0.0,
        "total": 0.0,
        "payment_method": "unknown",
        "category": "Unknown",
        "confidence": 0.5,
        "raw_text": text[:500]  # First 500 chars for debugging
    }
    
    # Try to find total
    total_patterns = [
        r'TOTAL[\s:]*[$]?([\d,]+\.\d{2})',
        r'AMOUNT[\s:]*[$]?([\d,]+\.\d{2})',
        r'Balance[\s:]*[$]?([\d,]+\.\d{2})'
    ]
    for pattern in total_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result["total"] = float(match.group(1).replace(',', ''))
            break
    
    # Try to find merchant (first non-empty line)
    for line in lines:
        line = line.strip()
        if line and len(line) > 3:
            result["merchant"] = line
            break
    
    # Try to find date
    date_patterns = [
        r'(\d{4}-\d{2}-\d{2})',
        r'(\d{2}/\d{2}/\d{4})',
        r'(\d{2}-\d{2}-\d{4})'
    ]
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                result["date"] = match.group(1)
            except:
                pass
            break
    
    return result

def format_receipt_for_display(receipt):
    """Pretty print a receipt for UI display."""
    lines = [
        f"📄 **{receipt['merchant']}**",
        f"📅 Date: {receipt['date']}",
        "",
        "**Items:**"
    ]
    
    for item in receipt.get('items', []):
        name = item.get('name') or item.get('desc', 'Item')
        price = item.get('line_total') or item.get('price', 0)
        lines.append(f"  • {name}: ${price:.2f}")
    
    lines.extend([
        "",
        f"**Tax:** ${receipt.get('tax', 0):.2f}",
        f"**Total:** ${receipt['total']:.2f}",
        f"**Payment:** {receipt.get('payment_method', 'unknown')}",
        f"**Category:** {receipt.get('category', 'Unknown')}"
    ])
    
    if receipt.get('note'):
        lines.extend(["", f"*{receipt['note']}*"])
    
    return "\n".join(lines)

def receipt_to_transaction(receipt, account_id=1):
    """Convert parsed receipt to transaction dict for DB insertion."""
    return {
        "account_id": account_id,
        "transaction_date": receipt["date"],
        "description": f"Receipt: {receipt['merchant']}",
        "merchant": receipt["merchant"],
        "amount": receipt["total"],
        "type": "expense",
        "payment_method": receipt.get("payment_method", "debit")
    }

def save_receipt_to_db(receipt, db_path='hal_budget.db'):
    """
    Save a parsed receipt as a transaction + receipt + line items.
    Returns the transaction_id.
    """
    import sqlite3
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Determine category id
    cursor.execute("SELECT id FROM categories WHERE name = ?", (receipt['category'],))
    row = cursor.fetchone()
    category_id = row[0] if row else None
    
    # Determine account id from payment method
    method = receipt.get('payment_method', 'debit')
    account_id = 2 if method == 'credit' else 1
    
    # Insert transaction
    cursor.execute("""
        INSERT INTO transactions (account_id, category_id, transaction_date, description, merchant, amount, type, payment_method)
        VALUES (?, ?, ?, ?, ?, ?, 'expense', ?)
    """, (account_id, category_id, receipt['date'], receipt['category'], receipt['merchant'], receipt['total'], method))
    transaction_id = cursor.lastrowid
    
    # Calculate subtotal
    subtotal = sum(item.get('line_total', item.get('price', 0)) for item in receipt['items'])
    
    # Insert receipt
    cursor.execute("""
        INSERT INTO receipts (transaction_id, merchant, transaction_date, subtotal, tax, total, payment_method)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (transaction_id, receipt['merchant'], receipt['date'], subtotal, receipt.get('tax', 0), receipt['total'], method))
    receipt_id = cursor.lastrowid
    
    # Insert line items
    for item in receipt['items']:
        item_name = item.get('name') or item.get('desc', 'Item')
        item_category = item.get('category', receipt['category'])
        cursor.execute("SELECT id FROM categories WHERE name = ?", (item_category,))
        row = cursor.fetchone()
        item_cat_id = row[0] if row else category_id
        
        quantity = item.get('quantity', 1)
        unit_price = item.get('unit_price', item.get('price', 0))
        line_total = item.get('line_total', round(quantity * unit_price, 2))
        
        cursor.execute("""
            INSERT INTO receipt_items (receipt_id, name, category_id, quantity, unit_price, line_total)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (receipt_id, item_name, item_cat_id, quantity, unit_price, line_total))
    
    conn.commit()
    conn.close()
    return transaction_id

def list_available_mocks():
    """Return list of mock receipt types for demo dropdown."""
    return list(MOCK_RECEIPTS.keys())

# ---- DEMO ----
if __name__ == '__main__':
    print("HAL Receipt Scanner Demo")
    print("=" * 50)
    
    for key in MOCK_RECEIPTS:
        receipt = parse_mock_receipt(key)
        print(f"\n{format_receipt_for_display(receipt)}")
        print("-" * 40)
    
    print("\nOCR Status:", "Available" if TESSERACT_AVAILABLE else "Not installed (mock mode)")
    print("Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki")
    print("Then: pip install pytesseract Pillow")
