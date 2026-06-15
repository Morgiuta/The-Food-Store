from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback
import logging

logger = logging.getLogger(__name__)

from fastapi.encoders import jsonable_encoder

def register_error_handlers(app: FastAPI):
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        # Determine a title based on status code
        title = "HTTP Error"
        if exc.status_code == 404:
            title = "Not Found"
        elif exc.status_code == 400:
            title = "Bad Request"
        elif exc.status_code == 401:
            title = "Unauthorized"
        elif exc.status_code == 403:
            title = "Forbidden"
            
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "type": "about:blank",
                "title": title,
                "status": exc.status_code,
                "detail": exc.detail,
                "instance": str(request.url.path),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "type": "about:blank",
                "title": "Validation Error",
                "status": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "detail": "Invalid input data",
                "errors": jsonable_encoder(exc.errors()),
                "instance": str(request.url.path),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}")
        traceback.print_exc()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "type": "about:blank",
                "title": "Internal Server Error",
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "detail": "An unexpected error occurred",
                "instance": str(request.url.path),
            },
        )
