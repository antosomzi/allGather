/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $DriverScoreOutSchema = {
    properties: {
        type: {
            type: 'string',
        },
        geometry: {
            type: 'LineStringModel',
            isRequired: true,
        },
        properties: {
            type: 'DriverScorePropertiesSchema',
            isRequired: true,
        },
    },
} as const;
