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
    <section className="mt-12 sm:mt-20">
      <p className="text-center outfit-regular text-3xl sm:text-6xl mb-6">
        How it Works ?
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 px-4 sm:px-12 py-6 sm:py-10">
        {cardData.map(({ step, image, title, description }) => (
          <div
            key={step}
            className="bg-white shadow-lg rounded-lg p-3 sm:p-4 h-auto"
          >
            <p className="bg-black text-white font-bold text-lg sm:text-2xl anton-regular rounded-full w-8 h-8 sm:w-10 sm:h-10 flex items-center justify-center">
              {step}
            </p>

            <div className="h-20 sm:h-26 flex items-center justify-center mt-3">
              <img
                src={image}
                alt={title}
                className="max-h-full max-w-full object-contain"
              />
            </div>

            <h3 className="mt-3 text-center font-semibold outfit-regular text-lg sm:text-2xl">
              {title}
            </h3>

            <p className="text-center outfit-regular mt-1 sm:mt-2 text-sm sm:text-base max-w-xs ms-auto me-auto">
              {description}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}

export { InfoCards };
