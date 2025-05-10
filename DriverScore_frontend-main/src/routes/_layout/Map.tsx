import "leaflet/dist/leaflet.css";

import { ArrowDownIcon, ArrowLeftIcon, HamburgerIcon } from "@chakra-ui/icons";
import {
    Box,
    Container,
    Flex,
    IconButton,
    Menu,
    MenuButton,
    MenuDivider,
    MenuItemOption,
    MenuList,
    MenuOptionGroup,
    Spacer,
    Stack,
    useDisclosure,
} from "@chakra-ui/react";
import {
    DEFAULT_MAP_CENTER,
    DisplayDataType,
    DisplayShapeOption,
    InputArray,
    Run,
    getCenterMap,
    getDataForSampleChart,
} from "@/features/Map";
import { MapContainer, TileLayer } from "react-leaflet";
import { RoutesService, RunsService } from "../../client";
import { useCallback, useRef, useState } from "react";

import { DrivingSessionComponent } from "@/features/Map/components/DrivingSession";
import { DrivingSessionsModal } from "@/features/Map/components";
import EmptyMap from "@/features/Map/components/EmptyMap";
import React from "react";
import { SampleChart } from "@/features/Map/components/SampleChart";
import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";

// const AvailableDisplayDataTypes = Object.values({
//     score: "score",
//     acceleration_x_ms2: "acceleration_x_ms2",
//     acceleration_y_ms2: "acceleration_y_ms2",
//     acceleration_z_ms2: "acceleration_z_ms2",
// }) as DisplayDataType[];
const AvailableDisplayDataTypes: DisplayDataType[] = [
    "score",
    "acceleration_x_ms2",
    "acceleration_y_ms2",
    "acceleration_z_ms2",
];
const availableDisplayShapeOptions: DisplayShapeOption[] = ["point", "RC"];

export const Route = createFileRoute("/_layout/Map")({
    component: Map,
});

