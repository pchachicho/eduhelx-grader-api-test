import json
from fastapi import Request, HTTPException
import sys
import os

current_dir = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, parent_dir)
from app.core.middleware.logger import LogMiddleware


class MockApp:
    def __init__(self):
        self.logger = MockLogger()

class MockLogger:
    def info(self, log_data):
        pass

async def mock_call_next(request):
    return MockResponse()

class MockResponse:
    def __init__(self, status_code=200, body=b'{"key": "value"}'):
        self.status_code = status_code
        self.body_iterator = [body]

async def test_log_middleware():
    request = Request({"type": "http", "method": "GET", "url": "http://mockURL.com"})
    middleware = LogMiddleware(MockApp())

    response = await middleware.dispatch(request, mock_call_next)

    assert isinstance(response, MockResponse)

    assert isinstance(middleware.log_data, dict)
    assert "req" in middleware.log_data
    assert "res" in middleware.log_data

    assert middleware.log_data["req"]["method"] == "GET"
    assert middleware.log_data["res"]["status_code"] == 200

    assert "GET" in str(middleware.log_data)

    json.dumps(middleware.log_data)

    middleware.log_data = None
