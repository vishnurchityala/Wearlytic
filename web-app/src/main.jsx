import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
import LandingPage from './pages/LandingPage.jsx';

const router = createBrowserRouter([
  {
    path: "/",
    element: <LandingPage/>,
  },
  {
    path: "/landing",
    element: <LandingPage/>,
  },
]);

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)