export function Map() {
    const {
        isOpen: isDrivingSessionModalOpen,
        onOpen: onDrivingSessionModalOpen,
        onClose: onDrivingSessionModalClose,
    } = useDisclosure();
    const { onToggle: onSampleChartToggle } = useDisclosure();
    const [fetchRunIds, setFetchRunIds] = useState<string[]>([]);
    const [inputs, setInputs] = useState<InputArray>([]);
    const [displayRunIds, setDisplayRunIds] = useState<string[]>([]);
    const [displayDirections, setDisplayDirections] = useState<string[][]>([]);

    const [hoveredPointIndex, setHoveredPointIndex] = useState<[string | null, number | null]>([null, null]);
    // const [selectedRunId, setSelectedRunId] = useState<string>("");
    const [displayShapeOptions, setDisplayShapeOptions] = useState<DisplayShapeOption[]>(["RC", "point"]);
    const [displayDataType, setDisplayDataType] = useState<DisplayDataType>("score");
    const mapRef = useRef<LeafletMap | null>(null);
    const memoizedSetHoveredPointIndex = useCallback(([activeLine, index]: [string | null, number | null]) => {
        setHoveredPointIndex([activeLine, index]);
    }, []);

    // Query scores, imu samples, and routes for the selected runs
    const {
        data: scoresData,
        isLoading: isScoresLoading,
        isError: isScoresError,
        error: scoresError,
    } = useQuery({
        queryKey: ["scores", fetchRunIds],
        queryFn: () => {
            return Promise.all(fetchRunIds.map((runId) => RunsService.getScoresByDirection({ runId })));
        },
    });
    const {
        data: runsData,
        isLoading: isRunsLoading,
        isError: isRunsError,
        error: runsError,
    } = useQuery({
        queryKey: ["runs"],
        queryFn: () => {
            return RunsService.getRuns1();
        },
    });

    const {
        data: routeBasedRCs,
        isLoading: isRoutesLoading,
        isError: isRoutesError,
        error: routesError,
    } = useQuery({
        queryKey: ["routes", fetchRunIds],
        queryFn: () => {
            return Promise.all(fetchRunIds.map((runId) => RoutesService.getRCs({ runId })));
        },
    });

    const {
        data: imuSamplesData,
        isLoading: isImuSamplesLoading,
        isError: isImuSamplesError,
        error: imuSamplesError,
    } = useQuery({
        queryKey: ["imu_samples", fetchRunIds],
        queryFn: () => {
            return Promise.all(fetchRunIds.map((runId) => RunsService.getImuSamplesByDirection({ runId })));
        },
    });

    // TODO: refactor these 3 into a single function
    // Get scores Data for selected displayDirections
    const scoresDataByDirection = React.useMemo(
        () =>
            scoresData !== undefined && scoresData.length > 0
                ? scoresData.map((scores, index) => {
                      const scoresEntries = Object.entries(scores).filter(
                          ([direction]) =>
                              displayDirections.length == 0 || displayDirections[index].includes(direction),
                      );
                      return Object.fromEntries(scoresEntries);
                  })
                : [],
        [scoresData, displayDirections],
    );

    // Get IMU Data for selected displayDirections
    const imuDataByDirection = React.useMemo(
        () =>
            imuSamplesData !== undefined && imuSamplesData.length > 0
                ? imuSamplesData.map((imuSamples, index) => {
                      const imuEntries = Object.entries(imuSamples).filter(
                          ([direction]) =>
                              displayDirections.length == 0 || displayDirections[index].includes(direction),
                      );
                      return Object.fromEntries(imuEntries);
                  })
                : [],
        [imuSamplesData, displayDirections],
    );

    // Get routes-based RCs for selected displayDirections
    const routeBasedRCsByDirection = React.useMemo(
        () =>
            routeBasedRCs !== undefined && routeBasedRCs.length > 0
                ? routeBasedRCs.map((routeBasedRC, index) => {
                      const routeBasedRCEntries = Object.entries(routeBasedRC).filter(
                          ([direction]) =>
                              displayDirections.length == 0 || displayDirections[index].includes(direction),
                      );
                      return Object.fromEntries(routeBasedRCEntries);
                  })
                : [],
        [routeBasedRCs, displayDirections],
    );

    const dataForSampleChart = React.useMemo(
        () => getDataForSampleChart(fetchRunIds, scoresDataByDirection, imuDataByDirection, displayDataType),
        [fetchRunIds, scoresDataByDirection, imuDataByDirection, displayDataType],
    );

    // Error and default handling
    if (isScoresLoading || isRunsLoading || scoresData === undefined || runsData === undefined) {
        return <EmptyMap center={DEFAULT_MAP_CENTER}></EmptyMap>;
    }
    if (isScoresError) {
        return <div>Error: {scoresError.message}</div>;
    }
    if (isRunsError) {
        return <div>Error: {runsError.message}</div>;
    }
    // TODO: Fix this later: Fly to the center of the map while waiting for IMU sample data
    const centerMap = getCenterMap(scoresData.map((record) => Object.values(record)).flat());
    // if (mapRef.current && scoresData.length > 0) {
    //     console.log(centerMap);
    //     mapRef.current.flyTo(centerMap, 13, { duration: 5 });
    // }

    if (isImuSamplesLoading || imuSamplesData === undefined || routeBasedRCs === undefined || isRoutesLoading) {
        return <EmptyMap center={DEFAULT_MAP_CENTER}></EmptyMap>;
    }

    if (isImuSamplesError) {
        return <div>Error: {imuSamplesError.message}</div>;
    }
    if (isRoutesError) {
        return <div>Error: {routesError.message}</div>;
    }

    const processedRunsData: Run[] = runsData.map((run) => {
        return { ...run, start_time: new Date(run.start_time) };
    });

    return (
        <Container maxW="full">
            <Box pt={12} m={4}>
                <MapContainer
                    ref={mapRef}
                    style={{ height: "60vh" }}
                    center={centerMap}
                    zoom={14}
                    zoomControl={false}
                    scrollWheelZoom={true}
                >
                    <TileLayer
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />
                    {/* <MinimapControl position="topright" zoom={9} scoresComponent={scoresComponent(1, 1)} /> */}
                    {/* TODO: Use Zustand instead of prop drilling */}
                    <DrivingSessionComponent
                        imuSamplesByDirection={imuDataByDirection}
                        scoresByDirection={scoresDataByDirection}
                        routeBasedRCsByDirection={routeBasedRCsByDirection}
                        fetchRunIds={fetchRunIds}
                        displayDataType={displayDataType}
                        displayShapeOptions={displayShapeOptions}
                        hoveredPointIndex={hoveredPointIndex}
                        setHoveredPointIndex={setHoveredPointIndex}
                        lineWidth={10}
                        radius={4}
                    />
                </MapContainer>
            </Box>
            <Flex>
                {/* TODO: Replace scoresData with valid input because runsData
            might be cached on Prod */}
                {scoresData.length == 0 ? (
                    <IconButton aria-label="Options" icon={<HamburgerIcon />} colorScheme="gray" disabled />
                ) : (
                    <Box zIndex="dropdown" position={"relative"}>
                        <Menu closeOnSelect={false}>
                            <MenuButton
                                as={IconButton}
                                aria-label="Options"
                                icon={<HamburgerIcon />}
                                colorScheme="teal"
                            />
                            <MenuList minWidth="240px">
                                <Stack direction="row" spacing={4} p={2}>
                                    <Stack spacing={4} p={2}>
                                        <MenuOptionGroup
                                            defaultValue={displayRunIds}
                                            flexDirection="row"
                                            title="Run ID"
                                            type="checkbox"
                                            onChange={(e) => {
                                                setDisplayRunIds(e as string[]);
                                            }}
                                        >
                                            {
                                                // TODO: Fix this duplicate code
                                                fetchRunIds.map((runId, index) => (
                                                    <MenuOptionGroup
                                                        key={runId}
                                                        title={runId}
                                                        type="checkbox"
                                                        defaultValue={["increasing", "decreasing"]}
                                                        onChange={(e) => {
                                                            const displayDirectionsCopy = [...displayDirections];
                                                            displayDirectionsCopy[index] = Array.isArray(e)
                                                                ? e.map((item) => item as string)
                                                                : [e as string];
                                                            setDisplayDirections(displayDirectionsCopy);
                                                        }}
                                                    >
                                                        {Object.entries(scoresData[index]).map(([direction]) => (
                                                            <MenuItemOption key={direction} value={direction}>
                                                                {direction}
                                                            </MenuItemOption>
                                                        ))}
                                                    </MenuOptionGroup>
                                                ))
                                            }
                                        </MenuOptionGroup>
                                        <MenuOptionGroup
                                            title="Trajectory Shape"
                                            type="checkbox"
                                            defaultValue={displayShapeOptions}
                                            onChange={(e) =>
                                                setDisplayShapeOptions(
                                                    Array.isArray(e)
                                                        ? e.map((item) => item as DisplayShapeOption)
                                                        : [e as DisplayShapeOption],
                                                )
                                            }
                                        >
                                            {availableDisplayShapeOptions.map((option) => (
                                                <MenuItemOption
                                                    key={option}
                                                    value={option}
                                                    isDisabled={
                                                        displayShapeOptions.length === 1 &&
                                                        displayShapeOptions.includes(option)
                                                    }
                                                >
                                                    {option}
                                                </MenuItemOption>
                                            ))}
                                        </MenuOptionGroup>
                                    </Stack>
                                    <MenuDivider />
                                    <MenuOptionGroup
                                        title="Data Type"
                                        type="radio"
                                        defaultValue={displayDataType}
                                        onChange={(e) => {
                                            setDisplayDataType(e as DisplayDataType);
                                        }}
                                    >
                                        {AvailableDisplayDataTypes.map((dataType) => (
                                            <MenuItemOption key={dataType} value={dataType}>
                                                {dataType}
                                            </MenuItemOption>
                                        ))}
                                    </MenuOptionGroup>
                                </Stack>
                            </MenuList>
                        </Menu>
                    </Box>
                )}
                <Spacer />
                <IconButton
                    isRound={true}
                    aria-label="View Chart"
                    icon={<ArrowDownIcon />}
                    colorScheme="teal"
                    onClick={onSampleChartToggle}
                />
                <Spacer />
                <IconButton
                    isRound={true}
                    aria-label="Select Sections"
                    icon={<ArrowLeftIcon />}
                    colorScheme="teal"
                    onClick={onDrivingSessionModalOpen}
                />
            </Flex>
            <DrivingSessionsModal
                isOpen={isDrivingSessionModalOpen}
                onClose={onDrivingSessionModalClose}
                setFetchRunIds={setFetchRunIds}
                setDisplayDirections={setDisplayDirections}
                runsData={processedRunsData}
                inputs={inputs}
                setInputs={setInputs}
                setDisplayRunIds={setDisplayRunIds}
            />
            <SampleChart
                data={dataForSampleChart}
                setHoveredPointIndex={memoizedSetHoveredPointIndex}
                dataType={displayDataType}
            />
        </Container>
    );
}
