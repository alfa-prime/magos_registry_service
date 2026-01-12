import httpx
from typing import Union
from app.core import settings
from app.core.decorators import log_and_catch


class GatewayService:
    def __init__(self, client: httpx.AsyncClient):
        self._client = client

    @log_and_catch()
    async def _base_request(
        self, method: str, url: str, is_json_response: bool, **kwargs
    ) -> Union[dict, str]:
        """
        Внутренний универсальный метод.
        """
        if not hasattr(self._client, method.lower()):
            raise ValueError(f"Неподдерживаемый HTTP метод: {method}")

        http_method_func = getattr(self._client, method.lower())

        # Выполняем запрос
        response = await http_method_func(url=url, **kwargs)
        response.raise_for_status()

        if is_json_response:
            return response.json() if response.content else {}
        return response.text

    async def request_json(self, method: str = "POST", **kwargs) -> dict:
        """
        Выполняет запрос к JSON-эндпоинту.
        """
        return await self._base_request(
            method=method,
            url=settings.GATEWAY_JSON_REQUEST_ENDPOINT,
            is_json_response=True,
            **kwargs,
        )

    async def request_html(self, method: str = "POST", **kwargs) -> str:
        """
        Выполняет запрос к HTML-эндпоинту.
        """
        return await self._base_request(
            method=method,
            url=settings.GATEWAY_HTML_REQUEST_ENDPOINT,
            is_json_response=False,
            **kwargs,
        )
