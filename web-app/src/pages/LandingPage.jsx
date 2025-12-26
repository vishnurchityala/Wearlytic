import { Navbar } from '../components/Navbar'
import { HeroBanner } from '../components/HeroBanner'
import {Footer} from '../components/Footer'
import { InfoBanner } from '../components/InfoBanner'
import { InfoCards } from '../components/InfoCards'
import { SuggestionBox } from '../components/SuggestionBox'

function LandingPage() {

  return (
    <>
      <Navbar/>
      <HeroBanner/>
      <InfoCards/>
      <InfoBanner/>
      <SuggestionBox/>
      <Footer/>
    </>
  );
};

export default LandingPage;
