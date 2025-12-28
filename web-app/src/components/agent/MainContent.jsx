import { useState } from "react";
import { ClothesSection } from "./ClothesSection";
import { PlaygroundSection } from "./PlaygroundSection";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faChevronDown, faChevronUp } from "@fortawesome/free-solid-svg-icons";

function MainContent() {
    const [showClothes, setShowClothes] = useState(false);

    return (
        <main className="w-full h-[90%] flex flex-col lg:flex-row gap-2 px-3">

            <div className="w-full py-2 lg:w-[40%] border border-gray-300 rounded-lg shadow-md overflow-hidden flex flex-col">

                <div
                    className="flex items-center justify-between px-4 mb-2 cursor-pointer"
                    onClick={() => setShowClothes(!showClothes)}
                >
                    <span className="font-medium text-gray-800 outfit-regular">Clothes</span>
                    <FontAwesomeIcon
                        icon={showClothes ? faChevronUp : faChevronDown}
                        className="text-gray-800 lg:hidden"
                    />
                </div>

                <div
                    className={`overflow-y-auto transition-all duration-300 
                    ${showClothes ? "max-h-500" : "max-h-0"} 
                    lg:max-h-500`}
                >
                    <ClothesSection />
                </div>
            </div>

            <section className="w-full lg:w-[60%] h-full flex flex-col">
                <PlaygroundSection />
            </section>

        </main>
    );
}

export { MainContent };
