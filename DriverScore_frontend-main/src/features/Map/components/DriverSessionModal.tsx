import { AddIcon, CloseIcon } from "@chakra-ui/icons";
import {
    Box,
    Button,
    DrawerHeader,
    Flex,
    Grid,
    IconButton,
    Menu,
    MenuButton,
    MenuItem,
    MenuList,
    Modal,
    ModalBody,
    ModalCloseButton,
    ModalContent,
    ModalOverlay,
} from "@chakra-ui/react";

import React from "react";
import { Select } from "chakra-react-select";
import { v4 as uuidv4 } from "uuid";

type runIdInput = {
    id: string;
    runId?: string;
};

type DriverSessionInput = {
    id: string;
    driverId?: number;
    startTimes: Date[];
    runIds: string[];
};

type Run = {
    driver_id: number;
    run_id: string;
    start_time: Date;
};

type InputArray = (runIdInput | DriverSessionInput)[];

export function DrivingSessionsModal(props: {
    isOpen: boolean;
    onClose: () => void;
    runsData: Run[];
    inputs: InputArray;
    setInputs: React.Dispatch<React.SetStateAction<InputArray>>;
    setFetchRunIds: React.Dispatch<React.SetStateAction<string[]>>;
    setDisplayRunIds: React.Dispatch<React.SetStateAction<string[]>>;
    setDisplayDirections: React.Dispatch<React.SetStateAction<string[][]>>;
}) {
    const {
        isOpen,
        onClose,
        setFetchRunIds,
        setDisplayRunIds,
        setDisplayDirections,
        runsData: availableRunsData,
        inputs,
        setInputs,
    } = props;

    const addRunIdInput = () => setInputs([...inputs, { runId: undefined, id: uuidv4() }]);
    const addDriverSessionInput = () => setInputs([...inputs, { driverId: undefined, startTimes: [], id: uuidv4() }]);
    const removeInputById = (id: string) => setInputs(inputs.filter((input) => input.id != id));
    const updateInputWithRunId = (id: string, runId?: string) =>
        setInputs(
            inputs.map((input) => {
                if (input.id != id) {
                    return input;
                }
                return { ...input, runId: runId };
            }),
        );
    const updateInputWithDriverId = (id: string, driverId?: number) =>
        setInputs(
            inputs.map((input) => {
                if (input.id != id) {
                    return input;
                }
                return { ...input, driverId: driverId };
            }),
        );
    const updateInputWithStartTime = (id: string, values: IterableIterator<{ value: Date; label: string }>) => {
        const driverId = getDriverIdByObjId(id);
        const startTimes: Date[] = [];
        const runIds: string[] = [];
        for (const value of values) {
            const startTime = value.value;
            startTimes.push(startTime);
            const runId = availableRunsData.find(
                (run) => run.driver_id === driverId && run.start_time.getTime() === startTime.getTime(),
            )?.run_id;

            if (runId === undefined) throw Error("runId cannot be undefined!");
            runIds.push(runId);
        }
        setInputs(
            inputs.map((input) => {
                if (input.id != id) {
                    return input;
                }
                return { ...input, startTimes: startTimes, runIds: runIds };
            }),
        );
    };
    const getValidOptions = () => {
        const options = [];
        for (const run of availableRunsData) {
            const foundInputGivenRun = inputs.find((input) => {
                if ("driverId" in input) {
                    // TODO: Fix Later
                    return run.driver_id === input.driverId && input.startTimes.length > 0;
                } else {
                    return run.run_id === (input as runIdInput).runId;
                }
            });

            if (foundInputGivenRun === undefined) options.push(run);
        }
        return options;
    };

    const getValidRunIdOptions = () => {
        const options = getValidOptions();
        return options.map((option) => {
            return { value: option.run_id, label: option.run_id };
        });
    };

    const getValidDriverIdOptions = () => {
        const options = getValidOptions();
        const seenDrivers = new Set<number>();
        return options
            .filter((option) => {
                if (seenDrivers.has(option.driver_id)) return false;
                seenDrivers.add(option.driver_id);
                return true;
            })
            .map((option) => {
                return {
                    value: option.driver_id,
                    label: option.driver_id,
                };
            });
    };

    const getRunIdByObjId = (id: string) => {
        const runId = (inputs.filter((input) => input.id == id)[0] as runIdInput).runId;
        return runId;
    };
    const getDriverIdByObjId = (id: string) => {
        const driverId = (inputs.filter((input) => input.id == id)[0] as DriverSessionInput).driverId;
        return driverId;
    };

    const getStartTimeByObjId = (id: string) => {
        const startTimes = (inputs.filter((input) => input.id == id)[0] as DriverSessionInput).startTimes;
        return startTimes;
    };
    const getValidStartTimeOptions = (id: string) => {
        const driverId = getDriverIdByObjId(id);
        const availableStartTimes = availableRunsData
            .filter((run) => {
                return run.driver_id === driverId;
            })
            .map((run) => run.start_time.getTime());

        const session = inputs.filter((input) => input.id == id)[0] as DriverSessionInput;
        const selectedStartTimes = session.startTimes.map((startTime) => startTime.getTime());

        return availableStartTimes
            .filter((startTime) => !selectedStartTimes.includes(startTime))
            .map((startTime) => {
                return { value: new Date(startTime), label: new Date(startTime).toLocaleString() };
            });
    };

    const selectStyles = (width: string) => {
        return {
            container: (provided) => ({
                ...provided,
                width: width, // Stretch horizontally
            }),
        };
    };

    const inputComponents = inputs.map((input) => {
        if ("runId" in input) {
            return (
                <Flex minWidth="max-content" alignItems="center" gap="2">
                    <Select
                        placeholder="e.g 0FPCR7F0SE6K0"
                        chakraStyles={selectStyles("100%")}
                        value={
                            getRunIdByObjId(input.id)
                                ? { value: getRunIdByObjId(input.id), label: getRunIdByObjId(input.id) }
                                : undefined
                        }
                        options={getValidRunIdOptions()}
                        onChange={(e) => {
                            updateInputWithRunId(input.id, e?.value);
                        }}
                    />
                    <IconButton aria-label="Remove" icon={<CloseIcon />} onClick={() => removeInputById(input.id)} />{" "}
                </Flex>
            );
        } else {
            return (
                <Grid templateColumns="5fr 8fr 1fr" gap={2}>
                    <Box>
                        <Select
                            placeholder="Select Driver ID"
                            value={
                                getDriverIdByObjId(input.id)
                                    ? { value: getDriverIdByObjId(input.id), label: getDriverIdByObjId(input.id) }
                                    : undefined
                            }
                            options={getValidDriverIdOptions()}
                            onChange={(e) => updateInputWithDriverId(input.id, e?.value)}
                        />
                    </Box>
                    <Box>
                        <Select
                            isMulti
                            placeholder="Select start time"
                            value={
                                getStartTimeByObjId(input.id)
                                    ? getStartTimeByObjId(input.id).map((date: Date) => {
                                          return {
                                              value: date,
                                              label: date.toLocaleString(),
                                          };
                                      })
                                    : undefined
                            }
                            options={getValidStartTimeOptions(input.id)}
                            isDisabled={!getDriverIdByObjId(input.id)}
                            onChange={(e) => updateInputWithStartTime(input.id, e?.values())}
                        />
                    </Box>
                    <Box>
                        <IconButton
                            aria-label="Remove"
                            icon={<CloseIcon />}
                            onClick={() => removeInputById(input.id)}
                        />{" "}
                    </Box>
                </Grid>
            );
        }
    });

    return (
        <>
            <Modal onClose={onClose} isOpen={isOpen} size="2xl">
                <ModalOverlay />
                <ModalContent>
                    <ModalCloseButton />
                    <DrawerHeader>{`Select Driving Sessions to display Driver Scores`}</DrawerHeader>
                    <ModalBody>
                        {inputComponents}
                        <Flex justifyContent="center" mt="5">
                            <Menu>
                                <MenuButton as={Button} rightIcon={<AddIcon />}>
                                    Add
                                </MenuButton>
                                <MenuList>
                                    <MenuItem onClick={addRunIdInput}>Run ID</MenuItem>
                                    <MenuItem onClick={addDriverSessionInput}>Driver Session</MenuItem>
                                </MenuList>
                            </Menu>
                            <Button
                                ml={4}
                                colorScheme="teal"
                                onClick={() => {
                                    const runIds = [];
                                    for (const input of inputs) {
                                        if ("driverId" in input) {
                                            runIds.push(...input.runIds);
                                        } else {
                                            const runId = (input as runIdInput).runId;
                                            if (runId !== undefined) runIds.push(runId);
                                        }
                                    }
                                    onClose();
                                    setFetchRunIds(runIds);
                                    setDisplayRunIds(runIds);
                                    setDisplayDirections(runIds.map(() => ["increasing", "decreasing"]));
                                }}
                            >
                                View
                            </Button>
                        </Flex>
                    </ModalBody>
                </ModalContent>
            </Modal>
        </>
    );
}
