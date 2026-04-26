export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/+$/, "");

function toEndpointPath(path) {
    if (!path) return "/";

    try {
        const parsedUrl = new URL(path);
        return `${parsedUrl.pathname}${parsedUrl.search}${parsedUrl.hash}`;
    } catch {
        return path.startsWith("/") ? path : `/${path}`;
    }
}

export function apiUrl(path = "/") {
    const endpointPath = toEndpointPath(path);

    if (!API_BASE_URL) {
        return endpointPath;
    }

    const adjustedPath =
        API_BASE_URL.endsWith("/api") && endpointPath.startsWith("/api/")
            ? endpointPath.slice("/api".length)
            : endpointPath;

    return `${API_BASE_URL}${adjustedPath}`;
}

export function apiFetch(path, options) {
    return fetch(apiUrl(path), options);
}
