import io
import itertools
import logging
import re

import geopandas as gpd
from fastapi import APIRouter, UploadFile, status
from shapely import Point

from ..run.schemas import DriverScoreOutSchema
from ..run.service import RunService
from .enums import DrivingDirection
from .schema import RouteBasedRCSchema
from .service import RouteService

router = APIRouter(dependencies=[])
logger = logging.getLogger(__name__)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload(file: UploadFile):
    route_id = file.filename.split(".")[0]
    service = RouteService(route_id=route_id)

    dissolved_route_file_obj = io.BytesIO(file.file.read())
    await service.persist_route_to_db(dissolved_route_file_obj)


# TODO: Fix the api endpoint later
@router.post("/curves/upload", status_code=status.HTTP_201_CREATED)
async def curve_upload(file: UploadFile):
    regex = r"(?P<route_id>\w+)_curves.geojson"
    if match := re.search(regex, file.filename):
        route_id = match.group("route_id")
    else:
        return {"message": "File name is not in the expected format. Expected format: <route_id>_curves.geojson"}

    service = RouteService(route_id=route_id)
    await service.persist_curves_to_db(curves_bin=await file.read())


@router.get("/{run_id}", response_model=dict[DrivingDirection, list[RouteBasedRCSchema]])
async def get_RCs(run_id: str) -> dict[DrivingDirection, list[RouteBasedRCSchema]]:
    """
    Get the road characteristics for a specific run.

    Parameters:
        run_id (str): The ID of the run.

    Returns:
        list[RoadCharacteristicSchema]: A list of road characteristics for the run.
    """
    # Building a score GeoDataFrame
    driver_scores = await RunService(run_id).get_scores_by_direction()

    def get_score_gdf_with_direction(
        driver_scores: dict[DrivingDirection, DriverScoreOutSchema], direction: DrivingDirection
    ) -> gpd.GeoDataFrame:
        driver_scores_with_direction = driver_scores[direction]
        scores = driver_scores_with_direction.properties.scores
        timestamps = driver_scores_with_direction.properties.timestamps
        geometry = [Point(coordinate) for coordinate in driver_scores_with_direction.geometry.coordinates]

        # TODO: Testing using pd.explode() later
        score_gdf = gpd.GeoDataFrame(
            data={
                "geometry": geometry,
                "score": scores,
                "timestamp": timestamps,
                "direction": [direction] * len(scores),
            },
            crs="EPSG:4326",
        )
        return score_gdf

    scores_inc_direction_gdf = get_score_gdf_with_direction(
        driver_scores=driver_scores, direction=DrivingDirection.INCREASING
    )
    scores_dec_direction_gdf = get_score_gdf_with_direction(
        driver_scores=driver_scores, direction=DrivingDirection.DECREASING
    )

    # Get road characteristics given the score GeoDataFrame
    # TODO: Mock
    route_id = "SR11"
    route_service = RouteService(route_id=route_id)
    inc_RCs = await route_service.get_route_based_RCs(score_gdf=scores_inc_direction_gdf)
    dec_RCs = await route_service.get_route_based_RCs(score_gdf=scores_dec_direction_gdf)
    return {DrivingDirection.INCREASING: inc_RCs, DrivingDirection.DECREASING: dec_RCs}
