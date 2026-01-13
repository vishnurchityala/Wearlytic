import { ChatInputBar } from "./ChatInputBar";
import { TryoutCanvas } from "./TryoutCanvas";

function PlaygroundSection() {
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
