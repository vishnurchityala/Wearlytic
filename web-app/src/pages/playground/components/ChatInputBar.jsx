import { useState } from "react";
import { apiFetch } from "@/api/env";
import { useAuth } from "@/auth/AuthContext";

const IMAGE_GENERATION_ALLOWED_ROLE = "super_user";

const noticeStyles = {
    success: "border-emerald-200 bg-emerald-50 text-emerald-800",
    warning: "border-amber-200 bg-amber-50 text-amber-800",
    error: "border-red-200 bg-red-50 text-red-700",
};

async function readErrorDetail(response) {
    try {
        const data = await response.json();
        return data.detail || data.result || "Image generation was blocked. No credits were charged.";
    } catch {
        return "Image generation was blocked. No credits were charged.";
    }
}

function ChatInputBar({ setImageGenerations, selectedProducts }) {
    const [value, setValue] = useState("");
    const [loading, setLoading] = useState(false);
    const [notice, setNotice] = useState(null);

    const { token } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();

        const trimmed = value.trim();
        if (!trimmed || loading) return;

        setNotice(null);
        setLoading(true);

        try {
            const meRes = await apiFetch(
                "/api/users/me",
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            );

            if (!meRes.ok) {
                setNotice({
                    type: "error",
                    message: "Could not verify your role. No generation was started.",
                });
                return;
            }

            const me = await meRes.json();

            if (me.role !== IMAGE_GENERATION_ALLOWED_ROLE) {
                setNotice({
                    type: "warning",
                    message: "Image generation is guarded for Super Users only. No credits were charged.",
                });
                return;
            }

            if (selectedProducts.length === 0) {
                setNotice({
                    type: "warning",
                    message: "Select at least one product before generating. No credits were charged.",
                });
                return;
            }

            const payload = {
                custom_prompt: trimmed,
                input_products: selectedProducts,
            };

            const genRes = await apiFetch(
                "/api/image_generations/",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${token}`,
                    },
                    body: JSON.stringify(payload),
                }
            );

            if (!genRes.ok) {
                const detail = await readErrorDetail(genRes);
                setNotice({
                    type: genRes.status === 403 ? "warning" : "error",
                    message: detail,
                });
                return;
            }

            const result = await genRes.json();

            if ("status" in result) {
                console.error("Generation failed:", result);
                setNotice({
                    type: "error",
                    message: "Image generation failed before completion. No credits were charged.",
                });
                return;
            }

            setImageGenerations((prev) => [...prev, result]);
            setValue("");
            setNotice({
                type: "success",
                message: "Your image is ready. Super Users are not charged credits for generation.",
            });
        } catch (err) {
            console.error("Image generation error:", err.message);
            setNotice({
                type: "error",
                message: "Image generation could not be completed. Check your generation history before trying again.",
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <form
            onSubmit={handleSubmit}
            className="w-full px-2 md:px-6 py-4 flex items-center justify-center bg-white"
        >
            <div className="w-full max-w-5xl relative">
                <div className="flex items-center rounded-full px-3 py-2 shadow-sm border-2 border-gray-200">

                    <input
                        type="text"
                        placeholder="Custom Prompt for Try Out (Prompt Well for Results)"
                        value={value}
                        onChange={(e) => setValue(e.target.value)}
                        disabled={loading}
                        className="flex-1 bg-transparent text-gray-700 outline-none text-xs md:text-sm mx-3 outfit-regular disabled:opacity-60"
                    />

                    <button
                        type="submit"
                        disabled={loading}
                        className={`py-2 px-4 outfit-regular text-xs md:text-sm rounded-full flex items-center justify-center gap-2 transition
                            ${loading
                                ? "bg-black text-white cursor-not-allowed"
                                : "bg-black text-white hover:bg-gray-900 cursor-pointer"
                            }`}
                    >
                        {loading ? (
                            <>
                                <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                Generating
                            </>
                        ) : (
                            <>
                                Generate
                            </>
                        )}
                    </button>

                </div>

                {notice && (
                    <p
                        role="status"
                        aria-live="polite"
                        className={`mt-2 rounded-md border px-3 py-2 text-xs outfit-regular ${noticeStyles[notice.type]}`}
                    >
                        {notice.message}
                    </p>
                )}
            </div>
        </form>
    );
}

export { ChatInputBar };
