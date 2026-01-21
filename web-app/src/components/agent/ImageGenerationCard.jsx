function ImageGenerationCard({ imageGeneration }) {
    return (
        <img
            src={imageGeneration.image}
            alt="Generated"
            className="shrink-0 max-w-55 shadow-sm object-contain rounded-md cursor-pointer"
        />
    );
}

export { ImageGenerationCard };
