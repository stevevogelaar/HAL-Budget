import streamlit as st
import sqlite3
import pandas as pd
import requests
import subprocess
import seed_data
from datetime import datetime
from budget_engine import BudgetEngine
from llm_sql_engine import DEFAULT_MODEL, ollama_available
from receipt_scanner import list_available_mocks, parse_mock_receipt, format_receipt_for_display, save_receipt_to_db

# Page config
st.set_page_config(
    page_title="HAL Budget",
    page_icon="Hal-Budget-Logo.png",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS — uses Streamlit theme variables so it adapts to light/dark mode
st.markdown("""
<style>
    :root {
        --hal-primary: #22c55e;
        --hal-bg: #0f172a;
        --hal-card: #1e293b;
        --hal-text: #f8fafc;
    }
    @media (prefers-color-scheme: light) {
        :root {
            --hal-bg: #f8fafc;
            --hal-card: #ffffff;
            --hal-text: #0f172a;
        }
    }
    .stApp { background-color: var(--hal-bg); color: var(--hal-text); }
    .main { background-color: var(--hal-bg); color: var(--hal-text); }
    .stTextInput > div > div > input {
        background-color: var(--hal-card);
        color: var(--hal-text);
        border: 1px solid rgba(128, 128, 128, 0.3);
        border-radius: 8px; padding: 12px; font-size: 16px;
    }
    div.stButton > button[kind="primary"],
    div.stButton > button[kind="secondary"] {
        background-color: var(--hal-primary) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
    }
    div.stButton > button[kind="primary"]:hover,
    div.stButton > button[kind="secondary"]:hover { filter: brightness(1.15) !important; }
    .answer-box {
        background-color: var(--hal-card); border-radius: 12px; padding: 20px;
        margin: 16px 0; border-left: 4px solid var(--hal-primary);
    }
    .receipt-card {
        background-color: var(--hal-card); border-radius: 12px; padding: 20px;
        margin: 12px 0; border: 1px solid rgba(128, 128, 128, 0.2);
    }
    .metric-card {
        background-color: var(--hal-card); border-radius: 8px; padding: 16px;
        text-align: center;
    }
    h1 { color: var(--hal-primary) !important; font-weight: 700 !important; }
    h2, h3 { color: var(--hal-text) !important; }
    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"] { color: var(--hal-text) !important; }
</style>
""", unsafe_allow_html=True)

def get_ollama_status(model=DEFAULT_MODEL):
    """Return (is_ready, message). Message is None when Ollama and the model are ready."""
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=4)
        if r.status_code != 200:
            return False, f"Ollama returned status {r.status_code}."
        models = [m.get("name", "") for m in r.json().get("models", [])]
        if model in models or model.split(":")[0] in {m.split(":")[0] for m in models}:
            return True, None
        return False, f"Model '{model}' is not downloaded. Available: {', '.join(models) or 'none'}."
    except Exception as e:
        return False, f"Could not reach Ollama: {e}"

# Initialize
if 'engine' not in st.session_state:
    st.session_state.engine = BudgetEngine()
    st.session_state.history = []
    st.session_state.scanned_receipt = None
    st.session_state.receipt_save_msg = None

engine = st.session_state.engine

# Header
header_col1, header_col2 = st.columns([1, 4])
with header_col1:
    st.image("Hal-Budget-Logo.png", width=100)
with header_col2:
    st.markdown("# HAL Budget")
    st.markdown("### Your money. Your machine. Your answers.")
    st.markdown("*Ask about spending, bills, savings — or scan a receipt. All data stays local.*")

# Quick stats (shared across all tabs)
conn = sqlite3.connect('hal_budget.db')
cursor = conn.cursor()
# Quick stats (shared across all tabs) — LIVE from transactions, not static
cursor.execute("""
    SELECT 
        COALESCE(SUM(amount), 0) 
    FROM transactions 
    WHERE type = 'income'
""")
total_income = cursor.fetchone()[0] or 0

cursor.execute("""
    SELECT 
        COALESCE(SUM(amount), 0) 
    FROM transactions 
    WHERE type = 'expense'
""")
total_expense = cursor.fetchone()[0] or 0

# Live checking balance from view
cursor.execute("SELECT calculated_balance FROM v_account_balances WHERE type = 'checking'")
row = cursor.fetchone()
checking = row[0] if row else 0
conn.close()

