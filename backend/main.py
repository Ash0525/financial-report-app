from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

from . import database, schemas
from .services import pdf_generator

from .version import APP_VERSION

FRONTEND_DIRECTORY = Path(__file__).resolve().parent.parent / "frontend"


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Initialize persistent resources before accepting requests."""

    database.initialize_database()
    database.create_database_backup()
    yield


app = FastAPI(
    title="Financial Report API",
    version=APP_VERSION,
    lifespan=lifespan,
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/reports",
    response_model=schemas.ReportRead,
    status_code=201,
)
def create_report(report: schemas.ReportCreate) -> schemas.ReportRead:
    report_id = database.create_report(report)
    saved_report = database.get_report(report_id)

    if saved_report is None:
        raise HTTPException(
            status_code=500,
            detail="Report was saved but could not be retrieved",
        )

    return saved_report


@app.get(
    "/reports",
    response_model=list[schemas.ReportSummary],
)
def list_reports() -> list[schemas.ReportSummary]:
    return database.list_reports()


@app.get(
    "/reports/{report_id}",
    response_model=schemas.ReportRead,
)
def get_report(report_id: int) -> schemas.ReportRead:
    report = database.get_report(report_id)

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    return report


@app.delete(
    "/reports/{report_id}",
    status_code=204,
)
def delete_report(report_id: int) -> None:
    was_deleted = database.delete_report(report_id)

    if not was_deleted:
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )


@app.get(
    "/reports/{report_id}/pdf",
    response_class=Response,
)
def download_report_pdf(report_id: int) -> Response:
    report = database.get_report(report_id)

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    pdf_bytes = pdf_generator.generate_report_pdf(report)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="report-{report_id}.pdf"'
            ),
        },
    )

@app.delete("/reports")
def delete_all_reports() -> dict[str, int]:
    deleted_count = database.delete_all_reports()

    return {
        "deleted_count": deleted_count,
    }

# Expose update to FastAPI
# PUT to replace the complete editable report
@app.put(
    "/reports/{report_id}",
    response_model=schemas.ReportRead,
)
def update_report(
    report_id: int,
    report: schemas.ReportCreate,
) -> schemas.ReportRead:
    was_updated = database.update_report(
        report_id,
        report,
    )

    # Raise code error
    if not was_updated:
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )
    
    # Update the report with get_report
    updated_report = database.get_report(report_id)

    if updated_report is None:
        raise HTTPException(
            status_code=500,
            detail="Report was udpated but could not be retrieved",
        )
    
    return updated_report

# Keep this catch-all mount after every API route.
app.mount(
    "/",
    StaticFiles(
        directory=FRONTEND_DIRECTORY,
        html=True,
    ),
    name="frontend",
)
