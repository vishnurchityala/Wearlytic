import { ChatInputBar } from "./ChatInputBar";
import { TryoutCanvas } from "./TryoutCanvas";

function PlaygroundSection({ selectedProducts, imageGenerations, setImageGenerations }) {
    return (
        <div className="h-full flex flex-col p-2 overflow-hidden">
            <div className="flex-1 min-h-0">
				<TryoutCanvas imageGenerations={imageGenerations} />
            </div>

            <ChatInputBar selectedProducts={selectedProducts} setImageGenerations={setImageGenerations} />
        </div>
    );
}

export { PlaygroundSection };
