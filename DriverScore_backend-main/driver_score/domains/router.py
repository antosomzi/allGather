from fastapi import APIRouter

from driver_score.settings import settings

from .allgather.api import router as allgather_router
from .driver.api import router as driver_router
from .route.api import router as route_router
from .run.api import router as run_router
from .summary.api import router as summary_router

v1_api_router = APIRouter(prefix=settings.API_V1_STR)
v1_api_router.include_router(allgather_router, prefix="/allgather", tags=["AllGather"])
v1_api_router.include_router(driver_router, prefix="/drivers", tags=["Drivers"])
v1_api_router.include_router(run_router, prefix="/runs", tags=["Runs"])
v1_api_router.include_router(route_router, prefix="/routes", tags=["Routes"])
v1_api_router.include_router(summary_router, prefix="/summary", tags=["Summary"])

# We can specify routers for /api/v2 here:
# v2_api_router = APIRouter(prefix=settings.API_V2_STR)
# ...
