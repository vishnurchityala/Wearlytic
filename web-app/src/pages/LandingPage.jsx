import { Navbar } from '../components/general/Navbar'
import { HeroBanner } from '../components/landing/HeroBanner'
import {Footer} from '../components/general/Footer'
import { InfoBanner } from '../components/landing/InfoBanner'
import { InfoCards } from '../components/landing/InfoCards'
import { SuggestionBox } from '../components/landing/SuggestionBox'

function LandingPage() {

  return (
    <div className='bg-gray-50'>
      <Navbar/>
      <HeroBanner/>
      <InfoCards/>
      <InfoBanner/>
      <SuggestionBox/>
      <Footer/>
    </div>
  );
};

export default LandingPage;
