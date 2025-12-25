import { useEffect, useState } from "react";

const infoData = [
  {
    image: "./try-out-image.png",
    title: (
      <>
        Virtually try clothes from any website at{" "}
        <span className="font-bold">One Place</span>
      </>
    ),
    description:
      "Preview fit, style, and appearance before buying, using realistic virtual try-on powered by accurate sizing.",
  },
  {
    image: "./website-image.png",
    title: (
      <>
        Bring styles from across the web at{" "}
        <span className="font-bold">One Place</span>
      </>
    ),
    description:
      "Collect clothing from multiple websites and preview them together without switching tabs or guessing how they will look.",
  },
];

function InfoBanner() {
  const [index, setIndex] = useState(0);
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const interval = setInterval(() => {
      setVisible(false);

      setTimeout(() => {
        setIndex((prev) => (prev + 1) % infoData.length);
        setVisible(true);
      }, 400);
    }, 8000);

    return () => clearInterval(interval);
  }, []);

  const { image, title, description } = infoData[index];

  return (
    <section className="w-full px-6 md:px-20 mb-15">
      <div
        className={`max-w-7xl mx-auto flex flex-col md:flex-row items-center gap-10
        transition-all duration-500 ease-in-out
        ${visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}
      >
        <img
          src={image}
          alt="Feature preview"
          className="w-full md:w-120 grayscale hover:grayscale-0 transition duration-300 object-cover"
        />

        <div className="flex flex-col items-center md:items-start text-center md:text-left gap-4">
          <p className="text-3xl md:text-6xl leading-tight outfit-regular">
            {title}
          </p>
          <p className="text-xl md:text-3xl leading-tight outfit-regular max-w-xl">
            {description}
          </p>
        </div>
      </div>
    </section>
  );
}

export { InfoBanner };
