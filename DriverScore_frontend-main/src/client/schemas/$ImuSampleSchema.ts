/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $ImuSampleSchema = {
    properties: {
        timestamp: {
            type: 'string',
            isRequired: true,
            format: 'date-time',
        },
        acceleration_x_ms2: {
            type: 'number',
            isRequired: true,
        },
        acceleration_y_ms2: {
            type: 'number',
            isRequired: true,
        },
        acceleration_z_ms2: {
            type: 'number',
            isRequired: true,
        },
        angular_velocity_x_rads: {
            type: 'number',
            isRequired: true,
        },
        angular_velocity_y_rads: {
            type: 'number',
            isRequired: true,
        },
        angular_velocity_z_rads: {
            type: 'number',
            isRequired: true,
        },
        pitch_rad: {
            type: 'number',
            isRequired: true,
        },
        yaw_rad: {
            type: 'number',
            isRequired: true,
        },
        roll_rad: {
            type: 'number',
            isRequired: true,
        },
    },
} as const;
