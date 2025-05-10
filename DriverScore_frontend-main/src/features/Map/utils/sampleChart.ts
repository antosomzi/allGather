import { DriverScoreOutSchema, ImuSampleSchema } from "@/client";

import { DisplayDataType } from "..";

export type SampleProps = { index: number; timestamp: string; lrs: number | null };

export const getDataForSampleChart = (
    fetchRunIds: string[],
    scoresDataByDirection?: Record<string, DriverScoreOutSchema>[],
    imuDataByDirection?: Record<string, ImuSampleSchema[]>[],
    displayDataType?: DisplayDataType,
): Map<string, SampleProps[]> => {
    if (scoresDataByDirection === undefined || scoresDataByDirection.length === 0 || displayDataType === undefined) {
        return new Map();
    }

    if (displayDataType === "score") {
        const result = new Map<string, SampleProps[]>();

        for (let i = 0; i < scoresDataByDirection.length; i++) {
            const runId = fetchRunIds[i];
            const singleScoresDataByDirection = scoresDataByDirection[i];

            Object.entries(singleScoresDataByDirection).map(([direction, scoresData]) => {
                const tmp = scoresData.properties.scores.map((score: number, index: number) => ({
                    index: index,
                    timestamp: new Date(scoresData.properties.timestamps[index]).toLocaleTimeString(),
                    lrs: scoresData.properties.lrs[index],
                    [`${runId}-${direction}`]: score,
                }));
                result.set(`${runId}-${direction}`, tmp);
            });
        }

        return result;
    }

    if (imuDataByDirection === undefined || imuDataByDirection.length === 0) {
        return new Map();
    }
    const result: SampleProps[][] = [];

    // TODO Same for IMU data
    for (let i = 0; i < imuDataByDirection.length; i++) {
        const runId = fetchRunIds[i];
        const singleImuDataBYDirection = imuDataByDirection[i];
        // Object.entries(imuDataByDirection[i].map((imuSample: ImuSampleSchema, index: number)) => ({
        //     index: index,
        //     timestamp: new Date(imuSample.timestamp).toLocaleTimeString(),
        //     value: imuSample[displayDataType],
        // }));
    }
    return result;
};
