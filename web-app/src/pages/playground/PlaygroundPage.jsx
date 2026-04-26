import { Navbar } from "@/layout/Navbar";
import { MainContent } from "./components/MainContent";

function PlaygroundPage() {
    return (
        <div className="w-screen h-screen flex flex-col">
            <Navbar />
            <MainContent />
        </div>
    );
}

export default PlaygroundPage;
