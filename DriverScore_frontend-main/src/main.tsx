import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { RouterProvider, createRouter } from "@tanstack/react-router";

import { ChakraProvider } from "@chakra-ui/react";
import { OpenAPI } from "./client";
import ReactDOM from "react-dom/client";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { StrictMode } from "react";
import { registerLicense } from "@syncfusion/ej2-base";
import { routeTree } from "./routeTree.gen";
import theme from "./theme";

OpenAPI.BASE = import.meta.env.VITE_API_URL;
// Configure the maximum upload size
OpenAPI.TOKEN = async () => {
    return localStorage.getItem("access_token") || "";
};

const queryClient = new QueryClient();

const router = createRouter({ routeTree });
declare module "@tanstack/react-router" {
    interface Register {
        router: typeof router;
    }
}


// Registering Syncfusion license key
registerLicense("Ngo9BigBOggjHTQxAR8/V1NBaF1cXmhIfEx1RHxQdld5ZFRHallYTnNWUj0eQnxTdEFjXH5ecHJWR2RZVExzXA==");

ReactDOM.createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <ChakraProvider theme={theme}>
            <QueryClientProvider client={queryClient}>
                <RouterProvider router={router} />
                <ReactQueryDevtools initialIsOpen={false} />
            </QueryClientProvider>
        </ChakraProvider>
    </StrictMode>,
);
