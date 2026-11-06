import streamlit as st
import pandas as pd
import plotly.express as px
from modules.db_handler import init_db, add_transaction, get_all_transactions
from modules.categorizer import categorize_transaction
from modules.parser import parse_bank_statement, parse_sms

init_db()

st.set_page_config(page_title="Smart UPI Tracker", page_icon="💳", layout="centered")

st.markdown("""
    <style>
    .stApp { max-width: 480px; margin: 0 auto; }
    </style>
""", unsafe_allow_html=True)

st.title("💳 Smart UPI Tracker")

tab1, tab2, tab3 = st.tabs(["📥 Add & SMS", "📊 Dashboard", "📤 Statement"])

with tab1:
    st.subheader("Automatic SMS Parsing")
    sms_input = st.text_area("Paste Bank SMS Here:")
    if st.button("Parse & Save SMS"):
        if sms_input:
            data = parse_sms(sms_input)
            cat = categorize_transaction(data['Description'])
            add_transaction(data['Date'], data['Description'], data['Amount'], data['Type'], cat)
            st.success(f"Saved under category: {cat}")

    st.markdown("---")
    st.subheader("Manual Entry")
    with st.form("manual"):
        m_amt = st.number_input("Amount (₹)", min_value=1.0)
        m_desc = st.text_input("Paid To / Merchant")
        m_cat = st.selectbox("Category", ["Food", "Shopping", "Travel", "Bills", "Healthcare", "Entertainment", "Personal / Other"])
        m_note = st.text_input("Optional Note (+)")
        if st.form_submit_button("Save Transaction"):
            add_transaction(pd.Timestamp.now().strftime("%Y-%m-%d"), m_desc, m_amt, "Expense", m_cat, m_note)
            st.success("Transaction saved successfully!")

with tab2:
    st.subheader("Monthly Dashboard")
    df = get_all_transactions()
    if not df.empty:
        total = df['Amount'].sum()
        st.metric("Total Expenses", f"₹{total:.2f}")
        
        fig = px.pie(df, values='amount', names='category', title="Category Wise Expenses", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(df[['date', 'description', 'amount', 'category', 'notes']], use_container_width=True)
    else:
        st.info("No records found yet.")

with tab3:
    st.subheader("Upload Bank / GPay Statement")
    uploaded_file = st.file_uploader("Upload PDF Statement", type=["pdf"])
    if uploaded_file is not None:
        with open("temp_statement.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("File uploaded successfully!")
        try:
            statement_df = parse_bank_statement("temp_statement.pdf")
            if not statement_df.empty:
                for _, row in statement_df.iterrows():
                    cat = categorize_transaction(row['Description'])
                    add_transaction(row['Date'], row['Description'], row['Amount'], row['Type'], cat, "Imported PDF")
                st.success(f"Imported {len(statement_df)} items!")
            else:
                st.warning("Could not auto-extract rows. Format mismatch.")
        except Exception as e:
            st.error(f"Error: {e}")