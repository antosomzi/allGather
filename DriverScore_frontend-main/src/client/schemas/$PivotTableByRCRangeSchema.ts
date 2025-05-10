/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $PivotTableByRCRangeSchema = {
    properties: {
        driver_id: {
            type: 'number',
            isRequired: true,
        },
        run_id: {
            type: 'string',
            isRequired: true,
        },
        RC_range: {
            type: 'string',
            isRequired: true,
        },
        score: {
            type: 'number',
            isRequired: true,
        },
    },
} as const;
