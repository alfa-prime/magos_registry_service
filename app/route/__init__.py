from fastapi import APIRouter
from .health import router as health_router
from .debug import router as debug_router
from .registry import router as registry_route
from .service import router as service_router

router = APIRouter()
router.include_router(health_router)
router.include_router(debug_router)
router.include_router(registry_route)
router.include_router(service_router)

__all__ = ["router"]
