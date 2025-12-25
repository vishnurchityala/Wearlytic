function HeroBanner() {
  return (
    <section className="min-h-[calc(95vh-5rem)] my-4 flex flex-col text-center">
      <div className="flex-1 flex flex-col items-center justify-center -mt-4">
        <p className="bbh-bartle-regular text-4xl sm:text-[70px]">
          Try Any Outfit Instantly
        </p>

        <p
          className="anton-regular text-6xl md:text-8xl text-gray-800"
          style={{
            WebkitTextStroke: "1.5px black",
            color: "transparent",
          }}
        >
          Clothes at your fingertips
        </p>

        <button className="mt-6 px-7 py-3 text-lg text-white bg-black rounded-full outfit-regular">
          Get Started <span className="px-1 font-bold">→</span>
        </button>
      </div>

      <div className="flex flex-col items-center gap-3">
        <div className="flex items-center justify-center gap-6 opacity-80 ">
          <img src="/brands/hm.png" alt="H&M" className="h-8 sm:h-15 transition duration-250" />
          <img src="/brands/amazon.png" alt="Amazon Fashion" className="h-8 sm:h-15 transition duration-250" />
          <img src="/brands/myntra.png" alt="Myntra" className="h-8 sm:h-15 transition duration-250" />
          <img src="/brands/souledstore.png" alt="Souled Store" className="h-8 sm:h-15 transition duration-250" />
          <img src="/brands/bluorng.png" alt="BluOrng" className="h-8 sm:h-16 transition duration-250" />
        </div>

        <p className="mt-3 text-sm underline text-gray-600 font-medium outfit-regular">
          Aggregated fashion data from leading online retailers
        </p>
      </div>
    </section>
  );
}

export { HeroBanner };
