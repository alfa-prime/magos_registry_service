from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logger_config import logger


def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # HTTPException уже “нормальная” ошибка — просто лог + единый формат
    logger.warning(f"[HTTP] {request.method} {request.url.path} {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "http_error", "detail": exc.detail},
    )


def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"[VALIDATION] {request.method} {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"error": "validation_error", "detail": exc.errors()},
    )
