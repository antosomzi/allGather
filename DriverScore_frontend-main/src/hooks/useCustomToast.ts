import { useCallback } from "react";
import { useToast } from "@chakra-ui/react";

const useCustomToast = () => {
    const toast = useToast();

    const showToast = useCallback(
        (title: string, description: string, status: "success" | "error") => {
            toast({
                title,
                description,
                status,
                isClosable: true,
                position: "bottom-right",
            });
        },
        [toast],
    );

    return showToast;
};

export default useCustomToast;
