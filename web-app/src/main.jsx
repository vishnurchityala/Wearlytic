import { StrictMode, useEffect } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import { createBrowserRouter, RouterProvider, Outlet, Navigate } from "react-router-dom";

import AuthProvider, { useAuth } from "./auth/AuthProvider.jsx";
import LandingPage from "./pages/LandingPage.jsx";
import { AgentPage } from "./pages/AgentPage.jsx";
import UserPage from "./pages/UserPage.jsx";

const ProtectedRoute = ({ redirectTo = "/landing" }) => {
  const { user, loading } = useAuth();

  if (loading)
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="w-10 h-10 border-4 border-t-black border-gray-300 rounded-full animate-spin"></div>
      </div>
    );

  if (!user) return <Navigate to={redirectTo} replace />;

  return <Outlet />;
};


const AuthLayout = () => {
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch("https://wearlytic-zbas.onrender.com/", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        });
      } catch (error) {
        console.error("API error:", error);
      }
    };
    fetchData();
    const intervalId = setInterval(fetchData, 40000); 
    return () => clearInterval(intervalId);
  }, []);

  return (
    <AuthProvider>
      <Outlet />
    </AuthProvider>
  );
};

const router = createBrowserRouter([
  {
    element: <AuthLayout />,
    children: [
      // Public routes
      { path: "/", element: <LandingPage /> },
      { path: "/landing", element: <LandingPage /> },

      // Protected routes
      {
        element: <ProtectedRoute />,
        children: [
          { path: "/playground", element: <AgentPage /> },
          { path: "/profile", element: <UserPage /> }
        ],
      },
    ],
  },
]);

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>
);
