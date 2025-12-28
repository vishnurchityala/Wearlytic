import './App.css'
import { Navbar } from './components/general/Navbar'
import { HeroBanner } from './components/landing/HeroBanner'
import {Footer} from './components/general/Footer'
import { InfoBanner } from './components/landing/InfoBanner'
import { InfoCards } from './components/landing/InfoCards'
function App() {

  return (
    <>
      <Navbar/>
      <HeroBanner/>
      <InfoCards/>
      <InfoBanner/>
      <Footer/>
    </>
  );
}

export default App
