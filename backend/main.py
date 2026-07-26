from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from . import database, schemas

@asynccontextmanager
async def lifespan(app: FastAPI):
    database.initialize_database()
    yield

app = FastAPI(
    title="Financial Report API",
    lifespan=lifespan,
)

# Registers the function below it as handler for HTTP GET request
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Decorator that reports endpoint
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

# Decorator to get reports
@app.get(
    "/reports",
    response_model=list[schemas.ReportSummary],
)
def list_reports() -> list[schemas.ReportSummary]:
    return database.list_reports()

# Decorator to get report id
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

# Decorator to delete through API
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
