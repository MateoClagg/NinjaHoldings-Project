# NinjaHoldings Data Engineering Take-Home Project

This project was completed as part of the NinjaHoldings Data Engineering Internship take-home assignment. It implements a lightweight ETL workflow for analyzing customer transaction data, including schema design, SQL queries, and a Python-based data transformation pipeline.

## Project Structure

```
ninjaholdings-intern-project/
├── data/                                        # Input CSV files
│   ├── customers.csv
│   └── transactions.csv
├── output/                                      # Generated outputs
│   └── transformed_transactions_monthly.csv
├── src/
│   └── etl.py                                   # ETL pipeline script
├── schema_and_queries.md                        # Part 1: Database design and SQL
├── reflection.md                                # Part 3: Scalability and reliability discussion
├── requirements.txt                             # Python dependencies
└── README.md
```

## Deliverables

### Part 1: Data Modeling & SQL ([schema_and_queries.md](schema_and_queries.md))
- Relational schema design (3NF) for customers and transactions
- DDL statements with constraints (PK, FK, CHECK, NOT NULL)
- Three analytical SQL queries:
  1. Total customers who signed up in 2024
  2. Top 5 customers by transaction volume
  3. Average transaction amount by state

### Part 2: ETL Pipeline ([src/etl.py](src/etl.py))
- Loads customer and transaction data from CSV files
- Cleans data: removes nulls, duplicates, and orphaned transactions
- Transforms transactions into monthly aggregates by customer
- Outputs: [output/transformed_transactions_monthly.csv](output/transformed_transactions_monthly.csv)

### Part 3: Reflection ([reflection.md](reflection.md))
- How the pipeline would scale to millions of rows
- Potential failure modes and edge cases
- Safeguards for graceful error handling
- Logging and monitoring strategies

## Setup & Usage

### Prerequisites
- Python 3.8+
- pip

### Installation

```bash
# Clone or download the project
cd ninjaholdings-intern-project

# Install dependencies
pip install -r requirements.txt
```

### Running the ETL Pipeline

```bash
python src/etl.py
```

The script generates `output/transformed_transactions_monthly.csv` containing monthly transaction summaries grouped by customer.

---

**Author**: Mateo Clagg

**Submitted for**: NinjaHoldings Data Engineering Summer Internship
