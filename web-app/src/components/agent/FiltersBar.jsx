function FiltersBar() {
    return (
        <div className="w-full bg-white px-4 pb-4 space-y-3 text-xs">
            <div>
                <input
                    type="text"
                    placeholder="Search using Prompt"
                    className="w-full px-3 py-1 text-sm rounded-full border border-gray-300 outline-none outfit-regular"
                />
            </div>
            <div className="space-y-1">
                <div className="font-medium text-gray-800 outfit-regular">Category</div>
                <div className="flex flex-wrap gap-1.5">
                    <button className="px-2.5 py-0.5 rounded-full border border-gray-300">T-shirts</button>
                    <button className="px-2.5 py-0.5 rounded-full border border-gray-300">Jackets</button>
                    <button className="px-2.5 py-0.5 rounded-full border border-gray-300">Shirts</button>
                    <button className="px-2.5 py-0.5 rounded-full border border-gray-300">Hoodies</button>
                    <button className="px-2.5 py-0.5 rounded-full border border-gray-300">Sweatshirts</button>
                    <button className="px-2.5 py-0.5 rounded-full border border-gray-300">Jumpers</button>
                    <button className="px-2.5 py-0.5 rounded-full border border-gray-300">Trousers</button>
                    <button className="px-2.5 py-0.5 rounded-full border border-gray-300">Jeans</button>
                    <button className="px-2.5 py-0.5 rounded-full border border-gray-300">Joggers</button>
                    <button className="px-2.5 py-0.5 rounded-full border border-gray-300">Vests</button>
                    <button className="px-2.5 py-0.5 rounded-full border border-gray-300">Shorts</button>
                </div>
            </div>

            <div className="space-y-1">
                <div className="font-medium text-gray-800 outfit-regular">Style</div>
                <div className="flex flex-wrap gap-1.5">
                    <button className="px-2.5 py-0.5 rounded-full border border-gray-300">Regular</button>
                    <button className="px-2.5 py-0.5 rounded-full border border-gray-300">Oversized</button>
                    <button className="px-2.5 py-0.5 rounded-full border border-gray-300">Slim</button>
                    <button className="px-2.5 py-0.5 rounded-full border border-gray-300">Relaxed</button>
                </div>
            </div>

            <div className="space-y-1">
                <div className="font-medium text-gray-800 outfit-regular">Brand</div>
                <div className="flex flex-wrap gap-1.5">
                    {["Nike","Adidas","Yeezy","New Balance","Balenciaga","Off-White"]
                        .map(b => (
                            <button key={b} className="px-2.5 py-0.5 rounded-full border border-gray-300">{b}</button>
                        ))
                    }
                </div>
            </div>

            <div className="space-y-1">
                <div className="font-medium text-gray-800 outfit-regular">Color</div>
                <div className="flex flex-wrap gap-1.5">
                    {["blue","red","green","yellow","brown","pink","purple","black","white","gray"].map(c => (
                        <button 
                            key={c} 
                            className="flex items-center gap-1.5 px-1.5 py-0.5 rounded-full border border-gray-300"
                        >
                            <span 
                                className="w-2.5 h-2.5 rounded-full" 
                                style={{ backgroundColor: c }} 
                            />
                            {c[0].toUpperCase() + c.slice(1)}
                        </button>
                    ))}
                </div>
            </div>

            <div className="space-y-1">
                <div className="font-medium text-gray-800 outfit-regular">Size</div>
                <div className="flex flex-wrap gap-1.5">
                    {["XS","S","M","L","XL","XXL","36","38","40","42","44","46"].map(s => (
                        <button key={s} className="px-2.5 py-0.5 rounded-full border border-gray-300">{s}</button>
                    ))}
                </div>
            </div>

            <div className="space-y-1">
                <div className="font-medium text-gray-800 outfit-regular">Price Range</div>

                <div className="flex items-center gap-2">
                    <input
                        type="number"
                        placeholder="Min"
                        className=" px-2 py-1 rounded-full border border-gray-300 text-[11px] outline-none outfit-regular"
                    />
                    <span className="text-[11px] text-gray-700">to</span>
                    <input
                        type="number"
                        placeholder="Max"
                        className="px-2 py-1 rounded-full border border-gray-300 text-[11px] outline-none outfit-regular"
                    />
                </div>
            </div>


        </div>
    );
}

export { FiltersBar };
