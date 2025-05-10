import logging

from fastapi import APIRouter

from .schema import PivotTableByRCRangeSchema, PivotTableByRCTypeSchema
from .service import SummaryService

router = APIRouter(dependencies=[])
logger = logging.getLogger(__name__)


# TODO: Replace with query parameters instead
@router.get("/range", response_model=list[PivotTableByRCRangeSchema])
async def get_summary_by_RC_range():
    service = SummaryService()
    return await service.get_summary_by_RC_range()


@router.get("/type", response_model=list[PivotTableByRCTypeSchema])
async def get_summary_by_RC_type():
    service = SummaryService()
    return await service.get_summary_by_RC_range()
