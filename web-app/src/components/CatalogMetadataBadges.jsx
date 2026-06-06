import { useEffect, useState } from "react";
import { getCatalogMetadata } from "@/api/catalog";

function formatProductCount(value) {
    if (typeof value !== "number" || Number.isNaN(value)) {
        return "Catalog stats unavailable";
    }

    return `${new Intl.NumberFormat().format(value)} products`;
}

function formatLastFetched(value) {
    if (!value) {
        return "Last data fetched: pending";
    }

    const fetchedAt = new Date(value);
    if (Number.isNaN(fetchedAt.getTime())) {
        return "Last data fetched: unavailable";
    }

    return `Updated ${new Intl.DateTimeFormat(undefined, {
        month: "short",
        day: "numeric",
        year: "numeric",
    }).format(fetchedAt)}`;
}

function CatalogMetadataBadges({ align = "center", className = "", variant = "default" }) {
    const [metadata, setMetadata] = useState(null);
    const [status, setStatus] = useState("loading");

    useEffect(() => {
        let isActive = true;

        async function fetchMetadata() {
            try {
                const data = await getCatalogMetadata();
                if (!isActive) return;
                setMetadata(data);
                setStatus("ready");
            } catch (error) {
                console.error("Catalog metadata error:", error);
                if (!isActive) return;
                setStatus("error");
            }
        }

        fetchMetadata();

        return () => {
            isActive = false;
        };
    }, []);

    const justifyClass = align === "start" ? "justify-start" : "justify-center";

    const isCompact = variant === "compact";
    const isHero = variant === "hero";
    const wrapperClass = isCompact
        ? `min-w-0 ${className}`
        : `flex flex-wrap ${justifyClass} gap-2 ${className}`;
    const badgeClass = isCompact
        ? "inline-flex max-w-full items-center gap-1.5 rounded-full border border-gray-200 bg-gray-50 px-2 py-0.5 text-[10px] text-gray-500 outfit-regular"
        : isHero
            ? "inline-flex items-center gap-2 rounded-full border border-gray-200 bg-white/85 px-4 py-2 text-sm text-gray-700 shadow-sm outfit-regular"
            : "rounded-full border border-gray-200 bg-white px-3 py-1 text-xs text-gray-700 shadow-sm outfit-regular";

    if (status === "loading") {
        if (isCompact || isHero) {
            return (
                <div className={wrapperClass}>
                    <span className={badgeClass}>Catalog stats loading</span>
                </div>
            );
        }

        return (
            <div className={wrapperClass}>
                <span className="rounded-full border border-gray-200 bg-white px-3 py-1 text-xs text-gray-500 outfit-regular">
                    Loading catalog stats
                </span>
                <span className="rounded-full border border-gray-200 bg-white px-3 py-1 text-xs text-gray-500 outfit-regular">
                    Last data fetched: loading
                </span>
            </div>
        );
    }

    if (status === "error") {
        return (
            <div className={wrapperClass}>
                <span className={isCompact || isHero ? badgeClass : "rounded-full border border-gray-200 bg-white px-3 py-1 text-xs text-gray-500 outfit-regular"}>
                    Catalog stats unavailable
                </span>
            </div>
        );
    }

    if (isCompact || isHero) {
        return (
            <div className={wrapperClass}>
                <span className={badgeClass}>
                    <span className="truncate">{formatProductCount(metadata?.product_count)}</span>
                    <span className="text-gray-300">•</span>
                    <span className="truncate">{formatLastFetched(metadata?.last_data_fetched)}</span>
                </span>
            </div>
        );
    }

    return (
        <div className={wrapperClass}>
            <span className="rounded-full border border-gray-200 bg-white px-3 py-1 text-xs text-gray-700 shadow-sm outfit-regular">
                {formatProductCount(metadata?.product_count)} cataloged
            </span>
            <span className="rounded-full border border-gray-200 bg-white px-3 py-1 text-xs text-gray-700 shadow-sm outfit-regular">
                {formatLastFetched(metadata?.last_data_fetched)}
            </span>
        </div>
    );
}

export { CatalogMetadataBadges };
