import json
import time
from starlette.types import Message
from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.middleware.iterator_wrapper import iterator_wrapper as aiwrap

class LogMiddleware(BaseHTTPMiddleware):
    # https://github.com/tiangolo/fastapi/issues/394#issuecomment-927272627
    async def set_body(self, request: Request):
        receive_ = await request._receive()

        async def receive() -> Message:
            return receive_

        request._receive = receive

    async def dispatch(self, request, call_next):
            start_time = time.time()

            await self.set_body(request)
            req_body = await request.body()
            response = await call_next(request)

            # Consuming FastAPI response and grabbing body here
            resp_body = [section async for section in response.__dict__['body_iterator']]
            # Repairing FastAPI response
            response.__setattr__('body_iterator', aiwrap(resp_body))

            # Formatting response body for logging
            try:
                resp_body = json.loads(resp_body[0].decode())
            except:
                resp_body = str(resp_body)

            request.app.logger.info(
                {
                    "req": {
                        "method": request.method, 
                        "url": str(request.url),
                        "body": req_body,
                        "user": request.user.onyen if hasattr(request.user, "onyen") else None,
                    },
                    "res": {
                        "status_code": response.status_code,
                        "response_time": f"{round((time.time() - start_time) * 1000)} ms",
                        "body": resp_body
                    }
                }
            )

            return response
    
    