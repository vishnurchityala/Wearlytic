import { useState } from "react";
import { useAuth } from "../../auth/AuthProvider";

function ChatInputBar({ setImageGenerations, selectedProducts }) {
    const [value, setValue] = useState("");
    const [loading, setLoading] = useState(false);
    const [hasEnoughTokens, setHasEnoughTokens] = useState(true);

    const { token } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();

        const trimmed = value.trim();
        if (!trimmed || loading) return;

        setLoading(true);

        try {
            const meRes = await fetch(
                "https://wearlytic-zbas.onrender.com/api/users/me",
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            );

            if (!meRes.ok) {
                throw new Error("Failed to fetch user data");
            }

            const me = await meRes.json();

            if (me.tokens < 50) {
                setHasEnoughTokens(false);
                setLoading(false);
                return;
            }

            setHasEnoughTokens(true);

            const payload = {
                custom_prompt: trimmed,
                input_products: selectedProducts,
            };

            const genRes = await fetch(
                "https://wearlytic-zbas.onrender.com/api/image_generations/",
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
                throw new Error("Image generation request failed");
            }

            const result = await genRes.json();

            if ("status" in result) {
                console.error("Generation failed:", result);
                return;
            }

            setImageGenerations((prev) => [...prev, result]);
            setValue("");
        } catch (err) {
            console.error("Image generation error:", err.message);
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
                        className="flex-1 bg-transparent text-gray-700 outline-none text-sm mx-3 outfit-regular disabled:opacity-60"
                    />

                    <button
                        type="submit"
                        disabled={loading || !hasEnoughTokens}
                        className={`py-2 px-4 outfit-regular text-xs md:text-sm rounded-full flex items-center justify-center gap-2 transition
                            ${loading || !hasEnoughTokens
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

                {!hasEnoughTokens && (
                    <p className="text-xs text-red-600 mt-2 px-3">
                        You need at least 50 tokens to generate an image.
                    </p>
                )}
            </div>
        </form>
    );
}

export { ChatInputBar };
