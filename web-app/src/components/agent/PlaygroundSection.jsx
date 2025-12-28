import { ChatInputBar } from "./ChatInputBar";
import { TryoutCanvas } from "./TryoutCanvas";

function PlaygroundSection(){
    return (
        <section className="w-full h-full flex flex-col bg-white">
            <div className="flex-1 overflow-hidden">
                <TryoutCanvas />
            </div>
            <ChatInputBar />
        </section>
    );
}

export { PlaygroundSection };