cols = st.columns(3)
with cols[0]:
    st.metric("💵 Total Income", f"${total_income:,.0f}")
with cols[1]:
    st.metric("💸 Total Spent", f"${total_expense:,.0f}")
with cols[2]:
    st.metric("🏦 Checking", f"${checking:,.0f}")

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["💬 Chat", "📷 Scan Receipt", "📊 Dashboard", "📋 All Transactions", "⚙️ Settings"])

# === TAB 1: CHAT ===
with tab1:
    # Demo questions
    st.markdown("**Try asking:**")
    demo_cols = st.columns(2)
    demo_questions = [
        "How much did I spend on Amazon?",
        "When is my next rent payment?",
        "Can I afford a new car?",
        "What are my subscriptions?",
        "How much do I spend on groceries?",
        "What's my checking balance?",
        "Show me my budget vs actual",
        "How much have I saved?",
        "How much did I spend on coffee?",
        "Show me all milk purchases"
    ]
    for i, q in enumerate(demo_questions):
        with demo_cols[i % 2]:
            if st.button(q, key=f"demo_{i}", use_container_width=True):
                st.session_state.current_question = q
                st.session_state.run_demo_question = q
    
    # LLM status indicator
    llm_ready, llm_msg = get_ollama_status(st.session_state.get('selected_model', DEFAULT_MODEL))
    if llm_ready:
        st.markdown(f"""
            <div style='font-size: 12px; color: #888; margin-bottom: 8px;'>
                🧠 LLM engine online ({st.session_state.get('selected_model', DEFAULT_MODEL)})
            </div>
        """, unsafe_allow_html=True)
    else:
        st.warning(f"⚡ {llm_msg} The app will use rule-based answers. Go to **Settings** to start Ollama.")
    
    # Input
    question = st.text_input(
        "Ask about your finances:",
        value=st.session_state.get('current_question', ''),
        placeholder="e.g., 'How much did I spend on groceries this month?'"
    )
    
    # Demo button override: if user clicked a demo button, run it immediately
    if st.session_state.get('run_demo_question'):
        question = st.session_state.run_demo_question
        st.session_state.run_demo_question = None
    
    if question and question != st.session_state.get('last_question', ''):
        st.session_state.last_question = question
        model_label = st.session_state.get('selected_model', DEFAULT_MODEL)
        with st.spinner(f"{model_label} is generating SQL..."):
            answer = engine.query(question)
        st.session_state.history.insert(0, {'question': question, 'answer': answer, 'time': datetime.now().strftime('%H:%M:%S')})
    
    # History
    if st.session_state.history:
        st.markdown("---")
        for item in st.session_state.history[:5]:
            st.markdown(f"""
            <div class='answer-box'>
                <div style='color: #e94560; font-size: 11px;'>{item['time']}</div>
                <div style='font-size: 17px; font-weight: 600; margin: 8px 0;'>{item['question']}</div>
                <div style='font-size: 15px; line-height: 1.6; white-space: pre-wrap;'>{item['answer']}</div>
            </div>
            """, unsafe_allow_html=True)

# === TAB 2: RECEIPT SCANNER ===
with tab2:
    st.markdown("### 📷 Receipt Scanner")
    st.markdown("*Simulated for hackathon demo. In production: Tesseract OCR.*")
    
    # Ensure session storage for scanned receipt exists
    if 'scanned_receipt' not in st.session_state:
        st.session_state.scanned_receipt = None
    if 'receipt_save_msg' not in st.session_state:
        st.session_state.receipt_save_msg = None
    
    # Show save confirmation from a previous run
    if st.session_state.receipt_save_msg:
        st.success(st.session_state.receipt_save_msg)
        st.session_state.receipt_save_msg = None
    
    mock_types = list_available_mocks()
    selected = st.selectbox("Select a receipt to scan:", mock_types)
    
    if st.button("Scan Receipt", type="primary"):
        with st.spinner("Processing receipt..."):
            st.session_state.scanned_receipt = parse_mock_receipt(selected)
    
    receipt = st.session_state.scanned_receipt
    if receipt:
        st.markdown("---")
        st.markdown("**🧾 Extracted Receipt:**")
        st.markdown(format_receipt_for_display(receipt))
        
        st.markdown("---")
        st.markdown("**What would you like to do?**")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save to Transactions", key="save_receipt"):
                tx_id = save_receipt_to_db(receipt)
                st.session_state.scanned_receipt = None
                st.session_state.receipt_save_msg = f"Saved: {receipt['merchant']} - ${receipt['total']:.2f} (with {len(receipt.get('items', []))} line items)"
                st.rerun()  # Refresh stats bar at top
        with col2:
            if st.button("❌ Cancel"):
                st.session_state.scanned_receipt = None
                st.info("Receipt discarded.")

