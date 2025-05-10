/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $GpsSampleSchema = {
    properties: {
        timestamp: {
            type: 'string',
            isRequired: true,
            format: 'date-time',
        },
        latitude: {
            type: 'number',
            isRequired: true,
        },
        longitude: {
            type: 'number',
            isRequired: true,
        },
        altitude: {
            type: 'number',
            isRequired: true,
        },
        pos_accuracy: {
            type: 'number',
            isRequired: true,
        },
        heading: {
            type: 'number',
            isRequired: true,
        },
        velocity: {
            type: 'number',
            isRequired: true,
        },
        vel_accuracy: {
            type: 'number',
            isRequired: true,
        },
    },
} as const;
