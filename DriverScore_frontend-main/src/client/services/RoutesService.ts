/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_Routes_curve_upload } from '../models/Body_Routes_curve_upload';
import type { Body_Routes_upload } from '../models/Body_Routes_upload';
import type { RouteBasedRCSchema } from '../models/RouteBasedRCSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class RoutesService {
    /**
     * Upload
     * @returns any Successful Response
     * @throws ApiError
     */
    public static upload({
        formData,
    }: {
        formData: Body_Routes_upload,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/routes/upload',
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Curve Upload
     * @returns any Successful Response
     * @throws ApiError
     */
    public static curveUpload({
        formData,
    }: {
        formData: Body_Routes_curve_upload,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/routes/curves/upload',
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Rcs
     * Get the road characteristics for a specific run.
     *
     * Parameters:
     * run_id (str): The ID of the run.
     *
     * Returns:
     * list[RoadCharacteristicSchema]: A list of road characteristics for the run.
     * @returns RouteBasedRCSchema Successful Response
     * @throws ApiError
     */
    public static getRCs({
        runId,
    }: {
        runId: string,
    }): CancelablePromise<Record<string, Array<RouteBasedRCSchema>>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/routes/{run_id}',
            path: {
                'run_id': runId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
