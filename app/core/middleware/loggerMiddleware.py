import json
import time
from starlette.middleware.base import BaseHTTPMiddleware
import json
from .iterator_wrapper import iterator_wrapper as aiwrap

class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
            start_time = time.time()
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
                        "body": await request.body(),
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
    
             # try:
            #     if(response.status_code <= 400):
            #         res = {
            #             "status_code": response.status_code,
            #             "response_time": f"{round((time.time() - start_time) * 1000)} ms"
            #         }
            #     else:
            #         res = {
            #             "status_code": response.status_code,
            #             "response_time": f"{round((time.time() - start_time) * 1000)} ms",
            #             "error_code": "error"
            #         }

            # except Exception as e:
            #     print(e)
            #     raise e
            # request.app.logger.info(
            #     {
            #         "req": { 
            #             "method": request.method, 
            #             "url": str(request.url),
            #             "body": await request.body(),
            #             "user": request.user.onyen if hasattr(request.user, "onyen") else None,
            #         },
            #         "res": { 
            #             "status_code": response.status_code,
            #             "response_time": f"{round((time.time() - start_time) * 1000)} ms"
            #         }
            #     }
            # )
            # return response
        


# if status code > 400, check the error code + message and add to the res
# add user id logging and other context from req