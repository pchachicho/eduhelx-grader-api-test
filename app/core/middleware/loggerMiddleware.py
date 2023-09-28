from starlette.middleware.base import BaseHTTPMiddleware

class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        request.app.logger.info(
            "Incoming request",
            extra={
                "req": { "method": request.method, "url": str(request.url) },
                "res": { "status_code": response.status_code, },
            },
        )
        request.app.logger.info({'data': "Successfully Implemented Custom Log"})
        request.app.logger.error("Here Is Your Error Log")
        return {'data': "Successfully Implemented Custom Log"}
        # return response