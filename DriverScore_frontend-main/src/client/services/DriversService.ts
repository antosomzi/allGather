/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { RunSchema } from '../models/RunSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DriversService {
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
}
