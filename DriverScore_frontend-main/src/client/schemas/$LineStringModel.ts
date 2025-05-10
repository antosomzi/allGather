/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $LineStringModel = {
    properties: {
        type: {
            type: 'string',
        },
        coordinates: {
            type: 'array',
            contains: {
                type: 'Coordinates',
            },
            isRequired: true,
        },
    },
} as const;
