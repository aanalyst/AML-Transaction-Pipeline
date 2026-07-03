import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

customer_ids = [f"CUST{str(i).zfill(3)}" for i in range(1, 201)]

high_risk_countries = ["Iran", "Myanmar", "Russia", "North Korea", "Venezuela"]

low_risk_countries = ["Australia", "United Kingdom", "United States",
                      "Germany", "Singapore", "Japan", "Canada",
                      "France", "Netherlands", "New Zealand"]


def generate_normal_transaction():
    return {
        "customer_id": random.choice(customer_ids),
        "amount": round(random.uniform(100, 50000), 2),
        "date": (datetime.now() - timedelta(days=random.randint(0, 90))).replace(microsecond=0),
        "country": random.choice(low_risk_countries)
    }


def generate_structuring():
    return {
        "customer_id": random.choice(customer_ids),
        "amount": round(random.uniform(9000, 9999), 2),
        "date": (datetime.now() - timedelta(days=random.randint(0, 90))).replace(microsecond=0),
        "country": random.choice(low_risk_countries)
    }


def generate_jurisdiction():
    return {
        "customer_id": random.choice(customer_ids),
        "amount": round(random.uniform(100, 50000), 2),
        "date": (datetime.now() - timedelta(days=random.randint(0, 90))).replace(microsecond=0),
        "country": random.choice(high_risk_countries)
    }


def generate_high_velocity():
    customer = random.choice(customer_ids)
    base_date = datetime.now() - timedelta(days=random.randint(0, 90))
    transactions = []
    for _ in range(6):
        transactions.append({
            "customer_id": customer,
            "amount": round(random.uniform(100, 50000), 2),
            "date": (base_date + timedelta(hours=random.randint(0, 23))).replace(microsecond=0),
            "country": random.choice(low_risk_countries)
        })
    return transactions


rows = []

for _ in range(850):
    rows.append(generate_normal_transaction())

for _ in range(50):
    rows.append(generate_structuring())

for _ in range(50):
    rows.append(generate_jurisdiction())

for _ in range(9):
    rows.extend(generate_high_velocity())

random.shuffle(rows)

df = pd.DataFrame(rows)
df.reset_index(drop=True, inplace=True)
df.insert(0, "transaction_id", [f"TXN{str(i).zfill(4)}" for i in range(1, len(df) + 1)])

df.to_csv("data/transactions.csv", index=False)
print(f"Generated {len(df)} transactions and saved to data/transactions.csv")