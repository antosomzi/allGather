import { CornerPositionType } from "../types/map";
import { LatLng } from "leaflet";

export const DEFAULT_MAP_CENTER = new LatLng(33.772163578, -84.390165106); // Georgia Tech

export const POSITION_CLASSES: Record<CornerPositionType, string> = {
    bottomleft: "leaflet-bottom leaflet-left",
    bottomright: "leaflet-bottom leaflet-right",
    topleft: "leaflet-top leaflet-left",
    topright: "leaflet-top leaflet-right",
};
