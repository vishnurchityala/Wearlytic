import { ImageGenerationCard } from "./ImageGenerationCard";

function TryoutCanvas({ imageGenerations }) {
    return (
        <div
            className="
				w-full h-full
				max-h-[65vh] md:max-h-none
				overflow-auto
                rounded-xl border border-gray-200
                bg-[radial-gradient(circle,rgba(0,0,0,0.12)_1px,transparent_1px)]
                bg-size-[12px_12px]
                p-4
            "
        >
            {imageGenerations.length === 0 ? (
				<div className="h-full w-full flex items-center justify-center">
					<p className="text-gray-600">Canvas Output</p>
				</div>
            ) : (
				<div className="min-h-full min-w-full flex items-center justify-center">
					<div className="flex flex-wrap justify-center items-start gap-3 content-start">
						{imageGenerations.map((item, index) => (
							<ImageGenerationCard
								key={item.id}
								imageGeneration={item}
							/>
						))}
					</div>
				</div>
            )}
        </div>
    );
}

export { TryoutCanvas };
