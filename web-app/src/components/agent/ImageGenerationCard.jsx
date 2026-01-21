function ImageGenerationCard({ imageGeneration }) {
    const openImage = () => {
        window.open(imageGeneration.image, "_blank", "noopener,noreferrer");
    };

    return (
        <img
            src={imageGeneration.image}
            alt="Generated"
            onClick={openImage}
            className="shrink-0 max-w-55 shadow-sm object-contain rounded-md cursor-pointer"
        />
    );
}

export { ImageGenerationCard };
