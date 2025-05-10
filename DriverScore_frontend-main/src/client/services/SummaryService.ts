/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PivotTableByRCRangeSchema } from '../models/PivotTableByRCRangeSchema';
import type { PivotTableByRCTypeSchema } from '../models/PivotTableByRCTypeSchema';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class SummaryService {
    /**
     * Get Summary By Rc Range
     * @returns PivotTableByRCRangeSchema Successful Response
     * @throws ApiError
     */
    public static getSummaryByRcRange(): CancelablePromise<Array<PivotTableByRCRangeSchema>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/summary/range',
        });
    }
    /**
     * Get Summary By Rc Type
     * @returns PivotTableByRCTypeSchema Successful Response
     * @throws ApiError
     */
    public static getSummaryByRcType(): CancelablePromise<Array<PivotTableByRCTypeSchema>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/summary/type',
        });
    }
}
