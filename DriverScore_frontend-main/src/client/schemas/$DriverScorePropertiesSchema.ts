/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $DriverScorePropertiesSchema = {
    properties: {
        driver_id: {
            type: 'number',
            isRequired: true,
        },
        timestamps: {
            type: 'array',
            contains: {
                type: 'string',
                format: 'date-time',
            },
            isRequired: true,
        },
        scores: {
            type: 'array',
            contains: {
                type: 'number',
            },
            isRequired: true,
        },
        lrs: {
            type: 'array',
            contains: {
                type: 'any-of',
                contains: [{
                    type: 'number',
                }, {
                    type: 'null',
                }],
            },
            isRequired: true,
        },
    },
} as const;
