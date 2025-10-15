# NinjaHoldings Data Engineering - Part 1: Data Modeling & SQL

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

This is a simple two-table relational schema optimized for analytical queries:

- **Customers** table stores customer information
- **Transactions** table stores transaction records
- One-to-many relationship: each customer can have multiple transactions

**The schema is in Third Normal Form (3NF):**
- All attributes depend on the primary key
- No transitive dependencies
- Foreign key relationship maintains referential integrity

**Schema design decisions:**
- Used `INTEGER` for ID fields (efficient storage and indexing, matches source data type)
- Kept `name` as single field (source data is synthetic "Customer_N" format - no benefit to splitting)
- State stored as `CHAR(2)` for standardized 2-letter state abbreviations
- Foreign key constraint ensures no orphaned transactions

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
    amount            DECIMAL(12, 2) CHECK (amount IS NOT NULL),
    transaction_date  DATE NOT NULL,

    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);
```

### Key Design Decisions

**Data Types:**
- `INTEGER` for IDs: Efficient storage and indexing, matches source data
- `DECIMAL(12, 2)`: Provides precise fixed-point storage for financial data up to 10 digits before the decimal and 2 after, avoiding floating-point rounding issues
- `DATE` for dates: Matches source data precision (no time component available)
- `CHAR(2)` for state: Fixed-length, efficient for 2-letter state codes
- `VARCHAR(50)` for names: Reasonable length for customer names

**Constraints:**
- `NOT NULL` on all columns: Ensures data completeness
- `CHECK (amount IS NOT NULL)`: Ensures valid non-null amounts while allowing potential refunds or credits if negative amounts are later introduced
- `PRIMARY KEY`: Ensures uniqueness and creates implicit index
- `FOREIGN KEY` with:
  - `ON DELETE RESTRICT`: Prevents deleting customers with existing transactions (data integrity)
  - `ON UPDATE CASCADE`: If customer_id changes, update related transactions automatically

---

## 3. SQL Queries

### Query 1: Total Customers Who Signed Up in 2024

**Objective:** Count the total number of customers who created accounts during the year 2024, useful for measuring year-over-year customer acquisition growth.

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

**Objective:** Identify the highest-value customers by total transaction volume. This helps prioritize customer retention efforts and identify VIP accounts for personalized service.

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

**Objective:** Calculate the average transaction amount for each state to identify geographic patterns in customer spending behavior. This can inform regional marketing strategies and pricing decisions.

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
- Transaction amounts are positive in this sample dataset, but the schema supports negative values for future use cases like refunds or credits
- Every transaction has a valid customer reference (enforced by foreign key constraint)
- Customer names in source CSV follow "Customer_N" format (synthetic test data)
- State codes in source data are valid 2-letter US state abbreviations

### Business Rules
- Customers cannot be deleted if they have existing transactions (ON DELETE RESTRICT)
- No duplicate customer IDs or transaction IDs (PRIMARY KEY constraint)
- All fields are required (NOT NULL constraints)

### Performance Notes
- For small datasets (<10K rows), indexes on foreign keys are created implicitly by constraints
- For production scale (millions of rows), would add explicit indexes on:
  - `transactions.customer_id` (for joins)
  - Other columns commonly used for queries (e.g. dates for grouping)
