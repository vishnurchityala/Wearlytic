import { apiFetch } from "./env";

export { API_BASE_URL, apiFetch, apiUrl } from "./env";

export async function getCurrentUserProfile(token) {
    const response = await apiFetch("/users/me", {
        headers: {
            "Authorization": token ? `Bearer ${token}` : undefined
        }
    });
    if (!response.ok) {
        const text = await response.text().catch(() => "");
        throw new Error(text || `Failed to load profile (${response.status})`);
    }
    return await response.json();
}