# === TAB 3: DASHBOARD ===
with tab3:
    st.markdown("### 📊 Financial Dashboard")
    
    conn = sqlite3.connect('hal_budget.db')
    
    # Monthly trend
    st.markdown("**Monthly Cash Flow**")
    df_monthly = pd.read_sql("SELECT * FROM v_monthly_summary", conn)
    if not df_monthly.empty:
        st.line_chart(df_monthly.set_index('year_month')[['total_income', 'total_expenses']])
    
    # Upcoming bills
    st.markdown("**Upcoming Bills**")
    df_upcoming = pd.read_sql("SELECT name, amount, next_due_date FROM v_upcoming_recurring LIMIT 5", conn)
    if not df_upcoming.empty:
        st.dataframe(df_upcoming, use_container_width=True, hide_index=True)
    
    # Savings goals
    st.markdown("**Savings Goals**")
    df_goals = pd.read_sql("SELECT name, target_amount, current_amount FROM savings_goals WHERE is_active = 1", conn)
    if not df_goals.empty:
        for _, row in df_goals.iterrows():
            pct = (row['current_amount'] / row['target_amount'] * 100) if row['target_amount'] else 0
            st.progress(min(pct / 100, 1.0), text=f"{row['name']}: ${row['current_amount']:.0f} / ${row['target_amount']:.0f} ({pct:.0f}%)")
    
    # Top merchants
    st.markdown("**Top Spending by Merchant (All Time)**")
    df_merchants = pd.read_sql("""
        SELECT merchant, SUM(amount) as total FROM transactions 
        WHERE type = 'expense' AND merchant IS NOT NULL AND merchant != ''
        GROUP BY merchant ORDER BY total DESC LIMIT 8
    """, conn)
    if not df_merchants.empty:
        st.bar_chart(df_merchants.set_index('merchant'))
    
    conn.close()

# === TAB 4: ALL TRANSACTIONS ===
with tab4:
    st.markdown("### 📋 All Transactions")
    st.markdown("*Filterable, sortable, and searchable transaction history.*")
    
    conn = sqlite3.connect('hal_budget.db')
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    # Date range
    with col1:
        cursor = conn.cursor()
        cursor.execute("SELECT MIN(transaction_date), MAX(transaction_date) FROM transactions")
        min_date, max_date = cursor.fetchone()
        cursor.close()
        
        date_from = st.date_input("From", value=datetime.strptime(min_date, '%Y-%m-%d') if min_date else datetime.now())
        date_to = st.date_input("To", value=datetime.strptime(max_date, '%Y-%m-%d') if max_date else datetime.now())
    
    # Category filter
    with col2:
        df_cats = pd.read_sql("SELECT DISTINCT name FROM categories ORDER BY name", conn)
        categories = ['All'] + df_cats['name'].tolist()
        selected_category = st.selectbox("Category", categories)
    
    # Type filter
    with col3:
        selected_type = st.selectbox("Type", ['All', 'income', 'expense', 'transfer'])
    
    # Search
    search = st.text_input("Search merchant or description:", placeholder="e.g., Amazon, Walmart, rent...")
    
    # Build query
    query = """
        SELECT 
            t.id,
            t.transaction_date AS Date,
            t.merchant AS Merchant,
            t.description AS Description,
            c.name AS Category,
            t.amount AS Amount,
            t.type AS Type,
            t.payment_method AS Method
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.transaction_date BETWEEN ? AND ?
    """
    params = [date_from.strftime('%Y-%m-%d'), date_to.strftime('%Y-%m-%d')]
    
    if selected_category != 'All':
        query += " AND c.name = ?"
        params.append(selected_category)
    
    if selected_type != 'All':
        query += " AND t.type = ?"
        params.append(selected_type)
    
    if search:
        query += " AND (t.merchant LIKE ? OR t.description LIKE ?)"
        params.append(f'%{search}%')
        params.append(f'%{search}%')
    
    query += " ORDER BY t.transaction_date DESC"
    
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    
    if not df.empty:
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Amount": st.column_config.NumberColumn(format="$%.2f"),
                "Date": st.column_config.DateColumn()
            }
        )
        st.markdown(f"**{len(df)} transactions** | Total: ${df['Amount'].sum():,.2f}")
    else:
        st.info("No transactions match your filters.")

