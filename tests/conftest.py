from typing import Union
from pathlib import Path
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
import json
import os
import sys
import inspect
import unittest.mock

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

# Note: UserModel can't be statically imported at the module scope due to it not being mocked yet.
def create_user_client(client: TestClient, user: Union[str, "UserModel"]):
    from app.database import SessionLocal
    from app.models import UserModel
    from app.core.middleware.authentication import CurrentUser
    from app.core.utils.token_helper import TokenHelper

    if isinstance(user, UserModel):
        user_model = user
    else:
        with SessionLocal() as session:
            user_model = session.query(UserModel).filter_by(onyen=user).first()

    current_user = CurrentUser(id=user_model.id, onyen=user_model.onyen)
    access_token = TokenHelper.encode(payload=current_user.dict(), expire_period=1E9)
    client.headers["Authorization"] = "Bearer " + access_token

    yield client
    
    del client.headers["Authorization"]

@pytest.fixture()
def user_client(test_client, request):
    yield next(create_user_client(test_client, request.param))

@pytest.fixture()
def admin_client(test_client):
    from .data.database.instructor import admin
    yield next(create_user_client(test_client, admin.onyen))

#########################
#        Mocking        #
#########################
@pytest.fixture(scope="session", autouse=True)
def mock_settings():
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

    mock_config_module = unittest.mock.MagicMock()
    mock_config_module.settings = MockSettings()

    sys.modules["app.core.config"] = mock_config_module
    
    yield mock_config_module.settings

    del sys.modules["app.core.config"]

    

@pytest.fixture(scope="session")
def mock_database(session_mocker):
    from sqlalchemy import create_engine
    from sqlalchemy.pool import StaticPool
    from sqlalchemy.orm import sessionmaker, declarative_base

    mock_database_module = unittest.mock.MagicMock()
    
    mock_engine = create_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )
    mock_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=mock_engine)
    mock_Base = declarative_base()

    mock_database_module.engine = mock_engine
    mock_database_module.SessionLocal = mock_SessionLocal
    mock_database_module.Base = mock_Base

    sys.modules["app.database"] = mock_database_module

    import app.models as models
    mock_Base.metadata.create_all(mock_engine)

    with mock_SessionLocal(expire_on_commit=False) as session:
        from .data import database as mock_database
        mock_database = inspect.getmembers(mock_database, inspect.ismodule)
        for (module_name, module) in mock_database:
            for model in module.data:
                session.add(model)

        session.commit()

    yield mock_database_module

    del sys.modules["app.database"]