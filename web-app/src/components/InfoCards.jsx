function InfoCards(){
    return (
        <section className="mt-20">
            <p className="text-center outfit-regular text-5xl">How it Works ?</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 px-12 sm:px-25 py-10">

                <div className="bg-white shadow-xl rounded-xl p-5">
                    <p className="bg-black text-white font-bold anton-regular rounded-full w-8 h-8 flex items-center justify-center">
                        1
                    </p>
                    <img src="web-search.jpg" className="h-26 grayscale hover:grayscale-0 transition ms-auto me-auto"/>
                    <h3 className="mt-4 text-center font-semibold outfit-regular text-2xl">Discover</h3>
                    <p className="text-center outfit-regular mt-2 w-50 ms-auto me-auto">
                        Find clothing from multiple sources gathered in one place.
                    </p>
                </div>

                <div className="bg-white shadow-xl rounded-xl p-4">
                    <p className="bg-black text-white font-bold anton-regular rounded-full w-8 h-8 flex items-center justify-center">
                        2
                    </p>
                    <img src="clothes-select.jpg" className="h-26 grayscale hover:grayscale-0 transition ms-auto me-auto"/>
                    <h3 className="mt-4 text-center font-semibold outfit-regular text-2xl">Select</h3>
                    <p className="text-center outfit-regular mt-2 w-50 ms-auto me-auto">
                        Use filters and tools to choose what matches your needs.
                    </p>
                </div>

                <div className="bg-white shadow-xl rounded-xl p-4">
                    <p className="bg-black text-white font-bold anton-regular rounded-full w-8 h-8 flex items-center justify-center">
                        3
                    </p>
                    <img src="try-out.jpg" className="h-26 grayscale hover:grayscale-0 transition ms-auto me-auto"/>
                    <h3 className="mt-4 text-center font-semibold outfit-regular text-2xl">Try Out</h3>
                    <p className="text-center outfit-regular mt-2 w-50 ms-auto me-auto">
                        Try your selected items in one place using artificial intelligence.
                    </p>
                </div>

                <div className="bg-white shadow-xl rounded-xl p-4">
                    <p className="bg-black text-white font-bold anton-regular rounded-full w-8 h-8 flex items-center justify-center">
                        4
                    </p>
                    <img src="checkout.jpg" className="h-26 grayscale hover:grayscale-0 transition ms-auto me-auto"/>
                    <h3 className="mt-4 text-center font-semibold outfit-regular text-2xl">Purchase</h3>
                    <p className="text-center outfit-regular mt-2 w-50 ms-auto me-auto">
                        Checkout and buy the items you selected without leaving the platform.
                    </p>
                </div>

            </div>
        </section>
    );
}

export { InfoCards };
