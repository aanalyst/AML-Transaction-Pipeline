import pandas as pd
import numpy as np
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# ── 1. Load CSV ──────────────────────────────────────────────────────────────
df = pd.read_csv("data/transactions.csv", parse_dates=["date"])
print(f"Loaded {len(df)} transactions")

# ── 2. Rule Engine ───────────────────────────────────────────────────────────
high_risk_countries = ["Iran", "Myanmar", "Russia", "North Korea", "Venezuela"]

# Rule 1 - Structuring: amount between $9,000 and $9,999
df["rule_structuring"] = df["amount"].between(9000, 9999).astype(int)

# Rule 2 - Jurisdiction: country is in high risk list
df["rule_jurisdiction"] = df["country"].isin(high_risk_countries).astype(int)

# Rule 3 - High velocity: same customer, more than 3 transactions in 24 hours
df = df.sort_values("date")
df["rule_velocity"] = 0

for customer in df["customer_id"].unique():
    mask = df["customer_id"] == customer
    customer_df = df[mask].copy()
    for idx, row in customer_df.iterrows():
        window_start = row["date"]
        window_end = row["date"] + pd.Timedelta(hours=24)
        count = customer_df[
            (customer_df["date"] >= window_start) &
            (customer_df["date"] <= window_end)
        ].shape[0]
        if count > 3:
            df.at[idx, "rule_velocity"] = 1

print("Rule engine complete")

# ── 3. ML Model ──────────────────────────────────────────────────────────────
le = LabelEncoder()
df["country_encoded"] = le.fit_transform(df["country"])

features = ["amount", "country_encoded", "rule_structuring", "rule_jurisdiction", "rule_velocity"]
X = df[features]

# Labels: flagged if any rule fires
y = ((df["rule_structuring"] + df["rule_jurisdiction"] + df["rule_velocity"]) > 0).astype(int)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

df["risk_score"] = model.predict_proba(X)[:, 1]

print("ML scoring complete")

# ── 4. Assign Risk Band ───────────────────────────────────────────────────────
def assign_risk_band(score):
    if score >= 0.7:
        return "High"
    elif score >= 0.4:
        return "Medium"
    else:
        return "Low"

df["risk_band"] = df["risk_score"].apply(assign_risk_band)
df["is_flagged"] = df["risk_score"] >= 0.7

print(f"Flagged transactions: {df['is_flagged'].sum()}")

# ── 5. Write to PostgreSQL ────────────────────────────────────────────────────
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cursor = conn.cursor()

for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO transactions (
            transaction_id, customer_id, amount, date, country,
            risk_score, risk_band, is_flagged, sar_narrative
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (transaction_id) DO UPDATE SET
            risk_score = EXCLUDED.risk_score,
            risk_band = EXCLUDED.risk_band,
            is_flagged = EXCLUDED.is_flagged
    """, (
        row["transaction_id"],
        row["customer_id"],
        row["amount"],
        row["date"],
        row["country"],
        round(float(row["risk_score"]), 4),
        row["risk_band"],
        bool(row["is_flagged"]),
        None
    ))

conn.commit()
cursor.close()
conn.close()

print("All transactions written to PostgreSQL")