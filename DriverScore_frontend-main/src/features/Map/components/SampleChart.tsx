import {
    Area,
    AreaChart,
    Brush,
    CartesianGrid,
    Legend,
    ReferenceLine,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";
import { DisplayDataType, SampleProps } from "..";

import React from "react";
import { curveCardinal } from "d3-shape";

interface SampleChartProps {
    data: Map<string, SampleProps[]>;
    dataType?: DisplayDataType;
    setHoveredPointIndex: (arg0: [string | null, number | null]) => void;
}

interface Item {
    lrs: number | null;
    [key: string]: number | null;
}

function mergeLists(lists: SampleProps[][]): Item[] {
    const mergedList: Item[] = [];
    const keySet = new Set<number | null>();

    for (const list of lists) {
        for (const item of list) {
            const existingItem = mergedList.find((i) => i.lrs === item.lrs);
            if (existingItem) {
                Object.assign(existingItem, item);
            } else {
                const newItem: Item = { lrs: item.lrs };
                for (const key in item) {
                    if (key !== "lrs") {
                        newItem[key] = item[key];
                    }
                }
                mergedList.push(newItem);
            }
            keySet.add(item.lrs);
        }
    }

    for (const item of mergedList) {
        for (const list of lists) {
            const listItem = list.find((i) => i.lrs === item.lrs);
            if (!listItem) {
                for (const key in list[0]) {
                    if (key !== "lrs" && !(key in item)) {
                        item[key] = null;
                    }
                }
            }
        }
    }

    return mergedList;
}

function getRandomColor(): string {
    const letters = "0123456789ABCDEF";
    let color = "#";

    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }

    return color;
}

export const SampleChart = React.memo(({ data, setHoveredPointIndex, dataType = "score" }: SampleChartProps) => {
    if (data.size == 0) {
        return null;
    }

    const displays = Array.from(data.keys());
    const mergedList = mergeLists([...data.values()]).sort((a, b) => a.lrs! - b.lrs!);
    const colorByDisplay = new Map<string, string>(displays.map((display) => [display, getRandomColor()]));

    const cardinal = curveCardinal.tension(0.2);

    return (
        <>
            <ResponsiveContainer width="100%" height="30%">
                <AreaChart
                    width={500}
                    height={500}
                    data={mergedList}
                    margin={{ top: 10, left: -20, right: 10, bottom: 10 }}
                    onMouseMove={(state) => {
                        let index = state.isTooltipActive ? state.activeTooltipIndex ?? null : null;
                        let activeLine: string | null = null;
                        if (index !== null) {
                            const activeItem = mergedList[index];
                            index = activeItem.index;
                            const found = Object.entries(activeItem).find(
                                ([display, value]) => displays.includes(display) && value !== null,
                            );

                            if (found) {
                                activeLine = found[0];
                            }
                        }
                        setHoveredPointIndex([activeLine, index]);
                    }}
                    onMouseLeave={() => setHoveredPointIndex([null, null])}
                >
                    <defs>
                        {[...colorByDisplay.entries()].map(([display, color]) => (
                            <linearGradient id={`colorSample-${display}`} x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor={color} stopOpacity={0.8} />
                                <stop offset="95%" stopColor={color} stopOpacity={0} />
                            </linearGradient>
                        ))}
                    </defs>
                    {dataType === "score" && (
                        <ReferenceLine
                            y={25}
                            label={{ value: "Danger", fontSize: 14, position: "insideBottom" }}
                            strokeWidth={2}
                            stroke="red"
                        />
                    )}
                    {dataType === "score" && (
                        <ReferenceLine
                            y={50}
                            label={{ value: "Warning", fontSize: 14, position: "bottom" }}
                            strokeWidth={2}
                            stroke="#e4e401"
                        />
                    )}

                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                        dataKey="lrs"
                        angle={-45}
                        fontSize={12}
                        dy={15}
                        height={60}
                        tickFormatter={(lrs) => lrs?.toFixed(3)}
                    />
                    <YAxis />
                    <Legend />
                    <Tooltip />
                    {displays.map((display) => (
                        <Area
                            type={cardinal}
                            dataKey={display}
                            stroke={colorByDisplay.get(display)}
                            fillOpacity={1}
                            fill={`url(#colorSample-${display})`}
                            connectNulls={true}
                        />
                    ))}
                    <Brush dataKey="lrs" height={30} stroke="#9c8200">
                        <AreaChart>
                            {displays.map((display) => (
                                <Area
                                    type="monotone"
                                    dataKey={display}
                                    stroke={colorByDisplay.get(display)}
                                    fillOpacity={1}
                                    fill={`url(#colorSample-${display})`}
                                    connectNulls={true}
                                />
                            ))}{" "}
                        </AreaChart>
                    </Brush>
                </AreaChart>
            </ResponsiveContainer>
        </>
    );
});
