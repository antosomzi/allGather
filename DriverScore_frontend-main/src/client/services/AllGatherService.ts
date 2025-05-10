/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_AllGather_upload } from '../models/Body_AllGather_upload';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AllGatherService {
    /**
     * Upload
     * Upload a compressed file (currently support `.zip`, `.tar` and `.tar.gz`) collected
     * by AllGather app containing GPS, Calibration, Acceleration and Camera (optional)
     * data for processing.
     *
     * - **file**: Compressed file collected by AllGather app (required)
     *
     * Returns:
     * - **filename**: Name of the uploaded file
     * - **content_type**: MIME type of the uploaded file
     * - **n_gps_samples**: Number of GPS samples processed from the file
     * @returns any Successful Response
     * @throws ApiError
     */
    public static upload({
        formData,
    }: {
        formData: Body_AllGather_upload,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/allgather/upload',
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
