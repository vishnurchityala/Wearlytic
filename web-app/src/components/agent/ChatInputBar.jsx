import { useState } from "react";

function ChatInputBar({ onSubmit }) {
    const [value, setValue] = useState("");

    const handleSubmit = (e) => {
        e.preventDefault();
        const trimmed = value.trim();
        if (!trimmed) return;
        if (onSubmit) onSubmit(trimmed);
        setValue("");
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
                        placeholder="Custom Prompt for Try Out  (Prompt Well for Results)"
                        value={value}
                        onChange={(e) => setValue(e.target.value)}
                        className="flex-1 bg-transparent text-gray-700 outline-none text-sm mx-3 outfit-regular"
                    />

                    <button
                        type="submit"
                        className="py-2 px-3 outfit-regular text-sm rounded-full flex items-center justify-center bg-black text-white cursor-pointer"
                    >
                        Generate <span className="px-1 text-lg">↑</span>
                    </button>
                </div>
            </div>
        </form>
    );
}

export { ChatInputBar };
