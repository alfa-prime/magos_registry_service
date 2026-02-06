import time
import uuid
from fastapi import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from app.core.logger_config import logger
from app.core import settings


async def _clone_response_with_body(response: Response) -> tuple[bytes, Response]:
    body = b""
    async for chunk in response.body_iterator:
        body += chunk
    new_response = Response(
        content=body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
        background=response.background,
    )
    return body, new_response


def _preview_bytes(data: bytes, limit: int = 2000) -> str:
    if not data:
        return ""
    s = data.decode("utf-8", errors="replace")
    if len(s) > limit:
        return s[:limit] + "…(truncated)"
    return s


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
        start = time.perf_counter()

        body_preview = None
        if settings.DEBUG_ROUTE:
            raw_body = await request.body()

            async def receive():
                return {"type": "http.request", "body": raw_body}

            request._receive = receive  # Подменяем метод получения данных

            body_preview = _preview_bytes(raw_body)

            logger.debug(
                f"[REQ] -> {request.method} {request.url.path} rid={request_id} "
                f"query={dict(request.query_params)} body={body_preview}"
            )

        try:
            response: Response = await call_next(request)
        except Exception as exc:
            duration_ms = int((time.perf_counter() - start) * 1000)
            logger.exception(
                f"[REQ] {request.method} {request.url.path} rid={request_id} {duration_ms}ms: {exc}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "internal_error",
                    "request_id": request_id,
                    "detail": "Internal server error",
                },
            )

        duration_ms = int((time.perf_counter() - start) * 1000)

        if settings.DEBUG_ROUTE:
            body, response = await _clone_response_with_body(response)
            logger.debug(
                f"[REQ] <- {request.method} {request.url.path} rid={request_id} "
                f"status={response.status_code} {duration_ms}ms resp={_preview_bytes(body)}"
            )
        else:
            logger.info(
                f"[REQ] {request.method} {request.url.path} rid={request_id} "
                f"-> {response.status_code} {duration_ms}ms"
            )

        response.headers["X-Request-Id"] = request_id
        return response
