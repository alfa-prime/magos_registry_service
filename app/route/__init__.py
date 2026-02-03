from fastapi import APIRouter

from .health import router as health_router
from .patient import router as patient_router
from .registry import router as registry_route
from .timetable import router as timetable_router
from .assist import router as assist_router

router = APIRouter()
router.include_router(health_router)
router.include_router(patient_router)
router.include_router(registry_route)
router.include_router(timetable_router)
router.include_router(assist_router)


__all__ = ["router"]
