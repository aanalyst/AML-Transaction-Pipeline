# AML Transaction Pipeline

An end-to-end Anti-Money Laundering (AML) transaction monitoring pipeline built in Python. The system generates synthetic banking transactions, scores them using a rule engine and machine learning model, generates professional SAR narratives via the Claude API, and outputs a formatted Excel compliance report.

---

## Architecture

![AML Pipeline Architecture](https://raw.githubusercontent.com/aanalyst/AML-Transaction-Pipeline/main/assets/architecture.png)

---

## Features

- **Synthetic data generation** — 1,004 realistic banking transactions with embedded AML patterns
- **Rule engine** — detects structuring, high-risk jurisdiction flags, and velocity spikes
- **Machine learning** — Random Forest classifier producing a continuous risk score per transaction
- **SAR narrative generation** — Claude API generates professional AUSTRAC-compliant narratives for each flagged case
- **Excel report** — formatted SAR report with colour-coded risk bands ready for compliance review

## AML Patterns Detected

| Pattern | Description |
|---|---|
| Structuring | Amounts between $9,000–$9,999 to avoid $10,000 reporting threshold |
| Jurisdiction | Transactions involving Iran, Myanmar, Russia, North Korea, Venezuela |
| Velocity | Same customer making 4+ transactions within a 24-hour window |

---

## Results

- 1,004 transactions scored
- 142 flagged as high risk
- 142 SAR narratives generated
- Full report exported to `output/sar_report.xlsx`

---

## Tech Stack

- Python
- PostgreSQL + psycopg2
- scikit-learn (Random Forest)
- Anthropic Claude API
- openpyxl
- pandas

---

## Setup

**1. Clone the repo**

**2. Create and activate virtual environment**
python -m venv venv
venv\Scripts\activate

**3. Install dependencies**
pip install pandas psycopg2-binary anthropic openpyxl scikit-learn python-dotenv

**4. Create a `.env` file in the project root**
DB_HOST=localhost
DB_PORT=5432
DB_NAME=aml_pipeline
DB_USER=postgres
DB_PASSWORD=your_password
ANTHROPIC_API_KEY=your_api_key

**5. Set up PostgreSQL**

Create the database and transactions table by connecting to PostgreSQL and running the schema in `db_setup.sql` (or manually via psql).

**6. Run the pipeline**
python src/generate_data.py
python src/score_transaction.py
python src/generate_narratives.py
python src/generate_report.py

---

## Output

The final SAR report is available in `output/sar_report.xlsx`. Each flagged transaction includes a Claude API-generated narrative referencing the AML/CTF Act 2006 and AUSTRAC obligations.

---

## Disclaimer

All transaction data is synthetically generated. No real customer information was used in this project.

