import { ClothesSection } from "./ClothesSection";
import { PlaygroundSection } from "./PlaygroundSection";
import { Group, Separator, Panel } from "react-resizable-panels";

function MainContent() {
    return (
        <div className="border-t-2 border-gray-300 h-full">

            <div className="flex flex-col md:hidden h-full">
                <ClothesSection />
                <PlaygroundSection />
            </div>

            <div className="hidden md:flex h-full">
                <Group direction="horizontal" className="h-full w-full">
                    <Panel className="h-full" minSize="20%" defaultSize={40}>
                        <ClothesSection />
                    </Panel>
                    <Separator className="w-1 bg-gray-300 cursor-col-resize" />
                    <Panel className="h-full" minSize="30%" defaultSize={40}>
                        <PlaygroundSection />
                    </Panel>
                </Group>
            </div>

        </div>
    );
}

export { MainContent };
