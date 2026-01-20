export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

export async function getCurrentUserProfile(token) {
    const response = await fetch(`${API_BASE_URL}/users/me`, {
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

