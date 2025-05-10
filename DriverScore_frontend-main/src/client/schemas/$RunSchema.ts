/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $RunSchema = {
    properties: {
        run_id: {
            type: 'string',
            isRequired: true,
        },
        driver_id: {
            type: 'number',
            isRequired: true,
        },
        start_time: {
            type: 'string',
            isRequired: true,
            format: 'date-time',
        },
    },
} as const;
