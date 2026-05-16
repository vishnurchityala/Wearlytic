const cardData = [
  {
    step: 1,
    image: "web-search.jpg",
    title: "Discover",
    description: "Find clothing from multiple sources gathered in one place."
  },
  {
    step: 2,
    image: "clothes-select.jpg",
    title: "Select",
    description: "Use filters and tools to choose what matches your needs."
  },
  {
    step: 3,
    image: "try-out.jpg",
    title: "Try Out",
    description: "Try your selected items in one place using artificial intelligence."
  },
  {
    step: 4,
    image: "checkout.jpg",
    title: "Purchase",
    description: "Checkout and buy the items you selected without leaving the platform."
  }
];

function InfoCards() {
  return (
    <section className="py-10 sm:py-14">
      <div className="mx-auto max-w-6xl px-4">
        <p className="text-center outfit-regular text-3xl sm:text-5xl mb-8">
          How it Works ?
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {cardData.map(({ step, image, title, description }) => (
            <div
              key={step}
              className="bg-white shadow-md rounded-2xl p-5 h-full flex flex-col"
            >
              <p className="bg-black text-white font-bold text-base sm:text-lg anton-regular rounded-full w-8 h-8 flex items-center justify-center">
                {step}
              </p>

              <div className="h-20 sm:h-24 flex items-center justify-center mt-4">
                <img
                  src={image}
                  alt={title}
                  className="max-h-full max-w-full object-contain"
                />
              </div>

              <h3 className="mt-4 text-center font-semibold outfit-regular text-lg sm:text-xl">
                {title}
              </h3>

              <p className="text-center outfit-regular mt-2 text-sm sm:text-base text-gray-600">
                {description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export { InfoCards };
