# financial-report-app

App for storing financials and for financial responsibility

## Run the backend

Activate the project's virtual environment and run the backend:

```bash
source .venv/bin/activate
python backend/main.py
```

You can also open `backend/main.py` and use VS Code's **Run Python File**
button.

schemas.py - financial report schema
database.py - create and initialize the SQLite tables
main.py - API functions to create, retrieve, and list reports

July 26, 2026

get_connection() - establishes a connection to sqlite3

initialize_database() - initialize the database. report_id: connects each line item to its report. item_type: says whether it is income or an expense. CHECK: prevents invalid values like "other". 

LineItem object - has a description (str) and an amount (Decimal)

create_report() - creates the report with title, start period, end period, and notes. Inserts line_items to table. Includes income and expense.

Create test_database.py for testing the database

setUp() - creates temporary database and initalize tables

test - save report, retrieve report, and compare values

tearDown() - restore real database path and delete temporary database