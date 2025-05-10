import { Box, IconButton, Menu, MenuButton, MenuItem, MenuList } from "@chakra-ui/react";
import { FiLogOut, FiUser } from "react-icons/fi";

import { FaUserAstronaut } from "react-icons/fa";
import { Link } from "@tanstack/react-router";

// import useAuth from "../../hooks/useAuth";

const UserMenu = () => {
    // TODO: mock logout
    // const { logout } = useAuth();
    const logout = () => true;

    const handleLogout = async () => {
        logout();
    };

    return (
        <>
            {/* Desktop */}
            <Box display={{ base: "none", md: "block" }} position="fixed" top={4} right={4}>
                <Menu>
                    <MenuButton
                        as={IconButton}
                        aria-label="Options"
                        icon={<FaUserAstronaut color="white" fontSize="18px" />}
                        bg="ui.main"
                        isRound
                    />
                    <MenuList>
                        <MenuItem icon={<FiUser fontSize="18px" />} as={Link} to="settings">
                            My profile
                        </MenuItem>
                        <MenuItem
                            icon={<FiLogOut fontSize="18px" />}
                            onClick={handleLogout}
                            color="ui.danger"
                            fontWeight="bold"
                        >
                            Log out
                        </MenuItem>
                    </MenuList>
                </Menu>
            </Box>
        </>
    );
};

export default UserMenu;
