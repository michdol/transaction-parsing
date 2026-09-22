# Agent Tasks: Transaction Import Application

A small operations team receives transaction exports and needs to understand what was accepted, what was rejected, and the total.

Main business rules of the entire project:
1. Select a supplied CSV through the React screen and import it.
2. Accept valid rows, reject invalid rows with their source row number and a useful reason.
3. Show accepted records, rejected rows, counts and the exact total for that import.
4. Store imports locally so they remain available after restarting the backend. The UI must let the user reopen a previous import.
5. Make loading, empty and failure states understandable. A failed request must not look like a successful import.

A single-process synchronous implementation with SQLite is entirely sufficient. You may choose another design but keep it runnable locally. No accounts, cloud deployment, background queue, authentication, XLSX support, charts or mobile styling are required.

## Goal

Implement a working project that consists of:
- FastApi backend
- React frontend
- Use Python 3.12+ and Node 22.12+.
- Keep the solution runnable locally.
- SQLite and synchronous processing are sufficient.
- accounts, cloud deployment, queues, authentication, XLSX support, charts, or mobile-specific work.

It should be a PoC, not production-ready applications, so implement things only asked for, nothing else.


## Tasks

1. Create docker image for the frontend app. Port: 5173
Read other tasks for configurations if necessary.
2. Backend task: There will be a ImportService class to be injected into FastApi app. It should implement a data evaluator accoring to below rules:

Data rules (used by the evaluator)

UTF-8 CSV with exactly these header names in any order: `transaction_id,date,customer,amount,currency`. Ignore blank lines. Trim surrounding whitespace in field values; header names are exact and unique. CSV quoting follows the standard CSV format. Inputs are at most 1 MiB / 1,000 records; multiline quoted fields and files beyond those limits are outside grading.

- ID and customer are nonempty after trimming. IDs are case-sensitive.
- Dates are real calendar dates in exact YYYY-MM-DD format.
- Amount is a positive decimal with zero, one or two decimal places, no sign/exponent/thousands separators, at most 1,000,000.00. Use exact cents, not floating-point rounding.
- Currency is exactly EUR after trimming.
- Within one import, the first **valid** occurrence of an ID wins. Later valid duplicates are rejected; an invalid row does not reserve its ID.
- Imports are independent: importing the same file twice creates two independent import records, not a global deduplication problem.
- Malformed/duplicate/missing headers or structurally malformed CSV return HTTP 400 without creating an import. A header-only file and a file whose data rows are all invalid are valid imports with zero accepted rows.
- Rows with too many/few fields are rejected as rows. Any useful explanation is acceptable; error text and error precedence are not prescribed.

`data/transactions.csv` contains synthetic data. Its expected result is 3 accepted, 3 rejected, total **13550 cents**.


3. Backend: ImportService dependency-injected into API
Implement the API contract:

- `GET /api/health` returns HTTP 200.
- `POST /api/imports` accepts `{"csv":"..."}` and returns HTTP 201 with the full import object.
- `GET /api/imports/{id}` returns the import object or HTTP 404.
- `GET /api/imports` returns imports newest first.

An import object has `id` (nonempty string), `accepted_count`, `rejected_count`, `total_minor` (integer cents), `currency:"EUR"`, `accepted` and `rejected` arrays. Accepted records contain normalized `transaction_id,date,customer,currency,amount_minor`. Rejected entries contain `row` (CSV record number, header = 1) and `reason` (nonempty string). Extra fields are fine. Set `DATABASE_PATH` for your local SQLite file; our runner supplies a writable path and uses the same value when restarting the server.

The evaluator exercises these contracts with other data following these rules. UI review checks that the user can perform the workflow, not pixel appearance or your component structure.
Should run on port 8000.

4. Frontend: Minimal working react app, keep .css to bare minimum, the less the better. Interface must work, doesn't have to be pretty.
- should run on port 5173
