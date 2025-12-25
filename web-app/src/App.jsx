import './App.css'
import { Navbar } from './components/Navbar'
import { HeroBanner } from './components/HeroBanner'
import {Footer} from './components/Footer'
import { InfoBanner } from './components/InfoBanner'
import { InfoCards } from './components/InfoCards'
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
