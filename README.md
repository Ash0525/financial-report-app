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

## Desktop Application Roadmap

The first distributable version will remain completely local. A user will
install a normal macOS application, open it from Finder or the Dock, and use
the existing interface without installing Python or starting a server
manually.

The application will continue to use the existing layers:

```text
macOS application window
        ↓
HTML, CSS, and JavaScript frontend
        ↓
FastAPI running on 127.0.0.1 only
        ↓
SQLite database and PDF generator
```

FastAPI will be bundled inside the application. It will not be exposed to the
internet, and the desktop launcher will start and stop it automatically.

### Phase 1: Safe Local Data

- [x] Store the working database in the user's macOS Application Support
  directory instead of inside the application bundle:
  `~/Library/Application Support/Financial Report App/reports.db`.
- [x] Create the data directory automatically on first launch.
- [x] Keep database-path selection configurable so tests can continue using
  isolated temporary databases.
- [x] Migrate the existing repository database without overwriting a database
  already present in Application Support.
- [x] Add timestamped local backups using SQLite's backup API.
- [x] Retain the 10 most recent backups so storage use stays predictable.
- [x] Add tests for data-directory creation, migration, backup creation, and
  backup cleanup.

This phase comes first because replacing or updating a `.app` must never erase
the user's financial reports.

### Phase 2: Desktop Launcher

- Add a desktop entry point separate from the development server entry point.
- Start FastAPI programmatically on `127.0.0.1`.
- Wait until the local API is ready before displaying the interface.
- Open the existing frontend in a macOS application window.
- Stop the local server cleanly when the application window closes.
- Display a useful error message if startup fails.

Development through Uvicorn and the browser will remain available.

### Phase 3: macOS Packaging

- Add the desktop runtime dependencies.
- Create a PyInstaller specification for a macOS `.app`.
- Include the complete `frontend` directory and other required assets.
- Resolve asset paths correctly in both development and packaged modes.
- Add an application name, bundle identifier, icon, and version.
- Initially build for the Mac processor architecture used by the target
  machine.
- Add a repeatable build command and document where the finished application
  is produced.

### Phase 4: Installation and Recovery Testing

- Test the application from Finder without VS Code or an active terminal.
- Test it from a clean macOS user account.
- Verify that reports remain after closing and reopening the application.
- Verify that reports remain after replacing the `.app` with a newer build.
- Verify PDF creation and downloads from the packaged application.
- Verify that a backup can restore the database.
- Confirm that the server accepts local connections only.
- Document the one-time Gatekeeper procedure required for the initial unsigned
  private build.

### Phase 5: Private Local Release

- Produce a versioned `.app` for private use.
- Package it in a `.zip` or disk image for transfer.
- Give the user short installation, backup, and recovery instructions.
- Treat application updates and user data as separate concerns: replacing the
  application must leave the Application Support directory unchanged.

This private version can use free tooling. An unsigned application may require
the user to Control-click it and select **Open** the first time.

### Phase 6: Professional Distribution

When the application is ready for customers:

- Join the Apple Developer Program.
- Sign the application with a Developer ID certificate.
- Enable the appropriate macOS security settings.
- Notarize releases with Apple.
- Add a controlled update process and release history.
- Add encrypted off-device backups and a documented recovery policy.

### Phase 7: Optional Hosted Product

If the product later becomes an online service:

- Replace local-only persistence with a managed production database.
- Add user accounts, secure authentication, authorization, and tenant
  separation.
- Encrypt network traffic and sensitive stored data.
- Add managed backups, monitoring, audit logs, rate limiting, and a secret
  management system.
- Create privacy, retention, incident-response, and support procedures before
  accepting customer financial data.

The frontend, validation rules, API concepts, database interface, and PDF
service should remain separated now so they can be reused during that
transition.

## Next Implementation Task

Implement Phase 1 before creating the desktop wrapper:

1. Introduce one function responsible for resolving the application data
   directory.
2. Update the database module to use that location by default.
3. Preserve the ability to inject a temporary database path in tests.
4. Add database backup and retention functions.
5. Add automated tests before moving on to the desktop launcher.
