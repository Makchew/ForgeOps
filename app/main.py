from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.models import Project

# Create database tables if they do not exist yet. 
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ForgeOps API")


def get_db():
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

	db.add(new_project)
	db.commit()
	db.refresh(new_project)

	return new_project

@app.get("/projects", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
	return db.query(Project).order_by(Project.id).all()

@app.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(
	project_id: int,
	db: Session = Depends(get_db),
):
	project = db.get(Project, project_id)

	if project is None:
		raise HTTPException(
			status_code=404,
			detail="Project not found",
		)

	return project
