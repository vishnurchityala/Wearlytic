import { useState } from "react";
import { ChatInputBar } from "./ChatInputBar";
import { TryoutCanvas } from "./TryoutCanvas";

function PlaygroundSection({selectedProducts}) {
    const [imageGenerations,setImageGenerations] = useState([]);
    return (
        <div className="h-full flex flex-col p-2">
            <div className="flex-1">
                <TryoutCanvas />
            </div>

            <ChatInputBar />
        </div>
    );
}

export { PlaygroundSection };
