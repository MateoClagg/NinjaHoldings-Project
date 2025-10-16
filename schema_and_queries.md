# NinjaHoldings Data Engineering - Part 1: Data Modeling & SQL

This section outlines how I designed a simple relational schema for customer and transaction data, along with the SQL queries needed for basic analytics. I kept the design straightforward; two tables in 3NF with proper constraints to ensure data integrity.

---

## 1. Relational Schema Design

### Entity-Relationship Model

```
┌─────────────────┐              ┌──────────────────────┐
│   CUSTOMERS     │              │    TRANSACTIONS      │
├─────────────────┤              ├──────────────────────┤
│ customer_id (PK)│──────────────│ transaction_id (PK)  │
│ name            │      1:N     │ customer_id (FK)     │
│ signup_date     │              │ amount               │
│ state           │              │ transaction_date     │
└─────────────────┘              └──────────────────────┘
```

**Relationship:** One customer can have many transactions (1:N relationship with referential integrity enforced)

### Design Justification

I designed this as a simple two-table schema optimized for analytical queries. The customers table stores basic customer info, and the transactions table records financial activity. Each customer can have multiple transactions (one-to-many relationship).

**Why this structure works:**
- **Third Normal Form (3NF):** All attributes depend on the primary key, no transitive dependencies, and the foreign key relationship maintains referential integrity.
- **No over-normalization:** I kept state codes directly in the customers table since they're just atomic 2-letter values. Creating a separate states table would add unnecessary complexity without real benefit.
- **Synthetic data consideration:** The source data has customer names like "Customer_1", so I kept `name` as a single field rather than splitting it into first/last names—there's no practical reason to parse synthetic data that way.

**Key design decisions:**
- Used `INTEGER` for ID fields since they match the source data and are efficient for indexing
- Used `DECIMAL(12, 2)` for currency to avoid floating-point precision errors
- Used `CHAR(2)` for state codes (fixed-length, efficient)
- Added a foreign key constraint to prevent orphaned transactions

---

## 2. SQL DDL (Data Definition Language)

### Customers Table

```sql
CREATE TABLE customers (
    customer_id  INTEGER PRIMARY KEY,
    name         VARCHAR(50) NOT NULL,
    signup_date  DATE NOT NULL,
    state        CHAR(2) NOT NULL
);
```

### Transactions Table

```sql
CREATE TABLE transactions (
    transaction_id    INTEGER PRIMARY KEY,
    customer_id       INTEGER NOT NULL,
    amount            DECIMAL(12, 2) NOT NULL CHECK (amount >= 0),
    transaction_date  DATE NOT NULL,

    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);
```

### Key Design Decisions

**Data Types:**
- `INTEGER` for IDs: Efficient storage and indexing, matches the source data
- `DECIMAL(12, 2)`: Precise fixed-point storage for currency (avoids floating-point rounding issues)
- `DATE` for dates: Matches source data precision—no time component is available
- `CHAR(2)` for state: Fixed-length, efficient for 2-letter codes
- `VARCHAR(50)` for names: Reasonable length for customer names

**Constraints:**
- `NOT NULL` on all columns: Ensures data completeness
- `CHECK (amount >= 0)`: Prevents negative transactions (refunds would be modeled separately)
- `PRIMARY KEY`: Ensures uniqueness and creates an implicit index
- `FOREIGN KEY` with:
  - `ON DELETE RESTRICT`: Prevents deleting customers who have existing transactions (preserves data integrity)
  - `ON UPDATE CASCADE`: If customer_id changes, related transactions update automatically

---

## 3. SQL Queries

### Query 1: Total Customers Who Signed Up in 2024

**Objective:** Count how many customers created accounts in 2024, useful for tracking year-over-year growth.

```sql
SELECT COUNT(*) AS total_customers_2024
FROM customers
WHERE signup_date >= '2024-01-01'
  AND signup_date < '2025-01-01';
```

**Expected Output:**
```
total_customers_2024
--------------------
42
```

---

### Query 2: Top 5 Customers by Total Transaction Amount

**Objective:** Identify the highest-value customers by total transaction volume to prioritize retention efforts and personalized service.

```sql
SELECT
    c.customer_id,
    c.name,
    SUM(t.amount) AS total_amount
FROM customers c
JOIN transactions t ON c.customer_id = t.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_amount DESC
LIMIT 5;
```

**Expected Output:**
```
customer_id | name        | total_amount
------------+-------------+--------------
47          | Customer_47 | 45829.33
28          | Customer_28 | 43192.87
...
```

---

### Query 3: Average Transaction Amount by State

**Objective:** Calculate average transaction amounts by state to identify geographic spending patterns. This could inform regional marketing strategies or pricing decisions.

```sql
SELECT
    c.state,
    COUNT(t.transaction_id) AS transaction_count,
    ROUND(AVG(t.amount), 2) AS avg_transaction_amount,
    SUM(t.amount) AS total_transaction_amount
FROM customers c
JOIN transactions t ON c.customer_id = t.customer_id
GROUP BY c.state
ORDER BY avg_transaction_amount DESC;
```

**Expected Output:**
```
state | transaction_count | avg_transaction_amount | total_transaction_amount
------+-------------------+------------------------+-------------------------
CA    | 125               | 542.18                 | 67772.50
TX    | 98                | 518.34                 | 50797.32
...
```

---

## 4. Notes and Assumptions

### Data Assumptions
- The sample data has all positive transaction amounts, but the schema uses `CHECK (amount >= 0)` to prevent negatives. Refunds or credits would be modeled as separate transaction types.
- Every transaction must reference a valid customer (enforced by foreign key constraint).
- Customer names follow the "Customer_N" format (synthetic test data).
- State codes are valid 2-letter US abbreviations.

### Business Rules
- Customers can't be deleted if they have existing transactions (`ON DELETE RESTRICT`).
- No duplicate customer IDs or transaction IDs (`PRIMARY KEY` constraint).
- All fields are required (`NOT NULL` constraints).

### Performance Notes
- For this small dataset (<10K rows), indexes are created implicitly by the primary and foreign key constraints.
- For production scale (millions of rows), I'd add explicit indexes on `transactions.customer_id` for joins and potentially on date columns for filtering and grouping.
