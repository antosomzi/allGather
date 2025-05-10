from fastapi import APIRouter

from ..allgather.schemas import GpsSampleSchema, ImuSampleSchema
from .schemas import DriverScoreOutSchema, RunSchema
from .service import RunService

router = APIRouter(dependencies=[])


@router.get("/", response_model=list[RunSchema])
async def get_runs() -> list[RunSchema]:
    """
    Get a specific run by its ID.

    - **run_id**: The ID of the run to retrieve.

    Returns the run details.
    """
    runs = await RunService.get_runs()
    return runs


@router.get("/{run_id}", response_model=RunSchema)
async def get_run(run_id: str) -> RunSchema:
    """
    Get a specific run by its ID.

    - **run_id**: The ID of the run to retrieve.

    Returns the run details.
    """
    run = await RunService(run_id).get_run()
    return run


@router.get("/{run_id}/scores", response_model=dict[str, DriverScoreOutSchema], response_model_exclude_none=False)
async def get_scores_by_direction(run_id: str) -> dict[str, DriverScoreOutSchema]:
    """
    Get the calculated driver scores for a specific run.

    - **run_id**: The ID of the run to retrieve scores for.

    Returns the calculated driver scores for the run.
    """
    scores = await RunService(run_id).get_scores_by_direction()
    return scores


@router.get("/{run_id}/gps_samples", response_model=dict[str, list[GpsSampleSchema]])
async def get_gps_samples_by_direction(run_id: str) -> dict[str, list[GpsSampleSchema]]:
    """
    Get GPS samples for a specific run ID.

    - **run_id**: The ID of the run to retrieve GPS samples for.

    Returns a list of GPS samples for the specified run ID.
    """
    gps_by_direction = await RunService(run_id).get_gps_samples_by_direction()
    return gps_by_direction


@router.get("/{run_id}/imu_samples", response_model=dict[str, list[ImuSampleSchema]])
async def get_imu_samples_by_direction(run_id: str) -> dict[str, list[ImuSampleSchema]]:
    """
    Get the IMU samples for a specific run by its ID.

    - **run_id**: The ID of the run to retrieve IMU samples for.

    Returns a list of IMU samples.
    """
    imu_by_direction = await RunService(run_id).get_imu_samples_by_direction()
    return imu_by_direction
