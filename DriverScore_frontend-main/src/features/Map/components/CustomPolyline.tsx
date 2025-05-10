import L from "leaflet";
import { Marker } from "react-leaflet";
import { Polyline } from "react-leaflet";

function CustomPolyline(props) {
    function createArrowIcon() {
        return L.divIcon({
            className: "arrow-icon",
            iconSize: [20, 20],
            iconAnchor: [10, 10],
            html: `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 4l-1.41 1.41L16.17 11H4v2h12.17l-5.58 5.59L12 20l8-8z" />
            </svg>`,
        });
    }
    const { positions, ...otherProps } = props;
    const center = L.polyline(positions).getCenter();
    return (
        <Polyline positions={positions} {...otherProps}>
            <Marker position={center} icon={createArrowIcon()} />
        </Polyline>
    );
}

export default CustomPolyline;
