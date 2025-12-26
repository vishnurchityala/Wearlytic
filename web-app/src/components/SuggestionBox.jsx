function SuggestionBox() {
    return (
        <section className="mb-20 flex justify-center">
            <div className="bg-gray-200 shadow px-5 py-10 w-[90%] sm:w-[75%] rounded-4xl flex flex-col items-center text-center">
                <p className="outfit-regular font-bold text-2xl sm:text-3xl md:text-4xl">
                    Didn't find what you were looking for ?
                </p>

                <p className="outfit-regular font-light mt-4 text-base sm:text-lg md:text-xl w-full sm:w-[70%] md:w-[50%]">
                    Our team is dedicated to provide personalised answers and discuss your specific needs.
                </p>

                <button className="mt-6 px-6 py-3 text-base sm:text-lg text-white bg-black rounded-full outfit-regular">
                    Contact Us <span className="px-1 font-bold">→</span>
                </button>
            </div>
        </section>
    );
}

export { SuggestionBox };
