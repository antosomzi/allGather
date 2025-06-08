import itertools
from datetime import datetime

import geopandas as gpd
import numpy as np
import orjson
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype
from pydantic_geojson import LineStringModel
from pyproj import Geod
from scipy.interpolate import interp1d
from shapely import LineString, Point
from sqlalchemy import func, select

from driver_score.core.database import get_db_session
from driver_score.core.models import GpsSample, ImuSample, RoadCharacteristic, Run, Score
from driver_score.domains.route.curve.service import RouteSpline

from ..allgather.schemas import GpsSampleSchema, ImuSampleSchema
from ..route.service import RouteService
from .schemas import DriverScoreOutSchema, DriverScorePropertiesSchema, RunBasedRCSchema, RunSchema


class RunService:
    def __init__(self, run_id: str, route_id: str = "SR11"):
        self.run_id = run_id
        self.route_id = route_id

    @staticmethod
    async def get_runs() -> list[RunSchema]:
        with get_db_session() as session:
            runs = session.query(Run).all()
            return [RunSchema.model_validate(run) for run in runs]

    async def get_run(self) -> RunSchema:
        with get_db_session() as session:
            filters = [
                Run.run_id == self.run_id if self.run_id is not None else True,
                # TODO: self.run_id is None or Run.run_id == self.run_id
            ]
            run = session.query(Run).filter(*filters).first()
            return RunSchema.model_validate(run)

    async def persist_run_to_db(self, driver_id: int, start_time: datetime) -> None:
        """
        Persist a run to the database once having driver_id and start_time.

        Parameters:
            driver_id (int): The ID of the driver.
            start_time (datetime): The start time of the run.

        Returns:
            None
        """
        with get_db_session() as session:
            run = Run(driver_id=driver_id, run_id=self.run_id, start_time=start_time)
            session.add(run)

    async def get_gps_samples(self) -> list[GpsSampleSchema]:
        with get_db_session() as session:
            gps_points = session.query(GpsSample).filter(GpsSample.run_id == self.run_id).all()
            gps_points = [GpsSampleSchema.model_validate(gps_point) for gps_point in gps_points]
            return gps_points

    async def get_gps_samples_by_direction(self) -> dict[str, list[GpsSampleSchema]]:
        """
        Query the database for GPS samples linked to the current run ID and validate each sample using GpsSampleSchema.

        Returns:
            list[GpsSampleSchema]: A list of validated GPS samples.
        """
        gps_points = await self.get_gps_samples()
        gps_points_by_direction = await self._get_gps_schemas_with_direction(gps_points)
        return gps_points_by_direction

    async def get_imu_samples(self) -> list[ImuSampleSchema]:
        with get_db_session() as session:
            # Get imu data and gps data first
            imu_points = session.query(ImuSample).filter(ImuSample.run_id == self.run_id).all()
            imu_points = [ImuSampleSchema.model_validate(imu_point).model_dump() for imu_point in imu_points]
            imu_df = pd.DataFrame.from_records(imu_points, index="timestamp")

            # Get all gps samples sorted by timestamp
            gps_samples = await self.get_gps_samples()
            gps_samples = sorted(gps_samples, key=lambda gps_sample: gps_sample.timestamp)
            gps_timestamps = pd.Series([gps_sample.timestamp for gps_sample in gps_samples])

            # Downsample imu data to gps timestamps
            downsampled_imu_df = pd.DataFrame(index=gps_timestamps.values, columns=imu_df.columns)
            for column in imu_df.columns:
                resampled_data = self._interpolate_time_series(
                    old_time=imu_df.index.values, data=imu_df[column], new_time=gps_timestamps
                )
                downsampled_imu_df[column] = resampled_data

            # Convert back to list of ImuSampleSchema for response
            downsampled_imu_points = [
                ImuSampleSchema.model_validate({"timestamp": timestamp, **dict(downsampled_imu_point)})
                for (timestamp, downsampled_imu_point) in zip(
                    downsampled_imu_df.index.to_pydatetime(),
                    downsampled_imu_df.to_dict("records"),
                    strict=True,
                )
            ]
            return downsampled_imu_points

    async def get_imu_samples_by_direction(self) -> dict[str, list[ImuSampleSchema]]:
        """
        Query the database for IMU samples linked to the current run ID and validate each sample using ImuSampleSchema.

        Returns:
            list[ImuSampleSchema]: A list of validated IMU samples.
        """
        downsampled_imu_samples = await self.get_imu_samples()
        gps_samples = await self.get_gps_samples()
        downsampled_imu_samples_by_direction = await self._get_imu_schemas_with_direction(
            points=downsampled_imu_samples, gps_points=gps_samples
        )

        return downsampled_imu_samples_by_direction

    async def _get_gps_schemas_with_direction(
        self, gps_points: list[GpsSampleSchema]
    ) -> dict[str, list[GpsSampleSchema]]:
        # TODO: Fix duplicate code
        gps_df = pd.DataFrame.from_records([gps_point.model_dump() for gps_point in gps_points], index="timestamp")
        geometry = gpd.points_from_xy(gps_df["longitude"], gps_df["latitude"])
        gps_gdf = gpd.GeoDataFrame(gps_df, geometry=geometry, crs="EPSG:4326")

        centerline = await RouteService(self.route_id).get_route(self.route_id)
        gps_gdf["direction"] = self._compute_direction(gps_gdf, centerline=centerline)

        # We remove the "direction" attribute from each record
        def _remove_key(samples: list[dict], key: str):
            return [{k: v for k, v in sample.items() if k != key} for sample in samples]

        tmp = {
            k: _remove_key(g.to_dict(orient="records", index=True), key="direction")
            for k, g in gps_gdf.reset_index().groupby("direction")
        }
        increasing, decreasing = self._get_increasing_and_decreasing(tmp)
        return {"increasing": increasing[1], "decreasing": decreasing[1]}

    async def _get_imu_schemas_with_direction(
        self, points: list[ImuSampleSchema], gps_points: list[GpsSampleSchema]
    ) -> dict[str, list[ImuSampleSchema]]:
        # TODO: Fix duplicate code
        # Get directions using GPS
        gps_df = pd.DataFrame.from_records([gps_point.model_dump() for gps_point in gps_points], index="timestamp")
        geometry = gpd.points_from_xy(gps_df["longitude"], gps_df["latitude"])
        gps_gdf = gpd.GeoDataFrame(gps_df, geometry=geometry, crs="EPSG:4326")

        centerline = await RouteService(self.route_id).get_route(self.route_id)

        # Points
        df = pd.DataFrame.from_records([imu_point.model_dump() for imu_point in points], index="timestamp")
        df["direction"] = self._compute_direction(gps_gdf, centerline=centerline)

        # We remove the "direction" attribute from each record
        def _remove_key(samples: list[dict], key: str):
            return [{k: v for k, v in sample.items() if k != key} for sample in samples]

        tmp = {
            k: _remove_key(g.to_dict(orient="records", index=True), key="direction")
            for k, g in df.reset_index().groupby("direction")
        }

        increasing, decreasing = self._get_increasing_and_decreasing(tmp)
        return {"increasing": increasing[1], "decreasing": decreasing[1]}

    async def get_scores(self) -> DriverScoreOutSchema:
        with get_db_session() as session:
            query = (
                select(
                    GpsSample.timestamp,
                    func.ST_AsGeoJson(GpsSample.geometry).label("geometry"),
                    Score.score,
                    RoadCharacteristic.gps_lrs,
                )
                .select_from(GpsSample)
                .outerjoin(Score, (GpsSample.run_id == Score.run_id) & (GpsSample.timestamp == Score.timestamp))
                .outerjoin(
                    RoadCharacteristic,
                    (GpsSample.run_id == RoadCharacteristic.run_id)
                    & (GpsSample.timestamp == RoadCharacteristic.timestamp),
                )
                .where(GpsSample.run_id == self.run_id)
            )

            result = session.execute(query).all()
            timestamps, geometries, scores, lrs = zip(*result, strict=False)
            coordinates = [orjson.loads(geometry)["coordinates"] for geometry in geometries]

            driver_id = (await self.get_run()).driver_id

            # TODO: Investigate why lrs is None at the beginning and the end
            return DriverScoreOutSchema(
                geometry=LineStringModel(coordinates=coordinates),
                properties=DriverScorePropertiesSchema(
                    driver_id=driver_id, timestamps=timestamps, scores=scores, lrs=lrs
                ),
            )

    async def get_scores_by_direction(self) -> dict[str, DriverScoreOutSchema]:
        scoresSchema = await self.get_scores()
        timestamps = scoresSchema.properties.timestamps
        scores = scoresSchema.properties.scores
        lrs = scoresSchema.properties.lrs
        coordinates = scoresSchema.geometry.coordinates

        score_gdf = gpd.GeoDataFrame(
            {
                "timestamp": timestamps,
                "geometry": [Point(coordinate) for coordinate in coordinates],
                "score": scores,
                "lrs": lrs,
            },
            crs="EPSG:4326",
        ).set_index("timestamp")

        driver_id = (await self.get_run()).driver_id
        score_gdf["driver_id"] = driver_id

        gps_samples = itertools.chain.from_iterable((await self.get_gps_samples_by_direction()).values())
        gps_samples = sorted(gps_samples, key=lambda gps_sample: gps_sample["timestamp"])
        driver_scores_by_direction = await self._get_scores_schemas_with_direction(df=score_gdf, gps_points=gps_samples)
        return driver_scores_by_direction

    async def _get_scores_schemas_with_direction(
        self, df: gpd.GeoDataFrame, gps_points: list[GpsSampleSchema]
    ) -> dict[str, DriverScoreOutSchema]:
        # TODO: Fix duplicate code
        # Get directions using GPS
        gps_df = pd.DataFrame.from_records(gps_points, index="timestamp")
        geometry = gpd.points_from_xy(gps_df["longitude"], gps_df["latitude"])
        gps_gdf = gpd.GeoDataFrame(gps_df, geometry=geometry, crs="EPSG:4326")

        centerline = await RouteService(self.route_id).get_route(self.route_id)

        # Score points
        df["direction"] = self._compute_direction(gps_gdf, centerline=centerline)

        # We remove the "direction" attribute from each record
        def _remove_key(samples: list[dict], key: str):
            return [{k: v for k, v in sample.items() if k != key} for sample in samples]

        tmp = {
            direction: _remove_key(samples.to_dict(orient="records", index=True), key="direction")
            for direction, samples in df.reset_index().groupby("direction")
        }

        def _samples_to_schema(samples: list[dict]) -> DriverScoreOutSchema:
            driver_id = samples[0]["driver_id"]
            timestamps = [sample["timestamp"] for sample in samples]
            scores = [sample["score"] for sample in samples]
            lrs = [sample["lrs"] for sample in samples]

            sub_schema = DriverScorePropertiesSchema(driver_id=driver_id, timestamps=timestamps, scores=scores, lrs=lrs)
            geometries = LineStringModel(coordinates=[sample["geometry"].coords[0] for sample in samples])
            return DriverScoreOutSchema(properties=sub_schema, geometry=geometries)

        increasing, decreasing = self._get_increasing_and_decreasing(tmp)
        return {"increasing": _samples_to_schema(increasing[1]), "decreasing": _samples_to_schema(decreasing[1])}

    async def get_run_based_RCs(self) -> list[RunBasedRCSchema]:
        """
        Return run-based RCs.
        This is more granular (per sample) and different from route-based RCs (per curve/tangent/intersection/etc).

        Args:
            run_id (str): _description_
        """
        route_centerline = await RouteService(self.route_id).get_route(self.route_id)
        route_spline = RouteSpline(route_geom=route_centerline)
        # # TODO: Mock
        # curve_gdf = gpd.read_file("data/SR11_curves.geojson", driver="GeoJSON")
        # curve_gdf.set_crs(
        #     epsg=4326, inplace=True
        # )  # for some reason the crs is not being read from the GeoJSON, thus setting it manually
        # curve_gdf.to_crs(2239, inplace=True)

        # route_gdf = gpd.read_file("data/SR11.shp")
        # route_gdf.to_crs(
        #     2239, inplace=True
        # )  # converting crs to feet, this is important for the spline radius results to be in feet as well, curvature will be in 1/ft
        # route_centerline = route_gdf.geometry[0]
        # route_spline = RouteSpline(route_centerline)

        scores_by_direction = await RunService(self.run_id).get_scores_by_direction()

        def _get_curvature_closest_curve_to_point(point: Point, curve_gdf: gpd.GeoDataFrame) -> float:
            distances = curve_gdf.geometry.distance(point)
            # Find the index of the row with the smallest distance
            closest_row_index = distances.idxmin()

            # Get the closest row
            closest_row = curve_gdf.loc[closest_row_index]

            return 1 / closest_row.c_radius

        # Flatten scores_by_direction and convert to list of RunBasedRCSchema
        run_based_RCs: list[RunBasedRCSchema] = []
        for direction, scores in scores_by_direction.items():
            timestamps = scores.properties.timestamps
            coordinates = scores.geometry.coordinates
            coordinates_in_feet = (
                gpd.GeoDataFrame(geometry=[Point(c.lon, c.lat) for c in coordinates], crs="EPSG:4326")
                .to_crs(2239)
                .geometry
            )

            for timestamp, gps_sample in zip(timestamps, coordinates_in_feet, strict=True):
                run_based_RC = RunBasedRCSchema(
                    run_id=self.run_id,
                    timestamp=timestamp,
                    dissolved_id=self.route_id,
                    gps_lrs=route_centerline.project(gps_sample),
                    driving_direction=direction,
                    curvature=route_spline.get_curveature_at_point(gps_sample),
                )
                run_based_RCs.append(run_based_RC)

        return run_based_RCs

    async def persist_run_based_RCs_to_db(self):
        """Persist run-based RCs to the road_chracteristics table."""
        with get_db_session() as session:
            run_based_RCs = await self.get_run_based_RCs()
            session.add_all([RoadCharacteristic(**run_based_RC.model_dump()) for run_based_RC in run_based_RCs])

    def _get_increasing_and_decreasing(self, tmp):
        # TODO: Clean this complicated code
        increasing = sorted(
            [(direction, val) for direction, val in tmp.items() if direction.startswith("increasing")],
            key=lambda x: len(x[1]),
            reverse=True,
        )[0]
        decreasing = sorted(
            [(direction, val) for direction, val in tmp.items() if direction.startswith("decreasing")],
            key=lambda x: len(x[1]),
            reverse=True,
        )[0]

        return increasing, decreasing

    def _compute_direction(self, gps_gdf: gpd.GeoDataFrame, centerline: LineString) -> pd.Series:
        """
        Computes the direction of the trajectory based on consecutive LRS values.

        Parameters:
        - gps_gdf: A GeoDataFrame with the GPS points. The index is assumed to be a timestamp.
        - centerline: A LineString representing the roadway centerline

        Returns:
        A Series of 'increasing', 'decreasing', or 'stationary' values.

        """

        def _compute_LRS(gdf: gpd.GeoDataFrame | gpd.GeoSeries, centerline: LineString):
            """
            Project data in GeoDataFrame on to a LineString to compute the linear reference distance for the data
            """
            return gdf.apply(lambda row: centerline.project(row.geometry, normalized=True), axis=1)

        LRS_values = _compute_LRS(gps_gdf, centerline)
        geod = Geod(ellps="WGS84")

        # Default to stationary for the first point
        directions = ["stationary 1"]
        current_direction = "stationary"
        count_by_direction = {"increasing": 1, "decreasing": 1, "stationary": 1}

        for i in range(1, len(LRS_values)):
            start_point = gps_gdf.geometry.iloc[i - 1]
            end_point = gps_gdf.geometry.iloc[i]

            if isinstance(gps_gdf.index, pd.DatetimeIndex):
                # Calculate time difference between consecutive points in seconds
                time_delta = (gps_gdf.index[i] - gps_gdf.index[i - 1]).total_seconds()
            else:
                time_delta = 1

            # Calculate distance between consecutive points
            _, _, distance = geod.inv(start_point.x, start_point.y, end_point.x, end_point.y)

            # Dynamic threshold based on time difference
            threshold = 0.5 * time_delta  # 0.5 meters/second * elapsed seconds

            next_direction = ""
            # Check for stationary condition
            if distance <= threshold:
                next_direction = "stationary"
            elif LRS_values.iloc[i] > LRS_values.iloc[i - 1]:
                next_direction = "increasing"
            else:
                next_direction = "decreasing"

            if next_direction != current_direction:
                count_by_direction[current_direction] += 1

            current_direction = next_direction
            counter = count_by_direction[current_direction]
            directions.append(f"{current_direction} {counter}")

        return pd.Series(directions, index=gps_gdf.index)

    def _interpolate_time_series(self, old_time: pd.Series, data: pd.Series, new_time: pd.Series) -> np.ndarray:
        """
        Author: Lucas Yu
        Interpolates time series data to align with a new time series.

        Parameters:
        old_time (pd.Series): Original time series (must be of datetime dtype).
        data (pd.Series): Data series corresponding to the old_time series.
        new_time (pd.Series): New time series to which data will be interpolated (must be of datetime dtype).

        Returns:
        np.ndarray: Interpolated data corresponding to the new_time series.

        Note:
        This function uses linear interpolation to fill in the data for the new_time series.
        If new_time contains points outside the range of old_time, the function will use the first and last values of data to fill in these points.
        """
        # Check if old_time and new_time are datetime dtype
        if is_datetime64_any_dtype(old_time) and is_datetime64_any_dtype(new_time):
            new_time = new_time.astype(np.int64) // 10**6
            old_time = old_time.astype(np.int64) // 10**6

        # If not datetime dtype, raise an error
        else:
            raise ValueError("Both old_time and new_time must be of datetime dtype.")

        f = interp1d(old_time, data, bounds_error=False, fill_value=(data.iloc[0], data.iloc[-1]))
        resampled_data = f(new_time)

        return resampled_data
