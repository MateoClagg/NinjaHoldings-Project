# NinjaHoldings Data Engineering - Part 3: Reflection

While my current implementation is simple and runs entirely in Pandas, this reflection outlines how I would evolve it if I were building for production scale and reliability. I'll discuss potential scalability challenges, failure modes, and approaches to error handling and monitoring that I've learned through coursework and my AWS certification studies.

---

## 1. If these files were millions of rows instead of a few thousand, what would you do differently?

My current approach loads entire datasets into memory, which works fine for small files but would hit memory limits as data grows.

**Tool Selection:**
- **Mid-scale (10-50M rows):** I'd switch to **Polars** for better memory efficiency and parallel processing, or **DuckDB** which would use SQL queries directly on the CSV files without loading everything into RAM.
- **Large-scale (100M+ rows):** I'd move to **Apache Spark** running on EMR for distributed compute, or consider loading data into a cloud warehouse like Redshift Spectrum or Snowflake.

**File Format & Storage:**
- I'd switch from CSV to **Parquet** for columnar storage. Parquet is much more efficient for analytical queries since it only reads the columns you need and has built-in compression.
- I'd store data in **S3** and partition by `transaction_date` so queries can skip irrelevant date ranges.

**Pipeline Architecture:**
- Instead of a one-off script, I'd set this up as a scheduled job using Airflow or AWS Step Functions, reading from S3 and writing partitioned Parquet outputs.
- The transformed data could then be loaded into Redshift or queried directly in Athena, with indexes on `customer_id` and `transaction_date` for faster joins.

**Fallback Strategy:**
- If I had to stick with Pandas, I'd use the `chunksize` parameter to process data in batches, though this could make groupby operations more complex.

---

## 2. How might my implementation fail?

**Data Quality Issues:**
- If the CSV files are malformed (e.g. wrong delimiters, inconsistent column counts), the `read_csv` call would fail with parsing errors.
- Non-numeric values in the `amount` column would crash during aggregation.
- Invalid dates that get converted to `NaT` could break the `year_month` groupby or produce unexpected results.

**Memory Constraints:**
- If files are too large for available RAM, Python would crash or the OS might kill the process.
- The groupby and merge operations create additional DataFrames in memory, which makes the problem worse.

**File System Issues:**
- If the input CSV files don't exist at the paths I specified, the script fails immediately.
- If there's no write permission or not enough disk space, the final `to_csv` operation would fail.

**Logic Errors:**
- If I accidentally joined on the wrong column name, rows would get silently dropped without any warning.
- If my cleaning filters are too aggressive (like if all transactions are orphaned), I'd end up with an empty output and no clear explanation why.

**Edge Cases:**
- Customer names with commas or quotes could break the CSV formatting for anyone using the output file downstream.
- If a DataFrame becomes empty after a cleaning step, aggregation functions might fail or return weird results.

---

## 3. What safeguards could I put in place to make sure my implementation fails gracefully?

**Input Validation:**
- I'd check that CSV files exist before trying to read them, and exit with a clear error message if they're missing.
- After loading, I'd validate that the required columns (`customer_id`, `amount`, `transaction_date`) are actually present.
- I could add basic schema checks to make sure data types match expectations before starting the transformation.

**Data Quality Checks:**
- After each cleaning step, I'd verify the DataFrame isn't empty and track how many rows were removed. If I'm filtering out more than 50% of the data, that probably indicates an upstream problem rather than normal cleaning.
- I'd add assertions for critical assumptions, like making sure at least some customers and transactions remain after cleaning.

**Error Handling:**
- I'd wrap file operations in try/except blocks and make sure error messages include useful context (like the file path and what went wrong).
- For type conversion failures, I could log the problematic rows and either skip them or fail with a clear explanation, rather than just crashing.

**Resource Management:**
- I'd check available disk space before writing the output file.
- For larger files, I could check the file size first and switch to chunked processing if needed.

**Graceful Degradation:**
- If the output would be empty (like if all transactions get filtered out), I'd write a summary explaining what happened instead of just creating an empty CSV.

---

## 4. What could I do to know how it failed and why it failed?

**Structured Logging:**
- I'd add logging at each major step (load, clean, transform, write) with timestamps and row counts, so I can see where data is getting lost or things are slowing down.
- I'd use different log levels (INFO, WARNING, ERROR) to indicate how serious each message is.

**Detailed Error Context:**
- When something fails, I'd capture the full stack trace and try to log the specific value that caused the problem (like "Failed to parse date '2023-13-45' at row 1523").
- I'd include file metadata in error messages (path, size, when it was last modified) to help with debugging.

**Data Quality Reporting:**
- After each run, I'd generate a summary showing: rows loaded, nulls removed, duplicates dropped, orphaned transactions filtered, and final rows written.
- If I was running this regularly, I could track these metrics over time to spot trends (like if the null rate suddenly jumps from 1% to 20%).

**Monitoring & Alerting (Production):**
- In a production environment, I'd set up CloudWatch (or similar) to collect logs and trigger alarms if the pipeline fails or takes unusually long to run.
- I'd also monitor resource usage (memory, disk, CPU) to catch problems before they cause crashes.

**Audit Trail:**
- For each run, I'd save metadata to a database or log file: start/end timestamps, input file hashes, row counts at each stage, total elapsed time, and whether it succeeded or failed.
- This would create a history I could use for debugging recurring issues or understanding what changed between runs.
