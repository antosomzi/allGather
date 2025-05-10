import { CSSProperties } from "react";
import { CornerPositionType } from "../types/map";
import { POSITION_CLASSES } from "..";

// import { useMap } from "react-leaflet";

export function HeatmapControl({ position, children }: { position: CornerPositionType; children: JSX.Element }) {
    // const parentMap = useMap();
    // const bounds = useState(parentMap.getBounds())[0];

    const positionClass = (position && POSITION_CLASSES[position]) || POSITION_CLASSES.topright;

    return (
        <div className={positionClass}>
            {/* <div className="leaflet-control leaflet-bar">{minimap}</div> */}
            <div className="leaflet-control leaflet-bar">{children}</div>
        </div>
    );
}

export function HeatmapLegend({
    colors,
    minValue,
    maxValue,
}: {
    colors: string[];
    minValue: number;
    maxValue: number;
}) {
    const gradientStyle: CSSProperties = {
        background: `linear-gradient(to bottom, ${colors.join(", ")})`,
        height: 120,
        width: 20,
        position: "relative",
    };

    const valueStyle: CSSProperties = {
        position: "absolute",
        fontSize: "12px",
        fontWeight: "bold",
    };

    const minValueStyle: CSSProperties = {
        ...valueStyle,
        bottom: 0,
        left: -10,
    };

    const maxValueStyle: CSSProperties = {
        ...valueStyle,
        top: -20,
        left: -10,
    };

    return (
        <div>
            <div style={gradientStyle}>
                <div style={maxValueStyle}>{maxValue}</div>
                <div style={minValueStyle}>{minValue}</div>
            </div>
        </div>
    );
}
