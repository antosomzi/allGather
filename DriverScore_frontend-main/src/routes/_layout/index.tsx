import { Box, Container } from "@chakra-ui/react";
import { GroupingBar, IDataOptions, IDataSet, Inject, PivotViewComponent } from "@syncfusion/ej2-react-pivotview";

import { SummaryService } from "@/client";
// import type { UserOut } from "../../client";
import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";

// import { useQueryClient } from "@tanstack/react-query";

export const Route = createFileRoute("/_layout/")({
    component: Dashboard,
});

function Dashboard() {
    // TODO: Mock for now
    // const queryClient = useQueryClient();
    // const currentUser = queryClient.getQueryData<UserOut>("currentUser");
    const {
        data: summaryByRCTypeData,
        isLoading: isSummaryByRCTypeLoading,
        isError: isSummaryByRCTypeError,
        error: summaryByRCTypeError,
    } = useQuery({
        queryKey: ["summaryByRCRange"],
        queryFn: () => {
            return SummaryService.getSummaryByRcRange();
        },
    });

    if (isSummaryByRCTypeLoading) {
        return <div>Loading...</div>;
    }
    if (isSummaryByRCTypeError) {
        return <div>Error: {summaryByRCTypeError.message}</div>;
    }
	console.log(summaryByRCTypeData);

    const dataSourceSettings = {
        enableSorting: true,
        columns: [
            // { name: "Route", caption: "Route" },
            // { name: "RC", caption: "RC" },
            { name: "RC_range", caption: "RC Range" },
        ],
        rows: [{ name: "driver_id", caption: "Driver ID" }],
        formatSettings: [{ name: "score" }],
        dataSource: summaryByRCTypeData,
        expandAll: false,
        values: [{ name: "score", caption: "Score" }],
        filters: [],
    };

    return (
        <>
            <PivotViewComponent
                id="PivotView"
                // ref={(scope) => {
                //     pivotObj = scope;
                // }}
                dataSourceSettings={dataSourceSettings}
                width={"100%"}
                height={"450"}
                showGroupingBar={true}
                groupingBarSettings={{ showFieldsPanel: true }}
                gridSettings={{ columnWidth: 140 }}
                showValuesButton={true}
            >
                <Inject services={[GroupingBar]} />
            </PivotViewComponent>
            <Container maxW="full">
                <Box pt={12} m={4}></Box>
            </Container>
        </>
    );
}

export default Dashboard;
