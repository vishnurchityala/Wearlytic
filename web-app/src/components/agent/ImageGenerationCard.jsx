function ImageGenerationCard({ imageGeneration }) {
    return (
        <div className="shrink-0 w-45 h-45 sm:w-50 sm:h-50 md:w-56 md:h-56 rounded-lg border border-gray-200 bg-white shadow-sm overflow-hidden hover:shadow-md transition-[transform,box-shadow] duration-200 will-change-transform">
            <div className="h-full w-full flex items-center justify-center text-gray-500 text-sm">
                Preview
            </div>
        </div>
    );
}

export { ImageGenerationCard };
