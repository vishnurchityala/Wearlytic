import { PastImageGenerationCard } from "./PastImageGenerationCard";

function PastImageGenerations({ pastImageGenerations }) {
    if (!pastImageGenerations || pastImageGenerations.length === 0) {
        return null;
    }

    

    return (
        <div className="w-full">
            {pastImageGenerations.map((generation) => (
                <PastImageGenerationCard
                    key={generation.id}
                    imageGeneration={generation}
                />
            ))}
        </div>
    );
}

export { PastImageGenerations };
