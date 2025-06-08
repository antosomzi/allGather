import io
from pathlib import Path

import geoalchemy2
import geopandas as gpd
import numpy as np
from pydantic_geojson import LineStringModel
from shapely.geometry import LineString, Point

from driver_score.core.database import db_engine, get_db_session
from driver_score.core.models import CurveInventory, DissolvedRoute
from driver_score.settings import settings

from .curve.service import CurveService, RouteSpline
from .schema import RcType, RouteBasedRCSchema

# TODO: Move this one to app.py, specify the reason is that it supports BytesCollection interface
# to construct a GeoDataFrame from .zip file of .shp and .shx file
if settings.GEOPANDAS_ENGINE == "fiona":
    import fiona
else:
    raise ImportError(f"Support for geopandas engine {settings.GEOPANDAS_ENGINE} not implemented")


class RouteService:
    def __init__(self, route_id: str):
        self.route_id = route_id

    async def persist_route_to_db(self, dissolved_route_obj: io.BytesIO):
        """
        Asynchronously persists a dissolved route object to the database.

        Args:
            dissolved_route_obj (io.BytesIO): The dissolved route object to be persisted.

        Returns:
            None

        This function retrieves a GeoDataFrame from the given BytesIO object using the _get_gdf_from_bytes_obj method.
        It then persists the GeoDataFrame to the "dissolved_route" table in the database using the to_postgis method.

        Example:
            >>> await persist_route_to_db(dissolved_route_obj)
        """

        def _get_gdf_from_bytes_obj(bytes_obj: io.BytesIO):
            with fiona.BytesCollection(bytes_obj.read()) as src:
                crs = "EPSG:4326"
                gdf: gpd.GeoDataFrame = gpd.GeoDataFrame.from_features(src, crs=crs)
                # gdf = self._route_to_points(gdf)
                gdf["dissolved_id"] = self.route_id
                return gdf

        route_gdf = _get_gdf_from_bytes_obj(dissolved_route_obj)[["geometry", "dissolved_id"]]
        route_gdf.to_postgis("dissolved_route", db_engine, if_exists="append", index=False)

    async def persist_curves_to_db(self, curves_bin: bytes) -> None:
        curve_service = CurveService()
        curve_gdf = curve_service.get_gdf_from_geojson(io.BytesIO(curves_bin))

        route_id = curve_gdf["dissolved_id"].iloc[0]
        route = await self.get_route(route_id)
        curve_gdf["pc_lrs"] = curve_gdf.apply(lambda x: route.project(Point(x.c_pc_x, x.c_pc_y)), axis=1)
        curve_gdf["pt_lrs"] = curve_gdf.apply(lambda x: route.project(Point(x.c_pt_x, x.c_pt_y)), axis=1)

        curve_gdf = curve_gdf[
            [
                "dissolved_id",
                "c_type",
                "c_radius",
                "c_devangle",
                "c_length",
                "c_pc_x",
                "c_pc_y",
                "c_pt_x",
                "c_pt_y",
                "pc_lrs",
                "pt_lrs",
                "geometry",
            ]
        ]
        curve_gdf.to_postgis("curve_inventory", db_engine, if_exists="append", index=False)

    async def persist_route_based_RCs_to_fb(self, score_gdf: gpd.GeoDataFrame) -> None:
        pass

    async def get_route(self, route_id: str) -> LineString:
        with get_db_session() as session:
            route = session.query(DissolvedRoute).filter(DissolvedRoute.dissolved_id == route_id).first()
            return geoalchemy2.shape.to_shape(route.geometry)

    # TODO: Make return consistent by always using pydantic schemas instead
    async def get_curves(self, route_id: str) -> gpd.GeoDataFrame:
        with get_db_session() as session:
            curves = session.query(CurveInventory).filter(CurveInventory.dissolved_id == route_id).all()
            gdf = gpd.GeoDataFrame(
                [{c.key: getattr(curve, c.key) for c in curve.__table__.columns} for curve in curves]
            )
            return gdf

    async def get_route_based_RCs(self, score_gdf: gpd.GeoDataFrame) -> list[RouteBasedRCSchema]:
        def _interpolate_points(line: LineString, num_points: int) -> LineString:
            """
            Interpolates num_points more points between 2 consecutive points along a line.
            """
            distances = [i / (num_points + 1) for i in range(1, num_points + 1)]
            interpolated_points = []
            for i in range(len(line.coords) - 1):
                segment = LineString([line.coords[i], line.coords[i + 1]])
                segment_length = segment.length
                segment_distances = [dist * segment_length for dist in distances]
                segment_points = [segment.interpolate(dist) for dist in segment_distances]
                interpolated_points.extend(segment_points)
            interpolated_points.append(line.coords[-1])
            return LineString(interpolated_points)

        route = await self.get_route(self.route_id)
        route = _interpolate_points(route, num_points=5)
        route_points = [Point(coord) for coord in route.coords]

        route_gdf = gpd.GeoDataFrame(geometry=route_points, crs="EPSG:4326")
        route_gdf["lrs"] = [route.project(point) for point in route_points]

        curve_gdf = await self.get_curves(self.route_id)
        curve_gdf.sort_values(by="pc_lrs", inplace=True)

        # Update score_gdf with their curvature
        # TODO: Convert to feet as suggested in the curve service
        spline_model = RouteSpline(LineString(route_gdf.geometry.tolist()))
        score_gdf["curvature"] = score_gdf.geometry.apply(spline_model.get_curveature_at_point)

        def _get_score_in_RC(curve_geo: LineString, score_gdf: gpd.GeoDataFrame) -> float:
            """
            Calculate the score within the buffer of a given LineString curve.

            Args:
                curve_geo (LineString): The LineString curve geometry.
                score_gdf (gpd.GeoDataFrame): The GeoDataFrame containing the scores.

            Returns:
                float: The mean score within the buffered curve. If the mean score is NaN, it returns 0.
            """
            buffer_distance = settings.BUFFER_DISTANCE
            buffered_curve_geo = curve_geo.buffer(buffer_distance)
            indices = score_gdf.sindex.query(buffered_curve_geo)

            if len(indices) == 0:
                score_in_curve = 0
            else:
                scores = score_gdf.loc[indices, "score"]
                score_in_curve = max(0, min(100, int(np.sum(scores) / len(scores))))

            return score_in_curve

        # Filter curves
        curves, counter = [], 0
        for row in curve_gdf.itertuples():
            curve = route_gdf.loc[route_gdf["lrs"].between(row.pc_lrs, row.pt_lrs, inclusive="both"), "geometry"]
            curve_geo = LineString(curve)
            score_in_curve = _get_score_in_RC(curve_geo, score_gdf)
            counter += 1

            curve_rc = RouteBasedRCSchema(
                type=RcType.CURVE,
                id=counter,
                score=score_in_curve,
                geometry=LineStringModel(coordinates=[coord[:2] for coord in curve_geo.coords]),
            )
            curves.append(curve_rc)

        # Filter tangents
        curve_gdf["pc_lrs"] = curve_gdf["pc_lrs"].shift(periods=-1)
        tangents, counter = [], 0
        for row in curve_gdf.itertuples():
            if row.pc_lrs is None:
                continue

            tangent = route_gdf.loc[route_gdf["lrs"].between(row.pt_lrs, row.pc_lrs, inclusive="both"), "geometry"]
            if tangent.shape[0] in {0, 1}:
                continue

            tangent_geo = LineString(tangent)
            score = _get_score_in_RC(tangent_geo, score_gdf)
            counter += 1

            tangent_rc = RouteBasedRCSchema(
                type=RcType.TANGENT,
                id=counter,
                score=score,
                geometry=LineStringModel(coordinates=[coord[:2] for coord in tangent_geo.coords]),
            )
            tangents.append(tangent_rc)

        return [*curves, *tangents]


