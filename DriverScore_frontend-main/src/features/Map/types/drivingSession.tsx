export type runIdInput = {
    id: string;
    runId?: string;
};
export type DriverSessionInput = {
    id: string;
    driverId?: number;
    startTimes: Date[];
    runIds: string[];
};

export type Run = {
    driver_id: number;
    run_id: string;
    start_time: Date;
};

export type InputArray = (runIdInput | DriverSessionInput)[];
