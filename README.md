
# ForgeOps

ForgeOps is a software operations and reliability platform built with
Python, FastAPI, SQLAlchemy, and SQLite.

The project is being developed incrementally to demonstrate backend
engineering, API design, automated testing, data persistence, and
reliable software development practices.

## Current Features

- Health-check endpoint
- Create software projects
- List existing projects
- Retrieve a project by ID
- Structured request validation
- SQLite persistence
- Automated API tests using pytest
- Isolated test databases

## Technology Stack

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- SQLite
- pytest
- HTTPX

## Local Setup

Clone the repository, then enter the project directory.

Create and activate a virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate

Install dependencies:

    python -m pip install -r requirements.txt

Start the development server:

    python -m uvicorn app.main:app --reload

Open the API documentation:

    http://127.0.0.1:8000/docs

## Running Tests

Run the automated test suite:

    python -m pytest -v

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | /health | Check application health |
| POST | /projects | Create a project |
| GET | /projects | List projects |
| GET | /projects/{project_id} | Retrieve a project |

## Development Roadmap

- [x] API foundation
- [x] SQLite persistence
- [x] Automated API tests
- [x] Basic input validation
- [ ] Improved error handling and test coverage
- [ ] Database migrations
- [ ] Structured logging and configuration
- [ ] Continuous integration
- [ ] Containerized deployment
- [ ] Service health and incident tracking

## Project Status

ForgeOps is an active learning and portfolio project. It is not
intended for production use yet.
