# Import data people can trust

A small operations team receives transaction exports and needs to understand what was accepted, what was rejected, and the total. Finish this small Python + React application.

## Time and approach

Stop after **two hours of implementation**. Setup trouble is not the signal we want: record it separately and ask for help if the supplied scaffold will not start. Use the coding agents you normally use. A working, narrow slice with honest limitations is preferable to pretending everything is complete.

Everyone implements the common outcome below. Spend any remaining time on your strongest area (backend, frontend or balanced delivery) and tell us what you chose. Optional polish, infrastructure or tools are not hidden acceptance requirements. If you normally add tests, formatting or linting, use your judgment.

## Starting point

Python 3.12+, Node 22.12+ or a compatible newer version. From this directory:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn backend.main:app --port 8000
# In a second terminal:
cd frontend
npm ci
npm run dev -- --host 127.0.0.1
```

Visit http://localhost:5173. The API health endpoint works; import behavior and the UI are intentionally incomplete. There are no supplied application tests, containers, CI or formatting rules. Starter setup files only get you to a productive starting point.

## Common outcome

1. Select a supplied CSV through the React screen and import it.
2. Accept valid rows, reject invalid rows with their source row number and a useful reason.
3. Show accepted records, rejected rows, counts and the exact total for that import.
4. Store imports locally so they remain available after restarting the backend. The UI must let the user reopen a previous import.
5. Make loading, empty and failure states understandable. A failed request must not look like a successful import.

A single-process synchronous implementation with SQLite is entirely sufficient. You may choose another design but keep it runnable locally. No accounts, cloud deployment, background queue, authentication, XLSX support, charts or mobile styling are required.

## Data rules (used by the evaluator)

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

## Small interface contract

Keep these routes so we can run behavior checks, but organize code as you prefer. Unknown import IDs return 404.

- `GET /api/health` -> HTTP 200.
- `POST /api/imports`, JSON `{"csv":"..."}` -> HTTP 201 with the complete import object.
- `GET /api/imports/{id}` -> that same object.
- `GET /api/imports` -> a JSON array of import objects, newest first.

An import object has `id` (nonempty string), `accepted_count`, `rejected_count`, `total_minor` (integer cents), `currency:"EUR"`, `accepted` and `rejected` arrays. Accepted records contain normalized `transaction_id,date,customer,currency,amount_minor`. Rejected entries contain `row` (CSV record number, header = 1) and `reason` (nonempty string). Extra fields are fine. Set `DATABASE_PATH` for your local SQLite file; our runner supplies a writable path and uses the same value when restarting the server.

The evaluator exercises these contracts with other data following these rules. UI review checks that the user can perform the workflow, not pixel appearance or your component structure.

## Return

ZIP the source, dependency manifests/locks, run instructions and `DECISIONS.md`. Do not include secrets, node_modules, virtualenvs, build output or your local database. In the note, state time spent, chosen emphasis, design tradeoffs, known limitations, verification performed, and your first next improvement. Do not spend extra hours polishing beyond the limit. We will discuss the code and the choices, including things you deliberately left out.
