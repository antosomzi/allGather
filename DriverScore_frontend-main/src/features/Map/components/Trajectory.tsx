import { CircleMarker, Marker, Polyline, Tooltip } from "react-leaflet";
import { Coordinates, ImuSampleSchema } from "../../../client";
import { DisplayDataType, getGradient } from "..";
import { HeatmapControl, HeatmapLegend } from "./Gradient";

import { LatLng } from "leaflet";
import { ReactNode } from "react";

type TrajectoryInCirclesProps = {
    coordinates: Coordinates[];
    scores: number[];
    timestamps: string[];
    driver_id: number;
    run_id: string;
    currentLine: string;
    radius: number;
    imu_samples: ImuSampleSchema[];
    displayDataType: DisplayDataType;
    hoveredPointIndex: [string | null, number | null];
    setHoveredPointIndex: ([activeLine, index]: [string | null, number | null]) => void;
    direction: string;
};

export function TrajectoryInCircles({
    coordinates,
    currentLine,
    scores,
    timestamps,
    driver_id,
    run_id,
    radius,
    imu_samples,
    displayDataType,
    hoveredPointIndex,
    setHoveredPointIndex,
    direction,
}: TrajectoryInCirclesProps) {
    const dataToBeDisplayed: { [key in DisplayDataType]: number[] } = {
        score: scores,
        acceleration_x_ms2: imu_samples.map((sample) => sample.acceleration_x_ms2),
        acceleration_y_ms2: imu_samples.map((sample) => sample.acceleration_y_ms2),
        acceleration_z_ms2: imu_samples.map((sample) => sample.acceleration_z_ms2),
    };
    const displayData = dataToBeDisplayed[displayDataType];
    const gradientColors = getGradient(displayData);
    const minValue = displayDataType === "score" ? 0 : Math.min(...displayData);
    const maxValue = displayDataType === "score" ? 100 : Math.max(...displayData);
    const [activeLine, index] = hoveredPointIndex;
    console.log(currentLine);

    function BoldIf({
        condition,
        color = "blue",
        children,
    }: {
        condition: boolean;
        color: string;
        children: ReactNode;
    }) {
        const style = condition ? { fontWeight: "bold", color: color, fontSize: "120%" } : {};
        return <span style={style}>{children}</span>;
    }

    return (
        <>
            <HeatmapControl position={"bottomright"}>
                <HeatmapLegend colors={["#00aa00", "#ffff00", "#ff0000"]} minValue={minValue} maxValue={maxValue} />
            </HeatmapControl>
            {activeLine === currentLine && index !== null && (
                <Marker
                    position={new LatLng(coordinates[index][1], coordinates[index][0])}
                    eventHandlers={{ click: () => setHoveredPointIndex([null, null]) }}
                />
            )}
            {coordinates.map((coordinate: Coordinates, index: number) => {
                const [lng, lat] = coordinate;
                const score = scores[index];
                const timestamp = new Date(timestamps[index]);
                const date = timestamp.toLocaleDateString();
                const time = timestamp.toLocaleTimeString();
                const imu_sample = imu_samples[index];
                const color = gradientColors[index];
                return (
                    <CircleMarker
                        key={index}
                        center={new LatLng(lat, lng)}
                        pathOptions={{ color: color }}
                        radius={radius}
                    >
                        <Tooltip sticky>
                            <b>Run ID: {run_id} </b>
                            <br />
                            Driver: {driver_id}
                            <hr />
                            Direction: {direction}
                            <br />
                            Coordinates: {lng} {lat}
                            <br />
                            Date: {date}
                            <br />
                            Time: {time}
                            <hr />
                            <BoldIf condition={displayDataType === "acceleration_x_ms2"} color={color}>
                                acceleration_x (ms2): {imu_sample.acceleration_x_ms2}
                            </BoldIf>
                            <br />
                            <BoldIf condition={displayDataType === "acceleration_y_ms2"} color={color}>
                                acceleration_y (ms2): {imu_sample.acceleration_y_ms2}
                            </BoldIf>
                            <br />
                            <BoldIf condition={displayDataType === "acceleration_z_ms2"} color={color}>
                                acceleration_z (ms2): {imu_sample.acceleration_z_ms2}
                            </BoldIf>
                            <br />
                            <BoldIf condition={displayDataType === "score"} color={color}>
                                Score: {score}
                            </BoldIf>
                        </Tooltip>
                    </CircleMarker>
                );
            })}
        </>
    );
}
export function SingleTrajectoryInLines(props: {
    coordinates: Coordinates[];
    scores: number[];
    timestamps: string[];
    driver_id: number;
    run_id: string;
    lineWidth: number;
    imu_samples: ImuSampleSchema[];
    displayDataType: DisplayDataType;
}) {
    // const segmentsByScoreLevel = getSegmentsByScoreLevel(props);
    // const [hoveredIndex, setHoveredIndex] = useState<number>(-1);

    const { coordinates, scores, timestamps, driver_id, lineWidth, imu_samples, displayDataType, run_id } = props;

    // TODO: Remove duplicate code
    const dataToBeDisplayed: { [key in DisplayDataType]: number[] } = {
        score: scores,
        acceleration_x_ms2: imu_samples.map((sample) => sample.acceleration_x_ms2),
        acceleration_y_ms2: imu_samples.map((sample) => sample.acceleration_y_ms2),
        acceleration_z_ms2: imu_samples.map((sample) => sample.acceleration_z_ms2),
    };
    const displayData = dataToBeDisplayed[displayDataType];
    const gradientColors = getGradient(displayData);
    const minValue = displayDataType === "score" ? 0 : Math.min(...displayData);
    const maxValue = displayDataType === "score" ? 100 : Math.max(...displayData);
    return (
        <>
            <HeatmapControl position={"bottomright"}>
                <HeatmapLegend colors={["#ff0000", "#ffff00", "#00aa00"]} minValue={minValue} maxValue={maxValue} />
            </HeatmapControl>
            {coordinates.map((_coordinates: Coordinates, index: number) => {
                let latLngCoordinates = [coordinates[index], coordinates[index]].map((coordinate) => [
                    coordinate[1],
                    coordinate[0],
                ]);

                if (index !== coordinates.length - 1) {
                    latLngCoordinates = [coordinates[index], coordinates[index + 1]].map((coordinate) => [
                        coordinate[1],
                        coordinate[0],
                    ]);
                }

                const timestamp = new Date(timestamps[index]);
                const date = timestamp.toLocaleDateString();
                const time = timestamp.toLocaleTimeString();
                const hoveredStyle = {
                    weight: 7, // Increase the weight (thickness) of the line on hover
                    opacity: 1,
                };
                const normalStyle = {
                    weight: lineWidth, // Reset the weight back to initial value
                    opacity: 1,
                };
                // const dimmedStyle = {
                //     weight: lineWidth, // Reset the weight back to initial value
                //     opacity: 0.5,
                // };
                return (
                    <Polyline
                        key={index}
                        positions={latLngCoordinates}
                        pathOptions={{ color: gradientColors[index], ...normalStyle }}
                        // pathOptions={
                        //     hoveredIndex === index ? hoveredStyle : hoveredIndex === -1 ? normalStyle : dimmedStyle
                        // }
                        eventHandlers={{
                            mouseover: (e) => {
                                // setHoveredIndex(index);
                                e.target.setStyle(hoveredStyle);
                                // displayOption === "lineWithPoints" && e.target.openPopup();
                            },
                            mouseout: (e) => {
                                e.target.setStyle(normalStyle);
                                // setHoveredIndex(-1);
                                // displayOption === "lineWithPoints" && e.target.closePopup();
                            },
                        }}
                    >
                        <Tooltip sticky>
                            Run ID: {run_id}
                            <br />
                            Driver: {driver_id}
                            <br />
                            Date: {date}
                            <br />
                            Time: {time}
                        </Tooltip>
                    </Polyline>
                );
            })}
        </>
    );
}
