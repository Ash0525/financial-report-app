# Financial Report App

A small full-stack application for creating financial reports, storing income
and expense line items in SQLite, and exporting reports as PDFs.

## Features

- Create reports with multiple income and expense entries.
- Validate money values and reporting periods.
- List, inspect, and delete saved reports.
- Calculate income, expense, and net totals.
- Export complete reports as PDF files.
- Exercise the database, API, validation, and PDF layers with isolated tests.

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run

Start the development server from the repository root:

```bash
python -m uvicorn backend.main:app --reload
```

Open the application at <http://127.0.0.1:8000>. Interactive API
documentation is available at <http://127.0.0.1:8000/docs>.

## Test

Run the complete test suite:

```bash
python -m unittest discover -s backend/tests -v
```

Tests use temporary SQLite databases and do not modify `backend/reports.db`.

## Structure

```text
backend/
├── database.py              SQLite persistence
├── main.py                  FastAPI routes and frontend hosting
├── schemas.py               Pydantic input and output models
├── services/
│   └── pdf_generator.py     PDF rendering
└── tests/                   Automated tests
frontend/
├── index.html               Page structure
├── app.js                   Browser behavior and API requests
└── style.css                Responsive presentation
```
