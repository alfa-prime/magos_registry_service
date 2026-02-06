from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.middleware import RequestLoggingMiddleware
from app.core.exceptions import http_exception_handler, validation_exception_handler

from app.core import settings, init_gateway_client, shutdown_gateway_client
from app.route import router

tags_metadata = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_gateway_client(app)
    yield
    await shutdown_gateway_client(app)


app = FastAPI(
    openapi_tags=tags_metadata,
    title="Сервис для записи на исследования в ЕВМИАС",
    description="Сервис для записи на исследования в ЕВМИАС",
    lifespan=lifespan,
    version=settings.APP_VERSION,
    swagger_ui_parameters={"persistAuthorization": True},
)

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.add_middleware(RequestLoggingMiddleware)  # noqa
app.add_middleware(
    CORSMiddleware,  # noqa
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