if __name__ == "__main__":
    route_shp_file = Path("data") / "SR190.shp"
    curve_geojson_file = Path("data") / "SR190_curves.geojson"
    service = RouteService(route_id="SR190")
    service.get_route_based_RCs(route_shp_file, curve_geojson_file)

    # def project(self, route_shp_file: Path, curve_geojson_file: Path):
    #     route_gdf = self.get_gdf_from_shp(route_shp_file)
    #     curve_gdf = CurveService().get_gdf_from_geojson(curve_geojson_file)
    #     curves = curve_gdf.geometry

    #     def _nearest_curve_idx_and_dist(point: Point, curves: gpd.GeoSeries):
    #         nearest = min(curves, key=lambda ls: point.distance(ls))
    #         distance = point.distance(nearest)
    #         nearest_idx = curves[curves == nearest].index[0]
    #         return nearest_idx, distance

    #     c_ids = [None] * route_gdf.shape[0]
    #     tangent_id = -1
    #     for idx, point in route_gdf.iterrows():
    #         nearest_idx, dist = _nearest_curve_idx_and_dist(point.geometry, curves)
    #         if dist < 0.001:
    #             c_id = curve_gdf.iloc[nearest_idx].c_id
    #         else:
    #             c_id = tangent_id
    #             tangent_id -= 1

    #         c_ids[idx] = c_id

    #     route_gdf["curve_id"] = c_ids
    #     print(route_gdf)
    #     linestrings = route_gdf.groupby("curve_id")["geometry"].apply(
    #         lambda x: LineString(x.tolist())
    #     )
    #     result_gdf = gpd.GeoDataFrame(linestrings, columns=["geometry"])
    #     result_gdf.reset_index(inplace=True)
    #     result_gdf["curve_id"] = result_gdf["curve_id"].astype(int)
    #     print(result_gdf)
    #     return result_gdf

    # def _get_gdf_from_shp(self, shape_file: Path):
    #     route_gdf: gpd.GeoDataFrame = gpd.read(shape_file, engine=settings.GEOPANDAS_ENGINE)
    #     route_gdf = self._route_to_points(route_gdf)
    #     return route_gdf
