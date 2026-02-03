import httpx
from fastapi import FastAPI

from app.core import logger, settings


async def init_gateway_client(app: FastAPI):
    """
    Создает экземпляр HTTPX клиента и сохраняет его в app.state.
    """
    gateway_client = httpx.AsyncClient(
        base_url=settings.GATEWAY_URL,
        headers={
            "X-API-KEY": settings.GATEWAY_API_KEY,
            "X-Session-ID": settings.GATEWAY_SESSION_ID,
        },
        timeout=settings.REQUEST_TIMEOUT,
    )
    app.state.gateway_client = gateway_client
    logger.info(f"Gateway client initialized for base_url: {settings.GATEWAY_URL}")


async def shutdown_gateway_client(app: FastAPI):
    """
    Закрывает HTTPX клиент.
    """
    if hasattr(app.state, "gateway_client"):
        await app.state.gateway_client.aclose()
        logger.info("Gateway client closed.")
