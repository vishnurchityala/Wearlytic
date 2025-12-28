import { Navbar } from "../components/general/Navbar";
import { MainContent } from "../components/agent/MainContent";

function AgentPage() {
    return (
        <div className="w-screen h-screen flex flex-col">
            <Navbar />
            <MainContent />
        </div>
    );
}

export { AgentPage };
