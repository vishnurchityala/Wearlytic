import { createContext, useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "./supabaseAuth";

const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const getSession = async () => {
      const { data } = await supabase.auth.getSession();
      if (data.session) {
        setUser(data.session.user);
        setToken(data.session.access_token);
      }
      setLoading(false);
    };

    getSession();
  }, []);

  const loginWithGoogle = async () => {
    setLoading(true);
    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: window.location.origin,
      },
    });

    if (error) {
      console.error("Supabase login failed:", error.message);
    }

    setLoading(false);
  };

  const logout = async () => {
    await supabase.auth.signOut();
    setUser(null);
    setToken(null);
    navigate("/");
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        loginWithGoogle,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;

export const useAuth = () => useContext(AuthContext);
