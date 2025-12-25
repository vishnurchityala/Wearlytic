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
    <section className="mt-20">
      <p className="text-center outfit-regular text-5xl">How it Works ?</p>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 px-12 sm:px-25 py-10">
        {cardData.map(({ step, image, title, description }) => (
          <div key={step} className="bg-white shadow-xl rounded-xl p-4 h-82">
            <p className="bg-black text-white font-bold anton-regular rounded-full w-8 h-8 flex items-center justify-center">
              {step}
            </p>

            <img
              src={image}
              className="h-26 transition ms-auto me-auto"
            />

            <h3 className="mt-4 text-center font-semibold outfit-regular text-2xl">
              {title}
            </h3>

            <p className="text-center outfit-regular mt-2 w-50 ms-auto me-auto">
              {description}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}

export { InfoCards };
