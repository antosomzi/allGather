import logging

from fastapi import APIRouter, File, UploadFile, status
from tsidpy import TSID

from ..model.service import DriverScoreModelService
from ..run.service import RunService
from .service import AllGatherService

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload(file: UploadFile = File(...)):
    """
    Upload a compressed file (currently support `.zip`, `.tar` and `.tar.gz`) collected
    by AllGather app containing GPS, Calibration, Acceleration and Camera (optional)
    data for processing.

    - **file**: Compressed file collected by AllGather app (required)

    Returns:
    - **filename**: Name of the uploaded file
    - **content_type**: MIME type of the uploaded file
    - **n_gps_samples**: Number of GPS samples processed from the file
    """

    # Generate tsid for run_id
    run_id = str(TSID.create())

    # Persist smartphone data into database
    gps_service = AllGatherService(run_id=run_id)
    timestamp_folder = await gps_service.extract_and_store_file(file=file)
    await gps_service.upload_smartphone_data(filename=file.filename, timestamp_folder=timestamp_folder)

    run_service = RunService(run_id=run_id)
    gps_samples = await run_service.get_gps_samples()
    imu_samples = await run_service.get_imu_samples()

    # Calculate driver scores and update database
    ds_algo_service = DriverScoreModelService()
    driver_scores = ds_algo_service.calculate_scores(gps_samples, imu_samples)
    await ds_algo_service.persist_scores_into_db(run_id=run_id, scores=driver_scores)

    # Create run-based road characteristics and update database
    # ! TODO: run_based_RCs_to_db() must be called after persisting scores.
    # ! This is not good and need to be fixed
    await run_service.persist_run_based_RCs_to_db()

    # Return statistics after persisting data
    return {"filename": file.filename, "content_type": file.content_type, "n_gps_samples": len(gps_samples)}
