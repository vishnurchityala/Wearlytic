import { Footer } from "@/layout/Footer";
import { Navbar } from "@/layout/Navbar";
import { HeroBanner } from "./components/HeroBanner";
import { InfoBanner } from "./components/InfoBanner";
import { InfoCards } from "./components/InfoCards";
import { SuggestionBox } from "./components/SuggestionBox";

function LandingPage() {

  return (
    <div className='bg-gray-50'>
      <Navbar />
      <HeroBanner />
      <InfoCards />
      <InfoBanner />
      <SuggestionBox />
      <Footer />
    </div>
  );
}

export default LandingPage;
