import { Container, Stack } from "@chakra-ui/react";
import { MapContainer, TileLayer } from "react-leaflet";

import { Box } from "@chakra-ui/react";
import { LatLng } from "leaflet";

export default function EmptyMap({ center }: { center: LatLng }) {
    return (
        <Container maxW="full">
            <Box pt={12} m={4}>
                <Stack>
                    <MapContainer
                        style={{ height: "90vh" }}
                        zoom={5}
                        center={center}
                        zoomControl={false}
                        scrollWheelZoom={true}
                    >
                        <TileLayer
                            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        />
                    </MapContainer>
                </Stack>
            </Box>
        </Container>
    );
}
