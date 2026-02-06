import httpx
from httpx import HTTPStatusError, RequestError
from fastapi import HTTPException, status
from typing import Union, Any
from app.core import settings
from app.core.logger_config import logger


class GatewayService:
    def __init__(self, client: httpx.AsyncClient):
        self._client = client

    async def _base_request(
        self, method: str, url: str, is_json_response: bool, **kwargs
    ) -> Union[dict, str]:
        """
        Внутренний универсальный метод.
        """
        if not hasattr(self._client, method.lower()):
            raise ValueError(f"Неподдерживаемый HTTP метод: {method}")

        http_method_func = getattr(self._client, method.lower())

        try:
            # Выполняем запрос
            response = await http_method_func(url=url, **kwargs)
            # Если шлюз вернул 4xx или 5xx, httpx выбросит исключение здесь
            response.raise_for_status()

            if is_json_response:
                return response.json() if response.content else {}
            return response.text

        except HTTPStatusError as exc:
            # Это ошибки типа 401, 403, 500 от ШЛЮЗА
            status_code = exc.response.status_code
            error_text = exc.response.text

            logger.error(f"[GATEWAY] Шлюз вернул ошибку {status_code} на запрос {method}. "
                         f"Возможно, слетела авторизация.")

            # Если включен дебаг, пишем детали ответа шлюза в DEBUG лог
            if settings.DEBUG_HTTP:
                logger.debug(f"[GATEWAY] Детали ответа шлюза: {error_text}")

            raise HTTPException(
                status_code=status_code,
                detail=f"Внешний шлюз сообщил об ошибке: {error_text[:200]}"
            )

        except RequestError as exc:
            # Это ошибки сети (шлюз вообще выключен или неверный IP)
            logger.critical(f"[GATEWAY] Не удалось соединиться со шлюзом: {exc}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Сервис шлюза временно недоступен. Проверьте соединение."
            )



    async def request_json(
        self, method: str = "POST", **kwargs
    ) -> list[dict[str, Any]] | dict[str, Any]:
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
