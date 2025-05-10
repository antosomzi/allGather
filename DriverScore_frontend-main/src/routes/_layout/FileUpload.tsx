import {
    Box,
    Button,
    Container,
    Flex,
    FormControl,
    FormLabel,
    Heading,
    Input,
    Text,
    useColorModeValue,
} from "@chakra-ui/react";
import { ChangeEvent, useState } from "react";

import { AllGatherService } from "../../client";
import { createFileRoute } from "@tanstack/react-router";
import { type SubmitHandler, useForm } from "react-hook-form";
import useCustomToast from "../../hooks/useCustomToast";

export const Route = createFileRoute("/_layout/FileUpload")({
    component: FileUpload,
});
const convertFileToBlob = (file: File): Promise<Blob> => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
            const blob = new Blob([reader.result as ArrayBuffer], {
                type: file.type,
            });
            resolve(blob);
        };
        reader.onerror = () => {
            reject(new Error("Failed to convert File to Blob"));
        };
        reader.readAsArrayBuffer(file);
    });
};

function FileUpload() {
    const {
        handleSubmit,
        formState: { isSubmitting },
    } = useForm<FormData>();
    const showToast = useCustomToast();

    const [file, setFile] = useState<File | null>(null);

    const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            setFile(e.target.files[0]);
        }
    };

    const onSubmit: SubmitHandler<FormData> = async () => {
        if (file === null) {
            throw new Error("File not selected!");
        }

        const blobFile: Blob = await convertFileToBlob(file);
        await AllGatherService.upload({
            formData: { file: blobFile },
        });
        showToast("File Uploaded", `Uploaded ${file.name}`, "success");
    };

    const bgColor = useColorModeValue("gray.100", "gray.700");
    const borderColor = useColorModeValue("gray.200", "gray.600");

    return (
        <>
            <Container maxW="full" as="form" onSubmit={handleSubmit(onSubmit)}>
                <Flex justify="center" align="center" minHeight="100vh">
                    <Box
                        p={8}
                        borderWidth={1}
                        borderRadius="lg"
                        boxShadow="lg"
                        bg={bgColor}
                        borderColor={borderColor}
                        maxWidth="500px"
                        width="100%"
                    >
                        <Heading as="h2" size="xl" textAlign="center" mb={6}>
                            Location File Upload
                        </Heading>
                        <FormControl>
                            <FormLabel>Select a file</FormLabel>
                            <Input type="file" onChange={handleFileChange} variant="filled" mb={4} />
                            {file && (
                                <Text fontSize="sm" color="gray.500" mb={4}>
                                    Selected file: {file.name}
                                </Text>
                            )}
                            <Button
                                type="submit"
                                disabled={!file}
                                isLoading={isSubmitting}
                                colorScheme="blue"
                                width="100%"
                            >
                                Upload
                            </Button>
                        </FormControl>
                    </Box>
                </Flex>
            </Container>
        </>
    );
}

export default FileUpload;
