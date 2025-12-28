function TryoutCanvas(){
    return (
        <div 
            className="
                w-full h-full
                flex items-center justify-center
                rounded-xl
                border border-gray-300
                bg-[radial-gradient(circle,rgba(0,0,0,0.12)_1px,transparent_1px)]
                bg-size-[12px_12px]
            "
        >
            <p className="text-gray-600">Canvas Output</p>
        </div>
    );
}

export { TryoutCanvas };
