import pytest
import json
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.testclient import TestClient

mock_data_dir = Path(os.path.dirname(__file__), "data")
mock_database_data_dir = mock_data_dir / "database"

@pytest.fixture()
def test_app(mock_database):
    from app.main import app as _app
    from app.core.dependencies import get_db

    # _app.dependency_overrides[get_db] = override_get_db

    yield _app

@pytest.fixture()
def test_client(test_app):
    client = TestClient(test_app)
    
    yield client



#########################
#        Mocking        #
#########################
@pytest.fixture(autouse=True)
def mock_settings(mocker):
    class MockSettings:
        API_V1_STR = "/api/v1"
        DEV_PHASE = "dev"
        DISABLE_AUTHENTICATION = False

        # Authentication
        JWT_SECRET_KEY = "test"
        JWT_ALGORITHM = "HS256"
        ACCESS_TOKEN_EXPIRES_MINUTES = 30
        REFRESH_TOKEN_EXPIRES_MINUTES = 60 * 24 * 30

        POSTGRES_HOST = ""
        POSTGRES_PORT = ""
        POSTGRES_DB = ""
        POSTGRES_USER = ""
        POSTGRES_PASSWORD = ""
        SQLALCHEMY_DATABASE_URI = ""
    
    mock_settings = MockSettings()
    mock = mocker.patch('app.core.config.settings', mock_settings)

    yield mock_settings
    mocker.stop(mock)

@pytest.fixture(scope="session")
def mock_database(session_mocker):
    from sqlalchemy import create_engine
    from sqlalchemy.pool import StaticPool
    from sqlalchemy.orm import sessionmaker, declarative_base
    
    mock_engine = create_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )
    mock_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=mock_engine)
    mock_Base = declarative_base()

    mock_engine_mocker = session_mocker.patch('app.database.engine', mock_engine)
    mock_SessionLocal_mocker = session_mocker.patch('app.database.SessionLocal', mock_SessionLocal)
    mock_Base_mocker = session_mocker.patch('app.database.Base', mock_Base)

    import app.models as models
    mock_Base.metadata.create_all(mock_engine)

    with mock_SessionLocal() as session:
        mock_data = (
            (models.CourseModel, mock_database_data_dir / "course.json"),
            (models.AssignmentModel, mock_database_data_dir / "assignment.json"),
            (models.ExtraTimeModel, mock_database_data_dir / "extra_time.json"),
            (models.SubmissionModel, mock_database_data_dir / "submission.json"),
            (models.StudentModel, mock_database_data_dir / "student.json"),
            (models.InstructorModel, mock_database_data_dir / "instructor.json")
        )
        for (Model, mock_path) in mock_data:
            with open(mock_path, "r") as mock_file:
                for row in json.load(mock_file):
                    model = Model(**row)
                    session.add(model)
        
        session.commit()

    yield (
        mock_engine,
        mock_SessionLocal,
        mock_Base
    )

    session_mocker.stop(mock_engine_mocker)
    session_mocker.stop(mock_SessionLocal_mocker)
    session_mocker.stop(mock_Base_mocker)