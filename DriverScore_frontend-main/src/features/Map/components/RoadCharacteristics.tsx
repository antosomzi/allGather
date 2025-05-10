import { HeatmapControl, HeatmapLegend } from "./Gradient";
import { LatLng, LatLngBounds } from "leaflet";
import { LineStringModel, RouteBasedRCSchema } from "../../../client";
import { Polyline, Tooltip } from "react-leaflet";

import { LatLngTuple } from "leaflet";
import { getGradient } from "../utils/map";
import { useState } from "react";

export function RoadCharacteristics(props: {
    RCs: { geometry: LineStringModel; values: { runId: string; type: string; direction: string; score: number }[] }[];
    lineWidth: number;
}) {
    // const segmentsByScoreLevel = getSegmentsByScoreLevel(props);
    // const [hoveredIndex, setHoveredIndex] = useState<number>(-1);
    const [showBoundingBox, setShowBoundingBox] = useState<boolean>(false);
    const [boundingBox, setBoundingBox] = useState<LatLngBounds | null>(null);
    const { RCs, lineWidth } = props;
    const gradientColors = getGradient(
        RCs.map((rc) => rc.values.reduce((acc, cur) => acc + cur.score, 0) / rc.values.length),
        true,
    );

    const getLatLngsFromGeo = (geometry: LineStringModel) => {
        return geometry.coordinates.map((coordinate) => new LatLng(coordinate[1], coordinate[0]));
    };
    return (
        <>
            <HeatmapControl position={"bottomright"}>
                <HeatmapLegend colors={["#00aa00", "#ffff00", "#ff0000"]} minValue={0} maxValue={100} />
            </HeatmapControl>
            {RCs.map(({ geometry, values }, index: number) => {
                const color = gradientColors[index];

                const hoveredStyle = {
                    weight: 10, // Increase the weight (thickness) of the line on hover
                    opacity: 1,
                };

                const normalStyle = {
                    weight: lineWidth, // Reset the weight back to initial value
                    color: color,
                    opacity: 1,
                };
                // const dimmedStyle = {
                //     weight: lineWidth, // Reset the weight back to initial value
                //     opacity: 0.5,
                // };

                return (
                    <Polyline
                        key={index}
                        positions={getLatLngsFromGeo(geometry)}
                        pathOptions={{ ...normalStyle }}
                        eventHandlers={{
                            mouseover: (e) => {
                                e.target.setStyle(hoveredStyle);
                                const coords = getLatLngsFromGeo(geometry).map(
                                    (latLng) => [latLng.lat, latLng.lng] as LatLngTuple,
                                );

                                const bounds = new LatLngBounds(coords);
                                setBoundingBox(bounds);
                                setShowBoundingBox(true);
                            },
                            mouseout: (e) => {
                                e.target.setStyle(normalStyle);
                                setShowBoundingBox(false);
                            },
                        }}
                    >
                        <Tooltip sticky>
                            RC type: {values[0].type ?? "unknown"}
                            <br />
                            <hr />
                            {values.map(({ runId, direction, score }) => (
                                <>
                                    Run ID: {runId}
                                    <br />
                                    Direction: {direction}
                                    <br />
                                    Score: {score}
                                    <br />
                                    <hr />
                                </>
                            ))}
                        </Tooltip>
                    </Polyline>
                );
            })}
        </>
    );
}
