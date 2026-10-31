
import logging
from typing import Literal
from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.models import Project, Service, HealthCheck


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("forgeops")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ForgeOps API")


def get_db():
    """Provide a database session for each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# Project schemas
# -------------------------

class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=2000)


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str


# -------------------------
# Service schemas
# -------------------------

class ServiceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    url: str = Field(min_length=1, max_length=500)
    description: str = Field(default="", max_length=2000)


class ServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    url: str
    description: str


# -------------------------
# Health check schemas
# -------------------------

class HealthCheckCreate(BaseModel):
    status: Literal["healthy", "unhealthy", "unknown"]
    response_time_ms: float | None = Field(default=None, ge=0)
    details: str = Field(default="", max_length=2000)


class HealthCheckResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    service_id: int
    status: str
    response_time_ms: float | None
    checked_at: object
    details: str


# -------------------------
# Health endpoint
# -------------------------

@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {"status": "healthy"}


# -------------------------
# Project endpoints
# -------------------------

@app.post(
    "/projects",
    response_model=ProjectResponse,
    status_code=201,
)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
):
    new_project = Project(
        name=project.name,
        description=project.description,
    )

    try:
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database error while creating a project")
        raise HTTPException(
            status_code=500,
            detail="Unable to create project due to a database error",
        ) from None

    logger.info("Project created successfully: id=%s", new_project.id)
    return new_project


@app.get("/projects", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).order_by(Project.id).all()
    logger.info("Project list requested: count=%s", len(projects))
    return projects


@app.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    project = db.get(Project, project_id)

    if project is None:
        logger.warning("Project not found: id=%s", project_id)
        raise HTTPException(status_code=404, detail="Project not found")

    logger.info("Project retrieved successfully: id=%s", project_id)
    return project


# -------------------------
# Service endpoints
# -------------------------

@app.post(
    "/services",
    response_model=ServiceResponse,
    status_code=201,
)
def create_service(
    service: ServiceCreate,
    db: Session = Depends(get_db),
):
    new_service = Service(
        name=service.name,
        url=service.url,
        description=service.description,
    )

    try:
        db.add(new_service)
        db.commit()
        db.refresh(new_service)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database error while creating a service")
        raise HTTPException(
            status_code=500,
            detail="Unable to register service",
        ) from None

    logger.info("Service registered: id=%s", new_service.id)
    return new_service


@app.get("/services", response_model=list[ServiceResponse])
def list_services(db: Session = Depends(get_db)):
    services = db.query(Service).order_by(Service.id).all()
    logger.info("Service list requested: count=%s", len(services))
    return services


@app.get("/services/{service_id}", response_model=ServiceResponse)
def get_service(
    service_id: int,
    db: Session = Depends(get_db),
):
    service = db.get(Service, service_id)

    if service is None:
        logger.warning("Service not found: id=%s", service_id)
        raise HTTPException(status_code=404, detail="Service not found")

    return service


# -------------------------
# Health check endpoints
# -------------------------

@app.post(
    "/services/{service_id}/checks",
    response_model=HealthCheckResponse,
    status_code=201,
)
def create_health_check(
    service_id: int,
    check: HealthCheckCreate,
    db: Session = Depends(get_db),
):
    service = db.get(Service, service_id)

    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")

    new_check = HealthCheck(
        service_id=service_id,
        status=check.status,
        response_time_ms=check.response_time_ms,
        details=check.details,
    )

    try:
        db.add(new_check)
        db.commit()
        db.refresh(new_check)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database error while recording health check")
        raise HTTPException(
            status_code=500,
            detail="Unable to record health check",
        ) from None

    logger.info(
        "Health check recorded: service_id=%s status=%s",
        service_id,
        new_check.status,
    )

    return new_check


@app.get(
    "/services/{service_id}/checks",
    response_model=list[HealthCheckResponse],
)
def list_health_checks(
    service_id: int,
    db: Session = Depends(get_db),
):
    service = db.get(Service, service_id)

    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")

    checks = (
        db.query(HealthCheck)
        .filter(HealthCheck.service_id == service_id)
        .order_by(HealthCheck.checked_at.desc())
        .all()
    )

    return checks
