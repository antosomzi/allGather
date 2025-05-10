import { LatLngBounds, Map as LeafletMap } from "leaflet";
import { MapContainer, Rectangle, TileLayer, useMap, useMapEvent } from "react-leaflet";
import { useCallback, useMemo, useState } from "react";

import { LeafletMouseEvent } from "leaflet";
// import { Map } from "leaflet";
import { PathOptions } from "leaflet";
import { useEventHandlers } from "@react-leaflet/core";

// Classes used by Leaflet to position controls
type CornerPositionType = "bottomleft" | "bottomright" | "topleft" | "topright";
const POSITION_CLASSES: Record<CornerPositionType, string> = {
    bottomleft: "leaflet-bottom leaflet-left",
    bottomright: "leaflet-bottom leaflet-right",
    topleft: "leaflet-top leaflet-left",
    topright: "leaflet-top leaflet-right",
};

const BOUNDS_STYLE = { weight: 1 };

interface MinimapBoundsProps {
    parentMap: LeafletMap;
    zoom: number;
}

function MinimapBounds({ parentMap, zoom }: MinimapBoundsProps): JSX.Element {
    const minimap = useMap();

    // Clicking a point on the minimap sets the parent's map center
    const onClick = useCallback(
        (e: LeafletMouseEvent) => {
            parentMap.setView(e.latlng, parentMap.getZoom());
        },
        [parentMap],
    );
    useMapEvent("click", onClick);

    // Keep track of bounds in state to trigger renders
    const [bounds, setBounds] = useState<LatLngBounds>(parentMap.getBounds());
    const onChange = useCallback(() => {
        setBounds(parentMap.getBounds());
        minimap.setView(parentMap.getCenter(), zoom);
    }, [minimap, parentMap, zoom]);

    // Listen to events on the parent map
    const handlers = useMemo(() => ({ move: onChange, zoom: onChange }), [onChange]);
    useEventHandlers({ instance: parentMap }, handlers);

    return <Rectangle bounds={bounds} pathOptions={BOUNDS_STYLE as PathOptions} />;
}

interface MinimapControlProps {
    position: CornerPositionType;
    zoom: number;
    scoresComponent: JSX.Element;
}

export default function MinimapControl({ position, zoom, scoresComponent }: MinimapControlProps): JSX.Element {
    const parentMap = useMap();
    const mapZoom = zoom || 0;

    // Memoize the minimap so it's not affected by position changes
    const minimap = useMemo(
        () => (
            <MapContainer
                style={{ height: 120, width: 120 }}
                center={parentMap.getCenter()}
                zoom={mapZoom}
                dragging={false}
                doubleClickZoom={false}
                scrollWheelZoom={false}
                attributionControl={false}
                zoomControl={false}
            >
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                {scoresComponent}
                <MinimapBounds parentMap={parentMap} zoom={mapZoom} />
            </MapContainer>
        ),
        [parentMap, mapZoom, scoresComponent],
    );

    const positionClass = POSITION_CLASSES[position] || POSITION_CLASSES.topright;
    return (
        <div className={positionClass}>
            <div className="leaflet-control leaflet-bar">{minimap}</div>
        </div>
    );
}
