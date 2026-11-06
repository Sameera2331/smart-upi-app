import re
import pdfplumber
import pandas as pd

def parse_bank_statement(pdf_file_path):
    transactions = []
    with pdfplumber.open(pdf_file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split('\n')
                for line in lines:
                    match = re.search(r'(\d{2}/\d{2}/\d{4})\s+(.+?)\s+([0-9,]+\.\d{2})', line)
                    if match:
                        date, desc, amount = match.groups()
                        transactions.append({
                            'Date': date,
                            'Description': desc.strip(),
                            'Amount': float(amount.replace(',', '')),
                            'Type': 'Expense'
                        })
    return pd.DataFrame(transactions)

def parse_sms(sms_text):
    amt_match = re.search(r'(?:Rs\.?|INR)\s*([\d,]+(?:\.\d{2})?)', sms_text, re.IGNORECASE)
    amount = float(amt_match.group(1).replace(',', '')) if amt_match else 0.0
    return {
        'Date': pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
        'Description': sms_text[:40],
        'Amount': amount,
        'Type': 'Expense'
    }