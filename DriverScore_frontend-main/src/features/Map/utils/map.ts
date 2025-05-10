import { DEFAULT_MAP_CENTER } from "..";
import { DriverScoreOutSchema } from "@/client";
import { LatLng } from "leaflet";

export function getCenterMap(data: DriverScoreOutSchema[]): LatLng {
    const coordinates = data.flatMap((d) => d.geometry.coordinates);
    if (coordinates.length === 0 || data === undefined) {
        return DEFAULT_MAP_CENTER;
    }

    let minX = coordinates[0][0],
        maxX = coordinates[0][0];
    let minY = coordinates[0][1],
        maxY = coordinates[0][1];

    // Calculate bounding box
    coordinates.forEach((coordinate) => {
        const lng = coordinate[0];
        const lat = coordinate[1];

        minX = Math.min(minX, lng);
        maxX = Math.max(maxX, lng);
        minY = Math.min(minY, lat);
        maxY = Math.max(maxY, lat);
    });

    // Calculate center
    const center = new LatLng((minY + maxY) / 2, (minX + maxX) / 2);
    return center;
}

export function getGradient(
    values: number[],
    isScore: boolean = false,
    color1: [number, number, number] = [255, 0, 0], //red
    color2: [number, number, number] = [255, 255, 0], // Yellow
    color3: [number, number, number] = [0, 170, 0], // Green
): string[] {
    const min_val = isScore ? 0 : Math.min(...values);
    const max_val = isScore ? 100 : Math.max(...values);
    const colors: string[] = [];

    for (const val of values) {
        const ratio = (val - min_val) / (max_val - min_val);
        let r, g, b;

        if (ratio < 0.5) {
            r = color1[0] + (color2[0] - color1[0]) * ratio * 2;
            g = color1[1] + (color2[1] - color1[1]) * ratio * 2;
            b = color1[2] + (color2[2] - color1[2]) * ratio * 2;
        } else {
            r = color2[0] + (color3[0] - color2[0]) * (ratio - 0.5) * 2;
            g = color2[1] + (color3[1] - color2[1]) * (ratio - 0.5) * 2;
            b = color2[2] + (color3[2] - color2[2]) * (ratio - 0.5) * 2;
        }

        const color = `rgb(${[Math.round(r), Math.round(g), Math.round(b)].join(",")})`;
        colors.push(color);
    }

    return colors;
}
