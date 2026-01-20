import { useState } from "react";
import { ChatInputBar } from "./ChatInputBar";
import { TryoutCanvas } from "./TryoutCanvas";

function PlaygroundSection({selectedProducts}) {
    const [imageGenerations,setImageGenerations] = useState([]);
    const [loading,setLoading] = useState(true);
    return (
        <div className="h-full flex flex-col p-2 overflow-hidden">
            <div className="flex-1 min-h-0">
				<TryoutCanvas imageGenerations={imageGenerations.length ? imageGenerations : undefined} />
            </div>

            <ChatInputBar />
        </div>
    );
}

export { PlaygroundSection };
