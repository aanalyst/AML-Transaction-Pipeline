import psycopg2
import anthropic
from dotenv import load_dotenv
import os
import time

load_dotenv()

# ── 1. Connect to PostgreSQL ──────────────────────────────────────────────────
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cursor = conn.cursor()

# ── 2. Fetch flagged transactions ─────────────────────────────────────────────
cursor.execute("""
    SELECT transaction_id, customer_id, amount, date, country, risk_score, risk_band
    FROM transactions
    WHERE is_flagged = TRUE AND sar_narrative IS NULL
""")
flagged = cursor.fetchall()
print(f"Found {len(flagged)} flagged transactions without narratives")

# ── 3. Initialise Anthropic client ────────────────────────────────────────────
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ── 4. Generate narrative for each flagged transaction ────────────────────────
for row in flagged:
    transaction_id, customer_id, amount, date, country, risk_score, risk_band = row

    prompt = f"""You are an AML compliance analyst. Write a concise SAR (Suspicious Activity Report) narrative for the following transaction. 
The narrative should be professional, factual, and suitable for submission to AUSTRAC.

Transaction Details:
- Transaction ID: {transaction_id}
- Customer ID: {customer_id}
- Amount: ${amount:,.2f}
- Date: {date}
- Country: {country}
- Risk Score: {risk_score:.2f}
- Risk Band: {risk_band}

Write 2-3 sentences maximum. Focus on why this transaction is suspicious based on the details provided."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )

    narrative = response.content[0].text

    cursor.execute("""
        UPDATE transactions
        SET sar_narrative = %s
        WHERE transaction_id = %s
    """, (narrative, transaction_id))

    conn.commit()
    print(f"Narrative generated for {transaction_id}")
    time.sleep(0.5)

cursor.close()
conn.close()
print("All narratives generated and saved to PostgreSQL")