# === TAB 5: SETTINGS ===
with tab5:
    st.markdown("### ⚙️ Settings")
    
    # ---- Ollama status & restart ----
    st.markdown("#### 🧠 Local AI Status")
    current_model = st.session_state.get('selected_model', DEFAULT_MODEL)
    ollama_ok, ollama_msg = get_ollama_status(current_model)
    
    if ollama_ok:
        st.success(f"Ollama is running and model '{current_model}' is ready.")
    else:
        st.error(f"Ollama issue: {ollama_msg}")
        st.markdown("""
        **What this means:** The smart AI answers are turned off right now. The app still works
        using its built-in rule engine, but it won't understand complex or unusual questions.
        
        **To fix it:** click the button below. A PowerShell window will open and start Ollama.
        Wait about 10–20 seconds, then come back here and refresh the page.
        """)
        if st.button("Open PowerShell & start Ollama", type="primary"):
            try:
                subprocess.Popen(
                    ["powershell", "-NoExit", "-Command", "ollama serve"],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
                st.info("PowerShell window opened. Wait a few seconds, then refresh this page.")
            except Exception as e:
                st.error(f"Could not open PowerShell: {e}")
    
    st.markdown("---")
    
    # ---- Model chooser ----
    st.markdown("#### Model")
    st.markdown("Choose which local Ollama model powers the natural-language SQL engine.")
    
    available_models = []
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=5)
        if r.status_code == 200:
            available_models = [m.get("name") for m in r.json().get("models", [])]
        else:
            st.warning(f"Ollama returned status {r.status_code}.")
    except Exception as e:
        st.warning(f"Could not reach Ollama: {e}")
    
    if not available_models:
        available_models = [DEFAULT_MODEL]
    
    selected = st.selectbox("Local LLM model", available_models, index=available_models.index(current_model) if current_model in available_models else 0)
    
    if selected != current_model:
        st.session_state.selected_model = selected
        # Rebuild engine with new model
        st.session_state.engine = BudgetEngine(model=selected)
        st.success(f"Switched to {selected}. The previous SQL cache was cleared so the new model generates fresh queries.")
    
    st.markdown("**Model guidance**")
    st.markdown(f"""
    - **{DEFAULT_MODEL}** (default): best SQL accuracy, slower on first-time questions.
    - **qwen2.5-coder:1.5b**: faster SQL generation, slightly less robust.
    - **tinyllama**: very fast, may struggle with complex questions.
    """)
    
    st.markdown("---")
    
    # ---- Demo-only reset data ----
    st.markdown("#### 🔄 Reset Demo Data")
    st.markdown("*Demo feature only — not part of a real app.*")
    st.markdown("If the database gets too full from testing, reset it back to the original fake demo data.")
    
    if st.button("Reset demo data now", type="secondary"):
        with st.spinner("Resetting database..."):
            try:
                # Clear cached SQL so the new database doesn't reuse stale queries
                if 'engine' in st.session_state:
                    st.session_state.engine.llm_engine.clear_cache()
                # Re-seed from scratch
                seed_data.main()
                # Reset app state
                st.session_state.engine = BudgetEngine(model=st.session_state.get('selected_model', DEFAULT_MODEL))
                st.session_state.history = []
                st.session_state.scanned_receipt = None
                st.session_state.receipt_save_msg = None
                st.session_state.last_question = ""
                st.session_state.current_question = ""
                st.success("Demo data reset. Refreshing...")
                st.rerun()
            except Exception as e:
                st.error(f"Could not reset demo data: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 12px;'>
    🔒 All data stored locally in SQLite. No cloud. No API keys.
    <br>
    Built with Streamlit + Python + Local LLM — Edge/On-Device — GDG Windsor Hackathon 2026
</div>
""", unsafe_allow_html=True)
