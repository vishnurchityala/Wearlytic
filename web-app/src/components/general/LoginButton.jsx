import { faUser, faRightFromBracket } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useAuth } from "../../auth/AuthProvider";

function LoginButton() {
  const { user, loginWithGoogle, logout, loading } = useAuth();

  const handleClick = () => {
    if (user) {
      logout();
    } else {
      loginWithGoogle();
    }
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={loading}
      className="px-4 py-2 text-base sm:text-lg text-white bg-black rounded-2xl outfit-regular font-medium flex items-center gap-2 cursor-pointer"
    >
      <FontAwesomeIcon icon={user ? faRightFromBracket : faUser} className="w-5 h-5" />
      {loading
        ? "Please wait..."
        : user
        ? "Logout"
        : "Login"}
    </button>
  );
}

export { LoginButton };
