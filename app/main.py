from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

app.add_middleware(
    CORSMiddleware,  # noqa
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
