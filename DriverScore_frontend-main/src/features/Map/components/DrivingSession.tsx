import { DisplayDataType, DisplayShapeOption } from "..";
import { DriverScoreOutSchema, ImuSampleSchema, RouteBasedRCSchema } from "@/client";
import { Marker, Tooltip } from "react-leaflet";
import { RoadCharacteristics, TrajectoryInCircles } from ".";

import { LatLng } from "leaflet";

interface drivingSessionProps {
    // imuSamplesData: ImuSampleSchema[][];
    // scoresData: DriverScoreOutSchema[];
    imuSamplesByDirection: Record<string, ImuSampleSchema[]>[];
    scoresByDirection: Record<string, DriverScoreOutSchema>[];
    routeBasedRCsByDirection: Record<string, RouteBasedRCSchema[]>[];
    displayDataType: DisplayDataType;
    displayShapeOptions: DisplayShapeOption[];
    fetchRunIds: string[];
    hoveredPointIndex: [string | null, number | null];
    setHoveredPointIndex: ([activeLine, index]: [string | null, number | null]) => void;
    radius: number;
    lineWidth: number;
}

export const DrivingSessionComponent = ({
    imuSamplesByDirection,
    scoresByDirection,
    routeBasedRCsByDirection,
    fetchRunIds,
    displayDataType,
    displayShapeOptions,
    radius,
    lineWidth,
    hoveredPointIndex,
    setHoveredPointIndex,
}: drivingSessionProps) => {
    // TODO: Clean the code later
    const RCsWithProps = new Map<string, any>();
    for (let index = 0; index < routeBasedRCsByDirection.length; index++) {
        const singleRouteBasedRCsByDirection = routeBasedRCsByDirection[index];

        for (const [direction, routeBasedRCs] of Object.entries(singleRouteBasedRCsByDirection)) {
            for (const { type, geometry, id, score } of routeBasedRCs) {
                const key = `${type}-${id}`;
                if (!RCsWithProps.has(key)) {
                    const obj = { geometry: geometry, values: [] };
                    RCsWithProps.set(key, obj);
                }

                const g = RCsWithProps.get(key).geometry;
                const values = [
                    ...RCsWithProps.get(key).values,
                    { runId: fetchRunIds[index], type: type, direction: direction, score: score },
                ];
                RCsWithProps.set(key, { geometry: g, values: values });
            }
        }
    }
    return (
        <>
            {/* Granularly display the runs */}
            {scoresByDirection.map((scoreByDirection, index: number) => {
                // Otherwise, display the run
                return Object.entries(scoreByDirection).map(
                    ([
                        direction,
                        {
                            geometry: { coordinates },
                            properties: { scores, timestamps, driver_id },
                        },
                    ]) => (
                        <>
                            <Marker position={new LatLng(coordinates[0][1], coordinates[0][0])}>
                                <Tooltip>Start</Tooltip>
                            </Marker>
                            <Marker
                                position={
                                    new LatLng(
                                        coordinates[coordinates.length - 1][1],
                                        coordinates[coordinates.length - 1][0],
                                    )
                                }
                            >
                                <Tooltip>Finish</Tooltip>
                            </Marker>

                            {displayShapeOptions.includes("point") && (
                                <TrajectoryInCircles
                                    coordinates={coordinates}
                                    scores={scores}
                                    key={`${fetchRunIds[index]}-${direction}_point`}
                                    currentLine={`${fetchRunIds[index]}-${direction}`}
                                    imu_samples={imuSamplesByDirection[index][direction]}
                                    timestamps={timestamps}
                                    driver_id={driver_id}
                                    run_id={fetchRunIds[index]}
                                    radius={radius}
                                    displayDataType={displayDataType}
                                    hoveredPointIndex={hoveredPointIndex}
                                    setHoveredPointIndex={setHoveredPointIndex}
                                    direction={direction}
                                ></TrajectoryInCircles>
                            )}
                        </>
                    ),
                );
            })}
            {/* Route based RCs */}
            {displayShapeOptions.includes("RC") && (
                <RoadCharacteristics RCs={[...RCsWithProps.values()]} lineWidth={lineWidth} />
            )}
        </>
    );
};
