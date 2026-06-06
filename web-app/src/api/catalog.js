import { apiFetch } from "./env";

export async function getCatalogMetadata() {
    const response = await apiFetch("/api/catalog/metadata/", {
        headers: {
            Accept: "application/json",
        },
    });

    if (!response.ok) {
        throw new Error("Failed to fetch catalog metadata");
    }

    return response.json();
}
