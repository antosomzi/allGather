from fastapi import APIRouter

from ..run.schemas import RunSchema
from .service import DriverService

router = APIRouter(dependencies=[])


@router.get("/{driver_id}/runs", response_model=list[RunSchema], tags=["Runs"])
async def get_runs(driver_id: int) -> list[RunSchema]:
    """
    Get runs for a specific driver or all runs.

    - **driver_id** (optional): The ID of the driver to filter runs by.

    Returns a list of runs.
    """
    runs = await DriverService(driver_id).get_runs()
    return runs
