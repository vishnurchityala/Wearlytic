import { useEffect } from "react";
import { createBrowserRouter, RouterProvider, Outlet, Navigate } from "react-router-dom";

import { apiFetch } from "@/api/env.js";
import AuthProvider from "@/auth/AuthProvider.jsx";
import { useAuth } from "@/auth/AuthContext.js";
import LandingPage from "@/pages/landing/LandingPage.jsx";
import PlaygroundPage from "@/pages/playground/PlaygroundPage.jsx";
import ProfilePage from "@/pages/profile/ProfilePage.jsx";

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
        await apiFetch("/", {
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
      { path: "/", element: <LandingPage /> },
      { path: "/landing", element: <LandingPage /> },
      {
        element: <ProtectedRoute />,
        children: [
          { path: "/playground", element: <PlaygroundPage /> },
          { path: "/profile", element: <ProfilePage /> },
        ],
      },
    ],
  },
]);

export default function AppRouter() {
  return <RouterProvider router={router} />;
}
