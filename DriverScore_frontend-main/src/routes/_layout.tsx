import { Flex, Spinner } from "@chakra-ui/react";
import { Outlet, createFileRoute, redirect } from "@tanstack/react-router";

import Sidebar from "../components/Common/Sidebar";
import UserMenu from "../components/Common/UserMenu";

// TODO: Mock authorization for now
// import useAuth, { isLoggedIn } from "../hooks/useAuth";
function isLoggedIn(): boolean {
    return true;
}

export const Route = createFileRoute("/_layout")({
    component: Layout,
    beforeLoad: async () => {
        if (!isLoggedIn()) {
            throw redirect({
                to: "/login",
            });
        }
    },
});

function Layout() {
	// TODO: Mock isLoading for now
    // const { isLoading } = useAuth();
	const isLoading = false;

    return (
        <Flex maxW="large" h="auto" position="relative">
            <Sidebar />
            {isLoading ? (
                <Flex justify="center" align="center" height="100vh" width="full">
                    <Spinner size="xl" color="ui.main" />
                </Flex>
            ) : (
                <Outlet />
            )}
            <UserMenu />
        </Flex>
    );
}

export default Layout;
