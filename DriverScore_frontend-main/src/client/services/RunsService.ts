/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DriverScoreOutSchema } from '../models/DriverScoreOutSchema';
import type { GpsSampleSchema } from '../models/GpsSampleSchema';
import type { ImuSampleSchema } from '../models/ImuSampleSchema';
import type { RunSchema } from '../models/RunSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class RunsService {
    /**
     * Get Runs
     * Get runs for a specific driver or all runs.
     *
     * - **driver_id** (optional): The ID of the driver to filter runs by.
     *
     * Returns a list of runs.
     * @returns RunSchema Successful Response
     * @throws ApiError
     */
    public static getRuns({
        driverId,
    }: {
        driverId: number,
    }): CancelablePromise<Array<RunSchema>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/drivers/{driver_id}/runs',
            path: {
                'driver_id': driverId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Runs
     * Get a specific run by its ID.
     *
     * - **run_id**: The ID of the run to retrieve.
     *
     * Returns the run details.
     * @returns RunSchema Successful Response
     * @throws ApiError
     */
    public static getRuns1(): CancelablePromise<Array<RunSchema>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/runs/',
        });
    }
    /**
     * Get Run
     * Get a specific run by its ID.
     *
     * - **run_id**: The ID of the run to retrieve.
     *
     * Returns the run details.
     * @returns RunSchema Successful Response
     * @throws ApiError
     */
    public static getRun({
        runId,
    }: {
        runId: string,
    }): CancelablePromise<RunSchema> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/runs/{run_id}',
            path: {
                'run_id': runId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Scores By Direction
     * Get the calculated driver scores for a specific run.
     *
     * - **run_id**: The ID of the run to retrieve scores for.
     *
     * Returns the calculated driver scores for the run.
     * @returns DriverScoreOutSchema Successful Response
     * @throws ApiError
     */
    public static getScoresByDirection({
        runId,
    }: {
        runId: string,
    }): CancelablePromise<Record<string, DriverScoreOutSchema>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/runs/{run_id}/scores',
            path: {
                'run_id': runId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Gps Samples By Direction
     * Get GPS samples for a specific run ID.
     *
     * - **run_id**: The ID of the run to retrieve GPS samples for.
     *
     * Returns a list of GPS samples for the specified run ID.
     * @returns GpsSampleSchema Successful Response
     * @throws ApiError
     */
    public static getGpsSamplesByDirection({
        runId,
    }: {
        runId: string,
    }): CancelablePromise<Record<string, Array<GpsSampleSchema>>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/runs/{run_id}/gps_samples',
            path: {
                'run_id': runId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Imu Samples By Direction
     * Get the IMU samples for a specific run by its ID.
     *
     * - **run_id**: The ID of the run to retrieve IMU samples for.
     *
     * Returns a list of IMU samples.
     * @returns ImuSampleSchema Successful Response
     * @throws ApiError
     */
    public static getImuSamplesByDirection({
        runId,
    }: {
        runId: string,
    }): CancelablePromise<Record<string, Array<ImuSampleSchema>>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/runs/{run_id}/imu_samples',
            path: {
                'run_id': runId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
