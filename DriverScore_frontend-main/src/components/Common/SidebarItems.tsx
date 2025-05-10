import { Box, Flex, Icon, Text, useColorModeValue } from "@chakra-ui/react";
import { FiHome, FiMap, FiSettings, FiUpload, FiUsers } from "react-icons/fi";

import { Link } from "@tanstack/react-router";

// import type { UserOut } from "../../client";
// import { useQueryClient } from "@tanstack/react-query";

const items = [
    { icon: FiHome, title: "Dashboard", path: "/" },
    { icon: FiUpload, title: "Upload", path: "/FileUpload" },
    { icon: FiMap, title: "Map", path: "/map" },
    { icon: FiSettings, title: "User Settings", path: "/settings" },
];

interface SidebarItemsProps {
    onClose?: () => void;
}

const SidebarItems = ({ onClose }: SidebarItemsProps) => {
    // const queryClient = useQueryClient();
    const textColor = useColorModeValue("ui.main", "ui.white");
    const bgActive = useColorModeValue("#E2E8F0", "#4A5568");
    // TODO: Mock current user
    // const currentUser = queryClient.getQueryData<UserOut>("currentUser");
    const currentUser = { is_superuser: true };

    const finalItems = currentUser?.is_superuser
        ? [...items, { icon: FiUsers, title: "Admin", path: "/admin" }]
        : items;

    const listItems = finalItems.map((item) => (
        <Flex
            as={Link}
            to={item.path}
            w="100%"
            p={2}
            key={item.title}
            activeProps={{
                style: {
                    background: bgActive,
                    borderRadius: "12px",
                },
            }}
            color={textColor}
            onClick={onClose}
        >
            <Icon as={item.icon} alignSelf="center" />
            <Text ml={2}>{item.title}</Text>
        </Flex>
    ));

    return (
        <>
            <Box>{listItems}</Box>
        </>
    );
};

export default SidebarItems;
