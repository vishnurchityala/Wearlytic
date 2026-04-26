function PastImageGenerationCard({ imageGeneration }) {
    const { image, task, created_at } = imageGeneration;

    return (
        <div className="border-2 border-gray-300 rounded-lg p-3 mb-4 bg-white outfit-regular shadow-sm">
            <div className="flex flex-col md:flex-row gap-4">
                
                <div className="md:w-1/3 flex justify-center">
                    <img
                        src={image}
                        alt="Generated"
                        onClick={() => window.open(image, "_blank", "noopener,noreferrer")}
                        className="w-full max-w-65 md:max-w-[320px] object-contain rounded-md cursor-pointer"
                    />
                </div>

                <div className="md:w-2/3">
                    <div className="mb-3">
                        <p className="text-sm uppercase tracking-wide text-gray-500 mb-1">
                            Custom Prompt
                        </p>
                        <p className="text-sm text-gray-700 leading-relaxed">
                            {task.custom_prompt || "—"}
                        </p>

                        <p className="text-xs text-gray-500 mt-2">
                            Generated on{" "}
                            {new Date(created_at).toLocaleString()}
                        </p>
                    </div>

                    <p className="text-sm uppercase tracking-wide text-gray-500 mb-2">
                        Products Used
                    </p>

                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                        {task.products.map(product => (
                            <div
                                key={product.id}
                                className="border-2 border-gray-300 rounded-md p-2 shadow-xs"
                            >
                                <div className="w-full h-28 sm:h-32 flex items-center justify-center mb-2 border border-gray-200 rounded-md overflow-hidden bg-white">
                                    <img
                                        src={product.image_url}
                                        alt={product.title}
                                        className="max-h-full max-w-full object-contain"
                                    />
                                </div>

                                <p className="text-base font-medium text-gray-800 line-clamp-2 mb-1">
                                    {product.title}
                                </p>

                                <p className="text-sm font-semibold text-gray-900 mb-2">
                                    ₹ {product.price}
                                </p>

                                <div className="flex justify-start">
                                    <a
                                        href={product.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-xs px-2 py-1 rounded-xl outfit-regular bg-black text-white hover:bg-gray-900 transition-colors"
                                        title="View"
                                    >
                                        View
                                    </a>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

export { PastImageGenerationCard };
