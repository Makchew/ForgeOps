
import logging

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database import Base, SessionLocal, engine
from app.models import Project


# Configure logging for the application.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("forgeops")

# Create database tables if they do not exist yet.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ForgeOps API")


def get_db():
    """Provide a database session for each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=2000)


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str


@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {"status": "healthy"}


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
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    logger.info("Project retrieved successfully: id=%s", project_id)

    return project
