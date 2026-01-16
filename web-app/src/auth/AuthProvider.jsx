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
    handleInitialSession();
  }, []);

  const handleInitialSession = async () => {
    try{
      // exchange token with backend
      const { data } = await supabase.auth.getSession();

      if (data.session) {
        await exchangeTokenWithBackend(data.session);
      }
    }
    catch (err){
      console.log('Session restore failed:',err);
    }
    finally{
      setLoading(false);
    }
  };

  const exchangeTokenWithBackend = async (session) => {
    try {
      const supabaseUserId = session.user.id;
      const email = session.user.email;

      // Call backend to generate tokens
      const res = await fetch(
        `${import.meta.env.VITE_API_BASE_URL}/auth/token/generate/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            supabase_uid: supabaseUserId,
          }),
        }
      );

      if (!res.ok) {
        throw new Error("Backend token generation failed");
      }

      const data = await res.json();

      // Your backend returns { access: "...", refresh: "..." }
      if (!data.access) {
        throw new Error("Malformed backend response");
      }

      // Set in-memory user + access token
      setUser({
        id: supabaseUserId,
        email: email,
      });

      setToken(data.access); // Only store access in memory
    } catch (err) {
      console.error("Token generation error:", err.message);
      setUser(null);
      setToken(null);
    }
  };



  // loginAction function
  const loginWithGoogle = async () => {
    setLoading(true);
    const {error} = await supabase.auth.signInWithOAuth({
        provider:'google',
        options: {
          redirectTo: window.location.origin
        }
      }
    )
    if (eror){
      console.error("Supabase login failed",error.message);
      setLoading(false);
    }
    setLoading(false);
  };

  // logoutAction function
  const logout = async () => {
    await supabase.auth.signOut();
    setUser(null);
    setToken(null);
    navigate('/');
  };


  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        loginWithGoogle,
        logout
      }}
    >
      {children}
    </AuthContext.Provider>
  );

};

export default AuthProvider;

export const useAuth = () => {
  return useContext(AuthContext);
};