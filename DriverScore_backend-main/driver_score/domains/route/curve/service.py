import io
from pathlib import Path

import geopandas as gpd
import numpy as np
from scipy.interpolate import splev, splprep
from shapely import wkb
from shapely.geometry import LineString, Point

from driver_score.settings import settings


class CurveService:
    def __init__(self):
        pass

    def get_gdf_from_geojson(self, curves_geojson: Path | io.BytesIO) -> gpd.GeoDataFrame:
        curve_gdf: gpd.GeoDataFrame = gpd.read_file(curves_geojson, engine=settings.GEOPANDAS_ENGINE)

        curve_gdf["geometry"] = curve_gdf["geometry"].apply(lambda x: wkb.loads(wkb.dumps(x, output_dimension=2)))
        curve_gdf.rename(columns={"c_segid": "dissolved_id", "c_id": "curve_id"}, inplace=True)
        curve_gdf.set_index("curve_id", inplace=True)

        return curve_gdf


# TODO: Merge with CurveService later. Use dissolved_id from __init__ of CurveService to query route_geom
class RouteSpline:
    def __init__(self, route_geom: LineString, spline_order: int = 3, smoothing_factor: float = 3) -> None:
        """
        IMPORTANT: coordinate reference system for the route_geom MUST BE IN FEET!!!

        Fit a spline to a given route geometry and compute curvature at any point on the route.
        Parameters:
            route_geom: shapely LineString object representing the route, the coordinate reference system MUST BE IN FEET.
            spline_order: order of the spline, default is 3.
            smoothing_factor: smothing factor, float or None.If s is None, will provide a default smoothing.
                            If 0, spline will interpolate through all data points. Default is None.
        """
        self.route_geom = route_geom  # unit for the line string is assumed to be ft
        self.spline_order = spline_order
        self.smoothing_factor = smoothing_factor
        self.spline_model = None

        # densify the route
        # densified_route = self.densify_linestring(route_geom)
        densified_route = route_geom
        self.spline_model = self.fit_spline(densified_route, spline_order, smoothing_factor)

    def densify_linestring(self, line: LineString, interval=15):
        """Return a densified LineString with the max distance between points defined as interval"""
        total_length = line.length
        sample_location = np.arange(0, total_length, interval)
        point_list = [line.interpolate(location) for location in sample_location]

        # make linestring from list of points
        return LineString(point_list)

    def fit_spline(self, line: LineString, spline_order: int = 3, smoothing_factor: float = 3):
        """Smooth a shapely LineString using scipy.interpolate.splprep methods.

        Parameters:
            line: LineString object to be smoothed, the smoothed line is resampled at equal distance specified by interval.
            spline_order: order of the spline, default is 3.
            smoothing_factor: smothing factor, float or None.If s is None, will provide a default smoothing.
                            If 0, spline will interpolate through all data points. Default is None.
        Return:
            tck: tuple containing the vector of knots, the B-spline coefficients, and the degree of the spline.

        """
        # extract coordinates form LineString
        coords = np.array(line.coords)
        x = coords[:, 0]
        y = coords[:, 1]

        # compute smoothing parameter
        if smoothing_factor is not None:
            m = coords.shape[0]
            s = smoothing_factor * (m + np.sqrt(m * 2))
        else:
            s = None

        # fit smoothed spline
        tck, _ = splprep([x, y], s=s, k=spline_order)

        return tck

    def compute_curvature(self, t: float):
        """Compute curvature of the spline at a given point t"""

        # compute first and second derivative of the spline
        dx, dy = splev(t, self.spline_model, der=1)
        ddx, ddy = splev(t, self.spline_model, der=2)

        # compute curvature
        curvature = abs((dx * ddy - dy * ddx) / (dx**2 + dy**2) ** 1.5)

        return curvature

    def get_curveature_at_point(self, point: Point):
        """Compute curvature of the spline at a given point"""

        # find normalized_LRS for the point
        t = self.route_geom.project(point, normalized=True)

        return self.compute_curvature(t)

    def get_curvature_at_LRS(self, lrs: float, normalized=False):
        """Compute curvature of the spline at a given LRS"""
        if lrs < 0:
            raise ValueError("LRS value should be greater than 0")
        if not normalized and lrs <= self.route_geom.length:
            lrs = lrs / self.route_geom.length
        elif normalized and lrs <= 1:
            pass
        else:
            raise ValueError("LRS value should be less than the length of the route")

        return self.compute_curvature(lrs)

    def get_radius_at_point(self, point: Point):
        """Compute radius of the curvature at a given point"""

        curvature = self.get_curveature_at_point(point)
        radius = 1 / curvature

        return radius

    def get_radius_at_LRS(self, lrs: float, normalized=False):
        """Compute radius of the curvature at a given LRS"""

        curvature = self.get_curvature_at_LRS(lrs, normalized)
        radius = 1 / curvature

        return radius


if __name__ == "__main__":
    service = CurveService()
    geojson_file = Path("data") / "SR190_curves.geojson"
    service.get_gdf_from_geojson(geojson_file)
